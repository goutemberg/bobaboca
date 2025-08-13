#!/bin/sh

python manage.py migrate --noinput
gunicorn bocaboca.wsgi:application --bind 0.0.0.0:${PORT}