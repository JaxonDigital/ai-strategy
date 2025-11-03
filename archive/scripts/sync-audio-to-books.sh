#!/bin/bash
# Sync audio files from audio-reviews folder to Mac Books app
# This makes them available in Books app on Mac and syncs to iPhone

AUDIO_SOURCE="/Users/bgerby/Documents/dev/ai/audio-reviews"
BOOKS_AUDIOBOOKS="$HOME/Library/Containers/com.apple.BKAgentService/Data/Documents/iBooks/Books/Audiobooks"

echo "Syncing audio files to Books app..."
echo "Source: $AUDIO_SOURCE"
echo "Target: $BOOKS_AUDIOBOOKS"
echo ""

# Copy all GAT MP3 files (excluding temp/chunk files)
for file in "$AUDIO_SOURCE"/GAT-*.mp3; do
    # Skip temp/chunk files
    if [[ "$file" == *".temp."* ]] || [[ "$file" == *".chunk"* ]]; then
        continue
    fi

    filename=$(basename "$file")

    # Check if file already exists in Books
    # Books stores files in SHA1-named folders, so we'll just copy to root
    # and let Books organize it
    if [ -f "$file" ]; then
        echo "Adding: $filename"
        open -a Books "$file"
        sleep 1  # Give Books time to import
    fi
done

echo ""
echo "✓ Sync complete!"
echo "Files should now appear in Books app on Mac"
echo "They will sync to iPhone when you connect or use wireless sync"
