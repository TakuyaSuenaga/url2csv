from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from scraper import scrape_text
from ai import parse_with_ai
import pandas as pd
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class RequestBody(BaseModel):
    urls: list[str]
    columns: list[str] = ["会社名", "住所"]


@app.post("/extract")
async def extract(body: RequestBody):
    async def generate():
        all_data = []
        total = len(body.urls)

        for i, url in enumerate(body.urls):
            yield {"data": json.dumps({"type": "progress", "message": f"スクレイピング中... ({i + 1}/{total})"})}

            try:
                text = await scrape_text(url)
            except Exception as e:
                yield {"data": json.dumps({"type": "error", "message": f"URL取得失敗 ({url}): {e}"})}
                continue

            yield {"data": json.dumps({"type": "progress", "message": f"AI解析中... ({i + 1}/{total})"})}

            try:
                data = await parse_with_ai(text, body.columns)
            except Exception as e:
                yield {"data": json.dumps({"type": "error", "message": f"AI解析失敗 ({url}): {e}"})}
                continue
            all_data.extend(data)

        # 重複除去
        seen: set[tuple] = set()
        unique_data = []
        for row in all_data:
            key = tuple(str(v) for v in row.values())
            if key not in seen:
                seen.add(key)
                unique_data.append(row)

        if unique_data:
            df = pd.DataFrame(unique_data)
            df.to_csv("output.csv", index=False)

        yield {"data": json.dumps({"type": "result", "data": unique_data})}

    return EventSourceResponse(generate())
