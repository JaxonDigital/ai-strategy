#!/usr/bin/env python3
"""
Retry audio generation for a single article.

Usage:
    python3 retry-single-audio.py GAT-518 "Article Title" /path/to/pdf
"""

import sys
import os
import json
import subprocess
import tempfile
from pathlib import Path

def extract_pdf_text(pdf_path):
    """Extract text from PDF using pdftotext."""
    try:
        result = subprocess.run(
            ['pdftotext', '-layout', str(pdf_path), '-'],
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )
        return result.stdout
    except Exception as e:
        print(f"Error extracting PDF text: {e}")
        return None

def crop_footer(text):
    """Remove footer content (Topics, Written by, Recommendations)."""
    lines = text.split('\n')

    # Find where footer starts
    footer_markers = [
        'Topics',
        'Written by',
        'Recommended from',
        'More from',
        'Help',
        'Status',
        'About',
        'Careers',
        'Press',
        'Blog',
        'Privacy',
        'Terms',
        'Text to speech',
        'Teams'
    ]

    # Scan backwards to find footer start
    cutoff = len(lines)
    for i in range(len(lines) - 1, max(0, len(lines) - 100), -1):
        line = lines[i].strip()
        if any(marker in line for marker in footer_markers):
            cutoff = i
            break

    return '\n'.join(lines[:cutoff])

def generate_audio_with_retry(text, output_path, max_retries=3):
    """Generate audio using OpenAI TTS with retry logic."""
    import time

    # Split text into chunks if needed (4096 char limit)
    max_chunk_size = 4000
    chunks = []

    if len(text) <= max_chunk_size:
        chunks = [text]
    else:
        # Split by paragraphs
        paragraphs = text.split('\n\n')
        current_chunk = ""

        for para in paragraphs:
            if len(current_chunk) + len(para) + 2 <= max_chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = para + "\n\n"

        if current_chunk:
            chunks.append(current_chunk)

    print(f"  Generating audio ({len(text)} chars, {len(chunks)} chunks)...")

    # Generate each chunk
    chunk_files = []
    for i, chunk in enumerate(chunks):
        chunk_file = output_path.parent / f"{output_path.stem}.temp.chunk{i}.mp3"

        # Retry logic for this chunk
        for attempt in range(max_retries):
            try:
                # Create temp JSON file for request
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                    json.dump({
                        "model": "tts-1",
                        "input": chunk,
                        "voice": "onyx"
                    }, f)
                    json_file = f.name

                # Use curl to call OpenAI API
                result = subprocess.run([
                    'curl', '-s',
                    'https://api.openai.com/v1/audio/speech',
                    '-H', f'Authorization: Bearer {os.environ.get("OPENAI_API_KEY")}',
                    '-H', 'Content-Type: application/json',
                    '-d', f'@{json_file}',
                    '--output', str(chunk_file)
                ], capture_output=True, timeout=60, check=True)

                os.unlink(json_file)

                # Verify file was created and has content
                if chunk_file.exists() and chunk_file.stat().st_size > 1000:
                    chunk_files.append(chunk_file)
                    print(f"    ✓ Chunk {i+1}/{len(chunks)} generated")
                    break
                else:
                    raise Exception(f"Chunk file is too small or missing")

            except Exception as e:
                print(f"    Attempt {attempt + 1}/{max_retries} failed for chunk {i+1}: {e}")
                if chunk_file.exists():
                    chunk_file.unlink()
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    # Cleanup and fail
                    for cf in chunk_files:
                        if cf.exists():
                            cf.unlink()
                    return False

    # Concatenate chunks if multiple
    if len(chunk_files) == 1:
        chunk_files[0].rename(output_path)
    else:
        # Use ffmpeg to concatenate
        concat_list = output_path.parent / f"{output_path.stem}.concat.txt"
        with open(concat_list, 'w') as f:
            for chunk_file in chunk_files:
                f.write(f"file '{chunk_file.name}'\n")

        subprocess.run([
            'ffmpeg', '-f', 'concat', '-safe', '0',
            '-i', str(concat_list),
            '-c', 'copy',
            str(output_path)
        ], capture_output=True, check=True)

        # Cleanup
        concat_list.unlink()
        for chunk_file in chunk_files:
            chunk_file.unlink()

    return True

def add_metadata(mp3_path, ticket_id, title):
    """Add ID3 tags to MP3 file."""
    subprocess.run([
        'ffmpeg', '-i', str(mp3_path),
        '-metadata', f'title={title}',
        '-metadata', f'artist=Jaxon Research',
        '-metadata', f'album=Medium Article Review',
        '-metadata', f'comment={ticket_id}',
        '-codec', 'copy',
        '-y',
        str(mp3_path) + '.tagged'
    ], capture_output=True, check=True)

    Path(str(mp3_path) + '.tagged').rename(mp3_path)
    print(f"  ✓ Added metadata")

