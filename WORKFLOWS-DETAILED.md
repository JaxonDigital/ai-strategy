# Detailed Article Review Workflows

This document contains step-by-step instructions for article review workflows. For quick reference, see CLAUDE.md.

## Medium Article Review Workflow

### Step 1: Extract Articles and Create JIRA Tickets

```bash
# Download email to /Users/bgerby/Desktop/MM-DD.eml
# Run extraction script
python3 /Users/bgerby/Desktop/extract-medium-articles.py \
    /Users/bgerby/Desktop/10-21.eml \
    --create-tickets \
    --output-json /tmp/medium-articles.json

# This creates:
# - JIRA tickets GAT-XXX for each article
# - JSON metadata file with article info
# - Prints list of articles to capture
```

### Step 2: Capture PDFs with Playwright

**⚠️ ABSOLUTE REQUIREMENT:** Do NOT EVER process a paywalled article without properly gaining access to the entire article by having the user log in first.

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

**PDF Naming Convention:**
- `01-article-title-slug.pdf` (sequential numbering)
- File size check: 400KB+ = success, ~115KB = paywall/failed

### Step 3: Upload PDFs to Google Drive

Ask Claude Code to run Python script:
```bash
python3 /Users/bgerby/Desktop/upload-to-drive-helper.py
```

Or manually:
- Read metadata JSON
- Upload each PDF to appropriate Drive folder (YYYY/MM-Month/DD/PDFs/)
- Get shareable link
- Update JIRA ticket description with PDF link

### Step 4: Review Articles and Create Assessment (Automated)

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

### Step 4a: Generate Medium Recommendation Analysis

After creating the relevance assessment, generate recommendations for improving Medium's daily digest:

```bash
# Run recommendation analysis script
python3 /Users/bgerby/Desktop/generate-medium-recommendations.py \
    /Users/bgerby/Desktop/medium-articles-relevance-assessment-YYYY-MM-DD.md \
    /tmp/medium-articles-10-23.json \
    /Users/bgerby/Desktop/medium-articles-YYYY-MM-DD/
```

**Output Format:**
- Prints to console (no files created)
- Specific actionable recommendations grouped by type:
  - ✅ **Authors to Follow**: Based on HIGH priority articles
  - 📰 **Publications to Follow**: Publications producing HIGH priority content
  - ➕ **Topics to Add**: New Medium topics based on HIGH priority content
  - ❌ **Consider Unfollowing**: Topics producing only LOW priority articles
  - ⚠️ **Authors to Watch**: Authors producing LOW priority content (grouped by frequency)

### Step 5: Generate Audio for High-Priority Articles

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

### Step 6: Upload Audio to Google Drive

```bash
# Run audio upload script
python3 /Users/bgerby/Desktop/upload-audio-to-drive.py

# This:
# - Uploads MP3s to Drive MP3s folder
# - Gets shareable links
# - Updates JIRA tickets with audio links
```

### Step 6a: Create Strategic Analysis and Google Docs

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

### Step 7: Final JIRA Ticket Format

After all steps complete, JIRA tickets look like:

```markdown
Medium Article Review

**Article URL:** https://medium.com/@author/article-slug
**PDF:** https://drive.google.com/file/d/FILE_ID/view?usp=sharing
**Audio:** https://drive.google.com/file/d/FILE_ID/view?usp=sharing

To be reviewed for relevance to Jaxon Digital's AI agent initiatives.
```

## Optimizely World Blog Monitoring Workflow

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

**Example Output:**
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

#### Option B: Historical Backfill (Optional - All 1163 Pages)

**Use only if you want ALL historical articles, not just recent ones.**

```bash
cd /Users/bgerby/Documents/dev/ai

# Scrape paginated HTML and automatically create tickets
python3 scripts/scrape-optimizely-history.py

# Optional flags:
# --start-page N      : Start from specific page
# --max-pages N       : Limit to N pages
# --since-date YYYY-MM-DD : Only articles after date
# --dry-run           : Test without creating tickets
```

**Note:** Historical scrape may take 30+ minutes for full backfill and create 100+ tickets. Use `--dry-run` first to preview.

### Daily Automated Workflow

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

### Next Steps After Tickets Created

Once JIRA tickets are created, proceed with:

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

#### Step 2-7: Same as Medium Workflow

Use the same process as Medium articles:
- Upload PDFs to Google Drive
- Create relevance assessment with Python script
- Generate audio for HIGH priority articles
- Upload audio to Drive
- Update podcast feed

## Podcast Feed Workflow

### Adding New Episodes

**1. Generate Audio from PDF**

