# CHANGELOG

Historical workflow improvements and fixes for the article review system.

---

## October 24, 2025

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

---

## October 29, 2025

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

---

## October 30, 2025

### 🎯 Assessment Visibility in JIRA Tickets

**Problem Solved:** Without assessments visible in JIRA, it was unclear why LOW priority articles had no audio files.

**Solution Implemented:**
- Modified `generate-audio-from-assessment.py` to add assessments to ALL ticket descriptions (not just HIGH)
- Two-phase processing:
  1. **Phase 1**: Update JIRA descriptions with assessments for ALL articles
  2. **Phase 2**: Generate audio only for HIGH priority articles

**Key Changes:**

1. **New Function: `build_jira_description()`** (line 416-471)
   - Builds complete JIRA description with:
     - Article URL, PDF link, Audio link (if exists)
     - Full assessment (relevance, key insights, strategic implications, action items, topics)
     - Priority with visual stars (⭐⭐⭐⭐⭐ HIGH, ⭐⭐⭐ MEDIUM, ⭐ LOW)
     - Special note for LOW/MEDIUM priority: "No audio file generated (only HIGH priority articles receive audio)"

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
   - Phase 2: Generate audio only for HIGH priority articles
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
**Audio:** https://drive.google.com/... (only if HIGH)

---

# Assessment (AUTO-GENERATED)

**Priority:** LOW ⭐
**Note:** No audio file generated (only HIGH priority articles receive audio)

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

---

## November 4, 2025

### 🚀 Email Auto-Detection & OpenAI API Resilience

**Problem Solved:** Manual email path specification was slowing down daily workflow, and OpenAI TTS API timeouts needed better handling.

**Solution Implemented:**

1. **Email Auto-Detection** (lines 255-308 in both scripts)
   - Both `monitor-all-news-sources.py` and `extract-medium-articles.py` now auto-detect latest `.eml` file
   - Uses file modification time sorting: `sorted(inputs_dir.glob("*.eml"), key=lambda p: p.stat().st_mtime, reverse=True)`
   - Backward compatible - explicit paths still work
   - Clear feedback when auto-detecting: `🔍 Auto-detected Medium email: inputs/11-04.eml`

2. **OpenAI TTS API Retry Strategy**
   - Long articles (27+ chunks, ~98k characters) may require multiple retry attempts
   - API timeouts (exit status 56/92) are transient and resolve with persistence
   - Use `scripts/retry-single-audio.py` for failed articles
   - Successfully completed GAT-613 (27 chunks) and GAT-615 (4 chunks) after retries

**Key Learnings:**
- **Auto-detection eliminates manual steps**: No need to specify email path every time
- **OpenAI API is eventually consistent**: Timeouts are transient, retries succeed
- **Login workflow critical**: Always pause and wait for explicit user confirmation before PDF capture
- **PDF filename matching**: Ensure all PDFs follow expected naming convention with full article titles

**Usage:**
```bash
# No email path needed - auto-detects latest from inputs/
python3 scripts/monitor-all-news-sources.py \
    --medium-pdfs pdfs/medium-articles-YYYY-MM-DD/

# Or explicit path (backward compatible)
python3 scripts/monitor-all-news-sources.py \
    --medium-email inputs/11-04.eml \
    --medium-pdfs pdfs/medium-articles-YYYY-MM-DD/
```

**Retry Strategy for Failed Audio:**
```bash
# When audio generation times out, retry individual articles
cd /Users/bgerby/Documents/dev/ai
OPENAI_API_KEY="sk-proj-..." python3 scripts/retry-single-audio.py \
    GAT-XXX \
    "Article Title" \
    pdfs/path/to/article.pdf
```

---

## November 5, 2025

### 🔧 Permanent Fixes for Recurring Issues

**Problem Solved:** Two recurring manual steps needed permanent automation:
1. Recommendations file was only printing to stdout, never saved to file
2. PDF filename mismatches required manual renaming after capture

**Solution Implemented:**

1. **Recommendations Auto-Save** (modified `scripts/generate-medium-recommendations.py`)
   - Script now automatically saves output to `outputs/medium-recommendations-{date}.txt`
   - Uses `io.StringIO()` and `redirect_stdout()` to capture output
   - Creates outputs directory if needed
   - Prints to console AND saves to file simultaneously
   - Automatic date-based filename generation

   **Code Changes:**
   ```python
   # Capture output to both stdout and file
   output_buffer = io.StringIO()
   with redirect_stdout(output_buffer):
       generate_recommendations(assessment_path, metadata_path, pdf_dir)

   # Print to console and save to file
   output_text = output_buffer.getvalue()
   print(output_text)
   with open(output_file, 'w') as f:
       f.write(output_text)
   ```

2. **PDF Capture Preparation** (new script `scripts/prepare-pdf-capture.py`)
   - Extracts article titles from Medium email BEFORE PDF capture begins
   - Generates exact slugified filenames that match extraction script expectations
   - Prints numbered guide with precise PDF filenames to use
   - Saves article list to `/tmp/medium-pdf-capture-list.json` for reference
   - Auto-detects latest email if no path provided

   **Usage:**
   ```bash
   # Step 0: Before capturing PDFs, run this first
   python3 scripts/prepare-pdf-capture.py

   # Output example:
   # 1. We're Not Ready for What AI Agents Are Actually Doing
   #    URL: https://medium.com/@alirezarezvani
   #    📄 SAVE AS: 01-were-not-ready-for-what-ai-agents-are-actually-doing.pdf

   # Then capture PDFs using the EXACT filenames shown
   ```

