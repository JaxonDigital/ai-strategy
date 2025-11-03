# Medium Article Review Workflow

**Date Created:** October 11, 2025
**Purpose:** Daily process for reviewing Medium articles and tracking insights relevant to Jaxon Digital's AI agent initiatives

## Overview

This workflow extracts articles from daily Medium digest emails, creates JIRA tickets for tracking, and reviews each article for relevance to our AI/MCP business strategy.

## Process Steps

### 1. Extract Article URLs from Email

```bash
# Parse the Medium daily digest email and extract article URLs
python3 << 'EOF'
import re
import base64

# Read the email file
with open('/Users/bgerby/Desktop/10-11.eml', 'r') as f:
    lines = f.readlines()

# Find and decode base64 sections
in_base64 = False
base64_content = []
all_decoded = []

for line in lines:
    if 'Content-Transfer-Encoding: base64' in line:
        in_base64 = True
        continue
    if in_base64:
        if line.strip() and not line.startswith('--'):
            base64_content.append(line.strip())
        elif line.startswith('--') and base64_content:
            try:
                b64_str = ''.join(base64_content)
                decoded = base64.b64decode(b64_str).decode('utf-8', errors='ignore')
                all_decoded.append(decoded)
            except:
                pass
            base64_content = []
            in_base64 = False

# Extract Medium article URLs
full_text = ' '.join(all_decoded)
article_pattern = r'https://medium\.com/@[^/]+/[^?\s<>]+'
urls = re.findall(article_pattern, full_text)

# Deduplicate and print
seen = set()
for url in urls:
    clean_url = url.split('?')[0].rstrip('>')
    if clean_url not in seen and '/' in clean_url.split('@')[1]:
        print(clean_url)
        seen.add(clean_url)
EOF
```

### 2. Check for Duplicate URLs in JIRA

**CRITICAL:** Before creating any tickets, check if URLs already exist in JIRA to avoid duplicates.

```bash
# Set authentication
export JIRA_API_TOKEN=$(cat ~/.jira.d/.pass)

# Get all GAT tickets and check URLs against new articles
# This script checks each URL from the extraction against existing JIRA tickets
python3 << 'EOF'
import subprocess
import re

# Read the new URLs
with open('/tmp/medium-urls.txt', 'r') as f:
    new_urls = [line.strip() for line in f if line.strip()]

# Get all GAT tickets
result = subprocess.run(
    ['jira', 'issue', 'list', '-p', 'GAT', '--plain'],
    capture_output=True,
    text=True,
    env={'JIRA_API_TOKEN': open('/Users/bgerby/.jira.d/.pass').read().strip()}
)

existing_tickets = result.stdout

# For each new URL, check if it exists in any ticket
print("\n=== DUPLICATE CHECK ===\n")
duplicates = []
new_articles = []

for url in new_urls:
    # Extract article slug from URL (the part after the last /)
    slug = url.split('/')[-1].split('?')[0]

    # Check if this slug appears in any ticket summary
    if slug in existing_tickets:
        # Find which ticket(s) contain this
        for line in existing_tickets.split('\n'):
            if slug in line or url in line:
                duplicates.append((url, line))
                print(f"⚠️  DUPLICATE: {url}")
                print(f"    Exists as: {line[:100]}")
                break
    else:
        new_articles.append(url)
        print(f"✅ NEW: {url}")

print(f"\n=== SUMMARY ===")
print(f"New articles to create: {len(new_articles)}")
print(f"Duplicates found: {len(duplicates)}")

# Save only new URLs for ticket creation
if new_articles:
    with open('/tmp/medium-urls-new-only.txt', 'w') as f:
        for url in new_articles:
            f.write(url + '\n')
    print(f"\n✅ Saved {len(new_articles)} new URLs to /tmp/medium-urls-new-only.txt")
else:
    print("\n⚠️  No new articles to create tickets for!")
EOF
```

**Alternative: Quick manual check**
```bash
# List recent review tickets to spot obvious duplicates
JIRA_API_TOKEN="`cat ~/.jira.d/.pass`" jira issue list -p GAT --plain | grep "Review:"
```

### 3. Access Paywalled Articles with Playwright

