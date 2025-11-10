#!/usr/bin/env python3
"""
Fix missing URLs and add assessments to JIRA tickets.

Uses existing audio-generation-results.json to map tickets to articles,
then updates JIRA with URLs and assessments from the assessment markdown files.

Usage:
    # Audit only
    python3 scripts/fix-missing-urls-and-assessments.py --audit

    # Fix URLs only
    python3 scripts/fix-missing-urls-and-assessments.py --fix-urls

    # Fix assessments only
    python3 scripts/fix-missing-urls-and-assessments.py --fix-assessments

    # Fix everything
    python3 scripts/fix-missing-urls-and-assessments.py --fix-all
"""

import argparse
import json
import os
import re
import subprocess
from pathlib import Path

# Paths
AUDIO_RESULTS_JSON = Path("/Users/bgerby/Documents/dev/ai/audio-reviews/audio-generation-results.json")
ASSESSMENTS_DIR = Path("/Users/bgerby/Documents/dev/ai/assessments")
JIRA_TOKEN_FILE = Path.home() / ".jira.d" / ".pass"

def get_jira_token():
    """Read JIRA API token."""
    return JIRA_TOKEN_FILE.read_text().strip()

def load_audio_results():
    """Load audio generation results JSON."""
    with open(AUDIO_RESULTS_JSON, 'r') as f:
        return json.load(f)

def parse_assessment_file(assessment_path):
    """Parse assessment markdown to extract article data."""
    content = assessment_path.read_text()
    articles = {}

    # Pattern to match article sections
    pattern = r'###\s+ARTICLE-(\d+)\s+-\s+(.+?)$'

    for match in re.finditer(pattern, content, re.MULTILINE):
        article_num = int(match.group(1))
        title = match.group(2).strip()

        # Extract section content
        start_pos = match.end()
        next_match = re.search(r'###\s+ARTICLE-\d+', content[start_pos:])
        if next_match:
            end_pos = start_pos + next_match.start()
        else:
            section_match = re.search(r'\n##\s+', content[start_pos:])
            end_pos = start_pos + section_match.start() if section_match else len(content)

        section_content = content[start_pos:end_pos]

        # Extract URL
        url_match = re.search(r'\*\*Article URL:\*\*\s+(.+?)$', section_content, re.MULTILINE)
        url = url_match.group(1).strip() if url_match else None

        # Extract priority
        priority_match = re.search(r'\*\*Priority:\*\*\s+(HIGH|MEDIUM|LOW)', section_content)
        priority = priority_match.group(1) if priority_match else "UNKNOWN"

        articles[title.lower()] = {
            'title': title,
            'url': url,
            'priority': priority,
            'assessment': section_content.strip()
        }

    return articles

def load_all_assessments():
    """Load all assessment markdown files."""
    all_articles = {}

    for assessment_file in sorted(ASSESSMENTS_DIR.glob("*assessment*.md")):
        print(f"Loading {assessment_file.name}...")
        articles = parse_assessment_file(assessment_file)
        all_articles.update(articles)

    return all_articles

def match_ticket_to_assessment(ticket_title, all_articles):
    """Match ticket title to assessment article."""
    # Normalize title for matching
    normalized_title = ticket_title.lower().replace("-", " ").strip()

    # Try exact match first
    if normalized_title in all_articles:
        return all_articles[normalized_title]

    # Try fuzzy match (significant word overlap)
    ticket_words = set(normalized_title.split())
    best_match = None
    best_score = 0

    for article_title, article_data in all_articles.items():
        article_words = set(article_title.lower().split())
        common = ticket_words & article_words
        score = len(common)

        if score > best_score and score >= 3:  # At least 3 words in common
            best_score = score
            best_match = article_data

    return best_match

def get_ticket_description(ticket_id):
    """Get current JIRA ticket description."""
    env = os.environ.copy()
    env['JIRA_API_TOKEN'] = get_jira_token()

    try:
        result = subprocess.run(
            ['jira', 'issue', 'view', ticket_id],
            capture_output=True,
            text=True,
            timeout=30,
            env=env
        )

        if result.returncode != 0:
            return None

        # Parse description
        desc_match = re.search(r'Description\s+————+\s+(.+?)\s+(?:View this issue|$)', result.stdout, re.DOTALL)
        return desc_match.group(1).strip() if desc_match else ""

    except Exception as e:
        print(f"Error querying {ticket_id}: {e}")
        return None

