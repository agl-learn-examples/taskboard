from flask import Blueprint

from ..errors import ApiError
from ..extensions import db
from ..models import PLAN_MEMBER_LIMIT, User
from ..tenancy import current_tenant, writable_tenant
from ..security import hash_password
from ..validation import MemberIn, parse

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
