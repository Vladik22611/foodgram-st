#!/bin/sh

echo 'Running migrations and collect static...'
python manage.py makemigrations
python manage.py migrate

python manage.py collectstatic --no-input 
sh -c "cp -r /app/collected_static/ /backend_static/static/"

# по умолчанию заполняем таблицу ingredients 
python /app/scripts/load_ingredients.py

gunicorn --bind 0.0.0.0:8000 foodgram_backend.wsgi
exec "$@"