from __future__ import annotations
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity, 
    SensorDeviceClass, 
    SensorStateClass
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import EntityCategory
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SENSOR_TYPES, CONF_SHOW_SENSORS, DEFAULT_SENSORS, CURRENCIES
from . import CoinMarketCapDataUpdateCoordinator

async def async_setup_entry(
    hass: HomeAssistant, 
    entry: ConfigEntry, 
    async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the CoinMarketCap sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    symbols = coordinator.symbols.split(',')
    # Get enabled sensors from options or fallback to default
    enabled_sensors = entry.options.get(CONF_SHOW_SENSORS, entry.data.get(CONF_SHOW_SENSORS, DEFAULT_SENSORS))
    
    entities = []
    
    # Add symbol-based sensors
    for symbol in symbols:
        for sensor_type in enabled_sensors:
            if sensor_type in SENSOR_TYPES and SENSOR_TYPES[sensor_type]["category"] == "symbol":
                entities.append(CoinMarketCapSensor(coordinator, symbol, sensor_type))
    
    # Add global, fear_greed and key_info sensors (these don't depend on a specific symbol)
    for sensor_type in enabled_sensors:
        if sensor_type in SENSOR_TYPES and SENSOR_TYPES[sensor_type]["category"] in ["global", "fear_greed", "key_info"]:
            entities.append(CoinMarketCapSensor(coordinator, None, sensor_type))
        
    async_add_entities(entities)

class CoinMarketCapSensor(CoordinatorEntity, SensorEntity):
    """Representation of a CoinMarketCap sensor."""

    def __init__(
        self, 
        coordinator: CoinMarketCapDataUpdateCoordinator, 
        symbol: str | None, 
        sensor_type: str
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._symbol = symbol.upper() if symbol else None
        self._sensor_type = sensor_type
        self._sensor_info = SENSOR_TYPES[sensor_type]
        
        if self._symbol:
            self._attr_name = f"{self._symbol} {self._sensor_info['name']}"
            self._attr_unique_id = f"{DOMAIN}_{self._symbol}_{sensor_type}"
        else:
            self._attr_name = f"CMC {self._sensor_info['name']}"
            self._attr_unique_id = f"{DOMAIN}_{sensor_type}"
            
        self._entry_id = coordinator.config_entry.entry_id
        
        # Set icon if defined
        if "icon" in self._sensor_info:
            self._attr_icon = self._sensor_info["icon"]
            
        # Set classes and categories
        if "device_class" in self._sensor_info:
            self._attr_device_class = self._sensor_info["device_class"]
        if "state_class" in self._sensor_info:
            self._attr_state_class = self._sensor_info["state_class"]
        if "entity_category" in self._sensor_info:
            if self._sensor_info["entity_category"] == "diagnostic":
                self._attr_entity_category = EntityCategory.DIAGNOSTIC
            elif self._sensor_info["entity_category"] == "config":
                self._attr_entity_category = EntityCategory.CONFIG
            else:
                self._attr_entity_category = self._sensor_info["entity_category"]

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this entity."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry_id)},
            name="CoinMarketCap",
            manufacturer="CoinMarketCap",
            entry_type="service",
        )

    @property
    def icon(self) -> str | None:
        """Return dynamic icon for Fear & Greed."""
        if self._sensor_type == "fear_greed_index":
            value = self.native_value
            if value is not None:
                if value <= 25: return "mdi:emoticon-dead"
                if value <= 45: return "mdi:emoticon-sad"
                if value <= 55: return "mdi:emoticon-neutral"
                if value <= 75: return "mdi:emoticon-happy"
                return "mdi:emoticon-excited"
        return self._sensor_info.get("icon")

    @property
    def native_value(self) -> str | float | int | None:
        """Return the state of the sensor."""
        category = self._sensor_info["category"]
        
        if category == "symbol" and self._symbol:
            data = self.coordinator.data.get('symbols', {}).get(self._symbol)
        elif category == "global":
            data = self.coordinator.data.get('global')
        elif category == "fear_greed":
            data = self.coordinator.data.get('fear_greed')
        elif category == "key_info":
            data = self.coordinator.data.get('key_info')
        else:
            data = None

        if data:
            value = data
            json_path = self._sensor_info["json_path"]
            
            # Dynamic path replacement for currency
            actual_path = [k.replace("{currency}", self.coordinator.currency) for k in json_path]
            
            for key in actual_path:
                if isinstance(value, dict):
                    value = value.get(key)
                else:
                    return None
                    
                if value is None:
                    return None
            
            # Formatting
            if isinstance(value, (int, float)):
                return round(value, self.coordinator.decimals)
            return value
            
        return None

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit of measurement."""
        unit = self._sensor_info.get("unit")
        if unit:
            currency_symbols = {"USD": "$", "EUR": "€", "GBP": "£", "BTC": "₿", "ETH": "Ξ"}
            symbol = currency_symbols.get(self.coordinator.currency, self.coordinator.currency)
            return unit.replace("{currency_symbol}", symbol)
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return the state attributes."""
        category = self._sensor_info["category"]
        
        if category == "symbol" and self._symbol:
            data = self.coordinator.data.get('symbols', {}).get(self._symbol)
            if data:
                quote = data.get('quote', {}).get(self.coordinator.currency, {})
                return {
                    "last_updated": quote.get('last_updated'),
                    "api_id": data.get('id'),
                    "logo_url": f"https://s2.coinmarketcap.com/static/img/coins/64x64/{data.get('id')}.png"
                }
        elif category == "global":
            data = self.coordinator.data.get('global')
            if data:
                return {
                    "last_updated": data.get('last_updated'),
                }
        elif category == "fear_greed":
            data = self.coordinator.data.get('fear_greed')
            if data:
                return {
                    "last_updated": data.get('last_updated'),
                }
        elif category == "key_info":
            data = self.coordinator.data.get('key_info', {})
            return {
                "plan_name": data.get('plan', {}).get('name'),
                "rate_limit_minute": data.get('plan', {}).get('rate_limit_minute')
            }
        return None
