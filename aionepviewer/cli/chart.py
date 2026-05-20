"""Chart subcommands — terminal bar charts via termgraph for humans."""

from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta

from rich.console import Console
from rich.table import Table

from ..client import NepViewer
from ..models import ChartType
from . import resolve_sn, resolve_sid

console = Console()

# ── termgraph rendering ───────────────────────────────────────────────


def _render_bar_chart(
    labels: list[str],
    values: list[float],
    *,
    title: str = "",
    suffix: str = "",
    color: str = "yellow",
) -> None:
    """Render a horizontal bar chart with termgraph."""
    from termgraph.module import Data, Args, BarChart  # type: ignore[import-untyped]

    if not values or all(v == 0 for v in values):
        console.print(f"[dim]  No data to chart.[/dim]")
        return

    data = Data([[v] for v in values], labels)
    args = Args(
        title=title,
        width=50,
        format="{:.1f}",
        suffix=suffix,
        colors=[color],
        no_labels=False,
        no_values=False,
    )
    chart = BarChart(data, args)
    chart.draw()


def _downsample(
    labels: list[str], values: list[float | None], max_points: int = 24
) -> tuple[list[str], list[float]]:
    """Downsample time-series data by averaging into *max_points* buckets."""
    clean = [(l, v if v is not None else 0.0) for l, v in zip(labels, values)]
    if len(clean) <= max_points:
        return [c[0] for c in clean], [c[1] for c in clean]

    step = len(clean) / max_points
    out_labels: list[str] = []
    out_values: list[float] = []
    for i in range(max_points):
        start = int(i * step)
        end = int((i + 1) * step)
        bucket = clean[start:end]
        if bucket:
            out_labels.append(bucket[0][0])
            out_values.append(sum(v for _, v in bucket) / len(bucket))
    return out_labels, out_values


# ── handlers ───────────────────────────────────────────────────────────


async def _chart_production(client: NepViewer, args: argparse.Namespace) -> None:
    """Production bar chart for a device."""
    sn = await resolve_sn(client, args.sn)
    period: str = args.period

    if period == "day":
        chart_type = ChartType.DAY
        chart_date = args.date or date.today().isoformat()
        title = f"Production: {sn} ({chart_date})"
        suffix = " W"
    elif period == "month":
        base = args.date or date.today().strftime("%Y-%m")
        # Build a date range for the whole month
        year, month = int(base[:4]), int(base[5:7])
        first = date(year, month, 1)
        if month == 12:
            last = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            last = date(year, month + 1, 1) - timedelta(days=1)
        chart_type = ChartType.DAILY
        chart_date = f"{first.isoformat()}~{last.isoformat()}"
        title = f"Daily Production: {sn} ({base})"
        suffix = " kWh"
    elif period == "year":
        year_str = args.date or str(date.today().year)
        chart_type = ChartType.YEARLY
        chart_date = f"{year_str}-01-01"
        title = f"Monthly Production: {sn} ({year_str})"
        suffix = " kWh"
    else:
        print(f"Unknown period: {period}", file=sys.stderr)
        sys.exit(1)

    lines = ["Production"] if chart_type == ChartType.DAY else []
    chart_data = await client.get_device_statistics_chart(
        sn, chart_type, date=chart_date, lines=lines,
    )

    if not chart_data.series:
        console.print("[dim]No chart data available.[/dim]")
        return

    series = chart_data.series[0]
    labels, values = _downsample(chart_data.x_axis_data, series.data)
    console.print()
    _render_bar_chart(labels, values, title=title, suffix=suffix, color="yellow")
    console.print()


