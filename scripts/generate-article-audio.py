#!/usr/bin/env python3
"""
Generate audio files from Medium article PDFs for listening on iPhone.
Only generates for articles rated 3+ stars.
"""

import os
import sys
import subprocess
import re
from pathlib import Path

# Configuration
PDF_DIRS = [
    Path("/Users/bgerby/Documents/dev/ai/pdfs/medium-articles-2025-10-16"),
    Path("/Users/bgerby/Documents/dev/ai/pdfs/medium-articles-2025-10-17"),
]
AUDIO_OUTPUT_DIR = Path("/Users/bgerby/Documents/dev/ai/audio-reviews")
ANALYSIS_DIR = Path("/tmp")

# Star rating threshold
MIN_STARS = 3

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

def extract_title_and_author(text):
    """Extract article title, author, and publish date from PDF text."""
    try:
        # Extract title - appears after publication name, before "min read"
        title_match = re.search(
            r'(?:· Follow publication|Follow)\s*\n\s*\n(.+?)\n\s*\d+\s+min read',
            text,
            re.DOTALL
        )

        if title_match:
            title = title_match.group(1).strip()
            title = ' '.join(title.split())  # Clean up newlines
        else:
            # Fallback
            title_match = re.search(r'(.+?)\n\s*\d+\s+min read', text)
            title = title_match.group(1).strip() if title_match else None
            if title:
                title = ' '.join(title.split())

        # Extract publish date - appears as "X min read · Month Day, Year"
        date_match = re.search(
            r'\d+\s+min read\s+·\s+([A-Z][a-z]+)\s+(\d+),\s+(\d+)',
            text
        )

        if date_match:
            month, day, year = date_match.groups()
            # Convert to natural format
            publish_date = f"{month} {day}, {year}"
        else:
            publish_date = None

        # Extract author - appears after "min read · Date"
        author_match = re.search(
            r'\d+\s+min read\s+·\s+[A-Z][a-z]+\s+\d+,\s+\d+\s*\n\s*([^\n]+)',
            text
        )

        if author_match:
            author = author_match.group(1).strip()
            author = re.sub(r'\s*(Follow|Listen|Share|More)\s*$', '', author)
        else:
            author = None

        return title, author, publish_date

    except Exception as e:
        return None, None, None

def clean_text_for_speech(text):
    """Clean text to make it better for text-to-speech."""
    # Remove login/account UI elements (appears at top of PDFs)
    text = re.sub(r'Welcome back\. You are signed into your member account.*?Not you\?', '', text, flags=re.DOTALL)
    text = re.sub(r'bg••••@jaxondigital\.com', '', text)

    # Remove URLs
    text = re.sub(r'https?://\S+', '', text)

    # Remove common Medium UI elements and buttons
    text = re.sub(r'(Sidebar menu|Medium Logo|Write|Search|Notifications|Follow publication|Member-only story)', '', text)
    text = re.sub(r'\b(Follow|Listen|Share|More)\b\s*\n', '', text)
    text = re.sub(r'\d+ min read\s*·\s*[A-Z][a-z]+\s+\d+,\s+\d+', '', text)  # "10 min read · Oct 8, 2025"
    text = re.sub(r'\d+ min read', '', text)
    text = re.sub(r'See all from.*', '', text)
    text = re.sub(r'Recommended from Medium', '', text)

    # Remove code blocks (lines with high density of special characters)
    lines = text.split('\n')
    cleaned_lines = []
    in_code_block = False

    for line in lines:
        # Detect code-like patterns
        special_char_count = sum(1 for c in line if c in '{}[]();,=<>|&')
        total_chars = len(line.strip())

        # If line has >30% special chars and >10 chars, likely code
        if total_chars > 10 and special_char_count / total_chars > 0.3:
            in_code_block = True
            continue
        # Skip short lines immediately after code (often fragments)
        elif in_code_block and total_chars < 20:
            continue
        else:
            in_code_block = False
            cleaned_lines.append(line)

    text = '\n'.join(cleaned_lines)

    # Remove excessive newlines
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)

    # Remove leading/trailing whitespace
    text = text.strip()

    return text

def get_star_rating(gat_number):
    """Check analysis file for star rating."""
    analysis_file = ANALYSIS_DIR / f"gat-{gat_number}-analysis.txt"

    if not analysis_file.exists():
        return None

    try:
        with open(analysis_file, 'r') as f:
            content = f.read()

        # Look for rating patterns like "3/5 stars" or "4/5 stars"
        match = re.search(r'## Relevance to Jaxon Digital: (\d)/5 stars', content)
        if match:
            return int(match.group(1))

    except Exception as e:
        print(f"Error reading analysis file {analysis_file}: {e}")

    return None