def upload_to_drive(mp3_path, ticket_id):
    """Upload MP3 to Google Drive and return download link."""
    # This would use the same upload logic from generate-audio-from-assessment.py
    # For now, we'll use the upload-audio-to-drive.py script
    upload_script = Path(__file__).parent / 'upload-audio-to-drive.py'

    result = subprocess.run([
        'python3', str(upload_script),
        str(mp3_path)
    ], capture_output=True, text=True, timeout=120)

    if result.returncode == 0:
        # Extract Drive link from output
        for line in result.stdout.split('\n'):
            if 'drive.google.com' in line and 'view?' in line:
                return line.split()[-1]

    return None

def update_jira(ticket_id, audio_link):
    """Update JIRA ticket with audio link."""
    # Fetch current ticket description
    result = subprocess.run([
        'bash', '-c',
        f'export JIRA_API_TOKEN="`cat ~/.jira.d/.pass`" && jira issue view {ticket_id} --plain'
    ], capture_output=True, text=True, timeout=30)

    if result.returncode != 0:
        print(f"  ✗ Failed to fetch JIRA ticket")
        return False

    # Update audio link in description
    current_desc = result.stdout

    # Find the audio line and update it
    lines = current_desc.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('**Audio:**'):
            lines[i] = f'**Audio:** {audio_link}'
            break
    else:
        # Audio line doesn't exist, add it after PDF line
        for i, line in enumerate(lines):
            if line.startswith('**PDF:**'):
                lines.insert(i + 1, f'**Audio:** {audio_link}')
                break

    new_desc = '\n'.join(lines)

    # Write to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(new_desc)
        temp_file = f.name

    # Update JIRA
    result = subprocess.run([
        'bash', '-c',
        f'export JIRA_API_TOKEN="`cat ~/.jira.d/.pass`" && jira issue edit {ticket_id} -b "$(cat {temp_file})" --no-input'
    ], capture_output=True, text=True, timeout=30)

    os.unlink(temp_file)

    return result.returncode == 0

def main():
    if len(sys.argv) != 4:
        print("Usage: python3 retry-single-audio.py GAT-XXX 'Article Title' /path/to/pdf")
        sys.exit(1)

    ticket_id = sys.argv[1]
    title = sys.argv[2]
    pdf_path = Path(sys.argv[3])

    if not pdf_path.exists():
        print(f"Error: PDF not found: {pdf_path}")
        sys.exit(1)

    output_dir = Path("/Users/bgerby/Documents/dev/ai/audio-reviews")
    output_mp3 = output_dir / f"{ticket_id}.mp3"

    print(f"\nRetrying audio generation for {ticket_id}")
    print(f"PDF: {pdf_path}")
    print(f"Output: {output_mp3}\n")

    # Extract text
    print("Extracting text from PDF...")
    text = extract_pdf_text(pdf_path)
    if not text:
        print("✗ Failed to extract PDF text")
        sys.exit(1)

    # Crop footer
    text = crop_footer(text)
    print(f"✓ Extracted {len(text)} characters\n")

    # Generate audio with retry
    if not generate_audio_with_retry(text, output_mp3):
        print("\n✗ Audio generation failed after retries")
        sys.exit(1)

    print(f"\n✓ Created: {output_mp3}")

    # Add metadata
    add_metadata(output_mp3, ticket_id, title)

    # Upload to Drive
    print("\nUploading to Google Drive...")
    audio_link = upload_to_drive(output_mp3, ticket_id)
    if not audio_link:
        print("✗ Upload failed")
        sys.exit(1)

    print(f"✓ Uploaded: {audio_link}")

    # Update JIRA
    print(f"\nUpdating JIRA ticket {ticket_id}...")
    if update_jira(ticket_id, audio_link):
        print(f"✓ JIRA ticket updated")
    else:
        print(f"⚠ JIRA update failed (but audio was uploaded)")

    # Update drive-urls.json
    drive_urls_file = output_dir / "drive-urls.json"
    if drive_urls_file.exists():
        with open(drive_urls_file, 'r') as f:
            drive_urls = json.load(f)
    else:
        drive_urls = {}

    file_id = audio_link.split('/d/')[1].split('/')[0]
    download_link = f"https://drive.google.com/uc?export=download&id={file_id}"
    drive_urls[f"{ticket_id}.mp3"] = download_link

    with open(drive_urls_file, 'w') as f:
        json.dump(drive_urls, f, indent=2, sort_keys=True)

    print(f"✓ Updated drive-urls.json")

    print("\n✅ Audio generation complete!")

if __name__ == '__main__':
    main()
