"""Tests for scraper/geocoder.py"""
import pytest
from unittest.mock import patch
from scraper.geocoder import geocode, clean_address

GSI_SUCCESS_RESPONSE = [
    {
        "geometry": {"coordinates": [139.6237, 35.9081]},
        "properties": {"title": "さいたま市大宮区吉敷町"},
    }
]

GSI_EMPTY_RESPONSE = []


class TestCleanAddress:
    def test_removes_postal_code(self):
        addr = "〒3309559　さいたま市大宮区吉敷町４ー２６３ー１コクーン2　2階"
        result = clean_address(addr)
        assert "〒" not in result
        assert "3309559" not in result

    def test_keeps_city_and_street(self):
        addr = "〒3309559　さいたま市大宮区吉敷町４ー２６３ー１"
        result = clean_address(addr)
        assert "さいたま市大宮区" in result

    def test_handles_address_without_postal_code(self):
        addr = "さいたま市浦和区高砂１ー２ー３"
        result = clean_address(addr)
        assert result == addr

    def test_strips_whitespace(self):
        addr = "　さいたま市大宮区吉敷町　"
        result = clean_address(addr)
        assert result == result.strip()


class TestGeocode:
    def test_returns_lat_lng_on_success(self):
        with patch("scraper.geocoder.requests.get") as mock_get:
            mock_get.return_value.json.return_value = GSI_SUCCESS_RESPONSE
            lat, lng = geocode("さいたま市大宮区吉敷町４ー２６３ー１")
        assert abs(lat - 35.9081) < 0.001
        assert abs(lng - 139.6237) < 0.001

    def test_returns_none_on_empty_response(self):
        with patch("scraper.geocoder.requests.get") as mock_get:
            mock_get.return_value.json.return_value = GSI_EMPTY_RESPONSE
            result = geocode("存在しない住所")
        assert result == (None, None)

    def test_returns_none_on_http_error(self):
        with patch("scraper.geocoder.requests.get", side_effect=Exception("timeout")):
            result = geocode("さいたま市大宮区吉敷町")
        assert result == (None, None)

    def test_calls_gsi_api(self):
        with patch("scraper.geocoder.requests.get") as mock_get:
            mock_get.return_value.json.return_value = GSI_SUCCESS_RESPONSE
            geocode("さいたま市大宮区")
        call_url = mock_get.call_args[0][0]
        assert "msearch.gsi.go.jp" in call_url

    def test_encodes_address_in_query(self):
        with patch("scraper.geocoder.requests.get") as mock_get:
            mock_get.return_value.json.return_value = GSI_SUCCESS_RESPONSE
            geocode("さいたま市大宮区")
        call_url = mock_get.call_args[0][0]
        assert "q=" in call_url
