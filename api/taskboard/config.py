"""Settings come from environment variables, so the same code runs on a laptop, in Docker and in CI."""
import os


class Config:
    # sqlite:///taskboard.db on your laptop; postgresql+psycopg://... in Docker Compose
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///taskboard.db")
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    JSON_SORT_KEYS = False
