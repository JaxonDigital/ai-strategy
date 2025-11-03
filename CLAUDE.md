# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## ⚠️ CRITICAL: Working Directory Policy

**NEVER work from ~/Desktop or any other directory outside this repository.**

- **Always work from**: `/Users/bgerby/Documents/dev/ai/`
- All scripts expect to run from repository root
- All relative paths assume repository root as working directory
- **PDF capture**: Save PDFs directly to `pdfs/` subdirectory (NOT Desktop)
- **Email files**: Save to `inputs/` subdirectory (NOT Desktop)
- **Assessments**: Generated in `assessments/` subdirectory

**Correct workflow:**
```bash
cd /Users/bgerby/Documents/dev/ai  # Always start here
python3 scripts/script-name.py     # Scripts run from repo root

# When capturing PDFs with Playwright:
# Save to: pdfs/medium-articles-YYYY-MM-DD/01-article.pdf
# NOT to: ~/Desktop/medium-articles-YYYY-MM-DD/01-article.pdf
```

**⚠️ DEPRECATED (November 2025):** Using Desktop for workflow files is no longer supported. All historical Desktop references in documentation have been updated to use repository paths.

## Repository Purpose

**Strategy and analysis repository** for Jaxon Digital's AI agent business initiatives. Contains strategic documents analyzing market opportunities, business models, and revenue strategies related to agentic AI and DXP platforms.

### Key Documents
- **agentic-ai-dxp-analysis.md**: Strategic analysis of agentic AI trends in DXP market
- **q4-2025-revenue-strategy.md**: Q4 2025 revenue generation strategy for Optimizely MCP services

## Business Context

⚠️ **IMPORTANT: Strategic Transformation in Progress (October 2025)**

Jaxon Digital is undergoing a 6-month transformation documented in the **Pivot project**.

**Canonical Strategy Source**: `/Users/bgerby/Documents/dev/pivot/sprint-0/STRATEGIC_CONTEXT.md`

### Strategic Transformation

**FROM (Legacy):**
- Optimizely implementation partner (billable hours)
- Managed services ($8-20K/month)
- Target: Existing Optimizely clients

**TO (New Direction):**
- **AI Operations Platform** (SaaS model, recurring revenue)
- **Product-led growth** targeting agencies first, then enterprises
- **Multi-tenant platform** with 17+ agent catalog
- **Subscription tiers**: $199-999/mo (agencies), $150K-500K ARR (enterprise)
- **Value proposition**: Autonomous agents handling 80%+ of operations

### Current Focus (Updated October 2025)
1. **Agent #19 (Early Warning System)** - TOP PRIORITY production agent
2. **Platform Architecture** - Multi-tenant SaaS foundation
3. **Agent Orchestration** - Hybrid LangGraph + n8n approach (PP-14)
4. **Agency Partnerships** - Go-to-market through Optimizely agency partners
5. **Learning Systems** - Feedback loops and continuous improvement ("Top 5% AI That Actually Works")

### Technology Stack
- **LangGraph** for complex agent orchestration (primary)
- **n8n** for simple workflows and integrations (secondary)
- **Custom MCPs** for Optimizely-specific operations
- **Multi-tenant architecture** for SaaS platform
- **Event-driven agents** with learning/feedback loops

### Meta-Pivot Strategy (Transferability)
- **20% Layer**: Optimizely-specific (DXP operations)
- **60% Layer**: Platform mechanics (multi-tenant, billing, orchestration)
- **95% Layer**: Universal patterns (agent design, monitoring, learning)

**For detailed strategic context, see**: `/Users/bgerby/Documents/dev/pivot/` (PP JIRA board)

### Legacy Business Model (Pre-October 2025)
*Note: This describes the old implementation partner model being phased out*

- **Company**: Jaxon Digital (Optimizely implementation partner)
- **Assets**: 3 built MCPs for Optimizely DXP (CMS, Commerce, Operations)
- **Focus**: Custom MCP and agent development for Optimizely CMS/Commerce/DevOps
- **Service Model**: Managed services (setup + monthly monitoring/operations)
- **Target Market**: Existing Optimizely clients and enterprises with custom systems

