"""Command-line interface for aionepviewer."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from dataclasses import asdict
from getpass import getpass
from typing import Any

import aiohttp

from ..client import NepViewer
from ..const import DEFAULT_HOST
from ..exceptions import NepAuthError, NepError


# ── shared helpers ─────────────────────────────────────────────────────


def get_credentials(args: argparse.Namespace) -> tuple[str, str]:
    """Resolve email/password from flags, env vars, or interactive prompt."""
    email = args.email or os.environ.get("AIONEPVIEWER_EMAIL", "")
    password = args.password or os.environ.get("AIONEPVIEWER_PASSWORD", "")
    if not email:
        email = input("Email: ")
    if not password:
        password = getpass("Password: ")
    return email, password


def dump_json(obj: Any) -> str:
    """Serialize a dataclass (or list of dataclasses) to indented JSON."""
    if hasattr(obj, "__dataclass_fields__"):
        return json.dumps(asdict(obj), indent=2, default=str)
    if isinstance(obj, list):
        items = [asdict(o) if hasattr(o, "__dataclass_fields__") else o for o in obj]
        return json.dumps(items, indent=2, default=str)
    return json.dumps(obj, indent=2, default=str)


async def resolve_sid(client: NepViewer, sid: str | None) -> str:
    """If *sid* is None, auto-discover the first site."""
    if sid:
        return sid
    sites = await client.get_sites()
    if not sites:
        print("No sites found on this account.", file=sys.stderr)
        sys.exit(1)
    return sites[0].sid


async def resolve_sn(client: NepViewer, sn: str | None) -> str:
    """If *sn* is None, auto-discover the first device serial number."""
    if sn:
        return sn
    devices = await client.get_devices()
    if not devices:
        print("No devices found on this account.", file=sys.stderr)
        sys.exit(1)
    return devices[0].sn


# ── parser construction ───────────────────────────────────────────────


def _build_parser() -> argparse.ArgumentParser:
    from .api import register_api_commands
    from .chart import register_chart_commands
    from .dashboard import register_dashboard_commands

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

    sub = parser.add_subparsers(dest="command", required=True)

    # Register command groups
    register_api_commands(sub)
    register_chart_commands(sub)
    register_dashboard_commands(sub)

    return parser


# ── main entry ─────────────────────────────────────────────────────────


async def _async_main(args: argparse.Namespace) -> None:
    email, password = get_credentials(args)
    async with aiohttp.ClientSession() as session:
        client = NepViewer(session, email, password, args.host)
        handler = args.func
        await handler(client, args)


def main() -> None:
    # Ensure UTF-8 output on Windows (needed for termgraph block chars and rich)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[union-attr]

    parser = _build_parser()
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
