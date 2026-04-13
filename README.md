# URL to CSV

URLを入力するだけで、AIがページ内容を解析し、指定した項目をCSVとして抽出するツール。

## 概要

- **スクレイピング**: 静的サイトは requests、JavaScriptで動的に描画されるサイト（Amazon等）は Playwright（Chromium）で取得
- **AI解析**: Claude Agent SDK を使い、取得したテキストから指定項目を自動抽出
- **出力**: 画面でプレビュー表示 + CSVダウンロード

## 機能

- 複数URLの一括処理（1行に1URL）
- 抽出する項目をカンマ区切りで自由に指定（例: `商品名, 価格, カテゴリー`）
- ページネーション自動追跡（最大3ページ）
- 遅延ロード（無限スクロール）対応
- 重複行の自動除去
- リアルタイム進捗表示
- 入力内容（URL・項目）はブラウザに自動保存

## 技術スタック

| レイヤー | 技術 |
|---|---|
| フロントエンド | React + TypeScript + Vite + Tailwind CSS |
| バックエンド | Python + FastAPI + uvicorn |
| スクレイピング | requests + BeautifulSoup + Playwright |
| AI | Claude Agent SDK |
| パッケージ管理 | uv（Python）/ npm（Node） |

## セットアップ

### 必要なもの

- Python 3.11+
- Node.js 20+
- uv（`pip install uv` または [公式サイト](https://docs.astral.sh/uv/)）
- Anthropic APIキー

### 環境変数の設定

```bash
cp backend/.env.example backend/.env
```

`backend/.env` を編集して APIキーを設定：

```
ANTHROPIC_API_KEY=your_api_key_here
```

### ローカルで起動

**バックエンド:**

```bash
cd backend
uv run playwright install chromium
uv run uvicorn main:app --reload
```

**フロントエンド（別ターミナル）:**

```bash
cd frontend
npm install
npm run dev
```

ブラウザで `http://localhost:5173` を開く。

### Dockerで起動

```bash
docker-compose up --build
```

ブラウザで `http://localhost:3000` を開く。

> 初回ビルドはPlaywrightのベースイメージ（約1.5GB）のダウンロードがあるため時間がかかります。

## 使い方

1. URLを入力欄に貼り付ける（複数の場合は1行に1URL）
2. 抽出する項目をカンマ区切りで入力（例: `会社名, 住所, 電話番号`）
3. 「抽出」ボタンをクリック
4. 結果が表示されたら「CSVをダウンロード」で保存

## ディレクトリ構成

```
url-to-csv/
├── backend/
│   ├── main.py        # FastAPI エントリーポイント
│   ├── scraper.py     # スクレイピング（requests + Playwright）
│   ├── ai.py          # Claude Agent SDK による抽出
│   ├── pyproject.toml
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.tsx    # メイン画面
│   │   └── main.tsx
│   ├── package.json
│   └── nginx.conf
└── docker-compose.yml
```
