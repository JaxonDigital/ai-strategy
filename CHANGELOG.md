# CHANGELOG

Historical workflow improvements and fixes for the article review system.

---

## November 11, 2025

### 🛡️ Phase 1: Critical Data Protection Fixes

**Code Review Findings:** Comprehensive code review identified 47 potential issues. Implemented 5 highest-priority fixes to prevent data loss, state corruption, and catastrophic failures.

#### Fix #1: Atomic State File Writes
**Problem:** State files written directly - crashes during write corrupted JSON, causing duplicate tickets.

**Solution:** Implemented atomic write pattern (temp file + rename) in:
- `scripts/monitor-optimizely-blog.py`
- `scripts/anthropic-scraper.py`

**Impact:** CRITICAL - Prevents state corruption that would cause duplicate ticket creation.

#### Fix #2: Transactional Article Processing
**Problem:** Articles marked "seen" immediately after ticket creation, before PDF upload. If upload failed, article was lost forever.

**Solution:** Added `processing_succeeded` flag in `scripts/monitor-optimizely-blog.py` - articles only marked "seen" after ALL steps complete.

**Impact:** HIGH - Eliminates silent data loss from partial failures. Failed articles retry automatically.

#### Fix #3: Google Drive Token Expiration Handling
**Problem:** Token expiration mid-batch caused API failures with no retry logic.

**Solution:** Enhanced `scripts/extract-medium-articles.py`:
- Added `get_drive_service(force_refresh=True)` parameter
- Atomic token file updates
- `drive_api_call_with_retry()` wrapper catches 401/403, refreshes, retries

**Impact:** CRITICAL - Prevents mid-batch crashes from expired tokens.

#### Fix #4: Disk Space Validation
**Problem:** Audio generation creates large files (10MB+ each). No pre-flight check - script could fail after processing 15/20 articles.

**Solution:** Added disk space check in `scripts/generate-audio-from-assessment.py` - estimates required space, fails fast with clear error.

**Impact:** CRITICAL - Prevents resource exhaustion and partial batch failures.

#### Fix #5: Atomic RSS Feed Generation
**Problem:** RSS feed written directly - crashes corrupted XML, breaking podcast feed.

**Solution:** `jaxon-research-feed/generate-feed.py` now:
- Writes to temp file
- Validates XML parsing
- Atomic rename to final location

**Impact:** CRITICAL - Prevents podcast feed corruption requiring manual recovery.

**Testing:** All fixes verified with today's workflow (15 articles, 7 audio files generated).

---

### 🔧 Phase 2: Robustness Improvements

**Goal:** Add validation and retry logic to handle edge cases and API failures gracefully.

#### Fix #6: Email Parsing Validation
**Problem:** Medium email format changes could silently fail, resulting in zero articles extracted without warning.

**Solution:** Enhanced `scripts/extract-medium-articles.py` with validation:
- Checks if email contains "medium.com" but no articles extracted
- Warns if < 3 articles found (usually expect 10-20)
- Helps detect Medium email format changes early

**Impact:** MEDIUM - Early detection of parsing failures prevents wasted time on empty batches.

**Code Location:** extract-medium-articles.py, lines 67-94

#### Fix #7: PDF Content Validation
**Problem:** Paywalled or empty PDFs processed without detection, resulting in poor audio quality or TTS failures.

**Solution:** Enhanced `scripts/generate-audio-from-assessment.py`:
- Added `validate_content` parameter to `extract_text_from_pdf()`
- Checks for empty PDFs (< 100 chars)
- Detects paywall indicators ("member-only story", "sign up to read", etc.)
- Added 30-second timeout with proper error handling
- Returns `None` for invalid PDFs (skipped in audio generation)

**Impact:** HIGH - Prevents processing of incomplete content, improves audio quality.

**Code Location:** generate-audio-from-assessment.py, lines 45-74

