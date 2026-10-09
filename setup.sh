#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if command -v python3.12 >/dev/null 2>&1; then
 python3.12 scripts/setup.py
elif command -v python3.11 >/dev/null 2>&1; then
 python3.11 scripts/setup.py
else
 echo 'Install Python 3.12 or 3.11, including its venv module, then retry.'; exit 1
fi
exec .venv/bin/python scripts/start.py
