#!/bin/bash
export DJANGO_SETTINGS_MODULE=hexaquebec.settings
python manage.py collectstatic --noinput
python manage.py migrate
gunicorn hexaquebec.wsgi:application --bind 0.0.0.0:$PORT

