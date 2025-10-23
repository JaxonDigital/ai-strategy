#!/usr/bin/env python3
"""
Capture Optimizely World blog articles as PDFs.

Uses hybrid strategy:
1. Try direct HTML fetch + conversion to PDF
2. Fall back to manual Playwright capture if needed

Usage:
    python3 scripts/capture-optimizely-articles.py /tmp/optimizely-articles.json /Users/bgerby/Desktop/optimizely-articles-2025-10-23
"""

import argparse
import json
import os
import sys
import urllib.request
import re
from pathlib import Path

def sanitize_filename(title):
    """Convert article title to safe filename."""
    # Remove special characters, replace spaces with hyphens
    filename = re.sub(r'[^\w\s-]', '', title.lower())
    filename = re.sub(r'[-\s]+', '-', filename)
    return filename[:100]  # Limit length


def fetch_article_html(url):
    """Fetch article HTML content."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        req = urllib.request.Request(url, headers=headers)

        with urllib.request.urlopen(req) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"  Error fetching HTML: {e}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(
        description='Capture Optimizely World articles as PDFs'
    )
    parser.add_argument('metadata_json', help='JSON file with article metadata from monitor script')
    parser.add_argument('output_dir', help='Output directory for PDFs')
    parser.add_argument('--playwright', action='store_true',
                        help='Use Playwright for all captures (skip HTML fetch)')

    args = parser.parse_args()

    # Load metadata
    if not os.path.exists(args.metadata_json):
        print(f"Error: Metadata file not found: {args.metadata_json}", file=sys.stderr)
        sys.exit(1)

    with open(args.metadata_json, 'r') as f:
        metadata = json.load(f)

    articles = metadata.get('articles', [])
    if not articles:
        print("No articles found in metadata file.")
        return

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Capturing {len(articles)} articles to {output_dir}/")
    print()

    # Track which articles need Playwright
    playwright_needed = []

    for i, article in enumerate(articles, 1):
        title = article['title']
        url = article['url']
        filename = f"{i:02d}-{sanitize_filename(title)}.pdf"
        output_path = output_dir / filename

        print(f"[{i}/{len(articles)}] {title}")
        print(f"  URL: {url}")

        if args.playwright:
            # Skip HTML fetch, use Playwright for all
            playwright_needed.append({
                'number': i,
                'title': title,
                'url': url,
                'filename': filename
            })
            print(f"  Status: Queued for Playwright capture")
        else:
            # Try HTML fetch first
            html = fetch_article_html(url)
            if html and len(html) > 5000:  # Reasonable threshold
                # HTML fetched successfully
                # Note: Converting HTML to PDF programmatically is complex
                # For now, mark for Playwright capture
                playwright_needed.append({
                    'number': i,
                    'title': title,
                    'url': url,
                    'filename': filename
                })
                print(f"  Status: HTML fetched ({len(html)} bytes), queued for Playwright PDF")
            else:
                # HTML fetch failed or too small
                playwright_needed.append({
                    'number': i,
                    'title': title,
                    'url': url,
                    'filename': filename
                })
                print(f"  Status: HTML fetch failed, queued for Playwright")

        print()

    # Summary
    print(f"\n=== CAPTURE SUMMARY ===")
    print(f"Total articles: {len(articles)}")
    print(f"Playwright capture needed: {len(playwright_needed)}")

    if playwright_needed:
        print(f"\n=== PLAYWRIGHT CAPTURE INSTRUCTIONS ===")
        print(f"Use Claude Code or Playwright MCP to capture these articles:\n")
        print(f"Output directory: {output_dir}\n")

        for item in playwright_needed:
            print(f"Article {item['number']}: {item['title']}")
            print(f"  URL: {item['url']}")
            print(f"  Filename: {item['filename']}")
            print()

        # Save Playwright manifest
        manifest_path = output_dir / 'playwright-manifest.json'
        with open(manifest_path, 'w') as f:
            json.dump({
                'output_dir': str(output_dir),
                'articles': playwright_needed
            }, f, indent=2)
        print(f"Playwright manifest saved to: {manifest_path}")
        print()
        print("To capture with Playwright MCP:")
        print("  1. Open browser: mcp__playwright__playwright_navigate(url, headless=false)")
        print("  2. Save PDF: mcp__playwright__playwright_save_as_pdf(name=filename, outputPath=output_dir, fullPage=true)")
        print("  3. Repeat for each article (browser stays open)")
        print("  4. Close browser: mcp__playwright__playwright_close()")


if __name__ == '__main__':
    main()
