#!/usr/bin/env bash
set -euo pipefail

HOST="127.0.0.1"
PORT="${AUTH_ROUTING_TEST_PORT:-3101}"
BASE_URL="http://${HOST}:${PORT}"
LOG_FILE="$(mktemp)"
SERVER_PID=""

cleanup() {
  if [[ -n "$SERVER_PID" ]]; then
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
  rm -f "$LOG_FILE"
}
trap cleanup EXIT

npx next start --hostname "$HOST" --port "$PORT" >"$LOG_FILE" 2>&1 &
SERVER_PID=$!

for _ in $(seq 1 30); do
  if curl --fail --silent "$BASE_URL/" >/dev/null 2>&1; then
    break
  fi
  if ! kill -0 "$SERVER_PID" 2>/dev/null; then
    cat "$LOG_FILE" >&2
    exit 1
  fi
  sleep 1
done

assert_status() {
  local expected="$1"
  local path="$2"
  shift 2
  local actual
  actual="$(curl --silent --output /dev/null --write-out '%{http_code}' "$@" "$BASE_URL$path")"
  if [[ "$actual" != "$expected" ]]; then
    echo "Expected $path to return $expected, got $actual" >&2
    cat "$LOG_FILE" >&2
    exit 1
  fi
}

# A stale cookie must never prevent users from reaching authentication pages.
assert_status 200 /login --header 'Cookie: lawscout_auth_token=expired-token'
assert_status 200 /register --header 'Cookie: lawscout_auth_token=expired-token'

# Protected pages must still require a cookie.
assert_status 307 /profile

echo "Authentication routing regression checks passed."
