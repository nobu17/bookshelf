# Bookshelf AI Guide

このドキュメントは、AIエージェントや新しい開発者がこのリポジトリを安全に理解・変更するための作業地図です。実装の事実はコードを優先してください。

## プロジェクト概要

Bookshelf は、書籍と読書レビューを管理する Web アプリケーションです。

- Backend: FastAPI, Pydantic, SQLAlchemy, Alembic, PostgreSQL
- Frontend: Vite, React 18, TypeScript, MUI, React Router
- Tests: pytest, FastAPI TestClient, pytest-docker
- 外部検索: フロントエンドの provider 境界から Google Books API と openBD API を利用

主な機能:

- ユーザー認証と bearer token 認証
- 書籍の登録・ISBN検索
- タグの作成・更新・削除、書籍へのタグ付け
- 読書レビューの作成・更新・削除
- 最新レビュー、ユーザー別レビュー、編集用レビュー一覧の取得

## ディレクトリ構成

```text
bookshelf_app/
  main.py                         FastAPI アプリのエントリポイント
  config.py                       アプリ設定: .env / .env.prod
  api/
    auth/                         認証ドメイン・サービス・ルータ
    books/                        書籍ドメイン・サービス・ルータ
    reviews/                      レビュードメイン・サービス・ルータ
    tags/                         タグドメイン・サービス・ルータ
    book_with_reviews/            書籍+レビュー集約の読み取りAPI
    shared/                       共通エラー、ルータ、値オブジェクト
  infra/
    dependencies.py               FastAPI Depends の組み立て
    db/                           SQLAlchemy DTO, repository, query service, migrations
    memory/                       メモリ実装の一部
    other/crypt.py                パスワードハッシュ/JWT系の実装
  frontend/                       Vite React アプリ
  helper/                         middleware, error handler, SPA配信
  tools/                          seed投入用ツール
tests/
  unit/                           ドメイン中心の単体テスト
  integration/                    TestClient + PostgreSQL 統合テスト
test_env/                         pytest-docker 用 PostgreSQL
```

## Backend Architecture

バックエンドはおおむね次の責務分離です。

- `api/*/domain.py`: ドメインモデル、値オブジェクト、repository interface、ドメインサービス
- `api/*/service.py`: アプリケーションサービス、DTO変換、認可以外のユースケース制御
- `api/*/router.py`: FastAPI ルータ、Pydantic request/response model、Depends
- `infra/db/*.py`: SQLAlchemy DTO、DB repository/query service、domain/app model への変換
- `infra/dependencies.py`: 本番用 dependency injection。DB repository と service をここで結線

変更時の基本方針:

- バリデーションや業務ルールはまず `domain.py` に置く。
- API入出力の形だけの変更は `router.py` とフロント API client を合わせて変更する。
- 永続化方式やクエリ変更は `infra/db/*.py` に閉じる。
- DBスキーマ変更は Alembic migration を追加する。

## Key Domain Rules

### Auth

実装:

- `bookshelf_app/api/auth/domain.py`
- `bookshelf_app/api/auth/service.py`
- `bookshelf_app/infra/other/crypt.py`

ルール:

- email は単純なメール形式のみ許可。
- password は 8-100 文字、英小文字・英大文字・数字を必須。
- user name は 1-20 文字。
- role は現状 `admin` のみが明示的に扱われる。
- `get_user_dependency` は認証済みユーザー、`get_admin_dependency` は admin 権限を要求する。

注意:

- `oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")` だが、実際のログインAPIは `/api/auth/token`。OpenAPI表示を直す場合はここも確認する。

### Books

実装:

- `bookshelf_app/api/books/domain.py`
- `bookshelf_app/api/books/service.py`
- `bookshelf_app/infra/db/books.py`

ルール:

- ISBN13 は 13桁、`978` または `979` 開始、数値のみ、チェックディジット検証あり。
- title, publisher, author は最大 100 文字。
- authors は 1 件以上必須。
- 同一書籍判定は「ISBN13 が同じ、かつ出版年が同じ」。
- 同一書籍は登録不可。ただし同じ ISBN13 でも出版年が異なれば登録可能。
- 書籍作成時の tags は空。タグ付けは `/api/books/tags/{id}` で更新する。

注意:

- `BookService.update_tags` の not found エラーでは Python 組み込みの `id` が文字列化されている箇所がある。修正時は `model.book_id` を使うのが自然。
- `PUT /api/books/tags/{id}` は path の `id` を受けているが、実際は body の `book_id` を使っている。

