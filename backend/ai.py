import json
import re
from claude_agent_sdk import query, ClaudeAgentOptions
from claude_agent_sdk.types import AssistantMessage, TextBlock


def _build_prompt(text: str, columns: list[str]) -> str:
    keys_ja = "、".join(f'「{c}」' for c in columns)
    keys_json = ", ".join(f'"{c}"' for c in columns)
    example_obj = ", ".join(f'"{c}": "値"' for c in columns)
    null_obj = ", ".join(f'"{c}": ""' for c in columns)

    return f"""あなたは構造化データ抽出エンジンです。

## タスク
以下のテキストから {keys_ja} を抽出し、JSON配列として出力してください。

## 出力ルール
1. 出力はJSON配列のみ。説明文・コードブロック・マークダウン記法は禁止
2. 配列の各要素は必ず {keys_json} のキーを持つオブジェクト
3. 項目が見つからない・不明な場合はそのキーの値を空文字列 "" にする（省略禁止）
4. 同一エンティティの情報が複数箇所に分散している場合は1件にまとめる
5. 明らかに異なるエンティティが複数ある場合は複数件出力する
6. テキストに該当する情報が一切ない場合のみ [] を返す

## 出力例（複数件の場合）
[
  {{{example_obj}}},
  {{{example_obj}}}
]

## 出力例（項目が一部不明な場合）
[
  {{{null_obj}}}
]

## 対象テキスト
{text}"""


async def parse_with_ai(text: str, columns: list[str]) -> list:
    prompt = _build_prompt(text, columns)

    options = ClaudeAgentOptions(
        allowed_tools=[],
    )

    content = ""
    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    content += block.text

    # Markdownコードブロック・末尾の ``` を除去
    content = re.sub(r"```(?:json)?\s*", "", content).strip()

    try:
        result = json.loads(content)
        if not isinstance(result, list):
            return []
        # 全キーが揃っているか補完する
        filled = []
        for row in result:
            if not isinstance(row, dict):
                continue
            filled.append({col: str(row.get(col, "")) for col in columns})
        return filled
    except json.JSONDecodeError as e:
        print(f"JSON解析エラー: {e}\nレスポンス: {content[:200]}")
        return []
