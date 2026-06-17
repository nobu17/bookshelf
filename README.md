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

停止するときは起動したターミナルで `Ctrl+C` を押します。DB コンテナだけ明示的に止めたい場合は次を使います。

```bash
./scripts/down.sh
```

## Database Migration

DB 接続先は `.env`、`.env.test`、`.env.test.mssql` などの `DB_CONNECTION` で切り替えます。

```bash
alembic upgrade head
```

Alembic は `bookshelf_app/infra/db/migrations` 配下の migration を使います。

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