**Benefits:**
- ✅ **No more missing recommendations files** - Always saved to outputs folder automatically
- ✅ **No more PDF renaming** - Use correct filenames from the start
- ✅ **Faster workflow** - Eliminates two manual steps entirely
- ✅ **Fewer errors** - Prevents filename mismatches that break extraction
- ✅ **Better organization** - All recommendations tracked in outputs/ directory

**Updated Workflow:**
```bash
# New Step 0: Get PDF filenames (before capture)
python3 scripts/prepare-pdf-capture.py

# Then capture PDFs using exact filenames from guide
# Then proceed with normal workflow - no renaming needed!

# Recommendations now auto-save
python3 scripts/generate-medium-recommendations.py \
    assessments/medium-articles-relevance-assessment-YYYY-MM-DD.md \
    /tmp/medium-articles.json
# ✅ Automatically saves to: outputs/medium-recommendations-YYYY-MM-DD.txt
```

**Key Learnings:**
- **Recurring manual steps indicate automation gaps** - If we fix the same thing multiple times, make it permanent
- **Upfront filename generation prevents downstream errors** - Extract article titles before capture, not after
- **Dual output (console + file) provides best UX** - User sees output immediately AND has file for reference

---

## November 7, 2025

### 🔧 Fixed Unified Workflow Script Paths

**Problem Discovered:** The `scripts/monitor-all-news-sources.py` script had incorrect hardcoded paths pointing to Desktop instead of the scripts directory, causing "file not found" errors.

**Solution Implemented:**
- Updated lines 49-50 in `scripts/monitor-all-news-sources.py`:
  ```python
  # ❌ BEFORE (incorrect paths)
  GENERATE_ASSESSMENT = Path.home() / "Desktop" / "generate-article-assessment.py"
  GENERATE_AUDIO = Path.home() / "Desktop" / "generate-audio-from-assessment.py"

  # ✅ AFTER (correct paths)
  GENERATE_ASSESSMENT = SCRIPTS_DIR / "generate-article-assessment.py"
  GENERATE_AUDIO = SCRIPTS_DIR / "generate-audio-from-assessment.py"
  ```

**Impact:** The unified workflow (`monitor-all-news-sources.py`) now works correctly from the repository directory.

### ⚠️ Critical: Prevent Duplicate Ticket Creation

**Problem Identified:** Running the unified workflow multiple times per day or after already processing sources separately causes duplicate JIRA tickets.

**Root Cause:**
- The unified workflow re-processes all sources (Medium, Optimizely, Anthropic) each time it runs
- If Medium email was already processed separately earlier in the day, running the unified workflow creates duplicates
- No cross-check between separate runs and unified workflow runs

**Example from November 7:**
- First run: Created GAT-649-658 (Medium articles)
- Second run (unified workflow): Created GAT-665-674 (same Medium articles - duplicates!)
- Result: Had to manually delete 11 duplicate tickets

**Prevention Strategy:**
1. **Run unified workflow ONLY ONCE per day** as the primary daily process
2. **OR** skip sources already processed when running unified workflow
3. **DO NOT** mix separate source processing + unified workflow on same day

**Daily Workflow Best Practice:**
```bash
# ✅ RECOMMENDED: Use unified workflow for ALL sources once per day
python3 scripts/monitor-all-news-sources.py \
    --medium-pdfs pdfs/medium-articles-YYYY-MM-DD/ \
    --optimizely-pdfs pdfs/optimizely-articles-YYYY-MM-DD/ \
    --anthropic-pdfs pdfs/anthropic-news-YYYY-MM-DD/

# ❌ AVOID: Mixing separate runs with unified workflow
# Don't do this:
python3 scripts/extract-medium-articles.py ...  # Separate Medium processing
python3 scripts/monitor-all-news-sources.py ... # Later unified workflow (creates dupes!)
```

**Safeguards in Place:**
- Each script maintains state files to track seen articles
- JIRA ticket creation checks for existing tickets by URL
- However, these safeguards don't prevent duplicates from multiple runs of different scripts processing the same source

**Resolution:**
- Deleted duplicate tickets GAT-663, GAT-665-674
- Kept original tickets GAT-649-658, GAT-662, GAT-664
- Documented proper daily workflow to prevent recurrence

### 📝 One-Off Article Processing

**Use Case:** Processing individual articles from sources not in the daily workflow (e.g., AWS Insights, LinkedIn, etc.)

**Process:**
1. **Create JIRA ticket** with article URL
2. **Capture PDF** using Playwright MCP
3. **Create metadata JSON** with proper structure:
   ```json
   {
     "source": "source-name",
     "total_articles": 1,
     "articles": [
       {
         "number": 1,
         "title": "Article Title",
         "url": "https://...",
         "ticket_id": "GAT-XXX"
       }
     ]
   }
   ```
4. **Generate assessment** and audio using standard scripts

**Example (November 7):**
- Processed AWS Insights article on autonomous agents
- Created GAT-675
- Generated HIGH priority assessment and audio
- Result: Successfully added to podcast feed
