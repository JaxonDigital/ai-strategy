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

**Updated:** October 23, 2025
- Added automated PDF assessment script (generate-article-assessment.py)
- Added Medium recommendation analysis feature
- Completed full workflow for Optimizely World articles (GAT-350 through GAT-369)
- Published 7 HIGH priority episodes to podcast feed

### Scripts

All scripts located at `/Users/bgerby/Desktop/`:

1. **`extract-medium-articles.py`** - Extract URLs from email, create JIRA tickets
2. **`upload-to-drive-helper.py`** - Upload PDFs to Google Drive, update JIRA (used by Claude Code)
3. **`generate-article-assessment.py`** - Automated PDF analysis and relevance assessment using OpenAI GPT-4 (NEW - October 23, 2025)
4. **`generate-audio-from-assessment.py`** - Generate audio from high-priority PDFs
5. **`upload-audio-to-drive.py`** - Upload audio to Drive, update JIRA
6. **`generate-medium-recommendations.py`** - Analyze relevance assessment and generate recommendations for improving Medium follows (NEW - October 23, 2025)

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

**Step 4: Review Articles and Create Assessment (Automated with Python + OpenAI)**

**NEW (October 23, 2025):** Use automated Python script to avoid Claude token limit issues when processing large batches.

```bash
# Set OpenAI API key (required)
export OPENAI_API_KEY="sk-proj-..."

# Run automated assessment script
python3 /Users/bgerby/Desktop/generate-article-assessment.py \
    /Users/bgerby/Desktop/medium-articles-YYYY-MM-DD/ \
    /tmp/medium-articles.json \
    /Users/bgerby/Desktop/medium-articles-relevance-assessment-YYYY-MM-DD.md

# This:
# - Extracts text from all PDFs using pdftotext
# - Analyzes each article with GPT-4 Turbo using Jaxon strategic context
# - Handles large PDFs by chunking with overlap (no token limits!)
# - Categorizes as HIGH/MEDIUM/LOW priority
# - Generates comprehensive markdown assessment document
```

**Why Python Script vs Claude Code:**
- **Scalability**: Handles 20, 50, 100+ articles without token limits
- **Consistency**: Same strategic criteria applied uniformly to all articles
- **Chunking**: Automatically splits large documents (12K+ chars) with overlap
- **Speed**: Parallel processing with rate limiting
- **Reliability**: Robust error handling, continues on failures

**OpenAI Analysis Quality:**
- Uses GPT-4 Turbo for strategic assessment
- Full Jaxon Digital context injected in every prompt
- Structured JSON output for consistency
- Synthesis step for multi-chunk articles

**Hybrid Approach (Best Results):**
After Python script generates initial assessment:
1. Claude Code reviews the assessment markdown (much smaller than all PDFs)
2. Claude adds meta-analysis and strategic synthesis
3. Claude creates detailed deep-dives for HIGH priority articles
4. Claude handles integration work (Drive uploads, JIRA updates)

**Alternative (Claude Only):**
For small batches (3-5 articles) or when you want Claude's direct analysis:
- Ask Claude Code to read PDFs sequentially
- Process in small groups to avoid token limits
- Takes longer but provides Claude's native reasoning

**Script Location:** `/Users/bgerby/Desktop/generate-article-assessment.py`

**Step 4a: Generate Medium Recommendation Analysis (NEW - October 23, 2025)**

After creating the relevance assessment, generate recommendations for improving Medium's daily digest:

```bash
# Run recommendation analysis script
python3 /Users/bgerby/Desktop/generate-medium-recommendations.py \
    /Users/bgerby/Desktop/medium-articles-relevance-assessment-YYYY-MM-DD.md \
    /tmp/medium-articles-10-23.json \
    /Users/bgerby/Desktop/medium-articles-YYYY-MM-DD/

# Optional: PDF directory parameter for extracting author metadata
# If omitted, uses @username from article URLs
```

**Output Format:**
- Prints to console (no files created)
- Specific actionable recommendations grouped by type:
  - ✅ **Authors to Follow**: Based on HIGH priority articles
  - 📰 **Publications to Follow**: Publications producing HIGH priority content
  - ➕ **Topics to Add**: New Medium topics based on HIGH priority content
  - ❌ **Consider Unfollowing**: Topics producing only LOW priority articles
  - 🔕 **Articles to Mute**: Specific LOW priority articles with reasons

**Analysis Logic:**
- HIGH priority article author → Strong follow recommendation
- HIGH priority article publication → Follow recommendation
- Article content/keywords → Suggest new topics (e.g., "Model Context Protocol", "Agentic AI")
- LOW priority articles → Mute recommendations with specific reasons
- Topics producing only LOW priority → Consider unfollowing

