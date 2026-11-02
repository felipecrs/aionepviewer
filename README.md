# aionepviewer

Async Python library for the [NEP solar inverter](https://www.nepviewer.com/) cloud API (`api.nepviewer.net`).

Built for [Home Assistant](https://www.home-assistant.io/) integrations, following the [Home Assistant API library guidelines](https://developers.home-assistant.io/docs/api_lib_index/).

## Single-session limit

The NEP API allows only one active session per account. Logging in from a second device or client invalidates earlier sessions, and subsequent requests return HTTP 401.

Do not use the same account simultaneously from the web portal, mobile app, and this library. If a session is invalidated, the library raises `NepAuthError` and clears the stored token so the next request can re-authenticate.

## Features

- Async client built on `aiohttp`, accepting an externally managed `ClientSession`
- Endpoints for authentication, sites, devices, modules, statistics, playback, weather, and reports
- Per-panel microinverter data by PLC serial number
- Power flow across PV panels, home, grid, battery, and generator
- Production statistics for today, yesterday, current month, year, and lifetime
- Environmental savings: CO₂, tree equivalent, vehicle kilometers avoided, lighting hours, and oil barrels
- Intraday (5-minute), daily, monthly, and yearly chart data
- 7-day weather forecasts per site
- Email report configuration (daily, weekly, and monthly)
- Token management with automatic re-authentication before expiry
- Automatic request signing with MD5
- Type annotations across all models and methods

## Installation

```bash
pip install aionepviewer
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add aionepviewer
```

To also install the CLI tool:

```bash
pip install aionepviewer[cli]
```

## Quick start

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

## Home Assistant integration

Pass Home Assistant's shared `aiohttp.ClientSession` when creating the client:

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

## API reference

### `NepViewer(session, email, password, host=DEFAULT_HOST)`

Main client class.

#### Authentication and account

| Method | Description |
|---|---|
| `authenticate()` | Sign in and return `AuthData` (user info + token) |
| `logout()` | Explicitly log out and invalidate the session token |
| `get_account_info()` | Get detailed user profile (`AccountInfo`) |

#### Global overview

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

#### Report settings

| Method | Description |
|---|---|
| `get_report_settings(sid, sn)` | Get email report notification settings for a device |
| `set_report_settings(sn, ...)` | Configure daily/weekly/monthly email reports and alert windows |

### Chart types

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

The package includes a command-line tool with three subcommands:

- `api`: JSON output mapped directly to API endpoints
- `chart`: terminal bar charts rendered with termgraph
- `status` and `weather`: formatted status displays with optional `--watch` auto-refresh

### Configuration

Run `configure` once to save your credentials. It will prompt for host, email, and password, verify the credentials against the API, and then save:

```bash
aionepviewer configure
```

This creates a TOML config file at the standard user config location:

| OS | Path |
|---|---|
| Linux | `~/.config/aionepviewer/config.toml` |
| macOS | `~/Library/Application Support/aionepviewer/config.toml` |
| Windows | `%APPDATA%\aionepviewer\config.toml` (Roaming) |

You can also check the path with `aionepviewer config-path`.

The config file format:

```toml
email = "user@example.com"
password = "secret"
host = "https://api.nepviewer.net"   # optional, only if non-default
```

### Authentication precedence

Credentials are resolved in this order (first non-empty value wins):

1. CLI flags: `--email` / `--password` / `--host`
2. Environment variables: `AIONEPVIEWER_EMAIL` / `AIONEPVIEWER_PASSWORD`
3. Config file (see above)
4. Interactive prompt (fallback for email and password)

```bash
# Uses config file (after running 'configure')
aionepviewer status

# Override email from config with a flag
aionepviewer -e other@example.com status

# Override with environment variables
export AIONEPVIEWER_EMAIL=user@example.com
export AIONEPVIEWER_PASSWORD=secret
aionepviewer status
```

### Dashboard commands

```bash
aionepviewer status                    # Full dashboard: overview + all sites with panels
aionepviewer status --site <sid>       # Dashboard for a specific site only
aionepviewer status --watch            # Auto-refresh every 5 minutes

aionepviewer weather [sid]             # 7-day weather forecast with icons
```

Site ID is auto-detected if omitted (uses the first site on your account).

### Chart commands

```bash
# Device production charts
aionepviewer chart production                          # Today's intraday power (W)
aionepviewer chart production --sn AABB1122            # Specific device
aionepviewer chart production --period month           # Daily bars for current month (kWh)
aionepviewer chart production --period year             # Monthly bars for current year
aionepviewer chart production --date 2026-05-20        # Specific date

# Parameter charts (Temperature, AC Voltage, etc.)
aionepviewer chart params                              # List available parameters
aionepviewer chart params Temperature "AC Voltage"     # Intraday parameter chart
aionepviewer chart params --sn AABB1122 Temperature    # Specific device

# Site production charts
aionepviewer chart site                                # Today's site production
aionepviewer chart site --period month                 # Daily bars for current month
```

Device SN and Site ID are auto-detected if omitted.

### API commands

All API commands output raw JSON. Use these for scripting or piping to `jq`.

```bash
aionepviewer api login                                 # Authenticate, return token info
aionepviewer api logout                                # Invalidate session token
aionepviewer api account-info                          # User profile details
aionepviewer api overview                              # Global production summary
aionepviewer api site-status-counts                    # Online/offline site counts

aionepviewer api sites                                 # List all sites
aionepviewer api site-detail <sid>                     # Full site information
aionepviewer api site-overview <sid>                   # Production, energy flow, alerts
aionepviewer api site-modules <sid>                    # Per-panel module data
aionepviewer api site-weather <sid>                    # 7-day forecast
aionepviewer api site-layout <sid>                     # Site layout picture info
aionepviewer api site-chart <sid> --type 1             # Site chart data

aionepviewer api devices                               # List all devices
aionepviewer api device-detail <sid> <sn>              # Full device information
aionepviewer api device-stats <sn>                     # Device statistics overview
aionepviewer api device-params <sn>                    # Available power parameters
aionepviewer api device-chart <sn> --type 1            # Device chart data
aionepviewer api device-energy <sn> 2026-05-20         # Day energy stats
aionepviewer api device-energy <sn> 2026-05            # Month energy stats
aionepviewer api device-playback <sn>                  # Today's 5-min playback
aionepviewer api product-info <sn...>                  # Product model info
aionepviewer api device-wifi-ota <sn...>               # WiFi OTA status
aionepviewer api report-settings <sid> <sn>            # Report notification settings
aionepviewer api report-setup <sn> --daily --monthly   # Configure reports
```

## Development

```bash
# Install dev dependencies
uv sync

# Run tests
uv run pytest

# Type checking
uv run mypy src/aionepviewer
```

## License

MIT