## Project Management

### JIRA Quick Reference

**Project**: GAT (Growth & AI Transformation)
**Board**: https://jaxondigital.atlassian.net/jira/software/c/projects/GAT/boards/228

**Essential Commands:**
```bash
export JIRA_API_TOKEN=$(cat ~/.jira.d/.pass)
jira issue list -p GAT --plain                    # List all tickets
jira issue view GAT-XXX                            # View ticket
jira issue move GAT-XXX "In Dev"                   # Update status
jira issue comment add GAT-XXX "comment" --no-input  # Add comment
```

**Critical Notes:**
- Always use `-p GAT` flag (space after `-p`!)
- Use backticks for token: `` `cat ~/.jira.d/.pass` `` not `$(cat ...)`
- Always add `--no-input` flag to avoid hangs
- For long comments, write to temp file first: `cat > /tmp/comment.txt << 'EOF'...` then `"$(cat /tmp/comment.txt)"`

## Article Review Workflows

Daily process for reviewing Medium articles and Optimizely World blog posts, tracking insights relevant to Jaxon's AI agent initiatives.

### Workflow Overview

| Step | Description | Key Script |
|------|-------------|------------|
| 1. Capture | Save articles as PDFs via Playwright | Via Claude Code with Playwright MCP |
| 2. Extract | Parse emails/RSS, create JIRA tickets **WITH PDF LINKS** | `extract-medium-articles.py` or `monitor-optimizely-blog.py` |
| 3. Assess | Analyze relevance with GPT-4 | `generate-article-assessment.py` |
| 4. Recommend | Generate Medium follow/mute suggestions | `generate-medium-recommendations.py` |
| 5. Audio | Generate podcast episodes for HIGH priority | `generate-audio-from-assessment.py` |
| 6. Publish | Upload to Drive, update RSS feed | Automatic in audio generation |

**⚠️ IMPORTANT CHANGE (October 30, 2025):** PDF links are now **MANDATORY** in JIRA tickets. Always capture PDFs BEFORE creating tickets.

### 🆕 Combined Workflow (Recommended - November 2025)

**NEW: Process all sources with one command!**

```bash
# Daily workflow - ALL THREE SOURCES in one go
python3 scripts/monitor-all-news-sources.py \
    --medium-email inputs/MM-DD.eml \
    --medium-pdfs pdfs/medium-articles-YYYY-MM-DD/ \
    --optimizely-pdfs pdfs/optimizely-articles-YYYY-MM-DD/ \
    --anthropic-pdfs pdfs/anthropic-news-YYYY-MM-DD/

# ✨ This automatically:
#   1. Extracts Medium articles from email
#   2. Checks Optimizely RSS for new articles
#   3. Processes Anthropic news (if scraped JSON provided)
#   4. Uploads ALL PDFs to Google Drive
#   5. Creates JIRA tickets with PDF links
#   6. Generates UNIFIED assessment for all sources
#   7. Generates audio for HIGH priority articles
#   8. Updates JIRA with assessments and audio links
#   9. Publishes RSS podcast feed
```

**Prerequisites:**
1. **Capture PDFs first** (via Claude Code + Playwright MCP):
   - Medium: Save paywall articles (login required)
   - Optimizely: Save from world.optimizely.com/blogs
   - Anthropic: Save from anthropic.com/news (no RSS, requires scraping)

2. **Anthropic scraping** (separate step, no RSS available):
   ```bash
   # Ask Claude Code to scrape Anthropic news:
   # "Navigate to https://www.anthropic.com/news and extract article data to JSON"
   # Output: /tmp/anthropic-news-YYYY-MM-DD.json

   # Then process with:
   python3 scripts/monitor-all-news-sources.py \
       --anthropic-scraped-json /tmp/anthropic-news-YYYY-MM-DD.json \
       --anthropic-pdfs pdfs/anthropic-news-YYYY-MM-DD/
   ```

**Benefits:**
- ✅ Single command for entire workflow
- ✅ Unified assessment across all sources
- ✅ No manual JIRA/Drive updates needed
- ✅ Consistent priority scoring
- ✅ Automatic podcast feed updates

