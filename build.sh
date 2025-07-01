#!/usr/bin/env bashAdd commentMore actions


set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --noinput

python manage.py migrateAdd comment