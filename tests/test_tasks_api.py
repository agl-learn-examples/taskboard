from pydantic import BaseModel, ConfigDict


class TaskOut(BaseModel):
    """The contract: exactly what a task looks like in every answer. A new or missing field fails the test,
    because the web and phone apps depend on this shape."""
    model_config = ConfigDict(extra="forbid", strict=True)
    id: int
    title: str
    done: bool
    priority: str
    board_id: int | None


class PageOut(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    items: list[TaskOut]
    page: int
    per_page: int
    total: int


def test_create_read_update_delete(owner):
    r = owner.post("/tasks", json={"title": "Write notes", "priority": "high"})
    assert r.status_code == 201
    task = TaskOut.model_validate(r.json())
    assert r.headers["Location"] == f"/tasks/{task.id}"

    assert owner.get(f"/tasks/{task.id}").json()["title"] == "Write notes"
    assert owner.patch(f"/tasks/{task.id}", json={"done": True}).json()["done"] is True
    assert owner.delete(f"/tasks/{task.id}").status_code == 204
    assert owner.get(f"/tasks/{task.id}").status_code == 404


def test_list_page_contract(owner):
    for title in ("b", "a", "c"):
        owner.post("/tasks", json={"title": title})
    page = PageOut.model_validate(owner.get("/tasks", params={"sort": "title", "per_page": 2}).json())
    assert [t.title for t in page.items] == ["a", "b"]
    assert page.total == 3


def test_validation_errors_name_the_field(owner):
    r = owner.post("/tasks", json={"title": "", "priority": "urgent"})
    assert r.status_code == 400
    assert {d["field"] for d in r.json()["details"]} == {"title", "priority"}


def test_tenants_cannot_see_each_other(owner, other_owner):
    task = owner.post("/tasks", json={"title": "secret plan"}).json()
    r = other_owner.get(f"/tasks/{task['id']}")
    assert r.status_code == 404                     # 404, not 403: nobody learns the task exists
    assert other_owner.get("/tasks").json()["total"] == 0
    assert other_owner.delete(f"/tasks/{task['id']}").status_code == 404
    assert owner.get(f"/tasks/{task['id']}").status_code == 200


def test_free_plan_member_limit(owner):
    for n in range(2):                              # the owner is member 1
        assert owner.post("/tenants/me/members", json={"email": f"m{n}-{id(owner)}@test.example", "name": "M",
                                                       "password": "test-password-1"}).status_code == 201
    r = owner.post("/tenants/me/members", json={"email": f"m9-{id(owner)}@test.example", "name": "M",
                                                "password": "test-password-1"})
    assert r.status_code == 403
    assert r.json()["code"] == "upgrade_required"