### Tags

実装:

- `bookshelf_app/api/tags/domain.py`
- `bookshelf_app/api/tags/service.py`
- `bookshelf_app/infra/db/tags.py`

ルール:

- tag name は空不可、ドメイン上は 15 文字以下。
- 同名タグは作成・更新不可。
- delete は物理削除ではなく `is_deleted=True`。
- create は認証済みユーザー、update/delete は admin のみ。

注意:

- DBカラムは `String(length=30)` だがドメイン制約は 15 文字以下。

### Reviews

実装:

- `bookshelf_app/api/reviews/domain.py`
- `bookshelf_app/api/reviews/service.py`
- `bookshelf_app/infra/db/reviews.py`

状態:

- `0`: NOT_YET
- `1`: IN_PROGRESS
- `2`: COMPLETED

ルール:

- content は空文字を許容し、最大 10000 文字。
- COMPLETED にする場合は `completed_at` 必須。
- `completed_at` は `TimeUtil.get_jst` で JST に寄せる。
- 同一ユーザー・同一書籍に対して、NOT_YET または IN_PROGRESS のレビューは合計 1 件まで。
- COMPLETED のレビューは同一ユーザー・同一書籍に複数作成可能。
- delete は `is_deleted=True` の論理削除。
- delete は admin またはレビュー所有者のみ可能。

注意:

- `SqlBookReviewRepository.find_latest_modified` は `order_by(BookReviewDTO.last_modified_at)` で昇順。名前から「最新順」を期待するなら降順にする必要がある。
- `BookReviewService.update` は更新者が所有者かどうかを明示チェックしていない。現在は既存レビューの `user_id` を使って更新後モデルを作るため、他人の `review_id` を知っていれば更新できる可能性がある。認可まわりの変更時は要確認。

### Book With Reviews

実装:

- `bookshelf_app/api/book_with_reviews/router.py`
- `bookshelf_app/api/book_with_reviews/service.py`
- `bookshelf_app/infra/db/book_with_reviews.py`

用途:

- 書籍・タグ・レビュー・レビュー投稿者をまとめて返す読み取りAPI。
- 一覧表示やマイページの主要データ取得で使う。

公開系API:

- `/api/book_with_reviews/latest/{max_count}`: draft でないレビューを対象
- `/api/book_with_reviews/user_id/{user_id}`: 特定ユーザーの公開レビュー
- `/api/book_with_reviews/me`: 自分の公開レビュー
- `/api/book_with_reviews/for_edit/me`: 自分の draft 含むレビュー
- `/api/book_with_reviews/for_edit/book_id/{book_id}`: 自分の特定書籍レビュー編集用

注意:

- `BookWithReviewLatestInputAppModel` の `__post_init__` がクラス外に定義されているため、dataclass の検証としては動かない。`BookReviewService.find_latest_modified` には max_count 検証があるが、book_with_reviews 側は要確認。
- query service 側も `last_modified_at` 昇順。

## API Summary

すべて `bookshelf_app/main.py` で `/api` prefix 配下に include されます。

Auth:

- `POST /api/auth/token`
- `GET /api/users/me`

Books:

- `POST /api/books` auth required
- `GET /api/books/isbn13/{isbn13}`
- `GET /api/books/book_id/{book_id}`
- `PUT /api/books/tags/{id}` auth required

Tags:

- `GET /api/tags`
- `POST /api/tags` auth required
- `PUT /api/tags/{id}` admin required
- `DELETE /api/tags/{id}` admin required

Reviews:

- `GET /api/reviews/find?review_id=...`
- `GET /api/reviews/me` auth required
- `GET /api/reviews/latest/{max_count}`
- `POST /api/reviews` auth required
- `PUT /api/reviews/{review_id}` auth required
- `DELETE /api/reviews/{review_id}` auth required

Book with reviews:

- `GET /api/book_with_reviews/latest/{max_count}`
- `GET /api/book_with_reviews/user_id/{user_id}`
- `GET /api/book_with_reviews/me` auth required
- `GET /api/book_with_reviews/for_edit/me` auth required
- `GET /api/book_with_reviews/for_edit/book_id/{book_id}` auth required

## Database

設定:

- `DB_CONNECTION` を `.env`, `.env.prod`, `.env.test` などで指定。
- Alembic script location は `bookshelf_app/infra/db/migrations`。
- `alembic.ini` の `sqlalchemy.url` は実質 `.env` の `DB_CONNECTION` を使う設計。

