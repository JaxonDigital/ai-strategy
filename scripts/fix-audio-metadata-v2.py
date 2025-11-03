#!/usr/bin/env python3
"""
Fix metadata on existing audio files with actual Medium article titles and authors.
"""

import subprocess
import re
from pathlib import Path

AUDIO_DIR = Path("/Users/bgerby/Documents/dev/ai/audio-reviews")
ANALYSIS_DIR = Path("/tmp")
PDF_DIRS = [
    Path("/Users/bgerby/Documents/dev/ai/pdfs/medium-articles-2025-10-16"),
    Path("/Users/bgerby/Documents/dev/ai/pdfs/medium-articles-2025-10-17"),
]

def extract_title_and_author(pdf_path):
    """Extract article title and author from PDF."""
    try:
        result = subprocess.run(
            ['pdftotext', str(pdf_path), '-'],
            capture_output=True,
            text=True,
            check=True
        )
        text = result.stdout

        # Extract title - usually appears after publication name, before "min read"
        # Pattern: Publication name · Follow (optional)\n\nTitle\nXX min read · Date\nAuthor

        # Look for the article title (between publication header and "min read")
        title_match = re.search(
            r'(?:· Follow publication|Follow)\s*\n\s*\n(.+?)\n\s*\d+\s+min read',
            text,
            re.DOTALL
        )

        if title_match:
            title = title_match.group(1).strip()
            # Clean up any remaining newlines within title
            title = ' '.join(title.split())
        else:
            # Fallback: try to find text before "min read"
            title_match = re.search(r'(.+?)\n\s*\d+\s+min read', text)
            title = title_match.group(1).strip() if title_match else "Unknown Title"
            title = ' '.join(title.split())

        # Extract author - appears after "min read · Date"
        author_match = re.search(
            r'\d+\s+min read\s+·\s+[A-Z][a-z]+\s+\d+,\s+\d+\s*\n\s*([^\n]+)',
            text
        )

        if author_match:
            author = author_match.group(1).strip()
            # Remove "Follow", "Listen", "Share" etc that might appear
            author = re.sub(r'\s*(Follow|Listen|Share|More)\s*$', '', author)
        else:
            author = "Unknown Author"

        return title, author

    except Exception as e:
        print(f"Error extracting from PDF: {e}")
        return None, None

def find_pdf_for_gat(gat_number):
    """Find the PDF file for a GAT number."""
    for pdf_dir in PDF_DIRS:
        if not pdf_dir.exists():
            continue
        # Look for files starting with GAT-{number}
        matches = list(pdf_dir.glob(f"GAT-{gat_number}-*.pdf"))
        if matches:
            return matches[0]  # Return first match
    return None

def get_star_rating(gat_number):
    """Get star rating from analysis file."""
    analysis_file = ANALYSIS_DIR / f"gat-{gat_number}-analysis.txt"

    if not analysis_file.exists():
        return None

    try:
        with open(analysis_file, 'r') as f:
            content = f.read()

        match = re.search(r'## Relevance to Jaxon Digital: (\d)/5 stars', content)
        return int(match.group(1)) if match else 0
    except:
        return None

def fix_metadata(mp3_path):
    """Update metadata on existing MP3 file with real title and author."""
    # Extract GAT number from filename
    match = re.match(r'GAT-(\d+)', mp3_path.stem)
    if not match:
        print(f"Skipping {mp3_path.name}: No GAT number found")
        return False

    gat_number = match.group(1)

    # Get star rating
    star_rating = get_star_rating(gat_number)
    if star_rating is None:
        print(f"Skipping GAT-{gat_number}: No analysis found")
        return False

    # Find PDF file
    pdf_path = find_pdf_for_gat(gat_number)
    if not pdf_path:
        print(f"Skipping GAT-{gat_number}: PDF not found")
        return False

    # Extract title and author
    title, author = extract_title_and_author(pdf_path)
    if not title or not author:
        print(f"Skipping GAT-{gat_number}: Could not extract title/author")
        return False

    # Build metadata
    # Title: "GAT-233: AI Agent for DevOps: How to Build an AI Logging Agent from Scratch"
    # Album: Same as title (so each is separate audiobook)
    # Artist: Author name
    # Album Artist: "Medium Articles"
    # Comment: "Relevance: 5/5 stars"

    full_title = f"GAT-{gat_number}: {title}"
    album_name = full_title  # Each article is its own album/book

    print(f"\nFixing metadata for {mp3_path.name}...")
    print(f"  Title: {full_title}")
    print(f"  Author: {author}")
    print(f"  Rating: {star_rating}/5 stars")

    # Create temp file for updated version
    temp_mp3 = mp3_path.parent / f"{mp3_path.stem}.fixed.mp3"

    try:
        # Update metadata using ffmpeg
        subprocess.run([
            'ffmpeg', '-i', str(mp3_path),
            '-acodec', 'copy',  # Don't re-encode, just update metadata
            '-metadata', f'title={full_title}',
            '-metadata', f'album={album_name}',
            '-metadata', f'artist={author}',
            '-metadata', 'album_artist=Medium Articles',
            '-metadata', 'track=1',
            '-metadata', f'comment=Relevance: {star_rating}/5 stars',
            '-metadata', 'genre=Podcast',
            '-y',
            str(temp_mp3)
        ], check=True, capture_output=True)

        # Replace original with fixed version
        mp3_path.unlink()
        temp_mp3.rename(mp3_path)

        print(f"  ✓ Fixed")
        return True

    except subprocess.CalledProcessError as e:
        print(f"  ✗ Error: {e}")
        if temp_mp3.exists():
            temp_mp3.unlink()
        return False

def main():
    """Fix metadata on all MP3 files."""
    print("Fixing Audio Metadata with Medium Titles & Authors")
    print("=" * 60)
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

    print(f"Found {len(mp3_files)} MP3 files to fix\n")

    success_count = 0
    error_count = 0

    for mp3_path in mp3_files:
        if fix_metadata(mp3_path):
            success_count += 1
        else:
            error_count += 1

    print(f"\n{'=' * 60}")
    print(f"Summary:")
    print(f"  Fixed: {success_count}")
    print(f"  Errors: {error_count}")
    print(f"\nMetadata updated with real Medium titles and authors!")

if __name__ == '__main__':
    main()
