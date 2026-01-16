"""Config flow for CoinMarketCap integration."""
import logging
import voluptuous as vol
import aiohttp

from homeassistant import config_entries
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, CONF_API_KEY, CONF_SYMBOLS, CONF_SCAN_INTERVAL, API_URL, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_API_KEY): str,
    vol.Required(CONF_SYMBOLS, default="BTC,ETH"): str,
    vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(cv.positive_int, vol.Range(min=60)),
})

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for CoinMarketCap."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            # Validate the API key
            valid = await self._test_api_key(user_input[CONF_API_KEY])
            if valid:
                return self.async_create_entry(title="CoinMarketCap", data=user_input)
            else:
                errors["base"] = "invalid_auth"

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)

    async def _test_api_key(self, api_key):
        """Test if the API key is valid."""
        headers = {
            'X-CMC_PRO_API_KEY': api_key,
            'Accepts': 'application/json',
        }
        params = {
            'symbol': 'BTC',
            'convert': 'USD'
        }
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(API_URL, headers=headers, params=params) as response:
                    return response.status == 200
            except Exception:
                return False

class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for CoinMarketCap."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_SYMBOLS,
                    default=self.config_entry.options.get(
                        CONF_SYMBOLS, 
                        self.config_entry.data.get(CONF_SYMBOLS, "BTC,ETH")
                    ),
                ): str,
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=self.config_entry.options.get(
                        CONF_SCAN_INTERVAL, 
                        self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
                    ),
                ): vol.All(cv.positive_int, vol.Range(min=60)),
            }),
        )
