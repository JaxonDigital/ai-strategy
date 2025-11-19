#!/usr/bin/env python3.11
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

import fcntl
import re
import base64
import sys
import subprocess
import os
import json
import tempfile
from datetime import datetime
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

# Import shared patterns and constants
try:
    from shared_patterns import (
        MEDIUM_USER_ARTICLE_PATTERN,
        MEDIUM_PUB_ARTICLE_PATTERN,
        JIRA_PROJECT_GAT,
        JIRA_TICKET_PATTERN,
        ERROR_LOG_FILE
    )
except ImportError:
    # Fallback if shared_patterns not available
    MEDIUM_USER_ARTICLE_PATTERN = r'https://medium\.com/@[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+-[a-f0-9]{12}'
    MEDIUM_PUB_ARTICLE_PATTERN = r'https://medium\.com/(?!plans|jobs-at-medium|@)[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+-[a-f0-9]{12}'
    JIRA_PROJECT_GAT = 'GAT'
    JIRA_TICKET_PATTERN = r'GAT-\d+'
    ERROR_LOG_FILE = "/tmp/workflow-errors.log"

# Import shared configuration
try:
    from config import Config
    JIRA_TOKEN_FILE = str(Config.JIRA_TOKEN_FILE)
    GOOGLE_DRIVE_TOKEN = str(Config.GOOGLE_DRIVE_TOKEN_FILE)
except ImportError:
    # Fallback if config not available
    JIRA_TOKEN_FILE = os.path.expanduser('~/.jira.d/.pass')
    GOOGLE_DRIVE_TOKEN = '/Users/bgerby/Documents/dev/ai/mcp-googledocs-server/token.json'

def log_subprocess_error(command_name, stderr_output, log_file=ERROR_LOG_FILE):
    """Log subprocess stderr to file for debugging."""
    if not stderr_output or not stderr_output.strip():
        return

    try:
        with open(log_file, 'a') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"{datetime.now().isoformat()} - {command_name}\n")
            f.write(f"{'='*60}\n")
            f.write(stderr_output)
            f.write(f"\n")
    except Exception as e:
        print(f"  ⚠️  Warning: Could not write to error log: {e}")

def extract_articles(email_path):
    """Extract all Medium article URLs from email file with validation."""
    with open(email_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        lines = content.split('\n')

    # Validation: Check if email contains Medium content at all
    has_medium_content = 'medium.com' in content.lower() or 'medium daily digest' in content.lower()

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

                        # Pattern 1: @username articles
                        user_urls = re.findall(MEDIUM_USER_ARTICLE_PATTERN, decoded)
                        for url in user_urls:
                            if url not in seen:
                                seen.add(url)
                                articles.append(url)

                        # Pattern 2: Publication articles
                        pub_urls = re.findall(MEDIUM_PUB_ARTICLE_PATTERN, decoded)
                        for url in pub_urls:
                            if url not in seen:
                                seen.add(url)
                                articles.append(url)
                    except Exception as e:
                        # Ignore malformed base64 or decode errors
                        pass
                    base64_content = []
                in_base64 = False
            else:
                base64_content.append(line.strip())

    # Validation: Warn if no articles found but email contains Medium content
    if len(articles) == 0 and has_medium_content:
        print("⚠️  WARNING: Email contains 'medium.com' but no article URLs extracted!")
        print("    This may indicate Medium changed their email format.")
        print("    Please verify email content and update regex patterns if needed.\n")
    elif len(articles) < 3 and has_medium_content:
        print(f"⚠️  WARNING: Only {len(articles)} articles found (usually 10-20 expected)")
        print("    This may indicate incomplete parsing. Please verify.\n")

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

def get_drive_service(force_refresh=False):
    """Get Google Drive API service using token from MCP server.

    Args:
        force_refresh: If True, force token refresh even if not expired
    """
    # Use the token from the MCP server
    token_path = GOOGLE_DRIVE_TOKEN

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

    # Refresh if needed or forced
    if force_refresh or (creds.expired and creds.refresh_token):
        creds.refresh(Request())
        # Update token file atomically
        import tempfile
        temp_fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(token_path))
        try:
            with os.fdopen(temp_fd, 'w') as f:
                token_data['access_token'] = creds.token
                json.dump(token_data, f)
            os.replace(temp_path, token_path)
        except Exception as e:
            try:
                os.unlink(temp_path)
            except OSError:
                # Temp file already cleaned up or doesn't exist
                pass
            raise

    return build('drive', 'v3', credentials=creds)