```bash
# Open browser and log in to Medium
# User must manually log in to access paywalled content
```

**Note:** The PDFs saved from Playwright may show Cloudflare security pages instead of content if pages haven't fully loaded. Better approach: Use `playwright_get_visible_html` after navigation with wait time.

### 4. Create JIRA Tickets (Only for New URLs)

```bash
# Set authentication
export JIRA_API_TOKEN=$(cat ~/.jira.d/.pass)

# Create ticket for each article
JIRA_API_TOKEN=$(cat ~/.jira.d/.pass) jira issue create -p GAT -t Task \
  -s "Review: [Article Title]" \
  -b "Medium Article Review

URL: [article URL]

PDF: See attachments

To be reviewed for relevance to Jaxon Digital's AI agent initiatives."
```

### 5. Attach PDFs to Tickets

Script location: `/Users/bgerby/Desktop/attach-pdfs.sh`

```bash
#!/bin/bash
cd /Users/bgerby/Desktop/medium-articles-10-11

AUTH=$(echo -n 'bgerby@jaxondigital.com:'$(cat ~/.jira.d/.pass) | base64)

# Example for one ticket
curl -s -X POST \
  -H "X-Atlassian-Token: no-check" \
  -H "Authorization: Basic $AUTH" \
  -F "file=@01-ai-gold-rush-5-business-ideas-2026.pdf" \
  "https://jaxondigital.atlassian.net/rest/api/3/issue/GAT-134/attachments" > /dev/null && echo "GAT-134 ✓"
```

### 6. Review Each Article

For each article:
1. Read the full content (use Playwright to get HTML or read PDF)
2. Summarize key points
3. Assess relevance to Jaxon Digital's work:
   - Custom MCP development
   - Agentic AI for Optimizely
   - DXP automation
   - Managed AI services
4. Identify actionable insights
5. Add summary as comment to JIRA ticket
6. Mark ticket as Done when complete

## Article Review Template

```markdown
## Article [N]: "[Title]"

**Summary:**
[2-3 sentence overview of main points]

**Key Points:**
- [Bullet point 1]
- [Bullet point 2]
- [Bullet point 3]

**Relevance to Jaxon Digital (HIGH/MEDIUM/LOW):**
- [Why it matters or doesn't matter to our AI agent work]

**Actionable Insights:**
- [Specific things we can apply]
- [Ideas for client conversations]
- [Technology/framework to explore]

**Recommendation:** [Archive/Follow-up/Create Action Item]
```

## Today's Batch (Oct 11, 2025)

**Tickets Created:** GAT-134 through GAT-148 (15 articles)

**High Priority Articles to Review:**
- GAT-136: 5 Boring n8n AI Automations (Part 2) - Direct relevance to our n8n roadmap
- GAT-138: Journey from AI to LLMs and MCP - MCP fundamentals
- GAT-141: Agentic AI - Comparing Open Source Frameworks - Framework evaluation
- GAT-143: Claude Code Template Library - Operational efficiency
- GAT-145: Build AI Sidekick with Claude Agents SDK - Technical implementation

## Article 1 Review (GAT-134)

**Title:** The Nano Banana AI Gold Rush: 5 Business Ideas to Start in 2026

**Summary:**
Article uses playful "Nano Banana" concept to explore AI transformation in niche industries. Main thesis: Next AI gold rush is embedding AI into hyper-specific niches, not building generic AI tools.

**Key Points:**
- AI-optimized nano farming with IoT sensors and disease prediction
- Nano-particle supplements designed by AI for specific health outcomes
- Tokenized commodity futures (nano banana blockchain exchange)
- AI-powered personalized diet recommendations
- Focus on vertical-specific AI applications over horizontal solutions

**Relevance to Jaxon Digital: MEDIUM**
- **Core Theme Validation:** Deep vertical integration > generic AI tools
  - Confirms our strategy: Optimizely-specific MCPs vs. off-the-shelf platforms
  - Supports "custom system enablement" positioning
- **Not Directly Applicable:** Agriculture/food tech outside our domain
- **Meta-Lesson:** "Absurdly specific niche" framing could strengthen sales messaging