### Quick Start Commands (Legacy - Individual Sources)

**Medium Articles:**
```bash
# Step 1: Capture PDFs (ask Claude Code to use Playwright)
# - Navigate with headless: false for manual login
# - Save as PDF: 01-article.pdf, 02-article.pdf, etc.
# - Keep browser open between articles
# - Files 400KB+ = success, ~115KB = paywall
# - Save to: pdfs/medium-articles-YYYY-MM-DD/

# Step 2: Extract from email AND upload PDFs (combined step)
# ⚠️ NOTE: Email files stored in: inputs/MM-DD.eml
python3 scripts/extract-medium-articles.py \
    inputs/MM-DD.eml \
    --create-tickets \
    --upload-to-drive pdfs/medium-articles-YYYY-MM-DD/ \
    --output-json /tmp/medium-articles.json

# ✓ This automatically:
#   - Uploads PDFs to Google Drive
#   - Creates JIRA tickets WITH PDF links
#   - Generates metadata JSON

# Step 4: Assess articles
export OPENAI_API_KEY="sk-proj-..."
python3 scripts/generate-article-assessment.py \
    pdfs/medium-articles-YYYY-MM-DD/ \
    /tmp/medium-articles.json \
    assessments/medium-articles-relevance-assessment-YYYY-MM-DD.md

# Step 5: Generate recommendations (REQUIRED for every Medium batch!)
python3 scripts/generate-medium-recommendations.py \
    assessments/medium-articles-relevance-assessment-YYYY-MM-DD.md \
    /tmp/medium-articles.json
# Output: outputs/medium-recommendations-YYYY-MM-DD.txt
# Analyzes which authors/publications/topics to follow/mute based on HIGH vs LOW priority

# Step 6: Generate audio for HIGH priority (FULLY AUTOMATIC!)
python3 scripts/generate-audio-from-assessment.py \
    pdfs/medium-articles-YYYY-MM-DD \
    assessments/medium-articles-relevance-assessment-YYYY-MM-DD.md
# ⚡ FULLY AUTOMATED (October 24, 2025):
#   - Crops footer content (Topics, Author, Recommendations)
#   - Uploads MP3s to Google Drive
#   - Updates JIRA tickets with audio links
#   - Regenerates RSS feed
#   - Commits and pushes to GitHub Pages
# NO MANUAL STEPS REQUIRED!
```

**Optimizely World Articles:**
```bash
# Step 1: Monitor RSS feed (run daily)
cd /Users/bgerby/Documents/dev/ai
python3 scripts/monitor-optimizely-blog.py

# Initial backfill (one-time):
python3 scripts/monitor-optimizely-blog.py --backfill

# Step 1+3 Combined: Monitor + Upload PDFs (automatic)
python3 scripts/monitor-optimizely-blog.py --upload-pdfs /path/to/pdf/directory
# Automatically uploads PDFs and updates JIRA tickets with Drive links

# Step 2-7: Same as Medium workflow
```

**Publish Podcast Feed:**
```bash
# ⚡ NO LONGER NEEDED - RSS feed is auto-updated by generate-audio-from-assessment.py!
# Only use this if you need to manually regenerate the feed:
cd /Users/bgerby/Documents/dev/ai/jaxon-research-feed
python3 sync-audio-to-drive.py  # Only if manually uploading audio
python3 generate-feed.py
git add feed.rss && git commit -m "Add episodes" && git push
```

### Critical: Medium Paywall Bypass

**⚠️ REQUIREMENT:** Never process paywalled articles without full access. Always have user log in first.

