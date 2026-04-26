"""Tests for scraper/parser.py"""
import pytest
from scraper.parser import parse_store_detail, parse_store_list_page

STORE_DETAIL_HTML = """
<!DOCTYPE html>
<html lang="ja">
<body>
<main class="mainblock">
  <section class="mainblock_content">
    <div class="mainblock_content__box storeinfo">
      <h3 class="storeinfo-name">アーバンリサーチストア　コクーンシティ店</h3>
      <dl class="storeinfo-details">
        <dt class="storeinfo-details-head">サービス</dt>
        <dd class="storeinfo-details-data">
          <span class="datatext">さいコイン</span>
          <span class="datatext">商品券</span>
        </dd>
      </dl>
      <dl class="storeinfo-details">
        <dt class="storeinfo-details-head">業種</dt>
        <dd class="storeinfo-details-data">
          <span class="datatext">その他</span>
        </dd>
      </dl>
      <dl class="storeinfo-details">
        <dt class="storeinfo-details-head">住所</dt>
        <dd class="storeinfo-details-data">
          <span class="datatext">〒3309559　さいたま市大宮区吉敷町４ー２６３ー１コクーン2　2階</span>
        </dd>
      </dl>
      <dl class="storeinfo-details">
        <dt class="storeinfo-details-head">TEL</dt>
        <dd class="storeinfo-details-data">
          <span class="datatext">048-600-0000</span>
        </dd>
      </dl>
    </div>
  </section>
</main>
</body>
</html>
"""

STORE_DETAIL_NO_TEL_HTML = """
<!DOCTYPE html>
<html lang="ja">
<body>
<main class="mainblock">
  <section class="mainblock_content">
    <div class="mainblock_content__box storeinfo">
      <h3 class="storeinfo-name">秋ヶ瀬</h3>
      <dl class="storeinfo-details">
        <dt class="storeinfo-details-head">サービス</dt>
        <dd class="storeinfo-details-data">
          <span class="datatext">商品券</span>
        </dd>
      </dl>
      <dl class="storeinfo-details">
        <dt class="storeinfo-details-head">業種</dt>
        <dd class="storeinfo-details-data">
          <span class="datatext">飲食</span>
        </dd>
      </dl>
      <dl class="storeinfo-details">
        <dt class="storeinfo-details-head">住所</dt>
        <dd class="storeinfo-details-data">
          <span class="datatext">〒3380001　さいたま市中央区上落合２ー３ー２</span>
        </dd>
      </dl>
      <dl class="storeinfo-details">
        <dt class="storeinfo-details-head">TEL</dt>
        <dd class="storeinfo-details-data">
          <span class="datatext"></span>
        </dd>
      </dl>
    </div>
  </section>
</main>
</body>
</html>
"""

STORE_LIST_HTML = """
<!DOCTYPE html>
<html lang="ja">
<body>
<div class="storelist">
  <article class="storecard">
    <a class="storecard-link" href="https://shop.saitama-tsunagu.com/store/store-a/">
      <h3 class="storecard-name">店舗A</h3>
    </a>
  </article>
  <article class="storecard">
    <a class="storecard-link" href="https://shop.saitama-tsunagu.com/store/store-b/">
      <h3 class="storecard-name">店舗B</h3>
    </a>
  </article>
</div>
</body>
</html>
"""


class TestParseStoreDetail:
    def test_extracts_name(self):
        result = parse_store_detail(STORE_DETAIL_HTML, url="https://example.com/store/test/")
        assert result["name"] == "アーバンリサーチストア　コクーンシティ店"

    def test_extracts_address(self):
        result = parse_store_detail(STORE_DETAIL_HTML, url="https://example.com/store/test/")
        assert result["address"] == "〒3309559　さいたま市大宮区吉敷町４ー２６３ー１コクーン2　2階"

    def test_extracts_phone(self):
        result = parse_store_detail(STORE_DETAIL_HTML, url="https://example.com/store/test/")
        assert result["phone"] == "048-600-0000"

    def test_phone_empty_when_missing(self):
        result = parse_store_detail(STORE_DETAIL_NO_TEL_HTML, url="https://example.com/store/test/")
        assert result["phone"] == ""

    def test_extracts_category(self):
        result = parse_store_detail(STORE_DETAIL_HTML, url="https://example.com/store/test/")
        assert result["category"] == "その他"

    def test_extracts_services_as_list(self):
        result = parse_store_detail(STORE_DETAIL_HTML, url="https://example.com/store/test/")
        assert result["services"] == ["さいコイン", "商品券"]

    def test_single_service(self):
        result = parse_store_detail(STORE_DETAIL_NO_TEL_HTML, url="https://example.com/store/test/")
        assert result["services"] == ["商品券"]

    def test_stores_url(self):
        url = "https://example.com/store/test/"
        result = parse_store_detail(STORE_DETAIL_HTML, url=url)
        assert result["url"] == url

    def test_lat_lng_initially_none(self):
        result = parse_store_detail(STORE_DETAIL_HTML, url="https://example.com/store/test/")
        assert result["lat"] is None
        assert result["lng"] is None


class TestParseStoreListPage:
    def test_extracts_store_urls(self):
        urls = parse_store_list_page(STORE_LIST_HTML)
        assert len(urls) == 2
        assert "https://shop.saitama-tsunagu.com/store/store-a/" in urls
        assert "https://shop.saitama-tsunagu.com/store/store-b/" in urls

    def test_returns_empty_list_when_no_stores(self):
        urls = parse_store_list_page("<html><body></body></html>")
        assert urls == []
