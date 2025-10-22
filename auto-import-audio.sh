#!/bin/bash
#
# Auto-import audio files from audio-reviews folder into Books app
# Run this script whenever you want to import new audio files
#

AUDIO_DIR="/Users/bgerby/Documents/dev/ai/audio-reviews"
IMPORTED_LOG="$AUDIO_DIR/.imported_files.log"

# Create log file if it doesn't exist
touch "$IMPORTED_LOG"

echo "Checking for new audio files in $AUDIO_DIR..."

# Find all MP3 files
find "$AUDIO_DIR" -name "*.mp3" | while read -r file; do
    # Check if file has already been imported
    if grep -q "$file" "$IMPORTED_LOG"; then
        echo "  Already imported: $(basename "$file")"
    else
        echo "  Importing: $(basename "$file")"

        # Import into Books app using AppleScript
        osascript <<EOF
tell application "Books"
    try
        open POSIX file "$file"
        delay 1
    on error errMsg
        display dialog "Error importing file: " & errMsg
    end try
end tell
EOF

        # Mark as imported
        echo "$file" >> "$IMPORTED_LOG"
        echo "  ✓ Imported successfully"
    fi
done

echo ""
echo "Import complete!"
echo "Audio files are now in Books app → Audiobooks section"
