#!/usr/bin/env python3
"""
Audit and fix JIRA tickets for missing URLs, PDFs, audio links, and assessments.

This script:
1. Reads all assessment files to extract ticket metadata (URLs, assessments, priorities)
2. Queries each JIRA ticket to check what's missing
3. Updates tickets with missing information
4. Adds assessment as comments where missing

Usage:
    # Audit only (no changes)
    python3 scripts/audit-and-fix-jira-tickets.py --audit-only

    # Fix everything
    python3 scripts/audit-and-fix-jira-tickets.py --fix-all

    # Fix specific issues
    python3 scripts/audit-and-fix-jira-tickets.py --fix-urls --fix-assessments
"""

import argparse
import glob
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# JIRA configuration
JIRA_TOKEN_FILE = os.path.expanduser("~/.jira.d/.pass")
JIRA_PROJECT = "GAT"

def get_jira_token():
    """Read JIRA API token."""
    with open(JIRA_TOKEN_FILE, 'r') as f:
        return f.read().strip()

def parse_assessment_file(assessment_path):
    """
    Parse assessment markdown file to extract:
    - Article number -> URL mapping
    - Article number -> Priority
    - Article number -> Full assessment text (for comments)
    """
    with open(assessment_path, 'r') as f:
        content = f.read()

    articles = {}

    # Pattern to match article sections
    pattern = r'###\s+ARTICLE-(\d+)\s+-\s+(.+?)$'

    for match in re.finditer(pattern, content, re.MULTILINE):
        article_num = int(match.group(1))
        title = match.group(2).strip()

        # Extract the full article section
        start_pos = match.end()
        next_match = re.search(r'###\s+ARTICLE-\d+', content[start_pos:])
        if next_match:
            end_pos = start_pos + next_match.start()
        else:
            section_match = re.search(r'\n##\s+', content[start_pos:])
            end_pos = start_pos + section_match.start() if section_match else len(content)

        section_content = content[start_pos:end_pos]

        # Extract priority
        priority_match = re.search(r'\*\*Priority:\*\*\s+(HIGH|MEDIUM|LOW)', section_content)
        priority = priority_match.group(1) if priority_match else "UNKNOWN"

        # Extract URL
        url_match = re.search(r'\*\*Article URL:\*\*\s+(.+?)$', section_content, re.MULTILINE)
        url = url_match.group(1).strip() if url_match else None

        # Extract full assessment (everything in this section)
        assessment = section_content.strip()

        articles[article_num] = {
            'article_num': article_num,
            'title': title,
            'url': url,
            'priority': priority,
            'assessment': assessment
        }

    return articles

def load_all_assessments(assessments_dir):
    """Load all assessment files and build complete article database."""
    assessments_dir = Path(assessments_dir)
    assessment_files = sorted(assessments_dir.glob("*assessment*.md"))

    all_articles = {}

    for assessment_file in assessment_files:
        print(f"Loading {assessment_file.name}...")
        articles = parse_assessment_file(assessment_file)

        # Merge into all_articles (later files override earlier ones)
        for article_num, data in articles.items():
            all_articles[article_num] = data

    return all_articles

def get_ticket_info(ticket_id):
    """Query JIRA for ticket description and comments."""
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

        output = result.stdout

        # Parse description section
        desc_match = re.search(r'Description\s+————+\s+(.+?)\s+(?:View this issue|$)', output, re.DOTALL)
        description = desc_match.group(1).strip() if desc_match else ""

        # Check for URL in description
        has_url = bool(re.search(r'Article URL:\s*https?://', description))
        url_unknown = 'Article URL: Unknown' in description or 'Article URL:** Unknown' in description

        # Check for PDF link
        has_pdf = bool(re.search(r'PDF:\s*https://drive\.google\.com', description))

        # Check for audio link
        has_audio = bool(re.search(r'Audio:\s*https://drive\.google\.com', description))

        # Check for assessment comment (would be in comments section)
        has_assessment = 'Relevance Summary:' in output or 'Strategic Implications:' in output

        return {
            'ticket_id': ticket_id,
            'description': description,
            'has_url': has_url and not url_unknown,
            'url_unknown': url_unknown,
            'has_pdf': has_pdf,
            'has_audio': has_audio,
            'has_assessment': has_assessment
        }

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

