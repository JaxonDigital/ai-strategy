#!/usr/bin/env python3.11
"""
Process manually selected articles (not from email digest).

Usage:
    python3.11 scripts/process-manual-articles.py \
        --pdf-dir pdfs/manual-batch-YYYY-MM-DD \
        --url "https://pub.towardsai.net/article-1" \
        --url "https://medium.com/@author/article-2" \
        [--url "..." ...]

What it does:
    1. Creates metadata JSON for articles
    2. Uploads PDFs to Google Drive
    3. Creates JIRA tickets with PDF links
    4. Generates AI assessment
    5. Generates audio for HIGH priority articles
    6. Updates JIRA with assessments and audio
    7. Regenerates and pushes RSS feed

Prerequisites:
    - PDFs must be captured first (via Playwright)
    - PDF filenames: 01-article-title.pdf, 02-article-title.pdf, etc.
    - Must be run from repository root
"""

import sys
import os
import json
import subprocess
import argparse
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request


def get_drive_service():
    """Get Google Drive API service."""
    token_path = '/Users/bgerby/Documents/dev/ai/mcp-googledocs-server/token.json'

    with open(token_path, 'r') as f:
        token_data = json.load(f)

    creds = Credentials(
        token=token_data.get('access_token'),
        refresh_token=token_data.get('refresh_token'),
        token_uri='https://oauth2.googleapis.com/token',
        client_id=token_data.get('client_id'),
        client_secret=token_data.get('client_secret')
    )

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        token_data['access_token'] = creds.token
        with open(token_path, 'w') as f:
            json.dump(token_data, f)

    return build('drive', 'v3', credentials=creds)


def upload_file_to_drive(service, file_path, parent_folder_id):
    """Upload file to Google Drive and return shareable link."""
    file_name = os.path.basename(file_path)
    file_metadata = {
        'name': file_name,
        'parents': [parent_folder_id]
    }

    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id,webViewLink',
        supportsAllDrives=True
    ).execute()

    # Make publicly viewable
    permission = {
        'type': 'anyone',
        'role': 'reader'
    }
    service.permissions().create(
        fileId=file['id'],
        body=permission,
        supportsAllDrives=True
    ).execute()

    return file['webViewLink']


