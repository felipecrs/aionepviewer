"""Microinverter module models for the NEP API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class Module:
    """A single microinverter module (panel-level data)."""

    plc_sn: str
    addr: int
    last_update: str
    last_update_time: int
    now: float
    today_power: float
    total_power: float
    now_unit: str
    today_power_unit: str
    total_power_unit: str
    version: str
    status: str
    page: int
    model: int
    model_name: str

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Module:
        return cls(
            plc_sn=data.get("plcSN", ""),
            addr=data.get("addr", 0),
            last_update=data.get("lastUpdate", ""),
            last_update_time=data.get("lastUpdateTime", 0),
            now=data.get("now", 0),
            today_power=data.get("todayPower", 0),
            total_power=data.get("totalPower", 0),
            now_unit=data.get("nowUnit", "W"),
            today_power_unit=data.get("todayPowerUnit", "kWh"),
            total_power_unit=data.get("totalPowerUnit", "kWh"),
            version=data.get("version", ""),
            status=data.get("status", "0000"),
            page=data.get("page", 0),
            model=data.get("model", 0),
            model_name=data.get("model_name", "-"),
        )


@dataclass(slots=True)
class DeviceModules:
    """Modules grouped by gateway/device serial number."""

    sn: str
    is_phase: bool
    modules: list[Module]
    status: int
    status_title: str
    alert_code: str
    alert_title: str
    model: int
    model_name: str
    last_update: str
    version: str
    alias: str

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> DeviceModules:
        return cls(
            sn=data.get("sn", ""),
            is_phase=data.get("isPhase", False),
            modules=[Module.from_api(m) for m in data.get("modules", [])],
            status=data.get("status", -1),
            status_title=data.get("statusTitle", "offline"),
            alert_code=data.get("alertCode", ""),
            alert_title=data.get("alertTitle", ""),
            model=data.get("model", 0),
            model_name=data.get("modelName", ""),
            last_update=data.get("lastUpdate", ""),
            version=data.get("version", ""),
            alias=data.get("alias", ""),
        )


@dataclass(slots=True)
class SiteModulesData:
    """All modules for a site, grouped by device."""

    devices: list[DeviceModules]
    total_plc: int
    is_all: bool

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> SiteModulesData:
        return cls(
            devices=[DeviceModules.from_api(d) for d in data.get("list", [])],
            total_plc=data.get("total_plc", 0),
            is_all=data.get("is_all", True),
        )