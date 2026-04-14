"""
main.py のテスト

- /extract エンドポイント: SSEイベント形式、progressイベント、resultイベント
- エラー処理: スクレイピング失敗・AI解析失敗でも他URLの処理を継続
- 重複除去: 同一データは1件にまとめられる
"""
import json
import pytest
from unittest.mock import AsyncMock, patch

import httpx
from httpx import ASGITransport

from main import app


# ---------------------------------------------------------------------------
# ヘルパー
# ---------------------------------------------------------------------------

def parse_sse_events(text: str) -> list[dict]:
    """SSEレスポンス本文から data: 行を抽出してJSONとしてパースする"""
    events = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("data: "):
            events.append(json.loads(line[6:]))
    return events


def events_of_type(events: list[dict], event_type: str) -> list[dict]:
    return [e for e in events if e.get("type") == event_type]


async def post_extract(payload: dict) -> list[dict]:
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/extract",
            json=payload,
            timeout=30.0,
        )
    return parse_sse_events(response.text)


# ---------------------------------------------------------------------------
# 正常系
# ---------------------------------------------------------------------------

class TestExtractHappyPath:
    async def test_result_event_is_emitted(self):
        """/extract は最後に type=result イベントを返す"""
        with patch("main.scrape_text", new_callable=AsyncMock, return_value="テキスト"), \
             patch("main.parse_with_ai", new_callable=AsyncMock,
                   return_value=[{"会社名": "テスト株式会社", "住所": "東京都"}]):
            events = await post_extract({"urls": ["https://example.com"], "columns": ["会社名", "住所"]})

        result_events = events_of_type(events, "result")
        assert len(result_events) == 1
        assert result_events[0]["data"] == [{"会社名": "テスト株式会社", "住所": "東京都"}]

    async def test_progress_events_are_emitted_per_url(self):
        """各URLに対してprogress（スクレイピング・AI解析）イベントが出る"""
        with patch("main.scrape_text", new_callable=AsyncMock, return_value="テキスト"), \
             patch("main.parse_with_ai", new_callable=AsyncMock, return_value=[]):
            events = await post_extract({"urls": ["https://a.com", "https://b.com"], "columns": ["会社名"]})

        progress_events = events_of_type(events, "progress")
        # 2 URL × 2 progress（スクレイピング + AI）= 4件
        assert len(progress_events) == 4

    async def test_multiple_urls_are_all_processed(self):
        """複数URLの結果がまとめてresultに含まれる"""
        ai_results = [
            [{"会社名": "A社", "住所": "東京"}],
            [{"会社名": "B社", "住所": "大阪"}],
        ]
        with patch("main.scrape_text", new_callable=AsyncMock, return_value="テキスト"), \
             patch("main.parse_with_ai", new_callable=AsyncMock, side_effect=ai_results):
            events = await post_extract({"urls": ["https://a.com", "https://b.com"], "columns": ["会社名", "住所"]})

        result = events_of_type(events, "result")[0]["data"]
        assert len(result) == 2
        company_names = {r["会社名"] for r in result}
        assert company_names == {"A社", "B社"}

    async def test_empty_result_when_no_data_extracted(self):
        """AIが何も抽出しない場合はresult.dataが空リスト"""
        with patch("main.scrape_text", new_callable=AsyncMock, return_value="テキスト"), \
             patch("main.parse_with_ai", new_callable=AsyncMock, return_value=[]):
            events = await post_extract({"urls": ["https://example.com"], "columns": ["会社名"]})

        result = events_of_type(events, "result")[0]["data"]
        assert result == []

    async def test_default_columns_are_used(self):
        """columns を省略した場合はデフォルト値（会社名・住所）が使われる"""
        captured_columns = []

        async def capture_ai(text, columns):
            captured_columns.extend(columns)
            return []

        with patch("main.scrape_text", new_callable=AsyncMock, return_value="テキスト"), \
             patch("main.parse_with_ai", side_effect=capture_ai):
            await post_extract({"urls": ["https://example.com"]})

        assert "会社名" in captured_columns
        assert "住所" in captured_columns


# ---------------------------------------------------------------------------
# 重複除去
# ---------------------------------------------------------------------------

