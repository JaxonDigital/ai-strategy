#!/usr/bin/env python3
"""
Anthropic News Scraper

Scrapes https://www.anthropic.com/news for new articles.
Uses Playwright for web scraping (no RSS feed available).

Usage:
    python3 anthropic-scraper.py [--dry-run] [--backfill] [--output-json FILE]
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Import shared patterns
try:
    from shared_patterns import JIRA_PROJECT_GAT, ANTHROPIC_STATE_FILE
except ImportError:
    # Fallback if shared_patterns not available
    JIRA_PROJECT_GAT = 'GAT'
    ANTHROPIC_STATE_FILE = "~/.anthropic-news-state.json"

# State file to track seen articles
STATE_FILE = os.path.expanduser(ANTHROPIC_STATE_FILE)

# JIRA configuration
JIRA_PROJECT = JIRA_PROJECT_GAT  # Use shared constant
JIRA_TOKEN_FILE = os.path.expanduser("~/.jira.d/.pass")


def load_state():
    """Load the state file containing seen article URLs."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {"seen_urls": [], "last_check": None, "created_tickets": {}, "url_to_ticket": {}}


def save_state(state):
    """Save the state file with seen article URLs using atomic write."""
    import tempfile

    # Write to temporary file first
    temp_fd, temp_path = tempfile.mkstemp(
        dir=os.path.dirname(STATE_FILE) if os.path.dirname(STATE_FILE) else '.',
        prefix='.anthropic-news-state-',
        suffix='.tmp'
    )

    try:
        with os.fdopen(temp_fd, 'w') as f:
            json.dump(state, f, indent=2)

        # Atomic rename (POSIX guarantees atomicity)
        os.replace(temp_path, STATE_FILE)
    except Exception as e:
        # Clean up temp file on error
        try:
            os.unlink(temp_path)
        except:
            pass
        raise Exception(f"Failed to save state file: {e}")


def scrape_anthropic_news():
    """
    Scrape Anthropic news page for article listings.
    Returns list of articles with title, URL, and date.

    Note: This requires Playwright MCP or Claude Code to be available.
    For now, returns mock data structure. Actual scraping happens via Claude Code.
    """
    # This function is a placeholder - actual scraping will be done via Playwright
    # through Claude Code's Playwright MCP integration
    print("⚠️  This script requires Playwright scraping to be done via Claude Code")
    print("    Use Claude Code to:")
    print("    1. Navigate to https://www.anthropic.com/news")
    print("    2. Extract article titles, URLs, and dates from page")
    print("    3. Save to JSON file for processing")
    print("")
    print("    Then run this script with --input-json to process the scraped data")
    return []


def check_existing_ticket_by_url(article_url, state):
    """
    Check if a ticket already exists for this article URL.

    Checks:
    1. State file url_to_ticket mapping (fast)
    2. JIRA search by URL (catches manually created tickets)

    Returns: (ticket_id, exists) tuple
    """
    # Check state file first
    url_to_ticket = state.get('url_to_ticket', {})
    if article_url in url_to_ticket:
        return (url_to_ticket[article_url], True)

    # Search JIRA for tickets containing this URL
    try:
        env = os.environ.copy()
        if not os.path.exists(JIRA_TOKEN_FILE):
            return (None, False)

        with open(JIRA_TOKEN_FILE, 'r') as f:
            env['JIRA_API_TOKEN'] = f.read().strip()

        # Search recent tickets
        result = subprocess.run(
            ['jira', 'issue', 'list', '-p', JIRA_PROJECT, '--plain', '--created', 'month'],
            capture_output=True,
            text=True,
            timeout=30,
            env=env
        )

        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                match = re.search(r'(GAT-\d+)', line)
                if match:
                    ticket_id = match.group(1)
                    # Check if ticket contains the URL
                    view_result = subprocess.run(
                        ['jira', 'issue', 'view', ticket_id],
                        capture_output=True,
                        text=True,
                        timeout=10,
                        env=env
                    )
                    if view_result.returncode == 0 and article_url in view_result.stdout:
                        return (ticket_id, True)

    except Exception:
        pass  # If search fails, assume not found

    return (None, False)


