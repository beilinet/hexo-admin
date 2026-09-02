#!/usr/bin/env bash
set -euo pipefail

uv pip install --system -r requirements.txt
python3 manage.py makemigrations
python3 manage.py migrate
