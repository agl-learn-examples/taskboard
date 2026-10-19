import sqlite3
from flask import Flask, request

app = Flask(__name__)
PRIORITIES = ("low", "normal", "high")

def db():
    con = sqlite3.connect("tasks.db")
    con.row_factory = sqlite3.Row
    con.execute("CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, title TEXT NOT NULL, done INTEGER NOT NULL DEFAULT 0, priority TEXT NOT NULL DEFAULT 'normal')")
    return con

def as_dict(r):
    return {"id": r["id"], "title": r["title"], "done": bool(r["done"]), "priority": r["priority"]}

def db_ok():
    try:
        with db() as con:
            con.execute("SELECT 1")
        return True
    except sqlite3.Error:
        return False

@app.get("/health")
def health():
    if not db_ok():
        return {"status": "error"}, 503
    return {"status": "ok"}

@app.get("/tasks")
def list_tasks():
    done = request.args.get("done")
    where, args = (" WHERE done = ?", (int(done == "true"),)) if done else ("", ())
    order = " ORDER BY title" if request.args.get("sort") == "title" else ""
    with db() as con:
        return [as_dict(r) for r in con.execute("SELECT * FROM tasks" + where + order, args)]

@app.post("/tasks")
def create_task():
    data = request.get_json(silent=True) or {}
    if not data.get("title"):
        return {"error": "title is required"}, 400
    priority = data.get("priority", "normal")
    if priority not in PRIORITIES:
        return {"error": "priority must be low, normal or high"}, 400
    with db() as con:
        cur = con.execute("INSERT INTO tasks (title, priority) VALUES (?, ?)", (data["title"], priority))
    task = {"id": cur.lastrowid, "title": data["title"], "done": False, "priority": priority}
    return task, 201, {"Location": f"/tasks/{task['id']}"}

@app.get("/tasks/<int:task_id>")
def get_task(task_id):
    with db() as con:
        r = con.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    return as_dict(r) if r else ({"error": "not found"}, 404)

@app.put("/tasks/<int:task_id>")
def replace_task(task_id):
    data = request.get_json(silent=True) or {}
    if not data.get("title"):
        return {"error": "title is required"}, 400
    with db() as con:
        cur = con.execute("UPDATE tasks SET title = ?, done = ? WHERE id = ?",
                          (data["title"], int(bool(data.get("done"))), task_id))
    if cur.rowcount == 0:
        return {"error": "not found"}, 404
    return {"id": task_id, "title": data["title"], "done": bool(data.get("done"))}

@app.delete("/tasks/<int:task_id>")
def delete_task(task_id):
    with db() as con:
        cur = con.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    return ("", 204) if cur.rowcount else ({"error": "not found"}, 404)