def drive_api_call_with_retry(api_call_func, max_retries=3):
    """Wrapper to handle token expiration, rate limits, and transient errors for Google Drive API calls.

    Args:
        api_call_func: Function that makes API call
        max_retries: Maximum number of retry attempts (default: 3)

    Returns:
        Result of api_call_func
    """
    from googleapiclient.errors import HttpError
    import time
    import random

    for attempt in range(max_retries):
        try:
            return api_call_func()
        except HttpError as e:
            status = e.resp.status

            # Handle 401 Unauthorized or 403 Forbidden (expired token)
            if status in [401, 403]:
                print(f"  → Token expired, refreshing and retrying...")
                # Force token refresh and retry once
                try:
                    return api_call_func()
                except Exception as retry_error:
                    print(f"  ✗ Retry failed: {retry_error}")
                    raise

            # Handle rate limiting (429) and transient errors (500, 503)
            elif status in [429, 500, 503]:
                if attempt < max_retries - 1:
                    # Exponential backoff with jitter
                    delay = (2 ** attempt) + random.uniform(0, 1)
                    print(f"  → Drive API error {status}, retrying in {delay:.1f}s (attempt {attempt + 1}/{max_retries})")
                    time.sleep(delay)
                else:
                    # Last attempt failed
                    print(f"  ✗ Drive API error {status} after {max_retries} attempts")
                    raise

            # Other HTTP errors, re-raise immediately
            else:
                raise

        except Exception as e:
            # Non-HTTP errors, don't retry
            raise

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
    # Read JIRA token securely from file (not via shell)
    with open(JIRA_TOKEN_FILE, 'r') as f:
        jira_token = f.read().strip()

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

    try:
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=15)

        # Log any errors from JIRA CLI
        if result.returncode != 0 and result.stderr:
            log_subprocess_error(f"JIRA edit {ticket_id}", result.stderr)
            print(f"    ✗ JIRA CLI error: {result.stderr.strip()[:100]}")

        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"    ✗ JIRA CLI timeout (15s) - ticket {ticket_id} may not be updated")
        return False

