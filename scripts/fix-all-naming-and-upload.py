#!/usr/bin/env python3
"""
Fix all file naming conventions and re-upload missing Oct 21 PDFs.
Renames files in Google Drive to follow {seq}-{ticket}-{title} convention.
"""

import os
import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

TOKEN_FILE = '/Users/bgerby/Documents/dev/ai/mcp-googledocs-server/token.json'

# Folder IDs
FOLDERS = {
    '21-pdfs': '14MfsiDvH_5NaxQDvKuqslWNf3gduQZmA',
    '21-mp3s': '1NB1a1jGrqTmXvSw8CVQAsi_j05DCBg59',
    '22-pdfs': '1Sv94sPyBtgPAl3WhcsGHxtk0lhmMhtgX',
    '22-mp3s': '1jZQcGQDMk6h69bhPvFZ_D0hSeEBap4ws',
    '23-pdfs': '12PnsXRMCEt2_RkKuNuwFZNHf4AQt6XwQ',
    '23-mp3s': '1eaaR8ScCGFyti1Y7Alr8zyVsUQevQWl5',
}

# Oct 21 MP3 renaming map (GAT-XXX -> seq-ticket-title)
OCT21_MP3_RENAMES = {
    'GAT-233-ai-logging-agent-devops.mp3': '01-233-ai-logging-agent-devops.mp3',
    'GAT-234-qa-agent-without-rag.mp3': '02-234-qa-agent-without-rag.mp3',
    'GAT-321.mp3': '03-321-how-i-use-codemcp-for-development.mp3',
    'GAT-324.mp3': '04-324-why-agent-skills-will-transform-ai.mp3',
    'GAT-327.mp3': '05-327-stop-letting-ai-waste-your-time-7-mcp-servers.mp3',
    'GAT-333.mp3': '06-333-optimizely-mcp-learns-cms.mp3',
    'GAT-334.mp3': '07-334-tool-calling-vs-mcp.mp3',
}

def get_drive_service():
    """Get authenticated Google Drive service."""
    creds = Credentials.from_authorized_user_file(TOKEN_FILE)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build('drive', 'v3', credentials=creds)

def upload_pdf(service, file_path, folder_id):
    """Upload a PDF file to Google Drive."""
    filename = os.path.basename(file_path)

    file_metadata = {
        'name': filename,
        'parents': [folder_id]
    }

    media = MediaFileUpload(file_path, mimetype='application/pdf', resumable=True)

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, name',
        supportsAllDrives=True
    ).execute()

    # Make publicly viewable
    service.permissions().create(
        fileId=file['id'],
        body={'type': 'anyone', 'role': 'reader'},
        supportsAllDrives=True
    ).execute()

    return file

def rename_file(service, file_id, new_name):
    """Rename a file in Google Drive."""
    file_metadata = {'name': new_name}
    service.files().update(
        fileId=file_id,
        body=file_metadata,
        supportsAllDrives=True
    ).execute()

def list_files(service, folder_id):
    """List all files in a folder."""
    results = service.files().list(
        q=f"'{folder_id}' in parents",
        fields='files(id, name)',
        supportsAllDrives=True,
        includeItemsFromAllDrives=True
    ).execute()
    return results.get('files', [])