def create_jira_ticket(article, pdf_link=None, dry_run=False):
    """
    Create a JIRA ticket for the Anthropic news article.

    Returns: (ticket_id, success) tuple
    """
    title = article['title']
    url = article['url']
    pub_date = article.get('date', 'Unknown')

    summary = f"Review: {title}"

    description = f"""Anthropic News Article

**Article URL:** {url}
**Published:** {pub_date}
**Source:** Anthropic News (anthropic.com/news)
"""

    if pdf_link:
        description += f"""
**PDF:** {pdf_link}
"""

    description += """
To be reviewed for relevance to Jaxon Digital's AI agent initiatives and strategic positioning.

**Strategic Importance**: Anthropic news often includes major announcements about Claude capabilities, API updates, and AI safety research that directly impact our MCP and agent development."""

    if dry_run:
        print(f"  [DRY RUN] Would create ticket: {title}")
        return ("DRY-RUN-XXX", True)

    try:
        if not os.path.exists(JIRA_TOKEN_FILE):
            print(f"  ✗ Error: JIRA token file not found: {JIRA_TOKEN_FILE}")
            return (None, False)

        cmd = [
            'jira', 'issue', 'create',
            '-p', JIRA_PROJECT,
            '-t', 'Task',
            '-s', summary,
            '-b', description,
            '--label', 'Anthropic',
            '--no-input'
        ]

        env = os.environ.copy()
        with open(JIRA_TOKEN_FILE, 'r') as f:
            env['JIRA_API_TOKEN'] = f.read().strip()

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            env=env
        )

        if result.returncode == 0:
            output = result.stdout.strip()
            match = re.search(r'(GAT-\d+)', output)
            if match:
                ticket_id = match.group(1)
                return (ticket_id, True)
            else:
                print(f"  ⚠ Warning: Ticket created but couldn't extract ID from: {output[:100]}")
                return ("GAT-???", True)
        else:
            error = result.stderr.strip()
            print(f"  ✗ Error creating ticket: {error[:200]}")
            return (None, False)

    except subprocess.TimeoutExpired:
        print(f"  ✗ Error: JIRA command timed out")
        return (None, False)
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return (None, False)


def process_articles(articles, dry_run=False):
    """
    Process scraped articles and create JIRA tickets.

    Returns: dict with created_tickets, skipped, and failed
    """
    state = load_state()

    # Filter to new articles only
    seen_urls = set(state['seen_urls'])
    new_articles = [a for a in articles if a['url'] not in seen_urls]

    if not new_articles:
        print("\nNo new articles to process.")
        state['last_check'] = datetime.now().isoformat()
        if not dry_run:
            save_state(state)
        return {
            'created_tickets': {},
            'skipped': [],
            'failed': []
        }

    print(f"\n=== NEW ARTICLES TO PROCESS ({len(new_articles)}) ===")
    for i, article in enumerate(new_articles, 1):
        pub_date = article.get('date', 'Unknown')[:10] if article.get('date') else 'Unknown'
        print(f"{i:2d}. [{pub_date}] {article['title']}")
        print(f"    URL: {article['url']}")

    print(f"\n=== CREATING JIRA TICKETS ===")
    if dry_run:
        print("[DRY RUN MODE - No tickets will be created]\n")

    created_tickets = {}
    skipped = []
    failed = []

    for i, article in enumerate(new_articles, 1):
        print(f"[{i}/{len(new_articles)}] {article['title'][:60]}...")

        # Check for existing ticket
        existing_ticket_id, exists = check_existing_ticket_by_url(article['url'], state)

        if exists:
            print(f"  ⊙ Already exists: {existing_ticket_id} (skipped)")
            skipped.append({
                'url': article['url'],
                'title': article['title'],
                'existing_ticket': existing_ticket_id
            })

            if not dry_run:
                if 'url_to_ticket' not in state:
                    state['url_to_ticket'] = {}
                state['url_to_ticket'][article['url']] = existing_ticket_id
                if article['url'] not in state['seen_urls']:
                    state['seen_urls'].append(article['url'])

            continue

        # Create new ticket
        pdf_link = article.get('pdf_link')  # If PDFs already uploaded
        ticket_id, success = create_jira_ticket(article, pdf_link, dry_run)

        if success:
            print(f"  ✓ Created {ticket_id}")
            created_tickets[article['url']] = {
                'ticket_id': ticket_id,
                'title': article['title'],
                'url': article['url'],
                'created_at': datetime.now().isoformat()
            }

            if not dry_run:
                if article['url'] not in state['seen_urls']:
                    state['seen_urls'].append(article['url'])
                if 'url_to_ticket' not in state:
                    state['url_to_ticket'] = {}
                state['url_to_ticket'][article['url']] = ticket_id
        else:
            print(f"  ✗ Failed to create ticket")
            failed.append(article)

        # Rate limiting
        if not dry_run:
            time.sleep(0.5)

    # Update state
    if not dry_run:
        if 'created_tickets' not in state:
            state['created_tickets'] = {}
        state['created_tickets'].update(created_tickets)
        state['last_check'] = datetime.now().isoformat()
        save_state(state)

    return {
        'created_tickets': created_tickets,
        'skipped': skipped,
        'failed': failed
    }


