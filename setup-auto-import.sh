#!/bin/bash
#
# Setup automatic audio import to Books app
# This creates a LaunchAgent that runs every hour
#

LAUNCH_AGENT_DIR="$HOME/Library/LaunchAgents"
PLIST_FILE="$LAUNCH_AGENT_DIR/com.jaxon.audio-import.plist"
SCRIPT_PATH="/Users/bgerby/Documents/dev/ai/auto-import-audio.sh"

mkdir -p "$LAUNCH_AGENT_DIR"

cat > "$PLIST_FILE" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.jaxon.audio-import</string>

    <key>ProgramArguments</key>
    <array>
        <string>$SCRIPT_PATH</string>
    </array>

    <key>StartInterval</key>
    <integer>3600</integer>

    <key>RunAtLoad</key>
    <true/>

    <key>StandardOutPath</key>
    <string>/tmp/audio-import.log</string>

    <key>StandardErrorPath</key>
    <string>/tmp/audio-import-error.log</string>
</dict>
</plist>
EOF

echo "LaunchAgent created at: $PLIST_FILE"
echo ""
echo "To enable automatic import (runs every hour):"
echo "  launchctl load $PLIST_FILE"
echo ""
echo "To disable automatic import:"
echo "  launchctl unload $PLIST_FILE"
echo ""
echo "To run manually anytime:"
echo "  $SCRIPT_PATH"
