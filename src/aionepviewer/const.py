"""Constants for the aionepviewer library."""

from __future__ import annotations

DEFAULT_HOST = "https://api.nepviewer.net"
API_BASE_PATH = "/v2"

DEFAULT_HEADERS = {
    "client": "web",
    "app": "0",
    "oem": "NEP",
    "lan": "6",
    "content-type": "application/json",
    "accept": "application/json, text/plain, */*",
}

REQUEST_TIMEOUT = 30
TOKEN_EXPIRY_MARGIN = 300  # Refresh token 5 min before expiry