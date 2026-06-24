# Bookshelf

技術書ノート用の Web アプリケーションです。書籍マスタ、タグ、読書レビューを管理できます。

## Stack

- Backend: FastAPI, SQLAlchemy, Alembic
- Frontend: Vite, React, TypeScript, MUI
- Database: PostgreSQL を基本に、SQL Server でも integration test を実行できる構成
- Tests: pytest, pytest-docker, FastAPI TestClient

## Local Development

Python dependencies:

```bash
. venv_webapp/bin/activate
pip install -r requirements-dev.txt
```

開発用サーバーをまとめて起動します。

```bash
./scripts/dev.sh
```

初回実行時に `.env.local` がなければ `.env.local.example` から自動作成します。`dev.sh` はローカルPostgreSQLコンテナを起動し、migrationを適用してから backend / frontend を起動します。

停止するときは起動したターミナルで `Ctrl+C` を押します。DB コンテナだけ明示的に止めたい場合は次を使います。

```bash
./scripts/down.sh
```

## Environment Files

普段のローカル開発では、基本的に `.env.local` だけを編集します。

| File | Git | 用途 |
| --- | --- | --- |
| `.env.local` | ignored | ローカル開発用。`dev.sh` が `ENV_FILE=.env.local` として読み込みます。Google Books API key もここに入れます。 |
| `.env.local.example` | tracked | `.env.local` の雛形。secret は入れません。 |
| `.env` | ignored | 手動実行や一時検証用。`dev.sh` はデフォルトでは使いません。 |
| `.env.prod` | ignored | 本番相当の手動実行用。必要な場合だけ作ります。 |
| `.env.test` | tracked | PostgreSQL integration / unit test 用。secret は入れません。 |
| `.env.test.mssql` | tracked | SQL Server integration test 用。secret は入れません。 |
| `.env.tool` | ignored | seed/tool のローカル用。 |
| `.env.tool.prod` | ignored | Azure SQL へ初期Adminなどを作る手動tool用。 |
| `.env.tool.example` | tracked | `.env.tool` の雛形。 |
| `.env.tool.prod.example` | tracked | `.env.tool.prod` の雛形。 |
| `bookshelf_app/frontend/.env.development` | tracked | Vite開発サーバー用。API root は `http://localhost:8000/api`。 |
| `bookshelf_app/frontend/.env.production` | tracked | Vite本番ビルド用。GitHub Actionsではworkflow内の値も使います。 |

`.env.local` や `.env.tool.prod` などの ignored ファイルにはsecretを入れて構いませんが、tracked な `*.example` や test 用envにはsecretを入れません。

## Database Migration

DB 接続先は `ENV_FILE` で指定したenvファイルの `DB_CONNECTION` で切り替えます。

```bash
alembic upgrade head
```

Alembic は `bookshelf_app/infra/db/migrations` 配下の migration を使います。

## Book Search Cache

出版社から探す機能では、外部サイト/APIへのアクセスを減らすためにDBキャッシュを使います。

| Table | TTL | 内容 |
| --- | --- | --- |
| `publisher_catalog_cache` | 3日 | 出版社公式カタログから取得した ISBN、タイトル、発行日、価格、URL。現在はオライリー・ジャパンに対応。 |
| `book_metadata_cache` | 30日 | ISBNごとに openBD / Google Books で補完した著者、出版社、出版日、書影URL、概要など。 |

通常の流れは次の通りです。

```text
出版社公式カタログ
  -> publisher_catalog_cache
  -> ISBNで絞り込み・最新順ソート
  -> book_metadata_cache
  -> 足りないISBNだけ openBD / Google Books で補完
```

デバッグ時に ISBN 補完キャッシュだけ削除する場合:

```bash
ENV_FILE=.env.local PYTHONPATH=. ./venv_webapp/bin/python -m bookshelf_app.tools.cache.book_search --metadata
```

特定ISBNだけ削除する場合:

```bash
ENV_FILE=.env.local PYTHONPATH=. ./venv_webapp/bin/python -m bookshelf_app.tools.cache.book_search --metadata --isbn13 9784814401703
```

出版社カタログキャッシュも含めて再取得したい場合:

```bash
ENV_FILE=.env.local PYTHONPATH=. ./venv_webapp/bin/python -m bookshelf_app.tools.cache.book_search --catalog --source-key oreilly_japan_catalog
```

## Azure App Service Deployment

Azure へ載せる最初の構成は次を想定します。

- Azure App Service: Linux / Python 3.12
- Azure SQL Database
- GitHub Actions: frontend build、unit test、App Service deploy

Azure App Service の Startup Command:

```bash
bash startup.sh
```

App Service の Application settings には次を設定します。

```text
CRYPT_SECRET_KEY=<your secret>
CRYPT_ALGORITHM=HS256
DB_CONNECTION=mssql+pymssql://<user>:<password>@<server>.database.windows.net:1433/<database>
GOOGLE_BOOKS_API_KEY=<optional>
SCM_DO_BUILD_DURING_DEPLOYMENT=1
```

