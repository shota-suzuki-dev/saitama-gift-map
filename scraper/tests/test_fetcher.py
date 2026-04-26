"""Tests for scraper/fetcher.py"""
import os
import pytest
from unittest.mock import patch, MagicMock
from scraper.fetcher import fetch_html, get_cache_path


SAMPLE_HTML = "<html><body><h1>Test</h1></body></html>"


class TestGetCachePath:
    def test_returns_path_inside_html_cache(self):
        path = get_cache_path("https://example.com/store/test/")
        assert "html_cache" in path

    def test_different_urls_give_different_paths(self):
        path_a = get_cache_path("https://example.com/store/a/")
        path_b = get_cache_path("https://example.com/store/b/")
        assert path_a != path_b

    def test_same_url_gives_same_path(self):
        url = "https://example.com/store/test/"
        assert get_cache_path(url) == get_cache_path(url)

    def test_path_ends_with_html(self):
        path = get_cache_path("https://example.com/store/test/")
        assert path.endswith(".html")


class TestFetchHtml:
    def test_returns_html_string(self, tmp_path, monkeypatch):
        monkeypatch.setattr("scraper.fetcher.CACHE_DIR", str(tmp_path))
        mock_resp = MagicMock()
        mock_resp.content = SAMPLE_HTML.encode("utf-8")
        with patch("scraper.fetcher.requests.get", return_value=mock_resp):
            result = fetch_html("https://example.com/store/test/")
        assert result == SAMPLE_HTML

    def test_saves_to_cache(self, tmp_path, monkeypatch):
        monkeypatch.setattr("scraper.fetcher.CACHE_DIR", str(tmp_path))
        mock_resp = MagicMock()
        mock_resp.content = SAMPLE_HTML.encode("utf-8")
        with patch("scraper.fetcher.requests.get", return_value=mock_resp):
            fetch_html("https://example.com/store/test/")
        cache_files = list(tmp_path.glob("*.html"))
        assert len(cache_files) == 1

    def test_reads_from_cache_on_second_call(self, tmp_path, monkeypatch):
        monkeypatch.setattr("scraper.fetcher.CACHE_DIR", str(tmp_path))
        mock_resp = MagicMock()
        mock_resp.content = SAMPLE_HTML.encode("utf-8")
        with patch("scraper.fetcher.requests.get", return_value=mock_resp) as mock_get:
            fetch_html("https://example.com/store/test/")
            fetch_html("https://example.com/store/test/")
            assert mock_get.call_count == 1

    def test_returns_cached_content(self, tmp_path, monkeypatch):
        monkeypatch.setattr("scraper.fetcher.CACHE_DIR", str(tmp_path))
        cached_html = "<html><body>cached</body></html>"
        mock_resp = MagicMock()
        mock_resp.content = SAMPLE_HTML.encode("utf-8")
        with patch("scraper.fetcher.requests.get", return_value=mock_resp):
            fetch_html("https://example.com/store/test/")
        # overwrite cache manually
        import hashlib
        url = "https://example.com/store/test/"
        fname = hashlib.md5(url.encode()).hexdigest() + ".html"
        (tmp_path / fname).write_text(cached_html, encoding="utf-8")
        result = fetch_html("https://example.com/store/test/")
        assert result == cached_html
