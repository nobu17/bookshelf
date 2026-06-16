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

- `requirements.txt`: アプリ実行用の依存関係
- `requirements-dev.txt`: テスト・開発用の依存関係。`requirements.txt` を含み、`pytest`、`pytest-docker`、`httpx`、SQL Server integration test 用の `pymssql` を追加します。

PostgreSQL で動かす本番環境は `requirements.txt` で足ります。SQL Server を本番DBにする場合は `pymssql` も本番依存に移すか、別途 SQL Server 用 requirements を作るのが安全です。
