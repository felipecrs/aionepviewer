"""Human-friendly dashboard commands with rich formatting and --watch support."""

from __future__ import annotations

import argparse
import asyncio
from collections.abc import Awaitable, Callable
from datetime import datetime
from typing import Any

from rich.console import Console, Group
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich.live import Live

from ..client import NepViewer
from ..models import SiteModulesData, SiteOverview

console = Console()

WATCH_INTERVAL = 300  # 5 minutes


# ── formatting helpers ─────────────────────────────────────────────────


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


# ── site detail renderable ────────────────────────────────────────────


def _build_site_detail(
    overview: SiteOverview,
    modules_data: SiteModulesData,
) -> list[Any]:
    """Return Rich renderables for a single site's detail section."""
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

    parts: list[Any] = [Columns([flow_panel, prod_panel], equal=True, expand=True)]

    # Modules grouped by device
    for dev in modules_data.devices:
        status = _status_dot(dev.status == 0)
        table = Table(
            title=f"{status} {dev.sn} ({dev.model_name})",
            show_header=True,
            header_style="bold",
        )
        table.add_column("Panel", style="cyan")
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
        parts.append("")
        parts.append(table)

    # Site-level alert
    if not overview.alert.is_ok:
        parts.append("")
        parts.append(Panel(
            f"[bold red]{overview.alert.title}[/bold red]\n{overview.alert.description}",
            title="⚠ Alert",
            border_style="red",
        ))

    return parts


# ── renderers ─────────────────────────────────────────────────────────


async def _render_status(client: NepViewer, site_filter: str | None) -> Group:
    """Build the full status dashboard.

    If *site_filter* is ``None``, show the global overview header followed
    by detail for every site.  If a site ID is given, show only that site.
    """
    sites = await client.get_sites()
    if site_filter:
        sites = [s for s in sites if s.sid == site_filter]

    # When showing all sites, fetch the global overview for the header
    show_overview = site_filter is None
    overview = await client.get_overview() if show_overview else None

    # Fetch detail for each site in parallel
    site_data: list[tuple[str, SiteOverview, SiteModulesData]] = []
    for s in sites:
        so, sm = await asyncio.gather(
            client.get_site_overview(s.sid),
            client.get_site_modules(s.sid),
        )
        site_data.append((s.site_name, so, sm))

    parts: list[Any] = []

    # Global overview header (only when not filtering)
    if overview is not None:
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

        parts.append(Panel(
            header,
            title=f"[bold]NEP Solar Dashboard[/bold]  ({overview.site_count} sites, {overview.device_count} devices)",
            border_style="cyan",
        ))

    # Per-site detail sections
    for name, so, sm in site_data:
        if len(site_data) > 1 or show_overview:
            parts.append("")
            parts.append(Rule(f"[bold]{name}[/bold]"))
        parts.extend(_build_site_detail(so, sm))

    parts.append(Text(f"\n  Last refresh: {datetime.now().strftime('%H:%M:%S')}", style="dim"))
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


# ── display / watch helper ─────────────────────────────────────────────


async def _display(
    render: Callable[[], Awaitable[Group]],
    *,
    watch: bool = False,
) -> None:
    """Print a renderable once, or auto-refresh it in a Live context."""
    if watch:
        with Live(console=console, refresh_per_second=0.5) as live:
            while True:
                try:
                    live.update(await render())
                    await asyncio.sleep(WATCH_INTERVAL)
                except KeyboardInterrupt:
                    break
    else:
        console.print(await render())


# ── command handlers ───────────────────────────────────────────────────


async def _cmd_status(client: NepViewer, args: argparse.Namespace) -> None:
    site_filter: str | None = args.site
    await _display(lambda: _render_status(client, site_filter), watch=args.watch)


async def _cmd_weather(client: NepViewer, args: argparse.Namespace) -> None:
    from . import resolve_sid
    sid = await resolve_sid(client, args.sid)
    await _display(lambda: _render_weather(client, sid))


# ── registration ───────────────────────────────────────────────────────


def register_dashboard_commands(parent_sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register human-friendly dashboard commands."""

    p = parent_sub.add_parser(
        "status",
        help="Dashboard with energy flow, production, and panels",
    )
    p.add_argument("--site", "-s", default=None, metavar="SID", help="Show only this site (default: all)")
    p.add_argument("--watch", "-w", action="store_true", help="Auto-refresh every 5 minutes")
    p.set_defaults(func=_cmd_status)

    p = parent_sub.add_parser(
        "weather",
        help="7-day weather forecast for a site",
    )
    p.add_argument("sid", nargs="?", default=None, help="Site ID (auto-detected if omitted)")
    p.set_defaults(func=_cmd_weather)