**Example Output:**
```
======================================================================
MEDIUM RECOMMENDATION ANALYSIS
======================================================================
Date: 2025-10-23
Articles Reviewed: 15 (5 HIGH, 6 MEDIUM, 4 LOW)

RECOMMENDED ACTIONS:

✅ FOLLOW THESE AUTHORS:
  1. Follow @johnnymullaney
     Reason: Wrote 2 HIGH priority articles about Optimizely MCP development
     Articles: GAT-333, GAT-356

➕ ADD THESE TOPICS:
  1. Follow topic 'Model Context Protocol'
     Reason: 9 points from HIGH priority articles with MCP content

🔕 MUTE THESE ARTICLES (LOW PRIORITY):
  1. Mute 'The Most Efficient Fat Loss Exercise On The Planet...'
     By: @ashley-richmond
     Reason: Completely off-topic. Health/fitness content not relevant.

======================================================================
CURRENT FOLLOWING STATUS (for reference):
======================================================================
Writers: Medium Staff
Publications: The Context Layer
Topics: Artificial Intelligence, Technology, Self Improvement

💡 Tip: Visit https://medium.com/me/following/suggestions to refine
======================================================================
```

**Integration with Workflow:**
- Run after creating relevance assessment
- Review recommendations before continuing to audio generation
- Use recommendations to improve future digest quality
- No JIRA ticket created (for now) - just console output

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

## Optimizely World Blog Monitoring Workflow

### Purpose

**Fully automated** monitoring of Optimizely World blog RSS feed. Automatically creates JIRA tickets for new articles with zero manual intervention required.

### Scripts

All scripts located in `/Users/bgerby/Documents/dev/ai/scripts/`:

1. **`monitor-optimizely-blog.py`** - RSS feed monitoring with **automatic JIRA ticket creation**
2. **`scrape-optimizely-history.py`** - One-time historical backfill scraper (optional)
3. **`capture-optimizely-articles.py`** - PDF capture helper (generates Playwright manifest)

### RSS Feed

- **URL**: `https://world.optimizely.com/blogs/?feed=RSS`
- **Format**: RSS 2.0 with Dublin Core namespace
- **Update Frequency**: TTL 60 minutes (feed refreshes hourly)
- **Articles**: Returns most recent 20 blog posts

### State Tracking

- **State File**: `~/.optimizely-blog-state.json`
- **Purpose**: Track seen article GUIDs and URL-to-ticket mappings to prevent duplicate processing
- **Format**:
  ```json
  {
    "seen_guids": ["https://world.optimizely.com/..."],
    "last_check": "2025-10-23T01:34:29.456667",
    "created_tickets": {
      "article-guid": {
        "ticket_id": "GAT-XXX",
        "title": "Article Title",
        "url": "https://...",
        "created_at": "2025-10-23..."
      }
    },
    "url_to_ticket": {
      "http://johnnymullaney.com/?p=3906": "GAT-333",
      "https://world.optimizely.com/blogs/...": "GAT-350"
    }
  }
  ```

### Duplicate Detection

**Updated:** October 23, 2025

Both monitoring scripts include robust duplicate detection to prevent creating tickets for articles already processed (either automatically or manually):

**Two-Tier Detection Approach:**
1. **State File Check (Fast)**: Checks `url_to_ticket` mapping in state file
2. **JIRA Search (Fallback)**: Searches existing GAT tickets for matching URLs

**Implementation:**
- Function: `check_existing_ticket_by_url(article_url, state)`
- Returns: `(ticket_id, exists)` tuple
- Behavior: Skips ticket creation if duplicate found, logs existing ticket ID

**Verified Working:**
- Automated test: `python3 scripts/monitor-optimizely-blog.py --dry-run`
- Result: Correctly identifies all 20 RSS articles as already processed
- No false positives or duplicate tickets created

**Known Limitation:**
WordPress blogs may use different URL formats for same article:
- Full permalink: `https://johnnymullaney.com/2025/10/20/article-slug/`
- Shortlink: `http://johnnymullaney.com/?p=3906`

Current implementation uses exact URL matching. Future enhancement could add URL normalization/resolution.

### Initial Setup (One-Time)

Choose ONE of the following approaches:

#### Option A: RSS-Only Backfill (Recommended - Most Recent ~20 Articles)

```bash
cd /Users/bgerby/Documents/dev/ai

# Fetch recent articles and automatically create JIRA tickets
python3 scripts/monitor-optimizely-blog.py --backfill

# This automatically:
# - Fetches all articles from RSS feed
# - Creates JIRA tickets for each article
# - Updates state file
# - Outputs summary with ticket IDs
```

