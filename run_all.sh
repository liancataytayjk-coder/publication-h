#!/usr/bin/env bash
# Rebuild everything from data/raw/. Add --download to refresh raw files first.
set -euo pipefail
cd "$(dirname "$0")"
PY=.venv/bin/python
if [[ "${1:-}" == "--download" ]]; then $PY scripts/01_download.py --force; fi
$PY -m pytest -q tests/
$PY scripts/02_build_panel.py
$PY scripts/03_data_checks.py
$PY scripts/04_replicate.py
