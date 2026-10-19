# TaskBoard

TaskBoard is a small to-do app for teams, sold as SaaS (software as a service). It is the running example of
the **Build a SaaS App** and **Testing and Quality** courses in Career Launch on
[agentlabs learn](https://learning.myagentlabs.ai).

It starts as the Tasks API you met in the DevOps track, and grows up course by course:

| part | what it does | built in |
|---|---|---|
| `api/` | the API service: Python and Flask | A2, A3 |
| Postgres | the database: tenants, users, tasks | A2 |
| Redis | fast, short-lived data: sessions, cached plans | A3 |
| `gateway/` | the one front door (nginx): routing, token check, rate limit, logs | A4 |
| `web/` | the web app (Angular) | A5 (later) |
| `mobile/` | the phone app (Flutter) | A6 (later) |

## You are at tag `a2-flask`

The end of Course A2, *Backend APIs with Python Flask*: the API service is a package with blueprints,
validated input, SQLAlchemy models on Postgres and Alembic migrations. It knows about tenants, but the client
still names its own tenant in an `X-Tenant-ID` header. Anyone could send any number: Course A3 fixes that with logins.

## Run it (one command)

You need Docker with Compose v2.

    git clone https://github.com/agl-learn-examples/taskboard.git
    cd taskboard
    git checkout a2-flask
    cp .env.example .env
    docker compose up --build

In a second terminal, add the demo data and ask for BlueLeaf Studio's tasks:

    docker compose exec api flask --app wsgi seed
    curl -H "X-Tenant-ID: 1" localhost:8000/tasks

Stop with Ctrl+C; `docker compose down -v` also deletes the database.

## Endpoints

| method | path | does |
|---|---|---|
| GET | /health | `{"status": "ok"}`, or 503 if the database is down |
| POST | /tenants | sign up a tenant: `{"name": "...", "plan": "free"}` (plans: free, team) |
| GET | /tenants/me | your tenant |
| GET, POST | /tenants/me/members | list or add members; the Free plan allows 3 |
| GET, POST | /boards | list or create boards |
| GET | /tasks | one page of tasks: `?done=false&priority=high&q=notes&sort=-created_at&page=1&per_page=20` |
| POST | /tasks | create: `{"title": "...", "priority": "high", "board_id": 1}` → 201 |
| GET, PUT, PATCH, DELETE | /tasks/&lt;id&gt; | read, replace, change some fields, delete; another tenant's task is 404 |

Errors are JSON: `{"error": "invalid input", "details": [{"field": "title", "message": "Field required"}]}`.

## Work on the API without Docker

    cd api
    python3 -m venv .venv
    . .venv/bin/activate
    pip install -r requirements-dev.txt
    pytest
    flask --app wsgi db upgrade      # makes taskboard.db (SQLite) from the migrations
    flask --app wsgi run

A new model field needs a migration: `flask --app wsgi db migrate -m "what changed"`, read the file it writes
in `api/migrations/versions/`, then `flask --app wsgi db upgrade`.
