#!/usr/bin/env python3
"""
Combined News Sources Monitor

Unified script to monitor and process articles from multiple sources:
1. Medium daily digest (email parsing)
2. Optimizely World blog (RSS feed)
3. FreeCodeCamp blog (RSS feed)
4. Anthropic news (web scraping)

This script orchestrates the complete workflow:
- Extract/scrape articles from all sources
- Upload PDFs to Google Drive
- Create JIRA tickets with PDF links
- Generate unified relevance assessment
- Generate audio for HIGH priority articles
- Update JIRA with assessments and audio links
- Publish RSS podcast feed

Usage:
    # Process all sources with PDFs ready
    python3 scripts/monitor-all-news-sources.py \\
        --medium-email ~/Desktop/digest.eml \\
        --medium-pdfs ~/Desktop/medium-articles-2025-11-01/ \\
        --optimizely-pdfs ~/Desktop/optimizely-articles-2025-11-01/ \\
        --anthropic-pdfs ~/Desktop/anthropic-news-2025-11-01/

    # Dry run to preview
    python3 scripts/monitor-all-news-sources.py --dry-run

    # Medium only
    python3 scripts/monitor-all-news-sources.py \\
        --medium-email ~/Desktop/digest.eml \\
        --medium-pdfs ~/Desktop/medium-articles-2025-11-01/
"""

import argparse
import fcntl
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Script paths
SCRIPTS_DIR = Path(__file__).parent
EXTRACT_MEDIUM = SCRIPTS_DIR / "extract-medium-articles.py"
MONITOR_OPTIMIZELY = SCRIPTS_DIR / "monitor-optimizely-blog.py"
MONITOR_FREECODECAMP = SCRIPTS_DIR / "monitor-freecodecamp-blog.py"
SCRAPE_ANTHROPIC = SCRIPTS_DIR / "anthropic-scraper.py"
GENERATE_ASSESSMENT = SCRIPTS_DIR / "generate-article-assessment.py"
GENERATE_AUDIO = SCRIPTS_DIR / "generate-audio-from-assessment.py"
GENERATE_RECOMMENDATIONS = SCRIPTS_DIR / "generate-medium-recommendations.py"

# Temp directory for JSON outputs
TEMP_DIR = Path("/tmp")


def run_command(cmd, description, dry_run=False):
    """Run a command and handle errors."""
    print(f"\n{'=' * 60}")
    print(f"📍 {description}")
    print(f"{'=' * 60}")

    if dry_run:
        print(f"[DRY RUN] Would run: {' '.join(cmd)}")
        return True

    print(f"Running: {' '.join(cmd)}\n")

    try:
        result = subprocess.run(cmd, check=True)
        print(f"\n✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ {description} failed with exit code {e.returncode}")
        return False
    except Exception as e:
        print(f"\n✗ {description} failed: {e}")
        return False


def process_medium(email_path, pdf_dir, dry_run=False):
    """Process Medium articles from email digest."""
    if not email_path:
        print("⊘ Skipping Medium (no email provided)")
        return None

    output_json = TEMP_DIR / f"medium-articles-{datetime.now().strftime('%Y-%m-%d')}.json"

    cmd = [
        "python3", str(EXTRACT_MEDIUM),
        email_path,
        "--create-tickets",
        "--output-json", str(output_json)
    ]

    if pdf_dir:
        cmd.extend(["--upload-to-drive", pdf_dir])

    if dry_run:
        cmd.append("--dry-run")

    success = run_command(cmd, "Extract Medium Articles", dry_run)

    if success and output_json.exists():
        return str(output_json)
    return None


def process_optimizely(pdf_dir, dry_run=False):
    """Process Optimizely World blog articles."""
    output_json = TEMP_DIR / f"optimizely-articles-{datetime.now().strftime('%Y-%m-%d')}.json"

    cmd = [
        "python3", str(MONITOR_OPTIMIZELY),
        "--output-json", str(output_json)
    ]

    if pdf_dir:
        cmd.extend(["--upload-pdfs", pdf_dir])

    if dry_run:
        cmd.append("--dry-run")

    success = run_command(cmd, "Monitor Optimizely World Blog", dry_run)

    if success and output_json.exists():
        return str(output_json)
    return None


def process_freecodecamp(dry_run=False):
    """Process FreeCodeCamp blog articles (RSS with full text)."""
    output_json = TEMP_DIR / f"freecodecamp-articles-{datetime.now().strftime('%Y-%m-%d')}.json"

    cmd = [
        "python3", str(MONITOR_FREECODECAMP),
        "--output-json", str(output_json)
    ]

    if dry_run:
        cmd.append("--dry-run")

    success = run_command(cmd, "Monitor FreeCodeCamp Blog", dry_run)

    if success and output_json.exists():
        return str(output_json)
    return None


