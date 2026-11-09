#!/bin/bash
# Pulls the latest kiosk content from GitHub and applies it. Run every minute by
# the com.computingkiosk.sync LaunchAgent (see setup_autosync.command).
# The repo is the source of truth: local tracked files are reset to match it.
# votes.json is runtime data written by the server, so it is preserved.
set -u

HUB_DIR="$(cd "$(dirname "$0")" && pwd)"
BRANCH="${KIOSK_BRANCH:-main}"
LABEL="com.computingkiosk.launch-kiosk"
cd "$HUB_DIR" || exit 1

log() { echo "$(date '+%Y-%m-%d %H:%M:%S') $*"; }

# Offline or GitHub unreachable: do nothing and try again next tick.
if ! git fetch --quiet origin "$BRANCH" 2>/dev/null; then
    exit 0
fi

LOCAL="$(git rev-parse HEAD)"
REMOTE="$(git rev-parse "origin/$BRANCH")"
[[ "$LOCAL" == "$REMOTE" ]] && exit 0

log "Updating ${LOCAL:0:7} -> ${REMOTE:0:7}"
CHANGED="$(git diff --name-only "$LOCAL" "$REMOTE")"

VOTES_BACKUP=""
if [[ -f votes.json ]]; then
    VOTES_BACKUP="$(mktemp)"
    cp votes.json "$VOTES_BACKUP"
fi

git reset --hard --quiet "origin/$BRANCH"

if [[ -n "$VOTES_BACKUP" ]]; then
    cp "$VOTES_BACKUP" votes.json
    rm -f "$VOTES_BACKUP"
fi

# Rebuild the lists from whatever arrived (no-ops when nothing is new). Same
# steps as start.command; each is skipped if the repo doesn't have it.
for step in scan_and_build.py python_scan.py webapp_scan.py cache_remote_images.py; do
    [[ -f "$step" ]] && python3 "$step"
done

if grep -qE '^(server\.py|launch_kiosk\.command|scan_and_build\.py|python_scan\.py|webapp_scan\.py)$' <<<"$CHANGED"; then
    log "Server or launcher changed: restarting the kiosk"
    launchctl kickstart -k "gui/$(id -u)/$LABEL" 2>/dev/null || true
elif command -v osascript >/dev/null 2>&1; then
    log "Reloading Chrome"
    osascript -e 'tell application "Google Chrome" to reload active tab of front window' 2>/dev/null || true
fi

log "Done"
