from flask import Blueprint

from ..errors import ApiError
from ..extensions import db
from ..models import Tenant, User
from ..security import check_password, hash_password
from ..tenancy import bearer_token, current_user
from ..tokens import decode, make_access, make_refresh
from ..validation import LoginIn, RefreshIn, SignupIn, parse

bp = Blueprint("auth", __name__, url_prefix="/auth")


def token_pair(user):
    access, claims = make_access(user)
    refresh, _ = make_refresh(user)
    return {"access_token": access, "refresh_token": refresh, "token_type": "Bearer",
            "expires_in": int((claims["exp"] - claims["iat"]).total_seconds())}


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


@bp.post("/login")
def login():
    data = parse(LoginIn)
    user = db.session.scalar(db.select(User).filter_by(email=data.email.lower()))
    if user is None or not check_password(data.password, user.password_hash):
        raise ApiError(401, "wrong email or password")     # never say which one: that would help an attacker
    return token_pair(user)


@bp.post("/refresh")
def refresh():
    claims = decode(parse(RefreshIn).refresh_token, "refresh")
    user = db.session.get(User, int(claims["sub"]))
    if user is None:
        raise ApiError(401, "user no longer exists")
    return token_pair(user)


@bp.get("/me")
def me():
    user = current_user()
    return {"user": user.to_dict(), "tenant": user.tenant.to_dict()}


@bp.get("/verify")
def verify():
    """For the gateway: is this a valid, unexpired access token? 204 yes, 401 no. Checks the signature
    only (no database), so it is fast; it hands who-is-asking on in headers."""
    claims = decode(bearer_token(), "access")
    return "", 204, {"X-User-Id": claims["sub"], "X-Tenant-Id": str(claims["tid"]), "X-Role": claims["role"]}
