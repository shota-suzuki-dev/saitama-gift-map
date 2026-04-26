"""スクレイピングのメインパイプライン。

処理の流れ:
  1. 商品券対応店舗の一覧ページ（272ページ）から店舗URLを収集
  2. 各店舗の詳細ページをHTMLキャッシュ経由で取得・解析
  3. 住所を国土地理院APIでジオコーディング（緯度・経度に変換）
  4. 結果を stores.json に随時保存（中断・再開に対応）

実行方法:
  uv run python -m scraper.pipeline          # 全件（約2,715店舗）
  uv run python -m scraper.pipeline 1        # 1ページ分（10件）のテスト実行
"""
import json
import os
import sys
from scraper.fetcher import fetch_html, REQUEST_DELAY
from scraper.parser import parse_store_detail, parse_store_list_page
from scraper.geocoder import geocode, clean_address, REQUEST_DELAY as GEO_DELAY

BASE_URL = "https://shop.saitama-tsunagu.com"

# 商品券サービスでフィルタした一覧ページのURLテンプレート
LIST_URL = (
    BASE_URL
    + "/tax/page/{page}/?s&store_service%5B%5D=%25e5%2595%2586%25e5%2593%2581%25e5%2588%25b8"
)

# 商品券対応店舗の総ページ数（1ページ10件 × 272 ≒ 2,715件）
TOTAL_PAGES = 272

# 出力先（プロジェクトルートの stores.json）
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "stores.json")


def collect_store_urls(max_pages: int = TOTAL_PAGES) -> list[str]:
    """一覧ページを順番に取得し、全店舗の詳細URLをリストで返す。

    HTMLキャッシュが効くため、2回目以降はほぼ瞬時に完了する。
    """
    urls: list[str] = []
    for page in range(1, max_pages + 1):
        url = LIST_URL.format(page=page)
        print(f"  一覧ページ取得中 {page}/{max_pages} ...", end="\r")
        html = fetch_html(url, delay=REQUEST_DELAY)
        page_urls = parse_store_list_page(html)
        urls.extend(page_urls)
    print(f"\n  店舗URL収集完了: {len(urls)} 件")
    return urls


def load_existing(output_file: str) -> dict[str, dict]:
    """既存の stores.json を読み込み、URL をキーにした辞書で返す。

    中断後の再実行時に処理済みの店舗をスキップするために使う。
    """
    if not os.path.exists(output_file):
        return {}
    with open(output_file, encoding="utf-8") as f:
        stores = json.load(f)
    return {s["url"]: s for s in stores}


def save_stores(stores: list[dict], output_file: str) -> None:
    """店舗リストを stores.json に書き出す。

    1件処理するたびに呼び出すことで、中断時のデータ損失を最小化する。
    """
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(stores, f, ensure_ascii=False, indent=2)


def run(max_pages: int = TOTAL_PAGES, dry_run: bool = False) -> None:
    """パイプライン全体を実行する。

    Args:
        max_pages: 一覧ページの取得上限。小さくするとテスト実行できる。
        dry_run  : True にすると stores.json への書き込みを行わない。
    """
    print("=== ステップ1: 店舗URL収集 ===")
    store_urls = collect_store_urls(max_pages)

    existing = load_existing(OUTPUT_FILE)
    new_urls = [u for u in store_urls if u not in existing]
    print(f"=== ステップ2: 詳細取得・ジオコーディング ({len(new_urls)} 件が未処理) ===")

    # 処理済みの店舗はそのまま引き継ぐ
    stores: list[dict] = list(existing.values())

    for i, url in enumerate(new_urls):
        print(f"  {i + 1}/{len(new_urls)}: {url[:60]}", end="\r")

        # 詳細ページHTMLを取得（キャッシュがあれば再フェッチしない）
        html = fetch_html(url, delay=REQUEST_DELAY)
        store = parse_store_detail(html, url=url)

        # 住所の郵便番号を除去してからジオコーディング
        address = clean_address(store["address"])
        if address:
            lat, lng = geocode(address, delay=GEO_DELAY)
            store["lat"] = lat
            store["lng"] = lng

        stores.append(store)

        # 1件ごとに保存（途中終了してもデータが残る）
        if not dry_run:
            save_stores(stores, OUTPUT_FILE)

    print(f"\n=== 完了: {len(stores)} 件を {OUTPUT_FILE} に保存 ===")
    geocoded = sum(1 for s in stores if s.get("lat") is not None)
    print(f"    ジオコーディング成功: {geocoded}/{len(stores)} ({geocoded / len(stores) * 100:.1f}%)")


if __name__ == "__main__":
    # コマンドライン引数でページ数を指定可能（省略時は全件）
    pages = int(sys.argv[1]) if len(sys.argv) > 1 else TOTAL_PAGES
    run(max_pages=pages)
