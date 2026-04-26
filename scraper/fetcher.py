"""Fetch and cache HTML pages."""
import hashlib
import os
import time
import requests

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "html_cache")
REQUEST_DELAY = 1.0


def get_cache_path(url: str) -> str:
    fname = hashlib.md5(url.encode()).hexdigest() + ".html"
    return os.path.join(CACHE_DIR, fname)


def fetch_html(url: str, delay: float = 0.0) -> str:
    """Return HTML for url, reading from cache if available."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_path = get_cache_path(url)
    if os.path.exists(cache_path):
        with open(cache_path, encoding="utf-8") as f:
            return f.read()
    if delay:
        time.sleep(delay)
    resp = requests.get(url, timeout=15)
    html = resp.content.decode("utf-8")
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(html)
    return html
