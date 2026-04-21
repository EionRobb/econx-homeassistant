"""Support for Econx climate/heatpump devices."""
import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.const import UnitOfTemperature
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
    """Set up the climate platform."""
    coordinator: EconxDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    
    for device_id, device_data in coordinator.data.items():
        # IR Devices
        irdevices = device_data.get("status", {}).get("irdevice", [])
        for i, irdevice in enumerate(irdevices):
            if str(irdevice.get("status")) != "-2":
                # Ensure it's a heatpump
                if "heatpump" in str(irdevice.get("type", "")).lower():
                    name = irdevice.get("name", f"Heatpump {i+1}")
                    entities.append(EconxClimate(coordinator, device_id, i, name))

    async_add_entities(entities)


class EconxClimate(CoordinatorEntity, ClimateEntity):
    """Representation of an Econx heatpump."""

    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
    )
    _attr_hvac_modes = [
        HVACMode.OFF,
        HVACMode.HEAT,
        HVACMode.COOL,
        HVACMode.AUTO,
    ]

    def __init__(
        self,
        coordinator: EconxDataUpdateCoordinator,
        device_id: str,
        index: int,
        name: str
    ) -> None:
        """Initialize the climate device."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._index = index
        self._attr_name = name
        self._attr_unique_id = f"{DOMAIN}_{device_id}_ir_{index + 1}"

    @property
    def hvac_mode(self) -> HVACMode:
        """Return hvac operation ie. heat, cool mode."""
        device_data = self.coordinator.data.get(self._device_id, {})
        items = device_data.get("status", {}).get("irdevice", [])
        if self._index < len(items):
            device_info = items[self._index]
            if str(device_info.get("status")) == "0":
                return HVACMode.OFF
            
            mode = device_info.get("mode", "auto").lower()
            if mode == "heat":
                return HVACMode.HEAT
            elif mode == "cool":
                return HVACMode.COOL
            elif mode in ("heatcool", "auto"):
                return HVACMode.AUTO
            
        return HVACMode.OFF

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        device_data = self.coordinator.data.get(self._device_id, {})
        items = device_data.get("status", {}).get("irdevice", [])
        if self._index < len(items):
            temp = items[self._index].get("temp")
            if temp is not None:
                try:
                    return float(temp)
                except ValueError:
                    pass
        return None

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode."""
        if hvac_mode == HVACMode.OFF:
            current_mode = "auto"
            current_temp = self.target_temperature or 21
            await self.coordinator.client.async_action(
                "IRDeviceOff", 
                params={
                    "deviceid": self._device_id, 
                    "index": self._index + 1,
                    "mode": current_mode,
                    "temp": current_temp,
                }
            )
        else:
            mode_str = "auto"
            if hvac_mode == HVACMode.HEAT:
                mode_str = "heat"
            elif hvac_mode == HVACMode.COOL:
                mode_str = "cool"
            
            current_temp = self.target_temperature or 21
            await self.coordinator.client.async_action(
                "IRDeviceOn", 
                params={
                    "deviceid": self._device_id, 
                    "index": self._index + 1,
                    "mode": mode_str,
                    "temp": current_temp,
                }
            )
        await self.coordinator.async_request_refresh()

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        temperature = kwargs.get("temperature")
        if temperature is not None:
            # Re-send current mode
            current_mode = "auto"
            if self.hvac_mode == HVACMode.HEAT:
                current_mode = "heat"
            elif self.hvac_mode == HVACMode.COOL:
                current_mode = "cool"
            
            method = "IRDeviceOn" if self.hvac_mode != HVACMode.OFF else "IRDeviceOff"

            await self.coordinator.client.async_action(
                method, 
                params={
                    "deviceid": self._device_id, 
                    "index": self._index + 1,
                    "mode": current_mode,
                    "temp": temperature,
                }
            )
            await self.coordinator.async_request_refresh()
