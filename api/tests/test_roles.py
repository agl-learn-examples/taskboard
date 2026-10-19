from conftest import login, signup

MEMBER = {"email": "meera@blueleaf.example", "name": "Meera", "password": "test-password-1"}


def test_member_cannot_add_members(client, tenant):
    client.post("/tenants/me/members", json=MEMBER, headers=tenant)
    meera = login(client, MEMBER["email"])
    r = client.post("/tenants/me/members", json={**MEMBER, "email": "x@blueleaf.example"}, headers=meera)
    assert r.status_code == 403
    assert r.get_json()["code"] == "forbidden"


def test_member_can_work_on_tasks(client, tenant):
    client.post("/tenants/me/members", json=MEMBER, headers=tenant)
    meera = login(client, MEMBER["email"])
    assert client.post("/tasks", json={"title": "Pick fonts"}, headers=meera).status_code == 201


def test_admin_can_add_members_but_not_change_the_plan(client, tenant):
    client.post("/tenants/me/members", json={**MEMBER, "role": "admin"}, headers=tenant)
    admin = login(client, MEMBER["email"])
    assert client.post("/tenants/me/members", json={**MEMBER, "email": "a@blueleaf.example"},
                       headers=admin).status_code == 201
    assert client.put("/tenants/me/plan", json={"plan": "team"}, headers=admin).status_code == 403


def test_owner_upgrades_then_can_add_a_fourth_member(client):
    owner = signup(client, "Sharma Traders", "ravi@sharma.example")
    for n in range(2):
        client.post("/tenants/me/members", json={**MEMBER, "email": f"m{n}@sharma.example"}, headers=owner)
    assert client.post("/tenants/me/members", json={**MEMBER, "email": "m3@sharma.example"},
                       headers=owner).status_code == 403
    assert client.put("/tenants/me/plan", json={"plan": "team"}, headers=owner).get_json()["plan"] == "team"
    assert client.post("/tenants/me/members", json={**MEMBER, "email": "m3@sharma.example"},
                       headers=owner).status_code == 201


def test_cannot_downgrade_with_too_many_members(client, tenant):
    client.put("/tenants/me/plan", json={"plan": "team"}, headers=tenant)
    for n in range(3):
        client.post("/tenants/me/members", json={**MEMBER, "email": f"m{n}@blueleaf.example"}, headers=tenant)
    assert client.put("/tenants/me/plan", json={"plan": "free"}, headers=tenant).status_code == 409


def test_only_admins_delete_boards(client, tenant):
    board = client.post("/boards", json={"name": "Launch"}, headers=tenant).get_json()
    client.post("/tasks", json={"title": "x", "board_id": board["id"]}, headers=tenant)
    client.post("/tenants/me/members", json=MEMBER, headers=tenant)
    meera = login(client, MEMBER["email"])
    assert client.delete(f"/boards/{board['id']}", headers=meera).status_code == 403
    assert client.delete(f"/boards/{board['id']}", headers=tenant).status_code == 204
    assert client.get("/tasks", headers=tenant).get_json()["total"] == 0