def get_executive_summary(gat_number, star_rating, article_title=None, publish_date=None):
    """Generate executive summary in format: Title, published on Date. Rated X stars because Y. Likely action items: Z."""
    analysis_file = ANALYSIS_DIR / f"gat-{gat_number}-analysis.txt"

    if not analysis_file.exists():
        return None

    try:
        with open(analysis_file, 'r') as f:
            content = f.read()

        # Start with article title and date (NO GAT number in audio)
        if article_title and publish_date:
            summary = f"{article_title}, published on {publish_date}. "
        elif article_title:
            summary = f"{article_title}. "
        else:
            summary = ""

        # Add star rating
        summary += f"Rated {star_rating} out of 5 stars "

        # Extract specific relevance reason
        # Look for text right after "## Relevance to Jaxon Digital: X/5 stars"
        relevance_match = re.search(
            r'## Relevance to Jaxon Digital: \d/5 stars\s*\n\s*\n([^\n]+(?:\n(?!##)[^\n]+)*)',
            content
        )

        if relevance_match:
            relevance_text = relevance_match.group(1).strip()
            # Clean markdown and get first 1-2 sentences
            relevance_clean = re.sub(r'\*\*([^*]+)\*\*', r'\1', relevance_text)
            relevance_clean = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', relevance_clean)

            # Get first sentence or two about WHY it's relevant
            sentences = re.split(r'[.!?]\s+', relevance_clean)
            why_text = sentences[0] if sentences else relevance_clean
            summary += f"because {why_text.lower()}. "
        else:
            summary += ". "

        # Extract action items from analysis
        action_patterns = [
            r'## (?:Recommended )?(?:Next Steps?|Actions?|Immediate Actions?)\s*\n\s*\n((?:[^\n#]+(?:\n(?!##)[^\n#]+)*){0,500})',
        ]

        action_items = []
        for pattern in action_patterns:
            action_match = re.search(pattern, content, re.IGNORECASE)
            if action_match:
                action_text = action_match.group(1).strip()
                # Extract bullet points
                bullets = re.findall(r'(?:^|\n)(?:\d+\.\s*)?[-•*]\s*([^\n]+)', action_text)
                if bullets:
                    # Clean up markdown and take first 2-3 items
                    for bullet in bullets[:3]:
                        clean = re.sub(r'\*\*([^*]+)\*\*', r'\1', bullet)
                        clean = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', clean)
                        # Remove checkbox markers
                        clean = re.sub(r'^[✅✓☑]\s*', '', clean)
                        action_items.append(clean.strip())
                break

        if action_items:
            # Format action items naturally
            if len(action_items) == 1:
                summary += f"Likely action item: {action_items[0]}. "
            elif len(action_items) == 2:
                summary += f"Likely action items: {action_items[0]}, and {action_items[1]}. "
            else:
                summary += f"Likely action items: {', '.join(action_items[:-1])}, and {action_items[-1]}. "

        # Add pause before article content
        summary += "\n\nNow, here's the full article. \n\n"

        return summary

    except Exception as e:
        print(f"Error generating executive summary: {e}")
        import traceback
        traceback.print_exc()

    return None

