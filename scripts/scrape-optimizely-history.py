#!/usr/bin/env python3
"""
Scrape historical Optimizely World blog articles from paginated HTML.

This script is for ONE-TIME historical backfill. For daily monitoring, use monitor-optimizely-blog.py.

Usage:
    # Scrape all pages until we find articles we've already seen
    python3 scripts/scrape-optimizely-history.py

    # Scrape specific page range
    python3 scripts/scrape-optimizely-history.py --start-page 1 --max-pages 10

    # Only articles after specific date
    python3 scripts/scrape-optimizely-history.py --since-date 2025-01-01

    # Dry run - don't create tickets
    python3 scripts/scrape-optimizely-history.py --dry-run
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from html.parser import HTMLParser

# JIRA configuration
JIRA_PROJECT = "GAT"
JIRA_TOKEN_FILE = os.path.expanduser("~/.jira.d/.pass")

# State file to track seen articles (shared with RSS monitor)
STATE_FILE = os.path.expanduser("~/.optimizely-blog-state.json")

# Base URL for paginated blog
BASE_URL = "https://world.optimizely.com/blogs/"


class BlogArticleParser(HTMLParser):
    """Parse Optimizely World blog HTML to extract article metadata."""

    def __init__(self):
        super().__init__()
        self.articles = []
        self.current_article = None
        self.in_title = False
        self.in_date = False

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        # Article container - varies by site structure
        if tag == 'article' or (tag == 'div' and 'class' in attrs_dict and 'blog-post' in attrs_dict['class']):
            self.current_article = {}

        # Article link/title
        if tag == 'a' and self.current_article is not None and 'href' in attrs_dict:
            href = attrs_dict['href']
            if href and ('blogs' in href or '.com' in href) and href not in ['#', '/']:
                if 'url' not in self.current_article:
                    self.current_article['url'] = href
                    self.in_title = True

    def handle_data(self, data):
        if self.in_title and self.current_article:
            text = data.strip()
            if text and len(text) > 5:  # Avoid short fragments
                self.current_article['title'] = text
                self.in_title = False

    def handle_endtag(self, tag):
        if tag == 'article' and self.current_article and 'url' in self.current_article:
            # Finalize article if we have minimum required data
            if 'title' in self.current_article:
                self.articles.append(self.current_article)
            self.current_article = None


def load_state():
    """Load the state file containing seen article GUIDs."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {"seen_guids": [], "last_check": None, "created_tickets": {}}


def save_state(state):
    """Save the state file with seen article GUIDs."""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def fetch_page_html(page_num):
    """Fetch HTML for a specific page number."""
    url = f"{BASE_URL}?pageNum={page_num}"
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        req = urllib.request.Request(url, headers=headers)

        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode('utf-8')
            return html

    except Exception as e:
        print(f"Error fetching page {page_num}: {e}", file=sys.stderr)
        return None


def parse_articles_from_html(html):
    """
    Extract article metadata from HTML.

    Returns list of articles with title and URL.
    """
    parser = BlogArticleParser()
    parser.feed(html)

    # Also try simple regex extraction as fallback
    articles = parser.articles[:]

    # Regex patterns for article links (backup method)
    # Pattern 1: /blogs/author/dates/YYYY/MM/article-slug/
    pattern1 = r'href="([^"]*?/blogs/[^"]+/dates/\d{4}/\d{2}/[^"]+/)"[^>]*>\s*([^<]+)'
    # Pattern 2: External blog URLs
    pattern2 = r'href="(https?://[^"]+\.(?:blog|com)/[^"]+)"[^>]*>\s*([^<]+)'

    for pattern in [pattern1, pattern2]:
        matches = re.findall(pattern, html)
        for url, title in matches:
            title = title.strip()
            if len(title) > 10 and url not in [a['url'] for a in articles]:
                articles.append({'title': title, 'url': url})

    return articles


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
        print(f"  [DRY RUN] Would create ticket: {title[:60]}")
        return ("DRY-RUN-XXX", True)

    # Write description to temp file
    temp_file = f'/tmp/optimizely-scrape-ticket-{int(time.time())}.txt'
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
            output = result.stdout.strip()
            match = re.search(r'(GAT-\d+)', output)
            if match:
                ticket_id = match.group(1)
                return (ticket_id, True)
            else:
                return ("GAT-???", True)
        else:
            error = result.stderr.strip()
            print(f"  ✗ Error: {error[:200]}")
            return (None, False)

    except subprocess.TimeoutExpired:
        print(f"  ✗ Error: Timeout")
        return (None, False)
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return (None, False)
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


