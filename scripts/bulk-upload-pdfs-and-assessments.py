#!/usr/bin/env python3
"""
Bulk upload PDFs and assessment documents to Google Drive.
Uploads files to the correct date-specific folders and creates Google Docs for assessments.
"""

import os
import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

# Token file location
TOKEN_FILE = '/Users/bgerby/Documents/dev/ai/mcp-googledocs-server/token.json'

# Folder IDs
FOLDERS = {
    '22-pdfs': '1Sv94sPyBtgPAl3WhcsGHxtk0lhmMhtgX',
    '22-summaries': '1ARd0NSOwAWdvswRk8WV5TRVL3eZXl6L3',
    '23-pdfs': '12PnsXRMCEt2_RkKuNuwFZNHf4AQt6XwQ',
    '23-summaries': '1yXpJSoAlG-jniHo0ttGEfzNn8wXHN5Hu',
}

def get_drive_service():
    """Get authenticated Google Drive service."""
    creds = Credentials.from_authorized_user_file(TOKEN_FILE)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build('drive', 'v3', credentials=creds)

def upload_pdf(service, file_path, folder_id, new_name=None):
    """Upload a PDF file to Google Drive."""
    filename = new_name if new_name else os.path.basename(file_path)

    file_metadata = {
        'name': filename,
        'parents': [folder_id]
    }

    media = MediaFileUpload(file_path, mimetype='application/pdf', resumable=True)

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, name, webViewLink',
        supportsAllDrives=True
    ).execute()

    # Make publicly viewable
    service.permissions().create(
        fileId=file['id'],
        body={'type': 'anyone', 'role': 'reader'},
        supportsAllDrives=True
    ).execute()

    return file

def create_google_doc_from_markdown(service, md_path, folder_id, doc_title):
    """Create a Google Doc from markdown file."""
    with open(md_path, 'r') as f:
        content = f.read()

    # Create empty Google Doc
    file_metadata = {
        'name': doc_title,
        'mimeType': 'application/vnd.google-apps.document',
        'parents': [folder_id]
    }

    doc = service.files().create(
        body=file_metadata,
        fields='id, name, webViewLink',
        supportsAllDrives=True
    ).execute()

    # Build Docs service to add content
    docs_service = build('docs', 'v1', credentials=service._http.credentials)

    # Insert content
    requests = [{
        'insertText': {
            'location': {'index': 1},
            'text': content
        }
    }]

    docs_service.documents().batchUpdate(
        documentId=doc['id'],
        body={'requests': requests}
    ).execute()

    # Make publicly viewable
    service.permissions().create(
        fileId=doc['id'],
        body={'type': 'anyone', 'role': 'reader'},
        supportsAllDrives=True
    ).execute()

    return doc

def main():
    service = get_drive_service()

    print("=== Starting Bulk Upload ===\n")

    # Upload Oct 22 Medium PDFs
    print("📄 Uploading Oct 22 Medium PDFs...")
    oct22_pdf_dir = '/Users/bgerby/Documents/dev/ai/pdfs/medium-articles-2025-10-22'
    oct22_pdfs = sorted([f for f in os.listdir(oct22_pdf_dir) if f.endswith('.pdf')])

    for pdf in oct22_pdfs:
        pdf_path = os.path.join(oct22_pdf_dir, pdf)
        result = upload_pdf(service, pdf_path, FOLDERS['22-pdfs'])
        print(f"  ✓ {result['name']}")

    print(f"\nUploaded {len(oct22_pdfs)} Oct 22 PDFs\n")

    # Upload Oct 22 Medium Assessment
    print("📝 Uploading Oct 22 Medium Assessment...")
    oct22_assessment = '/Users/bgerby/Documents/dev/ai/assessments/medium-articles-relevance-assessment-2025-10-22.md'
    doc = create_google_doc_from_markdown(
        service,
        oct22_assessment,
        FOLDERS['22-summaries'],
        'Medium Articles Relevance Assessment - Oct 22, 2025'
    )
    print(f"  ✓ Created: {doc['name']}")
    print(f"  🔗 {doc['webViewLink']}\n")

    # Upload Oct 23 Optimizely PDFs
    print("📄 Uploading Oct 23 Optimizely PDFs...")
    oct23_pdf_dir = '/Users/bgerby/Documents/dev/ai/pdfs/optimizely-articles-2025-10-23'
    oct23_pdfs = sorted([f for f in os.listdir(oct23_pdf_dir) if f.endswith('.pdf')])

    for pdf in oct23_pdfs:
        pdf_path = os.path.join(oct23_pdf_dir, pdf)
        result = upload_pdf(service, pdf_path, FOLDERS['23-pdfs'])
        print(f"  ✓ {result['name']}")

    print(f"\nUploaded {len(oct23_pdfs)} Oct 23 PDFs\n")

    # Upload Oct 23 Optimizely Assessment
    print("📝 Uploading Oct 23 Optimizely Assessment...")
    oct23_assessment = '/Users/bgerby/Documents/dev/ai/assessments/optimizely-articles-relevance-assessment-2025-10-23.md'
    doc = create_google_doc_from_markdown(
        service,
        oct23_assessment,
        FOLDERS['23-summaries'],
        'Optimizely Articles Relevance Assessment - Oct 23, 2025'
    )
    print(f"  ✓ Created: {doc['name']}")
    print(f"  🔗 {doc['webViewLink']}\n")

    print("=== Upload Complete ===")
    print(f"Total: {len(oct22_pdfs)} Oct 22 PDFs + {len(oct23_pdfs)} Oct 23 PDFs + 2 assessments")

if __name__ == '__main__':
    main()
