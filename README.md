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

## You are at tag `a3-auth`

The end of Course A3, *Security: logins and JWT*. Users log in with a password (stored as a bcrypt hash) and get
a JWT access token (15 minutes) and a refresh token (7 days). Every request sends
`Authorization: Bearer <access token>`; the tenant comes from the signed token. Redis remembers sessions
(refresh tokens), logged-out tokens and each tenant's plan. Roles: member, admin, owner.

## Run it (one command)

You need Docker with Compose v2.

    git clone https://github.com/agl-learn-examples/taskboard.git
    cd taskboard
    git checkout a3-auth
    cp .env.example .env
    docker compose up --build

In a second terminal, add the demo data, log in as Priya and ask for her team's tasks:

    docker compose exec api flask --app wsgi seed
    curl -s localhost:8000/auth/login -H "Content-Type: application/json" \
         -d '{"email": "priya@blueleaf.example", "password": "demo-password-123"}'

Copy the `access_token` from the answer, then:

    TOKEN=<paste it here>
    curl -H "Authorization: Bearer $TOKEN" localhost:8000/tasks

The demo users (password `demo-password-123`, a fake one for practice):

| user | tenant | plan | role |
|---|---|---|---|
| priya@blueleaf.example | BlueLeaf Studio | Team | owner |
| arjun@blueleaf.example | BlueLeaf Studio | Team | admin |
| meera@blueleaf.example | BlueLeaf Studio | Team | member |
| ravi@sharma.example | Sharma Traders | Free | owner |

Stop with Ctrl+C; `docker compose down -v` also deletes the database.

## Endpoints

All but `/health` and the first four `/auth` routes need `Authorization: Bearer <access token>`.

| method | path | who | does |
|---|---|---|---|
| GET | /health | anyone | `{"status": "ok"}`, or 503 if the database is down |
| POST | /auth/signup | anyone | a new tenant (Free plan) and its owner: `{"tenant_name", "name", "email", "password"}` |
| POST | /auth/login | anyone | `{"email", "password"}` → `{"access_token", "refresh_token", "token_type", "expires_in"}` |
| POST | /auth/refresh | anyone | `{"refresh_token"}` → a new token pair; each refresh token works once |
| GET | /auth/verify | anyone | 204 if the access token is valid, else 401 (the gateway's check) |
| POST | /auth/logout | member | ends the session: `{"refresh_token"}` |
| GET | /auth/me | member | you and your tenant |
| GET | /tenants/me | member | your tenant |
| GET | /tenants/me/members | member | the members |
| POST | /tenants/me/members | admin | add one: `{"email", "name", "password", "role"}`; the Free plan allows 3 |
| DELETE | /tenants/me/members/&lt;id&gt; | admin | remove one |
| PUT | /tenants/me/plan | owner | `{"plan": "team"}` |
| GET, POST | /boards | member | list or create boards |
| DELETE | /boards/&lt;id&gt; | admin | delete a board and its tasks |
| GET | /tasks | member | one page: `?done=false&priority=high&q=notes&sort=-created_at&page=1&per_page=20` |
| POST | /tasks | member | create: `{"title": "...", "priority": "high", "board_id": 1}` → 201 |
| GET, PUT, PATCH, DELETE | /tasks/&lt;id&gt; | member | read, replace, change some fields, delete; another tenant's task is 404 |

A tenant that stopped paying is read-only (403 on changes): `docker compose exec api flask --app wsgi set-active "Sharma Traders" false`.

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
