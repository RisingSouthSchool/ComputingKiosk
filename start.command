#!/bin/bash
set -u

HUB_DIR="$(cd "$(dirname "$0")" && pwd)"
PORT=8765
cd "$HUB_DIR" || exit 1

echo "Scanning game exports..."
python3 "$HUB_DIR/scan_and_build.py"
echo
echo "Starting the game hub at http://127.0.0.1:$PORT"
python3 -m http.server "$PORT" --directory "$HUB_DIR" &
SERVER_PID=$!
trap 'kill "$SERVER_PID" 2>/dev/null' EXIT INT TERM
open "http://127.0.0.1:$PORT/"
echo "The hub is running. Leave this window open."
wait "$SERVER_PID"