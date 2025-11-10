#!/usr/bin/env python3
"""
Extract all Medium articles from daily digest email and create Jira tickets.

Usage:
    python3 extract-medium-articles.py [/path/to/email.eml] [--create-tickets] [--output-json FILE] [--upload-to-drive PDF_DIR]

    If email path is not provided, automatically detects the most recent .eml file in inputs/ directory.

Options:
    --create-tickets         Automatically create Jira tickets for all articles
    --output-json FILE       Write article metadata to JSON file for Claude Code integration
    --upload-to-drive DIR    Upload PDFs from DIR to Google Drive and include links in JIRA tickets
                             REQUIRED when using --create-tickets (PDF links mandatory)

Best Practice:
    Always use --upload-to-drive when creating tickets to ensure PDF links are included:
    python3 extract-medium-articles.py --create-tickets --upload-to-drive /path/to/pdfs/
"""

import re
import base64
import sys
import subprocess
import os
import json
from datetime import datetime
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

def extract_articles(email_path):
    """Extract all Medium article URLs from email file."""
    with open(email_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    articles = []  # Changed from set to list to preserve document order
    seen = set()   # Track duplicates separately
    in_base64 = False
    base64_content = []

    for line in lines:
        if 'Content-Transfer-Encoding: base64' in line:
            in_base64 = True
            continue

        if in_base64:
            # Stop at boundary or next header
            if line.startswith('--') or line.startswith('Content-'):
                if base64_content:
                    try:
                        decoded = base64.b64decode(''.join(base64_content)).decode('utf-8', errors='ignore')
                        # Extract Medium article URLs - two patterns:
                        # 1. User articles: medium.com/@username/article-slug-12digitid
                        # 2. Publication articles: medium.com/publication/article-slug-12digitid

                        # Pattern 1: @username articles (original pattern)
                        user_urls = re.findall(r'https://medium\.com/@[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+-[a-f0-9]{12}', decoded)
                        for url in user_urls:
                            if url not in seen:
                                seen.add(url)
                                articles.append(url)

                        # Pattern 2: Publication articles (new pattern for "FROM YOUR FOLLOWING" section)
                        # Match medium.com/publication-name/article-slug-12digitid
                        # Exclude common non-article paths like /plans, /jobs-at-medium, etc.
                        pub_urls = re.findall(r'https://medium\.com/(?!plans|jobs-at-medium|@)[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+-[a-f0-9]{12}', decoded)
                        for url in pub_urls:
                            if url not in seen:
                                seen.add(url)
                                articles.append(url)
                    except:
                        pass
                    base64_content = []
                in_base64 = False
            else:
                base64_content.append(line.strip())

    return articles  # Removed sorted() to preserve document order

def extract_title_from_url(url):
    """Extract readable title from Medium URL slug."""
    # Get the slug part after the last /
    slug = url.split('/')[-1]
    # Split on hyphens and capitalize
    words = slug.split('-')
    # Remove article ID at end (format: word-word-abc123def)
    if len(words[-1]) == 12 and any(c.isalpha() for c in words[-1]) and any(c.isdigit() for c in words[-1]):
        words = words[:-1]
    # Capitalize and join
    title = ' '.join(word.capitalize() for word in words)
    return title

def get_drive_service():
    """Get Google Drive API service using token from MCP server."""
    # Use the token from the MCP server
    token_path = '/Users/bgerby/Documents/dev/ai/mcp-googledocs-server/token.json'

    if not os.path.exists(token_path):
        raise Exception(f"Google Drive token not found at {token_path}")

    with open(token_path, 'r') as f:
        token_data = json.load(f)

    creds = Credentials(
        token=token_data.get('access_token'),
        refresh_token=token_data.get('refresh_token'),
        token_uri='https://oauth2.googleapis.com/token',
        client_id=token_data.get('client_id'),
        client_secret=token_data.get('client_secret')
    )

    # Refresh if needed
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        # Update token file
        token_data['access_token'] = creds.token
        with open(token_path, 'w') as f:
            json.dump(token_data, f)

    return build('drive', 'v3', credentials=creds)

def get_or_create_folder(service, folder_name, parent_id):
    """Get folder ID or create it if it doesn't exist."""
    # Search for existing folder
    query = f"name='{folder_name}' and '{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name)',
        supportsAllDrives=True,
        includeItemsFromAllDrives=True
    ).execute()

    folders = results.get('files', [])
    if folders:
        return folders[0]['id']

    # Create folder
    folder_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id]
    }
    folder = service.files().create(
        body=folder_metadata,
        fields='id',
        supportsAllDrives=True
    ).execute()

    return folder['id']

