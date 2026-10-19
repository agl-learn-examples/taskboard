from flask import Blueprint, request

from ..errors import ApiError
from ..extensions import db
from ..models import PRIORITIES, Task
from ..tenancy import current_tenant, writable_tenant

bp = Blueprint("tasks", __name__, url_prefix="/tasks")


def find_task(tenant, task_id):
    """Another tenant's task answers 404, as if it were not there: nobody learns it exists."""
    task = db.session.scalar(db.select(Task).filter_by(id=task_id, tenant_id=tenant.id))
    if task is None:
        raise ApiError(404, "not found")
    return task


@bp.get("")
def list_tasks():
    tenant = current_tenant()
    query = db.select(Task).filter_by(tenant_id=tenant.id).order_by(Task.id)
    return [t.to_dict() for t in db.session.scalars(query)]


@bp.post("")
def create_task():
    tenant = writable_tenant()
    data = request.get_json(silent=True) or {}
    if not data.get("title"):
        raise ApiError(400, "title is required")
    priority = data.get("priority", "normal")
    if priority not in PRIORITIES:
        raise ApiError(400, "priority must be low, normal or high")
    task = Task(tenant_id=tenant.id, title=data["title"], priority=priority, board_id=data.get("board_id"))
    db.session.add(task)
    db.session.commit()
    return task.to_dict(), 201, {"Location": f"/tasks/{task.id}"}


@bp.get("/<int:task_id>")
def get_task(task_id):
    return find_task(current_tenant(), task_id).to_dict()


@bp.put("/<int:task_id>")
def replace_task(task_id):
    task = find_task(writable_tenant(), task_id)
    data = request.get_json(silent=True) or {}
    if not data.get("title"):
        raise ApiError(400, "title is required")
    task.title, task.done = data["title"], bool(data.get("done"))
    db.session.commit()
    return task.to_dict()


@bp.delete("/<int:task_id>")
def delete_task(task_id):
    task = find_task(writable_tenant(), task_id)
    db.session.delete(task)
    db.session.commit()
    return "", 204
