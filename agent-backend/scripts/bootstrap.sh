#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

if ! command -v uv >/dev/null 2>&1; then
  echo "错误：未找到 uv。请先安装 uv 后重试。" >&2
  exit 1
fi

uv sync --frozen
mkdir -p data
printf 'XERP Demo 依赖已安装。运行：%s/scripts/run_demo.sh\n' "$PROJECT_DIR"
