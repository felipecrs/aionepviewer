"""Playback models for the NEP API."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Any

from .chart import ChartData


class PlaybackType(IntEnum):
    """Playback data types for the device/playback endpoint."""

    POWER = 1  # Power playback (5-min intervals, full day)


@dataclass(slots=True)
class PlaybackModule:
    """Per-module playback data (5-min interval power values)."""

    plc_sn: str
    addr: int
    data: list[int]

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> PlaybackModule:
        return cls(
            plc_sn=data.get("plcSN", ""),
            addr=data.get("addr", 0),
            data=data.get("data", []),
        )


@dataclass(slots=True)
class PlaybackData:
    """Device playback data including total power and per-module breakdown."""

    overview: ChartData
    modules: list[PlaybackModule]
    unit: str

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> PlaybackData:
        return cls(
            overview=ChartData.from_api(data.get("overview", {})),
            modules=[PlaybackModule.from_api(m) for m in data.get("modules", [])],
            unit=data.get("unit", ""),
        )