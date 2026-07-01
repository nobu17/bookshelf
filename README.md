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
オライリー・ジャパンと技術評論社の公式カタログは最大1,000件をキャッシュし、画面では新着順に40件ずつページ表示します。
技術評論社は「プログラミング・システム開発」と「ネットワーク・UNIX・データベース」の2ジャンルを1つのカタログとして扱います。
タイトルで絞り込んだ場合は、絞り込み後の総件数を基準にページ分割します。

| Table | TTL | 内容 |
| --- | --- | --- |
| `publisher_catalog_cache` | 3日 | 出版社公式カタログ/APIから取得した ISBN、タイトル、発行日、価格、URL。 |
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

技術評論社だけ再取得したい場合:

```bash
ENV_FILE=.env.local PYTHONPATH=. ./venv_webapp/bin/python -m bookshelf_app.tools.cache.book_search --catalog --source-key gihyo_catalog
```

管理者ユーザーは、マイページの `管理` から `デバッグ` 画面を開き、`publisher_catalog_cache` と `book_metadata_cache` を個別に削除できます。対応APIは管理者権限を必須にしています。

### Metadata Cache Warmup

`.github/workflows/warm-book-metadata-cache.yml` は毎週日曜 03:17（JST）に起動します。
オライリー・ジャパンと技術評論社のカタログ全件から、次の書籍だけを40件ずつ補完します。

- `book_metadata_cache` に未登録
- `fetched_at` から14日以上経過
- 書影が未取得

openBDを先に一括照会し、書影が不足するISBNだけGoogle Booksで補完します。
処理結果はバッチごとに保存するため、途中で失敗した場合も次回は未完了分を中心に再実行されます。
workflowには既存のAzure OIDC設定、`AZURE_RESOURCE_GROUP`、`AZURE_SQL_SERVER_NAME`、`DB_CONNECTION`に加えて、GitHub Environment `production` のSecretとして `GOOGLE_BOOKS_API_KEY` が必要です。

ローカルから手動実行する場合:

```bash
ENV_FILE=.env.local PYTHONPATH=. ./venv_webapp/bin/python \
  -m bookshelf_app.tools.cache.warm_book_metadata
```

更新間隔やバッチサイズは `--refresh-after-days`、`--batch-size` で変更できます。

## Azure App Service Deployment

Azure へ載せる最初の構成は次を想定します。

- Azure App Service: Linux / Python 3.12
- Azure SQL Database
- GitHub Actions: frontend build、unit test、App Service deploy

Azure App Service の Startup Command:

```bash
bash startup.sh
```

`startup.sh` はGunicornのworker timeoutを既定120秒で起動します。
必要な場合はApp Serviceの環境変数 `GUNICORN_TIMEOUT` で秒数を変更できます。
DBアクセスを行うFastAPIルートは同期関数として定義し、FastAPIのスレッドプール上で実行します。
これによりAzure SQLの再開待ち中もUvicorn workerのイベントループをブロックしません。
一時的なDBエラーの再試行ログには、Azure SQLのエラーコード、各試行時間、累積時間を出力します。

App Service の Application settings には次を設定します。

```text
CRYPT_SECRET_KEY=<your secret>
CRYPT_ALGORITHM=HS256
DB_CONNECTION=mssql+pymssql://<user>:<password>@<server>.database.windows.net:1433/<database>
GOOGLE_BOOKS_API_KEY=<optional>
SCM_DO_BUILD_DURING_DEPLOYMENT=1
```

Frontend の API root は Vite のビルド時に決まります。未指定時は同一ドメインの `/api` を使います。別APIホストへ向ける場合だけ、GitHub Actions の build 時に `VITE_APP_API_ROOT` を設定してください。App Service の Application settings に後から `VITE_APP_API_ROOT` を足しても、既にビルド済みの静的ファイルには反映されません。

軽量なヘルスチェックとして `GET /api/health`、DB接続確認として `GET /api/health/db` を提供します。フロントエンドは起動時にDB接続確認を一度だけ行い、Azure SQLの再開を待ってから認証確認と各APIの読み込みを開始します。待機中は前回取得したホーム画面の書籍をブラウザのローカルストレージから読み取り専用で表示します。

GitHub Actions の `Wake Database` workflow は手動実行専用です。定期的なKeep WarmはAzure SQL無料枠のvCore秒を消費し、GitHub Actionsのスケジュール遅延もあるため使用しません。必要なときはActions画面から `Run workflow` を実行すると、`GET /api/health/db` によりApp ServiceとAzure SQLを事前に起動できます。

GitHub Actions には次を設定します。

- Repository variable: `AZURE_WEBAPP_NAME`
- Repository variable: `AZURE_WEBAPP_URL`
- Repository variable: `AZURE_RESOURCE_GROUP`
- Repository variable: `AZURE_SQL_SERVER_NAME`
- Repository secret: `AZURE_CLIENT_ID`
- Repository secret: `AZURE_TENANT_ID`
- Repository secret: `AZURE_SUBSCRIPTION_ID`
- Repository secret: `DB_CONNECTION`

GitHub Actions から Azure への認証は OIDC を使います。Azure 側で Microsoft Entra application / service principal を作成し、App Service のある Resource Group へ `Contributor` 以上のロールを付与します。その後、Federated credential を追加します。

Federated credential の設定値:

```text
Issuer: https://token.actions.githubusercontent.com
Subject: repo:<github-owner>/<github-repo>:environment:production
Audience: api://AzureADTokenExchange
```

GitHub Actions の deploy / migrate job は `environment: production` を使うため、Subject も `environment:production` にします。`AZURE_CLIENT_ID` は作成した application の Client ID、`AZURE_TENANT_ID` は Directory tenant ID、`AZURE_SUBSCRIPTION_ID` は Subscription ID を登録します。Publish Profile は使わないため、`AZURE_WEBAPP_PUBLISH_PROFILE` は不要です。

DB migration は GitHub Actions の `migrate` job で自動実行します。`migrate` job は GitHub-hosted runner の Public IP を Azure SQL firewall に一時追加し、`alembic upgrade head` を実行した後、firewall rule を削除します。migration が失敗した場合、App Service deploy は実行されません。

Azure SQL Server の `Public network access` は `Selected networks` にし、GitHub Actions 実行時の一時IP許可に任せます。ローカルから手動で migration したい場合だけ、自分のPublic IPをAzure SQL firewallに追加してください。

手動で migration を実行する場合:

```bash
DB_CONNECTION='mssql+pymssql://<user>:<password>@<server>.database.windows.net:1433/<database>' \
CRYPT_SECRET_KEY='<your secret>' \
CRYPT_ALGORITHM='HS256' \
alembic upgrade head
```

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
