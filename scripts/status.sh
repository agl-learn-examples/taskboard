#!/bin/sh
# Is TaskBoard up? (Course A7) The health check, the containers, and what the gateway saw in the last 5 minutes.
#     scripts/status.sh                          # the stack on http://localhost:8080
#     scripts/status.sh https://localhost:8443   # with HTTPS (-k: accept the self-signed certificate)
# Exits 1 when the health check fails, so a cron job or a CI step can act on it.
URL="${1:-http://localhost:8080}"
healthy=yes

echo "== health: $URL/v1/health"
# -f: an answer of 400 or more (503 when the database is down) counts as a failure; -L follows a redirect
curl -fsSLk --max-time 5 "$URL/v1/health" || healthy=no
echo

echo "== containers"
docker compose ps

echo "== gateway, last 5 minutes (one JSON line per request)"
logs=$(docker compose logs --since 5m --no-log-prefix gateway | grep '"status":')
echo "requests:                $(printf '%s\n' "$logs" | grep -c '"status":')"
echo "server errors (5xx):     $(printf '%s\n' "$logs" | grep -c '"status":5')"
echo "too many requests (429): $(printf '%s\n' "$logs" | grep -c '"status":429')"

if [ "$healthy" = no ]; then
    echo "UNHEALTHY"
    exit 1
fi
