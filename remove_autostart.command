#!/bin/bash
set -euo pipefail

if [[ "$(uname -s)" != "Darwin" ]]; then
    echo "remove_autostart.command must be run on macOS." >&2
    exit 1
fi

LABEL="com.computingkiosk.launch-kiosk"
PLIST_PATH="$HOME/Library/LaunchAgents/$LABEL.plist"
USER_ID="$(id -u)"

launchctl bootout "gui/$USER_ID/$LABEL" 2>/dev/null || true
if [[ -e "$PLIST_PATH" ]]; then
    rm "$PLIST_PATH"
fi

echo "Removed $LABEL and deleted $PLIST_PATH."