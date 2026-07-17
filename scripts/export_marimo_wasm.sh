#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="${ROOT}/build/marimo-wasm"

mkdir -p "${OUTPUT_DIR}"

UV_CACHE_DIR="${UV_CACHE_DIR:-/private/tmp/aipassport-uv-cache}" \
UV_TOOL_DIR="${UV_TOOL_DIR:-/private/tmp/aipassport-uv-tools}" \
UV_PYTHON_INSTALL_DIR="${UV_PYTHON_INSTALL_DIR:-/private/tmp/aipassport-uv-python}" \
uvx marimo==0.17.8 export html-wasm \
  "${ROOT}/marimo_notebooks/ai_passport.py" \
  --output "${OUTPUT_DIR}/index.html" \
  --mode run \
  --no-show-code \
  --force

echo "Exported ${OUTPUT_DIR}/index.html"
echo "Serve with: python3 -m http.server 8000 --directory ${OUTPUT_DIR}"
