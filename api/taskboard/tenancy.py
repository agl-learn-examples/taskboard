"""Who is asking, and for which tenant?

The answer comes from the access token in the Authorization header, which the server signed at login.
The tenant comes from the token, never from anything else the client sends.
"""
from flask import request

from . import cache
from .errors import ApiError
from .extensions import db
from .models import Tenant, User
from .tokens import decode


def bearer_token():
    scheme, _, token = request.headers.get("Authorization", "").partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise ApiError(401, "log in first: send Authorization: Bearer <access token>")
    return token


def current_user():
    """the logged-in user, worked out once per request"""
    if "taskboard.user" not in request.environ:
        claims = decode(bearer_token(), "access")
        if is_revoked(claims):
            raise ApiError(401, "logged out")
        user = db.session.get(User, int(claims["sub"]))
        if user is None:
            raise ApiError(401, "user no longer exists")
        request.environ["taskboard.user"] = user
        request.environ["taskboard.claims"] = claims
    return request.environ["taskboard.user"]


def is_revoked(claims):
    try:
        return bool(cache.r().exists(f"revoked:{claims['jti']}"))
    except cache.redis.RedisError:
        return False             # Redis down: a logged-out token works until it expires (at most 15 min)


def current_tenant():
    return db.session.get(Tenant, current_user().tenant_id)


def writable_tenant():
    """the tenant, if it may change data: a tenant that stopped paying is read-only"""
    tenant = current_tenant()
    if not cache.tenant_status(tenant)["active"]:
        raise ApiError(403, "subscription inactive: your tasks are read-only")
    return tenant
