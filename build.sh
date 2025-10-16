#!/usr/bin/env bash
set -euo pipefail

echo "[build] Installing dependencies..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "[build] Running migrations..."
python manage.py migrate --no-input

echo "[build] Collecting static files..."
python manage.py collectstatic --no-input

echo "[build] Build completed."