def check_existing_ticket_by_url(article_url):
    """
    Check if a ticket already exists for this article URL.

    Searches JIRA for tickets containing this URL in the description.
    This prevents duplicate tickets for the same article.

    Returns: (ticket_id, exists) tuple
    """
    try:
        env = os.environ.copy()
        if not os.path.exists(JIRA_TOKEN_FILE):
            return (None, False)

        with open(JIRA_TOKEN_FILE, 'r') as f:
            env['JIRA_API_TOKEN'] = f.read().strip()

        # Search using jira list - look for recent tickets with Medium label
        result = subprocess.run(
            ['jira', 'issue', 'list', '-p', JIRA_PROJECT_GAT, '-l', 'Medium', '--plain', '--created', 'month'],
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
        else:
            print(f"⚠️  WARNING: JIRA search command failed (exit code {result.returncode})")
            print(f"    stdout: {result.stdout[:200]}")
            print(f"    stderr: {result.stderr[:200]}")

    except Exception as e:
        # Log the error but don't silently create duplicates
        print(f"⚠️  WARNING: Duplicate check failed for {article_url}")
        print(f"    Error: {e}")
        print(f"    To avoid duplicates, manually check JIRA before proceeding.")
        print(f"    Returning 'not found' - ticket will be created.")

    return (None, False)


def create_jira_ticket(url, title, pdf_link=None):
    """Create a Jira ticket for the article with PDF link.

    Checks for existing tickets first to prevent duplicates.
    Returns existing ticket ID if found, or creates new ticket.
    """
    # Check for existing ticket first
    existing_ticket, exists = check_existing_ticket_by_url(url)
    if exists:
        print(f"    → Ticket already exists: {existing_ticket}")
        return existing_ticket

    # Read JIRA token securely from file (not via shell)
    with open(JIRA_TOKEN_FILE, 'r') as f:
        jira_token = f.read().strip()

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

    try:
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=15)

        if result.returncode == 0:
            # Extract ticket number from output
            match = re.search(r'GAT-\d+', result.stdout)
            if match:
                return match.group(0)
        else:
            # Log any errors from JIRA CLI
            if result.stderr:
                log_subprocess_error("JIRA create ticket", result.stderr)
                print(f"    ✗ JIRA CLI error: {result.stderr.strip()[:100]}")

        return None
    except subprocess.TimeoutExpired:
        print(f"    ✗ JIRA CLI timeout (15s) - ticket creation failed")
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

    # Prevent concurrent execution with lockfile
    lock_file_path = '/tmp/extract-medium-articles.lock'
    lock_file = open(lock_file_path, 'w')

    try:
        # Try to acquire exclusive lock (non-blocking)
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print("❌ Error: Another instance of this script is already running")
        print(f"   Lock file: {lock_file_path}")
        print("   If no other instance is running, remove the lock file manually")
        sys.exit(1)

    # Lock will be automatically released when script exits (or file closes)

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
            # Find PDF by article number prefix (robust to filename variations)
            pdf_prefix = f"{i:02d}-"
            pdf_files = [f for f in os.listdir(upload_to_drive) if f.startswith(pdf_prefix) and f.endswith('.pdf')]

            if pdf_files:
                # Use the first matching file (should only be one)
                pdf_filename = pdf_files[0]
                pdf_path = os.path.join(upload_to_drive, pdf_filename)

                # Validate PDF size (detect paywall failures)
                pdf_size_kb = os.path.getsize(pdf_path) / 1024
                if pdf_size_kb < 200:
                    print(f"    ⚠ Warning: PDF is very small ({pdf_size_kb:.1f} KB) - may be paywall failure")
                    print(f"    Expected: 400+ KB for full article, ~115 KB indicates paywall")

                try:
                    file_id, web_link = upload_file_to_drive(drive_service, pdf_path, pdfs_folder)
                    drive_link = get_shareable_link(drive_service, file_id)
                    print(f"    ✓ Uploaded to Drive: {drive_link}")
                except Exception as e:
                    print(f"    ✗ Upload failed: {e}")
            else:
                print(f"    ⚠ PDF not found with prefix: {pdf_prefix}")

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

    # Write JSON output if requested (atomic write to prevent corruption)
    if output_json:
        output_path = Path(output_json)
        temp_fd, temp_path = tempfile.mkstemp(
            dir=output_path.parent,
            prefix='.medium-articles-',
            suffix='.tmp'
        )

        try:
            with os.fdopen(temp_fd, 'w') as f:
                json.dump({
                    'date': current_date,
                    'email_path': email_path,
                    'articles': article_data
                }, f, indent=2)

            # Atomic rename (POSIX guarantees atomicity)
            os.replace(temp_path, output_json)
            print(f"\n✓ Wrote article metadata to {output_json}")
        except Exception as e:
            # Clean up temp file on error
            try:
                os.unlink(temp_path)
            except OSError:
                # Temp file already cleaned up or doesn't exist
                pass
            raise Exception(f"Failed to write article metadata: {e}")

if __name__ == '__main__':
    main()
