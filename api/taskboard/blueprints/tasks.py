from flask import Blueprint

from ..errors import ApiError
from ..extensions import db
from ..models import Board, Task
from ..tenancy import current_tenant, writable_tenant
from ..validation import TaskIn, TaskPatch, parse

bp = Blueprint("tasks", __name__, url_prefix="/tasks")


def find_task(tenant, task_id):
    """Another tenant's task answers 404, as if it were not there: nobody learns it exists."""
    task = db.session.scalar(db.select(Task).filter_by(id=task_id, tenant_id=tenant.id))
    if task is None:
        raise ApiError(404, "not found")
    return task


def check_board(tenant, board_id):
    if board_id is not None and not db.session.scalar(db.select(Board).filter_by(id=board_id, tenant_id=tenant.id)):
        raise ApiError(400, "invalid input", details=[{"field": "board_id", "message": "no such board"}])


@bp.get("")
def list_tasks():
    tenant = current_tenant()
    query = db.select(Task).filter_by(tenant_id=tenant.id).order_by(Task.id)
    return [t.to_dict() for t in db.session.scalars(query)]


@bp.post("")
def create_task():
    tenant = writable_tenant()
    data = parse(TaskIn)
    check_board(tenant, data.board_id)
    task = Task(tenant_id=tenant.id, **data.model_dump())
    db.session.add(task)
    db.session.commit()
    return task.to_dict(), 201, {"Location": f"/tasks/{task.id}"}


@bp.get("/<int:task_id>")
def get_task(task_id):
    return find_task(current_tenant(), task_id).to_dict()


@bp.put("/<int:task_id>")
def replace_task(task_id):
    """PUT replaces the whole task: fields you leave out go back to their defaults."""
    tenant = writable_tenant()
    task = find_task(tenant, task_id)
    data = parse(TaskIn)
    check_board(tenant, data.board_id)
    for field, value in data.model_dump().items():
        setattr(task, field, value)
    db.session.commit()
    return task.to_dict()


@bp.patch("/<int:task_id>")
def update_task(task_id):
    """PATCH changes only the fields you send."""
    tenant = writable_tenant()
    task = find_task(tenant, task_id)
    data = parse(TaskPatch)
    changes = data.model_dump(exclude_unset=True)
    if "board_id" in changes:
        check_board(tenant, changes["board_id"])
    for field, value in changes.items():
        if value is None and field != "board_id":
            raise ApiError(400, "invalid input", details=[{"field": field, "message": "may not be null"}])
        setattr(task, field, value)
    db.session.commit()
    return task.to_dict()


@bp.delete("/<int:task_id>")
def delete_task(task_id):
    task = find_task(writable_tenant(), task_id)
    db.session.delete(task)
    db.session.commit()
    return "", 204