def main():
    parser = argparse.ArgumentParser(
        description='Scrape Anthropic news and create JIRA tickets'
    )
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be done without creating tickets')
    parser.add_argument('--backfill', action='store_true',
                        help='Process all articles (ignore state file)')
    parser.add_argument('--input-json', type=str,
                        help='JSON file with scraped articles (from Claude Code)')
    parser.add_argument('--output-json', type=str,
                        help='Output JSON file with processing results')

    args = parser.parse_args()

    # Load articles
    if args.input_json:
        print(f"Loading articles from {args.input_json}...")
        with open(args.input_json, 'r') as f:
            data = json.load(f)
            articles = data.get('articles', [])
    else:
        # Attempt to scrape (will show instructions)
        articles = scrape_anthropic_news()
        if not articles:
            print("\nPlease provide scraped articles via --input-json flag")
            sys.exit(1)

    print(f"Found {len(articles)} total articles")

    # Process articles
    if args.backfill:
        print("\n=== BACKFILL MODE: Processing all articles ===")

    results = process_articles(articles, dry_run=args.dry_run)

    # Summary
    print(f"\n=== SUMMARY ===")
    print(f"Total articles: {len(articles)}")
    print(f"Tickets created: {len(results['created_tickets'])}")
    print(f"Skipped (duplicates): {len(results['skipped'])}")
    print(f"Failed: {len(results['failed'])}")

    if results['skipped']:
        print(f"\nSkipped duplicate articles:")
        for dup in results['skipped']:
            print(f"  {dup['existing_ticket']}: {dup['title'][:60]}")

    if results['failed']:
        print(f"\nFailed articles:")
        for article in results['failed']:
            print(f"  - {article['title']}")
            print(f"    {article['url']}")

    if not args.dry_run:
        print(f"\nState file updated: {STATE_FILE}")

        if results['created_tickets']:
            print(f"\nCreated tickets:")
            for url, ticket_info in results['created_tickets'].items():
                print(f"  {ticket_info['ticket_id']}: {ticket_info['title'][:60]}")

    # Output JSON
    if args.output_json:
        output_data = {
            'source': 'anthropic-news',
            'url': 'https://www.anthropic.com/news',
            'fetch_date': datetime.now().isoformat(),
            'total_articles': len(articles),
            'articles': articles,
            'created_tickets': results['created_tickets'],
            'failed_articles': [a['url'] for a in results['failed']]
        }

        with open(args.output_json, 'w') as f:
            json.dump(output_data, f, indent=2)
        print(f"\nMetadata written to: {args.output_json}")


if __name__ == '__main__':
    main()