def generate_audio_openai(text, output_path, title):
    """Generate audio using OpenAI TTS API."""
    import json
    import tempfile

    # Get API key from environment
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY not set in environment")
        return False

    try:
        # OpenAI has 4096 char limit - split into chunks if needed
        max_chunk_size = 4000  # Leave some margin

        if len(text) <= max_chunk_size:
            # Single chunk - simple case
            chunks = [text]
        else:
            # Split on paragraph boundaries to avoid cutting mid-sentence
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

        # Generate audio for each chunk
        chunk_files = []
        for i, chunk in enumerate(chunks):
            chunk_file = output_path.parent / f"{output_path.stem}.chunk{i}.mp3"

            # Create temporary file for request
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump({
                    "model": "tts-1",
                    "input": chunk,
                    "voice": "onyx",
                    "speed": 1.0
                }, f)
                json_file = f.name

            # Call OpenAI API using curl
            subprocess.run([
                'curl', '-s',
                'https://api.openai.com/v1/audio/speech',
                '-H', f'Authorization: Bearer {api_key}',
                '-H', 'Content-Type: application/json',
                '-d', f'@{json_file}',
                '--output', str(chunk_file)
            ], check=True, capture_output=True)

            # Clean up temp file
            os.unlink(json_file)

            if not chunk_file.exists() or chunk_file.stat().st_size < 1000:
                print(f"Error: Chunk {i} not created or too small")
                # Clean up chunk files
                for cf in chunk_files:
                    cf.unlink()
                return False

            chunk_files.append(chunk_file)

        # Combine chunks using ffmpeg if multiple
        if len(chunk_files) == 1:
            chunk_files[0].rename(output_path)
        else:
            # Create concat file for ffmpeg
            concat_file = output_path.parent / f"{output_path.stem}.concat.txt"
            with open(concat_file, 'w') as f:
                for chunk_file in chunk_files:
                    f.write(f"file '{chunk_file.name}'\n")

            # Concatenate audio files
            subprocess.run([
                'ffmpeg', '-f', 'concat', '-safe', '0',
                '-i', str(concat_file),
                '-acodec', 'copy',
                '-y', str(output_path)
            ], check=True, capture_output=True)

            # Clean up
            concat_file.unlink()
            for chunk_file in chunk_files:
                chunk_file.unlink()

        # Check if output was created
        if output_path.exists() and output_path.stat().st_size > 1000:
            return True
        else:
            print(f"Error: Final audio file not created or too small")
            return False

    except Exception as e:
        print(f"Error generating audio: {e}")
        return False

