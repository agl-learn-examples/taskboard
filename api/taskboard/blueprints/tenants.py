from flask import Blueprint

from .. import cache
from ..errors import ApiError
from ..extensions import db
from ..models import PLAN_MEMBER_LIMIT, User
from ..security import hash_password
from ..tenancy import current_tenant, require_role, writable_tenant
from ..validation import MemberIn, PlanIn, parse

bp = Blueprint("tenants", __name__, url_prefix="/tenants")


@bp.get("/me")
def me():
    return current_tenant().to_dict()


@bp.get("/me/members")
def list_members():
    tenant = current_tenant()
    return [u.to_dict() for u in db.session.scalars(db.select(User).filter_by(tenant_id=tenant.id).order_by(User.id))]


@bp.post("/me/members")
def add_member():
    """admins and owners add members; the plan decides how many"""
    require_role("admin")
    tenant = writable_tenant()
    data = parse(MemberIn)
    limit = PLAN_MEMBER_LIMIT[tenant.plan]
    count = db.session.scalar(db.select(db.func.count(User.id)).filter_by(tenant_id=tenant.id))
    if limit is not None and count >= limit:
        raise ApiError(403, f"the {tenant.plan.title()} plan allows up to {limit} members: upgrade to Team",
                       code="upgrade_required")
    if db.session.scalar(db.select(User).filter_by(email=data.email.lower())):
        raise ApiError(409, "a user with this email already exists")
    user = User(tenant_id=tenant.id, email=data.email.lower(), name=data.name,
                password_hash=hash_password(data.password), role=data.role)
    db.session.add(user)
    db.session.commit()
    return user.to_dict(), 201


@bp.delete("/me/members/<int:user_id>")
def remove_member(user_id):
    me = require_role("admin")
    tenant = writable_tenant()
    user = db.session.scalar(db.select(User).filter_by(id=user_id, tenant_id=tenant.id))
    if user is None:
        raise ApiError(404, "not found")
    if user.role == "owner":
        raise ApiError(403, "the owner cannot be removed", code="forbidden")
    if user.id == me.id:
        raise ApiError(400, "you cannot remove yourself")
    db.session.delete(user)
    db.session.commit()
    return "", 204


@bp.put("/me/plan")
def change_plan():
    """Only the owner changes the plan. (A real app would take a payment here first.)"""
    require_role("owner")
    tenant = current_tenant()
    data = parse(PlanIn)
    count = db.session.scalar(db.select(db.func.count(User.id)).filter_by(tenant_id=tenant.id))
    limit = PLAN_MEMBER_LIMIT[data.plan]
    if limit is not None and count > limit:
        raise ApiError(409, f"the {data.plan.title()} plan allows up to {limit} members; you have {count}")
    tenant.plan = data.plan
    db.session.commit()
    cache.forget_tenant(tenant.id)
    return tenant.to_dict()
