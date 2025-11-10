# Troubleshooting Guide

This document contains detailed troubleshooting steps for common issues in article review workflows.

## Medium Article Capture

### PDF file size ~115KB

**Problem:** Article is paywalled and wasn't captured fully.

**Solution:**
1. Re-capture with authenticated browser session
2. Ensure login session persists across articles
3. Check browser is not in headless mode during login
4. Verify user logged in successfully before starting capture

**Verification:**
```bash
# Check file sizes - successful captures are 400KB+
ls -lh /Users/bgerby/Desktop/medium-articles-*/*.pdf

# Files ~115KB = paywalled (only preview captured)
# Files 400KB-5MB = success (full article captured)
```

### Browser closes between articles

**Problem:** Login session lost, subsequent articles are paywalled.

**Solution:**
- Don't close browser between articles
- Keep using same browser instance with `headless: false`
- Only close browser after all articles captured

### Can't manually log in

**Problem:** Browser is headless, can't see login form.

**Solution:**
- Set `headless: false` in Playwright navigate call
- Browser window must be visible on screen
- Wait for user to complete login before proceeding

## Article Assessment

### Audio generation fails

**Check OpenAI API key:**
```bash
# Verify key is set
echo $OPENAI_API_KEY

# Should output: sk-proj-...
# If empty, export it:
export OPENAI_API_KEY="sk-proj-..."
```

**Verify API key is valid:**
- Check key is not expired in OpenAI dashboard
- Test with simple API call

**Check PDF text extraction:**
```bash
# Test extraction manually
pdftotext /path/to/file.pdf -

# Should output article text
# If empty or errors, PDF may be corrupted or image-based
```

**Review text cleaning:**
- Check `generate-audio-review.py:33-98` for cleaning regex
- Test cleaning on sample text
- May need to update patterns for new content types

### Assessment script fails

**Python/OpenAI errors:**
```bash
# Check Python version (needs 3.7+)
python3 --version

# Install/upgrade OpenAI library
pip3 install --upgrade openai

# Test OpenAI connection
python3 -c "from openai import OpenAI; print('OK')"
```

**Large PDF chunking issues:**
- Script automatically chunks PDFs over 12K chars
- Check overlap settings if context is lost between chunks
- May need to adjust chunk size in script

**Rate limiting:**
- Script includes rate limiting (sleep between calls)
- If hitting limits, increase sleep duration
- Check OpenAI API rate limits for your tier

## Google Drive Integration

### Upload fails

**Check token file:**
```bash
# Verify token exists and is readable
ls -l /Users/bgerby/Documents/dev/ai/mcp-googledocs-server/token.json

# Token should be ~1KB JSON file
# If missing, re-run MCP server auth
```

**Verify folder IDs:**
- Shared Drive root: `0ALLCxnOLmj3bUk9PVA`
- Check folder IDs in MCP commands match expected structure
- Use `mcp__google-docs-drive__listFolderContents` to verify

**Internet connection:**
- Ensure stable connection
- Large files (5MB+ PDFs) may timeout on slow connections
- Retry failed uploads

**Google Drive quota:**
- Check quota in Drive web UI
- Free up space if near limit
- Contact admin if using Shared Drive with quota

### Cannot create at Shared Drive root

**Problem:** MCP error when trying to create document at root level.

**Solution:**
- Must create folders first, then documents inside folders
- Use `parentFolderId` parameter (NOT `driveId`)
- Follow YYYY/MM/DD folder structure

**Correct approach:**
1. Create year folder with `parentFolderId=<SharedDriveId>`
2. Create month folder with `parentFolderId=<YearFolderId>`
3. Create day folder with `parentFolderId=<MonthFolderId>`
4. Create document with `parentFolderId=<DayFolderId>`

### File not appearing in Drive

**Check upload completed:**
- Script should output Drive file ID
- Verify ID in script logs

**Check permissions:**
- File must have public sharing enabled
- Use `mcp__google-docs-drive__*` tools with correct sharing settings

**Refresh Drive UI:**
- Browser cache may be stale
- Hard refresh (Cmd+Shift+R) or clear cache

## JIRA Integration

### Update fails

**Verify token:**
```bash
# Check token file exists
cat ~/.jira.d/.pass

# Should output API token (long alphanumeric string)
# If missing, regenerate in JIRA settings
```

**Check ticket ID:**
- Verify ticket exists: `jira issue view GAT-XXX`
- Check project key is correct (GAT not DXP, TW, etc.)
- Ensure ticket not deleted or moved

