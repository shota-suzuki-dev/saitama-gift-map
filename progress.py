"""scraping progress monitor"""
import json
import os
import sys
import time

STORES_JSON = os.path.join(os.path.dirname(__file__), "stores.json")
CACHE_DIR = os.path.join(os.path.dirname(__file__), "html_cache")
TOTAL_STORES = 2715
LIST_PAGES = 272


def show():
    cache_count = len(os.listdir(CACHE_DIR)) if os.path.exists(CACHE_DIR) else 0
    store_count = 0
    geocoded = 0
    if os.path.exists(STORES_JSON):
        try:
            with open(STORES_JSON, encoding="utf-8") as f:
                stores = json.load(f)
            store_count = len(stores)
            geocoded = sum(1 for s in stores if s.get("lat") is not None)
        except Exception:
            pass

    list_cached = min(cache_count, LIST_PAGES)
    detail_cached = max(0, cache_count - LIST_PAGES)
    pct = store_count / TOTAL_STORES * 100
    bar = "#" * int(30 * pct / 100) + "-" * (30 - int(30 * pct / 100))

    lines = [
        "==================================================",
        f"  list pages cached : {list_cached} / {LIST_PAGES}",
        f"  store pages cached: {detail_cached}",
        f"  stores.json saved : {store_count} / {TOTAL_STORES}",
        f"  geocoded          : {geocoded}",
        f"  progress [{bar}] {pct:.1f}%",
        "==================================================",
    ]
    sys.stdout.write("\n".join(lines) + "\n")
    sys.stdout.flush()


if __name__ == "__main__":
    watch = "--watch" in sys.argv
    if watch:
        sys.stdout.write("watching... (Ctrl+C to stop)\n")
        sys.stdout.flush()
        while True:
            time.sleep(5)
            sys.stdout.write("\033[8A\033[J")  # 8行上に戻してクリア
            sys.stdout.flush()
            show()
    else:
        show()
