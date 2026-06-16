#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

export ENV_FILE="${ENV_FILE:-.env.test.mssql}"
export INTEGRATION_DOCKER_COMPOSE_FILE="${INTEGRATION_DOCKER_COMPOSE_FILE:-test_env/docker-compose-sqlserver-integration.yml}"
export INTEGRATION_DOCKER_COMPOSE_PROJECT_NAME="${INTEGRATION_DOCKER_COMPOSE_PROJECT_NAME:-pytest-integration-sqlserver}"
export PYTHONPATH="${PYTHONPATH:-.}"

cd "${ROOT_DIR}"
./venv_webapp/bin/python -c "import pymssql" >/dev/null 2>&1 || {
  echo "[sqlserver-test] pymssql is required. Install it with: ./venv_webapp/bin/pip install pymssql" >&2
  exit 1
}

./venv_webapp/bin/pytest -q tests/integration "$@"
