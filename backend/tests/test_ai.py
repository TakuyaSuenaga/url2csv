"""
ai.py のテスト

- _build_prompt: カラム情報がプロンプトに正しく含まれるか
- parse_with_ai: JSON後処理（キー補完、非listガード、JSONエラー、マークダウン除去）
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from ai import _build_prompt, parse_with_ai
from claude_agent_sdk.types import AssistantMessage, TextBlock


# ---------------------------------------------------------------------------
# _build_prompt
# ---------------------------------------------------------------------------

class TestBuildPrompt:
    def test_contains_all_columns_in_japanese(self):
        prompt = _build_prompt("テキスト", ["会社名", "住所"])
        assert "「会社名」" in prompt
        assert "「住所」" in prompt

    def test_contains_all_columns_as_json_keys(self):
        prompt = _build_prompt("テキスト", ["会社名", "住所"])
        assert '"会社名"' in prompt
        assert '"住所"' in prompt

    def test_contains_source_text(self):
        prompt = _build_prompt("サンプルテキスト", ["会社名"])
        assert "サンプルテキスト" in prompt

    def test_single_column(self):
        prompt = _build_prompt("テキスト", ["電話番号"])
        assert "「電話番号」" in prompt
        assert '"電話番号"' in prompt

    def test_many_columns(self):
        columns = ["会社名", "住所", "電話番号", "メール", "代表者"]
        prompt = _build_prompt("テキスト", columns)
        for col in columns:
            assert col in prompt

    def test_prompt_mentions_json_array(self):
        prompt = _build_prompt("テキスト", ["会社名"])
        assert "JSON" in prompt or "json" in prompt


# ---------------------------------------------------------------------------
# parse_with_ai
# ---------------------------------------------------------------------------

def _make_mock_query(response_text: str):
    """claude_agent_sdk.query をモックするヘルパー"""
    async def fake_query(*args, **kwargs):
        msg = MagicMock(spec=AssistantMessage)
        block = MagicMock(spec=TextBlock)
        block.text = response_text
        msg.content = [block]
        yield msg

    return fake_query


class TestParseWithAi:
    async def test_returns_extracted_data(self):
        """正常なJSON配列が返ってくる場合"""
        response = '[{"会社名": "テスト株式会社", "住所": "東京都新宿区"}]'
        with patch("ai.query", side_effect=_make_mock_query(response)):
            result = await parse_with_ai("テキスト", ["会社名", "住所"])

        assert len(result) == 1
        assert result[0]["会社名"] == "テスト株式会社"
        assert result[0]["住所"] == "東京都新宿区"

    async def test_fills_missing_keys_with_empty_string(self):
        """AIがキーを省略した場合は空文字で補完される"""
        # 「住所」キーが欠けているレスポンス
        response = '[{"会社名": "株式会社ABC"}]'
        with patch("ai.query", side_effect=_make_mock_query(response)):
            result = await parse_with_ai("テキスト", ["会社名", "住所"])

        assert result[0]["会社名"] == "株式会社ABC"
        assert result[0]["住所"] == ""  # 補完される

    async def test_all_keys_always_present(self):
        """結果の全行に全カラムキーが揃っている"""
        response = '[{"会社名": "A"}, {"住所": "B"}]'
        with patch("ai.query", side_effect=_make_mock_query(response)):
            result = await parse_with_ai("テキスト", ["会社名", "住所"])

        for row in result:
            assert "会社名" in row
            assert "住所" in row

    async def test_strips_markdown_code_block(self):
        """```json ... ``` で囲まれたレスポンスを正しくパースできる"""
        response = '```json\n[{"会社名": "株式会社X", "住所": "大阪府"}]\n```'
        with patch("ai.query", side_effect=_make_mock_query(response)):
            result = await parse_with_ai("テキスト", ["会社名", "住所"])

        assert len(result) == 1
        assert result[0]["会社名"] == "株式会社X"

    async def test_returns_empty_list_on_invalid_json(self):
        """JSONとして解析できないレスポンスは [] を返す"""
        response = "これはJSONではありません"
        with patch("ai.query", side_effect=_make_mock_query(response)):
            result = await parse_with_ai("テキスト", ["会社名", "住所"])

        assert result == []

    async def test_returns_empty_list_when_ai_returns_empty(self):
        """AIが [] を返した場合は [] を返す"""
        with patch("ai.query", side_effect=_make_mock_query("[]")):
            result = await parse_with_ai("テキスト", ["会社名", "住所"])

        assert result == []

    async def test_returns_empty_list_when_response_is_not_list(self):
        """AIがdict（非list）を返した場合は [] を返す"""
        response = '{"会社名": "テスト", "住所": "東京"}'
        with patch("ai.query", side_effect=_make_mock_query(response)):
            result = await parse_with_ai("テキスト", ["会社名", "住所"])

        assert result == []

    async def test_skips_non_dict_items_in_list(self):
        """list内にdictでない要素が混在しても安全にスキップする"""
        response = '[{"会社名": "正常", "住所": "東京"}, "文字列", 123]'
        with patch("ai.query", side_effect=_make_mock_query(response)):
            result = await parse_with_ai("テキスト", ["会社名", "住所"])

        assert len(result) == 1
        assert result[0]["会社名"] == "正常"

    async def test_returns_multiple_rows(self):
        """複数件のデータが正しく返ってくる"""
        response = '[{"会社名": "A社", "住所": "東京"}, {"会社名": "B社", "住所": "大阪"}]'
        with patch("ai.query", side_effect=_make_mock_query(response)):
            result = await parse_with_ai("テキスト", ["会社名", "住所"])

        assert len(result) == 2
        assert result[0]["会社名"] == "A社"
        assert result[1]["会社名"] == "B社"

    async def test_values_are_coerced_to_string(self):
        """値が数値などでも文字列に変換される"""
        response = '[{"会社名": "テスト", "住所": 12345}]'
        with patch("ai.query", side_effect=_make_mock_query(response)):
            result = await parse_with_ai("テキスト", ["会社名", "住所"])

        assert isinstance(result[0]["住所"], str)
        assert result[0]["住所"] == "12345"
