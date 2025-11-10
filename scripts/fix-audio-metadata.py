#!/usr/bin/env python3
"""
Fix metadata on existing audio files so each appears as separate audiobook in Books app.
"""

import subprocess
import re
from pathlib import Path

AUDIO_DIR = Path("/Users/bgerby/Documents/dev/ai/audio-reviews")
ANALYSIS_DIR = Path("/tmp")

def get_article_info(gat_number):
    """Get article title and star rating from analysis file."""
    analysis_file = ANALYSIS_DIR / f"gat-{gat_number}-analysis.txt"

    if not analysis_file.exists():
        return None, None

    try:
        with open(analysis_file, 'r') as f:
            content = f.read()

        # Get star rating
        match = re.search(r'## Relevance to Jaxon Digital: (\d)/5 stars', content)
        star_rating = int(match.group(1)) if match else 0

        return star_rating
    except Exception as e:
        print(f"Error reading analysis for GAT-{gat_number}: {e}")
        return None

def fix_metadata(mp3_path):
    """Update metadata on existing MP3 file."""
    # Extract GAT number from filename
    match = re.match(r'GAT-(\d+)', mp3_path.stem)
    if not match:
        print(f"Skipping {mp3_path.name}: No GAT number found")
        return False

    gat_number = match.group(1)
    star_rating = get_article_info(gat_number)

    if star_rating is None:
        print(f"Skipping GAT-{gat_number}: No analysis found")
        return False

    # Create title from filename
    # Format: "GAT-234: qa-agent-without-rag (4/5)"
    article_slug = mp3_path.stem.replace(f'GAT-{gat_number}', '').strip('-')
    if not article_slug:
        article_slug = f"article-{gat_number}"

    title = f"GAT-{gat_number}: {article_slug} ({star_rating}/5)"

    print(f"\nFixing metadata for {mp3_path.name}...")
    print(f"  Title: {title}")
    print(f"  Album: {title}")  # Use same as title so each is separate book
    print(f"  Track: 1")
    print(f"  Rating: {star_rating}/5 stars")

    # Create temp file for updated version
    temp_mp3 = mp3_path.parent / f"{mp3_path.stem}.fixed.mp3"

    try:
        # Update metadata using ffmpeg
        subprocess.run([
            'ffmpeg', '-i', str(mp3_path),
            '-acodec', 'copy',  # Don't re-encode, just update metadata
            '-metadata', f'title={title}',
            '-metadata', f'album={title}',  # Each article is its own album/book
            '-metadata', 'track=1',
            '-metadata', f'comment=Relevance: {star_rating}/5 stars',
            '-metadata', 'genre=Podcast',
            '-y',
            str(temp_mp3)
        ], check=True, capture_output=True)

        # Replace original with fixed version
        mp3_path.unlink()
        temp_mp3.rename(mp3_path)

        print(f"  ✓ Fixed: {mp3_path.name}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"  ✗ Error: {e}")
        if temp_mp3.exists():
            temp_mp3.unlink()
        return False

def main():
    """Fix metadata on all MP3 files."""
    print("Fixing Audio Metadata")
    print("=" * 50)
    print(f"Audio Directory: {AUDIO_DIR}")
    print()

    # Find all GAT MP3 files (not temp/chunk files)
    mp3_files = sorted([
        f for f in AUDIO_DIR.glob("GAT-*.mp3")
        if not any(x in f.name for x in ['.temp.', '.chunk', '.fixed.'])
    ])

    if not mp3_files:
        print("No MP3 files found to fix")
        return

    print(f"Found {len(mp3_files)} MP3 files to fix:\n")

    success_count = 0
    error_count = 0

    for mp3_path in mp3_files:
        if fix_metadata(mp3_path):
            success_count += 1
        else:
            error_count += 1

    print(f"\n{'=' * 50}")
    print(f"Summary:")
    print(f"  Fixed: {success_count}")
    print(f"  Errors: {error_count}")
    print(f"\nEach article should now appear as a separate audiobook in Books app!")

if __name__ == '__main__':
    main()
