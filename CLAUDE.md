# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is a **strategy and analysis repository** for Jaxon Digital's AI agent business initiatives. It contains strategic documents analyzing market opportunities, business models, and revenue strategies related to agentic AI and DXP platforms.

## Key Documents

- **agentic-ai-dxp-analysis.md**: Strategic analysis of agentic AI trends in DXP market, including Jaxon Digital's positioning strategy for custom system agent enablement
- **q4-2025-revenue-strategy.md**: Detailed Q4 2025 revenue generation strategy focusing on Optimizely MCP services and OPAL implementations

## Working Context

### Business Context
- **Company**: Jaxon Digital (Optimizely implementation partner)
- **Assets**: 3 built MCPs for Optimizely DXP operations (CMS, Commerce, Operations)
- **Current Focus**: Custom MCP and agent development for Optimizely CMS/Commerce/DevOps
- **NOT Currently**: Working with Optimizely OPAL (OPAL focuses on experimentation/marketing campaigns; Jaxon focuses on core CMS/DevOps)
- **Service Model**: Managed services (setup + monthly monitoring/operations)
- **Target Market**: Existing Optimizely clients and enterprises with custom systems

### Strategic Focus Areas

**Current AI Agent Initiatives**:
1. **Custom Optimizely Agents** - Building production agents (e.g., Deployment Agent for DXP)
2. **Custom MCP Development** - Client-specific system integrations ($40-100K per MCP)
3. **Client System Integration** - Connecting legacy/proprietary systems to Optimizely
4. **Managed Agent Operations** - Ongoing monitoring and maintenance ($8-20K/month)
5. **CMS/DevOps Automation** - Deployment workflows, content operations, infrastructure management

**Service Approach**:
- **Build custom, not configure generic** - Paving own path vs using off-the-shelf platforms
- **Managed service model** - Not just build-and-leave, ongoing operations and support
- **Domain expertise** - Optimizely-native implementations, not generic automation
- **Production-ready agents** - Enterprise-grade with security, governance, audit trails

**Technology Stack**:
- **n8n** for workflow orchestration (MCP support confirmed on roadmap)
- **Custom MCPs** for Optimizely-specific operations
- **Proactive monitoring agents** - Event-driven architecture (not reactive/request-based)
- **Multi-MCP orchestration** - Complex workflows combining multiple MCPs

### Analysis Approach

When working with these strategic documents:
- Focus on actionable business insights, not generic commentary
- Maintain specific pricing, timelines, and ROI projections
- Preserve competitive analysis and market positioning details
- Keep sales messaging templates and objection handling intact
- Track metrics and success criteria as defined

### Document Updates

When updating these documents:
- Maintain the executive summary → detailed analysis structure
- Keep financial projections and pricing frameworks current
- Update based on actual client interactions and market feedback
- Preserve specific examples and case studies
- Document learnings and adjustments to strategy

## Project Management

### Jira Board
- **Project**: GAT (Growth & AI Transformation)
- **Board**: https://jaxondigital.atlassian.net/jira/software/c/projects/GAT/boards/228
- **Usage**: Use `jira` CLI commands with `-p GAT` flag for this project

**Common commands**:
```bash
export JIRA_API_TOKEN=$(cat ~/.jira.d/.pass)
jira issue list -p GAT --plain                    # List all tickets
jira issue view GAT-XXX                            # View specific ticket
jira issue move GAT-XXX "In Dev"                   # Update ticket status
```

## Medium Article Review Workflow

### Purpose
Daily process for reviewing Medium articles from digest emails and tracking insights relevant to Jaxon Digital's AI agent initiatives.

### Complete Workflow Reference
Full workflow documentation: `/Users/bgerby/Desktop/medium-article-review-workflow.md`

### CRITICAL: Bypassing Medium Paywalls with Playwright

**⚠️ ABSOLUTE REQUIREMENT:** Do NOT EVER process a paywalled article without properly gaining access to the entire article by having the user log in first. This is a hard requirement - no exceptions. Never generate PDFs, audio reviews, or analysis based on paywall preview content.

**Problem:** Many Medium articles are paywalled. PDFs saved without authentication show only preview content (~115KB files with "Create an account" message).