Frontend の API root は Vite のビルド時に決まります。未指定時は同一ドメインの `/api` を使います。別APIホストへ向ける場合だけ、GitHub Actions の build 時に `VITE_APP_API_ROOT` を設定してください。App Service の Application settings に後から `VITE_APP_API_ROOT` を足しても、既にビルド済みの静的ファイルには反映されません。

軽量なヘルスチェックとして `GET /api/health` を提供します。GitHub Actions の `Keep Warm` workflow は、無料枠のコールドスタート緩和用に JST 7:00-23:00 の間だけ30分ごとにこのエンドポイントを呼びます。無料枠のCPU制限を消費するため、常時起動の代替として過度に短い間隔では実行しません。

GitHub Actions には次を設定します。

- Repository variable: `AZURE_WEBAPP_NAME`
- Repository variable: `AZURE_WEBAPP_URL`
- Repository secret: `AZURE_CLIENT_ID`
- Repository secret: `AZURE_TENANT_ID`
- Repository secret: `AZURE_SUBSCRIPTION_ID`

GitHub Actions から Azure への認証は OIDC を使います。Azure 側で Microsoft Entra application / service principal を作成し、App Service のある Resource Group へ `Contributor` 以上のロールを付与します。その後、Federated credential を追加します。

Federated credential の設定値:

```text
Issuer: https://token.actions.githubusercontent.com
Subject: repo:<github-owner>/<github-repo>:environment:production
Audience: api://AzureADTokenExchange
```

GitHub Actions の deploy job は `environment: production` を使うため、Subject も `environment:production` にします。`AZURE_CLIENT_ID` は作成した application の Client ID、`AZURE_TENANT_ID` は Directory tenant ID、`AZURE_SUBSCRIPTION_ID` は Subscription ID を登録します。Publish Profile は使わないため、`AZURE_WEBAPP_PUBLISH_PROFILE` は不要です。

初回の DB migration は、デプロイ前にローカルから Azure SQL に対して手動実行するのが安全です。

```bash
DB_CONNECTION='mssql+pymssql://<user>:<password>@<server>.database.windows.net:1433/<database>' \
CRYPT_SECRET_KEY='<your secret>' \
CRYPT_ALGORITHM='HS256' \
alembic upgrade head
```

CI/CD で migration を自動化するのは、接続・バックアップ・失敗時の戻し方が決まってからにします。

### Initial Admin Account

初回ログイン用の Admin は migration では自動作成されません。DB migration 後に、初期Admin作成コマンドを1回実行します。

`.env.tool.prod.example` をコピーして、コード管理しない `.env.tool.prod` を作成します。

```bash
cp .env.tool.prod.example .env.tool.prod
```

`.env.tool.prod` に次を設定します。

```text
TOOL_INITIAL_USER_NAME=<admin name>
TOOL_INITIAL_USER_MAIL=<admin email>
TOOL_INITIAL_USER_PASS=<admin password>
```

Admin password は 8-100 文字で、大文字・小文字・数字を含めてください。

Azure SQL に作成する場合:

```bash
DB_CONNECTION='mssql+pymssql://<user>:<password>@<server>.database.windows.net:1433/<database>' \
CRYPT_SECRET_KEY='<your secret>' \
CRYPT_ALGORITHM='HS256' \
python -m bookshelf_app.tools.seeds.user
```

同じメールアドレスのユーザーが既に存在する場合は新規作成せず、そのユーザーをそのまま使います。

## Tests

PostgreSQL integration test:

```bash
ENV_FILE=.env.test PYTHONPATH=. ./venv_webapp/bin/pytest -q tests/integration
```

SQL Server integration test:

```bash
./scripts/test_integration_sqlserver.sh
```

特定のテストだけ実行する場合:

```bash
./scripts/test_integration_sqlserver.sh tests/integration/test_books.py
```

SQL Server 用テストは `test_env/docker-compose-sqlserver-integration.yml` で SQL Server コンテナを起動し、`.env.test.mssql` の接続文字列を使います。

## SQL Server Compatibility Notes

SQL Server 対応では、次の差分を吸収しています。

- 日本語文字列を保持するため、SQLAlchemy の `Unicode` / `UnicodeText` を使用
- `TRUNCATE ... CASCADE` は PostgreSQL 専用なので、SQL Server では `DELETE` でテストデータを掃除
- SQL Server が受け付けない Boolean SQL を避けるため、`false()` 比較に統一
- `DateTime(timezone=True)` の往復差を避けるため、レビュー日時は保存時に UTC 正規化
- SQL Server で未対応の Alembic comment 変更は migration 内でスキップ

## Dependency Note

依存関係は用途別に分けています。

- `requirements.txt`: アプリ実行用の依存関係。Azure SQL 接続用の `pymssql` と App Service 起動用の `gunicorn` を含みます。
- `requirements-dev.txt`: テスト・開発用の依存関係。`requirements.txt` を含み、`pytest`、`pytest-docker`、`httpx`、types 系を追加します。

PostgreSQL 専用の本番環境に戻す場合は、`pymssql` を SQL Server 用 requirements に分けても構いません。Azure SQL を本番DBにする間は `requirements.txt` に含めておきます。