class TestDeduplication:
    async def test_duplicate_rows_are_removed(self):
        """同一データが複数URLから抽出された場合は1件にまとめる"""
        duplicate = {"会社名": "重複株式会社", "住所": "東京都"}
        with patch("main.scrape_text", new_callable=AsyncMock, return_value="テキスト"), \
             patch("main.parse_with_ai", new_callable=AsyncMock,
                   return_value=[duplicate]):
            events = await post_extract({
                "urls": ["https://a.com", "https://b.com"],
                "columns": ["会社名", "住所"],
            })

        result = events_of_type(events, "result")[0]["data"]
        assert len(result) == 1

    async def test_unique_rows_are_all_kept(self):
        """異なるデータは重複除去されない"""
        ai_results = [
            [{"会社名": "A社", "住所": "東京"}],
            [{"会社名": "B社", "住所": "大阪"}],
        ]
        with patch("main.scrape_text", new_callable=AsyncMock, return_value="テキスト"), \
             patch("main.parse_with_ai", new_callable=AsyncMock, side_effect=ai_results):
            events = await post_extract({"urls": ["https://a.com", "https://b.com"], "columns": ["会社名", "住所"]})

        result = events_of_type(events, "result")[0]["data"]
        assert len(result) == 2


# ---------------------------------------------------------------------------
# エラー処理
# ---------------------------------------------------------------------------

class TestErrorHandling:
    async def test_scraper_error_emits_error_event(self):
        """スクレイピング失敗時はerrorイベントが出る"""
        with patch("main.scrape_text", new_callable=AsyncMock,
                   side_effect=Exception("接続タイムアウト")):
            events = await post_extract({"urls": ["https://broken.com"], "columns": ["会社名"]})

        error_events = events_of_type(events, "error")
        assert len(error_events) == 1
        assert "接続タイムアウト" in error_events[0]["message"]

    async def test_scraper_error_continues_to_next_url(self):
        """1つのURLのスクレイピングが失敗しても残りのURLを処理する"""
        scrape_side_effects = [Exception("失敗"), "正常なテキスト"]
        with patch("main.scrape_text", new_callable=AsyncMock,
                   side_effect=scrape_side_effects), \
             patch("main.parse_with_ai", new_callable=AsyncMock,
                   return_value=[{"会社名": "成功した会社", "住所": "東京"}]):
            events = await post_extract({
                "urls": ["https://bad.com", "https://good.com"],
                "columns": ["会社名", "住所"],
            })

        result = events_of_type(events, "result")[0]["data"]
        assert len(result) == 1
        assert result[0]["会社名"] == "成功した会社"

    async def test_ai_error_emits_error_event(self):
        """AI解析失敗時はerrorイベントが出る"""
        with patch("main.scrape_text", new_callable=AsyncMock, return_value="テキスト"), \
             patch("main.parse_with_ai", new_callable=AsyncMock,
                   side_effect=Exception("APIエラー")):
            events = await post_extract({"urls": ["https://example.com"], "columns": ["会社名"]})

        error_events = events_of_type(events, "error")
        assert len(error_events) == 1
        assert "APIエラー" in error_events[0]["message"]

    async def test_ai_error_continues_to_next_url(self):
        """AI解析が1URLで失敗しても残りのURLを処理する"""
        ai_side_effects = [Exception("AI失敗"), [{"会社名": "成功", "住所": "大阪"}]]
        with patch("main.scrape_text", new_callable=AsyncMock, return_value="テキスト"), \
             patch("main.parse_with_ai", new_callable=AsyncMock,
                   side_effect=ai_side_effects):
            events = await post_extract({
                "urls": ["https://a.com", "https://b.com"],
                "columns": ["会社名", "住所"],
            })

        result = events_of_type(events, "result")[0]["data"]
        assert len(result) == 1
        assert result[0]["会社名"] == "成功"

    async def test_error_url_is_included_in_message(self):
        """エラーメッセージに失敗したURLが含まれる"""
        target_url = "https://fail.example.com"
        with patch("main.scrape_text", new_callable=AsyncMock,
                   side_effect=Exception("timeout")):
            events = await post_extract({"urls": [target_url], "columns": ["会社名"]})

        error_events = events_of_type(events, "error")
        assert target_url in error_events[0]["message"]
