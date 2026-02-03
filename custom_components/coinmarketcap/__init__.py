"""The CoinMarketCap integration."""
import asyncio
import logging
from datetime import timedelta
from typing import Any

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.typing import ConfigType

from .const import (
    DOMAIN, 
    CONF_API_KEY, 
    CONF_SYMBOLS, 
    CONF_SCAN_INTERVAL, 
    CONF_DECIMALS, 
    CONF_SHOW_SENSORS,
    CONF_CURRENCY,
    API_URL, 
    GLOBAL_API_URL,
    FEAR_GREED_API_URL,
    KEY_INFO_API_URL,
    DEFAULT_SCAN_INTERVAL, 
    DEFAULT_DECIMALS,
    DEFAULT_CURRENCY,
    DEFAULT_SENSORS,
    SENSOR_TYPES
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "diagnostics"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up CoinMarketCap from a config entry."""
    session = async_get_clientsession(hass)
    
    # Use options if available, otherwise fallback to data
    api_key = entry.options.get(CONF_API_KEY, entry.data[CONF_API_KEY])
    symbols = entry.options.get(CONF_SYMBOLS, entry.data[CONF_SYMBOLS])
    scan_interval = entry.options.get(CONF_SCAN_INTERVAL, entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))
    decimals = entry.options.get(CONF_DECIMALS, entry.data.get(CONF_DECIMALS, DEFAULT_DECIMALS))
    currency = entry.options.get(CONF_CURRENCY, entry.data.get(CONF_CURRENCY, DEFAULT_CURRENCY))
    show_sensors = entry.options.get(CONF_SHOW_SENSORS, entry.data.get(CONF_SHOW_SENSORS, DEFAULT_SENSORS))

    coordinator = CoinMarketCapDataUpdateCoordinator(
        hass,
        session,
        api_key=api_key,
        symbols=symbols,
        scan_interval=scan_interval,
        decimals=decimals,
        currency=currency,
        show_sensors=show_sensors,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Register update listener
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)

class CoinMarketCapDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching CoinMarketCap data."""

    def __init__(
        self, 
        hass: HomeAssistant, 
        session: aiohttp.ClientSession, 
        api_key: str, 
        symbols: str, 
        scan_interval: int, 
        decimals: int, 
        currency: str, 
        show_sensors: list[str]
    ) -> None:
        """Initialize the coordinator."""
        self.session = session
        self.api_key = api_key
        self.symbols = symbols.replace(" ", "")
        self.decimals = decimals
        self.currency = currency
        self.show_sensors = show_sensors
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

    def _get_enabled_categories(self) -> set[str]:
        """Identify which sensor categories are currently enabled."""
        categories = set()
        for sensor_type in self.show_sensors:
            if sensor_type in SENSOR_TYPES:
                categories.add(SENSOR_TYPES[sensor_type]["category"])
        return categories

    async def _async_update_data(self):
        """Fetch data from API."""
        headers = {
            'X-CMC_PRO_API_KEY': self.api_key,
            'Accepts': 'application/json',
        }
        
        # Determine which calls are needed
        enabled_categories = self._get_enabled_categories()
        
        # 1. Fetch cryptocurrency quotes (symbol category)
        params_quotes = {
            'symbol': self.symbols,
            'convert': self.currency
        }
        
        async def fetch_url(url: str, params: dict[str, Any] | None = None) -> dict[str, Any] | None:
            """Helper to fetch JSON with error handling."""
            try:
                async with self.session.get(url, headers=headers, params=params, timeout=10) as response:
                    if response.status in (401, 403):
                        _LOGGER.error("Authentication failed (401/403) for %s. Triggering re-auth.", url)
                        raise ConfigEntryAuthFailed("Invalid API Key or insufficient permissions")
                    
                    if response.status == 429:
                        _LOGGER.warning("API Rate limit reached for %s", url)
                        return None
                        
                    if response.status != 200:
                        _LOGGER.error("Error fetching %s: %s", url, response.status)
                        return None
                    return await response.json()
            except ConfigEntryAuthFailed:
                raise
            except Exception as err:
                _LOGGER.error("Exception fetching %s: %s", url, err)
                return None

        tasks = []
        
        # Always fetch quotes if symbol-based sensors are enabled (or if no sensors enabled yet)
        if "symbol" in enabled_categories or not enabled_categories:
            tasks.append(fetch_url(API_URL, params_quotes))
        else:
            tasks.append(asyncio.sleep(0, result=None)) # Placeholder
            
        if "global" in enabled_categories:
            tasks.append(fetch_url(GLOBAL_API_URL, params={'convert': self.currency}))
        else:
            tasks.append(asyncio.sleep(0, result=None))
            
        if "fear_greed" in enabled_categories:
            tasks.append(fetch_url(FEAR_GREED_API_URL))
        else:
            tasks.append(asyncio.sleep(0, result=None))
            
        if "key_info" in enabled_categories:
            tasks.append(fetch_url(KEY_INFO_API_URL))
        else:
            tasks.append(asyncio.sleep(0, result=None))

        # Execute all needed fetches in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        final_data = {}
        
        # Process Quotes
        if results[0] and 'data' in results[0]:
            final_data['symbols'] = results[0]['data']
        
        # Process Global Metrics
        if results[1] and 'data' in results[1]:
            final_data['global'] = results[1]['data']

        # Process Fear & Greed
        if len(results) > 2 and results[2] and 'data' in results[2]:
            fg_list = results[2]['data']
            if fg_list and isinstance(fg_list, list):
                final_data['fear_greed'] = fg_list[0]
            elif isinstance(fg_list, dict):
                # Backup in case API format changes
                final_data['fear_greed'] = fg_list

        # Process Key Info (API Credits)
        if len(results) > 3 and results[3] and 'data' in results[3]:
            final_data['key_info'] = results[3]['data']

        if not final_data:
            raise UpdateFailed("Failed to fetch any data from CoinMarketCap")
            
        return final_data
