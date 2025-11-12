#!/usr/bin/env python3
"""
Monitor FreeCodeCamp blog RSS feed for new articles.

Automatically creates JIRA tickets for new articles.
Skips video content (YouTube embeds).
Extracts full article text from RSS feed (no PDF needed).

Usage:
    # Initial backfill - process all existing articles and create tickets
    python3 scripts/monitor-freecodecamp-blog.py --backfill

    # Daily incremental run - only new articles since last check
    python3 scripts/monitor-freecodecamp-blog.py

    # Dry run - show what would be created without actually creating tickets
    python3 scripts/monitor-freecodecamp-blog.py --dry-run

    # Output metadata JSON for assessment
    python3 scripts/monitor-freecodecamp-blog.py --output-json /tmp/freecodecamp-articles.json
"""

import argparse
import html
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
from html.parser import HTMLParser
from pathlib import Path

# JIRA configuration
JIRA_PROJECT = 'GAT'
JIRA_API_URL = "https://jaxondigital.atlassian.net"
JIRA_EMAIL = "bgerby@jaxondigital.com"
JIRA_TOKEN_FILE = os.path.expanduser("~/.jira.d/.pass")

# RSS feed URL
RSS_FEED_URL = "https://www.freecodecamp.org/news/rss/"

# State file to track seen articles
STATE_FILE = os.path.expanduser("~/.freecodecamp-state.json")


