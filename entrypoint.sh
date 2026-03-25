#!/bin/sh
uv run python manage.py migrate --noinput
uv run python manage.py import_countries
exec uv run gunicorn coinsdb.wsgi:application --bind 0.0.0.0:8000
