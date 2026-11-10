#!/bin/bash
# Pulls the latest kiosk content from GitHub and applies it.
#   - Run every minute by the com.computingkiosk.sync LaunchAgent.
#   - Run by the "Check for updates" button on the landing screen (server.py).
# The repo is the source of truth: local tracked files are reset to match it.
# votes.json is runtime data written by the server, so it is preserved.
# The last line of stdout is always RESULT:<current|updated|updated-restart|offline|error: ...>.
# The page reloads itself when it notices the served version change, so this
# script never has to poke Chrome.
set -u

# launchd starts agents with a minimal PATH; make sure git, python3 and the
# python.org / Homebrew installs are all findable.
export PATH="/usr/local/bin:/opt/homebrew/bin:/Library/Frameworks/Python.framework/Versions/Current/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

# Never wait on a password prompt, and give up on a stalled connection.
export GIT_TERMINAL_PROMPT=0 GIT_HTTP_LOW_SPEED_LIMIT=1000 GIT_HTTP_LOW_SPEED_TIME=20

HUB_DIR="$(cd "$(dirname "$0")" && pwd)"
BRANCH="${KIOSK_BRANCH:-main}"
LABEL="com.computingkiosk.launch-kiosk"
PYTHON="${PYTHON:-python3}"
NO_RESTART="${KIOSK_NO_RESTART:-}"   # set by server.py, which restarts itself
cd "$HUB_DIR" || exit 1

log() { echo "$(date '+%Y-%m-%d %H:%M:%S') $*"; }
result() { echo "RESULT:$*"; }

# Heartbeat: shows the job is actually running, even when nothing changed.
{ date '+%Y-%m-%d %H:%M:%S' > "$HOME/Library/Logs/com.computingkiosk.sync.lastcheck"; } 2>/dev/null

# Offline or GitHub unreachable: say why, and try again next time.
if ! FETCH_ERR="$(git fetch --quiet origin "$BRANCH" 2>&1)"; then
    log "fetch failed: ${FETCH_ERR:-unknown error}"
    if grep -qiE "could not resolve|failed to connect|could not connect|network is unreachable|no route to host|timed out|timeout|too slow|connection reset|name resolution|unexpected disconnect|early eof" <<<"$FETCH_ERR"; then
        result offline
    else
        result "error: $(head -n 1 <<<"${FETCH_ERR:-unknown error}")"
    fi
    exit 0
fi

LOCAL="$(git rev-parse HEAD)"
REMOTE="$(git rev-parse "origin/$BRANCH")"
if [[ "$LOCAL" == "$REMOTE" ]]; then
    result current
    exit 0
fi

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
for step in scan_and_build.py python_scan.py webapp_scan.py snippet_scan.py cache_remote_images.py; do
    [[ -f "$step" ]] && "$PYTHON" "$step"
done

if grep -qE '^(server\.py|launch_kiosk\.command|scan_and_build\.py|python_scan\.py|webapp_scan\.py)$' <<<"$CHANGED"; then
    if [[ -z "$NO_RESTART" ]]; then
        log "Server or launcher changed: restarting the kiosk"
        launchctl kickstart -k "gui/$(id -u)/$LABEL" 2>/dev/null || true
    fi
    log "Done (restart needed)"
    result updated-restart
else
    log "Done"
    result updated
fi
