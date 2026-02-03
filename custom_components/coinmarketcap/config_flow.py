from __future__ import annotations

import logging
from typing import Any
import voluptuous as vol
import aiohttp

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

    CONF_SCAN_INTERVAL, 
    CONF_DECIMALS, 
    CONF_SHOW_SENSORS,
    CONF_CURRENCY,
    API_URL, 
    DEFAULT_SCAN_INTERVAL, 
    DEFAULT_DECIMALS,
    DEFAULT_CURRENCY,
    DEFAULT_SENSORS,
    SENSOR_TYPES,
    CURRENCIES
)

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_API_KEY): str,
    vol.Required(CONF_SYMBOLS, default="BTC,ETH,SOL"): str,
    vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(cv.positive_int, vol.Range(min=60)),
    vol.Optional(CONF_DECIMALS, default=DEFAULT_DECIMALS): vol.All(cv.positive_int, vol.Range(min=0)),
    vol.Optional(CONF_CURRENCY, default=DEFAULT_CURRENCY): vol.In(CURRENCIES),
    vol.Optional(CONF_SHOW_SENSORS, default=DEFAULT_SENSORS): cv.multi_select(
        {k: v["name"] for k, v in SENSOR_TYPES.items()}
    ),
})

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for CoinMarketCap."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
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

    async def async_step_reauth(self, entry_data):
        """Handle initiation of re-authentication."""
        self._reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None):
        """Handle re-authentication confirm step."""
        errors = {}
        if user_input is not None:
            valid = await self._test_api_key(user_input[CONF_API_KEY])
            if valid:
                self.hass.config_entries.async_update_entry(
                    self._reauth_entry, data={**self._reauth_entry.data, **user_input}
                )
                await self.hass.config_entries.async_reload(self._reauth_entry.entry_id)
                return self.async_abort(reason="reauth_successful")
            errors["base"] = "invalid_auth"

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_API_KEY): str}),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> OptionsFlowHandler:
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)

    async def _test_api_key(self, api_key: str) -> bool:
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
        self._config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_API_KEY,
                    default=self._config_entry.options.get(
                        CONF_API_KEY, 
                        self._config_entry.data.get(CONF_API_KEY)
                    ),
                ): str,
                vol.Required(
                    CONF_SYMBOLS,
                    default=self._config_entry.options.get(
                        CONF_SYMBOLS, 
                        self._config_entry.data.get(CONF_SYMBOLS, "BTC,ETH")
                    ),
                ): str,
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=self._config_entry.options.get(
                        CONF_SCAN_INTERVAL, 
                        self._config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
                    ),
                ): vol.All(cv.positive_int, vol.Range(min=60)),
                vol.Optional(
                    CONF_DECIMALS,
                    default=self._config_entry.options.get(
                        CONF_DECIMALS, 
                        self._config_entry.data.get(CONF_DECIMALS, DEFAULT_DECIMALS)
                    ),
                ): vol.All(cv.positive_int, vol.Range(min=0)),
                vol.Optional(
                    CONF_CURRENCY,
                    default=self._config_entry.options.get(
                        CONF_CURRENCY,
                        self._config_entry.data.get(CONF_CURRENCY, DEFAULT_CURRENCY)
                    ),
                ): vol.In(CURRENCIES),
                vol.Optional(
                    CONF_SHOW_SENSORS,
                    default=self._config_entry.options.get(
                        CONF_SHOW_SENSORS, 
                        self._config_entry.data.get(CONF_SHOW_SENSORS, DEFAULT_SENSORS)
                    ),
                ): cv.multi_select({k: v["name"] for k, v in SENSOR_TYPES.items()}),
            }),
        )
