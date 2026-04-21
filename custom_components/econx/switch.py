"""Support for Econx switches."""
import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import EconxDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the switch platform."""
    coordinator: EconxDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    
    for device_id, device_data in coordinator.data.items():
        # Relays
        relays = device_data.get("status", {}).get("relay", [])
        for i, relay in enumerate(relays):
            if str(relay.get("status")) != "-2":
                name = relay.get("name", f"Relay {i+1}")
                # Filter out lights and covers for basic switch
                name_lower = name.lower()
                if "light" not in name_lower and "pendant" not in name_lower and "door" not in name_lower:
                    entities.append(EconxSwitch(coordinator, device_id, "relay", i, name))

        # Misc devices
        miscdevices = device_data.get("status", {}).get("miscdevice", [])
        for i, misc in enumerate(miscdevices):
            if str(misc.get("status")) != "-2":
                name = misc.get("name", f"Misc {i+1}")
                name_lower = name.lower()
                if "light" not in name_lower and "pendant" not in name_lower and "door" not in name_lower:
                    entities.append(EconxSwitch(coordinator, device_id, "misc", i, name))

    async_add_entities(entities)


class EconxSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of an Econx switch."""

    def __init__(
        self,
        coordinator: EconxDataUpdateCoordinator,
        device_id: str,
        device_type: str,
        index: int,
        name: str
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._device_type = device_type
        self._index = index
        self._attr_name = name
        self._attr_unique_id = f"{DOMAIN}_{device_id}_{device_type}_{index + 1}"

    @property
    def is_on(self) -> bool:
        """Return true if switch is on."""
        status_key = "relay" if self._device_type == "relay" else "miscdevice"
        device_data = self.coordinator.data.get(self._device_id, {})
        items = device_data.get("status", {}).get(status_key, [])
        if self._index < len(items):
            # status 1 = ON, 0 = OFF, -2 = Disabled
            return str(items[self._index].get("status")) == "1"
        return False

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""
        method = f"{self._device_type}On"
        await self.coordinator.client.async_action(
            method, 
            params={"deviceid": self._device_id, "index": self._index + 1}
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""
        method = f"{self._device_type}Off"
        await self.coordinator.client.async_action(
            method, 
            params={"deviceid": self._device_id, "index": self._index + 1}
        )
        await self.coordinator.async_request_refresh()
