"""API tests talk to the RUNNING stack over HTTP, through the gateway, like a real client does.

Start the stack first, with login limits raised so the tests' many sign-ups are not slowed down:

    AUTH_RATE=600r/m AUTH_BURST=100 docker compose up -d --build --wait
    pip install -r tests/requirements.txt
    pytest tests

TASKBOARD_URL changes where they point (default http://localhost:8080/v1).
Each test signs up its OWN new tenant, so tests never share data and can run in any order.
"""
import os
import uuid

import httpx
import pytest

BASE_URL = os.environ.get("TASKBOARD_URL", "http://localhost:8080/v1")
PASSWORD = "test-password-1"          # a fake practice password


@pytest.fixture(scope="session")
def base_url():
    try:
        httpx.get(f"{BASE_URL}/health", timeout=3).raise_for_status()
    except httpx.HTTPError as e:
        pytest.exit(f"TaskBoard is not running at {BASE_URL} ({e}). Start it: docker compose up -d --build --wait", 2)
    return BASE_URL


@pytest.fixture
def anon(base_url):
    """a client with no login"""
    with httpx.Client(base_url=base_url, timeout=10) as client:
        yield client


def new_owner(base_url, tenant_name="Test Tenant"):
    """sign up a brand-new tenant; return a client logged in as its owner, and the owner's email"""
    email = f"owner-{uuid.uuid4().hex[:12]}@test.example"
    client = httpx.Client(base_url=base_url, timeout=10)
    r = client.post("/auth/signup", json={"tenant_name": tenant_name, "name": "Owner", "email": email, "password": PASSWORD})
    assert r.status_code == 201, r.text
    login(client, email)
    return client, email


def login(client, email, password=PASSWORD):
    r = client.post("/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    tokens = r.json()
    client.headers["Authorization"] = f"Bearer {tokens['access_token']}"
    return tokens


@pytest.fixture
def owner(base_url):
    client, _ = new_owner(base_url)
    yield client
    client.close()


@pytest.fixture
def other_owner(base_url):
    client, _ = new_owner(base_url, "Another Tenant")
    yield client
    client.close()
