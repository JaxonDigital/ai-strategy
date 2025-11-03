# Desktop Working Notes

Local project-specific notes for daily workflows and automation experiments.

## Medium Article Review Workflow

### Overview
Daily process for extracting, reviewing, and tracking insights from Medium digest emails. Goal: Identify AI/MCP content relevant to Jaxon Digital's business strategy.

### Key Files
- `medium-article-review-workflow.md` - Complete workflow documentation
- `attach-pdfs.sh` - Script for bulk PDF attachment to JIRA
- `medium-articles-[date]/` - PDF storage directories

### Workflow Process (Established Oct 11-12, 2025)

#### 1. Email Parsing
```bash
# Extract article URLs from .eml file using Python
# Handles base64-encoded email content
# Outputs clean Medium article URLs to /tmp/medium-urls.txt
```

#### 2. Content Extraction
**Method:** Playwright with `playwright_get_visible_html`
- Navigate to article URL
- Wait 3 seconds for full page load (avoid Cloudflare security pages)
- Extract HTML with `removeScripts: true, cleanHtml: true`
- **Don't use PDF generation** - causes incomplete content capture

#### 3. JIRA Ticket Creation
```bash
# Always use -p flag for project context
export JIRA_API_TOKEN=$(cat ~/.jira.d/.pass)
jira issue create -p GAT -t Task -s "Review: [Title]" -b "[Description]"
```

#### 4. PDF Attachment (if needed)
- Use dedicated bash script with Basic auth
- Iterate through numbered PDFs matching ticket sequence
- Example: `/Users/bgerby/Desktop/attach-pdfs.sh`

#### 5. Article Review
**Template:**
- Summary (2-3 sentences)
- Key points (bullets)
- Relevance rating (HIGH/MEDIUM/LOW with score)
- Actionable insights (specific to Jaxon Digital's business)
- Recommendation (Archive/Follow-up/Create Action Item)

**Focus Areas:**
- Custom MCP development patterns
- n8n automation use cases
- Optimizely/DXP integration opportunities
- Agentic AI frameworks and approaches
- Vertical AI positioning vs horizontal platforms

### Key Learnings (Oct 11-12, 2025)

#### Strategic Insights
1. **"Vertical AI" Positioning (Article 1)**
   - Deep niche integration > generic AI tools
   - Messaging: "We don't build generic AI agents. We build Optimizely-native deployment agents that know your CMS better than you do."
   - Validates: Merging Optimizely expertise with AI (not pivoting away)

2. **"Boring Automations" as Service Model (Article 3)**
   - n8n + AI patterns = managed service SKUs
   - Examples: Support ticket sentiment routing → DXP alert prioritization
   - Framing: "Quiet leverage" that compounds over time

#### Technical Patterns
1. **Playwright Best Practices**
   - Always wait 3+ seconds after navigation before content extraction
   - Use `playwright_get_visible_html` instead of PDF generation for paywalled content
   - Keep browser session open across multiple article fetches

2. **JIRA CLI Tips**
   - Must use `-p PROJECT` flag explicitly (no defaults in config)
   - Export token separately before command in Claude's Bash tool
   - Status transitions: "Gathering Requirements" → "In Dev" → "Done"

3. **Email Parsing**
   - Medium digest emails are base64-encoded
   - Python regex pattern: `r'https://medium\.com/@[^/]+/[^?\s<>]+'`
   - Need to deduplicate URLs (article links appear multiple times in HTML)

### Future Automation Path

**Phase 1: Manual (Current)**
- Parse email → Extract URLs → Create tickets → Review articles
- Time: ~2-3 hours per batch of 15 articles

**Phase 2: Semi-Automated (Next)**
- n8n workflow: Email trigger → URL extraction → Content fetch → JIRA creation
- AI pre-analysis: GPT-4 generates initial relevance score + summary
- Human review: Final assessment and action items
- Time target: ~30 minutes per batch

**Phase 3: Fully Automated (Future)**
- Event-driven n8n agent monitoring RSS/email feeds
- AI analysis with confidence scoring
- Auto-prioritization: High relevance → Slack notification
- Batch summaries: Daily digest of all articles
- Time target: ~5 minutes for high-priority reviews only

**Demo Value:**
- "If we can automate OUR content review, we can automate YOUR deployment monitoring"
- Proves n8n + MCP + AI patterns in production use
- Client-facing pitch: "These same patterns monitor your DXP operations"

### n8n Prototype Candidates

1. **Daily Content Intelligence Agent**
   - Input: Medium digest email (via webhook or IMAP)
   - Process: Parse → Fetch content → AI analysis (GPT-4)
   - Output: JIRA tickets + Slack alerts for high-priority
   - MCPs: JIRA MCP + Custom Medium MCP + Claude MCP

2. **DXP Alert Prioritization Agent**
   - Input: Azure App Insights alerts
   - Process: AI sentiment/urgency analysis
   - Output: Prioritized Slack messages with context
   - MCPs: Optimizely DXP MCP + Slack MCP + Claude MCP

3. **Deployment Runbook Generator**
   - Input: Email threads about repeated deployment issues
   - Process: Pattern detection → GPT-4 runbook generation
   - Output: Notion documentation auto-updated
   - MCPs: Custom Email MCP + Notion MCP + Claude MCP

### Next Steps

- [ ] Process today's new email (Oct 12, 2025)
- [ ] Mark GAT-135, GAT-136 as Done with review summaries
- [ ] Create ticket for n8n prototype (Daily Content Intelligence Agent)
- [ ] Review remaining 13 articles from Oct 11 batch (time permitting)
- [ ] Document "Medium MCP" specification for content extraction

---

**Last Updated:** October 12, 2025
**Workflow Status:** Active - Daily email processing
**JIRA Project:** GAT (Growth & AI Transformation)
**Board:** https://jaxondigital.atlassian.net/jira/software/c/projects/GAT/boards/228
