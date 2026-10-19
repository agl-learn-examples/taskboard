import jwt

from conftest import signup


def test_login_gives_a_token_pair(client):
    signup(client, "BlueLeaf Studio", "priya@blueleaf.example")
    r = client.post("/auth/login", json={"email": "priya@blueleaf.example", "password": "test-password-1"})
    body = r.get_json()
    assert r.status_code == 200
    assert body["token_type"] == "Bearer" and body["expires_in"] == 15 * 60
    claims = jwt.decode(body["access_token"], options={"verify_signature": False})   # anyone can read a JWT
    assert claims["tid"] == 1 and claims["role"] == "owner" and claims["type"] == "access"


def test_wrong_password(client):
    signup(client, "BlueLeaf Studio", "priya@blueleaf.example")
    r = client.post("/auth/login", json={"email": "priya@blueleaf.example", "password": "nope-nope"})
    assert r.status_code == 401
    assert r.get_json() == {"error": "wrong email or password"}


def test_no_token(client):
    assert client.get("/tasks").status_code == 401


def test_tampered_token(client, tenant):
    token = tenant["Authorization"].split()[1]
    header, payload, sig = token.split(".")
    forged = f"{header}.{payload}.{sig[:-4]}AAAA"
    assert client.get("/tasks", headers={"Authorization": f"Bearer {forged}"}).status_code == 401


def test_token_signed_with_another_key(client, tenant):
    forged = jwt.encode({"sub": "1", "tid": 1, "role": "owner", "type": "access", "jti": "x", "exp": 9999999999},
                        "a-guessed-key-that-is-long-enough", algorithm="HS256")
    r = client.get("/tasks", headers={"Authorization": f"Bearer {forged}"})
    assert r.get_json() == {"error": "invalid token"}


def test_expired_token(app, client, tenant):
    app.config["ACCESS_TOKEN_MINUTES"] = -1
    r = client.post("/auth/login", json={"email": "priya@blueleaf.example", "password": "test-password-1"})
    old = {"Authorization": "Bearer " + r.get_json()["access_token"]}
    r = client.get("/tasks", headers=old)
    assert r.status_code == 401
    assert r.get_json() == {"error": "token expired"}


def test_refresh_gives_a_new_access_token(client):
    signup(client, "BlueLeaf Studio", "priya@blueleaf.example")
    pair = client.post("/auth/login", json={"email": "priya@blueleaf.example", "password": "test-password-1"}).get_json()
    r = client.post("/auth/refresh", json={"refresh_token": pair["refresh_token"]})
    assert r.status_code == 200
    assert client.get("/tasks", headers={"Authorization": "Bearer " + r.get_json()["access_token"]}).status_code == 200


def test_access_token_is_not_a_refresh_token(client, tenant):
    r = client.post("/auth/refresh", json={"refresh_token": tenant["Authorization"].split()[1]})
    assert r.status_code == 401


def test_verify_for_the_gateway(client, tenant):
    r = client.get("/auth/verify", headers=tenant)
    assert r.status_code == 204
    assert r.headers["X-Tenant-Id"] == "1"
    assert client.get("/auth/verify").status_code == 401


def test_me(client, tenant):
    assert client.get("/auth/me", headers=tenant).get_json()["user"]["email"] == "priya@blueleaf.example"


def pair_for(client, email="priya@blueleaf.example"):
    return client.post("/auth/login", json={"email": email, "password": "test-password-1"}).get_json()


def test_refresh_token_works_once(client, tenant):
    pair = pair_for(client)
    assert client.post("/auth/refresh", json={"refresh_token": pair["refresh_token"]}).status_code == 200
    r = client.post("/auth/refresh", json={"refresh_token": pair["refresh_token"]})
    assert r.status_code == 401


def test_logout(client, tenant):
    pair = pair_for(client)
    h = {"Authorization": "Bearer " + pair["access_token"]}
    assert client.post("/auth/logout", json={"refresh_token": pair["refresh_token"]}, headers=h).status_code == 204
    assert client.get("/tasks", headers=h).get_json() == {"error": "logged out"}
    assert client.get("/auth/verify", headers=h).status_code == 401
    assert client.post("/auth/refresh", json={"refresh_token": pair["refresh_token"]}).status_code == 401
