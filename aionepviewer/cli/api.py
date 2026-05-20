"""API subcommands — 1:1 mapping to NepViewer client methods, JSON output only."""

from __future__ import annotations

import argparse
from datetime import date

from ..client import NepViewer
from ..models import ChartType, DateStatisticsType
from . import dump_json


# ── handlers ───────────────────────────────────────────────────────────


async def _login(client: NepViewer, _args: argparse.Namespace) -> None:
    result = await client.authenticate()
    print(dump_json(result))


async def _logout(client: NepViewer, _args: argparse.Namespace) -> None:
    await client.authenticate()
    await client.logout()
    print('{"status": "logged out"}')


async def _account_info(client: NepViewer, _args: argparse.Namespace) -> None:
    print(dump_json(await client.get_account_info()))


async def _overview(client: NepViewer, _args: argparse.Namespace) -> None:
    print(dump_json(await client.get_overview()))


async def _site_status_counts(client: NepViewer, _args: argparse.Namespace) -> None:
    print(dump_json(await client.get_site_status_counts()))


async def _sites(client: NepViewer, _args: argparse.Namespace) -> None:
    print(dump_json(await client.get_sites()))


async def _site_detail(client: NepViewer, args: argparse.Namespace) -> None:
    print(dump_json(await client.get_site_detail(args.sid)))


async def _site_overview(client: NepViewer, args: argparse.Namespace) -> None:
    print(dump_json(await client.get_site_overview(args.sid)))


async def _site_modules(client: NepViewer, args: argparse.Namespace) -> None:
    print(dump_json(await client.get_site_modules(args.sid)))


async def _site_weather(client: NepViewer, args: argparse.Namespace) -> None:
    print(dump_json(await client.get_site_weather(args.sid)))


async def _site_layout(client: NepViewer, args: argparse.Namespace) -> None:
    print(dump_json(await client.get_site_layout(args.sid)))


async def _site_chart(client: NepViewer, args: argparse.Namespace) -> None:
    chart_type = ChartType(args.type)
    print(dump_json(
        await client.get_site_statistics_chart(
            args.sid, chart_type, date=args.date, range_date=args.range_date,
        )
    ))


async def _devices(client: NepViewer, _args: argparse.Namespace) -> None:
    print(dump_json(await client.get_devices()))


async def _device_detail(client: NepViewer, args: argparse.Namespace) -> None:
    print(dump_json(await client.get_device_detail(args.sid, args.sn)))


async def _device_stats(client: NepViewer, args: argparse.Namespace) -> None:
    print(dump_json(await client.get_device_statistics_overview(args.sn)))


async def _device_params(client: NepViewer, args: argparse.Namespace) -> None:
    print(dump_json(await client.get_device_power_parameters(args.sn)))


async def _device_chart(client: NepViewer, args: argparse.Namespace) -> None:
    chart_type = ChartType(args.type)
    print(dump_json(
        await client.get_device_statistics_chart(
            args.sn, chart_type, date=args.date, lines=args.lines or [],
        )
    ))


async def _device_energy(client: NepViewer, args: argparse.Namespace) -> None:
    date_str: str = args.date
    stat_type = DateStatisticsType.MONTH if len(date_str) == 7 else DateStatisticsType.DAY
    print(dump_json(await client.get_device_date_statistics(args.sn, stat_type, date_str)))


async def _device_playback(client: NepViewer, args: argparse.Namespace) -> None:
    print(dump_json(await client.get_device_playback(args.sn, args.date, args.date)))


async def _product_info(client: NepViewer, args: argparse.Namespace) -> None:
    print(dump_json(await client.get_product_info(args.sn)))


async def _device_wifi_ota(client: NepViewer, args: argparse.Namespace) -> None:
    devices = [(sn, "") for sn in args.sn]
    print(dump_json(await client.get_device_wifi_ota(devices)))


async def _report_settings(client: NepViewer, args: argparse.Namespace) -> None:
    print(dump_json(await client.get_report_settings(args.sid, args.sn)))


async def _report_setup(client: NepViewer, args: argparse.Namespace) -> None:
    await client.set_report_settings(
        args.sn,
        daily=args.daily,
        weekly=args.weekly,
        monthly=args.monthly,
        alert_start=args.alert_start,
        alert_end=args.alert_end,
    )
    print('{"status": "ok"}')


# ── registration ───────────────────────────────────────────────────────