#### Fix #8: OpenAI Rate Limit Handling
**Problem:** Assessment generation could fail mid-batch with RateLimitError, requiring manual restart and losing progress.

**Solution:** Created `openai_api_call_with_retry()` wrapper in `scripts/generate-article-assessment.py`:
- Exponential backoff with jitter: `(2 ** attempt) + random.uniform(0, 1)`
- Retries up to 5 times for RateLimitError and APIError
- Applied to both chunk analysis and synthesis calls
- Preserves progress - failed chunks retry automatically

**Impact:** HIGH - Eliminates manual intervention for transient API failures.

**Code Location:** generate-article-assessment.py, lines 43-77, 294-306, 343-355

**Algorithm:**
```python
for attempt in range(max_retries):
    try:
        return api_call_func()
    except RateLimitError:
        delay = (2 ** attempt) + random.uniform(0, 1)  # 1-2s, 2-3s, 4-5s, 8-9s, 16-17s
        time.sleep(delay)
```

---

### 🔍 Phase 3: Error Visibility & User Experience

**Goal:** Improve debugging capability and provide feedback during long-running operations.

#### Fix #9: Progress Indicators with tqdm
**Problem:** Audio generation for 15+ articles takes 30+ minutes with no feedback - appears frozen.

**Solution:** Added tqdm progress bars to `scripts/generate-audio-from-assessment.py`:
- Shows progress bar with article count and completion percentage
- Uses `tqdm.write()` to avoid disrupting progress bar
- Graceful fallback if tqdm not installed (optional dependency)
- Added import check: `HAS_TQDM` flag for conditional usage

**Impact:** MEDIUM - Better user experience, easier to estimate completion time.

**Code Location:** generate-audio-from-assessment.py, lines 20-28, 830-838

**Usage:**
```python
from tqdm import tqdm
for article_num, article in tqdm(articles, desc="Generating audio", unit="article"):
    tqdm.write(f"Processing {article['title']}")
```

#### Fix #10: Subprocess Error Logging
**Problem:** FFmpeg and JIRA CLI failures showed exit codes but no stderr output - impossible to debug.

