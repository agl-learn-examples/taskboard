"""Unit tests: one function at a time. A few need an app for its settings (current_app), but no database."""
import pytest

from taskboard import create_app


@pytest.fixture
def app_ctx():
    app = create_app({"TESTING": True, "BCRYPT_ROUNDS": 4, "SQLALCHEMY_DATABASE_URI": "sqlite://"})
    with app.app_context():
        yield app
