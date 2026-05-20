"""Human-friendly commands with rich formatting, colors, and --watch support."""

from __future__ import annotations

import argparse
import asyncio
import sys
from datetime import datetime
from typing import Any

from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich.live import Live

from ..client import NepViewer
from . import resolve_sid

console = Console()

WATCH_INTERVAL = 300  # 5 minutes


# ── formatting helpers ─────────────────────────────────────────────────


def _status_badge(is_online: bool) -> Text:
    if is_online:
        return Text(" ONLINE ", style="bold white on green")
    return Text(" OFFLINE ", style="bold white on red")


def _status_dot(is_online: bool) -> str:
    return "[green]●[/green]" if is_online else "[red]●[/red]"


def _alert_text(code: str, title: str) -> str:
    if code == "0000":
        return "[green]OK[/green]"
    return f"[bold red]{title}[/bold red]"


def _power_color(value: float, max_value: float = 2000) -> str:
    """Return a rich color tag based on power output relative to max."""
    if value <= 0:
        return "dim"
    ratio = min(value / max_value, 1.0)
    if ratio > 0.7:
        return "bold green"
    if ratio > 0.3:
        return "green"
    return "yellow"


WEATHER_ICONS = {
    "clear-day": "☀️ ",
    "clear-night": "🌙",
    "cloudy": "☁️ ",
    "fog": "🌫️ ",
    "partly-cloudy-day": "⛅",
    "partly-cloudy-night": "☁️ ",
    "rain": "🌧️ ",
    "showers-day": "🌦️ ",
    "showers-night": "🌧️ ",
    "snow": "❄️ ",
    "thunder-rain": "⛈️ ",
    "thunder-showers-day": "⛈️ ",
    "wind": "💨",
}


# ── renderers (return Rich renderables for use with Live) ─────────────


async def _render_status(client: NepViewer) -> Group:
    """Build the status dashboard renderable."""
    overview, sites, devices = await asyncio.gather(
        client.get_overview(),
        client.get_sites(),
        client.get_devices(),
    )

    # Header panel
    prod = overview.production
    header = Table.grid(padding=(0, 3))
    header.add_column(style="bold cyan")
    header.add_column()
    header.add_row("Current Power", f"[bold yellow]{prod.total_now}[/bold yellow] {prod.total_now_unit}")
    header.add_row("Today", f"{prod.today} {prod.today_unit}")
    header.add_row("This Month", f"{prod.month} {prod.month_unit}")
    header.add_row("This Year", f"{prod.year} {prod.year_unit}")
    header.add_row("Lifetime", f"[bold]{prod.total}[/bold] {prod.total_unit}")
    header.add_row("Revenue", f"[green]{prod.total_money}[/green] {prod.total_money_unit}")

    benefit = overview.benefit
    header.add_row("", "")
    header.add_row("CO₂ Avoided", f"{benefit.co2} {benefit.co2_unit}")
    header.add_row("Trees Equivalent", f"{benefit.tree} {benefit.tree_unit}")

    header_panel = Panel(
        header,
        title=f"[bold]NEP Solar Dashboard[/bold]  ({overview.site_count} sites, {overview.device_count} devices)",
        border_style="cyan",
    )

    # Sites table
    site_table = Table(title="Sites", show_header=True, header_style="bold")
    site_table.add_column("Status", width=3, justify="center")
    site_table.add_column("Name", style="cyan")
    site_table.add_column("Location")
    site_table.add_column("Power", justify="right")
    site_table.add_column("Today", justify="right")
    site_table.add_column("Lifetime", justify="right")
    site_table.add_column("Devices", justify="center")

    for s in sites:
        site_table.add_row(
            _status_dot(s.is_online),
            s.site_name,
            f"{s.city}, {s.country_name}",
            f"[{_power_color(s.now)}]{s.now}[/] {s.now_unit}",
            f"{s.today_power} {s.today_power_unit}",
            f"{s.total_power} {s.total_power_unit}",
            str(s.sn_count),
        )

    # Devices table
    dev_table = Table(title="Devices", show_header=True, header_style="bold")
    dev_table.add_column("Status", width=3, justify="center")
    dev_table.add_column("Serial Number", style="cyan")
    dev_table.add_column("Model")
    dev_table.add_column("Power", justify="right")
    dev_table.add_column("Alert")
    dev_table.add_column("Last Update", style="dim")

    for d in devices:
        dev_table.add_row(
            _status_dot(d.is_online),
            d.sn,
            d.model_name,
            f"[{_power_color(d.now)}]{d.now}[/] {d.now_unit}",
            _alert_text(d.alert_code, d.alert_title),
            d.last_update_cal,
        )

    timestamp = Text(f"\n  Last refresh: {datetime.now().strftime('%H:%M:%S')}", style="dim")

    return Group(header_panel, "", site_table, "", dev_table, timestamp)


