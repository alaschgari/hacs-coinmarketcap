"""Sensor platform for CoinMarketCap integration."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SENSOR_TYPES, CONF_SHOW_SENSORS, DEFAULT_SENSORS

async def async_setup_entry(hass, entry, async_add_entities):
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
    
    # Add global and fear_greed sensors (these don't depend on a specific symbol)
    for sensor_type in enabled_sensors:
        if sensor_type in SENSOR_TYPES and SENSOR_TYPES[sensor_type]["category"] in ["global", "fear_greed"]:
            entities.append(CoinMarketCapSensor(coordinator, None, sensor_type))
        
    async_add_entities(entities)

class CoinMarketCapSensor(CoordinatorEntity, SensorEntity):
    """Representation of a CoinMarketCap sensor."""

    def __init__(self, coordinator, symbol, sensor_type):
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
    def state(self):
        """Return the state of the sensor."""
        category = self._sensor_info["category"]
        
        if category == "symbol" and self._symbol:
            data = self.coordinator.data.get('symbols', {}).get(self._symbol)
        elif category == "global":
            data = self.coordinator.data.get('global')
        elif category == "fear_greed":
            data = self.coordinator.data.get('fear_greed')
        else:
            data = None

        if data:
            value = data
            for key in self._sensor_info["json_path"]:
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
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._sensor_info.get("unit")

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        category = self._sensor_info["category"]
        
        if category == "symbol" and self._symbol:
            data = self.coordinator.data.get('symbols', {}).get(self._symbol)
            if data:
                quote = data.get('quote', {}).get('USD', {})
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
        return None
