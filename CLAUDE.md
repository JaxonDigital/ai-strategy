# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Repository Purpose

**Strategy and analysis repository** for Jaxon Digital's AI agent business initiatives. Contains strategic documents analyzing market opportunities, business models, and revenue strategies related to agentic AI and DXP platforms.

### Key Documents
- **agentic-ai-dxp-analysis.md**: Strategic analysis of agentic AI trends in DXP market
- **q4-2025-revenue-strategy.md**: Q4 2025 revenue generation strategy for Optimizely MCP services

## Business Context

### Company Profile
- **Company**: Jaxon Digital (Optimizely implementation partner)
- **Assets**: 3 built MCPs for Optimizely DXP (CMS, Commerce, Operations)
- **Focus**: Custom MCP and agent development for Optimizely CMS/Commerce/DevOps
- **Service Model**: Managed services (setup + monthly monitoring/operations)
- **Target Market**: Existing Optimizely clients and enterprises with custom systems

### Strategic Focus
1. **Custom Optimizely Agents** - Production agents (e.g., Deployment Agent for DXP)
2. **Custom MCP Development** - Client-specific system integrations ($40-100K per MCP)
3. **Client System Integration** - Legacy/proprietary systems to Optimizely
4. **Managed Agent Operations** - Ongoing monitoring/maintenance ($8-20K/month)
5. **CMS/DevOps Automation** - Deployment workflows, content ops, infrastructure

### Technology Stack
- **n8n** for workflow orchestration (MCP support on roadmap)
- **Custom MCPs** for Optimizely-specific operations
- **Proactive monitoring agents** - Event-driven architecture
- **Multi-MCP orchestration** - Complex workflows combining multiple MCPs

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
| 1. Extract | Parse emails/RSS, create JIRA tickets | `extract-medium-articles.py` or `monitor-optimizely-blog.py` |
| 2. Capture | Save articles as PDFs via Playwright | Via Claude Code with Playwright MCP |
| 3. Upload | Upload PDFs to Google Drive | `upload-to-drive-helper.py` |
| 4. Assess | Analyze relevance with GPT-4 | `generate-article-assessment.py` |
| 5. Recommend | Generate Medium follow/mute suggestions | `generate-medium-recommendations.py` |
| 6. Audio | Generate podcast episodes for HIGH priority | `generate-audio-from-assessment.py` |
| 7. Publish | Upload to Drive, update RSS feed | `sync-audio-to-drive.py`, `generate-feed.py` |

### Quick Start Commands

**Medium Articles:**
```bash
# Step 1: Extract from email
python3 /Users/bgerby/Desktop/extract-medium-articles.py /Users/bgerby/Desktop/MM-DD.eml --create-tickets --output-json /tmp/medium-articles.json

# Step 2: Capture PDFs (ask Claude Code to use Playwright)
# - Navigate with headless: false for manual login
# - Save as PDF: 01-article.pdf, 02-article.pdf, etc.
# - Keep browser open between articles
# - Files 400KB+ = success, ~115KB = paywall

# Step 4: Assess articles
export OPENAI_API_KEY="sk-proj-..."
python3 /Users/bgerby/Desktop/generate-article-assessment.py \
    /Users/bgerby/Desktop/medium-articles-YYYY-MM-DD/ \
    /tmp/medium-articles.json \
    /Users/bgerby/Desktop/medium-articles-relevance-assessment-YYYY-MM-DD.md

# Step 5: Generate recommendations (REQUIRED for every Medium batch!)
python3 scripts/generate-medium-recommendations.py \
    /Users/bgerby/Documents/dev/ai/assessments/medium-articles-relevance-assessment-YYYY-MM-DD.md \
    /tmp/medium-articles.json
# Output: outputs/medium-recommendations-YYYY-MM-DD.txt
# Analyzes which authors/publications/topics to follow/mute based on HIGH vs LOW priority

# Step 6: Generate audio for HIGH priority (FULLY AUTOMATIC!)
python3 /Users/bgerby/Desktop/generate-audio-from-assessment.py \
    /Users/bgerby/Desktop/medium-articles-YYYY-MM-DD \
    /Users/bgerby/Desktop/medium-articles-relevance-assessment-YYYY-MM-DD.md
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

**Desktop scripts** (`/Users/bgerby/Desktop/`):
- `extract-medium-articles.py` - Parse Medium emails
- `upload-to-drive-helper.py` - Upload PDFs to Drive
- `generate-article-assessment.py` - AI analysis with GPT-4
- `generate-medium-recommendations.py` - Follow/mute suggestions
- `generate-audio-from-assessment.py` - TTS for HIGH priority
- `upload-audio-to-drive.py` - Upload MP3s to Drive

**Repository scripts** (`/Users/bgerby/Documents/dev/ai/scripts/`):
- `monitor-optimizely-blog.py` - RSS monitoring + JIRA ticket creation
- `scrape-optimizely-history.py` - Historical backfill (optional)
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
- Unified feed for all article reviews (Medium + Optimizely)
- Automatic played/unplayed tracking
- Sequential playback in podcast apps
- HIGH priority articles only

### Assessment Criteria

| Priority | Criteria |
|----------|----------|
| **HIGH** | Direct relevance to MCP development, AI agents, competitive intelligence |
| **MEDIUM** | Optimizely platform features, DevOps automation, CMS enhancements |
| **LOW** | Niche technical implementations, peripheral topics |

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

**Optimizely Articles**:
1. Monitor RSS → **optionally upload PDFs with `--upload-pdfs` flag** ✨
2. Capture PDFs (if not using `--upload-pdfs`)
3. Generate assessment
4. Generate audio → **automatically uploads to Drive + updates JIRA** ✨

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