```bash
export OPENAI_API_KEY="sk-proj-..."

cd /Users/bgerby/Documents/dev/ai/jaxon-research-feed
python3 generate-audio-review.py \
    "/path/to/article.pdf" \
    "GAT-333" \
    "Article Title" \
    "Executive summary with strategic context..." \
    "Author Name"

# Output: /Users/bgerby/Documents/dev/ai/audio-reviews/GAT-333.mp3
```

**2. Upload Audio to Google Drive**

```bash
cd /Users/bgerby/Documents/dev/ai/jaxon-research-feed
python3 sync-audio-to-drive.py

# This:
# - Finds new MP3 files in audio-reviews/
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

For generating audio for multiple high-priority articles:

```bash
export OPENAI_API_KEY="sk-proj-..."

python3 /Users/bgerby/Desktop/generate-audio-from-assessment.py \
    /Users/bgerby/Desktop/medium-articles-YYYY-MM-DD \
    /Users/bgerby/Desktop/medium-articles-relevance-assessment-YYYY-MM-DD.md

# Then sync to Drive and update feed:
cd /Users/bgerby/Documents/dev/ai/jaxon-research-feed
python3 sync-audio-to-drive.py
python3 generate-feed.py
git add feed.rss && git commit -m "Add [count] new episodes" && git push
```

## Google Drive Folder Structure

```
Shared Drive Root (0ALLCxnOLmj3bUk9PVA)
└── YYYY/ (e.g., 2025)
    └── MM-MonthName/ (e.g., 10-October)
        └── DD/ (e.g., 21)
            ├── PDFs/      (Article PDFs)
            ├── MP3s/      (Audio reviews)
            └── Summaries/ (Google Doc summaries)
```

**Creating Folder Structure Dynamically:**
1. Check if year folder exists (search for "YYYY" in Shared Drive root)
2. If not, create: `mcp__google-docs-drive__createFolder` with `parentFolderId=<SharedDriveId>`
3. Repeat for month (MM-MonthName) and day (DD)
4. Create type folders (PDFs/MP3s/Summaries) under day folder

**Important Limitations:**
- Documents CANNOT be created directly at Shared Drive root
- Must create folders first, then documents inside folders
- Use `parentFolderId` parameter (NOT `driveId`) for all operations

## Technical Details

### API Keys and Tokens

| Resource | Location | Usage |
|----------|----------|-------|
| OpenAI API Key | `~/.zshrc` as `OPENAI_API_KEY` | TTS audio generation, article assessment |
| Google Drive Token | `/Users/bgerby/Documents/dev/ai/mcp-googledocs-server/token.json` | Upload scripts, MCP |
| JIRA API Token | `~/.jira.d/.pass` | Creating/updating tickets |

### Article Metadata Mapping

- **PDFs**: Sequential numbering `01-article-title.pdf`
- **JIRA tickets**: GAT-321, GAT-322, etc. (assigned by JIRA)
- **Audio files**: Named by ticket `GAT-321.mp3`
- **Mapping**: Stored in JSON and assessment markdown

### File Naming Conventions

- **Medium PDFs**: `01-article-title-slug.pdf` (400KB-5MB = success, ~115KB = paywall)
- **Optimizely PDFs**: `01-article-title-slug.pdf` (200KB-2MB typically)
- **Audio**: `GAT-{ticket#}.mp3`
- **RSS Title**: `{ticket#} - {title}`

### OpenAI TTS API Settings

- **Model**: `tts-1` (standard quality)
- **Voice**: `onyx` (deep, authoritative)
- **Speed**: `1.0` (normal)
- **Max chunk size**: 4000 characters

### Podcast Feed Details

- **Subscribe URL**: `https://jaxondigital.github.io/jaxon-research-feed/feed.rss`
- **Format**: RSS 2.0 with iTunes extensions
- **Channel**: Jaxon Research Feed
- **Category**: Technology
- **Features**: Played/unplayed tracking, sequential playback, download management

## Combined Daily Process (Both Sources)

When processing both Medium and Optimizely articles together:

1. Process Medium email digest
2. Check Optimizely RSS for new articles
3. Capture all PDFs (both sources)
4. Upload to Google Drive (both sources)
5. Create unified relevance assessment (both sources together)
6. Generate audio for HIGH priority articles (both sources)
7. Update podcast feed (both sources)

**Shared Infrastructure:**
- Same Google Drive folder structure (separate source-specific folders)
- Same audio generation scripts and OpenAI TTS
- Same podcast feed (jaxon-research-feed)
- Same JIRA project (GAT)
- Same assessment criteria and priority levels