**Solution:** Use Playwright MCP with persistent browser session and manual login.

**Key Principle:**
- **Keep browser session open across all articles** - Don't close browser between articles
- Login persists as long as browser stays open
- Only close after capturing all articles

**Step-by-Step Process:**

1. **Open Browser with Visible UI (First Article Only)**
   ```bash
   # Navigate to Medium with headless: false so user can log in
   # Use Playwright MCP: mcp__playwright__playwright_navigate
   # Parameters:
   #   - url: "https://medium.com/@author/article-slug"
   #   - headless: false  # CRITICAL - must be visible for login
   #   - width: 1280, height: 720
   ```

2. **User Logs In Manually**
   - Browser window opens on screen
   - User clicks "Sign in" and enters credentials
   - Wait for login to complete
   - User signals ready to continue

3. **Capture First Article**
   ```bash
   # Save as PDF using Playwright MCP: mcp__playwright__playwright_save_as_pdf
   # Parameters:
   #   - name: "01-article-title.pdf"
   #   - outputPath: "/Users/bgerby/Desktop/medium-articles-YYYY-MM-DD"
   #   - fullPage: true
   #   - printBackground: true
   ```

4. **Navigate to Subsequent Articles (Browser Still Open)**
   ```bash
   # DO NOT close browser! Session persists.
   # Navigate to next article: mcp__playwright__playwright_navigate
   # Parameters:
   #   - url: "https://medium.com/@author/next-article"
   #   - headless: false  # Keep same session
   # Then save PDF with mcp__playwright__playwright_save_as_pdf
   ```

5. **Repeat for All Articles**
   - Navigate → Save PDF → Navigate → Save PDF
   - Session stays authenticated throughout
   - File sizes 400KB-5MB indicate successful capture
   - File sizes ~115KB indicate paywall (failed)

6. **Close Browser (After All Articles)**
   ```bash
   # Only close when done with entire batch
   # Use Playwright MCP: mcp__playwright__playwright_close
   ```

**Verification:**
```bash
# Check file sizes - successful captures are 400KB+
ls -lh /Users/bgerby/Desktop/medium-articles-*/*.pdf

# Files ~115KB = paywalled (only preview captured)
# Files 400KB-5MB = success (full article captured)
```

