"""Econx API Client."""
import logging
import json
import urllib.parse
from typing import Any, Dict, Optional

import aiohttp

from .const import BASE_URL

_LOGGER = logging.getLogger(__name__)

class EconxApiClientError(Exception):
    """Exception to indicate a general API error."""


class EconxAuthError(Exception):
    """Exception to indicate an authentication error."""


class EconxApiClient:
    """Client for interfacing with Econx API."""

    def __init__(self, email: str, password: str, session: aiohttp.ClientSession) -> None:
        """Initialize the API client."""
        self.email = email
        self.password = password
        self.session = session
        self.token: Optional[str] = None

    async def async_login(self) -> str:
        """Log in to the API and retrieve a token."""
        payload = {
            "username": self.email,
            "password": self.password
        }
        _LOGGER.debug("Logging in to Econx API")
        try:
            url = f"{BASE_URL}?method=login"
            async with self.session.post(url, data=payload) as response:
                response.raise_for_status()
                text = await response.text()
                # Parse JSON and lowercase all keys to match PHP implementation
                data = json.loads(text)
                data = self._lowercase_keys(data)

                if int(data.get("success", 0)) == 0:
                    raise EconxAuthError("Invalid username or password")
                
                self.token = data.get("token")
                return self.token
        except Exception as err:
            raise EconxAuthError("Failed to login to Econx") from err

    async def async_get_data(self) -> Dict[str, Any]:
        """Get the full device list and their statuses."""
        if not self.token:
            await self.async_login()

        device_list_data = await self._async_request("getDeviceList")
        if device_list_data.get("status") == 0:
            # Token might be expired, try to login again
            await self.async_login()
            device_list_data = await self._async_request("getDeviceList")
            if device_list_data.get("status") == 0:
                raise EconxAuthError("Token expired and re-login failed")

        devices = device_list_data.get("devicelist", {})
        full_data = {}

        for device_id, device_name in devices.items():
            status_data = await self._async_request("getStatus", {"deviceid": device_id})
            full_data[device_id] = {
                "name": device_name,
                "status": status_data.get("devicestatus", {})
            }

        return full_data

    async def async_action(self, method: str, params: Dict[str, Any] = None, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Perform an action."""
        if not self.token:
            await self.async_login()

        resp = await self._async_request(method, params, data)
        if resp.get("status") == 0:
             # Try refreshing auth
             await self.async_login()
             resp = await self._async_request(method, params, data)
             if resp.get("status") == 0:
                 raise EconxAuthError("Token expired")
             
        return resp

    async def _async_request(self, method: str, params: Dict[str, Any] = None, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make an authenticated request to the API."""
        url_params = {"method": method}
        if params:
            url_params.update(params)

        payload = {"token": self.token}
        if data:
            payload.update(data)

        url = f"{BASE_URL}?{urllib.parse.urlencode(url_params)}"

        try:
            async with self.session.post(url, data=payload) as response:
                response.raise_for_status()
                text = await response.text()
                return self._lowercase_keys(json.loads(text))
        except Exception as err:
            raise EconxApiClientError(f"API request failed: {err}") from err

    def _lowercase_keys(self, obj: Any) -> Any:
        """Recursively lowercase dictionary keys."""
        if isinstance(obj, dict):
            return {k.lower(): self._lowercase_keys(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self._lowercase_keys(x) for x in obj]
        return obj
