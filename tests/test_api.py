"""Regression coverage for the legacy Econx action protocol."""
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import AsyncMock

# Load the standalone API without importing Home Assistant's integration setup.
root = Path(__file__).resolve().parents[1] / "custom_components" / "econx"
package = types.ModuleType("econx_api_test")
package.__path__ = [str(root)]
sys.modules[package.__name__] = package
spec = importlib.util.spec_from_file_location("econx_api_test.api", root / "api.py")
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)


class ActionTests(unittest.IsolatedAsyncioTestCase):
    def client(self, status=1):
        client = api.EconxApiClient("email", "password", None)
        client.token = "test-token"
        client.async_login = AsyncMock()
        client._async_request = AsyncMock(return_value={"status": status})
        return client

    async def test_garage_action_sends_empty_code(self):
        client = self.client()
        params = {"deviceid": "test-device", "index": 1}
        await client.async_action("miscOff", params)
        client._async_request.assert_awaited_once_with("miscOff", params, {"code": ""})

    async def test_explicit_pin_is_preserved_without_mutating_input(self):
        client = self.client("1")
        data = {"code": "1234"}
        await client.async_action("miscOff", data=data)
        client._async_request.assert_awaited_once_with("miscOff", None, data)
        self.assertEqual(data, {"code": "1234"})

    async def test_pin_and_security_failures_are_not_retried(self):
        for status, message in [(0, "PIN"), ("0", "PIN"), (2, "security"), ("2", "security"), (None, "unexpected")]:
            with self.subTest(status=status):
                client = self.client(status)
                with self.assertRaisesRegex(api.EconxApiClientError, message):
                    await client.async_action("miscOff")
                client.async_login.assert_not_awaited()
                client._async_request.assert_awaited_once()


if __name__ == "__main__":
    unittest.main()