**Actionable Insights:**
- Sales messaging: "We don't build generic AI agents - we build Optimizely-native deployment agents that know your CMS better than you do"
- Validates differentiation through deep domain expertise + custom integration
- Consider emphasizing "vertical AI" in positioning materials

**Recommendation:** Archive after review. Strategic validation but no specific action items.

---

## Google Drive Integration (GAT-288)

**Status:** Planned (See `/Users/bgerby/Desktop/gat-288-google-drive-integration-plan.md`)

### Enhancement Overview

Automatically upload PDFs and audio files to Google Drive and update JIRA descriptions with shareable links.

### Benefits
- Cloud backup of all articles and audio
- Easy sharing with Jaxon Digital team
- Self-contained JIRA tickets with all resources
- Access content from any device

### Workflow Changes

**Updated Process:**
1. Extract articles from email → Create JIRA tickets
2. Capture PDFs with Playwright
3. **NEW:** Upload PDFs to Google Drive → Get shareable link → Update JIRA description
4. Generate audio files (for 3+ star articles)
5. **NEW:** Upload audio to Google Drive → Get shareable link → Update JIRA description

**Script Flags:**
```bash
# Upload PDFs to Drive and update JIRA
python3 extract-medium-articles.py 10-20.eml --create-tickets --upload-to-drive

# Upload audio to Drive and update JIRA
python3 generate-article-audio.py --upload-to-drive
```

**Updated JIRA Format:**
```markdown
Medium Article Review

**Article URL:** https://medium.com/@author/article-slug
**PDF:** https://drive.google.com/file/d/FILE_ID/view?usp=sharing
**Audio:** https://drive.google.com/file/d/FILE_ID/view?usp=sharing

To be reviewed for relevance to Jaxon Digital's AI agent initiatives.
```

**Drive Folder Structure:**
```
Google Drive/Medium Articles/
├── PDFs/
│   ├── 2025-10-16/
│   ├── 2025-10-17/
│   └── 2025-10-18/
└── Audio/
    └── reviews/
```

**Implementation Status:**
- [x] Strategic plan created (GAT-288)
- [ ] MCP server installed (piotr-agier/google-drive-mcp)
- [ ] OAuth credentials configured
- [ ] Scripts updated with --upload-to-drive flag
- [ ] Testing with GAT-304+ articles

---

## Future n8n Automation Potential

Once workflow is validated, this can be converted to an n8n agent:

**Workflow:**
1. **Trigger:** Daily email from Medium → n8n webhook
2. **Extract URLs:** Parse email for article links
3. **Medium Access:**
   - Option A: Use Medium RSS feed (limited)
   - Option B: Playwright node with saved session/cookies
   - Option C: Store session state for headless browser
4. **Content Extraction:** Playwright node to scrape full articles
5. **PDF Generation:** Convert to PDF for team sharing
6. **JIRA Integration:**
   - Create tickets via JIRA REST API
   - Attach PDFs to tickets
7. **AI Analysis:**
   - Use Claude MCP/API to summarize articles
   - Assess relevance against business criteria
   - Generate actionable insights
8. **Notification:**
   - Slack/email summary
   - Flag high-priority articles for immediate review

**Authentication Considerations:**
- Medium login session management
- Cookie refresh strategy
- API rate limits

**MCP Integration:**
- Could use custom MCP for Medium content extraction
- JIRA MCP for ticket management
- Claude MCP for content analysis

---

## Files Created Today

- `/Users/bgerby/Desktop/medium-articles-10-11/` - PDF storage directory
- `/Users/bgerby/Desktop/attach-pdfs.sh` - JIRA PDF attachment script
- `/tmp/medium-urls.txt` - Extracted URLs
- Email source: `/Users/bgerby/Desktop/10-11.eml`

## JIRA Board

Project: GAT (Growth & AI Transformation)
Board: https://jaxondigital.atlassian.net/jira/software/c/projects/GAT/boards/228

## Next Steps

1. Continue reviewing remaining 14 articles sequentially
2. Add summaries as JIRA comments
3. Create follow-up tickets for actionable items
4. Explore text-to-speech for audio versions (per user preference)
5. Document n8n automation requirements once workflow is finalized
