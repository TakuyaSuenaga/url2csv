# Playwright公式イメージ（Chromiumの依存ライブラリが全て入っている）
FROM mcr.microsoft.com/playwright/python:v1.58.0-jammy

WORKDIR /app

# uvをインストール
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 依存関係ファイルを先にコピー（キャッシュを有効活用）
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen

# PlaywrightでChromiumをインストール（システム依存はベースイメージ済み）
RUN uv run playwright install chromium

# ソースコードをコピー
COPY . .

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