**Common Mistakes:**
- Closing browser between articles (loses login session)
- Using headless: true (can't manually log in)
- Not waiting for page load before saving PDF
- Forgetting to check file sizes for verification

**Alternative Approaches (Not Recommended):**
- `playwright_get_visible_html` - Works but PDF is better for review/archival
- Cookie/session persistence - More complex, manual login simpler
- Medium RSS feeds - Limited content, not full articles

**Integration with Article Processing:**
See `/Users/bgerby/Desktop/extract-medium-articles.py` for automated email extraction and Jira ticket creation workflow.

### Google Drive Integration (GAT-314, GAT-315)

**Status:** ✅ Completed October 21, 2025

**MCP Server:** google-docs-mcp-shared by jasonWong-serviceDirect
- Location: `/Users/bgerby/Documents/dev/ai/mcp-googledocs-server`
- Configuration: `.mcp.json` in project root
- OAuth credentials: Configured and working

**Shared Drive:**
- ID: `0ALLCxnOLmj3bUk9PVA`
- URL: https://drive.google.com/drive/u/0/folders/0ALLCxnOLmj3bUk9PVA

**Folder Structure:**
```
Shared Drive Root (0ALLCxnOLmj3bUk9PVA)
└── YYYY/ (e.g., 2025)
    └── MM-MonthName/ (e.g., 10-October)
        └── DD/ (e.g., 21)
            ├── PDFs/      (Article PDFs)
            ├── MP3s/      (Audio reviews)
            └── Summaries/ (Google Doc summaries)
```

**Example (October 21, 2025):**
- Year: `1x_1rltQ50Xrjn-jvgOD6w_z3jDl_e9ce`
- Month: `1mT5aQDDedY8SnW0K8rVSwe7NTd-l5E6I`
- Day: `1L_jgEZL-vLMzAvS4iuLkxTfSY88rTzQz`
- PDFs: `14MfsiDvH_5NaxQDvKuqslWNf3gduQZmA`
- MP3s: `1NB1a1jGrqTmXvSw8CVQAsi_j05DCBg59`
- Summaries: `1rFhAPnn7HNTEZqM6OQOdRS2rWAwEDW-E`

**Creating Folder Structure Dynamically:**
Folders are created as needed based on article date. Use the pattern:
1. Check if year folder exists (search for "YYYY" in Shared Drive root)
2. If not, create: `mcp__google-docs-drive__createFolder` with `parentFolderId=<SharedDriveId>`
3. Repeat for month (MM-MonthName) and day (DD)
4. Create type folders (PDFs/MP3s/Summaries) under day folder

**Important Limitations:**
- Documents CANNOT be created directly at Shared Drive root
- Must create folders first, then documents inside folders
- Use `parentFolderId` parameter (NOT `driveId`) for all operations

**Uploading Files to Drive:**
PDFs and MP3s are uploaded using the Google Drive Python API (not MCP). The workflow uses token from `/Users/bgerby/Documents/dev/ai/mcp-googledocs-server/token.json`.

## Complete Streamlined Workflow

**Updated:** October 22, 2025 - Added Google Doc formatting and JIRA comment improvements

### Scripts

All scripts located at `/Users/bgerby/Desktop/`:

1. **`extract-medium-articles.py`** - Extract URLs from email, create JIRA tickets
2. **`upload-to-drive-helper.py`** - Upload PDFs to Google Drive, update JIRA (used by Claude Code)
3. **`generate-audio-from-assessment.py`** - Generate audio from high-priority PDFs
4. **`upload-audio-to-drive.py`** - Upload audio to Drive, update JIRA

### Step-by-Step Process

**Step 1: Extract Articles and Create JIRA Tickets**

```bash
# Download email to /Users/bgerby/Desktop/MM-DD.eml
# Run extraction script
python3 /Users/bgerby/Desktop/extract-medium-articles.py /Users/bgerby/Desktop/10-21.eml --create-tickets --output-json /tmp/medium-articles.json

# This creates:
# - JIRA tickets GAT-XXX for each article
# - JSON metadata file with article info
# - Prints list of articles to capture
```

**Step 2: Capture PDFs with Playwright (Via Claude Code)**

Ask Claude Code to:
1. Create PDF directory: `/Users/bgerby/Desktop/medium-articles-YYYY-MM-DD/`
2. Navigate to first article with `headless: false` (user logs in manually)
3. Save each article as PDF: `01-article-slug.pdf`, `02-article-slug.pdf`, etc.
4. Keep browser open between articles (session persistence)
5. Close browser after all articles captured

**PDF Naming Convention:**
- `01-article-title-slug.pdf` (sequential numbering)
- File size check: 400KB+ = success, ~115KB = paywall/failed

**Step 3: Upload PDFs to Google Drive (Via Claude Code)**

Ask Claude Code to run Python script:
```python
# Use upload-to-drive-helper.py with article metadata
# This uploads PDFs and updates JIRA tickets with Drive links
```

Or manually in Claude Code session:
- Read metadata JSON
- Upload each PDF to appropriate Drive folder (YYYY/MM-Month/DD/PDFs/)
- Get shareable link
- Update JIRA ticket description with PDF link

**Step 4: Review Articles and Create Assessment (Via Claude Code)**

Ask Claude Code to:
1. Read all PDFs
2. Assess relevance to Jaxon Digital AI initiatives
3. Categorize as HIGH/MEDIUM/LOW priority
4. Create assessment document: `/Users/bgerby/Desktop/medium-articles-relevance-assessment-YYYY-MM-DD.md`
5. Save to Google Drive Summaries folder

**Step 5: Generate Audio for High-Priority Articles**

```bash
# Set OpenAI API key (from ~/.zshrc)
export OPENAI_API_KEY="sk-proj-..."

# Run audio generation script
python3 /Users/bgerby/Desktop/generate-audio-from-assessment.py \
    /Users/bgerby/Desktop/medium-articles-YYYY-MM-DD \
    /Users/bgerby/Desktop/medium-articles-relevance-assessment-YYYY-MM-DD.md

# Output: MP3 files in /Users/bgerby/Documents/dev/ai/audio-reviews/
# Format: GAT-XXX.mp3 (one per high-priority article)
```

**Audio Generation Details:**
- Uses OpenAI TTS API (model: tts-1, voice: onyx)
- Prepends executive summary with relevance rating and action items
- Splits long articles into chunks (4000 char limit)
- Adds ID3 metadata for iPhone Books app

**Step 6: Upload Audio to Google Drive**

```bash
# Run audio upload script
python3 /Users/bgerby/Desktop/upload-audio-to-drive.py

# This:
# - Uploads MP3s to Drive MP3s folder
# - Gets shareable links
# - Updates JIRA tickets with audio links
```

**Step 6a: Create Strategic Analysis and Google Docs (For Individual High-Priority Articles)**

For high-priority articles that warrant detailed strategic analysis:

1. **Create Strategic Analysis Markdown**:
   - Document: `/Users/bgerby/Desktop/GAT-XXX-article-review.md`
   - Include: 5-star relevance rating, executive summary, key insights, strategic implications, action items

2. **Upload to Google Drive**:
   ```bash
   # Use upload script to get PDF, MP3, and analysis files to Drive
   # Files go to: YYYY/MM-Month/DD/PDFs/, MP3s/, Summaries/ folders
   ```

3. **Create and Format Google Doc**:
   ```bash
   # Create Google Doc using MCP
   # Then format with proper markdown conversion
   python3 /tmp/format-google-doc.py
   ```

   The formatting script (`/tmp/format-google-doc.py`):
   - Parses markdown to identify headings, bold/italic, lists
   - Applies Google Docs native formatting (Heading 1/2/3, bold, italic)
   - Much better than raw markdown text dump
   - Reusable for all future strategic analysis documents

4. **Update JIRA with Google Drive Links**:
   ```bash
   # CRITICAL: Use temp file approach to avoid heredoc hangs
   cat > /tmp/jira-comment.txt << 'EOF'
   **Google Drive Links:**
   - **PDF:** https://drive.google.com/file/d/FILE_ID/view?usp=sharing
   - **Audio Review:** https://drive.google.com/uc?export=download&id=FILE_ID
   - **Strategic Analysis (Google Doc):** https://docs.google.com/document/d/DOC_ID/edit
   - **Strategic Analysis (Markdown):** https://drive.google.com/uc?export=download&id=FILE_ID
   EOF

   # Then add comment
   JIRA_API_TOKEN="`cat ~/.jira.d/.pass`" jira issue comment add GAT-XXX "$(cat /tmp/jira-comment.txt)" --no-input
   ```

   **Why Temp File Approach:**
   - Heredoc syntax with jira CLI causes the command to hang waiting for stdin
   - Using `$(cat file.txt)` works reliably
   - Always use backticks for token: `` `cat ~/.jira.d/.pass` `` not `$(cat ...)`
   - Always add `--no-input` flag to prevent interactive prompts

**Step 7: Final JIRA Ticket Format**

After all steps complete, JIRA tickets look like:

```markdown
Medium Article Review

**Article URL:** https://medium.com/@author/article-slug
**PDF:** https://drive.google.com/file/d/FILE_ID/view?usp=sharing
**Audio:** https://drive.google.com/file/d/FILE_ID/view?usp=sharing

To be reviewed for relevance to Jaxon Digital's AI agent initiatives.
```

### Key Technical Details

**OpenAI API Key:**
- Location: `~/.zshrc` as `OPENAI_API_KEY`
- Must be exported before running audio generation script
- Used for TTS audio generation

**Google Drive Token:**
- Location: `/Users/bgerby/Documents/dev/ai/mcp-googledocs-server/token.json`
- Used by both upload scripts
- Auto-refreshes when expired

**JIRA API Token:**
- Location: `~/.jira.d/.pass`
- Used for creating/updating tickets
- Set as environment variable: `JIRA_API_TOKEN=$(cat ~/.jira.d/.pass)`

**Article Metadata Mapping:**
- PDFs numbered sequentially: 01-12
- JIRA tickets: GAT-321, GAT-322, etc. (assigned by JIRA)
- Audio files named by ticket: GAT-321.mp3
- Mapping stored in JSON and assessment markdown

### Troubleshooting

**PDF file size ~115KB:**
- Article is paywalled and wasn't captured fully
- Re-capture with authenticated browser session
- Ensure login session persists across articles

**Audio generation fails:**
- Check `OPENAI_API_KEY` is set
- Verify API key is valid (not expired)
- Check PDF text extraction (run `pdftotext file.pdf -` manually)

**Google Drive upload fails:**
- Check token file exists and is valid
- Verify folder IDs are correct
- Ensure internet connection is stable

**JIRA update fails:**
- Verify `~/.jira.d/.pass` file exists
- Check ticket ID is correct (GAT-XXX)
- Use `--no-input` flag to avoid interactive prompts

## Repository Type

This is a **documentation/analysis repository**, not a code repository. There are no build commands, tests, or deployment processes. Work here involves strategic analysis, business planning, and documentation refinement.

## Podcast Feed for Article Reviews

### Purpose

Unified podcast feed for all article reviews (Medium, Optimizely World, technical blogs) with automatic played/unplayed tracking and sequential playback on iPhone Podcast app.

### Repository

- **Location**: `/Users/bgerby/Documents/dev/ai/jaxon-research-feed/`
- **GitHub**: https://github.com/JaxonDigital/jaxon-research-feed
- **GitHub Pages**: https://jaxondigital.github.io/jaxon-research-feed/

### Subscribe URL

Add this URL to your podcast app:

```
https://jaxondigital.github.io/jaxon-research-feed/feed.rss
```

### Scripts

Located in `/Users/bgerby/Documents/dev/ai/jaxon-research-feed/`:

1. **`generate-audio-review.py`** - Generate audio from single PDF article
   - Enhanced text cleaning to remove login banners, footer sections, WordPress elements
   - Splits long articles into chunks (4000 char limit)
   - Adds ID3 metadata for podcast apps
   - Output: `/Users/bgerby/Documents/dev/ai/audio-reviews/GAT-XXX.mp3`

2. **`sync-audio-to-drive.py`** - Upload MP3 files to Google Drive
   - Uploads to Google Drive folder (ID: `1NB1a1jGrqTmXvSw8CVQAsi_j05DCBg59`)
   - Sets public sharing permissions
   - Creates `drive-urls.json` mapping file
   - Skips files already uploaded

3. **`generate-feed.py`** - Create podcast RSS feed
   - Reads MP3 metadata using ffprobe
   - Loads Google Drive URLs from `drive-urls.json`
   - Generates iTunes-compatible RSS 2.0 feed
   - Output: `feed.rss` for GitHub Pages

### Workflow for Adding New Episodes

**1. Generate Audio from PDF**

```bash
# Set OpenAI API key (required)
export OPENAI_API_KEY="sk-proj-..."

# Generate audio for single article
cd /Users/bgerby/Documents/dev/ai/jaxon-research-feed
python3 generate-audio-review.py \
    "/path/to/article.pdf" \
    "GAT-333" \
    "Article Title" \
    "Executive summary with strategic context..." \
    "Author Name"

# Output: /Users/bgerby/Documents/dev/ai/audio-reviews/GAT-333.mp3
```

**Audio Generation Details:**
- Uses OpenAI TTS API (model: tts-1, voice: onyx, speed: 1.0)
- Prepends executive summary before article content
- Removes login banners, footer sections, code blocks, tag bubbles
- Adds ID3 metadata: title, album, artist, comment, genre

**2. Upload Audio to Google Drive**

```bash
cd /Users/bgerby/Documents/dev/ai/jaxon-research-feed
python3 sync-audio-to-drive.py

# This:
# - Finds new MP3 files in /Users/bgerby/Documents/dev/ai/audio-reviews/
# - Uploads to Google Drive (skips existing files)
# - Updates drive-urls.json with download links
```

**3. Update RSS Feed**

```bash
cd /Users/bgerby/Documents/dev/ai/jaxon-research-feed
python3 generate-feed.py

# This:
# - Reads MP3 metadata from audio-reviews/
# - Matches files to Google Drive URLs
# - Generates feed.rss with all episodes
```

**4. Publish to GitHub**

```bash
cd /Users/bgerby/Documents/dev/ai/jaxon-research-feed
git add feed.rss
git commit -m "Add GAT-333: Article Title"
git push

# GitHub Pages automatically updates the feed URL
# Podcast app will detect new episode on next refresh
```

### Batch Processing Multiple Articles

For generating audio for multiple high-priority articles, use the assessment-based script:

```bash
export OPENAI_API_KEY="sk-proj-..."

python3 /Users/bgerby/Desktop/generate-audio-from-assessment.py \
    /Users/bgerby/Desktop/medium-articles-YYYY-MM-DD \
    /Users/bgerby/Desktop/medium-articles-relevance-assessment-YYYY-MM-DD.md

# This:
# - Reads assessment markdown
# - Finds all HIGH priority articles
# - Generates audio for each in parallel
# - Outputs to /Users/bgerby/Documents/dev/ai/audio-reviews/
```

Then sync to Drive and update feed:

```bash
cd /Users/bgerby/Documents/dev/ai/jaxon-research-feed
python3 sync-audio-to-drive.py
python3 generate-feed.py
git add feed.rss && git commit -m "Add [count] new episodes" && git push
```

### File Naming Convention

- **PDFs**: `{seq}-{ticket#}-{title}.pdf` (e.g., `01-321-codemcp-budget.pdf`)
- **Audio**: `GAT-{ticket#}.mp3` (e.g., `GAT-321.mp3`)
- **RSS Title**: `{ticket#} - {title}` (e.g., `321 - How to Use CodeMCP for Development`)

### Technical Details

**Google Drive Integration:**
- Folder ID: `1NB1a1jGrqTmXvSw8CVQAsi_j05DCBg59` (MP3s folder in Shared Drive)
- Token: `/Users/bgerby/Documents/dev/ai/mcp-googledocs-server/token.json`
- Download URL format: `https://drive.google.com/uc?export=download&id={file_id}`

**OpenAI TTS API:**
- API Key: Stored in `~/.zshrc` as `OPENAI_API_KEY`
- Model: `tts-1` (standard quality)
- Voice: `onyx` (deep, authoritative)
- Speed: `1.0` (normal)
- Max chunk size: 4000 characters

**RSS Feed:**
- Format: RSS 2.0 with iTunes extensions
- Channel: Jaxon Research Feed
- Category: Technology
- Explicit: No
- Self URL: `https://jaxondigital.github.io/jaxon-research-feed/feed.rss`

**Podcast App Features:**
- Played/Unplayed tracking (automatic)
- Auto-play next episode (sequential)
- Download management
- Sort by date (oldest to newest or newest to oldest)
- Single show grouping (all episodes in "Jaxon Research Feed")

### Troubleshooting

**Audio generation fails:**
- Check `OPENAI_API_KEY` is set: `echo $OPENAI_API_KEY`
- Verify API key is valid (not expired)
- Check PDF text extraction: `pdftotext file.pdf -`
- Review text cleaning in `generate-audio-review.py:33-98`

**Episodes not appearing in podcast app:**
- Verify MP3 uploaded to Google Drive: Check `drive-urls.json`
- Ensure RSS feed updated: `cat feed.rss | grep GAT-XXX`
- Confirm pushed to GitHub: `git log -1`
- Wait 5-15 minutes for podcast app to refresh feed
- Force refresh in podcast app (pull down on show page)

**Login banners or footer text in audio:**
- Update regex patterns in `clean_text_for_speech()` function
- Test cleaning: `pdftotext file.pdf - | python3 -c "import sys; exec(open('generate-audio-review.py').read()); print(clean_text_for_speech(sys.stdin.read())[:500])"`
- Re-generate audio with updated script

**Drive upload fails:**
- Check token file exists: `ls -l /Users/bgerby/Documents/dev/ai/mcp-googledocs-server/token.json`
- Verify folder ID is correct: `1NB1a1jGrqTmXvSw8CVQAsi_j05DCBg59`
- Ensure internet connection is stable
- Check Google Drive quota/permissions
