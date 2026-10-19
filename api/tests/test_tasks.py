from conftest import signup


def test_create_and_get(client, tenant):
    r = client.post("/tasks", json={"title": "Write notes"}, headers=tenant)
    assert r.status_code == 201
    assert r.headers["Location"] == "/tasks/1"
    assert client.get("/tasks/1", headers=tenant).get_json() == {
        "id": 1, "title": "Write notes", "done": False, "priority": "normal", "board_id": None}


def test_needs_a_tenant(client):
    r = client.get("/tasks")
    assert r.status_code == 401


def test_title_required(client, tenant):
    r = client.post("/tasks", json={"priority": "high"}, headers=tenant)
    assert r.status_code == 400
    assert r.get_json()["details"] == [{"field": "title", "message": "Field required"}]


def test_unknown_field_rejected(client, tenant):
    r = client.post("/tasks", json={"title": "x", "colour": "red"}, headers=tenant)
    assert r.status_code == 400


def test_patch_changes_only_what_is_sent(client, tenant):
    client.post("/tasks", json={"title": "Pick fonts", "priority": "high"}, headers=tenant)
    r = client.patch("/tasks/1", json={"done": True}, headers=tenant)
    assert r.get_json()["done"] is True
    assert r.get_json()["priority"] == "high"


def test_delete(client, tenant):
    client.post("/tasks", json={"title": "x"}, headers=tenant)
    assert client.delete("/tasks/1", headers=tenant).status_code == 204
    assert client.get("/tasks/1", headers=tenant).status_code == 404


def test_other_tenants_task_is_not_found(client, tenant):
    client.post("/tasks", json={"title": "secret plan"}, headers=tenant)
    other = signup(client, "Sharma Traders", "ravi@sharma.example")
    r = client.get("/tasks/1", headers=other)
    assert r.status_code == 404


def test_filter_sort_and_page(client, tenant):
    for title, prio in [("b", "low"), ("a", "high"), ("c", "normal")]:
        client.post("/tasks", json={"title": title, "priority": prio}, headers=tenant)
    body = client.get("/tasks?sort=-priority&per_page=2", headers=tenant).get_json()
    assert [t["title"] for t in body["items"]] == ["a", "c"]
    assert body["total"] == 3
    body = client.get("/tasks?sort=-priority&per_page=2&page=2", headers=tenant).get_json()
    assert [t["title"] for t in body["items"]] == ["b"]
    assert client.get("/tasks?priority=low", headers=tenant).get_json()["total"] == 1


def test_bad_query(client, tenant):
    assert client.get("/tasks?per_page=500", headers=tenant).status_code == 400