def register_api_commands(parent_sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the ``api`` subcommand group with all 1:1 API mappings."""
    api_parser = parent_sub.add_parser(
        "api",
        help="Raw API commands (JSON output)",
        description="1:1 mapping to NEP API endpoints. Always outputs JSON.",
    )
    sub = api_parser.add_subparsers(dest="api_command", required=True)

    # login / logout / account
    p = sub.add_parser("login", help="Authenticate and return token info")
    p.set_defaults(func=_login)

    p = sub.add_parser("logout", help="Invalidate session token")
    p.set_defaults(func=_logout)

    p = sub.add_parser("account-info", help="User profile details")
    p.set_defaults(func=_account_info)

    # overview
    p = sub.add_parser("overview", help="Global overview (all sites)")
    p.set_defaults(func=_overview)

    p = sub.add_parser("site-status-counts", help="Online/offline site counts")
    p.set_defaults(func=_site_status_counts)

    # sites
    p = sub.add_parser("sites", help="List all sites")
    p.set_defaults(func=_sites)

    p = sub.add_parser("site-detail", help="Detailed site information")
    p.add_argument("sid", help="Site ID")
    p.set_defaults(func=_site_detail)

    p = sub.add_parser("site-overview", help="Site overview (production, energy flow)")
    p.add_argument("sid", help="Site ID")
    p.set_defaults(func=_site_overview)

    p = sub.add_parser("site-modules", help="Per-panel module data")
    p.add_argument("sid", help="Site ID")
    p.set_defaults(func=_site_modules)

    p = sub.add_parser("site-weather", help="7-day weather forecast")
    p.add_argument("sid", help="Site ID")
    p.set_defaults(func=_site_weather)

    p = sub.add_parser("site-layout", help="Site layout picture info")
    p.add_argument("sid", help="Site ID")
    p.set_defaults(func=_site_layout)

    p = sub.add_parser("site-chart", help="Site chart data")
    p.add_argument("sid", help="Site ID")
    p.add_argument("--type", type=int, required=True, help="ChartType (1=day, 3=daily, 5=monthly, 6=yearly, 11=intraday)")
    p.add_argument("--date", default=date.today().isoformat(), help="Date (YYYY-MM-DD)")
    p.add_argument("--range-date", default=None, help="Date range (YYYY-MM-DD~YYYY-MM-DD)")
    p.set_defaults(func=_site_chart)

    # devices
    p = sub.add_parser("devices", help="List all devices")
    p.set_defaults(func=_devices)

    p = sub.add_parser("device-detail", help="Detailed device information")
    p.add_argument("sid", help="Site ID")
    p.add_argument("sn", help="Device serial number")
    p.set_defaults(func=_device_detail)

    p = sub.add_parser("device-stats", help="Device statistics overview")
    p.add_argument("sn", help="Device serial number")
    p.set_defaults(func=_device_stats)

    p = sub.add_parser("device-params", help="Available power parameters")
    p.add_argument("sn", help="Device serial number")
    p.set_defaults(func=_device_params)

    p = sub.add_parser("device-chart", help="Device chart data")
    p.add_argument("sn", help="Device serial number")
    p.add_argument("--type", type=int, required=True, help="ChartType (1=day, 3=daily, 5=monthly, 6=yearly, 11=intraday)")
    p.add_argument("--date", default=date.today().isoformat(), help="Date (YYYY-MM-DD)")
    p.add_argument("--lines", nargs="*", default=[], help="Parameter line names")
    p.set_defaults(func=_device_chart)

    p = sub.add_parser("device-energy", help="Power/consumption/economic for a period")
    p.add_argument("sn", help="Device serial number")
    p.add_argument("date", help="Date: YYYY-MM-DD (day) or YYYY-MM (month)")
    p.set_defaults(func=_device_energy)

    p = sub.add_parser("device-playback", help="5-min playback data")
    p.add_argument("sn", help="Device serial number")
    p.add_argument("--date", default=date.today().isoformat(), help="Date (YYYY-MM-DD)")
    p.set_defaults(func=_device_playback)

    p = sub.add_parser("product-info", help="Product model and capabilities")
    p.add_argument("sn", nargs="+", help="One or more device serial numbers")
    p.set_defaults(func=_product_info)

    p = sub.add_parser("device-wifi-ota", help="WiFi firmware OTA status")
    p.add_argument("sn", nargs="+", help="One or more device serial numbers")
    p.set_defaults(func=_device_wifi_ota)

    # reports
    p = sub.add_parser("report-settings", help="Report notification settings")
    p.add_argument("sid", help="Site ID")
    p.add_argument("sn", help="Device serial number")
    p.set_defaults(func=_report_settings)

    p = sub.add_parser("report-setup", help="Configure report notifications")
    p.add_argument("sn", help="Device serial number")
    p.add_argument("--daily", action="store_true", help="Enable daily reports")
    p.add_argument("--weekly", action="store_true", help="Enable weekly reports")
    p.add_argument("--monthly", action="store_true", help="Enable monthly reports")
    p.add_argument("--alert-start", default="8", help="Alert window start hour (default: 8)")
    p.add_argument("--alert-end", default="17", help="Alert window end hour (default: 17)")
    p.set_defaults(func=_report_setup)
