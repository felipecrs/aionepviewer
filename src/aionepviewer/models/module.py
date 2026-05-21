"""Microinverter module models for the NEP API."""

from __future__ import annotations

from typing import Any


class Module:
    """A single microinverter module (panel-level data)."""

    def __init__(self, raw_data: dict[str, Any]) -> None:
        self.raw_data = raw_data

    @property
    def plc_sn(self) -> str:
        return self.raw_data.get("plcSN", "")

    @property
    def addr(self) -> int:
        return self.raw_data.get("addr", 0)

    @property
    def last_update(self) -> str:
        return self.raw_data.get("lastUpdate", "")

    @property
    def last_update_time(self) -> int:
        return self.raw_data.get("lastUpdateTime", 0)

    @property
    def now(self) -> float:
        return self.raw_data.get("now", 0)

    @property
    def today_power(self) -> float:
        return self.raw_data.get("todayPower", 0)

    @property
    def total_power(self) -> float:
        return self.raw_data.get("totalPower", 0)

    @property
    def now_unit(self) -> str:
        return self.raw_data.get("nowUnit", "W")

    @property
    def today_power_unit(self) -> str:
        return self.raw_data.get("todayPowerUnit", "kWh")

    @property
    def total_power_unit(self) -> str:
        return self.raw_data.get("totalPowerUnit", "kWh")

    @property
    def version(self) -> str:
        return self.raw_data.get("version", "")

    @property
    def status(self) -> str:
        return self.raw_data.get("status", "0000")

    @property
    def page(self) -> int:
        return self.raw_data.get("page", 0)

    @property
    def model(self) -> int:
        return self.raw_data.get("model", 0)

    @property
    def model_name(self) -> str:
        return self.raw_data.get("model_name", "-")


class DeviceModules:
    """Modules grouped by gateway/device serial number."""

    def __init__(self, raw_data: dict[str, Any]) -> None:
        self.raw_data = raw_data

    @property
    def sn(self) -> str:
        return self.raw_data.get("sn", "").upper()

    @property
    def is_phase(self) -> bool:
        return self.raw_data.get("isPhase", False)

    @property
    def modules(self) -> list[Module]:
        return [Module(m) for m in self.raw_data.get("modules", [])]

    @property
    def status(self) -> int:
        return self.raw_data.get("status", -1)

    @property
    def status_title(self) -> str:
        return self.raw_data.get("statusTitle", "offline")

    @property
    def alert_code(self) -> str:
        return self.raw_data.get("alertCode", "")

    @property
    def alert_title(self) -> str:
        return self.raw_data.get("alertTitle", "")

    @property
    def model(self) -> int:
        return self.raw_data.get("model", 0)

    @property
    def model_name(self) -> str:
        return self.raw_data.get("modelName", "")

    @property
    def last_update(self) -> str:
        return self.raw_data.get("lastUpdate", "")

    @property
    def version(self) -> str:
        return self.raw_data.get("version", "")

    @property
    def alias(self) -> str:
        return self.raw_data.get("alias", "")


class SiteModulesData:
    """All modules for a site, grouped by device."""

    def __init__(self, raw_data: dict[str, Any]) -> None:
        self.raw_data = raw_data

    @property
    def devices(self) -> list[DeviceModules]:
        return [DeviceModules(d) for d in self.raw_data.get("list", [])]

    @property
    def total_plc(self) -> int:
        return self.raw_data.get("total_plc", 0)

    @property
    def is_all(self) -> bool:
        return self.raw_data.get("is_all", True)