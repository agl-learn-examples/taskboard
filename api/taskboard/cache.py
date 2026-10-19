"""Redis: fast, short-lived data, kept in memory.

TaskBoard keeps three kinds of things here, each with a time-to-live (TTL), after which Redis forgets it:

  refresh:<jti>   a refresh token that is still allowed (a login "session"); deleted at logout
  revoked:<jti>   an access token that was logged out before it expired
  tenant:<id>     a copy of a tenant's plan and status, so most requests skip the database

Lose all of it and nothing important is gone: people log in again, and the plans are read from Postgres.
"""
import json
import logging

import redis
from flask import current_app

log = logging.getLogger(__name__)
TENANT_TTL = 60          # seconds a cached plan is trusted


def init_app(app):
    app.extensions["redis"] = app.config.get("REDIS_CLIENT") or redis.Redis.from_url(
        app.config["REDIS_URL"], decode_responses=True, socket_timeout=2)


def r():
    return current_app.extensions["redis"]


def tenant_status(tenant):
    """{"plan": "free", "active": true} for this tenant: from Redis if we can, else from Postgres"""
    key = f"tenant:{tenant.id}"
    try:
        cached = r().get(key)
        if cached:
            return json.loads(cached)
    except redis.RedisError as e:                # Redis is down: slower, but still correct
        log.warning("redis unavailable, reading the plan from the database: %s", e)
        return {"plan": tenant.plan, "active": tenant.active}
    status = {"plan": tenant.plan, "active": tenant.active}
    try:
        r().set(key, json.dumps(status), ex=TENANT_TTL)
    except redis.RedisError:
        pass
    return status


def forget_tenant(tenant_id):
    """call after changing a tenant's plan or status, so the old copy is not used"""
    try:
        r().delete(f"tenant:{tenant_id}")
    except redis.RedisError:
        pass
