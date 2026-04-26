"""Parse store HTML pages from shop.saitama-tsunagu.com."""
from bs4 import BeautifulSoup


def parse_store_detail(html: str, url: str) -> dict:
    """Extract store info from a detail page HTML string."""
    soup = BeautifulSoup(html, "html.parser")
    name = soup.find("h3", class_="storeinfo-name")
    name_text = name.get_text(strip=True) if name else ""

    details = {}
    for dl in soup.find_all("dl", class_="storeinfo-details"):
        dt = dl.find("dt")
        if not dt:
            continue
        key = dt.get_text(strip=True)
        spans = dl.find_all("span", class_="datatext")
        values = [s.get_text(strip=True) for s in spans]
        details[key] = values

    return {
        "name": name_text,
        "address": details.get("住所", [""])[0],
        "phone": details.get("TEL", [""])[0],
        "category": details.get("業種", [""])[0],
        "services": [v for v in details.get("サービス", []) if v],
        "url": url,
        "lat": None,
        "lng": None,
    }


def parse_store_list_page(html: str) -> list[str]:
    """Extract store detail URLs from a list page HTML string."""
    soup = BeautifulSoup(html, "html.parser")
    urls = []
    for a in soup.find_all("a", class_="storecard-link"):
        href = a.get("href", "")
        if href:
            urls.append(href)
    return urls
