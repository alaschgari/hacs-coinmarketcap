"""The CoinMarketCap integration."""
import asyncio
import logging
from datetime import timedelta

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
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
    session = aiohttp.ClientSession()
    
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
        
        try:
            # We use gather to fetch all data points concurrently
            result = {}
            
            # Use multiple tasks for parallel fetching
            tasks = [
                self.session.get(API_URL, headers=headers, params=params_quotes),
                self.session.get(GLOBAL_API_URL, headers=headers),
                self.session.get(FEAR_GREED_API_URL, headers=headers)
            ]
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process Quotes
            if not isinstance(responses[0], Exception) and responses[0].status == 200:
                quotes_data = await responses[0].json()
                result['symbols'] = quotes_data.get('data', {})
            else:
                _LOGGER.error("Error fetching quotes: %s", responses[0])
            
            # Process Global Metrics
            if not isinstance(responses[1], Exception) and responses[1].status == 200:
                global_data = await responses[1].json()
                result['global'] = global_data.get('data', {})
            else:
                _LOGGER.error("Error fetching global metrics: %s", responses[1])

            # Process Fear & Greed
            if not isinstance(responses[2], Exception) and responses[2].status == 200:
                fg_data = await responses[2].json()
                # The response structure for fear and greed can vary, let's grab the first item
                fg_list = fg_data.get('data', [])
                if fg_list:
                    result['fear_greed'] = fg_list[0]
            else:
                _LOGGER.error("Error fetching Fear & Greed index: %s", responses[2])

            if not result:
                raise UpdateFailed("Failed to fetch any data from CoinMarketCap")
                
            return result
                
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")