**Output:**
```
=== BACKFILL MODE: Processing all articles ===
Found 20 articles in RSS feed

=== NEW ARTICLES TO PROCESS (20) ===
 1. [2025-10-06] Automated Page Audit for Large Content Sites
 2. [2025-10-08] Image Generation with Gemini 2.5 Flash
...

=== CREATING JIRA TICKETS ===
[1/20] Automated Page Audit for Large Content Sites...
  ✓ Created GAT-350
[2/20] Image Generation with Gemini 2.5 Flash...
  ✓ Created GAT-351
...

=== SUMMARY ===
Total new articles: 20
Tickets created: 20
Skipped (duplicates): 0
Failed: 0
```

**Duplicate Detection in Action:**
If articles already exist as tickets (manually or automatically created), they're skipped:
```
=== CREATING JIRA TICKETS ===
[1/20] Automated Page Audit for Large Content Sites...
  ⊙ Already exists: GAT-350 (skipped)
[2/20] Image Generation with Gemini 2.5 Flash...
  ✓ Created GAT-351
...

=== SUMMARY ===
Total new articles: 20
Tickets created: 1
Skipped (duplicates): 19
Failed: 0
```

#### Option B: Historical Backfill (Optional - All 1163 Pages)

**Use only if you want ALL historical articles, not just recent ones.**

```bash
cd /Users/bgerby/Documents/dev/ai

# Scrape paginated HTML and automatically create tickets
python3 scripts/scrape-optimizely-history.py

# This automatically:
# - Scrapes paginated blog pages (1, 2, 3...)
# - Extracts article metadata from HTML
# - Creates JIRA tickets for new articles
# - Stops when reaching articles already seen
# - Updates state file incrementally

# Optional flags:
# --start-page N      : Start from specific page
# --max-pages N       : Limit to N pages
# --since-date YYYY-MM-DD : Only articles after date
# --dry-run           : Test without creating tickets
```

**Note:** Historical scrape may take 30+ minutes for full backfill and create 100+ tickets. Use `--dry-run` first to preview.

**Ticket Format:**
```markdown
Optimizely World Blog Article

**Article URL:** https://world.optimizely.com/...
**Published:** 2025-10-XX...
**Source:** Optimizely World Blog (world.optimizely.com)

To be reviewed for relevance to Jaxon Digital's AI agent initiatives and Optimizely platform strategy.
```

### Daily Automated Workflow (After Initial Setup)

```bash
cd /Users/bgerby/Documents/dev/ai

# Run this daily (manually or via cron)
python3 scripts/monitor-optimizely-blog.py

# This automatically:
# - Checks RSS feed for new articles
# - Compares against state file
# - Creates JIRA tickets for new articles only
# - Updates state file
# - Outputs summary

# No new articles? Script outputs:
#   "No new articles to process."
#
# New articles found? Tickets created automatically:
#   ✓ Created GAT-XXX
#   ✓ Created GAT-YYY
```

**That's it!** No manual ticket creation needed. The workflow is now:
1. Script runs (daily)
2. New articles → JIRA tickets created automatically (duplicates skipped)
3. Proceed to PDF capture/assessment for new tickets

**Duplicate Protection:**
- Automatically skips articles already processed
- Works for both automated runs and manually created tickets
- Logs existing ticket ID when duplicate found
- No false positives or wasted API calls

### Next Steps After Tickets Created

Once JIRA tickets are created (either from initial setup or daily run), proceed with:

#### Step 1: Capture Articles as PDFs

```bash
# Option A: Use Playwright MCP (recommended for varied content)
# Ask Claude Code to:
# 1. Read metadata from /tmp/optimizely-articles.json
# 2. Create output directory: /Users/bgerby/Desktop/optimizely-articles-YYYY-MM-DD/
# 3. Navigate to each article URL with Playwright
# 4. Save as PDF: 01-article-title.pdf, 02-article-title.pdf, etc.
# 5. Keep browser open between articles (session persistence)

# Option B: Use capture script (generates Playwright manifest)
python3 scripts/capture-optimizely-articles.py \
    /tmp/optimizely-articles.json \
    /Users/bgerby/Desktop/optimizely-articles-YYYY-MM-DD

# This creates playwright-manifest.json with article list for manual capture
```

**PDF Naming Convention:**
- `01-article-title-slug.pdf` (sequential numbering)
- File size varies by article length (typically 200KB-2MB)

#### Step 4: Upload PDFs to Google Drive

Use existing Medium workflow scripts:
```bash
# Upload PDFs and update JIRA tickets with Drive links
# (Reuse upload-to-drive-helper.py or manual upload via MCP)
```

#### Step 5: Create Relevance Assessment (Automated)

Use the automated Python script (same as Medium workflow):

