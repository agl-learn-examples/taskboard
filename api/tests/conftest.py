"""Shared test setup. Each test gets a brand-new app and an empty database (a SQLite file in tmp_path),
so tests never see each other's data."""
import pytest

from taskboard import create_app
from taskboard.extensions import db


@pytest.fixture
def app(tmp_path):
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'test.db'}"})
    with app.app_context():
        db.create_all()          # tests make the tables from the models; Docker uses the migrations
        yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def tenant(client):
    """a fresh tenant; returns the headers that act as it"""
    return signup(client, "BlueLeaf Studio", "priya@blueleaf.example")


def signup(client, tenant_name, email):
    r = client.post("/auth/signup", json={"tenant_name": tenant_name, "name": "Owner", "email": email,
                                          "password": "test-password-1"})
    assert r.status_code == 201, r.get_json()
    return {"X-Tenant-ID": str(r.get_json()["tenant"]["id"])}
