"""Main pipeline: collect store URLs -> fetch HTML -> parse -> geocode -> save JSON."""
import json
import os
import sys
import time
from scraper.fetcher import fetch_html, REQUEST_DELAY
from scraper.parser import parse_store_detail, parse_store_list_page
from scraper.geocoder import geocode, clean_address, REQUEST_DELAY as GEO_DELAY

BASE_URL = "https://shop.saitama-tsunagu.com"
LIST_URL = (
    BASE_URL
    + "/tax/page/{page}/?s&store_service%5B%5D=%25e5%2595%2586%25e5%2593%2581%25e5%2588%25b8"
)
TOTAL_PAGES = 272
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "stores.json")


def collect_store_urls(max_pages: int = TOTAL_PAGES) -> list[str]:
    """Scrape list pages and return all store detail URLs."""
    urls: list[str] = []
    for page in range(1, max_pages + 1):
        url = LIST_URL.format(page=page)
        print(f"  list page {page}/{max_pages} ...", end="\r")
        html = fetch_html(url, delay=REQUEST_DELAY)
        page_urls = parse_store_list_page(html)
        urls.extend(page_urls)
    print(f"\n  collected {len(urls)} store URLs")
    return urls


def load_existing(output_file: str) -> dict[str, dict]:
    """Load already-processed stores keyed by URL."""
    if not os.path.exists(output_file):
        return {}
    with open(output_file, encoding="utf-8") as f:
        stores = json.load(f)
    return {s["url"]: s for s in stores}


def save_stores(stores: list[dict], output_file: str) -> None:
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(stores, f, ensure_ascii=False, indent=2)


def run(max_pages: int = TOTAL_PAGES, dry_run: bool = False) -> None:
    print("=== Step 1: Collecting store URLs ===")
    store_urls = collect_store_urls(max_pages)

    existing = load_existing(OUTPUT_FILE)
    print(f"=== Step 2: Fetching & parsing ({len(store_urls)} stores, {len(existing)} cached) ===")

    stores: list[dict] = list(existing.values())
    new_urls = [u for u in store_urls if u not in existing]

    for i, url in enumerate(new_urls):
        print(f"  store {i + 1}/{len(new_urls)}: {url[:60]}", end="\r")
        html = fetch_html(url, delay=REQUEST_DELAY)
        store = parse_store_detail(html, url=url)

        address = clean_address(store["address"])
        if address:
            lat, lng = geocode(address, delay=GEO_DELAY)
            store["lat"] = lat
            store["lng"] = lng

        stores.append(store)
        if not dry_run:
            save_stores(stores, OUTPUT_FILE)

    print(f"\n=== Done: {len(stores)} stores saved to {OUTPUT_FILE} ===")
    geocoded = sum(1 for s in stores if s.get("lat") is not None)
    print(f"    Geocoded: {geocoded}/{len(stores)} ({geocoded / len(stores) * 100:.1f}%)")


if __name__ == "__main__":
    pages = int(sys.argv[1]) if len(sys.argv) > 1 else TOTAL_PAGES
    run(max_pages=pages)
