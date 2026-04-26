"""国土地理院API を使って日本語住所を緯度・経度に変換するモジュール。

国土地理院（GSI）のジオコーディングAPIは無料・APIキー不要で、
日本国内の住所に高い精度で対応している。
API仕様: https://msearch.gsi.go.jp/address-search/AddressSearch?q=住所
"""
import re
import time
from urllib.parse import urlencode
import requests

# 国土地理院ジオコーディングAPIのエンドポイント
GSI_API = "https://msearch.gsi.go.jp/address-search/AddressSearch"

# APIへのリクエスト間隔（秒）。負荷を避けるため 0.5 秒空ける
REQUEST_DELAY = 0.5


def clean_address(address: str) -> str:
    """住所文字列から郵便番号（〒XXXXXXX）を取り除き、前後の空白を除去する。

    例: "〒3309559　さいたま市大宮区..." → "さいたま市大宮区..."
    """
    cleaned = re.sub(r"〒\d+[\s\u3000]*", "", address)
    return cleaned.strip()


def geocode(address: str, delay: float = 0.0) -> tuple[float | None, float | None]:
    """住所文字列を緯度・経度のタプル (lat, lng) に変換する。

    APIが結果を返せなかった場合や通信エラー時は (None, None) を返す。
    stores.json の lat/lng フィールドに格納される値がここで決まる。

    Args:
        address: ジオコーディングしたい住所（郵便番号なしが望ましい）
        delay  : リクエスト前の待機秒数

    Returns:
        (緯度, 経度) または (None, None)
    """
    if delay:
        time.sleep(delay)
    url = f"{GSI_API}?{urlencode({'q': address})}"
    try:
        resp = requests.get(url, timeout=10)
        results = resp.json()
        if not results:
            return (None, None)
        # APIレスポンスは GeoJSON 形式。coordinates は [経度, 緯度] の順
        coords = results[0]["geometry"]["coordinates"]
        lng, lat = coords[0], coords[1]
        return (lat, lng)
    except Exception:
        # タイムアウト・JSONパースエラーなど、あらゆる失敗は None で処理継続
        return (None, None)
