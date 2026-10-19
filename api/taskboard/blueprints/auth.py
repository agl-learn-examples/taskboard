from flask import Blueprint

from ..errors import ApiError
from ..extensions import db
from ..models import Tenant, User
from ..security import hash_password
from ..validation import SignupIn, parse

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.post("/signup")
def signup():
    """A new customer signs up: one tenant on the Free plan, and its owner."""
    data = parse(SignupIn)
    if db.session.scalar(db.select(User).filter_by(email=data.email.lower())):
        raise ApiError(409, "a user with this email already exists")
    tenant = Tenant(name=data.tenant_name, plan="free")
    db.session.add(tenant)
    db.session.flush()                         # gives tenant.id
    user = User(tenant_id=tenant.id, email=data.email.lower(), name=data.name,
                password_hash=hash_password(data.password), role="owner")
    db.session.add(user)
    db.session.commit()
    return {"tenant": tenant.to_dict(), "user": user.to_dict()}, 201
