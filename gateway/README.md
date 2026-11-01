# gateway/ — the API gateway (Course A4)

nginx, configured as TaskBoard's one front door (`templates/default.conf.template`):

| job | how |
|---|---|
| route | `/v1/...` goes to the API service with `/v1` taken off; everything else is the web app (A5), built into the gateway's image by `web/Dockerfile` |
| check the token | `auth_request` asks the API's `/auth/verify` first; a missing, expired or logged-out token gets 401 here, and the API never sees the request |
| rate limit | 10 requests a second per client (burst 20); login and sign-up: `AUTH_RATE`, 10 a minute by default (burst `AUTH_BURST`, 5) → 429 |
| log | one JSON line per request to stdout, with a request id, the tenant and the user: `docker compose logs gateway` |

The API service still checks the token itself on every request. The gateway's check is the first door,
not the only one.
