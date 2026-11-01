"""Settings come from environment variables, so the same code runs on a laptop, in Docker and in CI."""
import os


class Config:
    # sqlite:///taskboard.db on your laptop; postgresql+psycopg://... in Docker Compose
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///taskboard.db")
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}  # noqa: RUF012 (Flask only reads it)
    # The key that signs login tokens. Anyone who has it can make tokens for any user: in real life it
    # comes from a secret store, never from git. The default only works for practice on your laptop.
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    JWT_SECRET = os.environ.get("JWT_SECRET", "dev-only-insecure-secret-change-me-0000")
    BCRYPT_ROUNDS = 12                     # each +1 doubles the work; tests use 4 to run fast
    ACCESS_TOKEN_MINUTES = int(os.environ.get("ACCESS_TOKEN_MINUTES", "15"))
    REFRESH_TOKEN_DAYS = int(os.environ.get("REFRESH_TOKEN_DAYS", "7"))