async def _render_live(client: NepViewer, sid: str) -> Group:
    """Build the live site view renderable."""
    overview, modules_data = await asyncio.gather(
        client.get_site_overview(sid),
        client.get_site_modules(sid),
    )

    # Energy flow
    energy = overview.energy
    flow_grid = Table.grid(padding=(0, 2))
    flow_grid.add_column(justify="center")
    flow_grid.add_column(justify="center")
    flow_grid.add_column(justify="center")

    pv_text = f"[bold yellow]☀ PV Panel[/bold yellow]\n{energy.pv_panel.power} {energy.pv_panel.power_unit}"
    home_text = f"[bold blue]🏠 Home[/bold blue]\n{energy.home.power} {energy.home.power_unit}"
    grid_text = f"[bold white]⚡ Grid[/bold white]\n{energy.grid.power} {energy.grid.power_unit}"

    flow_grid.add_row(pv_text, "  →  ", home_text)
    if energy.grid.show:
        direction = "→" if energy.grid.direction == 1 else "←"
        flow_grid.add_row("", f"  {direction}  ", grid_text)

    if energy.battery.show:
        batt_text = f"[bold magenta]🔋 Battery[/bold magenta]\n{energy.battery.power} {energy.battery.power_unit}"
        flow_grid.add_row("", "  ↕  ", batt_text)

    flow_panel = Panel(flow_grid, title="Energy Flow", border_style="yellow")

    # Production stats
    prod = overview.production
    prod_table = Table.grid(padding=(0, 3))
    prod_table.add_column(style="bold")
    prod_table.add_column()
    prod_table.add_row("Current", f"[bold yellow]{prod.total_now}[/bold yellow] {prod.total_now_unit}")
    prod_table.add_row("Today", f"{prod.today} {prod.today_unit}  ([green]{prod.today_money}[/green] {prod.total_money_unit})")
    prod_table.add_row("Month", f"{prod.month} {prod.month_unit}")
    prod_table.add_row("Year", f"{prod.year} {prod.year_unit}")
    prod_table.add_row("Lifetime", f"[bold]{prod.total}[/bold] {prod.total_unit}")

    prod_panel = Panel(prod_table, title="Production", border_style="green")

    # Modules
    mod_table = Table(title="Panel Modules", show_header=True, header_style="bold")
    mod_table.add_column("Panel", style="cyan")
    mod_table.add_column("Addr", justify="center")
    mod_table.add_column("Power", justify="right")
    mod_table.add_column("Today", justify="right")
    mod_table.add_column("Total", justify="right")
    mod_table.add_column("Status")

    for dev in modules_data.devices:
        for m in dev.modules:
            color = _power_color(m.now)
            alert = ""
            if m.status != "0000":
                alert = f"[red] ⚠ {m.status}[/red]"
            mod_table.add_row(
                m.plc_sn,
                str(m.addr),
                f"[{color}]{m.now}[/] {m.now_unit}",
                f"{m.today_power} {m.today_power_unit}",
                f"{m.total_power} {m.total_power_unit}",
                f"[green]OK[/green]{alert}" if not alert else alert,
            )

    # Alert
    parts: list[Any] = [Columns([flow_panel, prod_panel], equal=True, expand=True), "", mod_table]

    if not overview.alert.is_ok:
        alert_panel = Panel(
            f"[bold red]{overview.alert.title}[/bold red]\n{overview.alert.description}",
            title="⚠ Alert",
            border_style="red",
        )
        parts.append("")
        parts.append(alert_panel)

    status = _status_badge(overview.is_online)
    timestamp = Text(f"\n  Last refresh: {datetime.now().strftime('%H:%M:%S')}  |  Updated: {overview.last_update_cal}", style="dim")
    parts.append(timestamp)

    return Group(*parts)


async def _render_modules(client: NepViewer, sid: str) -> Group:
    """Build the modules view renderable."""
    modules_data = await client.get_site_modules(sid)

    parts: list[Any] = []
    for dev in modules_data.devices:
        status = _status_dot(dev.status == 0)
        table = Table(
            title=f"{status} Device {dev.sn} ({dev.model_name})",
            show_header=True,
            header_style="bold",
        )
        table.add_column("Panel SN", style="cyan")
        table.add_column("Addr", justify="center")
        table.add_column("Power", justify="right")
        table.add_column("Today", justify="right")
        table.add_column("Total", justify="right")
        table.add_column("Status")

        for m in dev.modules:
            color = _power_color(m.now)
            alert = ""
            if m.status != "0000":
                alert = f"[red]⚠ {m.status}[/red]"
            table.add_row(
                m.plc_sn,
                str(m.addr),
                f"[{color}]{m.now}[/] {m.now_unit}",
                f"{m.today_power} {m.today_power_unit}",
                f"{m.total_power} {m.total_power_unit}",
                f"[green]OK[/green]" if not alert else alert,
            )

        if dev.alert_code and dev.alert_code != "0000":
            table.caption = f"[red]Alert: {dev.alert_title}[/red]"

        parts.append(table)
        parts.append("")

    timestamp = Text(f"  Last refresh: {datetime.now().strftime('%H:%M:%S')}", style="dim")
    parts.append(timestamp)

    return Group(*parts)


