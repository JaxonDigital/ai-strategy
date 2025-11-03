#!/usr/bin/env python3
"""
Helper script to upload PDFs to Google Drive and update JIRA tickets.
Handles uploading when tickets already exist.
"""

import sys
import os
import json
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
import subprocess

# Copy functions from extract-medium-articles.py
def get_drive_service():
    """Get Google Drive API service using token from MCP server."""
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

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        token_data['access_token'] = creds.token
        with open(token_path, 'w') as f:
            json.dump(token_data, f)

    return build('drive', 'v3', credentials=creds)

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

def update_jira_description(ticket_id, url, drive_link):
    """Update JIRA ticket description with Drive link."""
    jira_token = os.popen('cat ~/.jira.d/.pass').read().strip()

    new_description = f"""Medium Article Review

**Article URL:** {url}
**PDF:** {drive_link}

To be reviewed for relevance to Jaxon Digital's AI agent initiatives."""

    cmd = [
        'jira', 'issue', 'edit',
        ticket_id,
        '-b', new_description
    ]

    env = os.environ.copy()
    env['JIRA_API_TOKEN'] = jira_token

    result = subprocess.run(cmd, env=env, capture_output=True, text=True)
    return result.returncode == 0

def upload_existing_pdfs(pdf_dir, pdfs_folder_id, articles_data):
    """Upload PDFs for articles that already have JIRA tickets."""
    drive_service = get_drive_service()

    for article in articles_data:
        ticket_id = article['ticket_id']
        url = article['url']
        pdf_num = article['number']
        title = article['title']

        # Construct PDF filename
        pdf_filename = f"{pdf_num:02d}-{title.lower().replace(' ', '-')}.pdf"
        pdf_path = os.path.join(pdf_dir, pdf_filename)

        if not os.path.exists(pdf_path):
            print(f"⚠ PDF not found: {pdf_filename}")
            continue

        print(f"\n{pdf_num}. {title}")
        print(f"   Ticket: {ticket_id}")

        try:
            # Upload to Drive
            file_id, web_link = upload_file_to_drive(drive_service, pdf_path, pdfs_folder_id)
            shareable_link = get_shareable_link(drive_service, file_id)
            print(f"   ✓ Uploaded: {shareable_link}")

            # Update JIRA
            if update_jira_description(ticket_id, url, shareable_link):
                print(f"   ✓ Updated {ticket_id}")
            else:
                print(f"   ✗ Failed to update {ticket_id}")
        except Exception as e:
            print(f"   ✗ Error: {e}")

if __name__ == '__main__':
    # Article data from 10-21.eml
    articles = [
        {'number': 1, 'title': 'How I Use Codemcp For Development And Keep My Other Coding Assistants On Budget', 'url': 'https://medium.com/@PowerUpSkills/how-i-use-codemcp-for-development-and-keep-my-other-coding-assistants-on-budget-64320860db50', 'ticket_id': 'GAT-321'},
        {'number': 2, 'title': 'I Interviewed 100 Ai Product Managers Heres What They Actually Do', 'url': 'https://medium.com/@aakashgupta/i-interviewed-100-ai-product-managers-heres-what-they-actually-do-9e55d393a287', 'ticket_id': 'GAT-322'},
        {'number': 3, 'title': 'Youre Using Chatgpt Wrong Here Are The 9 Ai Tools Pms Actually Need', 'url': 'https://medium.com/@aakashgupta/youre-using-chatgpt-wrong-here-are-the-9-ai-tools-pms-actually-need-198a17f496a9', 'ticket_id': 'GAT-323'},
        {'number': 4, 'title': 'Why Agent Skills Will Transform How We Build Ai', 'url': 'https://medium.com/@alirezarezvani/why-agent-skills-will-transform-how-we-build-ai-32daee24fc8a', 'ticket_id': 'GAT-324'},
        {'number': 5, 'title': 'The Self Hosted Alternative To Google Notebook Lm Is Here', 'url': 'https://medium.com/@bytefer/the-self-hosted-alternative-to-google-notebook-lm-is-here-295352aa7437', 'ticket_id': 'GAT-325'},
        {'number': 6, 'title': 'How Perplexity Beat Google On Ai Search', 'url': 'https://medium.com/@civillearning/how-perplexity-beat-google-on-ai-search-6160bdadad4d', 'ticket_id': 'GAT-326'},
        {'number': 7, 'title': 'Stop Letting Ai Waste Your Time 7 Mcp Servers Every Developer Needs', 'url': 'https://medium.com/@deepakmardi/stop-letting-ai-waste-your-time-7-mcp-servers-every-developer-needs-82912216a9f5', 'ticket_id': 'GAT-327'},
        {'number': 8, 'title': 'My Ai Agents Have Their Own Inbox And Know How To Use It A Claude Code Skill Story', 'url': 'https://medium.com/@juan-pelaez/my-ai-agents-have-their-own-inbox-and-know-how-to-use-it-a-claude-code-skill-story-88ddc60d7062', 'ticket_id': 'GAT-328'},
        {'number': 9, 'title': 'How To Use Mcp Inspector', 'url': 'https://medium.com/@laurentkubaski/how-to-use-mcp-inspector-2748cd33faeb', 'ticket_id': 'GAT-329'},
        {'number': 10, 'title': 'My New Ai Driver Cc Gitea Gitea Mcp', 'url': 'https://medium.com/@steviee/my-new-ai-driver-cc-gitea-gitea-mcp-f98960bff054', 'ticket_id': 'GAT-330'},
        {'number': 11, 'title': 'The New Features Of Claude Code 2 0 A Comprehensive Guide', 'url': 'https://medium.com/@vedaterenoglu/the-new-features-of-claude-code-2-0-a-comprehensive-guide-3ed203d918b0', 'ticket_id': 'GAT-331'},
        {'number': 12, 'title': 'Building Claude Code From Scratch A Simple Journey Into Ai Agents', 'url': 'https://medium.com/@yashv6655/building-claude-code-from-scratch-a-simple-journey-into-ai-agents-2ca43eccad6e', 'ticket_id': 'GAT-332'},
    ]

    # Example usage - update these paths for your batch
    PDF_DIR = '/Users/bgerby/Documents/dev/ai/pdfs/medium-articles-YYYY-MM-DD'
    PDFS_FOLDER_ID = 'YOUR_DRIVE_FOLDER_ID'  # Get from Google Drive

    print("Uploading PDFs to Google Drive...")
    upload_existing_pdfs(PDF_DIR, PDFS_FOLDER_ID, articles)
    print("\n✓ Upload complete!")