def main():
    service = get_drive_service()

    print("=== FIXING FILE ORGANIZATION ===\n")

    # Step 1: Re-upload Oct 21 PDFs
    print("📄 Re-uploading Oct 21 PDFs...")
    oct21_pdf_dir = '/Users/bgerby/Documents/dev/ai/pdfs/medium-articles-2025-10-21'
    oct21_pdfs = sorted([f for f in os.listdir(oct21_pdf_dir) if f.endswith('.pdf')])

    for pdf in oct21_pdfs:
        pdf_path = os.path.join(oct21_pdf_dir, pdf)
        result = upload_pdf(service, pdf_path, FOLDERS['21-pdfs'])
        print(f"  ✓ {result['name']}")

    print(f"\nRe-uploaded {len(oct21_pdfs)} Oct 21 PDFs\n")

    # Step 2: Rename Oct 21 MP3s
    print("🎵 Renaming Oct 21 MP3s to proper convention...")
    oct21_mp3s = list_files(service, FOLDERS['21-mp3s'])

    for mp3 in oct21_mp3s:
        old_name = mp3['name']
        if old_name in OCT21_MP3_RENAMES:
            new_name = OCT21_MP3_RENAMES[old_name]
            rename_file(service, mp3['id'], new_name)
            print(f"  ✓ {old_name} → {new_name}")

    print(f"\nRenamed {len(oct21_mp3s)} Oct 21 MP3s\n")

    # Step 3: Rename Oct 22 PDFs
    print("📄 Renaming Oct 22 PDFs to add ticket numbers...")
    oct22_pdfs = list_files(service, FOLDERS['22-pdfs'])

    # Map: current name -> new name with ticket
    oct22_pdf_map = {
        '01-basics-of-mcps-why-and-what.pdf': '01-335-basics-of-mcps-why-and-what.pdf',
        '02-i-spent-200-on-claude.pdf': '02-336-i-spent-200-on-claude.pdf',
        '03-ai-coding-assistant-wasting-tokens.pdf': '03-337-ai-coding-assistant-wasting-tokens.pdf',
        '04-mcp-10-sampling-and-prompts.pdf': '04-338-mcp-10-sampling-and-prompts.pdf',
        '05-mcp-9-tools-in-mcp.pdf': '05-339-mcp-9-tools-in-mcp.pdf',
        '06-vespa-open-source-engine.pdf': '06-340-vespa-open-source-engine.pdf',
        '07-chatgpt-atlas-ai-browser.pdf': '07-341-chatgpt-atlas-ai-browser.pdf',
        '08-datadog-replace-pagerduty.pdf': '08-342-datadog-replace-pagerduty.pdf',
        '09-beyond-doomsday-narrative.pdf': '09-343-beyond-doomsday-narrative.pdf',
        '10-aws-fired-devops-team.pdf': '10-344-aws-fired-devops-team.pdf',
        '11-claude-model-unbelievably-fast.pdf': '11-345-claude-model-unbelievably-fast.pdf',
        '12-openai-ide-extension.pdf': '12-346-openai-ide-extension.pdf',
        '13-future-is-broken.pdf': '13-347-future-is-broken.pdf',
        '14-build-ai-agents-with-n8n.pdf': '14-348-build-ai-agents-with-n8n.pdf',
        '15-mcp-three-core-capabilities.pdf': '15-349-mcp-three-core-capabilities.pdf',
    }

    for pdf in oct22_pdfs:
        old_name = pdf['name']
        if old_name in oct22_pdf_map:
            new_name = oct22_pdf_map[old_name]
            rename_file(service, pdf['id'], new_name)
            print(f"  ✓ {old_name} → {new_name}")

    print(f"\nRenamed {len([p for p in oct22_pdfs if p['name'] in oct22_pdf_map])} Oct 22 PDFs\n")

    # Step 4: Rename Oct 23 PDFs
    print("📄 Renaming Oct 23 PDFs to add ticket numbers...")
    oct23_pdfs = list_files(service, FOLDERS['23-pdfs'])

    # Optimizely articles (GAT-350 to GAT-369)
    oct23_opti_map = {
        '01-automated-page-audit.pdf': '01-350-automated-page-audit.pdf',
        '02-image-generation-gemini.pdf': '02-351-image-generation-gemini.pdf',
        '03-sql-index-maintenance.pdf': '03-352-sql-index-maintenance.pdf',
        '04-jhoose-security.pdf': '04-353-jhoose-security.pdf',
        '05-hiding-showing-properties.pdf': '05-354-hiding-showing-properties.pdf',
        '06-contentareas-limit.pdf': '06-355-contentareas-limit.pdf',
        '07-mcp-discovery-first-part1.pdf': '07-356-mcp-discovery-first-part1.pdf',
        '08-optimizely-forms.pdf': '08-357-optimizely-forms.pdf',
        '09-exception-enrichment.pdf': '09-358-exception-enrichment.pdf',
        '10-ai-mcp-function-calling.pdf': '10-359-ai-mcp-function-calling.pdf',
        '11-omvp-blazor-addon.pdf': '11-360-omvp-blazor-addon.pdf',
        '12-cms-learning-ep05.pdf': '12-361-cms-learning-ep05.pdf',
        '13-commerce-price-processor.pdf': '13-362-commerce-price-processor.pdf',
        '14-going-headless.pdf': '14-363-going-headless.pdf',
        '15-custom-payment.pdf': '15-364-custom-payment.pdf',
        '16-mcp-learns-cms-part2.pdf': '16-365-mcp-learns-cms-part2.pdf',
        '17-fake-openid-auth.pdf': '17-366-fake-openid-auth.pdf',
        '18-mimekit-vulnerability.pdf': '18-367-mimekit-vulnerability.pdf',
        '19-notebooklm-implementation.pdf': '19-368-notebooklm-implementation.pdf',
        '20-multiple-auth-providers.pdf': '20-369-multiple-auth-providers.pdf',
    }

    # Medium articles (need ticket assignment first - skip for now)
    medium_pdfs_skipped = []

    for pdf in oct23_pdfs:
        old_name = pdf['name']
        if old_name in oct23_opti_map:
            new_name = oct23_opti_map[old_name]
            rename_file(service, pdf['id'], new_name)
            print(f"  ✓ {old_name} → {new_name}")
        elif old_name.startswith('0') and 'promptify' in old_name.lower() or 'claude-code' in old_name.lower():
            medium_pdfs_skipped.append(old_name)

    print(f"\nRenamed {len(oct23_opti_map)} Oct 23 Optimizely PDFs")
    if medium_pdfs_skipped:
        print(f"⚠️  Skipped {len(medium_pdfs_skipped)} Medium PDFs (need ticket assignment)")

    print("\n=== FIX COMPLETE ===")

if __name__ == '__main__':
    main()
