"""Playback models for the NEP API."""

from __future__ import annotations

from enum import IntEnum
from typing import Any

from .chart import ChartData


class PlaybackType(IntEnum):
    """Playback data types for the device/playback endpoint."""

    POWER = 1  # Power playback (5-min intervals, full day)


class PlaybackModule:
    """Per-module playback data (5-min interval power values)."""

    def __init__(self, raw_data: dict[str, Any]) -> None:
        self.raw_data = raw_data

    @property
    def plc_sn(self) -> str:
        return self.raw_data.get("plcSN", "")

    @property
    def addr(self) -> int:
        return self.raw_data.get("addr", 0)

    @property
    def data(self) -> list[int]:
        return self.raw_data.get("data", [])


class PlaybackData:
    """Device playback data including total power and per-module breakdown."""

    def __init__(self, raw_data: dict[str, Any]) -> None:
        self.raw_data = raw_data

    @property
    def overview(self) -> ChartData:
        return ChartData(self.raw_data.get("overview", {}))

    @property
    def modules(self) -> list[PlaybackModule]:
        return [PlaybackModule(m) for m in self.raw_data.get("modules", [])]

    @property
    def unit(self) -> str:
        return self.raw_data.get("unit", "")