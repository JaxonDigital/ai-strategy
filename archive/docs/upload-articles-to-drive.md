# Upload Medium Articles to Google Drive

This document describes the workflow for uploading Medium article PDFs to Google Drive using Claude Code.

## Prerequisites

1. Article metadata JSON file (created by `extract-medium-articles.py --output-json`)
2. PDF files captured with Playwright
3. Google Drive MCP configured with Shared Drive access

## Workflow

### Step 1: Run Python script to extract articles and create JIRA tickets

```bash
python3 /Users/bgerby/Desktop/extract-medium-articles.py /path/to/email.eml \
  --create-tickets \
  --output-json /tmp/medium-articles.json
```

This creates:
- JIRA tickets for each article
- JSON file with article metadata (titles, URLs, ticket IDs)

### Step 2: Capture PDFs with Playwright (via Claude Code)

For each article in the JSON file:
1. Navigate to article URL with authenticated browser
2. Save as PDF to local directory
3. Upload PDF to Google Drive (Year/Month/Day/PDFs folder)
4. Get shareable link
5. Update JIRA ticket description with Drive link

### Step 3: Generate audio reviews (optional, for high-value articles)

1. Read PDF content
2. Generate audio summary
3. Upload MP3 to Google Drive (Year/Month/Day/MP3s folder)
4. Update JIRA ticket with audio link

### Step 4: Create summary in Google Docs

1. Analyze article content
2. Create Google Doc summary in Summaries folder
3. Update JIRA ticket with summary link

## Folder Structure

```
Shared Drive (0ALLCxnOLmj3bUk9PVA)
└── 2025/
    └── 10-October/
        └── 21/
            ├── PDFs/     (14MfsiDvH_5NaxQDvKuqslWNf3gduQZmA)
            ├── MP3s/     (1NB1a1jGrqTmXvSw8CVQAsi_j05DCBg59)
            └── Summaries/(1rFhAPnn7HNTEZqM6OQOdRS2rWAwEDW-E)
```

Folders created dynamically based on article date.

## JIRA Ticket Format (After Upload)

```markdown
Medium Article Review

**Article URL:** https://medium.com/@author/article-slug
**PDF:** https://drive.google.com/file/d/FILE_ID/view?usp=sharing
**Audio:** https://drive.google.com/file/d/FILE_ID/view?usp=sharing  (if generated)
**Summary:** https://docs.google.com/document/d/DOC_ID/edit?usp=sharing

To be reviewed for relevance to Jaxon Digital's AI agent initiatives.
```

## Implementation Notes

- Python script handles email parsing and JIRA ticket creation
- Claude Code handles all Google Drive operations (can't be done from standalone Python)
- Metadata JSON file acts as bridge between the two
- Folder structure created dynamically based on article date