def main():
    parser = argparse.ArgumentParser(
        description='Scrape historical Optimizely World blog articles'
    )
    parser.add_argument('--start-page', type=int, default=1,
                        help='Starting page number (default: 1)')
    parser.add_argument('--max-pages', type=int, default=None,
                        help='Maximum pages to scrape (default: until duplicates)')
    parser.add_argument('--since-date', type=str, default=None,
                        help='Only articles after this date (YYYY-MM-DD)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be done without creating tickets')

    args = parser.parse_args()

    # Load state
    state = load_state()
    seen_guids = set(state.get('seen_guids', []))
    seen_urls = {ticket['url'] for ticket in state.get('created_tickets', {}).values()}

    print(f"Starting historical scrape from page {args.start_page}")
    print(f"Already tracking {len(seen_guids)} articles\n")

    if args.dry_run:
        print("[DRY RUN MODE - No tickets will be created]\n")

    total_articles_found = 0
    total_new_articles = 0
    total_created_tickets = 0
    consecutive_all_seen_pages = 0

    for page_num in range(args.start_page, (args.start_page + args.max_pages) if args.max_pages else 10000):
        print(f"\n=== PAGE {page_num} ===")

        # Fetch page HTML
        html = fetch_page_html(page_num)
        if not html:
            print(f"Failed to fetch page {page_num}, stopping")
            break

        # Parse articles
        articles = parse_articles_from_html(html)
        if not articles:
            print(f"No articles found on page {page_num}, stopping")
            break

        print(f"Found {len(articles)} articles on this page")
        total_articles_found += len(articles)

        # Check which are new
        new_articles = []
        for article in articles:
            # Use URL as unique identifier
            if article['url'] not in seen_urls:
                new_articles.append(article)
                seen_urls.add(article['url'])

        if not new_articles:
            consecutive_all_seen_pages += 1
            print(f"All articles on this page already seen ({consecutive_all_seen_pages} consecutive)")

            # Stop if we've seen 3 consecutive pages with no new articles
            if consecutive_all_seen_pages >= 3:
                print("\nReached historical limit (3 pages with no new articles)")
                break
            continue
        else:
            consecutive_all_seen_pages = 0

        print(f"{len(new_articles)} new articles to process")
        total_new_articles += len(new_articles)

        # Create JIRA tickets
        for i, article in enumerate(new_articles, 1):
            print(f"  [{i}/{len(new_articles)}] {article['title'][:50]}...")

            ticket_id, success = create_jira_ticket_direct(article, dry_run=args.dry_run)

            if success:
                print(f"    ✓ Created {ticket_id}")
                total_created_tickets += 1

                # Mark as seen
                if not args.dry_run:
                    state['seen_guids'].append(article['url'])
                    if 'created_tickets' not in state:
                        state['created_tickets'] = {}
                    state['created_tickets'][article['url']] = {
                        'ticket_id': ticket_id,
                        'title': article['title'],
                        'url': article['url'],
                        'created_at': datetime.now().isoformat()
                    }

            time.sleep(0.5)  # Rate limiting

        # Save state after each page
        if not args.dry_run:
            state['last_check'] = datetime.now().isoformat()
            save_state(state)

        # Delay between pages
        time.sleep(1)

    # Final summary
    print(f"\n=== SCRAPING COMPLETE ===")
    print(f"Pages scraped: {page_num - args.start_page + 1}")
    print(f"Total articles found: {total_articles_found}")
    print(f"New articles: {total_new_articles}")
    print(f"Tickets created: {total_created_tickets}")

    if not args.dry_run:
        print(f"\nState file updated: {STATE_FILE}")


if __name__ == '__main__':
    main()
