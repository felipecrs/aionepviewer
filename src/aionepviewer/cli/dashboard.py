"""Human-friendly dashboard commands with rich formatting and --watch support."""

from __future__ import annotations

import argparse
import asyncio
from collections.abc import Awaitable, Callable
from datetime import datetime
from typing import Any

from rich.console import Console, Group
from rich.columns import Columns
from rich.live import Live
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

from ..models.device import DeviceOverviewItem
from ..models.module import DeviceModules, Module, SiteModulesData
from ..models.site import SiteOverview
from ..nepviewer import NepViewer

console = Console()

WATCH_INTERVAL = 300  # 5 minutes


# ── formatting helpers ─────────────────────────────────────────────────


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


def _status_dot(is_online: bool) -> str:
    return "[green]●[/green]" if is_online else "[red]●[/red]"


def _power_style(value: float, max_value: float = 2000) -> str:
    """Return a rich style string based on power output relative to max."""
    if value <= 0:
        return "dim"
    ratio = min(value / max_value, 1.0)
    if ratio > 0.7:
        return "bold green"
    if ratio > 0.3:
        return "green"
    return "yellow"


def _module_panel(m: Module) -> Panel:
    """Render a single solar panel module as a small box."""
    power_sty = _power_style(m.now)
    is_ok = m.status == "0000"
    border = "green" if is_ok else "red"

    body = Text.assemble(
        (f"{m.now} {m.now_unit}\n", power_sty),
        (f"{m.today_power} {m.today_power_unit} today\n", ""),
        (f"{m.total_power} {m.total_power_unit} total", "dim"),
    )

    title = f"[bold]#{m.addr}[/bold]"
    if not is_ok:
        title += f" [red]⚠ {m.status}[/red]"

    return Panel(body, title=title, border_style=border, width=22, height=6)


def _device_header(
    dev: DeviceModules,
    dev_overview: DeviceOverviewItem | None,
) -> Panel:
    """Render the device summary bar."""
    is_online = dev.status == 0
    dot = _status_dot(is_online)

    grid = Table.grid(padding=(0, 3))
    grid.add_column(style="bold")
    grid.add_column()

    grid.add_row("Status", f"{dot} {dev.status_title}")
    if dev_overview:
        grid.add_row("Power", f"[{_power_style(float(dev_overview.now))}]{dev_overview.now} {dev_overview.now_unit}[/]")
        grid.add_row("Today", f"{dev_overview.today} {dev_overview.today_unit}")
    if dev.alert_code and dev.alert_code != "0000":
        grid.add_row("Alert", f"[bold red]{dev.alert_title}[/bold red]")
    if dev.version:
        grid.add_row("Firmware", f"[dim]{dev.version}[/dim]")

    return Panel(grid, title=f"[bold]{dev.sn}[/bold] ({dev.model_name})", border_style="cyan")


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
    prod_grid = Table.grid(padding=(0, 3))
    prod_grid.add_column(style="bold")
    prod_grid.add_column()
    prod_grid.add_row("Current", f"[bold yellow]{prod.total_now}[/bold yellow] {prod.total_now_unit}")
    prod_grid.add_row("Today", f"{prod.today} {prod.today_unit}  ([green]{prod.today_money}[/green] {prod.total_money_unit})")
    prod_grid.add_row("Month", f"{prod.month} {prod.month_unit}")
    prod_grid.add_row("Year", f"{prod.year} {prod.year_unit}")
    prod_grid.add_row("Lifetime", f"[bold]{prod.total}[/bold] {prod.total_unit}")
    prod_panel = Panel(prod_grid, title="Production", border_style="green")

    parts: list[Any] = [Columns([flow_panel, prod_panel], equal=True, expand=True)]

    # Build a quick SN→DeviceOverviewItem lookup from the site overview
    dev_overview_map: dict[str, DeviceOverviewItem] = {
        d.sn.upper(): d for d in overview.device_list
    }

    # Devices + module panels
    for dev in modules_data.devices:
        dev_ov = dev_overview_map.get(dev.sn.upper())
        parts.append("")
        parts.append(_device_header(dev, dev_ov))
        if dev.modules:
            module_boxes = [_module_panel(m) for m in dev.modules]
            parts.append(Columns(module_boxes, equal=False, expand=False, padding=(0, 1)))

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

    # Fetch detail for each site
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
