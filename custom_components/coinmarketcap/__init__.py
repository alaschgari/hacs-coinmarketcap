"""The CoinMarketCap integration."""
import asyncio
import logging
from datetime import timedelta

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN, 
    CONF_API_KEY, 
    CONF_SYMBOLS, 
    CONF_SCAN_INTERVAL, 
    CONF_DECIMALS, 
    API_URL, 
    GLOBAL_API_URL,
    FEAR_GREED_API_URL,
    DEFAULT_SCAN_INTERVAL, 
    DEFAULT_DECIMALS
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up CoinMarketCap from a config entry."""
    session = async_get_clientsession(hass)
    
    # Use options if available, otherwise fallback to data
    api_key = entry.options.get(CONF_API_KEY, entry.data[CONF_API_KEY])
    symbols = entry.options.get(CONF_SYMBOLS, entry.data[CONF_SYMBOLS])
    scan_interval = entry.options.get(CONF_SCAN_INTERVAL, entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))
    decimals = entry.options.get(CONF_DECIMALS, entry.data.get(CONF_DECIMALS, DEFAULT_DECIMALS))

    coordinator = CoinMarketCapDataUpdateCoordinator(
        hass,
        session,
        api_key=api_key,
        symbols=symbols,
        scan_interval=scan_interval,
        decimals=decimals,
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

class CoinMarketCapDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching CoinMarketCap data."""

    def __init__(self, hass, session, api_key, symbols, scan_interval, decimals):
        """Initialize the coordinator."""
        self.session = session
        self.api_key = api_key
        self.symbols = symbols.replace(" ", "")
        self.decimals = decimals
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self):
        """Fetch data from API."""
        headers = {
            'X-CMC_PRO_API_KEY': self.api_key,
            'Accepts': 'application/json',
        }
        
        # 1. Fetch cryptocurrency quotes (existing)
        params_quotes = {
            'symbol': self.symbols,
            'convert': 'USD'
        }
        
        async def fetch_url(url, params=None):
            """Helper to fetch JSON with error handling."""
            try:
                async with self.session.get(url, headers=headers, params=params, timeout=10) as response:
                    if response.status != 200:
                        _LOGGER.error("Error fetching %s: %s", url, response.status)
                        return None
                    return await response.json()
            except Exception as err:
                _LOGGER.error("Exception fetching %s: %s", url, err)
                return None

        # Execute all fetches in parallel
        results = await asyncio.gather(
            fetch_url(API_URL, params_quotes),
            fetch_url(GLOBAL_API_URL),
            fetch_url(FEAR_GREED_API_URL),
            return_exceptions=True
        )

        final_data = {}
        
        # Process Quotes
        if results[0] and 'data' in results[0]:
            final_data['symbols'] = results[0]['data']
        
        # Process Global Metrics
        if results[1] and 'data' in results[1]:
            final_data['global'] = results[1]['data']

        # Process Fear & Greed
        if results[2] and 'data' in results[2]:
            fg_list = results[2]['data']
            if fg_list and isinstance(fg_list, list):
                final_data['fear_greed'] = fg_list[0]
            elif isinstance(fg_list, dict):
                # Backup in case API format changes
                final_data['fear_greed'] = fg_list

        if not final_data:
            raise UpdateFailed("Failed to fetch any data from CoinMarketCap")
            
        return final_data
