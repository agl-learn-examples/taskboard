from flask import Blueprint, request

from ..errors import ApiError
from ..extensions import db
from ..models import Board
from ..tenancy import current_tenant, writable_tenant

bp = Blueprint("boards", __name__, url_prefix="/boards")


@bp.get("")
def list_boards():
    tenant = current_tenant()
    return [b.to_dict() for b in db.session.scalars(db.select(Board).filter_by(tenant_id=tenant.id).order_by(Board.id))]


@bp.post("")
def create_board():
    tenant = writable_tenant()
    data = request.get_json(silent=True) or {}
    if not data.get("name"):
        raise ApiError(400, "name is required")
    board = Board(tenant_id=tenant.id, name=data["name"])
    db.session.add(board)
    db.session.commit()
    return board.to_dict(), 201
