def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json() == {"status": "ok"}


def test_unknown_url_is_json(client):
    r = client.get("/nope")
    assert r.status_code == 404
    assert r.get_json() == {"error": "not found"}
