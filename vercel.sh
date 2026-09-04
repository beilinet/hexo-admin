#!/bin/bash
set -euo pipefail

# Install dependencies
python3 -m pip install --break-system-packages -r requirements.txt

# Validate committed migrations, then apply them to the selected database.
python3 manage.py check
python3 manage.py migrate --noinput