def update_ticket_description(ticket_id, new_description):
    """Update JIRA ticket description."""
    env = os.environ.copy()
    env['JIRA_API_TOKEN'] = get_jira_token()

    try:
        result = subprocess.run(
            ['jira', 'issue', 'edit', ticket_id, '-b', new_description, '--no-input'],
            capture_output=True,
            text=True,
            timeout=30,
            env=env
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error updating {ticket_id}: {e}")
        return False

def add_ticket_comment(ticket_id, comment):
    """Add comment to JIRA ticket."""
    env = os.environ.copy()
    env['JIRA_API_TOKEN'] = get_jira_token()

    try:
        result = subprocess.run(
            ['jira', 'issue', 'comment', 'add', ticket_id, comment, '--no-input', '-p', 'GAT'],
            capture_output=True,
            text=True,
            timeout=30,
            env=env
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error adding comment to {ticket_id}: {e}")
        return False

def build_description_with_url(current_desc, article_url):
    """Build updated description with article URL."""
    # Replace "Unknown" with actual URL
    if "Article URL: Unknown" in current_desc or "Article URL:** Unknown" in current_desc:
        new_desc = re.sub(
            r'(\*\*)?Article URL(\*\*)?:\s*(Unknown|\*\*\s*Unknown)',
            f'**Article URL:** {article_url}',
            current_desc
        )
        return new_desc
    elif "Article URL:" not in current_desc:
        # Insert URL at the beginning
        return f"""**Article URL:** {article_url}

{current_desc}"""
    else:
        # URL already exists, don't change
        return current_desc

def main():
    parser = argparse.ArgumentParser(description='Fix missing URLs and assessments')
    parser.add_argument('--audit', action='store_true', help='Audit only (no changes)')
    parser.add_argument('--fix-urls', action='store_true', help='Fix missing URLs')
    parser.add_argument('--fix-assessments', action='store_true', help='Add missing assessments')
    parser.add_argument('--fix-all', action='store_true', help='Fix everything')

    args = parser.parse_args()

    # Load data
    print("Loading audio generation results...")
    audio_results = load_audio_results()
    print(f"Found {len(audio_results)} tickets with audio\n")

    print("Loading assessment files...")
    all_articles = load_all_assessments()
    print(f"Loaded {len(all_articles)} articles from assessments\n")

    # Analyze tickets
    results = {
        'matched': [],
        'unmatched': [],
        'missing_url': [],
        'missing_assessment': []
    }

    print("=== ANALYZING TICKETS ===\n")

    for ticket_data in audio_results:
        ticket_id = ticket_data['ticket_id']
        title = ticket_data['title']

        print(f"Checking {ticket_id}: {title[:50]}...")

        # Match to assessment
        article_data = match_ticket_to_assessment(title, all_articles)

        if not article_data:
            print(f"  ⚠ No matching assessment found")
            results['unmatched'].append(ticket_id)
            continue

        results['matched'].append(ticket_id)

        # Get current description
        current_desc = get_ticket_description(ticket_id)
        if not current_desc:
            print(f"  ✗ Could not fetch ticket")
            continue

        # Check for missing URL
        has_url = bool(re.search(r'Article URL:\s*https?://', current_desc))
        url_unknown = 'Article URL: Unknown' in current_desc or 'Article URL:** Unknown' in current_desc

        if not has_url or url_unknown:
            results['missing_url'].append({
                'ticket_id': ticket_id,
                'url': article_data['url'],
                'current_desc': current_desc
            })
            print(f"  ⚠ Missing URL")

        # Check for assessment comment
        has_assessment = 'Relevance Summary:' in current_desc or 'Strategic Implications:' in current_desc
        if not has_assessment:
            results['missing_assessment'].append({
                'ticket_id': ticket_id,
                'assessment': article_data['assessment']
            })
            print(f"  ⚠ Missing assessment")

        if has_url and not url_unknown and has_assessment:
            print(f"  ✓ Complete")

    # Print summary
    print(f"\n=== SUMMARY ===")
    print(f"Matched: {len(results['matched'])}")
    print(f"Unmatched: {len(results['unmatched'])}")
    print(f"Missing URLs: {len(results['missing_url'])}")
    print(f"Missing assessments: {len(results['missing_assessment'])}")

    if args.audit:
        print("\n=== AUDIT COMPLETE (no changes made) ===")
        return

    # Fix issues
    if not (args.fix_all or args.fix_urls or args.fix_assessments):
        print("\nNo fix flags specified. Use --fix-all or --fix-urls/--fix-assessments")
        return

    fixed = 0

    # Fix URLs
    if (args.fix_all or args.fix_urls) and results['missing_url']:
        print(f"\n=== FIXING {len(results['missing_url'])} URLs ===\n")
        for item in results['missing_url']:
            ticket_id = item['ticket_id']
            url = item['url']
            current_desc = item['current_desc']

            if not url:
                print(f"⊙ {ticket_id}: No URL available in assessment")
                continue

            new_desc = build_description_with_url(current_desc, url)

            if update_ticket_description(ticket_id, new_desc):
                print(f"✓ {ticket_id}: Updated with URL")
                fixed += 1
            else:
                print(f"✗ {ticket_id}: Update failed")

    # Fix assessments
    if (args.fix_all or args.fix_assessments) and results['missing_assessment']:
        print(f"\n=== ADDING {len(results['missing_assessment'])} ASSESSMENTS ===\n")
        for item in results['missing_assessment']:
            ticket_id = item['ticket_id']
            assessment = item['assessment']

            comment = f"""# Article Assessment

{assessment}

---
*Assessment auto-generated from relevance analysis*"""

            if add_ticket_comment(ticket_id, comment):
                print(f"✓ {ticket_id}: Added assessment comment")
                fixed += 1
            else:
                print(f"✗ {ticket_id}: Comment failed")

    print(f"\n=== COMPLETE: {fixed} updates made ===")

if __name__ == '__main__':
    main()
