"""Passwords: we store a bcrypt hash, never the password.

bcrypt is slow on purpose (about a quarter of a second), and mixes a random salt into every hash, so two
users with the same password get different hashes, and a stolen table is very slow to crack.
"""
import bcrypt
from flask import current_app


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(current_app.config["BCRYPT_ROUNDS"])).decode()


def check_password(password: str, hashed: str | None) -> bool:
    if not hashed:
        return False
    return bcrypt.checkpw(password.encode(), hashed.encode())
