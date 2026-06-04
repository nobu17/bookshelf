#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "[down] stopping development DB container..."
(cd "${ROOT_DIR}/test_env" && docker compose down)
echo "[down] done."
