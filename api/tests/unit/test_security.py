"""Fixtures (app_ctx) and parametrize: one test, many cases."""
import pytest

from taskboard.security import check_password, hash_password

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("password", ["demo-password-123", "a much longer pass phrase", "ಕನ್ನಡ-पासवर्ड-1"])
def test_right_password_matches(app_ctx, password):
    assert check_password(password, hash_password(password))


@pytest.mark.parametrize("wrong", ["demo-password-124", "DEMO-PASSWORD-123", "", " demo-password-123"])
def test_wrong_password_does_not(app_ctx, wrong):
    assert not check_password(wrong, hash_password("demo-password-123"))


def test_same_password_two_hashes(app_ctx):
    """bcrypt mixes in a random salt, so equal passwords do not give equal hashes"""
    assert hash_password("same-password") != hash_password("same-password")


def test_user_without_a_password_cannot_log_in(app_ctx):
    assert check_password("anything", None) is False
