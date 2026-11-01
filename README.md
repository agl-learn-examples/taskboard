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
| web app | `web/` | Angular: log in, list, add and change tasks; served by the gateway | A5 |
| phone app | `mobile/` | Flutter: task list, login, tokens in secure storage | A6 |

## Where you are

`main` is the latest: everything up to Course A7, *Ship it: capstone*. To see the code as a lesson saw it, check out
that lesson's tag (below).

## Run it (one command)

You need [Docker](https://docs.docker.com/get-docker/) with Compose v2 (`docker compose version`) and Git.

    git clone https://github.com/agl-learn-examples/taskboard.git
    cd taskboard
    docker compose up --build

The first start downloads the images and takes a few minutes. It is ready when the gateway says `Healthy`
(`docker compose ps` in a second terminal). Stop it with Ctrl+C; `docker compose down -v` also deletes the data.

Open http://localhost:8080 for the web app (Course A5) and log in as one of the demo users below.

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
| `b3-api-tests` | B3 · API testing | httpx tests against the running stack: logins, contracts, tenants, rate limits; in CI |
| `a5-angular` | A5 · Web front end with Angular | the web app in `web/`: task list, form, login; served by the gateway at `/` |
| `a6-flutter` | A6 · Mobile app with Flutter | `mobile/`: task list, `ApiClient`, login with tokens in secure storage, logout; tests |
| `b4-playwright` | B4 · Web testing with Playwright | `tests/e2e/`: browser tests of the web app (login, tasks, the guard), a page object; in CI |
| `b5-quality` | B5 · Tests in CI, and quality habits | linters (ruff, ESLint) in CI, test reports as artifacts, a review checklist, a k6 performance test |
| `a7-ship` | A7 · Ship it: capstone | pinned base images, HTTPS at the gateway (`compose.https.yaml`), `scripts/status.sh` |

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

### API tests: the running stack, over HTTP

`tests/` (at the top of the repo) sends real requests through the gateway, as the web and phone apps will.
Each test signs up its own new tenant, so tests never share data.

    AUTH_RATE=600r/m AUTH_BURST=100 docker compose up -d --build --wait    # login limit raised for the tests
    python3 -m venv .venv && . .venv/bin/activate
    pip install -r tests/requirements.txt
    pytest tests
    docker compose down -v

GitHub Actions runs both kinds on every push and pull request (`.github/workflows/ci.yml`): first the API
service's tests, then the API tests against the whole stack. It also runs the web app's unit tests (A5) and the browser tests (B4).

## Course A5: the web app

The web app is in `web/` (its README lists which file each lesson uses). `docker compose up --build` builds
it (`web/Dockerfile`: Node builds the files, then they are copied into the gateway's nginx), so one address
serves both: http://localhost:8080/ is the app, http://localhost:8080/v1/ is the API. Same address, so the
browser needs no CORS settings.

To change the app and see it at once, run the dev server. You need [Node.js](https://nodejs.org) 22.22 or
newer (`node -v`).

    docker compose up --build -d     # the API and the gateway, on port 8080
    cd web
    npm ci                           # the exact versions in package-lock.json
    npm start                        # the dev server: http://localhost:4200, reloads when you save
    npm test                         # the unit tests (Vitest), once, no browser window
    npx ng build                     # the files the gateway serves, in dist/taskboard-web/browser/

The dev server sends every `/v1/...` request on to the gateway (`proxy.conf.json`), so the app's code
calls `/v1/tasks` in both places.

What it does, page by page:

| address | page | needs a login |
|---|---|---|
| `/login` | email and password; keeps the tokens in the browser's `localStorage` | no |
| `/tasks` | your team's tasks, newest first; tick one to mark it done | yes |
| `/tasks/new` | a new task: title (1 to 200 characters) and priority | yes |
| `/tasks/<id>/edit` | change a task's title, priority or done | yes |

Kept simple on purpose: no automatic token refresh (after 15 minutes the API answers 401 and the app sends
you back to the login page), only the first 100 tasks, no boards, no delete button. Pages have
`data-testid` attributes and labelled fields so Course B4's Playwright tests can find them.

## Course A6: the mobile app

`mobile/` is TaskBoard's phone app, in [Flutter](https://flutter.dev): log in, see your team's tasks, log out.
It calls the API through the gateway, like any other client. `mobile/README.md` says which file does what.

### Install Flutter

Follow [the Flutter install guide](https://docs.flutter.dev/get-started/install) for your computer, then run
`flutter doctor`: it lists what is still missing. The app was built with Flutter 3.47 (Dart 3.13). You do not
need Android Studio to start: the Linux desktop or Chrome is enough. On Linux, the secure storage needs
libsecret: `sudo apt install libsecret-1-dev`.

### Run it against the stack

    docker compose up -d --build --wait      # the whole stack, in the repo's top folder
    cd mobile
    flutter pub get                          # download the packages: http, flutter_secure_storage
    flutter run -d linux                     # a phone-sized window on the Linux desktop

Log in as `priya@blueleaf.example`, password `demo-password-123`. Close the app and start it again: you are
still logged in, because the tokens wait in secure storage. Log out with the button at the top right.

The app finds the gateway at `http://localhost:8080`. Somewhere else, say so when you start it:

| where the app runs | start it with |
|---|---|
| Linux, macOS or Windows desktop | `flutter run` (the default address works) |
| Android emulator | `flutter run --dart-define=API_BASE=http://10.0.2.2:8080` (the emulator's name for your laptop) |
| a real phone on your Wi-Fi | `flutter run --dart-define=API_BASE=http://<your laptop's IP>:8080` |
| Chrome | `flutter run -d chrome --web-browser-flag=--disable-web-security` (see below) |

In Chrome the app is served from another address than the gateway (`localhost:53211`, say, not
`localhost:8080`), and browsers block such calls unless the server allows them (CORS). The gateway does not,
so for practice the flag above turns that check off in the Chrome window Flutter opens. Never browse other
sites in that window.

### Test it

    cd mobile
    flutter test                                  # unit and widget tests with a fake API: no server needed
    flutter test integration_test -d linux        # the whole app against the running stack

| where | what | example |
|---|---|---|
| `mobile/test/task_test.dart` | unit tests: JSON to a `Task` | a task with no board; a task without a title is refused |
| `mobile/test/api_client_test.dart` | `ApiClient` against a fake server (`MockClient`) | the token is sent; the API's error message is shown |
| `mobile/test/task_list_screen_test.dart` | widget tests: the list screen with a fake `ApiClient` | spinner, then tasks; "No tasks yet"; error and "Try again" |
| `mobile/integration_test/` | the real app, the real stack | log in as Priya, see her tasks (not Sharma's), log out |

## Course B4: browser tests

`tests/e2e/` holds end-to-end tests: [Playwright](https://playwright.dev) opens a real Chromium, goes to
the web app through the gateway and clicks, types and checks what the page shows, as a person would. The
page, the gateway, the API and the database all have to work together for them to pass.

    docker compose up -d --build --wait      # the whole stack, in the repo's top folder
    cd tests/e2e
    npm ci                                   # the exact versions in package-lock.json
    npx playwright install --with-deps chromium   # the browser, once (--with-deps also asks for system libraries)
    npx playwright test                      # every test, headless, one line each
    npx playwright test --headed             # the same, with the browser window open
    npx playwright test login                # only the files with "login" in their name
    npx playwright show-report               # the HTML report of the last run, in your browser
    cd ../.. && docker compose down -v       # stop the stack and delete its data

The tests point at http://localhost:8080. Somewhere else? `BASE_URL=http://localhost:8081 npx playwright test`.

| file | what it tests or does |
|---|---|
| `playwright.config.ts` | where the app is, Chromium only, a screenshot when a test fails, a trace when a test is retried |
| `auth.setup.ts` | runs first: logs in as Priya once and saves the browser's storage to `playwright/.auth/` |
| `login.spec.ts` | logging in shows the task list; a wrong password shows the error; logging out goes to `/login`; the guard sends `/tasks` to `/login` |
| `tasks.spec.ts` | create a task, see it in the list, edit it, mark it done; the form will not save an empty title |
| `pages/login-page.ts` | a page object: the login page's fields and button in one class, used by the setup and the login tests |

The tests find things the way a user does: by role and visible name (`getByRole('button', { name: 'Save' })`),
by label (`getByLabel('Title')`), and by the `data-testid` attributes the web app puts on its pages
(`getByTestId('task-item')`). Never by CSS classes or page structure, which change when the design does.
They never sleep: Playwright waits for each thing to appear, and `expect` keeps checking until it is true.

**The login limit.** The gateway allows 10 logins a minute from one address (5 at once). So the tests do
not log in each time: `auth.setup.ts` logs in once and every task test starts from that saved login. Only
two login tests really log in (the right password, and the wrong one), so a run uses 3 logins and two runs
in a row still pass with the normal limit. The logout test logs in on its own, because logging out ends that
session on the server and would log out every test that shares it. CI raises the limit anyway
(`AUTH_RATE=600r/m AUTH_BURST=100`, as for the API tests), so a retried test never meets a 429.

Each task test's title ends with the time (`Write the release notes 1793...`), so running the tests again
never trips over a task an earlier run made. The tasks pile up in BlueLeaf's list until `docker compose down -v`.

**When a test fails** the report shows the step that failed, the error and a screenshot. To see every step,
run with a trace and open it:

    npx playwright test --trace on
    npx playwright show-trace test-results/<the test's folder>/trace.zip

The trace viewer shows each action with the page before and after it, the console and the network requests.
In CI (`.github/workflows/ci.yml`, job `e2e`) a failed test is retried once with a trace, and the HTML report,
traces included, is kept as the run's `playwright-report` artifact: download it, unzip it and run
`npx playwright show-report <the folder>`.

## Course B5: quality in CI

Every push and pull request runs `.github/workflows/ci.yml` on GitHub Actions. Each job is one kind of check;
if any of them fails, the run is red and the pull request shows it.

| job | what it runs | course |
|---|---|---|
| `test` | the API service's pytest tests, on Python 3.12 and 3.13 | B2 |
| `lint` | ruff on `api/`, ESLint on `web/` | B5 |
| `web` | the web app's unit tests (Vitest), then a production build | A5 |
| `api-tests` | the whole stack in Compose, then HTTP tests through the gateway | B3 |
| `e2e` | the whole stack, then Playwright in Chromium | B4 |

### Reports

A red run says *that* something failed; a report says *what*. Open the run on GitHub (the Actions tab) and
scroll to **Artifacts**:

| artifact | what is in it | kept |
|---|---|---|
| `pytest-report-3.12`, `pytest-report-3.13` | `pytest-report.xml` (JUnit XML: each test, passed or failed, and how long it took), `coverage.xml`, and `htmlcov/` (open `index.html`: every file, its missed lines in red) | always |
| `playwright-report` | the browser tests' HTML report, with screenshots and traces | when a test fails |

The run's summary page also shows the coverage total for each Python version. JUnit XML is the format almost
every CI tool reads, so the same file works in GitLab or Jenkins. To make the reports on your laptop:

    cd api
    pytest --cov --cov-report=html --junitxml=pytest-report.xml     # then open htmlcov/index.html

### Linting

A linter reads the code without running it and points at likely mistakes: an unused import, a variable that is
never used, an `except Exception:` that would hide a real bug. Fixing them is cheaper than reviewing them.

    cd api
    ruff check .              # ruff, with its default rules (api/ruff.toml sets only the Python version)
    ruff check --fix .        # and fix what it can fix by itself (import order, for example)

    cd web
    npm run lint              # ESLint with Angular's rules (eslint.config.js, made by `ng add angular-eslint`)

The `lint` job runs both, and one finding fails the build. In a pull request, ruff's findings also show on the
lines they are about. When the linter is wrong for one line, say so on that line and say why:
`# noqa: RUF012 (Flask only reads it)` in `api/taskboard/config.py`. Never switch a rule off for the whole project
to make a red build green.

### Code review

`.github/pull_request_template.md` fills in every new pull request: what changed, why, and a short checklist for
the author and for the reviewer. One line asks: *AI-assisted? Say which parts, and what you checked yourself.*
Code an assistant wrote is your code once you open the pull request: run it and read every line.

### Performance: k6

`tests/perf/tasks-list.js` is a [k6](https://grafana.com/docs/k6/) test. It logs in once (in `setup()`), then 5
virtual users ask for `GET /v1/tasks`, each about once a second, for 30 seconds. It passes when 95% of the
requests answer in under 500 ms (`p(95)<500`) and fewer than 1% fail. You do not need to install k6: Docker
runs it.

    docker compose up -d --build --wait
    docker run --rm -i --network host -v "$PWD/tests/perf:/perf" grafana/k6:2.3.0 run /perf/tasks-list.js
    docker compose down -v

`--network host` lets the k6 container reach `localhost:8080` on Linux. On macOS or Windows (Docker Desktop),
leave it out and add `-e BASE_URL=http://host.docker.internal:8080`. Change the load with `-e VUS=20` or
`-e DURATION=1m`.

On a laptop, 5 users give p95 of about 20 ms and no errors. With `-e VUS=20` almost half the requests fail
with 429: the gateway allows 10 requests a second from one address, so the test finds the rate limit, not a
slow API. That is a real result too: a performance test measures the whole path, gateway included.

It is not in the CI run for every push: it takes time, and a shared CI machine gives noisy numbers. Run it by
hand from the Actions tab (workflow **Performance**, button **Run workflow**, `.github/workflows/perf.yml`).

## Course A7: ship it

Shipping means: the same images every time, tests that guard every change, HTTPS in front, and a way to see that
the live app is well.

### 1. Docker images

Each part that is ours has a Dockerfile: `api/Dockerfile` (Python and gunicorn) and `web/Dockerfile` (Node builds
the web app, then nginx serves it; this image is the gateway). Compose builds both, or build one by hand and give
it a tag, a name for this version:

    docker build -t taskboard-api:a7 api/
    docker build -t taskboard-gateway:a7 web/
    docker images taskboard-api                  # the image, its tag and its size

The base images are pinned to an exact version (`FROM python:3.12.16-slim-trixie`, `node:22.23.4-alpine3.24`,
`nginx:1.30.6-alpine3.24`), and so are the packages (`requirements.txt`, `package-lock.json`). A tag like
`python:3.12` moves when a new 3.12 comes out, so the same Dockerfile could build a different image next month.
Stricter still is a digest (`python:3.12.16-slim-trixie@sha256:...`), which can never change.

### 2. Tests in CI

Every push runs the whole set on GitHub Actions: unit tests, lint, API tests and browser tests against the whole
stack. See *Course B5: quality in CI* above. Ship only from a green `main`.

### 3. HTTPS at the gateway

HTTPS encrypts everything between the browser and the gateway, so nobody on the Wi-Fi can read a password or a
token. The gateway (nginx) does it: it holds the certificate and the private key, decrypts each request, and
passes it on to the API as before. On your laptop:

    gateway/certs/make-dev-cert.sh                                        # once: a certificate for localhost
    docker compose -f compose.yaml -f compose.https.yaml up -d --build --wait
    curl -k https://localhost:8443/v1/health                             # -k: accept a self-signed certificate
    curl -i http://localhost:8080/v1/health                               # 301, Location: https://localhost:8443/...

Open https://localhost:8443. The browser warns first ("not private"): the certificate is self-signed, so nobody
vouches for it. Accept it for this one practice site. `curl` without `-k` refuses it for the same reason.

| file | what it does |
|---|---|
| `gateway/certs/make-dev-cert.sh` | `openssl` makes `localhost.crt` (the certificate) and `localhost.key` (the private key); both are in `.gitignore` |
| `gateway/https.conf` | nginx: `listen 443 ssl`, the two files, and a 301 from http to https |
| `compose.https.yaml` | adds port 8443, mounts the two files and `https.conf`, and checks health over https |

Without `compose.https.yaml` nothing changes: plain http on port 8080, which the tests use. To always start
with HTTPS, put `COMPOSE_FILE=compose.yaml:compose.https.yaml` in your `.env`.

A real deployment uses a real certificate, from a certificate authority such as
[Let's Encrypt](https://letsencrypt.org) (free), for a domain name you own. Browsers trust it, so there is no
warning and no `-k`. The private key stays on the server, never in git.

### 4. Monitoring the live app

Three things tell you whether TaskBoard is well:

| what | where | tells you |
|---|---|---|
| the health check | `GET /v1/health` | `{"status": "ok"}`, or 503 when the API cannot reach the database |
| the containers | `docker compose ps` | each service up, and *healthy* (Compose runs each health check every few seconds) |
| the access log | `docker compose logs gateway` | one JSON line per request: time, status, seconds, tenant, user, request id |

`scripts/status.sh` shows all three at once, with counts from the last 5 minutes of the log:

    scripts/status.sh                            # http://localhost:8080
    scripts/status.sh https://localhost:8443     # with HTTPS

It exits with 1 when the health check fails, so a cron job or a CI step can raise the alarm. Try it: stop the
database (`docker compose stop db`), run it again, and see 503 and `UNHEALTHY`.

Because each log line is JSON, a program can read it as well as you can. To see only the failures:

    docker compose logs --no-log-prefix gateway | grep '"status":5'

The `request_id` in a log line is also in the response's `X-Request-ID` header and in the request the API gets,
so one id follows a request from the browser to the API's log. Bigger systems send these lines to a log service
and draw charts from them; the lines are the same.

### 5. Retell and reflect

From `a1-start` to here, TaskBoard grew one course at a time. `git log --oneline` tells that story in small
commits, and the tag table above marks where each course stopped.

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
