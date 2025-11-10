#!/usr/bin/env python3
"""
Upload audio files to Google Drive and update JIRA tickets.

⚠️ DEPRECATED: This script is no longer used in the main workflow.
Audio uploads are now handled automatically by generate-audio-from-assessment.py (since Oct 24, 2025).

This script remains for manual uploads only. It uses today's date for folder organization.

Usage:
    python3 upload-audio-to-drive.py
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

# Configuration
AUDIO_DIR = Path("/Users/bgerby/Documents/dev/ai/audio-reviews")
RESULTS_FILE = AUDIO_DIR / "audio-generation-results.json"
TOKEN_PATH = '/Users/bgerby/Documents/dev/ai/mcp-googledocs-server/token.json'
SHARED_DRIVE_ROOT = '0ALLCxnOLmj3bUk9PVA'

def get_drive_service():
    """Get Google Drive API service."""
    if not os.path.exists(TOKEN_PATH):
        raise Exception(f"Google Drive token not found at {TOKEN_PATH}")

    with open(TOKEN_PATH, 'r') as f:
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
        with open(TOKEN_PATH, 'w') as f:
            json.dump(token_data, f)

    return build('drive', 'v3', credentials=creds)

def get_or_create_mp3_folder(service, year: str, month: str, day: str) -> str:
    """Get or create Drive folder structure: 2025/10-October/29/MP3s/"""
    parent_id = SHARED_DRIVE_ROOT

    # Navigate folder structure
    month_name = datetime.strptime(month, '%m').strftime('%B')
    folder_path = [
        (year, year),
        (f'{month}-{month_name}', f'{month}-{month_name}'),
        (day, day),
        ('MP3s', 'MP3s')
    ]

    for folder_display, search_name in folder_path:
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

def upload_file_to_drive(service, file_path, parent_folder_id=None):
    """Upload file to Google Drive and return file ID.

    If parent_folder_id is None, uses today's date to create/find the MP3 folder.
    """
    # Get date-specific folder if not provided
    if parent_folder_id is None:
        now = datetime.now()
        year = now.strftime('%Y')
        month = now.strftime('%m')
        day = now.strftime('%d')
        parent_folder_id = get_or_create_mp3_folder(service, year, month, day)

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
    permission = {
        'type': 'anyone',
        'role': 'reader'
    }
    service.permissions().create(
        fileId=file_id,
        body=permission,
        supportsAllDrives=True
    ).execute()

    file = service.files().get(
        fileId=file_id,
        fields='webViewLink',
        supportsAllDrives=True
    ).execute()

    return file['webViewLink']

def update_jira_description(ticket_id, article_url, pdf_link, audio_link):
    """Update JIRA ticket description with PDF and audio links."""
    jira_token = os.popen('cat ~/.jira.d/.pass').read().strip()

    # Determine source (Medium or Optimizely)
    source = "Optimizely World Blog" if article_url and "world.optimizely.com" in article_url else "Medium"

    # Build description - include PDF only if available
    if pdf_link:
        new_description = f"""{source} Article Review

**Article URL:** {article_url}
**PDF:** {pdf_link}
**Audio:** {audio_link}

To be reviewed for relevance to Jaxon Digital's AI agent initiatives."""
    else:
        new_description = f"""{source} Article Review

**Article URL:** {article_url}
**Audio:** {audio_link}

To be reviewed for relevance to Jaxon Digital's AI agent initiatives."""

    cmd = [
        'jira', 'issue', 'edit',
        ticket_id,
        '-b', new_description,
        '--no-input'
    ]

    env = os.environ.copy()
    env['JIRA_API_TOKEN'] = jira_token

    result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=30)
    return result.returncode == 0

def get_article_info(ticket_id):
    """Get article URL and PDF link from JIRA ticket."""
    jira_token = os.popen('cat ~/.jira.d/.pass').read().strip()

    env = os.environ.copy()
    env['JIRA_API_TOKEN'] = jira_token

    result = subprocess.run(
        ['jira', 'issue', 'view', ticket_id],
        env=env,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return None, None

    # Parse output for URL and PDF link
    import re
    output = result.stdout

    url_match = re.search(r'\*\*Article URL:\*\*\s+(https://[^\s]+)', output)
    pdf_match = re.search(r'\*\*PDF:\*\*\s+(https://[^\s]+)', output)

    article_url = url_match.group(1) if url_match else None
    pdf_link = pdf_match.group(1) if pdf_match else None

    return article_url, pdf_link

def main():
    if not RESULTS_FILE.exists():
        print(f"Error: Results file not found: {RESULTS_FILE}")
        print("Run generate-audio-from-assessment.py first")
        sys.exit(1)

    print("Audio Upload to Google Drive")
    print("=" * 50)
    print(f"Audio Directory: {AUDIO_DIR}")
    now = datetime.now()
    print(f"Using date-specific folders (today: {now.strftime('%Y-%m-%d')})")
    print()

    # Load results
    with open(RESULTS_FILE, 'r') as f:
        results = json.load(f)

    print(f"Found {len(results)} audio files to upload\n")

    # Get Drive service
    drive_service = get_drive_service()

    updated_results = []

    for result in results:
        ticket_id = result['ticket_id']
        audio_path = Path(result['audio_path'])

        if not audio_path.exists():
            print(f"⚠ Audio file not found: {audio_path}")
            continue

        print(f"\nProcessing {ticket_id}...")

        # Upload to Drive
        try:
            print(f"  Uploading {audio_path.name}...")
            # Upload with auto-detection of today's folder (parent_folder_id=None uses today's date)
            file_id, web_link = upload_file_to_drive(drive_service, str(audio_path))
            audio_link = get_shareable_link(drive_service, file_id)
            print(f"  ✓ Uploaded: {audio_link}")

            # Get article info from JIRA
            print(f"  Fetching article info from JIRA...")
            article_url, pdf_link = get_article_info(ticket_id)

            if not article_url:
                print(f"  ⚠ Could not get article URL from JIRA (skipping)")
                updated_results.append({
                    **result,
                    'audio_link': audio_link,
                    'jira_updated': False
                })
                continue

            # PDF link is optional - proceed even if missing
            if not pdf_link:
                print(f"  ℹ No PDF link found (will add audio only)")

            # Update JIRA
            print(f"  Updating JIRA ticket...")
            if update_jira_description(ticket_id, article_url, pdf_link, audio_link):
                print(f"  ✓ Updated {ticket_id}")
                updated_results.append({
                    **result,
                    'audio_link': audio_link,
                    'jira_updated': True
                })
            else:
                print(f"  ✗ Failed to update {ticket_id}")
                updated_results.append({
                    **result,
                    'audio_link': audio_link,
                    'jira_updated': False
                })

        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback
            traceback.print_exc()
            updated_results.append({
                **result,
                'error': str(e)
            })

    # Save updated results
    with open(RESULTS_FILE, 'w') as f:
        json.dump(updated_results, f, indent=2)

    print(f"\n{'=' * 50}")
    print(f"Uploaded {len([r for r in updated_results if 'audio_link' in r])} audio files")
    print(f"Updated {len([r for r in updated_results if r.get('jira_updated')])} JIRA tickets")
    print(f"\nResults saved to: {RESULTS_FILE}")

if __name__ == '__main__':
    main()