**Use --no-input flag:**
- Always add `--no-input` to avoid interactive prompts
- Interactive prompts hang in automated scripts

**Temp file approach for long comments:**
```bash
# ❌ Don't use heredoc directly - will hang
JIRA_API_TOKEN="..." jira issue comment add GAT-XXX "$(cat <<'EOF'
Long comment
EOF
)"

# ✅ Use temp file instead
cat > /tmp/comment.txt << 'EOF'
Long comment
EOF
JIRA_API_TOKEN="`cat ~/.jira.d/.pass`" jira issue comment add GAT-XXX "$(cat /tmp/comment.txt)" --no-input
```

### Ticket creation hangs

**Problem:** jira CLI waiting for stdin input.

**Causes:**
1. Using heredoc in command substitution
2. Missing `--no-input` flag
3. Interactive prompt triggered

**Solution:**
- Use backticks for token: `` `cat ~/.jira.d/.pass` `` not `$(cat ...)`
- Always add `--no-input` flag
- Write long descriptions to temp file first

### Wrong project

**Problem:** Ticket created in wrong project or not found.

**Solution:**
- Always use `-p` flag to specify project explicitly
- Don't rely on global config default project
- Example: `jira issue list -p GAT` (space after `-p`!)

## Optimizely World Monitoring

### RSS feed returns 403 Forbidden

**Problem:** Server blocking automated requests.

**Solution:**
- Script includes User-Agent header
- If blocked, update User-Agent in `monitor-optimizely-blog.py:60`
- Try different User-Agent strings

**Alternative:**
```python
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}
```

### No new articles found

**Expected behavior:**
- RSS feed only returns most recent 20 articles
- Older articles won't appear in incremental runs
- Check state file to verify articles marked as seen

**Verify state file:**
```bash
cat ~/.optimizely-blog-state.json | grep "last_check"

# Should show recent timestamp
# If old, state file may not be updating
```

### Article capture fails

**Causes:**
1. Personal blog with anti-scraping measures
2. URL not accessible
3. Login required

**Solutions:**
- Use Playwright MCP with manual browser session
- Verify URL accessible in normal browser first
- Check for paywalls or login requirements
- Try different User-Agent or headers

### JIRA ticket creation fails

**Check jira CLI:**
```bash
# Verify CLI installed
which jira

# Check config
cat ~/.config/.jira/.config.yml

# Test authentication
export JIRA_API_TOKEN=$(cat ~/.jira.d/.pass)
jira issue list -p GAT --plain
```

**Timeout issues:**
- Script has 60-second timeout per ticket
- Check network connection
- Retry failed tickets by running script again

**Failed tickets:**
- Reported in summary output
- Can retry by running script again (duplicates skipped)
- Check JIRA API status if consistent failures

### Duplicate tickets created

**Status:** As of October 23, 2025 - Duplicate detection implemented and verified working.

**Prevention:**
- Two-tier detection (state file + JIRA search)
- Automatically skips articles already processed
- Logs existing ticket ID when duplicate found

**Known limitation:**
- WordPress permalink vs shortlink variations may slip through
- Example: `https://example.com/2025/10/article` vs `http://example.com/?p=123`

**If duplicates found:**
1. Delete newer duplicate ticket
2. URL mapping in state file prevents recurrence
3. Consider adding URL normalization to script

## Podcast Feed

### Episodes not appearing in podcast app

**Verify MP3 uploaded:**
```bash
# Check drive-urls.json has entry
cat /Users/bgerby/Documents/dev/ai/jaxon-research-feed/drive-urls.json | grep GAT-XXX
```

**Ensure RSS feed updated:**
```bash
# Check feed has episode
cat /Users/bgerby/Documents/dev/ai/jaxon-research-feed/feed.rss | grep GAT-XXX
```

**Confirm pushed to GitHub:**
```bash
cd /Users/bgerby/Documents/dev/ai/jaxon-research-feed
git log -1

# Should show recent commit with feed.rss
```

**Wait for refresh:**
- Podcast apps cache feeds
- May take 5-15 minutes for new episodes to appear
- Force refresh in app (pull down on show page)

### Login banners or footer text in audio

**Problem:** PDF text extraction includes unwanted content.

**Solution:**
1. Update regex patterns in `clean_text_for_speech()` function
2. Test cleaning on sample text
3. Re-generate audio with updated script

**Test cleaning:**
```bash
pdftotext file.pdf - | python3 -c "
import sys
exec(open('generate-audio-review.py').read())
print(clean_text_for_speech(sys.stdin.read())[:500])
"
```

