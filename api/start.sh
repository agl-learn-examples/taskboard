#!/bin/sh
# Bring the database schema up to date, add the demo data if asked, then start the web server.
set -e
flask --app wsgi db upgrade
if [ "${SEED_DEMO:-0}" = "1" ]; then
    flask --app wsgi seed
fi
exec gunicorn -b 0.0.0.0:8000 --workers 2 --access-logfile - wsgi:app
