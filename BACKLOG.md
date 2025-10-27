# BACKLOG.md

Future enhancements and ideas for the Jaxon Research Feed project and related workflows.

## High Priority

### Autonomous Daily Article Processing Agent

**Status**: Planned for Q1 2026

**Description**: Create a fully autonomous agent that runs daily to process Medium articles and Optimizely blog posts without manual intervention.

**Capabilities**:
- Monitor Medium email digest (IMAP integration)
- Monitor Optimizely World RSS feed
- Extract article URLs and create JIRA tickets
- Capture PDFs using Playwright (with saved login session)
- Upload PDFs to Google Drive
- Generate relevance assessments
- Generate audio for HIGH priority articles
- Upload audio to Drive and update JIRA tickets
- Update podcast RSS feed
- Commit and push to GitHub Pages
- Send daily summary email/Slack notification

**Technical Requirements**:
- n8n workflow orchestration
- MCP servers: Google Drive, JIRA, Playwright, GitHub
- OpenAI API for assessment and TTS
- IMAP/email integration for Medium digests
- Scheduled trigger (daily at 8 AM)

**Value Proposition**:
- Zero manual work for daily article processing
- Consistent execution without missing articles
- Frees up 2-3 hours daily for strategic analysis

**Estimated Effort**: 40-60 hours development + testing

---

### Historical Optimizely World Blog Analysis

**Status**: Backlog (low priority)

**Description**: Retrieve and analyze historical Optimizely World blog posts to identify missed opportunities for agent automation.

**Scope**:
- 1,163 pages of historical blog posts (est. 5,000+ articles)
- Date range: 2010-2025
- Focus on identifying:
  - Recurring DXP operational issues
  - Common deployment problems
  - CMS workflow pain points
  - Commerce integration challenges

**Process**:
1. Run historical scraper: `python3 scripts/scrape-optimizely-history.py`
2. Create JIRA tickets for HIGH priority historical articles
3. Capture PDFs for selected articles
4. Analyze patterns for agent opportunities

**Value Proposition**:
- Discover agent opportunities from past Optimizely challenges
- Build competitive intelligence database
- Identify recurring customer pain points

**Estimated Effort**: 20-30 hours (mostly PDF capture and analysis)

**Note**: Use `--dry-run` first to estimate volume before creating 100+ JIRA tickets

---

## Medium Priority

### Medium Author/Publication Recommendation System

**Status**: Partially Complete (Oct 24, 2025)

**Description**: Automated system to generate follow/mute recommendations based on article relevance patterns.

**Current Implementation**:
- `scripts/generate-medium-recommendations.py` analyzes assessment files
- Generates recommendations based on HIGH vs LOW priority distribution
- Output: `outputs/medium-recommendations-YYYY-MM-DD.txt`

**Future Enhancements**:
- Track recommendations over time (trending authors/publications)
- Auto-mute LOW priority sources after 3+ consecutive LOW articles
- Integration with Medium API to programmatically follow/mute
- Dashboard showing author/publication performance over time

**Estimated Effort**: 15-20 hours

---

### Podcast Feed Analytics

**Status**: Planned

**Description**: Track podcast feed usage and engagement metrics.

**Features**:
- Listen/download analytics using GitHub Pages logs
- Episode completion rates (if possible via podcast app APIs)
- Popular episode identification
- RSS feed subscriber count tracking
- Integration with podcast hosting services (Spotify, Apple Podcasts)

**Value Proposition**:
- Understand which articles/topics resonate most
- Optimize content strategy based on engagement
- Demonstrate ROI for podcast feed to stakeholders

**Estimated Effort**: 10-15 hours

---

### Failed Audio Retry Mechanism

**Status**: Planned

**Description**: Automatically retry failed audio generations instead of manual intervention.

**Current Issues**:
- ffmpeg errors (exit code 254) - corrupted/mismatched audio chunks
- Chunk creation failures (file size too small)
- Network timeouts during OpenAI TTS API calls

**Proposed Solution**:
- Automatic retry with exponential backoff (3 attempts)
- Fallback to smaller chunk sizes if large chunks fail
- Error logging to identify systemic issues
- Success/failure tracking in JSON results file

**Estimated Effort**: 5-10 hours

---

## Low Priority

### Multi-Source RSS Feed

**Status**: Idea stage

**Description**: Separate RSS feeds for different content sources (Medium, Optimizely, Other).

**Rationale**:
- Some users may only want Medium articles
- Others may only want Optimizely technical content
- Allow subscribers to customize their feed

**Implementation**:
- `feed-medium.rss` - Medium articles only
- `feed-optimizely.rss` - Optimizely World articles only
- `feed-all.rss` - Combined feed (current)