async def _chart_params(client: NepViewer, args: argparse.Namespace) -> None:
    """Intraday parameter chart (Temperature, AC Voltage, etc.)."""
    sn = await resolve_sn(client, args.sn)
    param_names: list[str] = args.params

    if not param_names:
        # List available parameters
        params = await client.get_device_power_parameters(sn)
        console.print()
        table = Table(title=f"Available Parameters for {sn}", show_header=True)
        table.add_column("Parameter", style="cyan")
        table.add_column("Unit", style="green")
        for p in params:
            table.add_row(p.name, p.unit)
        console.print(table)
        console.print(
            f"\n  [dim]Usage: aionepviewer chart params {sn} Temperature \"AC Voltage\"[/dim]\n"
        )
        return

    chart_date = args.date or date.today().isoformat()
    chart_data = await client.get_device_statistics_chart(
        sn, ChartType.DAY, date=chart_date, lines=param_names,
    )

    colors = ["cyan", "green", "magenta", "yellow", "red", "blue"]
    console.print()
    for idx, series in enumerate(chart_data.series):
        color = colors[idx % len(colors)]
        labels, values = _downsample(chart_data.x_axis_data, series.data)
        _render_bar_chart(
            labels, values,
            title=f"{series.name} — {sn} ({chart_date})",
            suffix="",
            color=color,
        )
        console.print()


async def _chart_site(client: NepViewer, args: argparse.Namespace) -> None:
    """Production bar chart for a site."""
    sid = await resolve_sid(client, args.sid)
    period: str = args.period

    if period == "day":
        chart_type = ChartType.INTRADAY_POWER
        chart_date = args.date or date.today().isoformat()
        title = f"Site Production: {sid} ({chart_date})"
        suffix = " W"
    elif period == "month":
        base = args.date or date.today().strftime("%Y-%m")
        year, month = int(base[:4]), int(base[5:7])
        first = date(year, month, 1)
        if month == 12:
            last = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            last = date(year, month + 1, 1) - timedelta(days=1)
        chart_type = ChartType.DAILY
        chart_date = f"{first.isoformat()}~{last.isoformat()}"
        title = f"Daily Site Production: {sid} ({base})"
        suffix = " kWh"
    elif period == "year":
        year_str = args.date or str(date.today().year)
        chart_type = ChartType.YEARLY
        chart_date = f"{year_str}-01-01"
        title = f"Monthly Site Production: {sid} ({year_str})"
        suffix = " kWh"
    else:
        print(f"Unknown period: {period}", file=sys.stderr)
        sys.exit(1)

    chart_data = await client.get_site_statistics_chart(
        sid, chart_type, date=chart_date,
    )

    if not chart_data.series:
        console.print("[dim]No chart data available.[/dim]")
        return

    series = chart_data.series[0]
    labels, values = _downsample(chart_data.x_axis_data, series.data)
    console.print()
    _render_bar_chart(labels, values, title=title, suffix=suffix, color="yellow")
    console.print()


# ── registration ───────────────────────────────────────────────────────


def register_chart_commands(parent_sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the ``chart`` subcommand group."""
    chart_parser = parent_sub.add_parser(
        "chart",
        help="Terminal bar charts for humans (termgraph)",
        description="Visual bar charts rendered in the terminal using termgraph.",
    )
    sub = chart_parser.add_subparsers(dest="chart_command", required=True)

    # chart production
    p = sub.add_parser("production", help="Production bar chart for a device")
    p.add_argument("--sn", default=None, help="Device serial number (auto-detected if omitted)")
    p.add_argument("--period", choices=["day", "month", "year"], default="day", help="Chart period (default: day)")
    p.add_argument("--date", default=None, help="Date: YYYY-MM-DD (day), YYYY-MM (month), YYYY (year)")
    p.set_defaults(func=_chart_production)

    # chart params
    p = sub.add_parser("params", help="Intraday parameter chart (Temperature, Voltage, etc.)")
    p.add_argument("--sn", default=None, help="Device serial number (auto-detected if omitted)")
    p.add_argument("params", nargs="*", help="Parameter names (omit to list available)")
    p.add_argument("--date", default=None, help="Date (YYYY-MM-DD, default: today)")
    p.set_defaults(func=_chart_params)

    # chart site
    p = sub.add_parser("site", help="Production bar chart for a site")
    p.add_argument("--sid", default=None, help="Site ID (auto-detected if omitted)")
    p.add_argument("--period", choices=["day", "month", "year"], default="day", help="Chart period (default: day)")
    p.add_argument("--date", default=None, help="Date: YYYY-MM-DD (day), YYYY-MM (month), YYYY (year)")
    p.set_defaults(func=_chart_site)
