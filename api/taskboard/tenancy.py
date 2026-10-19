"""Which tenant is this request for?

For now the client says so itself, in an X-Tenant-ID header. That is NOT safe: anyone can send any
number. Course A3 replaces it with a login token that the server signs.
"""
from flask import request

from .errors import ApiError
from .extensions import db
from .models import Tenant


def current_tenant():
    raw = request.headers.get("X-Tenant-ID", "")
    if not raw.isdigit():
        raise ApiError(401, "send the X-Tenant-ID header")
    tenant = db.session.get(Tenant, int(raw))
    if tenant is None:
        raise ApiError(401, "unknown tenant")
    return tenant


def writable_tenant():
    """the tenant, if it may change data: a tenant that stopped paying is read-only"""
    tenant = current_tenant()
    if not tenant.active:
        raise ApiError(403, "subscription inactive: your tasks are read-only")
    return tenant
