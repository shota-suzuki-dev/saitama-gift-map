"""HTMLページの取得とローカルキャッシュを管理するモジュール。

一度取得したページは html_cache/ フォルダに保存する。
再実行時はキャッシュから読み込むため、対象サイトへのアクセスは初回のみ。
"""
import hashlib
import os
import time
import requests

# キャッシュ保存先（プロジェクトルートの html_cache/）
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "html_cache")

# サイトへのリクエスト間隔（秒）。負荷をかけないよう 1 秒空ける
REQUEST_DELAY = 1.0


def get_cache_path(url: str) -> str:
    """URLのMD5ハッシュを使ったキャッシュファイルのパスを返す。

    同じURLなら常に同じパスになるため、キャッシュ済みか判定できる。
    """
    fname = hashlib.md5(url.encode()).hexdigest() + ".html"
    return os.path.join(CACHE_DIR, fname)


def fetch_html(url: str, delay: float = 0.0) -> str:
    """指定URLのHTMLを返す。キャッシュがあればHTTPリクエストを省略する。

    Args:
        url  : 取得するURL
        delay: リクエスト前に待機する秒数（キャッシュヒット時は待機しない）

    Returns:
        ページのHTML文字列（UTF-8デコード済み）
    """
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_path = get_cache_path(url)

    # キャッシュがあればそのまま返す（サイトへのアクセスなし）
    if os.path.exists(cache_path):
        with open(cache_path, encoding="utf-8") as f:
            return f.read()

    # キャッシュなし → HTTPで取得してキャッシュに保存
    if delay:
        time.sleep(delay)
    resp = requests.get(url, timeout=15)
    html = resp.content.decode("utf-8")
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(html)
    return html