**Key Principles:**
- Keep browser session open across all articles (don't close between articles)
- Use `headless: false` for manual login
- Login persists as long as browser stays open
- Verify file sizes: 400KB+ = success, ~115KB = paywall

**Process:**
1. Open browser visible (`headless: false`) on first article
2. User logs in manually
3. Save first article as PDF
4. Navigate to next article (browser still open)
5. Repeat steps 3-4 for all articles
6. Close browser only when all articles captured

### Google Drive Integration

**Shared Drive Structure:**
```
Root (0ALLCxnOLmj3bUk9PVA)
└── YYYY/
    └── MM-MonthName/
        └── DD/
            ├── PDFs/
            ├── MP3s/
            └── Summaries/
```

**MCP Server:** google-docs-mcp-shared
- **Location**: `/Users/bgerby/Documents/dev/ai/mcp-googledocs-server`
- **Token**: `token.json` in server directory (auto-refreshes)

**Important:**
- Cannot create documents at Shared Drive root
- Must create folders first, then documents inside
- Use `parentFolderId` parameter (NOT `driveId`)

### Scripts Location

**All scripts are now in the repository** (`/Users/bgerby/Documents/dev/ai/scripts/`):
- `monitor-all-news-sources.py` - **🆕 UNIFIED processor for all sources (RECOMMENDED)**
- `extract-medium-articles.py` - Parse Medium emails
- `generate-article-assessment.py` - AI analysis with GPT-4
- `generate-medium-recommendations.py` - Follow/mute suggestions
- `generate-audio-from-assessment.py` - TTS for HIGH priority
- `monitor-optimizely-blog.py` - RSS monitoring + JIRA ticket creation
- `anthropic-scraper.py` - **🆕 Anthropic news processing (no RSS, requires scraped JSON)**
- `upload-to-drive-helper.py` - Upload PDFs to Drive (legacy)
- `capture-optimizely-articles.py` - PDF capture helper

**Podcast feed scripts** (`/Users/bgerby/Documents/dev/ai/jaxon-research-feed/`):
- `generate-audio-review.py` - Single article to audio
- `sync-audio-to-drive.py` - Upload MP3s to Drive
- `generate-feed.py` - Create RSS feed

### API Keys and Tokens

| Resource | Location | Usage |
|----------|----------|-------|
| OpenAI API | `~/.zshrc` as `OPENAI_API_KEY` | TTS, article assessment |
| Google Drive | `/Users/bgerby/Documents/dev/ai/mcp-googledocs-server/token.json` | Upload scripts, MCP |
| JIRA API | `~/.jira.d/.pass` | Ticket operations |

### File Naming Conventions

- **PDFs**: `01-article-title.pdf` (sequential)
- **Audio**: `GAT-{ticket}.mp3` (e.g., `GAT-321.mp3`)
- **Assessment**: `{source}-articles-relevance-assessment-YYYY-MM-DD.md`

### Podcast Feed

**Subscribe URL**: `https://jaxondigital.github.io/jaxon-research-feed/feed.rss`

**Repository**: `/Users/bgerby/Documents/dev/ai/jaxon-research-feed/`
**GitHub**: https://github.com/JaxonDigital/jaxon-research-feed

**Features:**
- Unified feed for all article reviews (Medium + Optimizely + Anthropic)
- Automatic played/unplayed tracking
- Sequential playback in podcast apps
- HIGH priority articles only

**Sources Monitored:**
1. **Medium** - Daily digest email (requires manual subscription)
2. **Optimizely World Blog** - RSS feed (automated monitoring)
3. **Anthropic News** - Web scraping (no RSS available)

### Assessment Criteria (Updated for SaaS Pivot - October 2025)

**Note**: Article assessment now uses strategic context from Pivot project automatically.
Scripts load from: `/Users/bgerby/Documents/dev/pivot/sprint-0/STRATEGIC_CONTEXT.md`

| Priority | Criteria (SaaS Platform Focus) |
|----------|--------------------------------|
| **HIGH** | SaaS business models & pricing, multi-tenant architecture, agent orchestration (LangGraph/AutoGen), product-led growth, agency partnerships, learning systems, marketplace strategies, Optimizely DXP technical content |
| **MEDIUM** | DevOps automation patterns, CMS/Commerce features, cloud optimization, monitoring/observability, customer onboarding, PLG tactics, competitive analysis |
| **LOW** | Generic business advice, unrelated technical topics, consumer product strategies, non-AI automation approaches |

**Strategic Questions for Assessment:**
1. Does this help us build better agents?
2. Does this help us scale the platform?
3. Does this help us acquire/retain customers?
4. Does this apply to the meta-pivot (transferable to other verticals)?
5. Does this help us partner with Optimizely or agencies?

**Context Sync**: The `generate-article-assessment.py` script automatically imports the latest strategic context from the Pivot project with graceful fallback to legacy context if unavailable.

### Why Python Scripts vs Claude Code

**Use Python scripts for:**
- Large batches (20+ articles) - avoids token limits
- Consistent analysis across all articles
- Parallel processing with rate limiting
- Automated workflows (cron jobs)

**Use Claude Code for:**
- Small batches (3-5 articles)
- Meta-analysis and strategic synthesis
- Complex reasoning about article implications
- Integration work (Drive uploads, JIRA updates)

**Best approach:** Python for initial processing, Claude for strategic analysis and synthesis.

## Feedback Loop System (Added October 30, 2025)

Systematic feedback capture and analysis to enable continuous improvement and autonomous agent operation.

### Overview

The feedback loop tracks assessment accuracy, audio quality, and action outcomes to identify patterns and improve the article review process over time.

**Key Components:**
- **Feedback Log**: `/Users/bgerby/Documents/dev/ai/feedback/article-feedback-log.jsonl`
- **Recording Tool**: `scripts/record-feedback.py`
- **Analysis Tool**: `scripts/analyze-feedback.py`
- **Reports**: `feedback/reports/`

### Recording Feedback

**Priority Corrections** (validate HIGH priority articles):
```bash
# Confirm correct priority
python3 scripts/record-feedback.py GAT-482 correct "Direct MCP relevance confirmed"

# Article over-rated (should be lower)
python3 scripts/record-feedback.py GAT-484 too-high "LocalStorage too niche for current priorities"

# Article under-rated (should be higher)
python3 scripts/record-feedback.py GAT-485 too-low "Actually very relevant to SaaS platform strategy"
```

**Quality Ratings** (audio and content value):
```bash
# Record listening experience
python3 scripts/record-feedback.py GAT-482 quality \
    --audio-rating 5 \
    --content-rating 5 \
    --listened \
    --completion 1.0
```

**Action Outcomes** (track completed items):
```bash
# Record action items completed
python3 scripts/record-feedback.py GAT-482 action \
    --completed "Research LangGraph" \
    --completed "Review subagent patterns"
```

### Analyzing Feedback

**Generate Reports:**
```bash
# Weekly summary (default)
python3 scripts/analyze-feedback.py --period week

# Monthly analysis
python3 scripts/analyze-feedback.py --period month

# Save to file
python3 scripts/analyze-feedback.py --period week \
    --output feedback/reports/2025-10-30-weekly-summary.md
```

**Report Includes:**
- Priority accuracy metrics (target: 90%+)
- Audio quality and content value ratings
- Action item completion tracking
- Systematic pattern detection
- Improvement recommendations

### Daily Validation Loop (5-10 minutes)

**Recommended workflow after Step 4 (Assessment Generated):**

1. Open assessment markdown file
2. Review each HIGH priority article summary
3. For obvious mis-classifications, record feedback:
   ```bash
   python3 scripts/record-feedback.py GAT-XXX too-high "Reason"
   ```
4. Spot-check 2-3 MEDIUM/LOW articles for surprises

**Target:** Validate 100% of HIGH priority, 20% sample of MEDIUM/LOW

### Weekly Review (10-15 minutes)

1. Generate weekly feedback report
2. Review Medium recommendations (`outputs/medium-recommendations-YYYY-MM-DD.txt`)
3. Implement follow/mute actions based on patterns
4. Track recommendation effectiveness

### JIRA Integration

Feedback recording automatically adds labels to tickets:
- `priority:correct` - AI prediction validated
- `priority:too-high` - Article over-rated
- `priority:too-low` - Article under-rated

Query via JIRA:
```bash
# Find all misclassifications
jira issue list -p GAT -l "priority:too-high OR priority:too-low" --plain

# Find validated HIGH priority articles
jira issue list -p GAT -l "priority:correct" --plain
```

### Path to Autonomous Operation

**Phase 1 (Weeks 1-4):** Collect baseline feedback (100+ validations)
**Phase 2 (Weeks 5-8):** Identify patterns, build confidence scoring
**Phase 3 (Weeks 9-12):** Implement auto-corrections for high-confidence patterns
**Phase 4 (Weeks 13-16):** Reduce human validation to 2-3 min/day (exception-only)

**Success Metrics:**
- Priority accuracy: 90%+ agreement with human validation
- Validation time: < 10 minutes/day
- Human intervention: < 5% of articles need manual review

### Fixing Missing PDF Links

If you discover tickets without PDF links (created before October 30, 2025), use the helper script:

```bash
# Audit only (see what's missing)
python3 scripts/fix-missing-pdf-links.py --dry-run

# Fix all missing PDF links
python3 scripts/fix-missing-pdf-links.py

# Fix specific date range
python3 scripts/fix-missing-pdf-links.py --start-date 2025-10-25 --end-date 2025-10-29
```

**What it does:**
1. Finds JIRA tickets missing PDF links
2. Searches for corresponding PDFs in pdfs/ directory
3. Uploads PDFs to Google Drive
4. Updates JIRA ticket descriptions with PDF links

## Optimizely World Monitoring

**RSS Feed**: `https://world.optimizely.com/blogs/?feed=RSS` (returns 20 most recent)
**State File**: `~/.optimizely-blog-state.json` (tracks seen articles, prevents duplicates)

**Daily workflow:**
```bash
cd /Users/bgerby/Documents/dev/ai
python3 scripts/monitor-optimizely-blog.py
# Automatically creates JIRA tickets for new articles
# Skips duplicates using state file + JIRA search
```

**Duplicate Detection:**
- Two-tier: State file check + JIRA search fallback
- Verified working as of October 23, 2025
- Known limitation: WordPress permalink variations (full URL vs shortlink)

**Initial setup:**
```bash
# Option A: Recent articles only (recommended)
python3 scripts/monitor-optimizely-blog.py --backfill

# Option B: Full historical backfill (optional, 1163 pages, 100+ tickets)
python3 scripts/scrape-optimizely-history.py --dry-run
```

## Anthropic News Monitoring (🆕 November 2025)

**Source**: `https://www.anthropic.com/news` (no RSS feed available, requires web scraping)
**State File**: `~/.anthropic-news-state.json` (tracks seen articles, prevents duplicates)

**Why Monitor Anthropic:**
- Major Claude capability announcements (directly impacts MCP development)
- API updates and new features
- AI safety research and best practices
- Strategic positioning insights

**Workflow:**

1. **Scrape articles** (via Claude Code + Playwright):
   ```bash
   # Ask Claude Code:
   # "Navigate to https://www.anthropic.com/news and extract all article data to JSON"
   # Save output: /tmp/anthropic-news-YYYY-MM-DD.json

   # Expected JSON structure:
   # {
   #   "articles": [
   #     {
   #       "title": "Claude Sonnet 4.5 Announcement",
   #       "url": "https://www.anthropic.com/news/...",
   #       "date": "2025-09-29",
   #       "category": "Product"
   #     }
   #   ]
   # }
   ```

2. **Capture PDFs** (via Claude Code + Playwright):
   ```bash
   # For each article URL, save as PDF:
   # pdfs/anthropic-news-YYYY-MM-DD/01-article-title.pdf
   ```

3. **Process articles and create tickets**:
   ```bash
   python3 scripts/anthropic-scraper.py \
       --input-json /tmp/anthropic-news-YYYY-MM-DD.json \
       --output-json /tmp/anthropic-processed.json

   # ✅ This creates JIRA tickets with "Anthropic" label
   # ✅ Tracks seen articles in state file
   # ✅ Skips duplicates automatically
   ```

4. **Or use combined workflow** (recommended):
   ```bash
   python3 scripts/monitor-all-news-sources.py \
       --anthropic-scraped-json /tmp/anthropic-news-YYYY-MM-DD.json \
       --anthropic-pdfs pdfs/anthropic-news-YYYY-MM-DD/
   ```

**Limitations:**
- **No RSS feed** - Requires manual scraping trigger
- **Lower frequency** - Anthropic publishes less often than Medium/Optimizely
- **Manual first step** - Must use Claude Code to scrape before processing

**Priority Weighting:**
- Anthropic news typically receives **HIGH** priority automatically
- Strategic importance to MCP and agent development
- Impacts product roadmap and competitive positioning

## Workflow Improvements (October 24, 2025)

### 🎉 New Automated Features

**1. Improved Audio Quality**
- Footer content (Topics, Author bio, Recommendations) now automatically cropped from TTS
- Reduces audio length by ~2-3 minutes per article
- Improved in `/Users/bgerby/Documents/dev/ai/scripts/generate-audio-from-assessment.py`

**2. Automatic Google Drive Upload & JIRA Updates**
- `generate-audio-from-assessment.py` now automatically:
  - Uploads MP3s to Google Drive
  - Updates JIRA tickets with audio links
  - Preserves existing PDF links
- No manual `upload-audio-to-drive.py` step needed

**3. Optimizely Blog PDF Upload**
- New `--upload-pdfs` flag for `monitor-optimizely-blog.py`
- Automatically uploads PDFs and updates tickets after creation
- Usage: `python3 scripts/monitor-optimizely-blog.py --upload-pdfs /path/to/pdfs/`

**4. Improved Error Handling**
- `upload-audio-to-drive.py` now handles missing PDF links gracefully
- Works with both Medium and Optimizely articles
- Automatically detects article source

### Updated Workflow

**Medium Articles** (now 6 steps instead of 7):
1. Extract articles + create JIRA tickets
2. Capture PDFs with Playwright
3. Upload PDFs to Drive (manual or with extract script)
4. Generate assessment
5. **Generate recommendations** → outputs to `outputs/medium-recommendations-YYYY-MM-DD.txt` ✨
6. Generate audio → **automatically uploads to Drive + updates JIRA** ✨

## Workflow Improvements (October 29, 2025)

### 🔧 Podcast Feed Reliability

**Issue Fixed:** Missing Google Drive URLs for historical episodes
- 7 episodes (GAT-466 to GAT-471, GAT-11) were using non-existent GitHub Pages URLs
- Root cause: drive-urls.json missing entries for audio files generated before automation was complete

**Solution Implemented:**
1. Query JIRA tickets to extract Google Drive audio URLs
2. Update drive-urls.json with missing entries (now 80 total)
3. Regenerate RSS feed with corrected URLs
4. Push to GitHub Pages

**Files Updated:**
- `/Users/bgerby/Documents/dev/ai/audio-reviews/drive-urls.json` - Added 7 missing entries
- `/Users/bgerby/Documents/dev/ai/jaxon-research-feed/feed.rss` - Regenerated with correct URLs

**Verification:**
- All 80 episodes now use Google Drive download URLs
- No episodes pointing to GitHub Pages
- Feed validated with comprehensive audit script

**Maintenance Note:**
- drive-urls.json is the source of truth for audio file URLs
- RSS feed generator checks drive-urls.json first before defaulting to GitHub Pages
- Always regenerate RSS feed after updating drive-urls.json

**Optimizely Articles**:
1. Monitor RSS → **optionally upload PDFs with `--upload-pdfs` flag** ✨
2. Capture PDFs (if not using `--upload-pdfs`)
3. Generate assessment
4. Generate audio → **automatically uploads to Drive + updates JIRA** ✨

## Workflow Improvements (October 30, 2025)

### 🎯 Assessment Visibility in JIRA Tickets

**Problem Solved:** Without assessments visible in JIRA, it was unclear why LOW priority articles had no audio files.

**Solution Implemented:**
- Modified `generate-audio-from-assessment.py` to add assessments to ALL ticket descriptions (not just HIGH/MEDIUM)
- Two-phase processing:
  1. **Phase 1**: Update JIRA descriptions with assessments for ALL articles
  2. **Phase 2**: Generate audio only for HIGH/MEDIUM priority articles

**Key Changes:**

1. **New Function: `build_jira_description()`** (line 416-471)
   - Builds complete JIRA description with:
     - Article URL, PDF link, Audio link (if exists)
     - Full assessment (relevance, key insights, strategic implications, action items, topics)
     - Priority with visual stars (⭐⭐⭐⭐⭐ HIGH, ⭐⭐⭐ MEDIUM, ⭐ LOW)
     - Special note for LOW priority: "No audio file generated (only HIGH/MEDIUM priority articles receive audio)"

2. **New Function: `update_jira_with_assessment()`** (line 468-525)
   - Replaces old `update_jira_with_audio_link()` function
   - Fetches current ticket to preserve PDF link
   - Updates description using `-b` flag directly (avoids JIRA CLI comment hang bug)
   - Works for both assessment-only (Phase 1) and assessment+audio (Phase 2)

3. **Process ALL Articles** (line 150-207)
   - Removed priority filter that skipped LOW priority articles
   - Extracts complete assessment data for all articles
   - Stores: relevance, key insights, strategic implications, action items, topics, author, published date

4. **Two-Phase Main Loop** (line 665-693)
   - Phase 1: Update ALL tickets with assessments
   - Phase 2: Generate audio only for HIGH/MEDIUM articles
   - When audio uploaded, re-update JIRA with audio link

**Benefits:**
- ✅ All articles have visible assessments in JIRA (including LOW priority)
- ✅ Clear explanation of why no audio exists for LOW priority
- ✅ No JIRA CLI comment hangs (using descriptions instead)
- ✅ Consistent format across all tickets
- ✅ Easier to understand article relevance at a glance

**JIRA CLI Best Practices (Updated):**
- **Avoid comments**: Comment command has stdin bug causing hangs (jira-cli v1.7.0 issues #641, #727)
- **Use descriptions**: Always put assessments in ticket descriptions using `-b` flag
- **Pattern**: `jira issue edit TICKET -b "description text" --no-input`
- **No temp files needed**: Pass description directly as string parameter

**Example Ticket Format:**
```
Medium Article Review

**Article URL:** https://...
**PDF:** https://drive.google.com/...
**Audio:** https://drive.google.com/... (only if HIGH/MEDIUM)

---

# Assessment (AUTO-GENERATED)

**Priority:** LOW ⭐
**Note:** No audio file generated (only HIGH/MEDIUM priority articles receive audio)

**Relevance Summary:**
[Assessment content...]

**Key Insights:**
- [Bullet points...]

**Strategic Implications:**
- [Bullet points...]

**Action Items:**
- [Bullet points...]

**Topics:** topic1, topic2, topic3
```

## Combined Daily Process

When processing both sources together:
1. Process Medium email digest
2. Check Optimizely RSS for new articles (with `--upload-pdfs` if PDFs ready)
3. Capture all PDFs (both sources, if not using automation)
4. Upload to Google Drive (now optional - audio generation does it automatically)
5. Create unified assessment (both sources together)
6. Generate audio for HIGH priority → **automatic upload + JIRA update** ✨
7. Update podcast feed (both sources)

## Detailed Documentation

For step-by-step guides, see: **WORKFLOWS-DETAILED.md**
For troubleshooting help, see: **TROUBLESHOOTING.md**

### When to Consult Detailed Docs

**Use WORKFLOWS-DETAILED.md for:**
- First-time setup instructions
- Complete step-by-step guides
- Detailed explanations of each script
- Example outputs and verification steps
- Google Drive folder structure details

**Use TROUBLESHOOTING.md for:**
- Error messages and solutions
- Common failure scenarios
- Verification commands
- Environment variable issues
- State file corruption recovery
- API key problems

## Document Updates

When updating strategy documents:
- Maintain executive summary → detailed analysis structure
- Keep financial projections and pricing frameworks current
- Update based on actual client interactions and market feedback
- Preserve specific examples and case studies
- Document learnings and adjustments to strategy

## Repository Type

This is a **documentation/analysis repository**, not a code repository. No build commands, tests, or deployment processes. Work involves strategic analysis, business planning, and documentation refinement.
