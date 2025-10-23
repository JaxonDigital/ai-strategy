#!/usr/bin/env python3
"""
Monitor Optimizely World blog RSS feed for new articles.

Automatically creates JIRA tickets for new articles.

Usage:
    # Initial backfill - process all existing articles and create tickets
    python3 scripts/monitor-optimizely-blog.py --backfill

    # Daily incremental run - only new articles since last check
    python3 scripts/monitor-optimizely-blog.py

    # Dry run - show what would be created without actually creating tickets
    python3 scripts/monitor-optimizely-blog.py --dry-run
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime

# JIRA configuration
JIRA_PROJECT = "GAT"
JIRA_API_URL = "https://jaxondigital.atlassian.net"
JIRA_EMAIL = "bgerby@jaxondigital.com"
JIRA_TOKEN_FILE = os.path.expanduser("~/.jira.d/.pass")

# RSS feed URL
RSS_FEED_URL = "https://world.optimizely.com/blogs/?feed=RSS"

# State file to track seen articles
STATE_FILE = os.path.expanduser("~/.optimizely-blog-state.json")


def load_state():
    """Load the state file containing seen article GUIDs."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {"seen_guids": [], "last_check": None, "created_tickets": {}, "url_to_ticket": {}}


def save_state(state):
    """Save the state file with seen article GUIDs."""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def fetch_rss_feed():
    """Fetch and parse the Optimizely World RSS feed."""
    print(f"Fetching RSS feed from {RSS_FEED_URL}...")

    try:
        # Add User-Agent header to avoid 403 Forbidden
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        req = urllib.request.Request(RSS_FEED_URL, headers=headers)

        with urllib.request.urlopen(req) as response:
            content = response.read()

        # Parse XML
        root = ET.fromstring(content)

        # Extract articles (items)
        articles = []
        for item in root.findall('.//item'):
            title = item.find('title').text if item.find('title') is not None else "Untitled"
            link = item.find('link').text if item.find('link') is not None else ""
            guid = item.find('guid').text if item.find('guid') is not None else link
            pub_date_str = item.find('pubDate').text if item.find('pubDate') is not None else ""
            description = item.find('description').text if item.find('description') is not None else ""

            # Parse pub date
            pub_date = None
            if pub_date_str:
                try:
                    pub_date = parsedate_to_datetime(pub_date_str)
                except:
                    pass

            articles.append({
                'title': title,
                'url': link,
                'guid': guid,
                'pub_date': pub_date.isoformat() if pub_date else "",
                'description': description
            })

        print(f"Found {len(articles)} articles in RSS feed")
        return articles

    except Exception as e:
        print(f"Error fetching RSS feed: {e}", file=sys.stderr)
        sys.exit(1)


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

        # Search using JQL - look for URL in description
        # Escape URL for JQL query
        search_url = article_url.replace(':', '\\:').replace('/', '\\/')

        # Use jira list with JQL filter
        # Note: This is a simplified check - searches recent tickets
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
                # If line contains a ticket ID, check that ticket for the URL
                match = re.search(r'(GAT-\d+)', line)
                if match:
                    ticket_id = match.group(1)
                    # Quick check: view ticket and search for URL
                    view_result = subprocess.run(
                        ['jira', 'issue', 'view', ticket_id],
                        capture_output=True,
                        text=True,
                        timeout=10,
                        env=env
                    )
                    if view_result.returncode == 0 and article_url in view_result.stdout:
                        return (ticket_id, True)

    except Exception as e:
        pass  # If search fails, assume not found

    return (None, False)