async def _render_weather(client: NepViewer, sid: str) -> Group:
    """Build the weather view renderable."""
    weather = await client.get_site_weather(sid)

    table = Table(
        title=f"7-Day Weather Forecast ({weather.temperature_unit})",
        show_header=True,
        header_style="bold",
    )
    table.add_column("Date")
    table.add_column("Day", style="cyan")
    table.add_column("", width=3)
    table.add_column("Conditions")
    table.add_column("Low", justify="right", style="blue")
    table.add_column("High", justify="right", style="red")

    for day in weather.forecasts:
        icon = WEATHER_ICONS.get(day.icon, "  ")
        table.add_row(
            day.datetime,
            day.week,
            icon,
            day.conditions,
            f"{day.temp_min}°",
            f"{day.temp_max}°",
        )

    return Group("", table, "")


# ── command handlers ───────────────────────────────────────────────────


async def _cmd_status(client: NepViewer, args: argparse.Namespace) -> None:
    """Quick dashboard: overview + sites + devices."""
    if args.watch:
        with Live(console=console, refresh_per_second=0.5) as live:
            while True:
                try:
                    content = await _render_status(client)
                    live.update(content)
                    await asyncio.sleep(WATCH_INTERVAL)
                except KeyboardInterrupt:
                    break
    else:
        content = await _render_status(client)
        console.print(content)


async def _cmd_live(client: NepViewer, args: argparse.Namespace) -> None:
    """Live site view: energy flow + modules."""
    sid = await resolve_sid(client, args.sid)

    if args.watch:
        with Live(console=console, refresh_per_second=0.5) as live:
            while True:
                try:
                    content = await _render_live(client, sid)
                    live.update(content)
                    await asyncio.sleep(WATCH_INTERVAL)
                except KeyboardInterrupt:
                    break
    else:
        content = await _render_live(client, sid)
        console.print(content)


async def _cmd_modules(client: NepViewer, args: argparse.Namespace) -> None:
    """Per-panel module view."""
    sid = await resolve_sid(client, args.sid)

    if args.watch:
        with Live(console=console, refresh_per_second=0.5) as live:
            while True:
                try:
                    content = await _render_modules(client, sid)
                    live.update(content)
                    await asyncio.sleep(WATCH_INTERVAL)
                except KeyboardInterrupt:
                    break
    else:
        content = await _render_modules(client, sid)
        console.print(content)


async def _cmd_weather(client: NepViewer, args: argparse.Namespace) -> None:
    """7-day weather forecast."""
    sid = await resolve_sid(client, args.sid)
    content = await _render_weather(client, sid)
    console.print(content)


# ── registration ───────────────────────────────────────────────────────


def register_dashboard_commands(parent_sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register human-friendly dashboard commands."""

    # status
    p = parent_sub.add_parser(
        "status",
        help="Dashboard: overview of all sites and devices",
    )
    p.add_argument("--watch", "-w", action="store_true", help="Auto-refresh every 5 minutes")
    p.set_defaults(func=_cmd_status)

    # live
    p = parent_sub.add_parser(
        "live",
        help="Live site view: energy flow, production, modules",
    )
    p.add_argument("sid", nargs="?", default=None, help="Site ID (auto-detected if omitted)")
    p.add_argument("--watch", "-w", action="store_true", help="Auto-refresh every 5 minutes")
    p.set_defaults(func=_cmd_live)

    # modules
    p = parent_sub.add_parser(
        "modules",
        help="Per-panel module status with color-coded power",
    )
    p.add_argument("sid", nargs="?", default=None, help="Site ID (auto-detected if omitted)")
    p.add_argument("--watch", "-w", action="store_true", help="Auto-refresh every 5 minutes")
    p.set_defaults(func=_cmd_modules)

    # weather
    p = parent_sub.add_parser(
        "weather",
        help="7-day weather forecast for a site",
    )
    p.add_argument("sid", nargs="?", default=None, help="Site ID (auto-detected if omitted)")
    p.set_defaults(func=_cmd_weather)