def process_anthropic(pdf_dir, scraped_json, dry_run=False):
    """Process Anthropic news articles."""
    if not scraped_json:
        print("⊘ Skipping Anthropic (no scraped JSON provided)")
        print("   Note: Anthropic has no RSS feed. Use Claude Code to scrape:")
        print("   1. Navigate to https://www.anthropic.com/news")
        print("   2. Extract article data to JSON")
        print("   3. Pass via --anthropic-scraped-json flag")
        return None

    output_json = TEMP_DIR / f"anthropic-news-{datetime.now().strftime('%Y-%m-%d')}.json"

    cmd = [
        "python3", str(SCRAPE_ANTHROPIC),
        "--input-json", scraped_json,
        "--output-json", str(output_json)
    ]

    if dry_run:
        cmd.append("--dry-run")

    success = run_command(cmd, "Process Anthropic News", dry_run)

    if success and output_json.exists():
        return str(output_json)
    return None


def combine_articles(json_files):
    """Combine article data from multiple JSON files."""
    combined = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'sources': [],
        'total_articles': 0,
        'articles': []
    }

    for json_file in json_files:
        if not json_file or not Path(json_file).exists():
            continue

        with open(json_file, 'r') as f:
            data = json.load(f)

        source = data.get('source', 'unknown')
        articles = data.get('articles', [])

        combined['sources'].append(source)
        combined['total_articles'] += len(articles)

        # Add source tag to each article
        for article in articles:
            article['source'] = source

        combined['articles'].extend(articles)

    return combined


def generate_assessment(json_files, pdf_dirs, dry_run=False):
    """Generate unified assessment for all articles."""
    # Combine all PDFs into single directory for assessment
    # (Assessment script expects all PDFs in one dir)

    # For now, use the first PDF directory
    # TODO: Copy all PDFs to temp unified directory
    primary_pdf_dir = None
    for pdf_dir in pdf_dirs:
        if pdf_dir and Path(pdf_dir).exists():
            primary_pdf_dir = pdf_dir
            break

    if not primary_pdf_dir:
        print("⚠️  No PDF directory available for assessment")
        return None

    # Combine JSON files
    combined_json = TEMP_DIR / f"combined-articles-{datetime.now().strftime('%Y-%m-%d')}.json"
    combined_data = combine_articles(json_files)

    with open(combined_json, 'w') as f:
        json.dump(combined_data, f, indent=2)

    # Generate assessment
    output_md = Path.home() / "Documents" / "dev" / "ai" / "assessments" / f"combined-articles-relevance-assessment-{datetime.now().strftime('%Y-%m-%d')}.md"

    cmd = [
        "python3", str(GENERATE_ASSESSMENT),
        primary_pdf_dir,
        str(combined_json),
        str(output_md)
    ]

    # Add OPENAI_API_KEY to environment
    env = os.environ.copy()
    if 'OPENAI_API_KEY' not in env:
        print("⚠️  OPENAI_API_KEY not set. Assessment may fail.")

    success = run_command(cmd, "Generate Combined Assessment", dry_run)

    if success and output_md.exists():
        return str(output_md)
    return None


def generate_audio(pdf_dir, assessment_file, dry_run=False):
    """Generate audio for HIGH priority articles."""
    if not assessment_file or not Path(assessment_file).exists():
        print("⊘ Skipping audio generation (no assessment file)")
        return False

    cmd = [
        "python3", str(GENERATE_AUDIO),
        pdf_dir,
        assessment_file
    ]

    # Add OPENAI_API_KEY to environment
    env = os.environ.copy()
    if 'OPENAI_API_KEY' not in env:
        print("⚠️  OPENAI_API_KEY not set. Audio generation will fail.")

    return run_command(cmd, "Generate Audio for HIGH Priority Articles", dry_run)


def generate_medium_recommendations(assessment_file, metadata_json, pdf_dir, dry_run=False):
    """Generate Medium follow/mute recommendations based on assessment."""
    if not assessment_file or not Path(assessment_file).exists():
        print("⊘ Skipping Medium recommendations (no assessment file)")
        return False

    if not metadata_json or not Path(metadata_json).exists():
        print("⊘ Skipping Medium recommendations (no metadata file)")
        return False

    cmd = [
        "python3", str(GENERATE_RECOMMENDATIONS),
        assessment_file,
        metadata_json
    ]

    if pdf_dir and Path(pdf_dir).exists():
        cmd.append(pdf_dir)

    return run_command(cmd, "Generate Medium Recommendations", dry_run)


def auto_detect_latest_email():
    """Auto-detect the most recent .eml file in inputs/ directory."""
    inputs_dir = Path(__file__).parent.parent / "inputs"

    if not inputs_dir.exists():
        return None

    email_files = sorted(inputs_dir.glob("*.eml"), key=lambda p: p.stat().st_mtime, reverse=True)

    if email_files:
        return str(email_files[0])

    return None


