"""Alert and device status models for the NEP API."""

from __future__ import annotations

from enum import IntEnum
from typing import Any


class DeviceStatus(IntEnum):
    """Device online/offline status."""

    ONLINE = 0
    OFFLINE = -1


class AlertInfo:
    """Alert information for a device or site."""

    def __init__(self, raw_data: dict[str, Any]) -> None:
        self.raw_data = raw_data

    @property
    def code(self) -> str:
        return self.raw_data.get("code", self.raw_data.get("alertCode", "0000"))

    @property
    def title(self) -> str:
        return self.raw_data.get("title", self.raw_data.get("alertTitle", "OK"))

    @property
    def description(self) -> str:
        return self.raw_data.get(
            "desc",
            self.raw_data.get(
                "description", self.raw_data.get("alertDescription", "")
            ),
        )

    @property
    def is_ok(self) -> bool:
        return self.code == "0000"