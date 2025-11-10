#!/usr/bin/env python3.11
"""
Update metadata for existing audio files with relevance summaries.

This script:
1. Reads all assessment files to extract relevance summaries by article number
2. Reads JSON files to map article numbers to ticket IDs
3. Finds corresponding audio files in audio-reviews/
4. Updates the MP3 comment field with the relevance summary
5. Preserves all other metadata (title, artist, album, etc.)

Usage:
    # Update all audio files
    python3.11 scripts/update-existing-audio-metadata.py

    # Dry run (show what would be done)
    python3.11 scripts/update-existing-audio-metadata.py --dry-run

    # Update specific tickets
    python3.11 scripts/update-existing-audio-metadata.py GAT-321 GAT-322 GAT-323
"""

import os
import re
import subprocess
import argparse
import json
from pathlib import Path
from typing import Dict, Optional, Tuple
from glob import glob

# Paths
ASSESSMENTS_DIR = "/Users/bgerby/Documents/dev/ai/assessments"
AUDIO_DIR = "/Users/bgerby/Documents/dev/ai/audio-reviews"
JSON_DIR = "/tmp"  # JSON files from extract-medium-articles.py

def extract_date_from_filename(filename: str) -> Optional[str]:
    """Extract date from assessment filename (YYYY-MM-DD format)."""
    # Match formats like: medium-articles-relevance-assessment-2025-10-29.md
    # or: optimizely-articles-relevance-assessment-2025-10-23.md
    match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    return match.group(1) if match else None

def load_json_metadata(date: str) -> Dict[int, str]:
    """Load article number to ticket ID mapping from JSON file."""
    # Try multiple JSON filename patterns
    json_patterns = [
        f"medium-articles-{date}.json",
        f"medium-articles-{date.replace('-', '-')}.json",
        f"optimizely-articles-{date}.json"
    ]

    for pattern in json_patterns:
        json_path = os.path.join(JSON_DIR, pattern)
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                data = json.load(f)
                # Build mapping: article number -> ticket ID
                mapping = {}
                for article in data.get('articles', []):
                    num = article.get('number')
                    ticket = article.get('ticket_id')
                    if num and ticket:
                        mapping[num] = ticket
                return mapping

    return {}

def extract_article_data_from_assessment(assessment_path: str) -> Tuple[Dict[str, dict], int]:
    """Extract article data (article number, relevance) from assessment file."""
    articles_by_number = {}
    article_count = 0

    with open(assessment_path, 'r') as f:
        content = f.read()

    # Split by article sections (### ARTICLE-NN format)
    # Example: ### ARTICLE-04 - Claude Code V2 0 28
    sections = re.split(r'\n### ARTICLE-(\d+)', content)

    # Process pairs of (article_number, section_content)
    for i in range(1, len(sections), 2):
        article_num = int(sections[i])
        section = sections[i + 1]
        article_count += 1

        # Extract relevance summary (everything after "**Relevance Summary:**" until next **section)
        relevance_match = re.search(
            r'\*\*Relevance Summary:\*\*\s*(.*?)(?=\n\*\*|$)',
            section,
            re.DOTALL | re.IGNORECASE
        )

        if relevance_match:
            relevance = relevance_match.group(1).strip()
            # Remove any markdown formatting
            relevance = re.sub(r'\*\*', '', relevance)
            relevance = re.sub(r'\n+', ' ', relevance)
            relevance = relevance.strip()

            # Truncate if too long (RSS readers limit to ~200 chars)
            if len(relevance) > 200:
                relevance = relevance[:197] + "..."

            articles_by_number[article_num] = {
                'article_number': article_num,
                'relevance_summary': relevance
            }

    return articles_by_number, article_count

