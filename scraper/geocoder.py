"""Geocode Japanese addresses using the GSI (国土地理院) API."""
import re
import time
from urllib.parse import urlencode
import requests

GSI_API = "https://msearch.gsi.go.jp/address-search/AddressSearch"
REQUEST_DELAY = 0.5


def clean_address(address: str) -> str:
    """Remove postal code prefix and strip whitespace."""
    cleaned = re.sub(r"〒\d+[\s\u3000]*", "", address)
    return cleaned.strip()


def geocode(address: str, delay: float = 0.0) -> tuple[float | None, float | None]:
    """Return (lat, lng) for address using GSI API, or (None, None) on failure."""
    if delay:
        time.sleep(delay)
    url = f"{GSI_API}?{urlencode({'q': address})}"
    try:
        resp = requests.get(url, timeout=10)
        results = resp.json()
        if not results:
            return (None, None)
        coords = results[0]["geometry"]["coordinates"]
        lng, lat = coords[0], coords[1]
        return (lat, lng)
    except Exception:
        return (None, None)