def upload_file_to_drive(service, file_path, parent_folder_id):
    """Upload file to Google Drive and return file ID."""
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

    return file['id'], file['webViewLink']

def get_shareable_link(service, file_id):
    """Make file publicly viewable and return shareable link."""
    # Set permission to anyone with link can view
    permission = {
        'type': 'anyone',
        'role': 'reader'
    }
    service.permissions().create(
        fileId=file_id,
        body=permission,
        supportsAllDrives=True
    ).execute()

    # Get the web view link
    file = service.files().get(
        fileId=file_id,
        fields='webViewLink',
        supportsAllDrives=True
    ).execute()

    return file['webViewLink']

def update_jira_description(ticket_id, url, drive_link):
    """Update JIRA ticket description with Drive link."""
    jira_token = os.popen('cat ~/.jira.d/.pass').read().strip()

    new_description = f"""Medium Article Review

**Article URL:** {url}
**PDF:** {drive_link}

To be reviewed for relevance to Jaxon Digital's AI agent initiatives."""

    # Use JIRA CLI to update description
    cmd = [
        'jira', 'issue', 'edit',
        ticket_id,
        '-b', new_description
    ]

    env = os.environ.copy()
    env['JIRA_API_TOKEN'] = jira_token

    result = subprocess.run(cmd, env=env, capture_output=True, text=True)
    return result.returncode == 0

def create_jira_ticket(url, title, pdf_link=None):
    """Create a Jira ticket for the article with PDF link."""
    jira_token = os.popen('cat ~/.jira.d/.pass').read().strip()

    summary = f"Review: {title}"

    # Include PDF link in description if provided
    body = f"""Medium Article Review

**Article URL:** {url}"""

    if pdf_link:
        body += f"""

**PDF:** {pdf_link}"""

    body += """

To be reviewed for relevance to Jaxon Digital's AI agent initiatives."""

    cmd = [
        'jira', 'issue', 'create',
        '-p', 'GAT',
        '-t', 'Task',
        '-s', summary,
        '-b', body,
        '--label', 'Medium'
    ]

    env = os.environ.copy()
    env['JIRA_API_TOKEN'] = jira_token

    result = subprocess.run(cmd, env=env, capture_output=True, text=True)

    if result.returncode == 0:
        # Extract ticket number from output
        match = re.search(r'GAT-\d+', result.stdout)
        if match:
            return match.group(0)

    return None

def auto_detect_latest_email():
    """Auto-detect the most recent .eml file in inputs/ directory."""
    script_dir = Path(__file__).parent
    inputs_dir = script_dir.parent / "inputs"

    if not inputs_dir.exists():
        return None

    email_files = sorted(inputs_dir.glob("*.eml"), key=lambda p: p.stat().st_mtime, reverse=True)

    if email_files:
        return str(email_files[0])

    return None

