#!/bin/bash
set -euo pipefail

# A LaunchAgent is preferred over an osascript login item here: it starts in the
# user's GUI session and can be inspected, replaced, and removed deterministically.

if [[ "$(uname -s)" != "Darwin" ]]; then
    echo "setup_autostart.command must be run on macOS." >&2
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LAUNCHER="$SCRIPT_DIR/launch_kiosk.command"
LABEL="com.computingkiosk.launch-kiosk"
AGENTS_DIR="$HOME/Library/LaunchAgents"
PLIST_PATH="$AGENTS_DIR/$LABEL.plist"
USER_ID="$(id -u)"

if [[ ! -x "$LAUNCHER" ]]; then
    echo "Launcher is missing or not executable: $LAUNCHER" >&2
    exit 1
fi

mkdir -p "$AGENTS_DIR"
chmod +x "$LAUNCHER"

cat > "$PLIST_PATH" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$LABEL</string>
    <key>ProgramArguments</key>
    <array>
        <string>$LAUNCHER</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>WorkingDirectory</key>
    <string>$SCRIPT_DIR</string>
    <key>StandardOutPath</key>
    <string>$HOME/Library/Logs/com.computingkiosk.launch-kiosk.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/Library/Logs/com.computingkiosk.launch-kiosk.error.log</string>
</dict>
</plist>
EOF

# Replace the existing job when present, preventing duplicate registrations.
if launchctl print "gui/$USER_ID/$LABEL" >/dev/null 2>&1; then
    launchctl bootout "gui/$USER_ID/$LABEL"
fi
launchctl bootstrap "gui/$USER_ID" "$PLIST_PATH"

echo "Registered $LABEL for login:"
launchctl print "gui/$USER_ID/$LABEL" >/dev/null
echo "  $PLIST_PATH"