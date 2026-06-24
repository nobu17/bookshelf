#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_PID=""
FRONTEND_PID=""
REQUIRED_NODE_MAJOR=20

cleanup() {
  local exit_code=$?

  if [[ -n "${FRONTEND_PID}" ]] && kill -0 "${FRONTEND_PID}" 2>/dev/null; then
    kill "${FRONTEND_PID}" 2>/dev/null || true
  fi
  if [[ -n "${BACKEND_PID}" ]] && kill -0 "${BACKEND_PID}" 2>/dev/null; then
    kill "${BACKEND_PID}" 2>/dev/null || true
  fi

  wait "${FRONTEND_PID}" 2>/dev/null || true
  wait "${BACKEND_PID}" 2>/dev/null || true

  (cd "${ROOT_DIR}/test_env" && docker compose down)
  exit "${exit_code}"
}

trap cleanup EXIT INT TERM

check_node_version() {
  if ! command -v node >/dev/null 2>&1; then
    echo "[dev] Node.js is not installed or not found in PATH." >&2
    exit 1
  fi

  local node_version
  local node_major
  node_version="$(node -p "process.versions.node")"
  node_major="${node_version%%.*}"
  if (( node_major < REQUIRED_NODE_MAJOR )); then
    echo "[dev] Node.js ${REQUIRED_NODE_MAJOR}+ is required. Current: v${node_version}" >&2
    echo "[dev] If you use nodebrew, run: nodebrew use v22.13.1" >&2
    exit 1
  fi
  echo "[dev] using Node.js v${node_version}"
}

export ENV_FILE="${ENV_FILE:-.env.local}"

if [[ "${ENV_FILE}" == ".env.local" && ! -f "${ROOT_DIR}/.env.local" ]]; then
  echo "[dev] creating .env.local from .env.local.example..."
  cp "${ROOT_DIR}/.env.local.example" "${ROOT_DIR}/.env.local"
fi

if [[ -d "${HOME}/.nodebrew/current/bin" ]]; then
  export PATH="${HOME}/.nodebrew/current/bin:${PATH}"
fi

echo "[dev] starting PostgreSQL container..."
(cd "${ROOT_DIR}/test_env" && docker compose up -d)

echo "[dev] waiting for PostgreSQL..."
for _ in {1..30}; do
  if "${ROOT_DIR}/venv_webapp/bin/python" -c "import socket; socket.create_connection(('127.0.0.1', 17432), 1).close()" 2>/dev/null; then
    break
  fi
  sleep 1
done

echo "[dev] applying database migrations..."
(cd "${ROOT_DIR}" && ./venv_webapp/bin/alembic upgrade head)

echo "[dev] starting backend: http://localhost:8000"
(cd "${ROOT_DIR}" && ./venv_webapp/bin/uvicorn bookshelf_app.main:app --reload --host 0.0.0.0 --port 8000) &
BACKEND_PID=$!

echo "[dev] selecting Node.js v22.13.1 with nodebrew..."
if command -v nodebrew >/dev/null 2>&1; then
  nodebrew use v22.13.1
fi
check_node_version

echo "[dev] starting frontend: http://localhost:5173"
(cd "${ROOT_DIR}/bookshelf_app/frontend" && npm run dev) &
FRONTEND_PID=$!

echo "[dev] ready. Press Ctrl+C to stop backend, frontend, and DB."
while kill -0 "${BACKEND_PID}" 2>/dev/null && kill -0 "${FRONTEND_PID}" 2>/dev/null; do
  sleep 1
done

echo "[dev] backend or frontend stopped. Cleaning up..."
exit 1
