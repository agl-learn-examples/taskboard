import jwt
import pytest

from taskboard.errors import ApiError
from taskboard.models import User
from taskboard.tokens import decode, make_access, make_refresh

pytestmark = pytest.mark.unit
PRIYA = User(id=1, tenant_id=7, email="priya@blueleaf.example", name="Priya", role="owner")


def test_access_token_says_who_and_which_tenant(app_ctx):
    token, _ = make_access(PRIYA)
    claims = decode(token, "access")
    assert (claims["sub"], claims["tid"], claims["role"]) == ("1", 7, "owner")


def test_kinds_are_not_interchangeable(app_ctx):
    token, _ = make_refresh(PRIYA)
    with pytest.raises(ApiError, match="expected an access token"):
        decode(token, "access")


def test_expired(app_ctx):
    app_ctx.config["ACCESS_TOKEN_MINUTES"] = -1
    token, _ = make_access(PRIYA)
    with pytest.raises(ApiError, match="token expired"):
        decode(token, "access")


def test_changed_payload_breaks_the_signature(app_ctx):
    _, claims = make_access(PRIYA)
    forged = jwt.encode({**claims, "tid": 8}, "not-the-server-key-but-long-enough!", algorithm="HS256")
    with pytest.raises(ApiError, match="invalid token"):
        decode(forged, "access")
