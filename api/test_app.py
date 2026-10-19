import pytest
import app as tasks_app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)          # tasks.db is made in a fresh folder for each test
    return tasks_app.app.test_client()


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json() == {"status": "ok"}


def test_get_missing_task(client):
    r = client.get("/tasks/99")
    assert r.status_code == 404
    assert r.get_json() == {"error": "not found"}


def test_create_and_list(client):
    r = client.post("/tasks", json={"title": "learn HTTP"})
    assert r.status_code == 201
    assert client.get("/tasks").get_json() == [{"id": 1, "title": "learn HTTP", "done": False, "priority": "normal"}]


def test_sort_by_title(client):
    for title in ("tag a release", "fetch", "open a PR"):
        client.post("/tasks", json={"title": title})
    assert [t["title"] for t in client.get("/tasks?sort=title").get_json()] == ["fetch", "open a PR", "tag a release"]


def test_title_required(client):
    assert client.post("/tasks", json={}).status_code == 400


def test_filter_by_done(client):
    client.post("/tasks", json={"title": "write tests"})
    client.put("/tasks/1", json={"title": "write tests", "done": True})
    client.post("/tasks", json={"title": "open a PR"})
    assert [t["title"] for t in client.get("/tasks?done=true").get_json()] == ["write tests"]
    assert [t["title"] for t in client.get("/tasks?done=false").get_json()] == ["open a PR"]


def test_priority(client):
    r = client.post("/tasks", json={"title": "ship it", "priority": "high"})
    assert r.status_code == 201
    assert r.get_json()["priority"] == "high"


def test_unknown_priority(client):
    r = client.post("/tasks", json={"title": "ship it", "priority": "urgent"})
    assert r.status_code == 400