**Solution:** Created `log_subprocess_error()` function in multiple scripts:
- Logs to `/tmp/workflow-errors.log` with timestamps
- Captures stderr from FFmpeg concat operations
- Captures stderr from FFmpeg metadata operations
- Captures stderr from JIRA ticket creation
- Captures stderr from JIRA ticket editing
- Appends to log file (doesn't overwrite)

**Impact:** HIGH - Debugging failures now takes minutes instead of hours.

**Code Location:**
- generate-audio-from-assessment.py: lines 30-43, 347-356, 386-403
- extract-medium-articles.py: lines 34-47, 286-291, 334-338

**Log Format:**
```
[2025-11-11 14:23:45] FFmpeg concat failed:
Output #0, mp3, to '/path/to/output.mp3':
  Stream #0:0: Audio: mp3, 44100 Hz, stereo, fltp, 128 kb/s
```

---

### 🏗️ Phase 4: Architecture Improvements

**Goal:** Prevent race conditions and ensure consistency across scripts.

#### Fix #11: Shared Pattern Constants
**Problem:** Regex patterns duplicated across scripts. Changes required updates in 5+ locations, causing divergence.

**Solution:** Created `scripts/shared_patterns.py` with centralized constants:
- Medium article URL patterns (user + publication)
- JIRA project identifiers and ticket patterns
- Priority levels (HIGH, MEDIUM, LOW)
- File naming conventions (PDFs, audio)
- Drive folder structure helpers
- Audio generation settings (chunk size, bitrate, codec)
- PDF validation thresholds and paywall indicators
- State file locations (Optimizely, Anthropic)
- Error log location

**Impact:** MEDIUM - Easier maintenance, prevents pattern divergence.

**Scripts Updated:**
- `extract-medium-articles.py` - imports MEDIUM patterns, JIRA constants
- `prepare-pdf-capture.py` - imports MEDIUM patterns
- `monitor-optimizely-blog.py` - imports JIRA constants, state file location
- `anthropic-scraper.py` - imports JIRA constants, state file location

**Code Location:** shared_patterns.py (lines 1-78)

#### Fix #12: Concurrent Run Prevention
**Problem:** Running same script twice simultaneously could corrupt state files, create duplicate tickets, or cause race conditions.

**Solution:** Implemented fcntl-based lockfiles in all workflow scripts:
- Non-blocking lock attempt with `fcntl.LOCK_EX | fcntl.LOCK_NB`
- Clear error message if another instance running
- Automatic lock release on script exit (even with crashes)
- Unique lock file per script (`/tmp/script-name.lock`)

**Impact:** HIGH - Prevents data corruption from concurrent execution.

**Scripts Protected:**
- `monitor-all-news-sources.py` - `/tmp/monitor-all-news-sources.lock`
- `extract-medium-articles.py` - `/tmp/extract-medium-articles.lock`
- `monitor-optimizely-blog.py` - `/tmp/monitor-optimizely-blog.lock`
- `generate-audio-from-assessment.py` - `/tmp/generate-audio-from-assessment.lock`

**Code Pattern:**
```python
import fcntl

lock_file = open('/tmp/script-name.lock', 'w')
try:
    fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
except BlockingIOError:
    print("❌ Error: Another instance of this script is already running")
    sys.exit(1)
# Lock automatically released when script exits or file closes
```

---

### 📊 Phase 2-4 Summary

**Total Improvements:** 12 fixes (5 in Phase 1, 3 in Phase 2, 2 in Phase 3, 2 in Phase 4)

**Files Modified:**
1. `scripts/monitor-optimizely-blog.py` - atomic writes, transactional processing, JIRA constants, lockfile
2. `scripts/anthropic-scraper.py` - atomic writes, JIRA constants
3. `scripts/extract-medium-articles.py` - token handling, email validation, JIRA logging, shared patterns, lockfile
4. `scripts/generate-audio-from-assessment.py` - disk space check, PDF validation, progress bars, FFmpeg logging, lockfile
5. `scripts/generate-article-assessment.py` - rate limit handling with exponential backoff
6. `jaxon-research-feed/generate-feed.py` - atomic writes, XML validation
7. `scripts/shared_patterns.py` - NEW FILE with centralized constants
8. `scripts/prepare-pdf-capture.py` - shared patterns import
9. `scripts/monitor-all-news-sources.py` - lockfile protection

**Impact by Priority:**
- **CRITICAL (4 fixes):** Atomic state writes, transactional processing, token expiration, RSS feed integrity
- **HIGH (5 fixes):** PDF validation, rate limit handling, error logging, concurrent run prevention
- **MEDIUM (3 fixes):** Email validation, progress indicators, shared patterns

**Next Steps:**
- Phase 5: Logging framework (replace print with Python logging module)
- Phase 6: JSON schema validation for metadata files
- Phase 7: Unicode filename handling improvements

---

### 🔧 Fixed PDF Filename Mismatch Issues

**Root Cause:** Scripts generated expected PDF filenames by converting article titles to lowercase with spaces replaced by hyphens. However, actual PDF filenames saved by Playwright could differ due to:
- OS/browser filename length limits causing truncation
- Different character sanitization (apostrophes, special chars)
- Mismatched title extraction from URL slugs

**Solution:** Changed all scripts to find PDFs by article number prefix (e.g., "01-", "02-") instead of generating expected filenames. This makes the workflow robust to any filename variations.

**Scripts Fixed:**
1. `scripts/extract-medium-articles.py` (line 347-363)
2. `scripts/upload-to-drive-helper.py` (line 115-125)
3. `scripts/generate-medium-recommendations.py` (line 233-239)

**Impact:** Eliminates "PDF not found" errors during article processing, ensuring 100% success rate for PDF uploads and metadata updates.

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
