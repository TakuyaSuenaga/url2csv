# URL to CSV — プロジェクトガイド

## プロジェクト概要

URLを入力するとWebページをスクレイピングし、AIが指定した項目を抽出してCSVとして返すツール。

- **バックエンド**: FastAPI + Playwright + Claude Agent SDK（Python）
- **フロントエンド**: React + TypeScript + Tailwind CSS
- **インフラ**: Docker Compose

## スキルの使用ルール

このプロジェクトには `.claude/skills/` にスキルが用意されています。
**ユーザーの指示に対応するスキルがある場合は、必ずそのスキルを読み込んで従ってください。**

### スキル選択の優先順位

1. ユーザーの指示を受けたら、まず `.claude/skills/` 内のスキルを確認する
2. 指示に合致するスキルが1つ以上あれば、該当スキルの `SKILL.md` を読み込んで手順に従う
3. 複数のスキルが該当する場合は、最も関連性の高いものを選択し、必要なら複数を順番に適用する
4. 対応するスキルがない場合のみ、通常の判断で回答する

### スキルと用途の対応表

| スキル | 使用する場面 |
|--------|-------------|
| `code-review-skill` | コードのレビュー・バグ確認・改善提案を求められたとき |
| `devops-assistant` | Docker・デプロイ・CI/CD・インフラ設定を扱うとき |
| `ui-ux-layout-advisor` | UI改善・レイアウト見直し・フロントエンドデザインを求められたとき |
| `deep-research-synthesizer` | 大量テキストの分析・プロンプト設計・情報抽出の精度改善を求められたとき |
| `workflow-automation-agent` | 複雑なタスクをステップ分解・自動化フロー設計を求められたとき |
| `flowchart-decision-builder` | 処理フロー・分岐ロジックの可視化を求められたとき |
| `knowledge-structuring-skill` | 情報の整理・構造化・ドキュメント化を求められたとき |
| `scqa-writing-framework` | ドキュメント・記事・説明文の執筆を求められたとき |
| `long-form-summary-compressor` | 長文の要約・圧縮を求められたとき |
| `skill-creator-meta-skill` | 新しいスキルの作成・既存スキルの改善を求められたとき |
| `excalidraw-diagram-generator` | 図・アーキテクチャ図・関係図の作成を求められたとき |
| `infographic-builder` | インフォグラフィック・視覚的なまとめを求められたとき |
| `source-validation-skill` | 情報源の信頼性確認・検証を求められたとき |
| `competitive-intelligence-skill` | 製品・ツール・サービスの比較分析を求められたとき |
| `content-repurposing-engine` | 既存コンテンツを別フォーマットに変換するとき |
| `tone-style-enforcer` | 特定のトーン・ブランドボイスに統一するとき |
| `structured-copywriting-skill` | マーケティングコピー・SNS投稿の作成を求められたとき |
| `hook-generator` | 冒頭フック・導入文の作成を求められたとき |
| `video-script-generator` | 動画スクリプトの作成を求められたとき |
| `video-editing-planner` | 動画編集の構成・カット計画を求められたとき |
| `caption-subtitle-formatter` | 字幕・キャプションの整形を求められたとき |
| `onchain-transaction-analyzer` | ブロックチェーントランザクションの分析を求められたとき |

## 開発メモ

- バックエンド起動: `cd backend && uv run uvicorn main:app --reload`
- フロントエンド起動: `cd frontend && npm run dev`
- Docker起動: `docker compose up --build`
- Python バージョン: `.python-version` 参照
- 依存管理: `uv`（`pip` は使わない）