def create_jira_ticket(title, url, drive_link):
    """Create JIRA ticket and return ticket ID."""
    jira_token = os.popen('cat ~/.jira.d/.pass').read().strip()

    description = f"""Medium Article Review

**Article URL:** {url}
**PDF:** {drive_link}

To be reviewed for relevance to Jaxon Digital's AI agent initiatives."""

    # Write description to temp file (multi-line descriptions need this)
    desc_file = '/tmp/jira-test-desc.txt'
    with open(desc_file, 'w') as f:
        f.write(description)

    # Use bash subprocess with full command (pattern from CLAUDE.md)
    bash_command = f'JIRA_API_TOKEN="`cat ~/.jira.d/.pass`" /usr/local/bin/jira issue create -p GAT -t Task -s "{title}" -b "$(cat {desc_file})" --no-input'

    result = subprocess.run(
        ['/bin/bash', '-c', bash_command],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        # Extract ticket ID from output
        import re
        for line in result.stdout.split('\n'):
            if 'GAT-' in line:
                # Extract just the ticket ID (GAT-XXX) from URLs or plain text
                match = re.search(r'(GAT-\d+)', line)
                if match:
                    return match.group(1)

    raise Exception(f"Failed to create JIRA ticket: {result.stderr}")


def update_jira_with_assessment(ticket_id, assessment_text):
    """Update JIRA ticket with assessment."""
    # Write assessment to temp file (multi-line text)
    desc_file = '/tmp/jira-update-desc.txt'
    with open(desc_file, 'w') as f:
        f.write(assessment_text)

    # Use bash subprocess with full command (pattern from CLAUDE.md)
    bash_command = f'JIRA_API_TOKEN="`cat ~/.jira.d/.pass`" /usr/local/bin/jira issue edit {ticket_id} -b "$(cat {desc_file})" --no-input'

    result = subprocess.run(
        ['/bin/bash', '-c', bash_command],
        capture_output=True,
        text=True
    )

    return result.returncode == 0


def slugify(text):
    """Convert text to URL-safe slug."""
    text = text.lower()
    text = text.replace(' ', '-')
    # Remove special characters
    import re
    text = re.sub(r'[^a-z0-9-]', '', text)
    return text


def main():
    parser = argparse.ArgumentParser(description='Process manually selected articles')
    parser.add_argument('--pdf-dir', required=True, help='Directory containing PDFs (e.g., pdfs/manual-batch-YYYY-MM-DD)')
    parser.add_argument('--url', action='append', dest='urls', required=True, help='Article URL (can be specified multiple times)')
    args = parser.parse_args()

    # Validate OPENAI_API_KEY is set
    if not os.environ.get('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("Set it with: export OPENAI_API_KEY='sk-proj-...'")
        sys.exit(1)

    pdf_dir = args.pdf_dir
    urls = args.urls

    # Validate PDF directory exists
    if not os.path.exists(pdf_dir):
        print(f"❌ Error: PDF directory not found: {pdf_dir}")
        sys.exit(1)

    # Get list of PDFs
    pdfs = sorted([f for f in os.listdir(pdf_dir) if f.endswith('.pdf')])

    if len(pdfs) != len(urls):
        print(f"❌ Error: Found {len(pdfs)} PDFs but {len(urls)} URLs provided")
        print(f"PDFs: {pdfs}")
        sys.exit(1)

    print(f"\n{'='*70}")
    print(f"PROCESSING {len(urls)} MANUAL ARTICLES")
    print(f"{'='*70}\n")

    # Initialize Google Drive service
    drive_service = get_drive_service()
    folder_id = '0ALLCxnOLmj3bUk9PVA'  # Shared Drive root

    # Process each article
    articles = []
    for i, (url, pdf_filename) in enumerate(zip(urls, pdfs), 1):
        print(f"[{i}/{len(urls)}] {pdf_filename}")

        # Extract title from PDF filename (remove number prefix and .pdf)
        title_slug = pdf_filename[3:-4]  # Remove "01-" and ".pdf"
        title = title_slug.replace('-', ' ').title()

        pdf_path = os.path.join(pdf_dir, pdf_filename)

        # Upload PDF
        print(f"  → Uploading to Drive...")
        drive_link = upload_file_to_drive(drive_service, pdf_path, folder_id)
        print(f"  ✓ Uploaded: {drive_link}")

        # Create JIRA ticket
        print(f"  → Creating JIRA ticket...")
        ticket_id = create_jira_ticket(title, url, drive_link)
        print(f"  ✓ Created: {ticket_id}")

        # Add to articles list
        articles.append({
            'number': i,
            'title': title.replace(' ', ' ').strip(),  # Normalize spaces
            'url': url,
            'ticket_id': ticket_id,
            'drive_link': drive_link,
            'date': datetime.now().strftime('%Y-%m-%d')
        })

        print()

    # Create metadata JSON
    metadata_file = '/tmp/manual-articles-metadata.json'
    with open(metadata_file, 'w') as f:
        json.dump({'articles': articles}, f, indent=2)
    print(f"✓ Created metadata: {metadata_file}\n")

    # Generate assessment
    assessment_file = '/tmp/manual-articles-assessment.md'
    print(f"{'='*70}")
    print("GENERATING ASSESSMENT")
    print(f"{'='*70}\n")

    result = subprocess.run(
        ['python3.11', 'scripts/generate-article-assessment.py', pdf_dir, metadata_file, assessment_file],
        env={**os.environ, 'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY', '')},
        cwd='/Users/bgerby/Documents/dev/ai'
    )

    if result.returncode != 0:
        print("❌ Assessment generation failed")
        sys.exit(1)

    print(f"\n✓ Assessment complete: {assessment_file}\n")

    # Parse assessment to get priorities and update JIRA
    print(f"{'='*70}")
    print("UPDATING JIRA TICKETS")
    print(f"{'='*70}\n")

    with open(assessment_file, 'r') as f:
        assessment_content = f.read()

    # Extract article sections from assessment
    for article in articles:
        ticket_id = article['ticket_id']
        article_num = article['number']

        # Find article section in assessment (between ARTICLE-XX headers)
        import re
        pattern = rf'### ARTICLE-{article_num:02d}.*?(?=### ARTICLE-|\Z)'
        match = re.search(pattern, assessment_content, re.DOTALL)

        if match:
            article_section = match.group(0)

            # Build updated description
            updated_desc = f"""Medium Article Review

**Article URL:** {article['url']}
**PDF:** {article['drive_link']}

---

{article_section}"""

            print(f"  → Updating {ticket_id}...")
            if update_jira_with_assessment(ticket_id, updated_desc):
                print(f"  ✓ Updated {ticket_id}")
            else:
                print(f"  ⚠ Failed to update {ticket_id}")

    print()

    # Generate audio for HIGH priority articles
    print(f"{'='*70}")
    print("GENERATING AUDIO (HIGH PRIORITY ONLY)")
    print(f"{'='*70}\n")

    result = subprocess.run(
        ['python3.11', 'scripts/generate-audio-from-assessment.py', pdf_dir, assessment_file],
        env={**os.environ, 'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY', '')},
        cwd='/Users/bgerby/Documents/dev/ai'
    )

    if result.returncode != 0:
        print("⚠ Audio generation encountered issues (may be expected for MEDIUM/LOW priority)")
    else:
        print("\n✓ Audio generation complete\n")

    # Push RSS feed
    print(f"{'='*70}")
    print("PUBLISHING RSS FEED")
    print(f"{'='*70}\n")

    result = subprocess.run(
        'git add feed.rss && git commit -m "Add manual article episodes" && git push',
        shell=True,
        cwd='/Users/bgerby/Documents/dev/ai',
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print("✓ RSS feed published to GitHub\n")
    else:
        print("⚠ RSS feed update skipped (no changes or error)\n")

    # Summary
    print(f"{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}\n")
    print(f"Articles processed: {len(articles)}")
    print("\nTickets created:")
    for article in articles:
        print(f"  - {article['ticket_id']}: {article['title']}")
    print(f"\nAssessment: {assessment_file}")
    print(f"Metadata: {metadata_file}")
    print()


if __name__ == '__main__':
    main()