def query_jira_for_title(ticket_id: str) -> Optional[str]:
    """Query JIRA to get article title from ticket summary."""
    try:
        token_path = os.path.expanduser("~/.jira.d/.pass")
        with open(token_path, 'r') as f:
            token = f.read().strip()

        env = os.environ.copy()
        env["JIRA_API_TOKEN"] = token

        result = subprocess.run(
            ['jira', 'issue', 'view', ticket_id],
            env=env,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            # Extract summary (format: "Review: Article Title")
            match = re.search(r'Summary:\s*Review:\s*(.+)', result.stdout)
            if match:
                return match.group(1).strip()
    except Exception:
        pass

    return None

def match_article_by_title(title_from_jira: str, assessment_file: str, articles_by_num: Dict[int, dict]) -> Optional[int]:
    """Try to match JIRA title to article in assessment by comparing titles."""
    # Normalize title for comparison
    normalized_jira = re.sub(r'[^a-z0-9]+', '', title_from_jira.lower())

    with open(assessment_file, 'r') as f:
        content = f.read()

    # Find article sections with titles
    # Format: ### ARTICLE-04 - Claude Code V2 0 28
    for article_num in articles_by_num.keys():
        pattern = rf'### ARTICLE-{article_num:02d}\s*-\s*([^\n]+)'
        match = re.search(pattern, content)
        if match:
            article_title = match.group(1).strip()
            normalized_article = re.sub(r'[^a-z0-9]+', '', article_title.lower())

            # Fuzzy match (at least 70% overlap)
            if normalized_jira in normalized_article or normalized_article in normalized_jira:
                return article_num

    return None

def get_all_article_data() -> Dict[str, dict]:
    """Load all article data from all assessment files and JSON metadata."""
    all_articles_by_ticket = {}

    # Find all assessment files
    assessment_files = glob(os.path.join(ASSESSMENTS_DIR, "*-relevance-assessment-*.md"))

    print(f"Loading data from {len(assessment_files)} assessment files...\n")

    # First pass: Load data from JSON files
    for assessment_file in assessment_files:
        basename = os.path.basename(assessment_file)

        # Extract date from filename
        date = extract_date_from_filename(basename)
        if not date:
            print(f"  ⚠ {basename}: Could not extract date")
            continue

        # Load JSON metadata for this date
        json_mapping = load_json_metadata(date)

        # Extract article data from assessment
        articles_by_num, total = extract_article_data_from_assessment(assessment_file)

        # Map article numbers to ticket IDs
        matched_count = 0
        for article_num, article_data in articles_by_num.items():
            ticket_id = json_mapping.get(article_num)
            if ticket_id:
                all_articles_by_ticket[ticket_id] = article_data
                matched_count += 1

        print(f"  {basename}")
        print(f"    Date: {date}")
        print(f"    Articles: {total}")
        print(f"    JSON matched: {matched_count}")
        if matched_count < total:
            print(f"    ⚠ {total - matched_count} articles need JIRA fallback")
        print()

    json_matched = len(all_articles_by_ticket)

    # Second pass: Use JIRA fallback for unmatched articles
    print(f"\nPhase 2: Querying JIRA for missing mappings...\n")

    # Get all audio files to find ticket numbers
    audio_files = glob(os.path.join(AUDIO_DIR, "GAT-*.mp3"))
    ticket_numbers = set()
    for audio_file in audio_files:
        match = re.search(r'GAT-(\d+)', os.path.basename(audio_file))
        if match:
            ticket_numbers.add(f"GAT-{match.group(1)}")

    # Query JIRA for tickets not yet matched
    unmatched_tickets = ticket_numbers - set(all_articles_by_ticket.keys())

    jira_matched = 0
    for ticket_id in sorted(unmatched_tickets):
        # Get title from JIRA
        title = query_jira_for_title(ticket_id)
        if not title:
            continue

        # Try to match against assessment files
        for assessment_file in assessment_files:
            articles_by_num, _ = extract_article_data_from_assessment(assessment_file)
            article_num = match_article_by_title(title, assessment_file, articles_by_num)

            if article_num and article_num in articles_by_num:
                all_articles_by_ticket[ticket_id] = articles_by_num[article_num]
                jira_matched += 1
                print(f"  ✓ {ticket_id}: Matched via JIRA title")
                break

    print(f"\nMatching Summary:")
    print(f"  JSON matched: {json_matched}")
    print(f"  JIRA matched: {jira_matched}")
    print(f"  Total: {len(all_articles_by_ticket)}\n")

    return all_articles_by_ticket

def get_current_metadata(audio_path: str) -> Optional[Dict[str, str]]:
    """Extract current metadata from MP3 file."""
    try:
        result = subprocess.run([
            'ffprobe', '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            str(audio_path)
        ], capture_output=True, text=True, check=True)

        import json
        data = json.loads(result.stdout)
        tags = data.get('format', {}).get('tags', {})

        return {
            'title': tags.get('title', ''),
            'album': tags.get('album', ''),
            'artist': tags.get('artist', ''),
            'album_artist': tags.get('album_artist', ''),
            'track': tags.get('track', ''),
            'comment': tags.get('comment', ''),
            'genre': tags.get('genre', '')
        }
    except Exception as e:
        print(f"  ✗ Error reading metadata: {e}")
        return None

def update_audio_metadata(audio_path: str, new_description: str, dry_run: bool = False) -> bool:
    """Update MP3 file with new description in comment field."""
    if dry_run:
        print(f"  [DRY RUN] Would update comment to: {new_description[:60]}...")
        return True

    # Get current metadata
    metadata = get_current_metadata(audio_path)
    if not metadata:
        return False

    # Create temp file
    temp_path = str(audio_path).replace('.mp3', '.temp.mp3')

    try:
        # Update metadata with ffmpeg
        subprocess.run([
            'ffmpeg', '-i', str(audio_path),
            '-acodec', 'copy',  # Don't re-encode
            '-metadata', f'title={metadata["title"]}',
            '-metadata', f'album={metadata["album"]}',
            '-metadata', f'artist={metadata["artist"]}',
            '-metadata', f'album_artist={metadata["album_artist"]}',
            '-metadata', f'track={metadata["track"]}',
            '-metadata', f'comment={new_description}',  # New description
            '-metadata', f'genre={metadata["genre"]}',
            '-y',
            temp_path
        ], check=True, capture_output=True)

        # Replace original with updated file
        os.replace(temp_path, audio_path)
        return True

    except Exception as e:
        print(f"  ✗ Error updating metadata: {e}")
        # Clean up temp file if it exists
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Update audio file metadata with relevance summaries",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument('tickets', nargs='*',
                       help="Specific ticket numbers to update (e.g., GAT-321). If not provided, updates all.")
    parser.add_argument('--dry-run', action='store_true',
                       help="Show what would be done without making changes")

    args = parser.parse_args()

    print("=" * 60)
    print("Update Audio Metadata with Relevance Summaries")
    print("=" * 60)
    print(f"Dry run: {args.dry_run}")
    print()

    # Load all article data
    article_data = get_all_article_data()

    # Find all audio files
    audio_files = glob(os.path.join(AUDIO_DIR, "GAT-*.mp3"))
    print(f"\nFound {len(audio_files)} audio files\n")

    # Filter by specific tickets if provided
    if args.tickets:
        audio_files = [f for f in audio_files if any(t in f for t in args.tickets)]
        print(f"Filtered to {len(audio_files)} audio files matching: {', '.join(args.tickets)}\n")

    updated_count = 0
    skipped_count = 0
    error_count = 0

    for audio_file in sorted(audio_files):
        filename = os.path.basename(audio_file)
        ticket_match = re.search(r'GAT-(\d+)', filename)

        if not ticket_match:
            print(f"⚠️  {filename}: Could not extract ticket number")
            skipped_count += 1
            continue

        ticket_id = f"GAT-{ticket_match.group(1)}"

        # Get article data
        article = article_data.get(ticket_id)

        if not article:
            print(f"⚠️  {ticket_id}: No assessment data found")
            skipped_count += 1
            continue

        # Get current metadata
        current_metadata = get_current_metadata(audio_file)
        current_description = current_metadata.get('comment', '') if current_metadata else ''

        print(f"\n{ticket_id}:")
        print(f"  Current: {current_description}")
        print(f"  New:     {article['relevance_summary'][:80]}...")

        # Skip if already has the same description
        if current_description == article['relevance_summary']:
            print(f"  ✓ Already up to date")
            skipped_count += 1
            continue

        # Update metadata
        if update_audio_metadata(audio_file, article['relevance_summary'], args.dry_run):
            print(f"  ✓ Updated")
            updated_count += 1
        else:
            print(f"  ✗ Failed")
            error_count += 1

    # Summary
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total audio files: {len(audio_files)}")

    if args.dry_run:
        print(f"Would update: {updated_count}")
    else:
        print(f"Updated: {updated_count}")

    print(f"Skipped (up to date or no data): {skipped_count}")
    print(f"Errors: {error_count}")

    if not args.dry_run and updated_count > 0:
        print(f"\n✓ Next step: Regenerate RSS feed with updated metadata")
        print(f"  cd /Users/bgerby/Documents/dev/ai/jaxon-research-feed")
        print(f"  python3 generate-feed.py")
        print(f"  git add feed.rss && git commit -m 'Update episode descriptions' && git push")

if __name__ == "__main__":
    main()
