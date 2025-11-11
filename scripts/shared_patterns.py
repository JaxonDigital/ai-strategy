"""
Shared constants and regex patterns used across article processing scripts.

This module centralizes commonly used patterns to prevent divergence between
scripts like extract-medium-articles.py and prepare-pdf-capture.py.

Updated: November 11, 2025
"""

# Medium article URL patterns
# Format: medium.com/@username/article-slug-12digitid
MEDIUM_USER_ARTICLE_PATTERN = r'https://medium\.com/@[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+-[a-f0-9]{12}'

# Format: medium.com/publication/article-slug-12digitid
# Exclude common non-article paths
MEDIUM_PUB_ARTICLE_PATTERN = r'https://medium\.com/(?!plans|jobs-at-medium|@)[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+-[a-f0-9]{12}'

# JIRA project identifiers
JIRA_PROJECT_GAT = 'GAT'  # Growth & AI Transformation
JIRA_TICKET_PATTERN = r'GAT-\d+'

# Priority levels
PRIORITY_HIGH = 'HIGH'
PRIORITY_MEDIUM = 'MEDIUM'
PRIORITY_LOW = 'LOW'

# File naming conventions
def get_pdf_filename_pattern(article_number):
    """Get glob pattern for finding PDF by article number (robust to filename variations)."""
    return f"{article_number:02d}-*.pdf"

def get_audio_filename(ticket_id):
    """Get standard audio filename for a JIRA ticket."""
    return f"{ticket_id}.mp3"

# Drive folder structure
SHARED_DRIVE_ID = '0ALLCxnOLmj3bUk9PVA'

def get_drive_folder_path(date_obj):
    """
    Get Drive folder path components for a given date.

    Args:
        date_obj: datetime object

    Returns:
        tuple: (year, month, day) folder names
    """
    year = date_obj.strftime('%Y')
    month = date_obj.strftime('%m-%B')  # e.g., "11-November"
    day = date_obj.strftime('%d')
    return (year, month, day)

# Audio generation settings
AUDIO_CHUNK_MAX_CHARS = 4000  # OpenAI TTS limit
AUDIO_BITRATE = '128k'
AUDIO_CODEC = 'libmp3lame'

# PDF validation thresholds
PDF_MIN_CHARS = 100  # Minimum chars for valid PDF
PDF_SUSPICIOUS_THRESHOLD = 500  # Chars below which PDF is suspicious
PDF_PAYWALL_THRESHOLD = 2000  # Max chars for detected paywall content

PAYWALL_INDICATORS = [
    'member-only story',
    'this story is for medium members',
    'upgrade to continue reading',
    'become a member to read this story',
    'sign up to read'
]

# State file locations
OPTIMIZELY_STATE_FILE = "~/.optimizely-blog-state.json"
ANTHROPIC_STATE_FILE = "~/.anthropic-news-state.json"

# Error log location
ERROR_LOG_FILE = "/tmp/workflow-errors.log"
