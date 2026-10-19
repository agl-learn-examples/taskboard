#!/bin/sh
# Bring the database schema up to date, then start the web server.
set -e
flask --app wsgi db upgrade
exec gunicorn -b 0.0.0.0:8000 --access-logfile - wsgi:app
