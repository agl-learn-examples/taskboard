"""What gunicorn and `flask` load: `gunicorn wsgi:app`, `flask --app wsgi run`."""
from taskboard import create_app

app = create_app()
