# web/ — the TaskBoard web app (Course A5)

TaskBoard's web front end, built with **Angular** (standalone components, signals, plain CSS, no extra
libraries). It talks to the API only through the gateway, at `/v1/...`.

| file | what it is | lesson |
|---|---|---|
| `src/index.html`, `src/main.ts` | the one HTML page; Angular starts in `<app-root>` | 1 · a single-page app |
| `src/app/app.ts`, `app.html` | the shell: header, and `<router-outlet>` where the page goes | 1 |
| `src/app/tasks/task-item.ts`, `.html` | one row: an `input` (the task) and an `output` (checkbox clicked) | 2 · components and templates |
| `src/app/tasks/task-list-page.ts`, `.html` | the task list: `@for` over the tasks | 2 |
| `src/app/tasks/task.ts`, `task.service.ts` | the task's shape, and every API call for tasks (`HttpClient`) | 3 · services and HttpClient |
| `src/app/app.routes.ts` | which page shows for which address | 4 · routing and forms |
| `src/app/tasks/task-form-page.ts`, `.html` | new and edit, one reactive form, with the API's rules | 4 |
| `src/app/auth/auth.service.ts` | log in, keep the tokens in `localStorage`, log out | 5 · login |
| `src/app/auth/auth.interceptor.ts` | adds `Authorization: Bearer <token>` to every request | 5 |
| `src/app/auth/auth.guard.ts` | pages that need a login send you to `/login` | 5 |
| `src/app/**/*.spec.ts` | unit tests: the task row and the auth service | |
| `proxy.conf.json` | in development, sends `/v1` to the gateway on port 8080 | |
| `Dockerfile` | builds the app and puts the files into the gateway's nginx | |

See the top-level README, *Course A5: the web app*, for how to run it.
