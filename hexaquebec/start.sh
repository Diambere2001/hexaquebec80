#!/bin/bash
# Définit le fichier de configuration Django
export DJANGO_SETTINGS_MODULE=hexaquebec.settings
export PYTHONUNBUFFERED=1

# Collecte les fichiers statiques
python manage.py collectstatic --noinput

# Applique les migrations de la base de données
python manage.py migrate

# Démarre le serveur Gunicorn
gunicorn hexaquebec.wsgi:application --bind 0.0.0.0:$PORT