**Estimated Effort**: 3-5 hours

---

### Article Clustering and Topic Analysis

**Status**: Idea stage

**Description**: Use ML to cluster articles by topic and identify emerging trends.

**Features**:
- Semantic clustering using embeddings (OpenAI or local models)
- Topic modeling to identify themes (e.g., "MCP development", "AI agents", "DevOps")
- Trend analysis over time (e.g., "Claude Skills" mentions increasing)
- Visual dashboard showing topic distribution

**Value Proposition**:
- Identify emerging technologies before they become mainstream
- Understand market sentiment shifts
- Guide Jaxon Digital's strategic priorities

**Estimated Effort**: 30-40 hours

---

### Interactive Web Dashboard

**Status**: Idea stage

**Description**: Web-based dashboard for article tracking, analytics, and management.

**Features**:
- View all articles with filters (date, priority, source)
- Play audio directly in browser
- Search articles by keyword/topic
- View recommendations and author performance
- Manual ticket creation/editing
- Analytics charts (articles over time, priority distribution)

**Tech Stack**:
- Frontend: React or Vue.js
- Backend: FastAPI or Express.js
- Database: PostgreSQL or SQLite
- Hosting: GitHub Pages (static) or Vercel (dynamic)

**Estimated Effort**: 60-80 hours

---

### Alternative TTS Voices

**Status**: Idea stage

**Description**: Experiment with different TTS voices for variety and engagement.

**Options**:
- OpenAI TTS: nova, shimmer, onyx (currently using "nova")
- ElevenLabs for more natural-sounding voices
- Google Cloud TTS for cost comparison
- Multi-voice support (different voices for different article types)

**Considerations**:
- Cost per article varies by provider
- Quality/naturalness trade-offs
- API rate limits and reliability
- User preference testing

**Estimated Effort**: 5-10 hours

---

## Technical Debt

### Python Environment Standardization

**Status**: Ongoing issue

**Current State**:
- Mix of Python 3.7.3 (system) and Python 3.11 (scripts)
- Some scripts require 3.11 for modern libraries
- Others work with 3.7 for compatibility

**Recommendation**:
- Standardize on Python 3.11+ across all scripts
- Update shebang lines: `#!/usr/bin/env python3.11`
- Document required Python version in README
- Use virtual environments for dependency isolation

**Estimated Effort**: 2-3 hours

---

### Google Drive Token Refresh

**Status**: Recurring maintenance

**Issue**: Google OAuth tokens expire and require manual refresh every 7 days.

**Current Workaround**:
- Run MCP server once to auto-refresh token
- Token stored in `/Users/bgerby/Documents/dev/ai/mcp-googledocs-server/token.json`

**Proposed Solution**:
- Implement automatic token refresh in upload scripts
- Add token refresh check before Drive API calls
- Service account setup for long-lived credentials (if possible)

**Estimated Effort**: 3-5 hours

---

### Error Notification System

**Status**: Planned

**Description**: Automated notifications when workflows fail.

**Features**:
- Email alerts for failed audio generation
- Slack notifications for script errors
- Daily summary of workflow status
- Integration with monitoring tools (Sentry, DataDog)

**Estimated Effort**: 5-8 hours

---

## Research & Learning

### Explore Gemini 2.5 Flash for TTS

**Status**: Research phase

**Context**: User mentioned "nano banana (gemini 2.5 flash) is VERY good" for image generation.

**Investigation**:
- Does Gemini 2.5 Flash support TTS?
- Cost comparison vs OpenAI TTS
- Quality/naturalness comparison
- API integration effort

**Next Steps**:
- Review Gemini API docs for TTS capabilities
- Run side-by-side comparison if TTS available
- Evaluate for potential migration

**Estimated Effort**: 2-4 hours

---

### n8n MCP Integration

**Status**: Monitoring roadmap

**Context**: n8n is working on MCP support which would enable MCP-based workflows.

**Benefits**:
- Use existing MCPs (Google Drive, JIRA, Playwright) in n8n workflows
- Eliminate custom Python scripts where possible
- Visual workflow design for non-technical users
- Better error handling and retry logic

**Timeline**: n8n MCP support expected Q2 2025

**Next Steps**:
- Monitor n8n roadmap and beta releases
- Plan migration of Python scripts to n8n workflows
- Identify workflows best suited for n8n vs custom scripts

**Estimated Effort**: TBD (depends on n8n MCP maturity)

---

## Notes

- This backlog is a living document and should be updated as priorities change
- Effort estimates are rough and may vary based on complexity
- High priority items should be scheduled first, but remain flexible
- Review and update quarterly based on Jaxon Digital's strategic priorities
