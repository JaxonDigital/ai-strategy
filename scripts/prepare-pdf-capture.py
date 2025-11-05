#!/usr/bin/env python3
"""
Extract article list from Medium email and generate PDF capture instructions.
This ensures PDFs are captured with the CORRECT filenames from the start.

Usage:
    python3 prepare-pdf-capture.py [EMAIL_PATH]
    
If EMAIL_PATH is not provided, auto-detects latest .eml file from inputs/
    
Output:
    - Prints numbered list of articles with URLs
    - Prints exact PDF filenames to use
    - Saves article list to /tmp for later use
"""

import sys
import os
import email
import re
from html import unescape
from pathlib import Path
import json

def find_latest_email():
    """Find the most recent .eml file in inputs directory."""
    inputs_dir = Path(__file__).parent.parent / 'inputs'
    
    eml_files = list(inputs_dir.glob('*.eml'))
    if not eml_files:
        return None
    
    # Sort by modification time, most recent first
    latest = max(eml_files, key=lambda p: p.stat().st_mtime)
    return str(latest)

def slugify(text):
    """Convert text to URL-safe slug."""
    # Remove special characters, convert to lowercase
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')

def extract_articles(email_path):
    """Extract article titles and URLs from Medium email."""
    with open(email_path, 'r') as f:
        msg = email.message_from_file(f)
    
    # Get HTML body
    body = ''
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == 'text/html':
                body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                break
    else:
        body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
    
    # Unescape HTML entities
    body = unescape(body)
    
    # Extract article titles and URLs
    # Pattern: <h2...>Title</h2> followed by URL
    articles = []
    
    # Find all article blocks
    article_pattern = r'<h2[^>]*>([^<]+)</h2>.*?href="(https://medium\.com/@[^"]+)"'
    
    for match in re.finditer(article_pattern, body, re.DOTALL):
        title = match.group(1).strip()
        url = match.group(2).strip()
        
        # Clean URL (remove tracking parameters)
        url = url.split('?')[0]
        
        # Skip if title looks like navigation/UI
        if title in ['Open in app', 'Sign up', 'Sign in', 'Get started']:
            continue
        
        articles.append({
            'title': title,
            'url': url,
            'slug': slugify(title)
        })
    
    # Deduplicate by URL
    seen_urls = set()
    unique_articles = []
    for article in articles:
        if article['url'] not in seen_urls:
            seen_urls.add(article['url'])
            unique_articles.append(article)
    
    return unique_articles

def main():
    # Get email path
    if len(sys.argv) > 1:
        email_path = sys.argv[1]
    else:
        email_path = find_latest_email()
        if not email_path:
            print("Error: No .eml files found in inputs/ directory", file=sys.stderr)
            sys.exit(1)
        print(f"🔍 Auto-detected email: {email_path}\n")
    
    if not os.path.exists(email_path):
        print(f"Error: Email file not found: {email_path}", file=sys.stderr)
        sys.exit(1)
    
    # Extract articles
    articles = extract_articles(email_path)
    
    if not articles:
        print("Error: No articles found in email", file=sys.stderr)
        sys.exit(1)
    
    print("=" * 70)
    print("MEDIUM ARTICLE PDF CAPTURE GUIDE")
    print("=" * 70)
    print(f"Found {len(articles)} articles\n")
    
    print("STEP 1: Navigate to each article and save as PDF with these EXACT filenames:")
    print()
    
    # Print numbered list with exact filenames
    for i, article in enumerate(articles, 1):
        filename = f"{i:02d}-{article['slug']}.pdf"
        print(f"{i}. {article['title']}")
        print(f"   URL: {article['url']}")
        print(f"   📄 SAVE AS: {filename}")
        print()
    
    print("=" * 70)
    print()
    print("STEP 2: After saving all PDFs, run:")
    print(f"  python3 scripts/extract-medium-articles.py \\")
    print(f"      --create-tickets \\")
    print(f"      --upload-to-drive pdfs/medium-articles-$(date +%Y-%m-%d)/ \\")
    print(f"      --output-json /tmp/medium-articles-$(date +%Y-%m-%d).json")
    print()
    
    # Save article list for reference
    output_file = '/tmp/medium-pdf-capture-list.json'
    with open(output_file, 'w') as f:
        json.dump({
            'email_path': email_path,
            'articles': articles
        }, f, indent=2)
    
    print(f"✓ Article list saved to: {output_file}")

if __name__ == '__main__':
    main()
