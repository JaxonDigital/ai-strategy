#!/usr/bin/env python3.11
"""
Audit JIRA tickets for missing PDF links and upload/update them.

This script:
1. Finds JIRA tickets in GAT project (Medium articles)
2. Checks if they have PDF links in the description
3. Searches for corresponding PDFs in the pdfs/ directory
4. Uploads missing PDFs to Google Drive
5. Updates JIRA ticket descriptions with PDF links

Usage:
    # Audit only (no changes)
    python3 fix-missing-pdf-links.py --dry-run

    # Fix all missing PDF links
    python3 fix-missing-pdf-links.py

    # Fix specific date range
    python3 fix-missing-pdf-links.py --start-date 2025-10-25 --end-date 2025-10-29

Examples:
    python3 fix-missing-pdf-links.py --dry-run
    python3 fix-missing-pdf-links.py --start-date 2025-10-29
"""

import os
import sys
import json
import re
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from glob import glob

# Google Drive API imports
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

# Constants
JIRA_TOKEN_PATH = os.path.expanduser("~/.jira.d/.pass")
GOOGLE_TOKEN_PATH = "/Users/bgerby/Documents/dev/ai/mcp-googledocs-server/token.json"
PDFS_BASE_DIR = "/Users/bgerby/Documents/dev/ai/pdfs"
SHARED_DRIVE_ROOT = "0ALLCxnOLmj3bUk9PVA"

def get_jira_token() -> str:
    """Get JIRA API token."""
    if not os.path.exists(JIRA_TOKEN_PATH):
        raise Exception(f"JIRA token not found at {JIRA_TOKEN_PATH}")

    with open(JIRA_TOKEN_PATH, 'r') as f:
        return f.read().strip()

def get_drive_service():
    """Get Google Drive API service."""
    if not os.path.exists(GOOGLE_TOKEN_PATH):
        raise Exception(f"Google Drive token not found at {GOOGLE_TOKEN_PATH}")

    with open(GOOGLE_TOKEN_PATH, 'r') as f:
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
        with open(GOOGLE_TOKEN_PATH, 'w') as f:
            json.dump(token_data, f)

    return build('drive', 'v3', credentials=creds)

def get_jira_tickets(start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict]:
    """Get JIRA tickets from GAT project."""
    token = get_jira_token()

    # Build JQL query
    jql_parts = ['project = GAT', 'labels = Medium']

    if start_date:
        jql_parts.append(f'created >= "{start_date}"')
    if end_date:
        jql_parts.append(f'created <= "{end_date}"')

    jql = ' AND '.join(jql_parts)

    # Use jira CLI to get tickets
    env = os.environ.copy()
    env["JIRA_API_TOKEN"] = token

    cmd = ['jira', 'issue', 'list', '-p', 'GAT', '-q', jql, '--plain']

    try:
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            print(f"Warning: jira list failed: {result.stderr}")
            return []

        # Parse output (format: KEY    SUMMARY    STATUS)
        tickets = []
        for line in result.stdout.strip().split('\n'):
            if not line or line.startswith('KEY'):
                continue

            parts = line.split('\t')
            if len(parts) >= 1:
                tickets.append({'key': parts[0].strip()})

        return tickets

    except subprocess.TimeoutExpired:
        print("Warning: jira list timed out")
        return []
    except Exception as e:
        print(f"Warning: jira list error: {e}")
        return []

def get_ticket_details(ticket_key: str) -> Optional[Dict]:
    """Get JIRA ticket description."""
    token = get_jira_token()

    env = os.environ.copy()
    env["JIRA_API_TOKEN"] = token

    cmd = ['jira', 'issue', 'view', ticket_key]

    try:
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=10)

        if result.returncode != 0:
            return None

        # Parse the output to extract description
        output = result.stdout

        # Extract description section
        desc_match = re.search(r'Description[^\n]*\n+(.*?)\n+(?:Comments|View this issue)', output, re.DOTALL)
        description = desc_match.group(1).strip() if desc_match else ""

        return {
            'key': ticket_key,
            'description': description
        }

    except Exception as e:
        print(f"Error getting {ticket_key}: {e}")
        return None

def has_pdf_link(description: str) -> bool:
    """Check if description has PDF link."""
    # Look for **PDF:** or **PDF Link:** patterns
    return bool(re.search(r'\*\*PDF.*?:\*\*.*?https://drive\.google\.com', description, re.IGNORECASE))

def extract_article_url(description: str) -> Optional[str]:
    """Extract article URL from description."""
    # Look for **Article URL:** pattern
    match = re.search(r'\*\*Article URL:\*\*\s*(https?://[^\s]+)', description, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Fallback: look for any Medium URL
    match = re.search(r'(https://medium\.com/[^\s]+)', description)
    if match:
        return match.group(1).strip()

    return None

def find_pdf_for_ticket(ticket_key: str, article_url: Optional[str]) -> Optional[str]:
    """Find PDF file for a ticket."""
    # Search in pdfs/ directory for files matching the ticket or article
    pdf_patterns = [
        f"**/*{ticket_key}*.pdf",
        f"**/medium-articles-*/**.pdf"
    ]

    for pattern in pdf_patterns:
        pdf_files = glob(os.path.join(PDFS_BASE_DIR, pattern), recursive=True)

        if pdf_files:
            # If we have an article URL, try to match by title
            if article_url:
                article_slug = article_url.split('/')[-1].split('?')[0]

                for pdf_file in pdf_files:
                    if article_slug.lower().replace('-', '') in os.path.basename(pdf_file).lower().replace('-', ''):
                        return pdf_file

            # Otherwise return first match
            if pdf_files:
                return pdf_files[0]

    return None

def get_or_create_drive_folder(service, year: str, month: str, day: str) -> str:
    """Get or create Drive folder structure: 2025/10-October/29/PDFs/"""
    # Navigate folder structure
    # Start from shared drive root
    parent_id = SHARED_DRIVE_ROOT

    # Find or create year folder
    month_name = datetime.strptime(month, '%m').strftime('%B')
    folder_path = [
        ('2025', year),
        ('10-October', f'{month}-{month_name}'),
        (day, day),
        ('PDFs', 'PDFs')
    ]

    for folder_name, search_name in folder_path:
        # Search for folder
        query = f"name='{search_name}' and '{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"

        results = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)',
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
            corpora='drive',
            driveId=SHARED_DRIVE_ROOT
        ).execute()

        folders = results.get('files', [])

        if folders:
            parent_id = folders[0]['id']
        else:
            # Create folder
            file_metadata = {
                'name': search_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_id]
            }

            folder = service.files().create(
                body=file_metadata,
                fields='id',
                supportsAllDrives=True
            ).execute()

            parent_id = folder['id']

    return parent_id