**Common patterns to remove:**
- Login banners: "Sign in", "Create account", "Member-only story"
- Footer sections: "Written by", "Published in", "Follow", "More from"
- Code blocks: Triple backticks, syntax highlighting
- Tag bubbles: "#python", "#javascript"
- WordPress elements: "Leave a Reply", "Comment", "Subscribe"

### Drive upload fails

**Check token:**
```bash
# Verify token file exists
ls -l /Users/bgerby/Documents/dev/ai/mcp-googledocs-server/token.json
```

**Verify folder ID:**
- MP3s folder: `1NB1a1jGrqTmXvSw8CVQAsi_j05DCBg59`
- Check ID is correct in script

**Network issues:**
- Ensure stable internet connection
- Large MP3 files (10MB+) may timeout
- Retry failed uploads

**Drive quota:**
- Check quota in Drive web UI
- Free up space if needed

## Python Script Errors

### Module not found

**Problem:** Script fails with "ModuleNotFoundError".

**Solution:**
```bash
# Install missing module
pip3 install <module-name>

# Common modules needed:
pip3 install openai
pip3 install google-api-python-client
pip3 install google-auth-httplib2
pip3 install google-auth-oauthlib
pip3 install mutagen  # For MP3 metadata
```

### Permission denied

**Problem:** Script can't read/write files.

**Solution:**
```bash
# Check file permissions
ls -l /path/to/file

# Make script executable
chmod +x script.py

# Check directory permissions
ls -ld /path/to/directory
```

### Python version issues

**Check version:**
```bash
python3 --version

# Need 3.7+ for most scripts
# Upgrade if needed:
brew upgrade python3
```

## Environment Variables

### Variable not set

**Problem:** Script fails with "environment variable not set".

**Check common variables:**
```bash
# OpenAI API key
echo $OPENAI_API_KEY

# JIRA API token
echo $JIRA_API_TOKEN

# GitHub token (if using gh CLI)
echo $GH_TOKEN
```

**Set variables:**
```bash
# Temporarily (current session only)
export OPENAI_API_KEY="sk-proj-..."

# Permanently (add to ~/.zshrc)
echo 'export OPENAI_API_KEY="sk-proj-..."' >> ~/.zshrc
source ~/.zshrc
```

### Variable doesn't persist

**Problem:** Variable set but script doesn't see it.

**Claude Code Bash tool:**
- Each Bash tool invocation is separate shell session
- Variables don't persist between calls
- Must set variable in same command that uses it

**Solution:**
```bash
# ❌ Don't do this (won't work in Bash tool)
export OPENAI_API_KEY="sk-proj-..."
python3 script.py

# ✅ Do this instead
OPENAI_API_KEY="sk-proj-..." python3 script.py
```

## State File Issues

### State file corrupted

**Location:** `~/.optimizely-blog-state.json`

**Recovery:**
```bash
# Backup current state
cp ~/.optimizely-blog-state.json ~/.optimizely-blog-state.json.bak

# Reset state (will re-process all articles)
rm ~/.optimizely-blog-state.json
python3 scripts/monitor-optimizely-blog.py --dry-run

# Or manually fix JSON errors
nano ~/.optimizely-blog-state.json
```

### State file not updating

**Check permissions:**
```bash
ls -l ~/.optimizely-blog-state.json

# Should be writable by user
# If not:
chmod 644 ~/.optimizely-blog-state.json
```

**Check disk space:**
```bash
df -h ~

# Ensure sufficient space available
```

## Git/GitHub Issues

### Push rejected

**Problem:** GitHub rejects push.

**Common causes:**
1. Branch protection rules
2. Out of sync with remote
3. Authentication failed

**Solutions:**
```bash
# Pull latest changes first
git pull origin main

# Resolve conflicts if any
git status
# ... fix conflicts ...
git add .
git commit -m "Resolve conflicts"

# Push again
git push origin main

# If authentication fails, check token:
echo $GH_TOKEN
```

### GitHub Pages not updating

**Check Pages settings:**
1. Go to repository settings
2. Navigate to Pages section
3. Verify source branch is correct (main)
4. Check build status

**Force rebuild:**
- Make empty commit
- Push to trigger rebuild

```bash
git commit --allow-empty -m "Trigger Pages rebuild"
git push
```

**Wait for build:**
- Pages may take 1-2 minutes to rebuild
- Check Actions tab for build status
