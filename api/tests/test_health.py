def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json() == {"status": "ok"}


def test_unknown_url_is_json(client):
    r = client.get("/nope")
    assert r.status_code == 404
    assert r.get_json() == {"error": "not found"}


def test_health_when_the_database_is_down(client, monkeypatch):
    from sqlalchemy.exc import OperationalError

    from taskboard.extensions import db

    def broken(*args, **kwargs):
        raise OperationalError("SELECT 1", {}, Exception("connection refused"))

    monkeypatch.setattr(db.session, "execute", broken)        # pretend Postgres stopped
    r = client.get("/health")
    assert r.status_code == 503
    assert r.get_json() == {"status": "error", "database": "down"}