主なテーブル/DTO:

- `users`: `infra/db/auth.py`
- `tags`: `infra/db/tags.py`
- `books`, `publishers`, `authors`, association tables: `infra/db/books.py`
- `book_reviews`: `infra/db/reviews.py`

共通カラム:

- `Base`: `created_at`, `last_modified`, `is_deleted`
- `DeletableBase`: `is_deleted`

注意:

- `tags` と `book_reviews` は論理削除。
- `books` は現状削除実装なし。
- DTO は `to_domain_model` / `from_domain_model` を持つ。DB層の変更では domain 変換の整合性を必ず確認する。

## Frontend Architecture

場所:

- `bookshelf_app/frontend`

主要構成:

- `src/App.tsx`: ルーティング、MUI theme、Context provider
- `src/components/contexts/AuthContext.tsx`: 認証状態、ログイン/ログアウト、起動時の token 復元
- `src/hooks/UseAuthApi.tsx`: Axios interceptor で bearer token 付与、401/403 時にサインインへ遷移
- `src/libs/apis/*.ts`: バックエンド API client と snake_case/camelCase 変換
- `src/libs/bookSearch/*`: 外部書籍検索 provider。Google Books と openBD ISBN fallback を実装済み
- `src/types/data.ts`: フロントの主要データ型と ReviewState 定義
- `src/types/bookSearch.ts`: 外部検索結果の共通型
- `src/pages/*`: ページ単位
- `src/components/containers/*`: API hook と画面部品の接続
- `src/components/parts/*`: 表示部品、フォーム、ダイアログなど

ルーティング:

- `/mypage`
- `/mypage/reviews`
- `/mypage/book/search`
- `/auth/signin`
- `/auth/signout`
- `/reviews/user/:id`
- その他は `Home`

API設定:

- `VITE_APP_API_ROOT`: API root。空なら相対URL寄りの挙動。
- `VITE_APP_API_TIMEOUT`: Axios timeout。未指定なら 5000ms。

外部API:

- `src/libs/bookSearch/index.ts` が検索用 facade。
- `src/libs/bookSearch/provider.ts` に `BookSearchProvider` interface がある。
- `src/libs/bookSearch/providers/googleBooks.ts` が `https://www.googleapis.com/books/v1/volumes` を呼ぶ。
- `src/libs/bookSearch/providers/openBd.ts` が `https://api.openbd.jp/v1/get` を ISBN 検索用 fallback として呼ぶ。
- `src/libs/bookSearch/providers/composite.ts` が Google Books と openBD の結果を合成する。
- 外部APIレスポンスは `BookSearchResult` に正規化して UI に渡す。
- ISBN10 -> ISBN13 変換と出版日 parse は `src/libs/bookSearch/normalizers` に分離。
- 書影は検索結果の `imageUrl` を優先し、なければ `/images/no_image.jpg` に fallback する。
- ISBN検索では Google Books と openBD の両方を試し、両方取れた場合は openBD の有効な項目を優先する。ただし書影などは値がある方を使う。
- Google Books が 429 を返した場合、ISBN検索では openBD fallback を試す。通常キーワード検索では「しばらく時間を置いてから再度お試しください」というメッセージに正規化する。

注意:

- `vite.config.ts` の dev server proxy は `/books` のみだが、実際の API は `/api/...`。ローカル開発でAPI rootを使わない場合は proxy 設定の見直しが必要。
- `BookTag` 型は `{ id, name }` だがバックエンドの通常レスポンスは `{ tag_id, name }`。一部変換で未調整の箇所があるため、タグ表示変更時は API client と型を確認する。
- openBD は現状 ISBN fallback 用。キーワード検索は Google Books が担当する。

## Environment Variables

アプリ本体:

```text
CRYPT_SECRET_KEY
CRYPT_ALGORITHM
DB_CONNECTION
ENV_FILE
```

seed/tool:

```text
TOOL_INITIAL_USER_MAIL
TOOL_INITIAL_USER_NAME
TOOL_INITIAL_USER_PASS
```

frontend:

```text
VITE_APP_API_ROOT
VITE_APP_API_TIMEOUT
VITE_GOOGLE_BOOKS_API_KEY
```

注意:

