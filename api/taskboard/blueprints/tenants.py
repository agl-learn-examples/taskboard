from flask import Blueprint, request

from ..errors import ApiError
from ..extensions import db
from ..models import PLAN_MEMBER_LIMIT, PLANS, Tenant, User
from ..tenancy import current_tenant, writable_tenant

bp = Blueprint("tenants", __name__, url_prefix="/tenants")


@bp.post("")
def create_tenant():
    data = request.get_json(silent=True) or {}
    if not data.get("name"):
        raise ApiError(400, "name is required")
    tenant = Tenant(name=data["name"], plan=data.get("plan", "free"))
    if tenant.plan not in PLANS:
        raise ApiError(400, "plan must be free or team")
    db.session.add(tenant)
    db.session.commit()
    return tenant.to_dict(), 201


@bp.get("/me")
def me():
    return current_tenant().to_dict()


@bp.get("/me/members")
def list_members():
    tenant = current_tenant()
    return [u.to_dict() for u in db.session.scalars(db.select(User).filter_by(tenant_id=tenant.id).order_by(User.id))]


@bp.post("/me/members")
def add_member():
    tenant = writable_tenant()
    data = request.get_json(silent=True) or {}
    if not data.get("email") or not data.get("name"):
        raise ApiError(400, "email and name are required")
    limit = PLAN_MEMBER_LIMIT[tenant.plan]
    count = db.session.scalar(db.select(db.func.count(User.id)).filter_by(tenant_id=tenant.id))
    if limit is not None and count >= limit:
        raise ApiError(403, f"the {tenant.plan.title()} plan allows up to {limit} members: upgrade to Team",
                       code="upgrade_required")
    user = User(tenant_id=tenant.id, email=data["email"].lower(), name=data["name"])
    db.session.add(user)
    db.session.commit()
    return user.to_dict(), 201
