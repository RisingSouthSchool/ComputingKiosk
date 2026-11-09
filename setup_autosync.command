#!/bin/bash
set -euo pipefail

# Registers a LaunchAgent that runs sync_from_repo.sh every 60 seconds.
# Run once from inside the Student Station account, like setup_autostart.command.

if [[ "$(uname -s)" != "Darwin" ]]; then
    echo "setup_autosync.command must be run on macOS." >&2
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC="$SCRIPT_DIR/sync_from_repo.sh"
LABEL="com.computingkiosk.sync"
AGENTS_DIR="$HOME/Library/LaunchAgents"
PLIST_PATH="$AGENTS_DIR/$LABEL.plist"
USER_ID="$(id -u)"

if ! git -C "$SCRIPT_DIR" rev-parse --git-dir >/dev/null 2>&1; then
    echo "$SCRIPT_DIR is not a git clone. Clone the repo first:" >&2
    echo "  git clone https://github.com/RisingSouthSchool/ComputingKiosk" >&2
    exit 1
fi

chmod +x "$SYNC"
mkdir -p "$AGENTS_DIR"

cat > "$PLIST_PATH" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$LABEL</string>
    <key>ProgramArguments</key>
    <array>
        <string>$SYNC</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>StartInterval</key>
    <integer>60</integer>
    <key>WorkingDirectory</key>
    <string>$SCRIPT_DIR</string>
    <key>StandardOutPath</key>
    <string>$HOME/Library/Logs/com.computingkiosk.sync.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/Library/Logs/com.computingkiosk.sync.error.log</string>
</dict>
</plist>
EOF

if launchctl print "gui/$USER_ID/$LABEL" >/dev/null 2>&1; then
    launchctl bootout "gui/$USER_ID/$LABEL"
fi
launchctl bootstrap "gui/$USER_ID" "$PLIST_PATH"

echo "Registered $LABEL (checks GitHub every 60 seconds):"
echo "  $PLIST_PATH"
echo "Log: $HOME/Library/Logs/com.computingkiosk.sync.log"
