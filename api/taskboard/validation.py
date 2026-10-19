"""Check what the client sent before we use it.

Each request body has a model: the fields it may have, their types and limits. parse() turns the JSON
into that model, or answers 400 with one clear message per bad field:

    {"error": "invalid input", "details": [{"field": "title", "message": "Field required"}]}
"""
from typing import Literal

from flask import request
from pydantic import BaseModel, ConfigDict, EmailStr, Field, ValidationError

from .errors import ApiError

Name = Field(min_length=1, max_length=100)
Priority = Literal["low", "normal", "high"]


class Body(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)   # unknown fields are an error


class TenantIn(Body):
    name: str = Name
    plan: Literal["free", "team"] = "free"


class MemberIn(Body):
    email: EmailStr
    name: str = Name


class BoardIn(Body):
    name: str = Name


class TaskIn(Body):
    title: str = Field(min_length=1, max_length=200)
    done: bool = False
    priority: Priority = "normal"
    board_id: int | None = None


class TaskPatch(Body):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    done: bool | None = None
    priority: Priority | None = None
    board_id: int | None = None


def parse(model):
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ApiError(400, "send a JSON object with Content-Type: application/json")
    try:
        return model.model_validate(data)
    except ValidationError as e:
        details = [{"field": ".".join(str(p) for p in err["loc"]) or "body", "message": err["msg"]}
                   for err in e.errors()]
        raise ApiError(400, "invalid input", details=details)
