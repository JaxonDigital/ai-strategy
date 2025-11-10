#!/usr/bin/env python3
"""
Move misplaced MP3s from October 21st folder to correct date-specific folders.

This fixes the issue where MP3s from Oct 24-31, 2025 were uploaded to the wrong folder
due to hardcoded folder ID bug (now fixed).

Usage:
    python3 fix-misplaced-mp3s.py --dry-run    # Preview what would be moved
    python3 fix-misplaced-mp3s.py              # Actually move files
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Configuration
TOKEN_PATH = '/Users/bgerby/Documents/dev/ai/mcp-googledocs-server/token.json'
SHARED_DRIVE_ROOT = '0ALLCxnOLmj3bUk9PVA'
WRONG_FOLDER_ID = '1NB1a1jGrqTmXvSw8CVQAsi_j05DCBg59'  # Oct 21 folder where they're currently misplaced

# Mapping of ticket ranges to review dates (based on when articles were processed)
# This is derived from the assessment filenames and JIRA ticket creation dates
TICKET_DATE_MAP = {
    # Oct 24, 2025 - First day of bug (tickets created this day)
    range(472, 481): '2025-10-24',  # GAT-472 to GAT-480

    # Oct 25, 2025
    range(481, 490): '2025-10-25',  # GAT-481 to GAT-489

    # Oct 26, 2025
    range(490, 498): '2025-10-26',  # GAT-490 to GAT-497

    # Oct 28, 2025 (no articles on Oct 27 based on file structure)
    range(498, 507): '2025-10-28',  # GAT-498 to GAT-506

    # Oct 29, 2025
    range(507, 514): '2025-10-29',  # GAT-507 to GAT-513

    # Oct 30, 2025
    range(514, 517): '2025-10-30',  # GAT-514 to GAT-516

    # Oct 31, 2025
    range(517, 527): '2025-10-31',  # GAT-517 to GAT-526
}

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

    # Refresh if needed
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        token_data['access_token'] = creds.token
        with open(TOKEN_PATH, 'w') as f:
            json.dump(token_data, f)

    return build('drive', 'v3', credentials=creds)

def get_or_create_mp3_folder(service, year: str, month: str, day: str) -> str:
    """Get or create Drive folder structure: 2025/10-October/DD/MP3s/"""
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
            print(f"  Created folder: {search_name}")

    return parent_id

def get_ticket_number_from_filename(filename: str) -> int:
    """Extract ticket number from filename like 'GAT-518.mp3'"""
    import re
    match = re.search(r'GAT-(\d+)', filename)
    if match:
        return int(match.group(1))
    return None

def get_review_date_for_ticket(ticket_num: int) -> str:
    """Get the review date for a ticket based on TICKET_DATE_MAP"""
    for ticket_range, date in TICKET_DATE_MAP.items():
        if ticket_num in ticket_range:
            return date
    return None

def list_files_in_folder(service, folder_id):
    """List all MP3 files in the specified folder."""
    query = f"'{folder_id}' in parents and mimeType='audio/mpeg' and trashed=false"

    results = service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name)',
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
        corpora='drive',
        driveId=SHARED_DRIVE_ROOT,
        pageSize=1000
    ).execute()

    return results.get('files', [])

def move_file(service, file_id, file_name, old_folder_id, new_folder_id, dry_run=False):
    """Move file from old folder to new folder."""
    if dry_run:
        print(f"  [DRY RUN] Would move: {file_name}")
        return True

    try:
        # Remove from old folder and add to new folder
        file = service.files().update(
            fileId=file_id,
            addParents=new_folder_id,
            removeParents=old_folder_id,
            fields='id, parents',
            supportsAllDrives=True
        ).execute()

        print(f"  ✓ Moved: {file_name}")
        return True
    except Exception as e:
        print(f"  ✗ Error moving {file_name}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Move misplaced MP3s to correct date folders')
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview what would be moved without actually moving files')
    args = parser.parse_args()

    print("Fix Misplaced MP3s - Oct 24-31, 2025")
    print("=" * 50)

    if args.dry_run:
        print("DRY RUN MODE - No files will be moved\n")
    else:
        print("LIVE MODE - Files will be moved\n")

    # Get Drive service
    service = get_drive_service()

    # List all MP3s in the wrong folder
    print(f"Scanning wrong folder (Oct 21): {WRONG_FOLDER_ID}")
    files = list_files_in_folder(service, WRONG_FOLDER_ID)
    print(f"Found {len(files)} MP3 files\n")

    if not files:
        print("No files to move!")
        return

    # Group files by date
    files_by_date = {}
    skipped_files = []

    for file in files:
        ticket_num = get_ticket_number_from_filename(file['name'])

        if ticket_num is None:
            skipped_files.append(file['name'])
            continue

        review_date = get_review_date_for_ticket(ticket_num)

        if review_date is None:
            # Not in our date range (probably legitimately from Oct 21-23)
            continue

        if review_date not in files_by_date:
            files_by_date[review_date] = []

        files_by_date[review_date].append(file)

    # Report what will be moved
    print("Files to move by date:")
    for date in sorted(files_by_date.keys()):
        print(f"  {date}: {len(files_by_date[date])} files")

    if skipped_files:
        print(f"\nSkipping {len(skipped_files)} files with no ticket number")

    total_to_move = sum(len(files) for files in files_by_date.values())
    print(f"\nTotal files to move: {total_to_move}\n")

    if total_to_move == 0:
        print("Nothing to move!")
        return

    # Process each date
    moved_count = 0
    failed_count = 0

    for date in sorted(files_by_date.keys()):
        files_for_date = files_by_date[date]

        # Parse date
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        year = date_obj.strftime('%Y')
        month = date_obj.strftime('%m')
        day = date_obj.strftime('%d')

        print(f"Processing {date} ({len(files_for_date)} files)...")

        # Get or create target folder
        target_folder_id = get_or_create_mp3_folder(service, year, month, day)

        # Move files
        for file in files_for_date:
            if move_file(service, file['id'], file['name'], WRONG_FOLDER_ID, target_folder_id, args.dry_run):
                moved_count += 1
            else:
                failed_count += 1

        print()

    # Summary
    print("=" * 50)
    if args.dry_run:
        print(f"DRY RUN COMPLETE")
        print(f"Would move: {moved_count} files")
    else:
        print(f"MOVE COMPLETE")
        print(f"Successfully moved: {moved_count} files")
        print(f"Failed: {failed_count} files")

if __name__ == '__main__':
    main()
