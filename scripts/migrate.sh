#!/usr/bin/env sh
set -e
/venv/bin/python manage.py migrate --noinput
gunicorn bocaboca.wsgi:application --bind 0.0.0.0:${PORT}