```bash
# Set OpenAI API key
export OPENAI_API_KEY="sk-proj-..."

# Run automated assessment
python3 /Users/bgerby/Desktop/generate-article-assessment.py \
    /Users/bgerby/Desktop/optimizely-articles-YYYY-MM-DD/ \
    /tmp/optimizely-articles.json \
    /Users/bgerby/Desktop/optimizely-articles-relevance-assessment-YYYY-MM-DD.md

# This:
# - Extracts and analyzes all PDFs with GPT-4 Turbo
# - Handles large batches without token limits
# - Applies Jaxon strategic context to each article
# - Generates comprehensive markdown assessment
```

**Assessment Criteria (Built into script):**
- HIGH: Direct relevance to MCP development, AI agents, or competitive intelligence
- MEDIUM: Optimizely platform features, DevOps automation, or CMS enhancements
- LOW: Niche technical implementations or peripheral topics

**After Script Completes:**
- Optionally: Ask Claude Code to review assessment and add meta-analysis
- Upload assessment markdown to Google Drive Summaries folder

#### Step 6: Generate Audio for High-Priority Articles

Same workflow as Medium articles:
```bash
export OPENAI_API_KEY="sk-proj-..."
python3 /Users/bgerby/Desktop/generate-audio-from-assessment.py \
    /Users/bgerby/Desktop/optimizely-articles-YYYY-MM-DD \
    /Users/bgerby/Desktop/optimizely-articles-relevance-assessment-YYYY-MM-DD.md
```

#### Step 7: Update Podcast Feed

```bash
cd /Users/bgerby/Documents/dev/ai/jaxon-research-feed
python3 sync-audio-to-drive.py
python3 generate-feed.py
git add feed.rss && git commit -m "Add Optimizely World articles" && git push
```

### High-Priority Article Examples

From October 2025 backfill (GAT-350 to GAT-369), these are HIGH priority for Jaxon:

1. **GAT-356**: "Building a Discovery-First MCP for Optimizely CMS – Part 1 of 4" (Johnny Mullaney)
   - Direct competitive intelligence - another developer building Optimizely MCP
   - Technical deep-dive into MCP architecture

2. **GAT-333** (manual), **GAT-365** (duplicate, deleted): "How Optimizely MCP Learns Your CMS (and Remembers It)" (Johnny Mullaney Part 2)
   - Continuation of MCP series - caching and performance optimization
   - Note: GAT-365 was duplicate of GAT-333 (different URL formats)

3. **GAT-359**: "AI Tools, MCP, and Function Calling for Optimizely"
   - MCP integration patterns with AI tools
   - Function calling vs MCP comparison

4. **GAT-368**: "Connecting the Dots Between Research and Specification to Implementation using NotebookLM"
   - AI-assisted implementation workflow
   - Google NotebookLM for knowledge management

### Troubleshooting

**RSS feed returns 403 Forbidden:**
- Script includes User-Agent header to avoid blocking
- If blocked, try updating User-Agent in monitor-optimizely-blog.py:60

**No new articles found:**
- RSS feed only returns most recent 20 articles
- Older articles will no longer appear in incremental runs
- Check state file to verify expected articles are marked as seen

**Article capture fails:**
- Some articles may be on personal blogs with anti-scraping measures
- Use Playwright MCP with manual browser session for problematic articles
- Verify URL is accessible in normal browser first

**JIRA ticket creation fails:**
- Check JIRA API token is valid: `cat ~/.jira.d/.pass`
- Verify jira CLI is installed: `which jira`
- Check jira CLI config: `~/.config/.jira/.config.yml`
- Script has 60-second timeout per ticket
- Failed tickets are reported in summary - can retry by running script again

**Duplicate tickets created:**
- As of October 23, 2025: Duplicate detection implemented and verified working
- Skips articles already processed (checks both state file and JIRA)
- Known limitation: WordPress permalink vs shortlink variations may slip through
- If duplicates found: Delete newer ticket, URL mapping in state prevents recurrence

### Integration with Medium Workflow

The Optimizely World workflow is designed to run alongside the Medium article workflow:

**Combined Daily Process:**
1. Process Medium email digest (existing workflow)
2. Check Optimizely RSS for new articles (new workflow)
3. Capture all PDFs (both sources)
4. Upload to Google Drive (both sources)
5. Create unified relevance assessment (both sources together)
6. Generate audio for HIGH priority articles (both sources)
7. Update podcast feed (both sources)

**Shared Infrastructure:**
- Same Google Drive folder structure (separate Optimizely-* folders)
- Same audio generation scripts and OpenAI TTS
- Same podcast feed (jaxon-research-feed)
- Same JIRA project (GAT)
- Same assessment criteria and priority levels

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
