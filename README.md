# aionepviewer

Async Python library for the [NEP solar inverter](https://www.nepviewer.com/) cloud API (`api.nepviewer.net`).

Designed as a backend library for [Home Assistant](https://www.home-assistant.io/) integrations, following the [HA API library best practices](https://developers.home-assistant.io/docs/api_lib_index/).

## Important: Single-Session Limitation

The NEP API only allows **one active session per account** at a time. If you log in from a second device or client, the first session's token is immediately invalidated and all its requests will fail with a 401 error.

This means:
- You **cannot** use the same NEP account simultaneously from the web portal and this library (or from two library instances).
- If your Home Assistant integration suddenly starts getting authentication errors, check if someone opened the NEP web portal or mobile app with the same account.
- The library handles this gracefully by raising `NepAuthError` and clearing the token, so the next request will trigger a re-authentication.

## Features

- **Fully async** — built on `aiohttp`, accepts an externally managed `ClientSession`
- **Complete API coverage** — authentication, sites, devices, modules, statistics, playback, weather, reports
- **Module-level monitoring** — individual microinverter panel data (per-PLC serial number)
- **Energy flow** — PV panel, home, grid, battery, and generator power flow data
- **Production statistics** — today, yesterday, month, year, and lifetime energy with currency values
- **Environmental benefit** — CO₂ saved, trees equivalent, car km avoided, light hours, oil barrels
- **Charts & playback** — intraday (5-min), daily, monthly, yearly chart data
- **Weather** — 7-day forecast for each site
- **Report settings** — read and configure email notification reports (daily/weekly/monthly)
- **Account management** — user profile info and explicit logout
- **Automatic token management** — JWT sign-in with auto-refresh on expiry
- **Request signing** — MD5-based `sign` header computed automatically
- **Type-annotated** — full type hints with `from __future__ import annotations`

## Installation

```bash
pip install aionepviewer
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add aionepviewer
```

## Quick Start

```python
import asyncio
import aiohttp
from aionepviewer import NepViewer

async def main():
    async with aiohttp.ClientSession() as session:
        client = NepViewer(session, "your-email@example.com", "your-password")

        # Authenticate (also called automatically on first request)
        auth = await client.authenticate()
        print(f"Logged in as {auth.user_info.email}, {auth.site_count} site(s)")

        # List all sites
        sites = await client.get_sites()
        for site in sites:
            print(f"Site: {site.site_name} ({site.sid})")
            print(f"  Current power: {site.now} {site.now_unit}")
            print(f"  Today: {site.today_power} {site.today_power_unit}")
            print(f"  Total: {site.total_power} {site.total_power_unit}")

            # Get detailed overview with energy flow
            overview = await client.get_site_overview(site.sid)
            print(f"  PV → Home: {overview.energy.pv_panel.power} W")
            print(f"  Grid: {overview.energy.grid.power} W")
            print(f"  CO₂ saved: {overview.benefit.co2} {overview.benefit.co2_unit}")

            # Get module-level data
            modules = await client.get_site_modules(site.sid)
            for device in modules.devices:
                print(f"  Device {device.sn} ({device.model_name}):")
                for module in device.modules:
                    print(f"    Panel {module.plc_sn}: {module.now} {module.now_unit}")

asyncio.run(main())
```

## Home Assistant Integration Usage

This library is designed to be used inside a Home Assistant custom integration. The caller provides the `aiohttp.ClientSession` (for connection pooling and SSL), and the library handles authentication and data fetching.

```python
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from aionepviewer import NepViewer, NepAuthError

async def async_setup_entry(hass, entry):
    session = async_get_clientsession(hass)
    client = NepViewer(
        session,
        entry.data["email"],
        entry.data["password"],
    )

    try:
        await client.authenticate()
    except NepAuthError:
        raise ConfigEntryAuthFailed("Invalid credentials")

    # Use with DataUpdateCoordinator
    async def async_update_data():
        sites = await client.get_sites()
        result = {}
        for site in sites:
            overview = await client.get_site_overview(site.sid)
            modules = await client.get_site_modules(site.sid)
            result[site.sid] = {
                "site": site,
                "overview": overview,
                "modules": modules,
            }
        return result

    coordinator = DataUpdateCoordinator(
        hass,
        logger,
        name="nep",
        update_method=async_update_data,
        update_interval=timedelta(seconds=300),
    )
    await coordinator.async_config_entry_first_refresh()
```

## API Reference

### `NepViewer(session, email, password, host=DEFAULT_HOST)`

Main client class.

#### Authentication & Account

| Method | Description |
|---|---|
| `authenticate()` | Sign in and return `AuthData` (user info + token) |
| `logout()` | Explicitly log out and invalidate the session token |
| `get_account_info()` | Get detailed user profile (`AccountInfo`) |

#### Global Overview

| Method | Description |
|---|---|
| `get_overview()` | Global production, benefit, and device counts |
| `get_site_status_counts()` | Online/offline site counts |

#### Sites

| Method | Description |
|---|---|
| `get_sites(...)` | List all sites with device summaries |
| `get_site_detail(sid)` | Full site info (location, timezone, panels, pricing) |
| `get_site_overview(sid)` | Production stats, energy flow, device list, alerts |
| `get_site_modules(sid)` | Per-panel module data grouped by device |
| `get_site_weather(sid)` | 7-day weather forecast |
| `get_site_statistics_chart(sid, chart_type, ...)` | Chart data (intraday, daily, monthly, yearly) |

#### Devices

| Method | Description |
|---|---|
| `get_devices(...)` | List all devices with status and power |
| `get_device_detail(sid, sn)` | Full device info |
| `get_device_statistics_overview(sn)` | Production, benefit, energy flow, alerts |
| `get_device_power_parameters(sn)` | Available parameters (voltage, frequency, temperature, per-channel) |
| `get_device_statistics_chart(sn, chart_type, ...)` | Chart data |
| `get_device_date_statistics(sn, stat_type, date)` | Power/consumption/economic for a period |
| `get_device_playback(sn, start, end)` | 5-min interval data with per-module breakdown |

#### Report Settings

| Method | Description |
|---|---|
| `get_report_settings(sid, sn)` | Get email report notification settings for a device |
| `set_report_settings(sn, ...)` | Configure daily/weekly/monthly email reports and alert windows |

### Chart Types

| `ChartType` | Description |
|---|---|
| `DAY` (1) | Intraday data with configurable interval and parameter lines |
| `DAILY` (3) | Daily bars within a date range (`"YYYY-MM-DD~YYYY-MM-DD"`) |
| `MONTHLY` (5) | Monthly bars |
| `YEARLY` (6) | Yearly data (months on x-axis) |
| `INTRADAY_POWER` (11) | Intraday AC output power (15-min intervals) |

### Exceptions

| Exception | Description |
|---|---|
| `NepError` | Base exception |
| `NepAuthError` | Authentication failure (invalid credentials or expired token) |
| `NepConnectionError` | Network connectivity issue |
| `NepTimeoutError` | Request timed out |
| `NepApiError` | API returned a non-200 code (has `.code` and `.message`) |

## CLI

The package includes a command-line tool for quick interaction with the API.

### Authentication

Credentials can be provided via flags, environment variables, or interactive prompt:

```bash
# Flags
aionepviewer -e user@example.com -p secret sites

# Environment variables
export AIONEPVIEWER_EMAIL=user@example.com
export AIONEPVIEWER_PASSWORD=secret
aionepviewer sites

# Interactive prompt (if not provided)
aionepviewer sites
```

### Commands

```bash
aionepviewer login                              # Verify credentials
aionepviewer overview                           # Global production & benefit summary
aionepviewer sites                              # List all sites with device summaries
aionepviewer site-detail  <sid>                 # Full site information
aionepviewer site-overview <sid>                # Production, energy flow, alerts
aionepviewer site-modules  <sid>                # Per-panel microinverter data
aionepviewer site-weather  <sid>                # 7-day forecast

aionepviewer devices                            # List all devices
aionepviewer device-detail <sid> <sn>           # Full device information
aionepviewer device-stats  <sn>                 # Production, benefit, energy flow
aionepviewer device-params <sn>                 # Available power parameters
aionepviewer device-energy <sn> 2026-05-20      # Day energy stats
aionepviewer device-energy <sn> 2026-05                # Month energy stats
aionepviewer device-playback <sn>               # Today's 5-min playback
aionepviewer device-playback <sn> --date 2026-05-20    # Specific date
```

Add `--json` / `-j` to any command for machine-readable JSON output:

```bash
aionepviewer -j site-overview BR_20260317_tXFI
```

## Development

```bash
# Install dev dependencies
uv sync

# Run tests
uv run pytest

# Type checking
uv run mypy aionepviewer
```

## License

MIT