- 現フェーズでは Google Books API をフロントエンドから直接呼ぶため、Google Books API key は `bookshelf_app/frontend/.env` に `VITE_GOOGLE_BOOKS_API_KEY` として置く。
- Vite は `VITE_` prefix の環境変数だけをブラウザ側へ公開する。ルート `.env` の `GOOGLE_BOOKS_API_KEY` はバックエンド用の名前として扱い、フロントではそのまま読めない。
- `VITE_` 付きの key はビルド成果物に含まれるため、Google Cloud 側で Books API のみに制限し、localhost/本番ドメインなどの HTTP referrer 制限を設定する。

## Runbook

Backend:

```bash
uvicorn bookshelf_app.main:app --reload --host 0.0.0.0 --port 8000
```

または:

```bash
python -m bookshelf_app.main
```

Frontend:

```bash
cd bookshelf_app/frontend
nodebrew use v22.13.1
npm install
npm run dev
```

Frontend build:

```bash
cd bookshelf_app/frontend
nodebrew use v22.13.1
npm run build
```

FastAPI は `bookshelf_app/frontend/dist` を SPA として mount するため、本番配信前は frontend build が必要です。

注意:

- Node.js は nodebrew 管理。`/usr/local/bin/node` が古い場合があるため、frontend の `npm run build` や `npm run lint` 前に `nodebrew use v22.13.1` を実行する。
- `node -v` が `v22.13.1` であることを確認してからフロントエンド作業を進める。

Migration:

```bash
alembic upgrade head
```

Seed:

```bash
python bookshelf_app/tools/seeds/test_data.py
```

## Tests

Unit tests:

```bash
pytest tests/unit
```

Integration tests:

```bash
pytest tests/integration
```

統合テストは `tests/integration/conftest.py` で `test_env/docker-compose-integration.yml` を使い、PostgreSQL 起動後に Alembic migration を head まで適用します。

テスト用アカウント:

- admin: `hoge@hoge.com` / `Hoge123456789`
- user: `user@user.com` / `ABCabc12345`

注意:

- `.env.test` が必要。
- Docker が必要。
- DB truncate helper は `TRUNCATE ... CASCADE` を使うため PostgreSQL 前提。

## Common Change Recipes

### 新しいAPIを追加する

1. `api/<feature>/domain.py` にドメインルールや interface を追加。
2. `api/<feature>/service.py` に app model と use case を追加。
3. `infra/db/<feature>.py` に repository/query service を実装。
4. `infra/dependencies.py` に service factory を追加。
5. `api/<feature>/router.py` に Pydantic request/response と route を追加。
6. `main.py` で router を include。
7. フロントが使うなら `frontend/src/libs/apis` と `frontend/src/types` を更新。
8. 単体テストと統合テストを追加。

### DBカラムを追加する

1. 対象 DTO にカラムを追加。
2. domain/app model/response model に必要な変換を追加。
3. Alembic revision を追加。
4. 既存データの nullable/default/backfill を migration で考慮。
5. 統合テストで round trip を確認。

### 認証付きフロントAPIを追加する

1. `src/libs/apis/*.ts` に API client method を追加。
2. 呼び出す component/container/hook で API instance を作る。
3. `useAuthApi(api)` を使い、bearer token と 401/403 処理を有効にする。
4. snake_case/camelCase 変換を API client 内に閉じる。

## Known Issues / Watch Points

- `README.md` は概要のみで、実行手順はこのファイルの方が詳しい。
- Python 依存関係ファイルがリポジトリ直下に見当たらない。環境再構築時は実行環境の依存管理方法を別途確認する。
- `pytest.ini` に `[tool.pytest.ini_options]` と `[pytest]` が混在している。pytest-env の設定が期待通り効くか要確認。
- `BookWithReviewLatestInputAppModel.__post_init__` がクラス外にあり、検証として機能していない可能性が高い。
- latest 系クエリは名前に反して昇順の可能性がある。
- review update の所有者チェックは明示されていない。
- OAuth2 docs の token URL が実ルートとずれている。
- フロントの Vite proxy は実 API prefix とずれている。
- API response の tag key は `tag_id` と `id` の混在に注意。

## High-Value Files To Read First

変更前に迷ったら、まずこの順で読むと早いです。

1. `bookshelf_app/main.py`
2. `bookshelf_app/infra/dependencies.py`
3. 対象機能の `api/<feature>/domain.py`
4. 対象機能の `api/<feature>/service.py`
5. 対象機能の `api/<feature>/router.py`
6. 対象機能の `infra/db/*.py`
7. 関連する `tests/unit` または `tests/integration`
8. フロント影響がある場合は `bookshelf_app/frontend/src/libs/apis/*.ts` と `src/types/data.ts`