def add_ticket_comment(ticket_id, comment_text):
    """Add comment to JIRA ticket."""
    env = os.environ.copy()
    env['JIRA_API_TOKEN'] = get_jira_token()

    try:
        result = subprocess.run(
            ['jira', 'issue', 'comment', 'add', ticket_id, comment_text, '--no-input', '-p', JIRA_PROJECT],
            capture_output=True,
            text=True,
            timeout=30,
            env=env
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error adding comment to {ticket_id}: {e}")
        return False

def build_description(article_data, ticket_info):
    """Build complete ticket description with URL, PDF, and audio."""
    url = article_data.get('url', 'Unknown')

    # Extract existing links from current description
    desc = ticket_info['description']
    pdf_match = re.search(r'PDF:\s*(https://drive\.google\.com[^\s]+)', desc)
    audio_match = re.search(r'Audio:\s*(https://drive\.google\.com[^\s]+)', desc)

    pdf_link = pdf_match.group(1) if pdf_match else "Not yet uploaded"
    audio_link = audio_match.group(1) if audio_match else "(Pending - HIGH/MEDIUM priority only)"

    description = f"""Medium Article Review

**Article URL:** {url}
**PDF:** {pdf_link}
**Audio:** {audio_link}

To be reviewed for relevance to Jaxon Digital's AI agent initiatives."""

    return description

def audit_tickets(all_articles, start_ticket=None, end_ticket=None):
    """Audit all tickets and report what's missing."""
    results = {
        'missing_url': [],
        'missing_pdf': [],
        'missing_audio': [],  # For HIGH/MEDIUM only
        'missing_assessment': [],
        'total_checked': 0,
        'errors': []
    }

    # Determine ticket range from articles
    if not start_ticket:
        start_ticket = min(all_articles.keys()) if all_articles else 479
    if not end_ticket:
        end_ticket = max(all_articles.keys()) if all_articles else 491

    print(f"\n=== AUDITING TICKETS GAT-{start_ticket} to GAT-{end_ticket} ===\n")

    for article_num in range(start_ticket, end_ticket + 1):
        ticket_id = f"GAT-{article_num}"
        article_data = all_articles.get(article_num)

        if not article_data:
            print(f"⊙ {ticket_id}: No assessment data found (might be Optimizely or older format)")
            continue

        print(f"Checking {ticket_id} ({article_data['title'][:50]}...)...")
        ticket_info = get_ticket_info(ticket_id)

        if not ticket_info:
            results['errors'].append(ticket_id)
            print(f"  ✗ Error querying ticket")
            continue

        results['total_checked'] += 1
        issues = []

        # Check URL
        if not ticket_info['has_url'] or ticket_info['url_unknown']:
            results['missing_url'].append(ticket_id)
            issues.append("missing URL")

        # Check PDF
        if not ticket_info['has_pdf']:
            results['missing_pdf'].append(ticket_id)
            issues.append("missing PDF")

        # Check audio (only for HIGH/MEDIUM)
        if article_data['priority'] in ['HIGH', 'MEDIUM'] and not ticket_info['has_audio']:
            results['missing_audio'].append(ticket_id)
            issues.append("missing audio")

        # Check assessment comment
        if not ticket_info['has_assessment']:
            results['missing_assessment'].append(ticket_id)
            issues.append("missing assessment")

        if issues:
            print(f"  ⚠ Issues: {', '.join(issues)}")
        else:
            print(f"  ✓ Complete")

    return results

def fix_tickets(all_articles, audit_results, fix_urls=False, fix_assessments=False):
    """Fix tickets based on audit results."""
    print(f"\n=== FIXING TICKETS ===\n")

    fixed_count = 0

    # Fix URLs
    if fix_urls and audit_results['missing_url']:
        print(f"Fixing {len(audit_results['missing_url'])} tickets with missing URLs...")
        for ticket_id in audit_results['missing_url']:
            article_num = int(ticket_id.split('-')[1])
            article_data = all_articles.get(article_num)

            if not article_data or not article_data['url']:
                print(f"  ⊙ {ticket_id}: No URL data available")
                continue

            ticket_info = get_ticket_info(ticket_id)
            if not ticket_info:
                print(f"  ✗ {ticket_id}: Could not fetch ticket")
                continue

            new_desc = build_description(article_data, ticket_info)

            if update_ticket_description(ticket_id, new_desc):
                print(f"  ✓ {ticket_id}: Updated with URL")
                fixed_count += 1
            else:
                print(f"  ✗ {ticket_id}: Update failed")

    # Fix assessment comments
    if fix_assessments and audit_results['missing_assessment']:
        print(f"\nAdding assessments to {len(audit_results['missing_assessment'])} tickets...")
        for ticket_id in audit_results['missing_assessment']:
            article_num = int(ticket_id.split('-')[1])
            article_data = all_articles.get(article_num)

            if not article_data or not article_data['assessment']:
                print(f"  ⊙ {ticket_id}: No assessment data available")
                continue

            # Format assessment as comment
            comment = f"""# Article Assessment

{article_data['assessment']}

---
*Assessment auto-generated from relevance analysis*"""

            if add_ticket_comment(ticket_id, comment):
                print(f"  ✓ {ticket_id}: Added assessment comment")
                fixed_count += 1
            else:
                print(f"  ✗ {ticket_id}: Comment failed")

    return fixed_count

def main():
    parser = argparse.ArgumentParser(description='Audit and fix JIRA tickets')
    parser.add_argument('--audit-only', action='store_true', help='Only audit, do not fix')
    parser.add_argument('--fix-all', action='store_true', help='Fix all issues')
    parser.add_argument('--fix-urls', action='store_true', help='Fix missing URLs only')
    parser.add_argument('--fix-assessments', action='store_true', help='Fix missing assessments only')
    parser.add_argument('--start-ticket', type=int, help='Start ticket number (e.g., 479)')
    parser.add_argument('--end-ticket', type=int, help='End ticket number (e.g., 491)')
    parser.add_argument('--assessments-dir', default='/Users/bgerby/Documents/dev/ai/assessments',
                        help='Directory containing assessment markdown files')

    args = parser.parse_args()

    # Load all assessment data
    print("Loading assessment files...")
    all_articles = load_all_assessments(args.assessments_dir)
    print(f"Loaded {len(all_articles)} articles from assessment files\n")

    # Audit tickets
    audit_results = audit_tickets(all_articles, args.start_ticket, args.end_ticket)

    # Print summary
    print(f"\n=== AUDIT SUMMARY ===")
    print(f"Total tickets checked: {audit_results['total_checked']}")
    print(f"Missing URLs: {len(audit_results['missing_url'])}")
    print(f"Missing PDFs: {len(audit_results['missing_pdf'])}")
    print(f"Missing audio (HIGH/MEDIUM): {len(audit_results['missing_audio'])}")
    print(f"Missing assessments: {len(audit_results['missing_assessment'])}")
    print(f"Errors: {len(audit_results['errors'])}")

    if args.audit_only:
        print("\n=== AUDIT COMPLETE (no changes made) ===")
        return

    # Fix issues if requested
    if args.fix_all:
        fix_urls = True
        fix_assessments = True
    else:
        fix_urls = args.fix_urls
        fix_assessments = args.fix_assessments

    if fix_urls or fix_assessments:
        fixed_count = fix_tickets(all_articles, audit_results, fix_urls, fix_assessments)
        print(f"\n=== FIX COMPLETE: {fixed_count} tickets updated ===")
    else:
        print("\n=== No fix flags specified, use --fix-all or --fix-urls/--fix-assessments ===")

if __name__ == '__main__':
    main()
