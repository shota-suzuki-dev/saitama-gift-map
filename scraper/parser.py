"""shop.saitama-tsunagu.com のHTMLページから店舗情報を抽出するモジュール。"""
from bs4 import BeautifulSoup


def parse_store_detail(html: str, url: str) -> dict:
    """店舗詳細ページのHTMLを解析して店舗情報を辞書で返す。

    取得する情報:
      - name     : 店舗名
      - address  : 住所（郵便番号含む）
      - phone    : 電話番号（なければ空文字）
      - category : 業種
      - services : 利用できるサービスのリスト（例: ["さいコイン", "商品券"]）
      - url      : 元ページのURL
      - lat/lng  : 緯度・経度（この時点では None、後でジオコーディングで埋める）
    """
    soup = BeautifulSoup(html, "html.parser")

    # <h3 class="storeinfo-name"> から店舗名を取得
    name = soup.find("h3", class_="storeinfo-name")
    name_text = name.get_text(strip=True) if name else ""

    # <dl class="storeinfo-details"> が「サービス/業種/住所/TEL」の各項目に対応
    details: dict[str, list[str]] = {}
    for dl in soup.find_all("dl", class_="storeinfo-details"):
        dt = dl.find("dt")
        if not dt:
            continue
        key = dt.get_text(strip=True)
        # 値は <span class="datatext"> に複数入っている場合がある
        spans = dl.find_all("span", class_="datatext")
        values = [s.get_text(strip=True) for s in spans]
        details[key] = values

    return {
        "name": name_text,
        "address": details.get("住所", [""])[0],
        "phone": details.get("TEL", [""])[0],
        "category": details.get("業種", [""])[0],
        # 空文字のスパンを除外してサービス一覧を作成
        "services": [v for v in details.get("サービス", []) if v],
        "url": url,
        "lat": None,
        "lng": None,
    }


def parse_store_list_page(html: str) -> list[str]:
    """店舗一覧ページのHTMLから、各店舗の詳細ページURLをリストで返す。

    一覧ページの各カードは <a class="result-box-block" href="..."> の形式。
    """
    soup = BeautifulSoup(html, "html.parser")
    urls = []
    for a in soup.find_all("a", class_="result-box-block"):
        href = a.get("href", "")
        if href:
            urls.append(href)
    return urls
