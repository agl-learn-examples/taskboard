// Course B5: a performance test of the task list, with k6 (https://grafana.com/docs/k6/).
// Logs in once, then several virtual users (VUs) ask for GET /v1/tasks again and again.
// Run it against the running stack (README, "Course B5"):
//     docker run --rm -i --network host -v "$PWD/tests/perf:/perf" grafana/k6:2.3.0 run /perf/tasks-list.js
import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8080';

export const options = {
  vus: Number(__ENV.VUS || 5), // 5 users, each about one request a second: under the gateway's 10 a second
  duration: __ENV.DURATION || '30s',
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests answer in under 500 ms
    http_req_failed: ['rate<0.01'], // under 1% fail (any status of 400 or more counts as failed)
  },
};

// setup() runs once, before the users start: one login, not one per request (the login limit is 10 a minute)
export function setup() {
  const res = http.post(
    `${BASE_URL}/v1/auth/login`,
    JSON.stringify({ email: 'priya@blueleaf.example', password: 'demo-password-123' }),
    { headers: { 'Content-Type': 'application/json' } },
  );
  if (res.status !== 200) throw new Error(`login failed: ${res.status} ${res.body}`);
  return { token: res.json('access_token') };
}

// each virtual user runs this again and again until the time is up
export default function (data) {
  const res = http.get(`${BASE_URL}/v1/tasks`, {
    headers: { Authorization: `Bearer ${data.token}` },
  });
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(1);
}