def generate_audio(text, output_path, title):
    """Generate audio - tries OpenAI first, falls back to macOS say."""
    # Try OpenAI TTS first (much better quality)
    if os.environ.get('OPENAI_API_KEY'):
        # OpenAI outputs MP3 directly - use that
        if generate_audio_openai(text, output_path, title):
            return True
        else:
            print("  OpenAI TTS failed, falling back to macOS say...")

    # Fallback to macOS say (outputs AIFF)
    try:
        # Use Daniel voice (UK English, more natural)
        # Rate: 160 words per minute
        subprocess.run(
            ['say', '-v', 'Daniel', '-r', '160', '-o', str(output_path), text],
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error generating audio: {e}")
        return False

def add_metadata(audio_path, title, track_number, star_rating, author="Unknown Author", slug=""):
    """Add ID3 metadata to audio file using ffmpeg."""
    try:
        # Add metadata to MP3 (need to re-encode for metadata to work)
        # Include slug in filename for easier identification
        if slug:
            final_mp3 = audio_path.parent / f"GAT-{track_number}-{slug}.mp3"
        else:
            final_mp3 = audio_path.parent / f"GAT-{track_number}.mp3"

        # Improve title display for Books app
        # Remove "GAT-XXX:" prefix and replace all colons with dashes
        # "233 - AI Agent for DevOps - How to Build..." instead of "GAT-233: AI Agent for DevOps: How to Build..."
        display_title = title.replace(f'GAT-{track_number}:', f'{track_number} -')
        display_title = display_title.replace(':', ' -')  # Replace remaining colons

        # Use title as album so each appears as separate audiobook
        album_name = display_title

        subprocess.run([
            'ffmpeg', '-i', str(audio_path),
            '-acodec', 'libmp3lame',
            '-ab', '128k',
            '-metadata', f'title={display_title}',
            '-metadata', f'album={album_name}',
            '-metadata', f'artist={author}',
            '-metadata', 'album_artist=Medium Articles',
            '-metadata', 'track=1',  # Always track 1 since each is its own book
            '-metadata', f'comment=Relevance: {star_rating}/5 stars',
            '-metadata', 'genre=Podcast',
            '-y',  # Overwrite output file
            str(final_mp3)
        ], check=True, capture_output=True)

        # Remove temp file
        audio_path.unlink()

        return final_mp3
    except subprocess.CalledProcessError as e:
        print(f"Error adding metadata: {e}")
        return None

def process_article(pdf_path):
    """Process a single article PDF."""
    filename = pdf_path.stem

    # Extract GAT number and slug from filename (e.g., "GAT-234-article-title.pdf")
    match = re.match(r'GAT-(\d+)(?:-(.+))?', filename)
    if not match:
        print(f"Skipping {filename}: No GAT number found")
        return False

    gat_number = match.group(1)
    slug = match.group(2) if match.group(2) else ""  # Optional slug after GAT number

    # Check PDF file size (small PDFs are likely paywalled/incomplete)
    pdf_size = pdf_path.stat().st_size
    if pdf_size < 200_000:  # Less than 200KB likely paywall
        print(f"Skipping GAT-{gat_number}: PDF too small ({pdf_size:,} bytes, likely paywalled)")
        return False

    # Check star rating
    star_rating = get_star_rating(gat_number)
    if star_rating is None:
        print(f"Skipping GAT-{gat_number}: No analysis found (not reviewed yet)")
        return False

    if star_rating < MIN_STARS:
        print(f"Skipping GAT-{gat_number}: Only {star_rating}/5 stars (< {MIN_STARS})")
        return False

    print(f"\nProcessing GAT-{gat_number} ({star_rating}/5 stars)...")

    # Check if audio already exists
    output_mp3 = AUDIO_OUTPUT_DIR / f"GAT-{gat_number}.mp3"
    if output_mp3.exists():
        print(f"  Audio already exists: {output_mp3}")
        return True

    # Extract text
    print(f"  Extracting text from PDF...")
    text = extract_text_from_pdf(pdf_path)
    if not text:
        return False

    # Extract title, author, and publish date for metadata and summary
    article_title, article_author, publish_date = extract_title_and_author(text)

    # Clean text
    print(f"  Cleaning text...")
    text = clean_text_for_speech(text)

    if len(text) < 100:
        print(f"  Skipping: Text too short ({len(text)} chars)")
        return False

    # Prepend executive summary with title, date, relevance, and action items
    executive_summary = get_executive_summary(gat_number, star_rating, article_title, publish_date)
    if executive_summary:
        print(f"  Adding executive summary...")
        text = executive_summary + "\n\n" + text

    # Generate audio
    print(f"  Generating audio ({len(text)} chars)...")
    temp_audio = AUDIO_OUTPUT_DIR / f"GAT-{gat_number}.temp.mp3"

    if not generate_audio(text, temp_audio, filename):
        return False

    # Add metadata
    print(f"  Adding metadata...")
    if article_title and article_author:
        title = f"GAT-{gat_number}: {article_title}"
        author = article_author
    else:
        # Fallback to filename if extraction failed
        title = f"GAT-{gat_number}: {filename.replace('GAT-' + gat_number + '-', '')} ({star_rating}/5)"
        author = "Unknown Author"

    mp3_path = add_metadata(temp_audio, title, int(gat_number), star_rating, author, slug)
    if not mp3_path:
        return False

    print(f"  ✓ Created: {mp3_path}")
    return True

def main():
    """Main function."""
    # Create output directory
    AUDIO_OUTPUT_DIR.mkdir(exist_ok=True)

    print(f"Medium Article Audio Generator")
    print(f"================================")
    print(f"PDF Directories: {', '.join(str(d) for d in PDF_DIRS)}")
    print(f"Output Directory: {AUDIO_OUTPUT_DIR}")
    print(f"Minimum Stars: {MIN_STARS}")
    print()

    # Check for required commands
    required_commands = ['pdftotext', 'say', 'ffmpeg']
    for cmd in required_commands:
        try:
            subprocess.run(['which', cmd], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print(f"Error: Required command '{cmd}' not found")
            print(f"Install with: brew install {cmd}")
            return 1

    # Find all PDFs across all directories
    pdf_files = []
    for pdf_dir in PDF_DIRS:
        if pdf_dir.exists():
            pdf_files.extend(pdf_dir.glob("GAT-*.pdf"))
    pdf_files = sorted(pdf_files)

    if not pdf_files:
        print(f"No PDF files found in any directory")
        return 1

    print(f"Found {len(pdf_files)} PDF files\n")

    # Process each PDF
    success_count = 0
    skip_count = 0
    error_count = 0

    for pdf_path in pdf_files:
        try:
            result = process_article(pdf_path)
            if result:
                success_count += 1
            else:
                skip_count += 1
        except Exception as e:
            print(f"Error processing {pdf_path}: {e}")
            error_count += 1

    # Summary
    print(f"\n{'='*50}")
    print(f"Summary:")
    print(f"  Generated: {success_count}")
    print(f"  Skipped: {skip_count}")
    print(f"  Errors: {error_count}")
    print(f"\nAudio files saved to: {AUDIO_OUTPUT_DIR}")
    print(f"\nNext steps:")
    print(f"  1. Connect iPhone via cable")
    print(f"  2. Finder → iPhone → Check 'Show this iPhone when on Wi-Fi'")
    print(f"  3. Drag {AUDIO_OUTPUT_DIR} to Podcasts tab")
    print(f"  4. Click Sync")
    print(f"  5. Disconnect cable (wireless sync works from now on!)")

if __name__ == '__main__':
    sys.exit(main())
