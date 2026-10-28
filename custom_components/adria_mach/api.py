"""Async client for the Adria MACH cloud API (mach-backend.solvesall.com).

Verified against the MACH app's own traffic (2026-10-28):
  POST /v0/client/api/auth  {username, password} -> {token, durationMSec}
  POST /v0/client/api/all   {token, machId, payload:{type:"ui-req",
                             payload:{type, content:{method, ...}}}}
                            -> {status, payload}
"""

from __future__ import annotations

import time
from typing import Any

import aiohttp

from .const import BASE_URL, NOT_SET, TOKEN_MARGIN, USER_AGENT


class AdriaMachError(Exception):
    """Base error."""


class AdriaMachAuthError(AdriaMachError):
    """Authentication failed."""


class AdriaMachConnectionError(AdriaMachError):
    """Could not reach the backend or got an unexpected answer."""


class AdriaMachApi:
    """Minimal client: authenticate, read all values, set a value."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        username: str,
        password: str,
        mach_id: str | None = None,
    ) -> None:
        self._session = session
        self._username = username
        self._password = password
        self.mach_id = mach_id
        self._token: str | None = None
        self._token_expires: float = 0.0

    async def _post(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        try:
            async with self._session.post(
                BASE_URL + path,
                json=body,
                headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                if resp.status in (401, 403):
                    raise AdriaMachAuthError(f"HTTP {resp.status} on {path}")
                if resp.status != 200:
                    raise AdriaMachConnectionError(f"HTTP {resp.status} on {path}")
                data = await resp.json(content_type=None)
        except aiohttp.ClientError as err:
            raise AdriaMachConnectionError(str(err)) from err
        if not isinstance(data, dict):
            raise AdriaMachConnectionError(f"Unexpected response on {path}")
        return data

    async def async_authenticate(self) -> None:
        """Log in and cache the token."""
        data = await self._post(
            "/v0/client/api/auth",
            {"username": self._username, "password": self._password},
        )
        token = data.get("token")
        if not token:
            raise AdriaMachAuthError("No token in auth response")
        duration_s = int(data.get("durationMSec", 0)) / 1000
        self._token = token
        self._token_expires = time.monotonic() + max(duration_s - TOKEN_MARGIN, 60)

    async def _ensure_token(self) -> str:
        if not self._token or time.monotonic() >= self._token_expires:
            await self.async_authenticate()
        assert self._token is not None
        return self._token

    async def async_discover_devices(self) -> list[dict[str, str]]:
        """List the MACH units registered on this account (mobile API syncData).

        Returns [{"mach_id", "name", "type"}]. Other fields in the response,
        such as the per-device shared secret, are deliberately not kept.
        """
        data = await self._post(
            "/v0/api/mobile/syncData",
            {
                "payload": {"current": [], "deleted": []},
                "auth": {"username": self._username, "password": self._password},
            },
        )
        devices = data.get("devices") or {}
        found: list[dict[str, str]] = []
        for bucket in ("add", "update"):
            for dev in devices.get(bucket) or []:
                if isinstance(dev, dict) and dev.get("machId"):
                    found.append(
                        {
                            "mach_id": str(dev["machId"]).upper(),
                            "name": str(dev.get("name") or ""),
                            "type": str(dev.get("type") or ""),
                        }
                    )
        return found

    async def async_rpc(
        self, rtype: str, method: str, _retry: bool = True, **content: Any
    ) -> Any:
        """Call the generic /all RPC endpoint and return its payload."""
        if not self.mach_id:
            raise AdriaMachConnectionError("No MACH unit selected")
        token = await self._ensure_token()
        body = {
            "token": token,
            "machId": self.mach_id,
            "payload": {
                "type": "ui-req",
                "payload": {"type": rtype, "content": {"method": method, **content}},
            },
        }
        data = await self._post("/v0/client/api/all", body)
        status = data.get("status")
        if status != 200:
            if _retry:
                # Token may have been invalidated server-side: re-auth once.
                self._token = None
                return await self.async_rpc(rtype, method, _retry=False, **content)
            raise AdriaMachConnectionError(f"RPC {rtype}/{method} returned status {status}")
        return data.get("payload")

    async def async_get_mach_info(self) -> dict[str, Any]:
        """Firmware/type info for the MACH unit."""
        payload = await self.async_rpc("systemRequest", "getMachInfo")
        return payload if isinstance(payload, dict) else {}

    async def async_get_all_values(self) -> dict[str, Any]:
        """Return {device_id: status} for every device the unit reports."""
        payload = await self.async_rpc("device", "getValuesAll")
        values: dict[str, Any] = {}
        for item in (payload or {}).get("values", []):
            if not isinstance(item, dict) or "device" not in item:
                continue
            status = item.get("status")
            if status == NOT_SET:
                status = None
            values[str(item["device"])] = status
        return values

    async def async_set_value(self, value_id: str, value: Any) -> bool:
        """Set one value on the unit. Envelope verified from the app's own call."""
        payload = await self.async_rpc(
            "device", "setValue", request=[{"valueId": value_id, "value": value}]
        )
        successes = (payload or {}).get("successes") or []
        return bool(successes and successes[0])
