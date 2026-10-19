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

## You are at tag `a1-start`

This is where Course A1 begins: the Tasks API from the DevOps track, copied into `api/`, unchanged.
One program, one user, one SQLite file. Course A1 draws the map of what it will become.

## Run it

    git clone https://github.com/agl-learn-examples/taskboard.git
    cd taskboard/api
    python3 -m venv .venv
    . .venv/bin/activate
    pip install -r requirements.txt
    flask --app app run

Then, in a second terminal:

    curl localhost:5000/health

Run the tests with `pytest` (inside the virtual environment).
