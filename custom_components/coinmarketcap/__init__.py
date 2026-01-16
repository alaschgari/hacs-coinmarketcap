"""The CoinMarketCap integration."""
import asyncio
import logging
from datetime import timedelta

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, CONF_API_KEY, CONF_SYMBOLS, CONF_SCAN_INTERVAL, API_URL, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up CoinMarketCap from a config entry."""
    session = aiohttp.ClientSession()
    
    # Use options if available, otherwise fallback to data
    symbols = entry.options.get(CONF_SYMBOLS, entry.data[CONF_SYMBOLS])
    scan_interval = entry.options.get(CONF_SCAN_INTERVAL, entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))

    coordinator = CoinMarketCapDataUpdateCoordinator(
        hass,
        session,
        api_key=entry.data[CONF_API_KEY],
        symbols=symbols,
        scan_interval=scan_interval,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Register update listener
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

    return unload_ok

async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)

class CoinMarketCapDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching CoinMarketCap data."""

    def __init__(self, hass, session, api_key, symbols, scan_interval):
        """Initialize the coordinator."""
        self.session = session
        self.api_key = api_key
        self.symbols = symbols.replace(" ", "")
        
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
        params = {
            'symbol': self.symbols,
            'convert': 'USD'
        }
        
        try:
            async with self.session.get(API_URL, headers=headers, params=params) as response:
                if response.status != 200:
                    raise UpdateFailed(f"Error communicating with API: {response.status}")
                data = await response.json()
                return data['data']
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")
