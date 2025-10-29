#!/usr/bin/env python3
"""
Generate audio files for high-priority Medium articles.
Works with assessment markdown and numbered PDFs (01-article.pdf format).

Usage:
    python3 generate-audio-from-assessment.py \\
        /Users/bgerby/Desktop/medium-articles-2025-10-21 \\
        /Users/bgerby/Desktop/medium-articles-relevance-assessment-2025-10-21.md \\
        /Users/bgerby/Desktop/upload-to-drive-helper.py
"""

import os
import sys
import re
import subprocess
import json
from pathlib import Path

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using pdftotext."""
    try:
        result = subprocess.run(
            ['pdftotext', str(pdf_path), '-'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return None

def clean_text_for_speech(text):
    """Clean text to make it better for text-to-speech."""
    # Remove login/account UI elements
    text = re.sub(r'Welcome back\. You are signed into your member account.*?Not you\?', '', text, flags=re.DOTALL)
    text = re.sub(r'bg••••@jaxondigital\.com', '', text)

    # Remove URLs
    text = re.sub(r'https?://\S+', '', text)

    # Remove common Medium UI elements
    text = re.sub(r'(Sidebar menu|Medium Logo|Write|Search|Notifications|Follow publication|Member-only story)', '', text)
    text = re.sub(r'\b(Follow|Listen|Share|More)\b\s*\n', '', text)
    text = re.sub(r'\d+ min read\s*·\s*[A-Z][a-z]+\s+\d+,\s+\d+', '', text)
    text = re.sub(r'\d+ min read', '', text)

    # IMPROVED: Crop at footer sections (Topics, Author bio, Recommendations)
    # Find earliest occurrence of footer patterns and truncate there
    footer_patterns = [
        r'\n\s*Topics\s*\n',                    # "Topics" section header
        r'\n\s*Topics\s*$',                     # "Topics" at end of line
        r'\n\s*See all from\s+\w+',            # "See all from [Author]"
        r'\n\s*Recommended from Medium',        # Medium recommendations section
        r'\n\s*More from\s+\w+',               # "More from [Publication]"
        r'\n\s*\d+\s+responses?\s*\n',         # Response count (e.g., "12 responses")
        r'\n\s*Written by\s*\n',               # Author byline section
        r'\n\s*--\s*\n',                       # Horizontal rule often precedes footer
    ]

    earliest_footer_pos = len(text)
    matched_pattern = None

    for pattern in footer_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match and match.start() < earliest_footer_pos:
            earliest_footer_pos = match.start()
            matched_pattern = pattern

    # Crop at footer if found
    if earliest_footer_pos < len(text):
        text = text[:earliest_footer_pos]
        # Note: Could add logging here for debugging
        # print(f"  → Cropped {len(text[earliest_footer_pos:])} chars at pattern: {matched_pattern}")

    # Remove code blocks
    lines = text.split('\n')
    cleaned_lines = []
    in_code_block = False

    for line in lines:
        special_char_count = sum(1 for c in line if c in '{}[]();,=<>|&')
        total_chars = len(line.strip())

        if total_chars > 10 and special_char_count / total_chars > 0.3:
            in_code_block = True
            continue
        elif in_code_block and total_chars < 20:
            continue
        else:
            in_code_block = False
            cleaned_lines.append(line)

    text = '\n'.join(cleaned_lines)
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    text = text.strip()

    return text

def parse_assessment(assessment_path, metadata_path=None):
    """Parse assessment markdown to extract article metadata and ratings."""
    with open(assessment_path, 'r') as f:
        content = f.read()

    # Load metadata to get article number to ticket ID mapping
    article_to_ticket = {}
    if metadata_path and os.path.exists(metadata_path):
        try:
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
                article_to_ticket = {a['number']: a['ticket_id'] for a in metadata['articles']}
        except Exception as e:
            print(f"Warning: Could not load metadata from {metadata_path}: {e}")
            print("Will use fallback ticket ID format (GAT-{article_num})")

    articles = {}

    # Match article sections - supports new format from generate-article-assessment.py
    # Format: ### ARTICLE-NN - Title
    #         **Priority:** HIGH ⭐⭐⭐⭐⭐
    pattern = r'###\s+ARTICLE-(\d+)\s+-\s+(.+?)$'

    for match in re.finditer(pattern, content, re.MULTILINE):
        article_num = int(match.group(1))
        title = match.group(2).strip()

        # Extract the article section content
        start_pos = match.end()
        # Find next article or section break
        next_match = re.search(r'###\s+ARTICLE-\d+', content[start_pos:])
        if next_match:
            end_pos = start_pos + next_match.start()
        else:
            # Look for section breaks
            section_match = re.search(r'\n##\s+', content[start_pos:])
            if section_match:
                end_pos = start_pos + section_match.start()
            else:
                end_pos = len(content)

        section_content = content[start_pos:end_pos]

        # Extract priority
        priority_match = re.search(r'\*\*Priority:\*\*\s+(HIGH|MEDIUM|LOW)', section_content)
        priority = priority_match.group(1) if priority_match else "UNKNOWN"

        # Only include HIGH and MEDIUM priority articles
        if priority not in ['HIGH', 'MEDIUM']:
            continue

        # Extract relevance summary and strategic implications for executive summary
        relevance_match = re.search(r'\*\*Relevance Summary:\*\*\s*(.+?)(?=\n\*\*|$)', section_content, re.DOTALL)
        relevance = relevance_match.group(1).strip() if relevance_match else ""

        # Extract action items
        action_items_match = re.search(r'\*\*Action Items:\*\*\s*(.+?)(?=\n\*\*|###|$)', section_content, re.DOTALL)
        action_items = action_items_match.group(1).strip() if action_items_match else ""

        # Build executive summary from relevance and action items
        executive_summary = (
            f"{title}. "
            f"Rated as HIGH priority. {relevance} "
            f"{action_items}"
            "\n\nNow, here's the full article.\n\n"
        )

        # Get actual ticket ID from metadata, fallback to GAT-{article_num} if not found
        ticket_id = article_to_ticket.get(article_num, f'GAT-{article_num}')

        articles[article_num] = {
            'number': article_num,
            'title': title,
            'ticket_id': ticket_id,
            'executive_summary': executive_summary,
            'priority': priority
        }

    return articles

def generate_audio_openai(text, output_path):
    """Generate audio using OpenAI TTS API."""
    import tempfile

    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY not set in environment")
        return False

    try:
        max_chunk_size = 4000

        if len(text) <= max_chunk_size:
            chunks = [text]
        else:
            paragraphs = text.split('\n\n')
            chunks = []
            current_chunk = ""

            for para in paragraphs:
                if len(current_chunk) + len(para) + 2 <= max_chunk_size:
                    current_chunk += para + "\n\n"
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = para + "\n\n"

            if current_chunk:
                chunks.append(current_chunk.strip())

        chunk_files = []
        for i, chunk in enumerate(chunks):
            chunk_file = output_path.parent / f"{output_path.stem}.chunk{i}.mp3"

            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump({
                    "model": "tts-1",
                    "input": chunk,
                    "voice": "onyx",
                    "speed": 1.0
                }, f)
                json_file = f.name

            subprocess.run([
                'curl', '-s',
                'https://api.openai.com/v1/audio/speech',
                '-H', f'Authorization: Bearer {api_key}',
                '-H', 'Content-Type: application/json',
                '-d', f'@{json_file}',
                '--output', str(chunk_file)
            ], check=True, capture_output=True)

            os.unlink(json_file)

            if not chunk_file.exists() or chunk_file.stat().st_size < 1000:
                print(f"Error: Chunk {i} not created or too small")
                for cf in chunk_files:
                    cf.unlink()
                return False

            chunk_files.append(chunk_file)

        if len(chunk_files) == 1:
            chunk_files[0].rename(output_path)
        else:
            concat_file = output_path.parent / f"{output_path.stem}.concat.txt"
            with open(concat_file, 'w') as f:
                for chunk_file in chunk_files:
                    f.write(f"file '{chunk_file.name}'\n")

            subprocess.run([
                'ffmpeg', '-f', 'concat', '-safe', '0',
                '-i', str(concat_file),
                '-acodec', 'copy',
                '-y', str(output_path)
            ], check=True, capture_output=True)

            concat_file.unlink()
            for chunk_file in chunk_files:
                chunk_file.unlink()

        if output_path.exists() and output_path.stat().st_size > 1000:
            return True
        else:
            print(f"Error: Final audio file not created or too small")
            return False

    except Exception as e:
        print(f"Error generating audio: {e}")
        import traceback
        traceback.print_exc()
        return False

def add_metadata(audio_path, title, gat_number, author="Medium Author"):
    """Add ID3 metadata to audio file."""
    try:
        final_mp3 = audio_path.parent / f"{gat_number}.mp3"

        display_title = f"{gat_number.replace('GAT-', '')} - {title}"
        album_name = display_title

        subprocess.run([
            'ffmpeg', '-i', str(audio_path),
            '-acodec', 'libmp3lame',
            '-ab', '128k',
            '-metadata', f'title={display_title}',
            '-metadata', f'album={album_name}',
            '-metadata', f'artist={author}',
            '-metadata', 'album_artist=Medium Articles',
            '-metadata', 'track=1',
            '-metadata', 'comment=High Priority Article',
            '-metadata', 'genre=Podcast',
            '-y',
            str(final_mp3)
        ], check=True, capture_output=True)

        audio_path.unlink()

        return final_mp3
    except subprocess.CalledProcessError as e:
        print(f"Error adding metadata: {e}")
        return None

def get_drive_service():
    """Get Google Drive API service using token from MCP server."""
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request

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

def upload_audio_to_drive(audio_path, mp3_folder_id="1NB1a1jGrqTmXvSw8CVQAsi_j05DCBg59"):
    """Upload audio file to Google Drive and return shareable link."""
    from googleapiclient.http import MediaFileUpload

    try:
        service = get_drive_service()

        file_name = os.path.basename(audio_path)
        file_metadata = {
            'name': file_name,
            'parents': [mp3_folder_id]
        }

        media = MediaFileUpload(str(audio_path), resumable=True)
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id',
            supportsAllDrives=True
        ).execute()

        file_id = file['id']

        # Make publicly accessible
        permission = {
            'type': 'anyone',
            'role': 'reader'
        }
        service.permissions().create(
            fileId=file_id,
            body=permission,
            supportsAllDrives=True
        ).execute()

        # Return shareable link (view link, not direct download)
        file = service.files().get(
            fileId=file_id,
            fields='webViewLink',
            supportsAllDrives=True
        ).execute()

        return file['webViewLink']

    except Exception as e:
        print(f"  ✗ Error uploading to Drive: {e}")
        return None

def update_jira_with_audio_link(ticket_id, audio_link):
    """Update JIRA ticket description to include audio link."""
    try:
        jira_token_file = os.path.expanduser("~/.jira.d/.pass")
        if not os.path.exists(jira_token_file):
            print(f"  ✗ JIRA token not found")
            return False

        with open(jira_token_file, 'r') as f:
            jira_token = f.read().strip()

        env = os.environ.copy()
        env['JIRA_API_TOKEN'] = jira_token

        # Get current ticket description
        result = subprocess.run(
            ['jira', 'issue', 'view', ticket_id],
            capture_output=True,
            text=True,
            timeout=30,
            env=env
        )

        if result.returncode != 0:
            print(f"  ✗ Failed to fetch ticket {ticket_id}")
            return False

        # Parse current description for article URL and PDF link
        output = result.stdout

        # Extract existing fields
        article_url_match = re.search(r'\*\*(?:Article URL|URL):\*\*\s+(https?://[^\s]+)', output)
        pdf_match = re.search(r'\*\*PDF:\*\*\s+(https?://[^\s]+)', output)

        article_url = article_url_match.group(1) if article_url_match else "Unknown"
        pdf_link = pdf_match.group(1) if pdf_match else None

        # Build updated description
        source = "Optimizely World Blog" if "world.optimizely.com" in article_url else "Medium"

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

        # Write description to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(new_description)
            temp_file = f.name

        # Update ticket
        result = subprocess.run(
            ['jira', 'issue', 'edit', ticket_id, '-b', new_description, '--no-input'],
            capture_output=True,
            text=True,
            timeout=30,
            env=env
        )

        os.unlink(temp_file)

        return result.returncode == 0

    except Exception as e:
        print(f"  ✗ Error updating JIRA: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    pdf_dir = Path(sys.argv[1])
    assessment_path = Path(sys.argv[2])
    output_dir = Path("/Users/bgerby/Documents/dev/ai/audio-reviews")

    # Optional metadata path for ticket ID mapping
    metadata_path = None
    if len(sys.argv) > 3:
        metadata_path = sys.argv[3]
    else:
        # Try to find metadata JSON automatically in /tmp/
        # Extract date from assessment filename (e.g., medium-articles-relevance-assessment-2025-10-28.md)
        import glob
        assessment_filename = assessment_path.name
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', assessment_filename)
        if date_match:
            date_str = date_match.group(1)
            # Try both with and without year prefix
            potential_patterns = [
                f'/tmp/medium-articles-{date_str}.json',
                f'/tmp/medium-articles-{date_str[-5:]}.json'  # MM-DD format
            ]
            for pattern in potential_patterns:
                matches = glob.glob(pattern)
                if matches:
                    metadata_path = matches[0]
                    break

    if not pdf_dir.exists():
        print(f"Error: PDF directory not found: {pdf_dir}")
        sys.exit(1)

    if not assessment_path.exists():
        print(f"Error: Assessment file not found: {assessment_path}")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    print("Medium Article Audio Generator")
    print("=" * 50)
    print(f"PDF Directory: {pdf_dir}")
    print(f"Assessment: {assessment_path}")
    if metadata_path:
        print(f"Metadata: {metadata_path}")
    print(f"Output Directory: {output_dir}")
    print()

    # Parse assessment
    print("Parsing assessment...")
    articles = parse_assessment(assessment_path, metadata_path)
    print(f"Found {len(articles)} HIGH/MEDIUM priority articles")
    print()

    results = []

    for article_num, article in sorted(articles.items()):
        print(f"\nProcessing Article {article_num}: {article['title']}")
        print(f"Ticket: {article['ticket_id']}")

        # Check if audio already exists
        output_mp3 = output_dir / f"{article['ticket_id']}.mp3"
        if output_mp3.exists():
            print(f"  ✓ Audio already exists: {output_mp3}")
            results.append({
                'ticket_id': article['ticket_id'],
                'audio_path': str(output_mp3),
                'status': 'existing'
            })
            continue

        # Find PDF - try both GAT format and numbered format
        # Format 1: GAT-387-how-to-work-with-claude-code...pdf
        pdf_pattern = f"{article['ticket_id']}-*.pdf"
        matching_pdfs = list(pdf_dir.glob(pdf_pattern))

        # Format 2 (fallback): 03-how-to-work-with-claude-code...pdf
        if not matching_pdfs:
            numbered_pattern = f"{article_num:02d}-*.pdf"
            matching_pdfs = list(pdf_dir.glob(numbered_pattern))
            if matching_pdfs:
                print(f"  Found PDF using numbered format: {matching_pdfs[0].name}")
            else:
                print(f"  ⚠ No PDF found (tried {pdf_pattern} and {numbered_pattern})")
                continue
        else:
            print(f"  Found PDF: {matching_pdfs[0].name}")

        pdf_path = matching_pdfs[0]

        # Extract and clean text
        print(f"  Extracting text from PDF...")
        text = extract_text_from_pdf(pdf_path)
        if not text:
            continue

        text = clean_text_for_speech(text)
        if len(text) < 100:
            print(f"  ⚠ Text too short ({len(text)} chars)")
            continue

        # Prepend executive summary
        full_text = article['executive_summary'] + text

        # Generate audio
        print(f"  Generating audio ({len(full_text)} chars)...")
        temp_audio = output_dir / f"{article['ticket_id']}.temp.mp3"

        if not generate_audio_openai(full_text, temp_audio):
            print(f"  ✗ Audio generation failed")
            continue

        # Add metadata
        print(f"  Adding metadata...")
        final_mp3 = add_metadata(temp_audio, article['title'], article['ticket_id'])

        if not final_mp3:
            print(f"  ✗ Metadata addition failed")
            continue

        print(f"  ✓ Created: {final_mp3}")

        # Upload to Google Drive
        print(f"  Uploading to Google Drive...")
        audio_drive_link = upload_audio_to_drive(final_mp3)

        if audio_drive_link:
            print(f"  ✓ Uploaded: {audio_drive_link}")

            # Convert view link to download link
            # Format: https://drive.google.com/file/d/FILE_ID/view?usp=drivesdk
            # Convert to: https://drive.google.com/uc?export=download&id=FILE_ID
            file_id_match = re.search(r'/d/([a-zA-Z0-9_-]+)/', audio_drive_link)
            if file_id_match:
                file_id = file_id_match.group(1)
                download_link = f"https://drive.google.com/uc?export=download&id={file_id}"

                # Update drive-urls.json
                drive_urls_file = output_dir / "drive-urls.json"
                try:
                    if drive_urls_file.exists():
                        with open(drive_urls_file, 'r') as f:
                            drive_urls = json.load(f)
                    else:
                        drive_urls = {}

                    drive_urls[f"{article['ticket_id']}.mp3"] = download_link

                    with open(drive_urls_file, 'w') as f:
                        json.dump(drive_urls, f, indent=2, sort_keys=True)

                    print(f"  ✓ Updated drive-urls.json")
                except Exception as e:
                    print(f"  ⚠ Failed to update drive-urls.json: {e}")

            # Update JIRA ticket with audio link
            print(f"  Updating JIRA ticket {article['ticket_id']}...")
            if update_jira_with_audio_link(article['ticket_id'], audio_drive_link):
                print(f"  ✓ JIRA ticket updated")
                results.append({
                    'ticket_id': article['ticket_id'],
                    'audio_path': str(final_mp3),
                    'audio_drive_link': audio_drive_link,
                    'title': article['title'],
                    'status': 'generated',
                    'jira_updated': True
                })
            else:
                print(f"  ⚠ JIRA update failed (audio file still available)")
                results.append({
                    'ticket_id': article['ticket_id'],
                    'audio_path': str(final_mp3),
                    'audio_drive_link': audio_drive_link,
                    'title': article['title'],
                    'status': 'generated',
                    'jira_updated': False
                })
        else:
            print(f"  ⚠ Drive upload failed (audio file still available locally)")
            results.append({
                'ticket_id': article['ticket_id'],
                'audio_path': str(final_mp3),
                'title': article['title'],
                'status': 'generated',
                'jira_updated': False
            })

    # Save results for reference
    results_file = output_dir / "audio-generation-results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n{'=' * 50}")
    print(f"Generated {len([r for r in results if r['status'] == 'generated'])} audio files")
    uploaded = len([r for r in results if r.get('audio_drive_link')])
    jira_updated = len([r for r in results if r.get('jira_updated')])
    print(f"Uploaded to Drive: {uploaded} files")
    print(f"JIRA tickets updated: {jira_updated}")
    print(f"Results saved to: {results_file}")

    # Update RSS feed if any audio files were generated
    if uploaded > 0:
        print(f"\n{'=' * 50}")
        print("Updating podcast RSS feed...")
        feed_dir = Path('/Users/bgerby/Documents/dev/ai/jaxon-research-feed')

        try:
            # Regenerate RSS feed
            result = subprocess.run(
                ['python3', 'generate-feed.py'],
                cwd=str(feed_dir),
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                print("✓ RSS feed regenerated")

                # Commit and push to GitHub Pages
                commit_msg = f"Add {uploaded} audio reviews from {Path(pdf_dir).name.split('-')[-1]}"

                subprocess.run(['git', 'add', 'feed.rss'], cwd=str(feed_dir), check=True)
                subprocess.run(['git', 'commit', '-m', commit_msg], cwd=str(feed_dir), check=True)
                subprocess.run(['git', 'push'], cwd=str(feed_dir), check=True)

                print("✓ RSS feed published to GitHub Pages")
                print("\nSubscribe URL:")
                print("https://jaxondigital.github.io/jaxon-research-feed/feed.rss")
            else:
                print(f"✗ RSS feed generation failed: {result.stderr}")

        except Exception as e:
            print(f"✗ Error updating RSS feed: {e}")
            print("  You can manually update with:")
            print(f"  cd {feed_dir}")
            print("  python3 generate-feed.py")
            print("  git add feed.rss && git commit -m 'Update feed' && git push")

if __name__ == '__main__':
    main()
