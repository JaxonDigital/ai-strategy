#!/usr/bin/env python3
"""
Audit all Medium article assessments to find missing audio files.
Checks HIGH and MEDIUM priority articles against existing MP3s.
"""

import os
import re
from pathlib import Path
from datetime import datetime

ASSESSMENTS_DIR = Path("/Users/bgerby/Documents/dev/ai/assessments")
AUDIO_DIR = Path("/Users/bgerby/Documents/dev/ai/audio-reviews")

def parse_assessment(filepath):
    """Extract HIGH and MEDIUM priority article ticket IDs from assessment."""
    with open(filepath, 'r') as f:
        content = f.read()

    articles = []
    current_priority = None

    # Match both new and old assessment formats
    lines = content.split('\n')
    for i, line in enumerate(lines):
        # Detect priority sections
        if 'HIGH Priority' in line or 'HIGH PRIORITY' in line:
            current_priority = 'HIGH'
        elif 'MEDIUM Priority' in line or 'MEDIUM PRIORITY' in line:
            current_priority = 'MEDIUM'
        elif 'LOW Priority' in line or 'LOW PRIORITY' in line:
            current_priority = None

        # Extract ticket IDs
        if current_priority and ('GAT-' in line or '**Ticket:**' in line):
            # Try multiple patterns
            match = re.search(r'GAT-(\d+)', line)
            if match:
                ticket_id = f"GAT-{match.group(1)}"
                articles.append({
                    'ticket': ticket_id,
                    'priority': current_priority
                })

    return articles

def check_audio_exists(ticket_id):
    """Check if MP3 file exists for given ticket."""
    audio_file = AUDIO_DIR / f"{ticket_id}.mp3"
    return audio_file.exists()

def audit_all_assessments():
    """Audit all Medium article assessments."""
    print("=" * 70)
    print("AUDIO GENERATION AUDIT REPORT")
    print("=" * 70)
    print()

    all_missing = []
    date_summaries = []

    # Find all Medium article assessments
    assessment_files = sorted(ASSESSMENTS_DIR.glob("medium-articles-relevance-assessment-*.md"))

    for filepath in assessment_files:
        # Extract date from filename
        match = re.search(r'(\d{4}-\d{2}-\d{2})', filepath.name)
        if not match:
            continue
        date = match.group(1)

        # Parse assessment
        articles = parse_assessment(filepath)
        if not articles:
            continue

        # Check which ones are missing audio
        missing = []
        found = []
        for article in articles:
            if check_audio_exists(article['ticket']):
                found.append(article)
            else:
                missing.append(article)
                all_missing.append({**article, 'date': date})

        # Summary for this date
        high_total = len([a for a in articles if a['priority'] == 'HIGH'])
        medium_total = len([a for a in articles if a['priority'] == 'MEDIUM'])
        high_missing = len([a for a in missing if a['priority'] == 'HIGH'])
        medium_missing = len([a for a in missing if a['priority'] == 'MEDIUM'])

        date_summaries.append({
            'date': date,
            'high_total': high_total,
            'medium_total': medium_total,
            'high_missing': high_missing,
            'medium_missing': medium_missing,
            'total_should_have': high_total + medium_total,
            'total_found': len(found),
            'total_missing': len(missing),
            'missing_tickets': [a['ticket'] for a in missing]
        })

    # Print summary by date
    print("SUMMARY BY DATE")
    print("-" * 70)
    for summary in date_summaries:
        print(f"\n{summary['date']}:")
        print(f"  Articles: {summary['high_total']} HIGH + {summary['medium_total']} MEDIUM = {summary['total_should_have']} total")
        print(f"  Audio Found: {summary['total_found']}")
        print(f"  Missing: {summary['total_missing']} ({summary['high_missing']} HIGH, {summary['medium_missing']} MEDIUM)")

        if summary['missing_tickets']:
            print(f"  Missing Tickets: {', '.join(summary['missing_tickets'])}")

    # Overall summary
    print("\n" + "=" * 70)
    print("OVERALL SUMMARY")
    print("=" * 70)

    total_should_have = sum(s['total_should_have'] for s in date_summaries)
    total_found = sum(s['total_found'] for s in date_summaries)
    total_missing = sum(s['total_missing'] for s in date_summaries)
    total_high_missing = sum(s['high_missing'] for s in date_summaries)
    total_medium_missing = sum(s['medium_missing'] for s in date_summaries)

    print(f"\nTotal HIGH/MEDIUM articles across all dates: {total_should_have}")
    print(f"Total audio files found: {total_found}")
    print(f"Total missing: {total_missing} ({total_high_missing} HIGH, {total_medium_missing} MEDIUM)")

    if all_missing:
        print(f"\n\nMISSING AUDIO FILES ({len(all_missing)} total):")
        print("-" * 70)

        by_date = {}
        for article in all_missing:
            date = article['date']
            if date not in by_date:
                by_date[date] = []
            by_date[date].append(article)

        for date in sorted(by_date.keys()):
            articles = by_date[date]
            high = [a for a in articles if a['priority'] == 'HIGH']
            medium = [a for a in articles if a['priority'] == 'MEDIUM']

            print(f"\n{date}:")
            if high:
                print(f"  HIGH ({len(high)}): {', '.join(a['ticket'] for a in high)}")
            if medium:
                print(f"  MEDIUM ({len(medium)}): {', '.join(a['ticket'] for a in medium)}")

    print("\n" + "=" * 70)
    print("END OF REPORT")
    print("=" * 70)

    return all_missing, date_summaries

if __name__ == '__main__':
    audit_all_assessments()
