"""TaskBoard's API service.

create_app() is an "app factory": it builds a new Flask app each time it is called, so tests can make
their own app with their own settings.
"""
from flask import Flask

from .config import Config
from .extensions import db, migrate


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if config:
        app.config.update(config)
    app.json.sort_keys = False               # keep JSON keys in the order we write them

    db.init_app(app)
    migrate.init_app(app, db)

    from . import errors
    errors.register(app)

    from .blueprints import boards, health, tasks, tenants
    app.register_blueprint(health.bp)
    app.register_blueprint(tenants.bp)
    app.register_blueprint(boards.bp)
    app.register_blueprint(tasks.bp)

    from . import cli
    cli.register(app)
    return app
