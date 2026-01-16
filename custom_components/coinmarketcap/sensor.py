"""Sensor platform for CoinMarketCap integration."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the CoinMarketCap sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = []
    for symbol in coordinator.symbols.split(','):
        entities.append(CoinMarketCapSensor(coordinator, symbol, "price"))
        entities.append(CoinMarketCapSensor(coordinator, symbol, "percent_change_24h"))
        
    async_add_entities(entities)

class CoinMarketCapSensor(CoordinatorEntity, SensorEntity):
    """Representation of a CoinMarketCap sensor."""

    def __init__(self, coordinator, symbol, sensor_type):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._symbol = symbol.upper()
        self._sensor_type = sensor_type
        self._attr_name = f"CoinMarketCap {self._symbol} {sensor_type.replace('_', ' ').capitalize()}"
        self._attr_unique_id = f"{DOMAIN}_{self._symbol}_{sensor_type}"
        self._entry_id = coordinator.config_entry.entry_id

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
        data = self.coordinator.data.get(self._symbol)
        if data:
            if self._sensor_type == "price":
                price = data['quote']['USD']['price']
                return round(price, self.coordinator.decimals)
            elif self._sensor_type == "percent_change_24h":
                percent = data['quote']['USD']['percent_change_24h']
                return round(percent, self.coordinator.decimals)
        return None

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        if self._sensor_type == "price":
            return "$"
        elif self._sensor_type == "percent_change_24h":
            return "%"
        return None

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        data = self.coordinator.data.get(self._symbol)
        if data:
            return {
                "market_cap": data['quote']['USD']['market_cap'],
                "volume_24h": data['quote']['USD']['volume_24h'],
                "last_updated": data['quote']['USD']['last_updated'],
            }
        return None