def create_jira_ticket_direct(article, dry_run=False):
    """
    Create a JIRA ticket directly using jira CLI.

    Returns: (ticket_id, success) tuple
    """
    title = article['title']
    url = article['url']
    pub_date = article.get('pub_date', 'Unknown')

    description = f"""Optimizely World Blog Article

**Article URL:** {url}
**Published:** {pub_date}
**Source:** Optimizely World Blog (world.optimizely.com)

To be reviewed for relevance to Jaxon Digital's AI agent initiatives and Optimizely platform strategy.
"""

    if dry_run:
        print(f"  [DRY RUN] Would create ticket: {title}")
        return ("DRY-RUN-XXX", True)

    # Write description to temp file
    temp_file = f'/tmp/optimizely-ticket-{int(time.time())}.txt'
    try:
        with open(temp_file, 'w') as f:
            f.write(description)

        # Get JIRA API token
        if not os.path.exists(JIRA_TOKEN_FILE):
            print(f"  ✗ Error: JIRA token file not found: {JIRA_TOKEN_FILE}")
            return (None, False)

        # Create JIRA ticket
        cmd = [
            'jira', 'issue', 'create',
            '-p', JIRA_PROJECT,
            '-t', 'Task',
            '-s', title,
            '-b', description,
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
            # Extract ticket ID from output
            # Output format: "GAT-XXX" or contains "Created: GAT-XXX"
            output = result.stdout.strip()
            match = re.search(r'(GAT-\d+)', output)
            if match:
                ticket_id = match.group(1)
                return (ticket_id, True)
            else:
                # Success but couldn't parse ticket ID
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
    finally:
        # Clean up temp file
        if os.path.exists(temp_file):
            os.remove(temp_file)


def main():
    parser = argparse.ArgumentParser(
        description='Monitor Optimizely World blog RSS feed and auto-create JIRA tickets'
    )
    parser.add_argument('--backfill', action='store_true',
                        help='Process all existing articles (ignore state file)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be done without actually creating tickets')
    parser.add_argument('--output-json', type=str,
                        help='Output JSON file with article metadata')

    args = parser.parse_args()

    # Fetch RSS feed
    all_articles = fetch_rss_feed()

    # Load state
    state = load_state()

    # Determine which articles are new
    if args.backfill:
        print("\n=== BACKFILL MODE: Processing all articles ===")
        new_articles = all_articles
        # Don't reset state in backfill - just process what we haven't seen
        seen_guids = set(state.get('seen_guids', []))
        new_articles = [a for a in all_articles if a['guid'] not in seen_guids]
    else:
        print("\n=== INCREMENTAL MODE: Processing only new articles ===")
        seen_guids = set(state['seen_guids'])
        new_articles = [a for a in all_articles if a['guid'] not in seen_guids]
        print(f"Found {len(new_articles)} new articles (out of {len(all_articles)} total)")

    if not new_articles:
        print("\nNo new articles to process.")
        state['last_check'] = datetime.now().isoformat()
        save_state(state)
        return

    # Sort by pub_date (oldest first for sequential processing)
    new_articles.sort(key=lambda x: x.get('pub_date', ''))

    print(f"\n=== NEW ARTICLES TO PROCESS ({len(new_articles)}) ===")
    for i, article in enumerate(new_articles, 1):
        pub_date = article.get('pub_date', 'Unknown')[:10]  # YYYY-MM-DD
        print(f"{i:2d}. [{pub_date}] {article['title']}")
        print(f"    URL: {article['url']}")

    # Create JIRA tickets automatically
    print(f"\n=== CREATING JIRA TICKETS ===")
    if args.dry_run:
        print("[DRY RUN MODE - No tickets will be created]\n")

    created_tickets = {}
    skipped_duplicates = []
    failed_articles = []

    for i, article in enumerate(new_articles, 1):
        print(f"[{i}/{len(new_articles)}] {article['title'][:60]}...")

        # Check for existing ticket first
        existing_ticket_id, exists = check_existing_ticket_by_url(article['url'], state)

        if exists:
            print(f"  ⊙ Already exists: {existing_ticket_id} (skipped)")
            skipped_duplicates.append({
                'url': article['url'],
                'title': article['title'],
                'existing_ticket': existing_ticket_id
            })

            # Update state mappings
            if not args.dry_run:
                if 'url_to_ticket' not in state:
                    state['url_to_ticket'] = {}
                state['url_to_ticket'][article['url']] = existing_ticket_id
                if article['guid'] not in state['seen_guids']:
                    state['seen_guids'].append(article['guid'])

            continue

        # Create new ticket
        ticket_id, success = create_jira_ticket_direct(article, dry_run=args.dry_run)

        if success:
            print(f"  ✓ Created {ticket_id}")
            created_tickets[article['guid']] = {
                'ticket_id': ticket_id,
                'title': article['title'],
                'url': article['url'],
                'created_at': datetime.now().isoformat()
            }

            # Mark as seen immediately after successful creation
            if not args.dry_run:
                if article['guid'] not in state['seen_guids']:
                    state['seen_guids'].append(article['guid'])
                # Add to URL mapping
                if 'url_to_ticket' not in state:
                    state['url_to_ticket'] = {}
                state['url_to_ticket'][article['url']] = ticket_id

        else:
            print(f"  ✗ Failed to create ticket")
            failed_articles.append(article)

        # Small delay to avoid overwhelming JIRA API
        if not args.dry_run:
            time.sleep(0.5)

    # Update state with created tickets
    if not args.dry_run:
        if 'created_tickets' not in state:
            state['created_tickets'] = {}
        state['created_tickets'].update(created_tickets)
        state['last_check'] = datetime.now().isoformat()
        save_state(state)

    # Summary
    print(f"\n=== SUMMARY ===")
    print(f"Total new articles: {len(new_articles)}")
    print(f"Tickets created: {len(created_tickets)}")
    print(f"Skipped (duplicates): {len(skipped_duplicates)}")
    print(f"Failed: {len(failed_articles)}")

    if skipped_duplicates:
        print(f"\nSkipped duplicate articles:")
        for dup in skipped_duplicates:
            print(f"  {dup['existing_ticket']}: {dup['title'][:60]}")

    if failed_articles:
        print(f"\nFailed articles (can retry):")
        for article in failed_articles:
            print(f"  - {article['title']}")
            print(f"    {article['url']}")

    if not args.dry_run:
        print(f"\nState file updated: {STATE_FILE}")

        # List created tickets for easy reference
        if created_tickets:
            print(f"\nCreated tickets:")
            for guid, ticket_info in created_tickets.items():
                print(f"  {ticket_info['ticket_id']}: {ticket_info['title'][:60]}")

    # Output metadata JSON
    if args.output_json:
        output_data = {
            'source': 'optimizely-world-blog',
            'feed_url': RSS_FEED_URL,
            'fetch_date': datetime.now().isoformat(),
            'total_articles': len(all_articles),
            'new_articles': len(new_articles),
            'articles': new_articles,
            'created_tickets': created_tickets,
            'failed_articles': [a['url'] for a in failed_articles]
        }

        with open(args.output_json, 'w') as f:
            json.dump(output_data, f, indent=2)
        print(f"\nMetadata written to: {args.output_json}")


if __name__ == '__main__':
    main()
