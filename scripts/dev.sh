#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_PID=""
FRONTEND_PID=""

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

export ENV_FILE="${ENV_FILE:-.env}"

if [[ -d "${HOME}/.nodebrew/current/bin" ]]; then
  export PATH="${HOME}/.nodebrew/current/bin:${PATH}"
fi

echo "[dev] starting PostgreSQL container..."
(cd "${ROOT_DIR}/test_env" && docker compose up -d)

echo "[dev] starting backend: http://localhost:8000"
(cd "${ROOT_DIR}" && ./venv_webapp/bin/uvicorn bookshelf_app.main:app --reload --host 0.0.0.0 --port 8000) &
BACKEND_PID=$!

echo "[dev] selecting Node.js v22.13.1 with nodebrew..."
if command -v nodebrew >/dev/null 2>&1; then
  nodebrew use v22.13.1
fi

echo "[dev] starting frontend: http://localhost:5173"
(cd "${ROOT_DIR}/bookshelf_app/frontend" && npm run dev) &
FRONTEND_PID=$!

echo "[dev] ready. Press Ctrl+C to stop backend, frontend, and DB."
while kill -0 "${BACKEND_PID}" 2>/dev/null && kill -0 "${FRONTEND_PID}" 2>/dev/null; do
  sleep 1
done

echo "[dev] backend or frontend stopped. Cleaning up..."
exit 1
