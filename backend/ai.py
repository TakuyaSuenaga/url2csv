import json
import re
from claude_agent_sdk import query, ClaudeAgentOptions
from claude_agent_sdk.types import AssistantMessage, TextBlock


async def parse_with_ai(text: str, columns: list[str]) -> list:
    keys = "、".join(f'「{c}」' for c in columns)
    example_obj = ", ".join(f'"{c}": "..."' for c in columns)
    prompt = f"""
あなたはデータ抽出エンジンです。

以下のテキストから {keys} を抽出してください。

出力条件:
- JSON配列のみ
- 余計な文章は禁止
- 必ずキーは {keys}

例:
[
  {{{example_obj}}}
]

見つからない場合:
[]

テキスト:
{text}
"""

    options = ClaudeAgentOptions(
        allowed_tools=[],
        permission_mode="acceptEdits",
    )

    content = ""
    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    content += block.text

    # Markdownコードブロックを除去
    content = re.sub(r"```(?:json)?\s*", "", content).strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        print(f"JSON解析エラー: {e}\nレスポンス: {content[:200]}")
        return []
