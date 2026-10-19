from conftest import signup


def test_signup_makes_a_free_tenant_and_its_owner(client):
    r = client.post("/auth/signup", json={"tenant_name": "Sharma Traders", "name": "Ravi",
                                          "email": "Ravi@Sharma.example", "password": "test-password-1"})
    assert r.status_code == 201
    body = r.get_json()
    assert body["tenant"]["plan"] == "free"
    assert body["user"] == {"id": 1, "email": "ravi@sharma.example", "name": "Ravi", "role": "owner"}


def test_password_is_stored_hashed(app, client):
    from taskboard.extensions import db
    from taskboard.models import User
    signup(client, "Sharma Traders", "ravi@sharma.example")
    stored = db.session.get(User, 1).password_hash
    assert "test-password-1" not in stored
    assert stored.startswith("$2b$")          # a bcrypt hash


def test_short_password_rejected(client):
    r = client.post("/auth/signup", json={"tenant_name": "T", "name": "N", "email": "n@t.example", "password": "short"})
    assert r.status_code == 400


def test_free_plan_allows_three_members(client):
    h = signup(client, "Sharma Traders", "ravi@sharma.example")          # the owner is member 1
    for n in range(2):
        assert client.post("/tenants/me/members", json={"email": f"m{n}@sharma.example", "name": f"M{n}",
                                                        "password": "test-password-1"}, headers=h).status_code == 201
    r = client.post("/tenants/me/members", json={"email": "m4@sharma.example", "name": "M4",
                                                 "password": "test-password-1"}, headers=h)
    assert r.status_code == 403
    assert r.get_json()["code"] == "upgrade_required"


def test_inactive_tenant_is_read_only(app, client, tenant):
    from taskboard.extensions import db
    from taskboard.models import Tenant
    db.session.get(Tenant, 1).active = False
    db.session.commit()
    from taskboard.cache import forget_tenant
    forget_tenant(1)
    assert client.get("/tasks", headers=tenant).status_code == 200
    assert client.post("/tasks", json={"title": "x"}, headers=tenant).status_code == 403
