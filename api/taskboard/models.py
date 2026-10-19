"""The tables. Every row that belongs to a customer carries tenant_id: that is what keeps tenants apart."""
from datetime import datetime, timezone

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .extensions import db

PLANS = ("free", "team")
PLAN_MEMBER_LIMIT = {"free": 3, "team": None}       # None: no limit
PRIORITIES = ("low", "normal", "high")
ROLES = ("member", "admin", "owner")      # each can do what the ones before it can, and more


def now():
    return datetime.now(timezone.utc)


class Tenant(db.Model):
    __tablename__ = "tenants"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    plan: Mapped[str] = mapped_column(String(20), default="free")
    active: Mapped[bool] = mapped_column(default=True)      # False: stopped paying, so read-only
    created_at: Mapped[datetime] = mapped_column(default=now)

    users: Mapped[list["User"]] = relationship(back_populates="tenant")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "plan": self.plan, "active": self.active}


class User(db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    # bcrypt hash of the password, never the password itself; NULL: this user cannot log in yet
    password_hash: Mapped[str | None] = mapped_column(String(100))
    role: Mapped[str] = mapped_column(String(10), default="member", server_default="member")
    created_at: Mapped[datetime] = mapped_column(default=now)

    tenant: Mapped[Tenant] = relationship(back_populates="users")

    def to_dict(self):
        return {"id": self.id, "email": self.email, "name": self.name, "role": self.role}


class Board(db.Model):
    __tablename__ = "boards"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(default=now)

    def to_dict(self):
        return {"id": self.id, "name": self.name}


class Task(db.Model):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True)
    board_id: Mapped[int | None] = mapped_column(ForeignKey("boards.id"))
    title: Mapped[str] = mapped_column(String(200))
    done: Mapped[bool] = mapped_column(default=False)
    priority: Mapped[str] = mapped_column(String(10), default="normal")
    created_at: Mapped[datetime] = mapped_column(default=now)

    def to_dict(self):
        return {"id": self.id, "title": self.title, "done": self.done, "priority": self.priority,
                "board_id": self.board_id}
