from flask import Blueprint

from ..extensions import db
from ..models import Board
from ..tenancy import current_tenant, writable_tenant
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
