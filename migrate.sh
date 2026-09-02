#!/usr/bin/env bash
set -euo pipefail

python3 -m pip install --disable-pip-version-check -r requirements.txt
python3 manage.py makemigrations
python3 manage.py migrate
