# TaskBoard

TaskBoard is a small to-do app for teams, sold as SaaS (software as a service). Teams sign up, invite their
members and share task boards. It is the running example of the **Build a SaaS App** and **Testing and
Quality** courses in Career Launch on [agentlabs learn](https://learning.myagentlabs.ai).

It starts as the Tasks API you met in the DevOps track, and grows up course by course:

```
 web app (Angular, A5) ──┐
                         ├─► API gateway (nginx) ─► API service (Flask) ─┬─► Postgres (data, on disk)
 phone app (Flutter, A6) ┘   route · check token    tenants · users      └─► Redis (sessions, cached plans)
                             rate limit · log       plans · tasks
```

| part | folder | what it does | built in |
|---|---|---|---|
| API gateway | `gateway/` | the one front door (nginx): routing, token check, rate limit, logs | A4 |
| API service | `api/` | Python and Flask: the rules (tenants, users, roles, plans, tasks) | A2, A3 |
| Postgres | (image) | the database: tenants, users, boards, tasks | A2 |
| Redis | (image) | fast, short-lived data: sessions, logged-out tokens, cached plans | A3 |
| web app | `web/` | Angular | A5 (later) |
| phone app | `mobile/` | Flutter | A6 (later) |

## You are at tag `b2-pytest`

Course B2, *Pytest from zero*: the API has a test suite to learn from (`api/tests/`), with fixtures, parametrize,
mocking and coverage. The app is the same as at `a4-gateway`.

## Run it (one command)

You need [Docker](https://docs.docker.com/get-docker/) with Compose v2 (`docker compose version`) and Git.

    git clone https://github.com/agl-learn-examples/taskboard.git
    cd taskboard
    docker compose up --build

The first start downloads the images and takes a few minutes. It is ready when the gateway says `Healthy`
(`docker compose ps` in a second terminal). Stop it with Ctrl+C; `docker compose down -v` also deletes the data.

The stack starts with demo data. In a second terminal, log in as Priya and ask for her team's tasks:

    curl -s localhost:8080/v1/auth/login -H "Content-Type: application/json" \
         -d '{"email": "priya@blueleaf.example", "password": "demo-password-123"}'

Copy the `access_token` from the answer, then:

    TOKEN=<paste it here>
    curl -H "Authorization: Bearer $TOKEN" localhost:8080/v1/tasks

The demo users all have the password `demo-password-123`, a fake one for practice:

| user | tenant | plan | role |
|---|---|---|---|
| priya@blueleaf.example | BlueLeaf Studio | Team | owner |
| arjun@blueleaf.example | BlueLeaf Studio | Team | admin |
| meera@blueleaf.example | BlueLeaf Studio | Team | member |
| ravi@sharma.example | Sharma Traders | Free | owner |

Settings (ports, passwords, rate limits) have practice defaults in `compose.yaml`. To change one, copy
`.env.example` to `.env` and edit it. Every value in it is a fake example: never put a real secret in git.

## Which lesson uses which tag

Each lesson says "check out tag X". To go there: `git checkout X`, then `docker compose down -v` (the
database may be from another tag) and start again as the README at that tag says.

| tag | course | what the code has |
|---|---|---|
| `a1-start` | A1 · How a SaaS app fits together | the Tasks API from the DevOps track, unchanged, in `api/` |
| `a2-flask` | A2 · Backend APIs with Python Flask | blueprints, validation, SQLAlchemy on Postgres, Alembic migrations, tenants, pagination |
| `a3-auth` | A3 · Security: logins and JWT | bcrypt passwords, JWT access and refresh tokens, roles, Redis sessions and logout |
| `a4-gateway` | A4 · The API gateway | nginx in front: routing, token check, rate limits, JSON logs; one-command stack |
| `b2-pytest` | B2 · Pytest from zero | the test suite: fixtures, parametrize, mocking, coverage |
| `b3-api-tests` | B3 · API testing | (coming) httpx tests against the running stack, in CI |

## Endpoints

Through the gateway, every path starts with `/v1` (`localhost:8080/v1/tasks`). All but `/v1/health` and the
first three `/auth` routes need `Authorization: Bearer <access token>`; without a valid one the gateway answers
401 and the API never sees the request.

| method | path | who | does |
|---|---|---|---|
| GET | /health | anyone | `{"status": "ok"}`, or 503 if the database is down |
| POST | /auth/signup | anyone | a new tenant (Free plan) and its owner: `{"tenant_name", "name", "email", "password"}` |
| POST | /auth/login | anyone | `{"email", "password"}` → `{"access_token", "refresh_token", "token_type", "expires_in"}` |
| POST | /auth/refresh | anyone | `{"refresh_token"}` → a new token pair; each refresh token works once |
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
| GET, PUT, PATCH, DELETE | /tasks/&lt;id&gt; | member | read, replace (fields left out go back to defaults), change some fields, delete; another tenant's task is 404 |

Errors are JSON: `{"error": "invalid input", "details": [{"field": "title", "message": "Field required"}]}`.

| status | means |
|---|---|
| 400 | the body or query is wrong; `details` says which field |
| 401 | no token, a bad one, an expired one, or logged out |
| 403 | your role or plan does not allow it, or the tenant stopped paying (read-only) |
| 404 | no such thing in *your* tenant |
| 429 | too many requests: the gateway's rate limit |

A tenant that stopped paying is read-only: `docker compose exec api flask --app wsgi set-active "Sharma Traders" false`.

## See what is going on

    docker compose ps                    # the four services and their health
    docker compose logs -f gateway       # one JSON line per request: status, tenant, user, time
    docker compose logs -f api
    docker compose exec db psql -U taskboard -c "SELECT id, tenant_id, title, done FROM tasks"
    docker compose exec redis redis-cli keys '*'

## Tests

    cd api
    python3 -m venv .venv
    . .venv/bin/activate
    pip install -r requirements-dev.txt
    pytest                           # every test; they use SQLite and a fake Redis, so nothing else needs to run
    pytest tests/unit                # only the unit tests: one function at a time
    pytest -k refresh -v             # only tests with "refresh" in their name, one line each
    pytest --cov                     # and which lines of taskboard/ no test reached

| where | what | example |
|---|---|---|
| `api/tests/unit/` | unit tests: one function, no app or database | `test_validation.py` (parametrize), `test_cache.py` (mocking Redis) |
| `api/tests/` | the API service through Flask's test client, with a fresh database per test | `test_auth.py`, `test_roles.py` |
| `api/tests/conftest.py` | shared fixtures: `app`, `client`, `tenant` (a signed-up, logged-in owner) | |

GitHub Actions runs them on every push and pull request (`.github/workflows/ci.yml`).

## Work on the API without Docker

    cd api
    python3 -m venv .venv
    . .venv/bin/activate
    pip install -r requirements-dev.txt
    flask --app wsgi db upgrade      # makes taskboard.db (SQLite) from the migrations
    flask --app wsgi seed            # demo data; needs Redis only for logging in
    flask --app wsgi run

A new model field needs a migration: `flask --app wsgi db migrate -m "what changed"` (against `DATABASE_URL`,
SQLite by default) writes a file in `api/migrations/versions/`. Read it, then `flask --app wsgi db upgrade`.
