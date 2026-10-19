def test_free_plan_allows_three_members(client):
    t = client.post("/tenants", json={"name": "Sharma Traders"}).get_json()
    h = {"X-Tenant-ID": str(t["id"])}
    for n in range(3):
        assert client.post("/tenants/me/members", json={"email": f"m{n}@sharma.example", "name": f"M{n}"},
                           headers=h).status_code == 201
    r = client.post("/tenants/me/members", json={"email": "m4@sharma.example", "name": "M4"}, headers=h)
    assert r.status_code == 403
    assert r.get_json()["code"] == "upgrade_required"


def test_inactive_tenant_is_read_only(app, client, tenant):
    from taskboard.extensions import db
    from taskboard.models import Tenant
    db.session.get(Tenant, int(tenant["X-Tenant-ID"])).active = False
    db.session.commit()
    assert client.get("/tasks", headers=tenant).status_code == 200
    assert client.post("/tasks", json={"title": "x"}, headers=tenant).status_code == 403
