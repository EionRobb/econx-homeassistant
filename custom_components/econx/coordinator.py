"""DataUpdateCoordinator for Econx."""
import logging
from copy import deepcopy
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import EconxApiClient, EconxAuthError, EconxApiClientError
from .const import DOMAIN, CONF_EMAIL, CONF_PASSWORD

_LOGGER = logging.getLogger(__name__)

class EconxDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Econx data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.client = EconxApiClient(
            email=entry.data[CONF_EMAIL],
            password=entry.data[CONF_PASSWORD],
            session=async_get_clientsession(hass),
        )
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )

    async def _async_update_data(self) -> dict:
        """Update data via API."""
        try:
            return await self.client.async_get_data()
        except EconxAuthError as err:
            raise UpdateFailed(f"Auth error: {err}") from err
        except EconxApiClientError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}") from err

    def optimistic_update(self, device_id: str, device_type: str, index: int, status: str) -> None:
        """Publish a successful command immediately, pending the next API poll."""
        if not self.data or device_id not in self.data:
            return
        key = "relay" if device_type == "relay" else "miscdevice"
        items = self.data[device_id].get("status", {}).get(key, [])
        if index >= len(items):
            return
        updated = deepcopy(self.data)
        updated[device_id]["status"][key][index]["status"] = status
        self.async_set_updated_data(updated)

    def refresh_in_background(self) -> None:
        """Reconcile optimistic state with the authoritative cloud state."""
        self.hass.async_create_task(self.async_request_refresh())