def upload_pdf_to_drive(service, pdf_path: str, ticket_key: str) -> str:
    """Upload PDF to Google Drive and return shareable link."""
    # Determine date from ticket key or file path
    # For now, use today's date
    now = datetime.now()
    year = now.strftime('%Y')
    month = now.strftime('%m')
    day = now.strftime('%d')

    # Get/create folder
    folder_id = get_or_create_drive_folder(service, year, month, day)

    # Upload file
    file_metadata = {
        'name': os.path.basename(pdf_path),
        'parents': [folder_id]
    }

    media = MediaFileUpload(pdf_path, mimetype='application/pdf', resumable=True)

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id,webViewLink',
        supportsAllDrives=True
    ).execute()

    # Make shareable (already done by shared drive permissions)

    return file['webViewLink']

def update_jira_description(ticket_key: str, pdf_link: str, current_description: str) -> bool:
    """Update JIRA ticket description with PDF link."""
    token = get_jira_token()

    # Insert PDF link after Article URL
    if '**Article URL:**' in current_description:
        # Find insertion point
        lines = current_description.split('\n')
        new_lines = []

        for line in lines:
            new_lines.append(line)
            if line.strip().startswith('**Article URL:**'):
                # Add PDF link after Article URL
                new_lines.append('')
                new_lines.append(f'**PDF:** {pdf_link}')

        new_description = '\n'.join(new_lines)
    else:
        # Prepend PDF link
        new_description = f'**PDF:** {pdf_link}\n\n{current_description}'

    # Update ticket
    env = os.environ.copy()
    env["JIRA_API_TOKEN"] = token

    # Write description to temp file
    with open('/tmp/jira_desc.txt', 'w') as f:
        f.write(new_description)

    cmd = ['jira', 'issue', 'edit', ticket_key, '--no-input', '-b', new_description]

    try:
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except Exception as e:
        print(f"Error updating {ticket_key}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Audit and fix missing PDF links in JIRA tickets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument('--dry-run', action='store_true',
                       help="Show what would be done without making changes")
    parser.add_argument('--start-date',
                       help="Start date (YYYY-MM-DD)")
    parser.add_argument('--end-date',
                       help="End date (YYYY-MM-DD)")

    args = parser.parse_args()

    print("Auditing JIRA tickets for missing PDF links...")
    print(f"Dry run: {args.dry_run}")

    # Get tickets
    tickets = get_jira_tickets(args.start_date, args.end_date)
    print(f"Found {len(tickets)} tickets to check\n")

    # Initialize Drive service
    if not args.dry_run:
        drive_service = get_drive_service()
    else:
        drive_service = None

    missing_count = 0
    fixed_count = 0
    error_count = 0

    for ticket in tickets:
        ticket_key = ticket['key']

        # Get ticket details
        details = get_ticket_details(ticket_key)
        if not details:
            print(f"❌ {ticket_key}: Could not fetch details")
            error_count += 1
            continue

        description = details['description']

        # Check if PDF link exists
        if has_pdf_link(description):
            print(f"✓ {ticket_key}: Has PDF link")
            continue

        missing_count += 1
        print(f"\n⚠️  {ticket_key}: Missing PDF link")

        # Extract article URL
        article_url = extract_article_url(description)
        if article_url:
            print(f"   Article: {article_url[:60]}...")

        # Find PDF
        pdf_path = find_pdf_for_ticket(ticket_key, article_url)

        if not pdf_path:
            print(f"   ❌ No PDF found")
            error_count += 1
            continue

        print(f"   📄 Found PDF: {os.path.basename(pdf_path)}")

        if args.dry_run:
            print(f"   [DRY RUN] Would upload and update ticket")
            continue

        try:
            # Upload PDF
            pdf_link = upload_pdf_to_drive(drive_service, pdf_path, ticket_key)
            print(f"   ✓ Uploaded: {pdf_link}")

            # Update JIRA
            if update_jira_description(ticket_key, pdf_link, description):
                print(f"   ✓ Updated JIRA ticket")
                fixed_count += 1
            else:
                print(f"   ❌ Failed to update JIRA")
                error_count += 1

        except Exception as e:
            print(f"   ❌ Error: {e}")
            error_count += 1

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Total tickets checked: {len(tickets)}")
    print(f"Missing PDF links: {missing_count}")

    if args.dry_run:
        print(f"Dry run - no changes made")
    else:
        print(f"Fixed: {fixed_count}")
        print(f"Errors: {error_count}")

if __name__ == "__main__":
    main()
