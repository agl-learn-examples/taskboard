"""Mocking an outside service: what does TaskBoard do when Redis is slow, empty or down?"""
from unittest.mock import MagicMock

import pytest
import redis

from taskboard import cache
from taskboard.models import Tenant

pytestmark = pytest.mark.unit
BLUELEAF = Tenant(id=7, name="BlueLeaf Studio", plan="team", active=True)


@pytest.fixture
def fake_redis(app_ctx, monkeypatch):
    mock = MagicMock()
    monkeypatch.setitem(app_ctx.extensions, "redis", mock)     # swap the real client for a mock
    return mock


def test_cache_hit_skips_the_database(fake_redis):
    fake_redis.get.return_value = '{"plan": "free", "active": false}'
    assert cache.tenant_status(BLUELEAF) == {"plan": "free", "active": False}    # Redis's copy wins
    fake_redis.set.assert_not_called()


def test_cache_miss_reads_and_remembers(fake_redis):
    fake_redis.get.return_value = None
    assert cache.tenant_status(BLUELEAF) == {"plan": "team", "active": True}
    fake_redis.set.assert_called_once_with("tenant:7", '{"plan": "team", "active": true}', ex=cache.TENANT_TTL)


def test_redis_down_falls_back_to_the_database(fake_redis):
    fake_redis.get.side_effect = redis.ConnectionError("Connection refused")
    assert cache.tenant_status(BLUELEAF) == {"plan": "team", "active": True}


def test_forget_tenant_survives_redis_down(fake_redis):
    fake_redis.delete.side_effect = redis.ConnectionError("Connection refused")
    cache.forget_tenant(7)            # no exception: forgetting is best effort
