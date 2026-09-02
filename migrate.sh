#!/usr/bin/env bash
set -euo pipefail

BUILD_VENV="$(mktemp -d)"
trap 'rm -rf "$BUILD_VENV"' EXIT

uv venv "$BUILD_VENV" --python 3.12
uv pip install --python "$BUILD_VENV/bin/python" -r requirements.txt
"$BUILD_VENV/bin/python" manage.py makemigrations
"$BUILD_VENV/bin/python" manage.py migrate
