"""Command-line interface for aionepviewer."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from dataclasses import asdict
from datetime import date, timedelta
from getpass import getpass
from typing import Any

import aiohttp

from .client import NepViewer
from .const import DEFAULT_HOST
from .exceptions import NepAuthError, NepError
from .models import ChartType, DateStatisticsType


def _make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aionepviewer",
        description="CLI for the NEP solar inverter cloud API (nepviewer.net)",
    )
    parser.add_argument(
        "--email", "-e", help="NEP account email (or set AIONEPVIEWER_EMAIL env var)"
    )
    parser.add_argument(
        "--password", "-p", help="NEP account password (or set AIONEPVIEWER_PASSWORD env var)"
    )
    parser.add_argument(
        "--host", default=DEFAULT_HOST, help=f"API host (default: {DEFAULT_HOST})"
    )
    parser.add_argument(
        "--json", "-j", action="store_true", dest="as_json", help="Output raw JSON"
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # ── login ──────────────────────────────────────────────────────────
    sub.add_parser("login", help="Verify credentials")

    # ── overview ───────────────────────────────────────────────────────
    sub.add_parser("overview", help="Global overview (all sites)")

    # ── sites ──────────────────────────────────────────────────────────
    sub.add_parser("sites", help="List all sites")

    # ── site-detail ────────────────────────────────────────────────────
    p = sub.add_parser("site-detail", help="Detailed site information")
    p.add_argument("sid", help="Site ID")

    # ── site-overview ──────────────────────────────────────────────────
    p = sub.add_parser("site-overview", help="Site overview (production, energy flow)")
    p.add_argument("sid", help="Site ID")

    # ── site-modules ───────────────────────────────────────────────────
    p = sub.add_parser("site-modules", help="Per-panel module data for a site")
    p.add_argument("sid", help="Site ID")

    # ── site-weather ───────────────────────────────────────────────────
    p = sub.add_parser("site-weather", help="7-day weather forecast for a site")
    p.add_argument("sid", help="Site ID")

    # ── devices ────────────────────────────────────────────────────────
    sub.add_parser("devices", help="List all devices")

    # ── device-detail ──────────────────────────────────────────────────
    p = sub.add_parser("device-detail", help="Detailed device information")
    p.add_argument("sid", help="Site ID")
    p.add_argument("sn", help="Device serial number")

    # ── device-stats ───────────────────────────────────────────────────
    p = sub.add_parser("device-stats", help="Device statistics overview")
    p.add_argument("sn", help="Device serial number")

    # ── device-params ──────────────────────────────────────────────────
    p = sub.add_parser("device-params", help="Available power parameters for a device")
    p.add_argument("sn", help="Device serial number")

    # ── device-energy ──────────────────────────────────────────────────
    p = sub.add_parser(
        "device-energy",
        help="Power/consumption/economic for a day or month",
    )
    p.add_argument("sn", help="Device serial number")
    p.add_argument(
        "date",
        help="Date: YYYY-MM-DD (day) or YYYY-MM (month)",
    )

    # ── device-playback ────────────────────────────────────────────────
    p = sub.add_parser(
        "device-playback", help="5-min playback data for a device"
    )
    p.add_argument("sn", help="Device serial number")
    p.add_argument(
        "--date",
        default=date.today().isoformat(),
        help="Date (YYYY-MM-DD, default: today)",
    )

    # ── product-info ────────────────────────────────────────────────────
    p = sub.add_parser("product-info", help="Product model and capabilities by SN")
    p.add_argument("sn", nargs="+", help="One or more device serial numbers")

    # ── device-wifi-ota ─────────────────────────────────────────────────
    p = sub.add_parser("device-wifi-ota", help="WiFi firmware OTA status")
    p.add_argument("sn", nargs="+", help="One or more device serial numbers")

    # ── site-layout ─────────────────────────────────────────────────────
    p = sub.add_parser("site-layout", help="Site layout picture info")
    p.add_argument("sid", help="Site ID")

    return parser


# ── helpers ────────────────────────────────────────────────────────────


def _get_credentials(
    args: argparse.Namespace,
) -> tuple[str, str]:
    import os

    email = args.email or os.environ.get("AIONEPVIEWER_EMAIL", "")
    password = args.password or os.environ.get("AIONEPVIEWER_PASSWORD", "")
    if not email:
        email = input("Email: ")
    if not password:
        password = getpass("Password: ")
    return email, password


def _dump_json(obj: Any) -> str:
    if hasattr(obj, "__dataclass_fields__"):
        return json.dumps(asdict(obj), indent=2, default=str)
    if isinstance(obj, list):
        items = [asdict(o) if hasattr(o, "__dataclass_fields__") else o for o in obj]
        return json.dumps(items, indent=2, default=str)
    return json.dumps(obj, indent=2, default=str)


def _header(text: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}\n")


def _kv(label: str, value: Any, unit: str = "") -> None:
    suffix = f" {unit}" if unit else ""
    print(f"  {label:<30s} {value}{suffix}")


# ── command handlers ───────────────────────────────────────────────────


async def _cmd_login(client: NepViewer, _args: argparse.Namespace) -> Any:
    auth = await client.authenticate()
    _header("Login successful")
    _kv("User ID", auth.user_info.uid)
    _kv("Email", auth.user_info.email)
    _kv("Country", auth.user_info.country)
    _kv("Sites", auth.site_count)
    return auth


async def _cmd_overview(client: NepViewer, _args: argparse.Namespace) -> Any:
    ov = await client.get_overview()
    _header("Global Overview")
    _kv("Sites", ov.site_count)
    _kv("Devices", ov.device_count)
    _kv("Microinverters", ov.mr_count)
    print()
    _kv("Current power", ov.production.total_now, ov.production.total_now_unit)
    _kv("Today", ov.production.today, ov.production.today_unit)
    _kv("Yesterday", ov.production.yesterday, ov.production.yesterday_unit)
    _kv("This month", ov.production.month, ov.production.month_unit)
    _kv("This year", ov.production.year, ov.production.year_unit)
    _kv("Lifetime", ov.production.total, ov.production.total_unit)
    _kv("Total revenue", ov.production.total_money, ov.production.total_money_unit)
    print()
    _kv("CO2 avoided", ov.benefit.co2, ov.benefit.co2_unit)
    _kv("Trees equivalent", ov.benefit.tree, ov.benefit.tree_unit)
    return ov


async def _cmd_sites(client: NepViewer, _args: argparse.Namespace) -> Any:
    sites = await client.get_sites()
    _header(f"Sites ({len(sites)})")
    for s in sites:
        status = "ONLINE" if s.is_online else "OFFLINE"
        print(f"  [{status}] {s.site_name} (sid={s.sid})")
        _kv("    Location", f"{s.city}, {s.state_name}, {s.country_name}")
        _kv("    Devices", s.sn_count)
        _kv("    Current power", s.now, s.now_unit)
        _kv("    Today", s.today_power, s.today_power_unit)
        _kv("    Lifetime", s.total_power, s.total_power_unit)
        for d in s.devices:
            print(f"      SN {d.sn} ({d.model}) - {d.now} {d.now_unit}")
        print()
    return sites


async def _cmd_site_detail(client: NepViewer, args: argparse.Namespace) -> Any:
    detail = await client.get_site_detail(args.sid)
    _header(f"Site Detail: {detail.site_name}")
    _kv("Site ID", detail.sid)
    _kv("Location", f"{detail.city}, {detail.state_name}, {detail.country_name}")
    _kv("Address", detail.street)
    _kv("ZIP", detail.zip_code)
    _kv("Timezone", detail.timezone)
    _kv("Coordinates", f"{detail.latitude}, {detail.longitude}")
    _kv("Currency", detail.currency)
    _kv("Electricity price", detail.electricity_price, detail.currency)
    _kv("Panel model", detail.panel_model)
    _kv("Panel type", detail.panel_type)
    _kv("Power rating", detail.power_rating, "kW")
    _kv("Max power", detail.power_max, "kW")
    _kv("Registered", detail.register_date)
    _kv("Company", detail.company_name)
    return detail


async def _cmd_site_overview(client: NepViewer, args: argparse.Namespace) -> Any:
    ov = await client.get_site_overview(args.sid)
    status = "ONLINE" if ov.is_online else "OFFLINE"
    _header(f"Site Overview [{status}]")

    print("  Production:")
    _kv("    Current power", ov.production.total_now, ov.production.total_now_unit)
    _kv("    Today", ov.production.today, ov.production.today_unit)
    _kv("    Yesterday", ov.production.yesterday, ov.production.yesterday_unit)
    _kv("    This month", ov.production.month, ov.production.month_unit)
    _kv("    This year", ov.production.year, ov.production.year_unit)
    _kv("    Lifetime", ov.production.total, ov.production.total_unit)
    _kv("    Total revenue", ov.production.total_money, ov.production.total_money_unit)

    print("\n  Energy Flow:")
    _kv("    PV Panel", ov.energy.pv_panel.power, ov.energy.pv_panel.power_unit)
    _kv("    Home", ov.energy.home.power, ov.energy.home.power_unit)
    _kv("    Grid", ov.energy.grid.power, ov.energy.grid.power_unit)
    if ov.energy.battery.show:
        _kv("    Battery", ov.energy.battery.power, ov.energy.battery.power_unit)
    if ov.energy.generator.show:
        _kv("    Generator", ov.energy.generator.power, ov.energy.generator.power_unit)

    if not ov.alert.is_ok:
        print(f"\n  Alert: {ov.alert.title}")
        print(f"    {ov.alert.description}")

    print(f"\n  Devices ({len(ov.device_list)}):")
    for d in ov.device_list:
        status_d = "ONLINE" if d.status == 0 else "OFFLINE"
        print(f"    [{status_d}] {d.sn} ({d.model_name}) - {d.now} {d.now_unit}")
    return ov


async def _cmd_site_modules(client: NepViewer, args: argparse.Namespace) -> Any:
    data = await client.get_site_modules(args.sid)
    _header(f"Site Modules ({data.total_plc} panels)")
    for dev in data.devices:
        status = "ONLINE" if dev.status == 0 else "OFFLINE"
        print(f"  Device {dev.sn} ({dev.model_name}) [{status}]")
        if dev.alert_code and dev.alert_code != "0000":
            print(f"    Alert: {dev.alert_title}")
        for m in dev.modules:
            alert = "" if m.status == "0000" else f" [!{m.status}]"
            print(
                f"    Panel {m.addr} ({m.plc_sn}): "
                f"{m.now} {m.now_unit} | "
                f"today {m.today_power} {m.today_power_unit} | "
                f"total {m.total_power} {m.total_power_unit}"
                f"{alert}"
            )
        print()
    return data


async def _cmd_site_weather(client: NepViewer, args: argparse.Namespace) -> Any:
    weather = await client.get_site_weather(args.sid)
    _header(f"7-Day Weather ({weather.temperature_unit})")
    for day in weather.forecasts:
        print(
            f"  {day.datetime} ({day.week}): "
            f"{day.temp_min}-{day.temp_max} deg, {day.conditions}"
        )
    return weather


async def _cmd_devices(client: NepViewer, _args: argparse.Namespace) -> Any:
    devices = await client.get_devices()
    _header(f"Devices ({len(devices)})")
    for d in devices:
        status = "ONLINE" if d.is_online else "OFFLINE"
        alert = "" if d.alert_code == "0000" else f" [{d.alert_title}]"
        print(
            f"  [{status}] {d.sn} ({d.model_name}) - "
            f"{d.now} {d.now_unit}{alert}"
        )
        _kv("    Site", f"{d.site_name} (sid={d.sid})")
        _kv("    Location", f"{d.city}, {d.state_name}, {d.country_name}")
        _kv("    WiFi version", d.wifi_version)
        _kv("    Last update", d.last_update_cal)
        print()
    return devices


async def _cmd_device_detail(client: NepViewer, args: argparse.Namespace) -> Any:
    detail = await client.get_device_detail(args.sid, args.sn)
    _header(f"Device Detail: {detail.sn}")
    _kv("Model", f"{detail.model} ({detail.model_title})")
    _kv("Firmware", detail.version)
    _kv("Site", detail.site_name)
    _kv("Location", f"{detail.city}, {detail.state_name}, {detail.country_name}")
    _kv("Timezone", detail.timezone)
    _kv("Coordinates", f"{detail.latitude}, {detail.longitude}")
    _kv("WiFi version", detail.wifi_version)
    _kv("Power max", detail.power_max, "kW")
    _kv("Power rating", detail.power_rating, "kW")
    _kv("Connection type", detail.connection_type)
    _kv("Currency", detail.currency_unit)
    _kv("Electricity price", detail.local_electric_price, detail.currency_unit)
    _kv("Registered", detail.register_date)
    return detail


async def _cmd_device_stats(client: NepViewer, args: argparse.Namespace) -> Any:
    stats = await client.get_device_statistics_overview(args.sn)
    status = "ONLINE" if stats.is_online else "OFFLINE"
    _header(f"Device Statistics: {args.sn} [{status}]")

    if stats.alert_code and stats.alert_code != "0000":
        print(f"  Alert: {stats.alert_title}")
        print(f"    {stats.alert_description}\n")

    print("  Production:")
    _kv("    Current power", stats.total_now, stats.total_now_unit)
    _kv("    Today", stats.production.today, stats.production.today_unit)
    _kv("    Yesterday", stats.production.yesterday, stats.production.yesterday_unit)
    _kv("    This month", stats.production.month, stats.production.month_unit)
    _kv("    This year", stats.production.year, stats.production.year_unit)
    _kv("    Lifetime", stats.production.total, stats.production.total_unit)

    print("\n  Energy Flow:")
    _kv("    PV Panel", stats.energy.pv_panel.power, stats.energy.pv_panel.power_unit)
    _kv("    Home", stats.energy.home.power, stats.energy.home.power_unit)
    _kv("    Grid", stats.energy.grid.power, stats.energy.grid.power_unit)
    if stats.energy.battery.show:
        _kv("    Battery", stats.energy.battery.power, stats.energy.battery.power_unit)

    print("\n  Environmental Benefit:")
    _kv("    CO2 avoided", stats.environmental_benefit.co2, stats.environmental_benefit.co2_unit)
    _kv("    Trees", stats.environmental_benefit.tree, stats.environmental_benefit.tree_unit)
    _kv("    Car km", stats.environmental_benefit.car, stats.environmental_benefit.car_unit)

    _kv("\n  Last update", stats.last_update)
    return stats


async def _cmd_device_params(client: NepViewer, args: argparse.Namespace) -> Any:
    params = await client.get_device_power_parameters(args.sn)
    _header(f"Power Parameters: {args.sn}")
    for p in params:
        print(f"  {p.name:<25s} ({p.unit})")
    return params


async def _cmd_device_energy(client: NepViewer, args: argparse.Namespace) -> Any:
    date_str: str = args.date
    if len(date_str) == 7:  # YYYY-MM
        stat_type = DateStatisticsType.MONTH
    else:
        stat_type = DateStatisticsType.DAY
    stats = await client.get_device_date_statistics(args.sn, stat_type, date_str)
    _header(f"Energy Statistics: {args.sn} ({date_str})")
    _kv("Power", stats.power, stats.power_unit)
    _kv("Consumption", stats.consumption, stats.consumption_unit)
    _kv("Economic value", stats.economic, stats.economic_unit)
    return stats


async def _cmd_device_playback(client: NepViewer, args: argparse.Namespace) -> Any:
    pb = await client.get_device_playback(args.sn, args.date, args.date)
    _header(f"Playback: {args.sn} ({args.date})")
    print("  Time-series overview (total power):")
    non_zero = [
        (t, v)
        for t, v in zip(pb.overview.x_axis_data, pb.overview.series[0].data)
        if v and v > 0
    ]
    if non_zero:
        peak_time, peak_val = max(non_zero, key=lambda x: x[1])
        _kv("  Peak", f"{peak_val} W at {peak_time}")
        _kv("  Active intervals", len(non_zero))
    else:
        print("    No production data for this date.")

    if pb.modules:
        print(f"\n  Modules ({len(pb.modules)}):")
        for m in pb.modules:
            total = sum(m.data)
            peak = max(m.data) if m.data else 0
            print(f"    {m.plc_sn} (addr {m.addr}): peak {peak} W, sum {total}")
    return pb


async def _cmd_product_info(client: NepViewer, args: argparse.Namespace) -> Any:
    products = await client.get_product_info(args.sn)
    _header(f"Product Info ({len(products)} results)")
    for p in products:
        exists = "registered" if p.is_exist else "not registered"
        print(f"  {p.sn} - {p.model_name} (model {p.model}) [{exists}]")
        if p.functions:
            print("    Capabilities:")
            for f in p.functions:
                signals = []
                if f.signal_mqtt:
                    signals.append("MQTT")
                if f.signal_bluetooth:
                    signals.append("Bluetooth")
                if f.signal_at:
                    signals.append("AT")
                if f.signal_ap:
                    signals.append("AP")
                sig_str = ", ".join(signals) if signals else "none"
                print(f"      {f.func_name} (via {sig_str})")
        print()
    return products


async def _cmd_device_wifi_ota(client: NepViewer, args: argparse.Namespace) -> Any:
    devices = [(sn, "") for sn in args.sn]
    results = await client.get_device_wifi_ota(devices)
    _header(f"WiFi OTA Status ({len(results)} devices)")
    for d in results:
        update = "UPDATE AVAILABLE" if d.update_available else "up to date"
        print(f"  {d.sn} - WiFi {d.wifi_version or 'unknown'} [{update}]")
        if d.address:
            _kv("    Download", d.address)
    return results


async def _cmd_site_layout(client: NepViewer, args: argparse.Namespace) -> Any:
    layout = await client.get_site_layout(args.sid)
    _header(f"Site Layout: {layout.site_name}")
    _kv("Site ID", layout.sid)
    _kv("Layout picture", layout.layout_pic or "(none)")
    _kv("Layout scale", layout.layout_scale)
    return layout


# ── dispatch ───────────────────────────────────────────────────────────

COMMANDS = {
    "login": _cmd_login,
    "overview": _cmd_overview,
    "sites": _cmd_sites,
    "site-detail": _cmd_site_detail,
    "site-overview": _cmd_site_overview,
    "site-modules": _cmd_site_modules,
    "site-weather": _cmd_site_weather,
    "devices": _cmd_devices,
    "device-detail": _cmd_device_detail,
    "device-stats": _cmd_device_stats,
    "device-params": _cmd_device_params,
    "device-energy": _cmd_device_energy,
    "device-playback": _cmd_device_playback,
    "product-info": _cmd_product_info,
    "device-wifi-ota": _cmd_device_wifi_ota,
    "site-layout": _cmd_site_layout,
}


async def _async_main(args: argparse.Namespace) -> None:
    email, password = _get_credentials(args)
    async with aiohttp.ClientSession() as session:
        client = NepViewer(session, email, password, args.host)
        handler = COMMANDS[args.command]
        result = await handler(client, args)
        if args.as_json:
            print(_dump_json(result))


def main() -> None:
    parser = _make_parser()
    args = parser.parse_args()
    try:
        asyncio.run(_async_main(args))
    except NepAuthError as exc:
        print(f"Authentication failed: {exc}", file=sys.stderr)
        sys.exit(1)
    except NepError as exc:
        print(f"API error: {exc}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == "__main__":
    main()