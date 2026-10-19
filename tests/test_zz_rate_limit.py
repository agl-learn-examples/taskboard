"""Last on purpose (zz): it uses up this client's request allowance for a moment."""
import time
from concurrent.futures import ThreadPoolExecutor

import pytest


@pytest.mark.slow
def test_too_many_requests(owner):
    with ThreadPoolExecutor(max_workers=10) as pool:
        codes = list(pool.map(lambda _: owner.get("/tasks").status_code, range(60)))
    assert 200 in codes
    assert 429 in codes                               # the gateway's limit: 10 a second, burst 20
    r = owner.get("/tasks")
    if r.status_code == 429:
        assert r.json() == {"error": "too many requests, slow down"}
    time.sleep(2.5)                                   # let the allowance refill before anything else runs
