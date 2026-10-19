from flask import Blueprint

from ..errors import ApiError
from ..extensions import db
from ..models import Board, Task
from ..tenancy import current_tenant, require_role, writable_tenant
from ..validation import BoardIn, parse

bp = Blueprint("boards", __name__, url_prefix="/boards")


@bp.get("")
def list_boards():
    tenant = current_tenant()
    return [b.to_dict() for b in db.session.scalars(db.select(Board).filter_by(tenant_id=tenant.id).order_by(Board.id))]


@bp.post("")
def create_board():
    tenant = writable_tenant()
    board = Board(tenant_id=tenant.id, name=parse(BoardIn).name)
    db.session.add(board)
    db.session.commit()
    return board.to_dict(), 201


@bp.delete("/<int:board_id>")
def delete_board(board_id):
    """admins and owners only: it deletes the board's tasks too"""
    require_role("admin")
    tenant = writable_tenant()
    board = db.session.scalar(db.select(Board).filter_by(id=board_id, tenant_id=tenant.id))
    if board is None:
        raise ApiError(404, "not found")
    db.session.execute(db.delete(Task).filter_by(board_id=board.id, tenant_id=tenant.id))
    db.session.delete(board)
    db.session.commit()
    return "", 204
