import httpx

from conftest import PASSWORD, login, new_owner


def test_health_through_the_gateway(anon):
    r = anon.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
    assert r.headers["X-Request-ID"]                 # the gateway tags every request


def test_no_token_stopped_at_the_gateway(anon):
    r = anon.get("/tasks")
    assert r.status_code == 401
    assert r.headers["Content-Type"] == "application/json"
    assert r.json() == {"error": "log in first: send Authorization: Bearer <access token>"}


def test_bad_token(anon):
    r = anon.get("/tasks", headers={"Authorization": "Bearer not.a.token"})
    assert r.status_code == 401
    assert r.json() == {"error": "invalid token"}


def test_wrong_password(anon, owner):
    me = owner.get("/auth/me").json()["user"]
    r = anon.post("/auth/login", json={"email": me["email"], "password": "wrong-password"})
    assert r.status_code == 401
    assert r.json() == {"error": "wrong email or password"}


def test_refresh_then_logout(base_url):
    client, email = new_owner(base_url)
    tokens = login(client, email)
    r = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert r.status_code == 200
    fresh = r.json()
    client.headers["Authorization"] = f"Bearer {fresh['access_token']}"
    assert client.get("/tasks").status_code == 200
    assert client.post("/auth/logout", json={"refresh_token": fresh["refresh_token"]}).status_code == 204
    r = client.get("/tasks")
    assert r.status_code == 401 and r.json() == {"error": "logged out"}
    assert httpx.post(f"{base_url}/auth/refresh", json={"refresh_token": fresh["refresh_token"]}).status_code == 401
    client.close()


def test_member_role(owner):
    r = owner.post("/tenants/me/members", json={"email": f"m-{id(owner)}@test.example", "name": "M",
                                                "password": PASSWORD})
    assert r.status_code == 201
    member = httpx.Client(base_url=str(owner.base_url), timeout=10)
    with member:
        login(member, r.json()["email"])
        assert member.post("/tasks", json={"title": "allowed"}).status_code == 201
        r = member.put("/tenants/me/plan", json={"plan": "team"})
        assert r.status_code == 403 and r.json()["code"] == "forbidden"