def main():
    parser = argparse.ArgumentParser(
        description='Combined news sources monitor and processor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    # Medium arguments
    parser.add_argument('--medium-email', type=str,
                        help='Path to Medium daily digest .eml file (auto-detects latest from inputs/ if not provided)')
    parser.add_argument('--medium-pdfs', type=str,
                        help='Directory containing Medium article PDFs')

    # Optimizely arguments
    parser.add_argument('--optimizely-pdfs', type=str,
                        help='Directory containing Optimizely article PDFs')

    # FreeCodeCamp arguments
    parser.add_argument('--freecodecamp', action='store_true',
                        help='Monitor FreeCodeCamp blog (RSS feed, no PDFs needed)')

    # Anthropic arguments
    parser.add_argument('--anthropic-scraped-json', type=str,
                        help='JSON file with scraped Anthropic news data')
    parser.add_argument('--anthropic-pdfs', type=str,
                        help='Directory containing Anthropic news PDFs')

    # General options
    parser.add_argument('--dry-run', action='store_true',
                        help='Preview actions without executing')
    parser.add_argument('--skip-assessment', action='store_true',
                        help='Skip assessment generation')
    parser.add_argument('--skip-audio', action='store_true',
                        help='Skip audio generation')

    args = parser.parse_args()

    # Auto-detect email if not provided
    if not args.medium_email:
        auto_email = auto_detect_latest_email()
        if auto_email:
            args.medium_email = auto_email
            print(f"🔍 Auto-detected Medium email: {auto_email}")

    # Validate inputs
    if not any([args.medium_email, args.optimizely_pdfs, args.freecodecamp, args.anthropic_scraped_json]):
        print("❌ Error: No sources specified. Provide at least one of:")
        print("   --medium-email, --optimizely-pdfs, --freecodecamp, or --anthropic-scraped-json")
        sys.exit(1)

    # Prevent concurrent execution with lockfile
    lock_file_path = '/tmp/monitor-all-news-sources.lock'
    lock_file = open(lock_file_path, 'w')

    try:
        # Try to acquire exclusive lock (non-blocking)
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print("❌ Error: Another instance of this script is already running")
        print(f"   Lock file: {lock_file_path}")
        print("   If no other instance is running, remove the lock file manually")
        sys.exit(1)

    # Lock will be automatically released when script exits (or file closes)

    print("\n" + "=" * 60)
    print("📰 COMBINED NEWS SOURCES MONITOR")
    print("=" * 60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Show what will be processed
    print("\nSources to process:")
    if args.medium_email:
        print(f"  ✓ Medium (email: {args.medium_email})")
    if args.optimizely_pdfs or not any([args.medium_email, args.freecodecamp, args.anthropic_scraped_json]):
        print(f"  ✓ Optimizely World Blog (RSS)")
    if args.freecodecamp:
        print(f"  ✓ FreeCodeCamp Blog (RSS)")
    if args.anthropic_scraped_json:
        print(f"  ✓ Anthropic News (scraped: {args.anthropic_scraped_json})")

    # Process each source
    json_files = []
    pdf_dirs = []

    # Medium
    if args.medium_email:
        medium_json = process_medium(args.medium_email, args.medium_pdfs, args.dry_run)
        if medium_json:
            json_files.append(medium_json)
        if args.medium_pdfs:
            pdf_dirs.append(args.medium_pdfs)

    # Optimizely
    optimizely_json = process_optimizely(args.optimizely_pdfs, args.dry_run)
    if optimizely_json:
        json_files.append(optimizely_json)
    if args.optimizely_pdfs:
        pdf_dirs.append(args.optimizely_pdfs)

    # FreeCodeCamp
    if args.freecodecamp:
        freecodecamp_json = process_freecodecamp(args.dry_run)
        if freecodecamp_json:
            json_files.append(freecodecamp_json)
        # Note: FreeCodeCamp articles have text in JSON, no PDFs needed

    # Anthropic
    if args.anthropic_scraped_json:
        anthropic_json = process_anthropic(args.anthropic_pdfs, args.anthropic_scraped_json, args.dry_run)
        if anthropic_json:
            json_files.append(anthropic_json)
        if args.anthropic_pdfs:
            pdf_dirs.append(args.anthropic_pdfs)

    # Generate unified assessment
    assessment_file = None
    if not args.skip_assessment and json_files:
        assessment_file = generate_assessment(json_files, pdf_dirs, args.dry_run)

    # Generate audio
    if not args.skip_audio and assessment_file and pdf_dirs:
        # Use first PDF directory with content
        primary_pdf_dir = pdf_dirs[0] if pdf_dirs else None
        if primary_pdf_dir:
            generate_audio(primary_pdf_dir, assessment_file, args.dry_run)

    # Generate Medium recommendations (if Medium was processed)
    if medium_json and assessment_file and args.medium_pdfs:
        generate_medium_recommendations(
            assessment_file,
            medium_json,
            args.medium_pdfs,
            args.dry_run
        )

    # Final summary
    print("\n" + "=" * 60)
    print("✅ PROCESSING COMPLETE")
    print("=" * 60)

    if json_files:
        print(f"\nArticle metadata files:")
        for json_file in json_files:
            print(f"  • {json_file}")

    if assessment_file:
        print(f"\nAssessment file:")
        print(f"  • {assessment_file}")

    print("\nNext steps:")
    print("  1. Review JIRA tickets in GAT project")
    print("  2. Listen to generated audio files (if any)")
    print("  3. Check podcast feed updates (if audio generated)")

    if not args.dry_run:
        print("\n💡 Tip: Use --dry-run flag to preview before executing")


if __name__ == '__main__':
    main()
