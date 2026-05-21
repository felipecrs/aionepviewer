"""Alert and device status models for the NEP API."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Any


class DeviceStatus(IntEnum):
    """Device online/offline status."""

    ONLINE = 0
    OFFLINE = -1


@dataclass(slots=True)
class AlertInfo:
    """Alert information for a device or site."""

    code: str
    title: str
    description: str

    @property
    def is_ok(self) -> bool:
        return self.code == "0000"

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> AlertInfo:
        return cls(
            code=data.get("code", data.get("alertCode", "0000")),
            title=data.get("title", data.get("alertTitle", "OK")),
            description=data.get(
                "desc", data.get("description", data.get("alertDescription", ""))
            ),
        )