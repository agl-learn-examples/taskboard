"""Login tokens are JWTs (JSON Web Tokens): three base64 parts, header.payload.signature.

The payload says who you are ("sub": user id, "tid": tenant id, "role") and when the token expires ("exp").
Anyone can READ a JWT (paste one into jwt.io), so never put a secret in it. Nobody can CHANGE one
without the server's key: the signature would no longer match.

  access token   short-lived (15 min); sent with every request: Authorization: Bearer <token>
  refresh token  long-lived (7 days); sent only to POST /auth/refresh, to get a new access token
"""
import uuid
from datetime import datetime, timedelta, timezone

import jwt
from flask import current_app

from .errors import ApiError

ALGORITHM = "HS256"


def _make(user, kind, lifetime):
    now = datetime.now(timezone.utc)
    claims = {"sub": str(user.id), "tid": user.tenant_id, "role": user.role, "type": kind,
              "jti": uuid.uuid4().hex, "iat": now, "exp": now + lifetime}
    return jwt.encode(claims, current_app.config["JWT_SECRET"], algorithm=ALGORITHM), claims


def make_access(user):
    return _make(user, "access", timedelta(minutes=current_app.config["ACCESS_TOKEN_MINUTES"]))


def make_refresh(user):
    return _make(user, "refresh", timedelta(days=current_app.config["REFRESH_TOKEN_DAYS"]))


def decode(token, kind):
    """the token's claims, or 401: expired, tampered with, or the wrong kind of token"""
    try:
        claims = jwt.decode(token, current_app.config["JWT_SECRET"], algorithms=[ALGORITHM],
                            options={"require": ["exp", "sub", "type", "jti"]})
    except jwt.ExpiredSignatureError:
        raise ApiError(401, "token expired")
    except jwt.InvalidTokenError:
        raise ApiError(401, "invalid token")
    if claims["type"] != kind:
        raise ApiError(401, f"expected an {kind} token")
    return claims
