"""
scraper.py のテスト

- _parse_html: HTMLからテキスト抽出、script/style除去
- scrape_text: requestsで取得 → 短すぎる/エラー時はPlaywrightへフォールバック
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock

from scraper import _parse_html, scrape_text, MIN_TEXT_LENGTH, MAX_TEXT_LENGTH


# ---------------------------------------------------------------------------
# _parse_html
# ---------------------------------------------------------------------------

class TestParseHtml:
    def test_extracts_plain_text(self):
        html = "<html><body><p>Hello World</p></body></html>"
        result = _parse_html(html)
        assert "Hello World" in result

    def test_strips_script_tags(self):
        html = "<html><body><script>alert('xss')</script><p>本文</p></body></html>"
        result = _parse_html(html)
        assert "alert" not in result
        assert "本文" in result

    def test_strips_style_tags(self):
        html = "<html><head><style>body { color: red; }</style></head><body><p>内容</p></body></html>"
        result = _parse_html(html)
        assert "color" not in result
        assert "内容" in result

    def test_strips_both_script_and_style(self):
        html = """
        <html>
          <head><style>.cls{}</style></head>
          <body>
            <script>var x = 1;</script>
            <p>テキスト</p>
          </body>
        </html>
        """
        result = _parse_html(html)
        assert "var x" not in result
        assert ".cls" not in result
        assert "テキスト" in result

    def test_returns_empty_string_for_empty_html(self):
        result = _parse_html("")
        assert result == ""

    def test_uses_newline_separator(self):
        html = "<html><body><p>Line1</p><p>Line2</p></body></html>"
        result = _parse_html(html)
        assert "\n" in result


# ---------------------------------------------------------------------------
# scrape_text
# ---------------------------------------------------------------------------

LONG_TEXT = "あ" * (MIN_TEXT_LENGTH + 1)
SHORT_TEXT = "短い"


class TestScrapeText:
    async def test_uses_requests_when_text_is_sufficient(self):
        """requestsで十分な長さのテキストが取れる場合はPlaywrightを呼ばない"""
        mock_response = MagicMock()
        mock_response.text = f"<html><body>{'あ' * (MIN_TEXT_LENGTH + 1)}</body></html>"

        with patch("scraper._requests_get", return_value=mock_response) as mock_get, \
             patch("scraper._fetch_with_playwright", new_callable=AsyncMock) as mock_pw:
            result = await scrape_text("https://example.com")

        mock_get.assert_called_once_with("https://example.com")
        mock_pw.assert_not_called()
        assert len(result) > 0

    async def test_falls_back_to_playwright_when_text_too_short(self):
        """requestsで取得したテキストが短すぎる場合はPlaywrightにフォールバック"""
        mock_response = MagicMock()
        mock_response.text = f"<html><body>{SHORT_TEXT}</body></html>"

        with patch("scraper._requests_get", return_value=mock_response), \
             patch("scraper._fetch_with_playwright", new_callable=AsyncMock, return_value=LONG_TEXT) as mock_pw:
            result = await scrape_text("https://example.com")

        mock_pw.assert_called_once_with("https://example.com")
        assert result == LONG_TEXT

    async def test_falls_back_to_playwright_on_requests_error(self):
        """requestsが例外を上げた場合はPlaywrightにフォールバック"""
        with patch("scraper._requests_get", side_effect=Exception("connection error")), \
             patch("scraper._fetch_with_playwright", new_callable=AsyncMock, return_value=LONG_TEXT) as mock_pw:
            result = await scrape_text("https://example.com")

        mock_pw.assert_called_once()
        assert result == LONG_TEXT

    async def test_truncates_text_to_max_length(self):
        """MAX_TEXT_LENGTH を超えるテキストは切り捨てる"""
        long_html = f"<html><body>{'あ' * (MAX_TEXT_LENGTH + 1000)}</body></html>"
        mock_response = MagicMock()
        mock_response.text = long_html

        with patch("scraper._requests_get", return_value=mock_response), \
             patch("scraper._fetch_with_playwright", new_callable=AsyncMock):
            result = await scrape_text("https://example.com")

        assert len(result) <= MAX_TEXT_LENGTH

    async def test_passes_url_to_playwright(self):
        """Playwright フォールバック時に正しいURLが渡される"""
        with patch("scraper._requests_get", side_effect=Exception("error")), \
             patch("scraper._fetch_with_playwright", new_callable=AsyncMock, return_value="content") as mock_pw:
            await scrape_text("https://target.example.com/page")

        mock_pw.assert_called_once_with("https://target.example.com/page")