class HTMLTextExtractor(HTMLParser):
    """Extract plain text from HTML, removing tags but preserving structure."""

    def __init__(self):
        super().__init__()
        self.text_parts = []
        self.in_script = False
        self.in_style = False

    def handle_starttag(self, tag, attrs):
        if tag == 'script':
            self.in_script = True
        elif tag == 'style':
            self.in_style = True
        elif tag in ['p', 'br', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.text_parts.append('\n')

    def handle_endtag(self, tag):
        if tag == 'script':
            self.in_script = False
        elif tag == 'style':
            self.in_style = False

    def handle_data(self, data):
        if not self.in_script and not self.in_style:
            # Decode HTML entities
            text = html.unescape(data)
            # Clean up whitespace
            text = ' '.join(text.split())
            if text:
                self.text_parts.append(text)

    def get_text(self):
        """Return extracted text, cleaned up."""
        text = ' '.join(self.text_parts)
        # Clean up multiple newlines/spaces
        text = re.sub(r'\n\s*\n+', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        return text.strip()


def load_state():
    """Load the state file containing seen article GUIDs."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {"seen_guids": [], "last_check": None, "created_tickets": {}, "url_to_ticket": {}}


def save_state(state):
    """Save the state file with seen article GUIDs using atomic write."""
    import tempfile

    # Write to temporary file first
    temp_fd, temp_path = tempfile.mkstemp(
        dir=os.path.dirname(STATE_FILE) if os.path.dirname(STATE_FILE) else '.',
        prefix='.freecodecamp-state-',
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


def is_video_content(html_content):
    """
    Detect if article is primarily video content.
    Returns True if YouTube iframe is detected.
    """
    if not html_content:
        return False

    # Check for YouTube embeds
    youtube_patterns = [
        r'<iframe[^>]+youtube\.com/embed/',
        r'<iframe[^>]+youtube-nocookie\.com/embed/',
        r'https://www\.youtube\.com/watch'
    ]

    for pattern in youtube_patterns:
        if re.search(pattern, html_content, re.IGNORECASE):
            return True

    return False


def extract_text_from_html(html_content):
    """Extract plain text from HTML content."""
    if not html_content:
        return ""

    parser = HTMLTextExtractor()
    try:
        parser.feed(html_content)
        return parser.get_text()
    except Exception as e:
        print(f"  ⚠ Warning: Error extracting text from HTML: {e}", file=sys.stderr)
        # Fallback: simple regex strip
        text = re.sub(r'<[^>]+>', ' ', html_content)
        text = html.unescape(text)
        text = ' '.join(text.split())
        return text


def fetch_rss_feed():
    """Fetch and parse the FreeCodeCamp RSS feed."""
    print(f"Fetching RSS feed from {RSS_FEED_URL}...")

    try:
        # Add User-Agent header to avoid 403 Forbidden
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        req = urllib.request.Request(RSS_FEED_URL, headers=headers)

        with urllib.request.urlopen(req) as response:
            content = response.read()

        # Parse XML with namespace handling
        root = ET.fromstring(content)

        # Define namespaces
        namespaces = {
            'dc': 'http://purl.org/dc/elements/1.1/',
            'content': 'http://purl.org/rss/1.0/modules/content/',
            'media': 'http://search.yahoo.com/mrss/'
        }

        # Extract articles (items)
        articles = []
        for item in root.findall('.//item'):
            # Extract and clean title (decode HTML entities, trim whitespace)
            title_elem = item.find('title')
            title = html.unescape(title_elem.text).strip() if title_elem is not None and title_elem.text else "Untitled"

            link = item.find('link').text if item.find('link') is not None else ""
            guid = item.find('guid').text if item.find('guid') is not None else link
            pub_date_str = item.find('pubDate').text if item.find('pubDate') is not None else ""

            # Extract and clean author (dc:creator)
            author_elem = item.find('dc:creator', namespaces)
            author = html.unescape(author_elem.text).strip() if author_elem is not None and author_elem.text else "Unknown"

            # Extract and clean categories (multiple possible)
            categories = []
            for cat_elem in item.findall('category'):
                if cat_elem.text:
                    # Decode HTML entities and trim whitespace
                    cat_text = html.unescape(cat_elem.text).strip()
                    if cat_text:
                        categories.append(cat_text)

            # Extract full HTML content (content:encoded)
            content_elem = item.find('content:encoded', namespaces)
            html_content = content_elem.text if content_elem is not None else ""

            # Extract description (fallback)
            description = item.find('description').text if item.find('description') is not None else ""

            # Parse pub date
            pub_date = None
            if pub_date_str:
                try:
                    pub_date = parsedate_to_datetime(pub_date_str)
                except:
                    pass

            # Check if video content
            is_video = is_video_content(html_content)

            # Extract text from HTML (for non-video articles)
            article_text = ""
            if not is_video and html_content:
                article_text = extract_text_from_html(html_content)

            articles.append({
                'title': title,
                'url': link,
                'guid': guid,
                'pub_date': pub_date.isoformat() if pub_date else "",
                'author': author,
                'categories': categories,
                'description': description,
                'html_content': html_content,
                'article_text': article_text,
                'is_video': is_video
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

        # Search using jira list - look for recent tickets with FreeCodeCamp label
        result = subprocess.run(
            ['jira', 'issue', 'list', '-p', JIRA_PROJECT, '-l', 'FreeCodeCamp', '--plain', '--created', 'month'],
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
    author = article.get('author', 'Unknown')
    categories = article.get('categories', [])
    categories_str = ', '.join(categories) if categories else 'None'

    description = f"""FreeCodeCamp Article

**Article URL:** {url}
**Published:** {pub_date}
**Author:** {author}
**Categories:** {categories_str}
**Source:** FreeCodeCamp (freecodecamp.org)

To be reviewed for relevance to Jaxon Digital's AI agent initiatives and technical infrastructure.
"""

    if dry_run:
        print(f"  [DRY RUN] Would create ticket: {title}")
        return ("DRY-RUN-XXX", True)

    # Write description to temp file
    temp_file = f'/tmp/freecodecamp-ticket-{int(time.time())}.txt'
    try:
        with open(temp_file, 'w') as f:
            f.write(description)

        # Get JIRA API token
        if not os.path.exists(JIRA_TOKEN_FILE):
            print(f"  ✗ Error: JIRA token file not found: {JIRA_TOKEN_FILE}")
            return (None, False)

        # Create JIRA ticket with FreeCodeCamp label
        cmd = [
            'jira', 'issue', 'create',
            '-p', JIRA_PROJECT,
            '-t', 'Task',
            '-s', title,
            '-b', description,
            '-l', 'FreeCodeCamp',
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
        try:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
        except:
            pass


def main():
    parser = argparse.ArgumentParser(description='Monitor FreeCodeCamp blog for new articles')
    parser.add_argument('--backfill', action='store_true', help='Process all articles (initial run)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be created without creating tickets')
    parser.add_argument('--output-json', type=str, help='Output metadata JSON file for assessment')
    args = parser.parse_args()

    # Load state
    state = load_state()

    # Fetch articles from RSS
    articles = fetch_rss_feed()

    if args.backfill:
        print("\n=== BACKFILL MODE: Processing all articles ===")
        new_articles = articles
    else:
        print("\n=== INCREMENTAL MODE: Processing only new articles ===")
        seen_guids = set(state.get('seen_guids', []))
        new_articles = [a for a in articles if a['guid'] not in seen_guids]
        print(f"Found {len(new_articles)} new articles (out of {len(articles)} total)")

    # Filter out video content
    text_articles = [a for a in new_articles if not a['is_video']]
    video_count = len(new_articles) - len(text_articles)

    if video_count > 0:
        print(f"\n⏩ Skipping {video_count} video article(s)")

    if not text_articles:
        print("\nNo new text articles to process.")
        return

    print(f"\n=== NEW ARTICLES TO PROCESS ({len(text_articles)}) ===")
    for i, article in enumerate(text_articles, 1):
        categories_str = ', '.join(article['categories'][:3]) if article['categories'] else 'None'
        print(f"{i:2}. [{article['pub_date'][:10] if article['pub_date'] else 'Unknown'}] {article['title']}")
        print(f"    Author: {article['author']}")
        print(f"    Categories: {categories_str}")
        print(f"    URL: {article['url']}")

    # Create JIRA tickets
    print(f"\n=== CREATING JIRA TICKETS ===")
    created_tickets = {}
    failed_tickets = []
    skipped_tickets = []

    for i, article in enumerate(text_articles, 1):
        title = article['title']
        url = article['url']

        print(f"[{i}/{len(text_articles)}] {title[:70]}...")

        # Check if ticket already exists
        existing_ticket, exists = check_existing_ticket_by_url(url, state)
        if exists:
            print(f"  ⏩ Skipped (ticket {existing_ticket} already exists)")
            skipped_tickets.append(url)
            created_tickets[url] = existing_ticket
            continue

        # Create ticket
        ticket_id, success = create_jira_ticket_direct(article, dry_run=args.dry_run)

        if success:
            print(f"  ✓ Created {ticket_id}")
            created_tickets[url] = ticket_id
            # Update state immediately
            if article['guid'] not in state.get('seen_guids', []):
                state['seen_guids'].append(article['guid'])
            state['created_tickets'][article['guid']] = ticket_id
            state['url_to_ticket'][url] = ticket_id
            if not args.dry_run:
                save_state(state)
        else:
            print(f"  ✗ Failed")
            failed_tickets.append(url)

        # Rate limiting
        if not args.dry_run and i < len(text_articles):
            time.sleep(1)

    # Update state with final results
    state['last_check'] = datetime.now().isoformat()
    if not args.dry_run:
        save_state(state)

    # Output metadata JSON for assessment
    if args.output_json:
        # Build metadata with ticket IDs
        metadata = []
        for article in text_articles:
            if article['url'] in created_tickets:
                metadata.append({
                    'title': article['title'],
                    'url': article['url'],
                    'ticket_id': created_tickets[article['url']],
                    'author': article['author'],
                    'categories': article['categories'],
                    'pub_date': article['pub_date'],
                    'article_text': article['article_text'],
                    'source': 'FreeCodeCamp'
                })

        with open(args.output_json, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"\nMetadata written to: {args.output_json}")

    # Summary
    print(f"\n=== SUMMARY ===")
    print(f"Total new articles: {len(text_articles)}")
    print(f"Tickets created: {len(created_tickets) - len(skipped_tickets)}")
    print(f"Skipped (duplicates): {len(skipped_tickets)}")
    print(f"Failed: {len(failed_tickets)}")
    print(f"Videos skipped: {video_count}")

    if not args.dry_run:
        print(f"\nState file updated: {STATE_FILE}")

    if created_tickets:
        print(f"\nCreated tickets:")
        for url, ticket_id in created_tickets.items():
            if url not in skipped_tickets:
                # Find article title
                article_title = next((a['title'] for a in text_articles if a['url'] == url), url)
                print(f"  {ticket_id}: {article_title[:70]}")


if __name__ == '__main__':
    main()
