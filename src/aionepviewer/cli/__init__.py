"""Command-line interface for aionepviewer."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import tomllib
from getpass import getpass
from pathlib import Path
from typing import Any

import aiohttp
import tomli_w
from platformdirs import user_config_path

from ..nepviewer import NepViewer
from ..const import DEFAULT_HOST
from ..exceptions import NepAuthError, NepError

APP_NAME = "aionepviewer"


# ── configuration ──────────────────────────────────────────────────────


def config_path() -> Path:
    """Return the path to the user config file."""
    return user_config_path(APP_NAME, appauthor=False, roaming=True) / "config.toml"


def load_config() -> dict[str, Any]:
    """Load the user config file. Returns empty dict if it doesn't exist."""
    path = config_path()
    if not path.exists():
        return {}
    with open(path, "rb") as f:
        return tomllib.load(f)


def save_config(cfg: dict[str, Any]) -> Path:
    """Write *cfg* to the user config file. Returns the path written."""
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        tomli_w.dump(cfg, f)
    return path


# ── credential resolution ─────────────────────────────────────────────
# Precedence: CLI flags > env vars > config file > interactive prompt


def _resolve_credentials(args: argparse.Namespace) -> tuple[str, str, str]:
    """Resolve host, email, and password using the full precedence chain.

    Returns ``(host, email, password)``.  Falls back to interactive prompts
    for any value that cannot be determined from flags / env / config.
    """
    cfg = load_config()

    # Host: CLI flag (non-default) > env > config > default
    if args.host != DEFAULT_HOST:
        host = str(args.host)
    else:
        host = (
            os.environ.get("AIONEPVIEWER_HOST", "")
            or str(cfg.get("host", ""))
            or DEFAULT_HOST
        )

    email = (
        args.email
        or os.environ.get("AIONEPVIEWER_EMAIL", "")
        or str(cfg.get("email", ""))
    )
    password = (
        args.password
        or os.environ.get("AIONEPVIEWER_PASSWORD", "")
        or str(cfg.get("password", ""))
    )

    if not host:
        host = input(f"API host [{DEFAULT_HOST}]: ").strip() or DEFAULT_HOST
    if not email:
        email = input("Email: ").strip()
    if not password:
        password = getpass("Password: ")
    return host, email, password


def dump_json(obj: Any) -> str:
    """Serialize a model (or list of models) to indented JSON via raw_data."""
    if hasattr(obj, "raw_data"):
        return json.dumps(obj.raw_data, indent=2, default=str)
    if isinstance(obj, list):
        items = [o.raw_data if hasattr(o, "raw_data") else o for o in obj]
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
        "--email", "-e", help="NEP account email (overrides config/env)"
    )
    parser.add_argument(
        "--password", "-p", help="NEP account password (overrides config/env)"
    )
    parser.add_argument(
        "--host", default=DEFAULT_HOST, help=f"API host (default: {DEFAULT_HOST})"
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # configure
    p = sub.add_parser(
        "configure",
        help="Set up credentials and save to config file",
    )
    p.set_defaults(func=_cmd_configure, needs_client=False)

    # config-path
    p = sub.add_parser(
        "config-path",
        help="Print the config file path",
    )
    p.set_defaults(func=_cmd_config_path, needs_client=False)

    # Register command groups
    register_api_commands(sub)
    register_chart_commands(sub)
    register_dashboard_commands(sub)

    return parser


# ── configure commands ─────────────────────────────────────────────────


async def _cmd_configure(_client: Any, _args: argparse.Namespace) -> None:
    """Interactive config setup with credential verification."""
    from rich.console import Console

    console = Console()
    cfg = load_config()

    console.print("\n[bold]NEP Viewer CLI Configuration[/bold]\n")
    console.print(f"  Config file: [cyan]{config_path()}[/cyan]\n")

    current_host = str(cfg.get("host", DEFAULT_HOST))
    current_email = str(cfg.get("email", ""))

    host = input(f"API host [{current_host}]: ").strip() or current_host

    prompt_email = f"Email [{current_email}]: " if current_email else "Email: "
    email = input(prompt_email).strip() or current_email

    password = getpass("Password (input hidden): ")
    if not password and cfg.get("password"):
        password = str(cfg["password"])
        console.print("  [dim](kept existing password)[/dim]")

    if not email or not password:
        console.print("\n  [red]Email and password are required.[/red]\n")
        sys.exit(1)

    # Verify credentials before saving
    console.print("\n  Verifying credentials...", end="")
    async with aiohttp.ClientSession() as session:
        client = NepViewer(session, email, password, host)
        try:
            auth = await client.authenticate()
        except NepError as exc:
            console.print(f" [red]FAILED[/red]\n  {exc}\n")
            sys.exit(1)
    console.print(f" [green]OK[/green] (logged in as {auth.user_info.email})")

    cfg["host"] = host
    cfg["email"] = email
    cfg["password"] = password

    path = save_config(cfg)
    console.print(f"\n  [green]Configuration saved to {path}[/green]\n")


async def _cmd_config_path(_client: Any, _args: argparse.Namespace) -> None:
    """Print config file location."""
    path = config_path()
    exists = path.exists()
    print(str(path))
    if not exists:
        print("(file does not exist yet — run 'aionepviewer configure' to create it)",
              file=sys.stderr)


# ── main entry ─────────────────────────────────────────────────────────


async def _async_main(args: argparse.Namespace) -> None:
    # Commands that don't need a client connection
    if getattr(args, "needs_client", True) is False:
        await args.func(None, args)
        return

    host, email, password = _resolve_credentials(args)
    async with aiohttp.ClientSession() as session:
        client = NepViewer(session, email, password, host)
        await args.func(client, args)


def main() -> None:
    # Ensure UTF-8 output on Windows (needed for termgraph block chars and rich)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

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