def main():
    # Parse arguments manually (simple approach)
    email_path = None
    create_tickets = '--create-tickets' in sys.argv

    # Check if first arg is email path (doesn't start with --)
    if len(sys.argv) >= 2 and not sys.argv[1].startswith('--'):
        email_path = sys.argv[1]

    # Auto-detect if not provided
    if not email_path:
        email_path = auto_detect_latest_email()
        if email_path:
            print(f"🔍 Auto-detected Medium email: {email_path}\n")
        else:
            print("❌ Error: No email file found in inputs/ directory")
            print(__doc__)
            sys.exit(1)

    # Check for --output-json flag
    output_json = None
    for i, arg in enumerate(sys.argv):
        if arg == '--output-json' and i + 1 < len(sys.argv):
            output_json = sys.argv[i + 1]
            break

    # Check for --upload-to-drive flag
    upload_to_drive = None
    for i, arg in enumerate(sys.argv):
        if arg == '--upload-to-drive' and i + 1 < len(sys.argv):
            upload_to_drive = sys.argv[i + 1]
            break

    print(f"Extracting articles from: {email_path}")
    articles = extract_articles(email_path)

    print(f"\nFound {len(articles)} articles:\n")

    # Store article metadata for JSON output
    article_data = []
    current_date = datetime.now().strftime('%Y-%m-%d')

    # Google Drive setup
    drive_service = None
    if upload_to_drive:
        print("Initializing Google Drive service...")
        drive_service = get_drive_service()

        # Shared Drive ID and folder structure
        SHARED_DRIVE_ID = '0ALLCxnOLmj3bUk9PVA'
        date_obj = datetime.now()
        year = date_obj.strftime('%Y')
        month = date_obj.strftime('%m-%B')  # e.g., "10-October"
        day = date_obj.strftime('%d')

        # Create folder structure: Year/Month/Day/PDFs
        year_folder = get_or_create_folder(drive_service, year, SHARED_DRIVE_ID)
        month_folder = get_or_create_folder(drive_service, month, year_folder)
        day_folder = get_or_create_folder(drive_service, day, month_folder)
        pdfs_folder = get_or_create_folder(drive_service, 'PDFs', day_folder)

        print(f"✓ Drive folder ready: {year}/{month}/{day}/PDFs\n")

    for i, url in enumerate(articles, 1):
        title = extract_title_from_url(url)
        print(f"{i:2d}. {title}")
        print(f"    {url}")

        # Upload to Drive FIRST if requested (required for ticket creation)
        drive_link = None
        if upload_to_drive:
            # Look for PDF file
            pdf_filename = f"{i:02d}-{title.lower().replace(' ', '-')}.pdf"
            pdf_path = os.path.join(upload_to_drive, pdf_filename)

            if os.path.exists(pdf_path):
                try:
                    file_id, web_link = upload_file_to_drive(drive_service, pdf_path, pdfs_folder)
                    drive_link = get_shareable_link(drive_service, file_id)
                    print(f"    ✓ Uploaded to Drive: {drive_link}")
                except Exception as e:
                    print(f"    ✗ Upload failed: {e}")
            else:
                print(f"    ⚠ PDF not found: {pdf_path}")

        # Create ticket with PDF link (or without if --upload-to-drive not used)
        ticket_id = None
        if create_tickets:
            # Require PDF upload if --upload-to-drive was specified
            if upload_to_drive and not drive_link:
                print(f"    ✗ Skipping ticket creation - PDF upload required but failed")
            else:
                ticket_id = create_jira_ticket(url, title, drive_link)
                if ticket_id:
                    print(f"    ✓ Created {ticket_id}")
                else:
                    print(f"    ✗ Failed to create ticket")

        # Add to metadata
        article_data.append({
            'number': i,
            'title': title,
            'url': url,
            'ticket_id': ticket_id,
            'drive_link': drive_link,
            'date': current_date
        })
        print()

    print(f"\nTotal: {len(articles)} articles")

    if not create_tickets:
        print("\nTo create Jira tickets, run with --create-tickets flag")

    if not upload_to_drive:
        print("To upload PDFs to Drive, run with --upload-to-drive PDF_DIR flag")

    # Write JSON output if requested
    if output_json:
        with open(output_json, 'w') as f:
            json.dump({
                'date': current_date,
                'email_path': email_path,
                'articles': article_data
            }, f, indent=2)
        print(f"\n✓ Wrote article metadata to {output_json}")

if __name__ == '__main__':
    main()
