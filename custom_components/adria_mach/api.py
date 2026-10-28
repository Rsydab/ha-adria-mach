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

from .const import BASE_URL, NOT_SET, TOKEN_MARGIN, UPDATES_URL, USER_AGENT


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

    async def _post(self, path: str, body: dict[str, Any]) -> Any:
        url = path if path.startswith("http") else BASE_URL + path
        try:
            async with self._session.post(
                url,
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
        if not isinstance(data, (dict, list)):
            raise AdriaMachConnectionError(f"Unexpected response on {path}")
        return data

    async def async_get_updates_available(self, mach_info: dict[str, Any]) -> list[dict[str, Any]]:
        """Firmware updates the app's update service offers for this unit (often empty)."""
        data = await self._post(
            UPDATES_URL,
            {
                "releaseType": mach_info.get("releaseType", ""),
                "machId": self.mach_id,
                "version": mach_info.get("version", ""),
            },
        )
        return [item for item in data if isinstance(item, dict)] if isinstance(data, list) else []

    async def async_authenticate(self) -> None:
        """Log in and cache the token."""
        data = await self._post(
            "/v0/client/api/auth",
            {"username": self._username, "password": self._password},
        )
        token = data.get("token") if isinstance(data, dict) else None
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
        devices = (data.get("devices") or {}) if isinstance(data, dict) else {}
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
        if not isinstance(data, dict):
            raise AdriaMachConnectionError(f"Unexpected RPC response for {rtype}/{method}")
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

    async def async_get_user_settings(self) -> dict[str, str]:
        """Names of light groups/scenes, AUX name and Wi-Fi SSID.

        The backend also returns the hotspot password; it is dropped here and
        never stored.
        """
        payload = await self.async_rpc("systemRequest", "getMachUserSettings")
        settings: dict[str, str] = {}
        if isinstance(payload, dict):
            for key, value in payload.items():
                if isinstance(value, str) and (
                    key.endswith("_name") or key in ("wifiSsid", "auxName")
                ):
                    settings[key] = value.strip()
        return settings

    async def async_count_notifications(self) -> int | None:
        """Number of notifications in the unit's own notification centre."""
        payload = await self.async_rpc("notification", "countNotifications", params={})
        try:
            return int((payload or {}).get("count"))
        except (TypeError, ValueError):
            return None

    async def async_get_chart(self, value_id: str) -> list[tuple[int, float]]:
        """7-day history for one value as (epoch_ms, value) pairs."""
        payload = await self.async_rpc("chart", "getChart", device=value_id)
        times = (payload or {}).get("time") or []
        values = (payload or {}).get("value") or []
        points: list[tuple[int, float]] = []
        for ts, val in zip(times, values):
            try:
                points.append((int(ts), float(val)))
            except (TypeError, ValueError):
                continue
        return points

    async def async_set_value(self, value_id: str, value: Any) -> bool:
        """Set one value on the unit. Envelope verified from the app's own call."""
        payload = await self.async_rpc(
            "device", "setValue", request=[{"valueId": value_id, "value": value}]
        )
        successes = (payload or {}).get("successes") or []
        return bool(successes and successes[0])
