# GAT-288: Google Drive Integration Strategic Plan

**JIRA:** https://jaxondigital.atlassian.net/browse/GAT-288
**Date Created:** October 20, 2025
**Status:** Planning
**Owner:** Brian Gerby

## Executive Summary

Enhance the Medium article review workflow by automatically uploading PDFs and audio files to Google Drive, then updating JIRA ticket descriptions with shareable links. This provides cloud backup, team collaboration, and makes JIRA tickets self-contained with all resources.

## Current State

### Workflow Gaps
- **PDFs**: Stored locally at `/Users/bgerby/Desktop/medium-articles-YYYY-MM-DD/*.pdf`
- **Audio**: Stored locally at `/Users/bgerby/Documents/dev/ai/audio-reviews/*.mp3`
- **No cloud backup**: Single point of failure on local machine
- **No team sharing**: Files not accessible to team members
- **JIRA incomplete**: Tickets contain URLs but not actual content

### Current Scripts
1. **extract-medium-articles.py**: Extracts URLs from emails, creates JIRA tickets
2. **generate-article-audio.py**: Generates MP3 audio from PDFs for listening

## Strategic Goals

1. **Cloud Backup**: All articles and audio backed up to Google Drive
2. **Team Collaboration**: Easy sharing with Jaxon Digital team
3. **Self-Contained JIRA**: Tickets include links to all resources
4. **Cross-Device Access**: Access content from any device
5. **No Storage Limits**: Remove local storage constraints

## Technical Approach: MCP-First Architecture

### Option 1: Google Drive MCP Server (Recommended)

**Why MCP First:**
- Aligns with Jaxon Digital's MCP expertise and business model
- Reusable across multiple projects
- Standard protocol interface
- Easier to maintain and test
- Demonstrates MCP capabilities to clients

**Available MCP Servers:**

| Server | Author | Features | Auth | Language | Notes |
|--------|--------|----------|------|----------|-------|
| **isaacphi/mcp-gdrive** | Isaac Phi | List, read, search files; Read/write Google Sheets | OAuth 2.0 | TypeScript | Most mature, active development |
| **piotr-agier/google-drive-mcp** | Piotr Agier | Full CRUD on Drive, Docs, Sheets, Slides | OAuth 2.0 | TypeScript | Comprehensive file management |
| **felores/gdrive-mcp-server** | Felores | Search, list, read files | OAuth 2.0 | Python | Lightweight implementation |
| **distrihub/mcp-google-workspace** | DistriHub | Drive + Sheets integration | OAuth 2.0 | Rust | High performance |
| **aaronsb/google-workspace-mcp** | Aaron SB | Drive, Gmail, Calendar | OAuth 2.0 | TypeScript | Full workspace integration |

**Recommended Server:** `piotr-agier/google-drive-mcp`
- **Rationale**: Full file management capabilities (create, upload, get shareable links)
- Secure OAuth 2.0 authentication
- Active maintenance
- Supports all required operations

### Option 2: Direct Google Drive API

**Fallback if no suitable MCP exists:**
- Python `google-api-python-client` library
- Service account authentication
- More control, no MCP dependencies
- **Downside**: Less reusable, more boilerplate

## Implementation Roadmap

### Phase 1: MCP Server Setup (Week 1)

**Tasks:**
1. [ ] Install chosen Google Drive MCP server (`piotr-agier/google-drive-mcp`)
2. [ ] Configure OAuth 2.0 credentials (Google Cloud Console)
3. [ ] Add MCP server to `.mcp.json` configuration
4. [ ] Test basic operations: upload file, get shareable link
5. [ ] Document authentication setup

**Acceptance Criteria:**
- MCP server running and authenticated
- Can upload test file to Drive
- Can retrieve shareable link
- Documented in project README

### Phase 2: Folder Structure Setup (Week 1)

**Tasks:**
1. [ ] Create Google Drive folder structure:
   ```
   Medium Articles/
   ├── PDFs/
   │   ├── 2025-10-16/
   │   ├── 2025-10-17/
   │   ├── 2025-10-18/
   │   └── 2025-10-19/
   └── Audio/
       └── reviews/
   ```
2. [ ] Set sharing permissions (Jaxon Digital team)
3. [ ] Get folder IDs for programmatic access
4. [ ] Test folder creation via MCP

**Acceptance Criteria:**
- Folder structure created in Drive
- Team members can access folders
- Folder IDs documented for scripts

### Phase 3: Script Integration (Week 2)

#### 3.1 Update extract-medium-articles.py

**Changes:**
```python
# Add new flag
parser.add_argument('--upload-to-drive', action='store_true',
                   help='Upload PDFs to Google Drive and update JIRA with links')

# After PDF capture
if args.upload_to_drive:
    drive_link = upload_to_drive(pdf_path, gat_number)
    update_jira_description(gat_number, pdf_link=drive_link)
```

**Functions to implement:**
- `upload_to_drive(pdf_path, gat_number)`: Upload PDF, return shareable link
- `update_jira_description(gat_number, pdf_link, audio_link=None)`: Update JIRA description

#### 3.2 Update generate-article-audio.py

**Changes:**
```python
# Add new flag
parser.add_argument('--upload-to-drive', action='store_true',
                   help='Upload audio to Google Drive and update JIRA with links')

# After audio generation
if args.upload_to_drive:
    drive_link = upload_to_drive(audio_path, gat_number)
    update_jira_description(gat_number, audio_link=drive_link)
```

**Tasks:**
1. [ ] Add `--upload-to-drive` flag to both scripts
2. [ ] Implement MCP client for Drive operations
3. [ ] Implement JIRA description update via API
4. [ ] Add retry logic for upload failures
5. [ ] Add progress indicators

**Acceptance Criteria:**
- Scripts upload files to correct Drive folders
- Shareable links retrieved successfully
- JIRA descriptions updated automatically
- Error handling for upload failures

### Phase 4: JIRA Description Format (Week 2)

**New JIRA Ticket Format:**
```markdown
Medium Article Review

**Article URL:** https://medium.com/@author/article-slug
**PDF:** https://drive.google.com/file/d/FILE_ID/view?usp=sharing
**Audio:** https://drive.google.com/file/d/FILE_ID/view?usp=sharing

⭐ Relevance Rating: [To be determined]

To be reviewed for relevance to Jaxon Digital's AI agent initiatives.

---
🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

**Tasks:**
1. [ ] Define Jinja2 template for JIRA descriptions
2. [ ] Implement `update_jira_description()` function
3. [ ] Test with existing tickets (dry-run mode)
4. [ ] Backfill links for recent tickets (GAT-273+)

### Phase 5: Testing & Validation (Week 3)

**Test Cases:**
1. [ ] Upload PDF for new article (GAT-304+)
2. [ ] Generate audio and upload for 3+ star article
3. [ ] Verify JIRA description updates correctly
4. [ ] Test with paywalled article (large PDF)
5. [ ] Test with multiple articles in batch
6. [ ] Verify team member access to Drive files
7. [ ] Test error handling (network failure, auth expiry)

**Acceptance Criteria:**
- All test cases pass
- No data loss during uploads
- Error messages are clear and actionable
- Performance is acceptable (< 30s per file)

### Phase 6: Documentation & Rollout (Week 3)

**Documentation Updates:**
1. [ ] Update `/Users/bgerby/Desktop/medium-article-review-workflow.md`
2. [ ] Add Google Drive setup section
3. [ ] Document MCP server configuration
4. [ ] Add troubleshooting guide
5. [ ] Create team onboarding doc for Drive access

**Rollout:**
1. [ ] Enable for new articles (GAT-304+)
2. [ ] Monitor for issues
3. [ ] Backfill links for GAT-273 through GAT-303 (optional)
4. [ ] Announce to team

## MCP vs Direct API Trade-offs

| Factor | MCP Server | Direct API |
|--------|-----------|-----------|
| **Complexity** | Lower (standard interface) | Higher (custom implementation) |
| **Reusability** | High (use in other projects) | Low (specific to this workflow) |
| **Maintenance** | Community maintained | Self maintained |
| **Control** | Less (limited to MCP tools) | More (full API access) |
| **Dependencies** | MCP server + runtime | Python libraries only |
| **Performance** | MCP overhead | Direct API calls |
| **Auth Management** | MCP handles it | Self-managed OAuth |
| **Debugging** | MCP abstraction layer | Direct API errors |
| **Learning Curve** | MCP protocol knowledge | Google API knowledge |
| **Strategic Value** | Demonstrates MCP expertise | Standard integration |

**Decision:** Use MCP Server (piotr-agier/google-drive-mcp)
**Rationale:** Aligns with business model, reusable, demonstrates expertise to clients

## Technical Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Medium Email Digest                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │ extract-medium-      │
          │ articles.py          │
          │ --create-tickets     │
          │ --upload-to-drive    │
          └──────────┬───────────┘
                     │
         ┌───────────┼───────────┐
         │           │           │
         ▼           ▼           ▼
    ┌────────┐  ┌────────┐  ┌──────────┐
    │Playwright│ │  JIRA  │  │  Google  │
    │  (PDF)   │ │  API   │  │  Drive   │
    │          │ │        │  │   MCP    │
    └────┬─────┘ └────────┘  └────┬─────┘
         │                         │
         │     ┌──────────────────┐│
         │     │ generate-article-││
         └────►│ audio.py         ││
               │ --upload-to-drive││
               └──────────────────┘│
                                   │
               ┌───────────────────┘
               │
               ▼
         ┌──────────┐
         │  Google  │
         │  Drive   │
         │   MCP    │
         └──────────┘
```

### MCP Integration Flow

1. **Upload File:**
   - Script calls MCP tool: `gdrive_upload_file(path, folder_id)`
   - MCP server authenticates with OAuth
   - File uploaded to Drive
   - Returns file ID and shareable link

2. **Get Shareable Link:**
   - MCP tool: `gdrive_get_file_link(file_id)`
   - Returns public shareable URL

3. **Update JIRA:**
   - Direct JIRA REST API call (no MCP needed)
   - Update description with Drive links
   - Preserve existing content

## Security & Access Control

### Authentication
- **Google Drive**: OAuth 2.0 (user consent flow)
- **JIRA**: API token stored in `~/.jira.d/.pass`
- **MCP Server**: Runs with user credentials

### Permissions
- **Drive Folder**: Shared with `@jaxondigital.com` (View access)
- **File Links**: Anyone with link can view
- **JIRA**: Existing project permissions

### Best Practices
1. Never commit OAuth tokens to git
2. Store credentials in secure locations
3. Use service account for production (future)
4. Rotate JIRA API tokens regularly
5. Review Drive sharing permissions quarterly

## Cost Analysis

### Google Drive Storage
- **Free Tier**: 15 GB per Google Workspace account
- **Current Usage Estimate**:
  - PDFs: ~1 MB each × 15 articles/day × 30 days = ~450 MB/month
  - Audio: ~50 MB each × 5 articles/day × 30 days = ~7.5 GB/month
  - **Total**: ~8 GB/month (within free tier for now)
- **Future**: May need Google Workspace storage upgrade (~$6/user/month for 2TB)

### Development Time
- **Phase 1-2**: 8 hours (MCP setup, folder structure)
- **Phase 3**: 16 hours (script integration)
- **Phase 4**: 4 hours (JIRA format)
- **Phase 5**: 8 hours (testing)
- **Phase 6**: 4 hours (docs)
- **Total**: ~40 hours (~1 week full-time)

### Maintenance
- **Ongoing**: ~1 hour/month (monitoring, troubleshooting)
- **OAuth Token Refresh**: Automated by MCP server
- **Script Updates**: As needed for API changes

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| **MCP server bugs** | High | Test thoroughly, have API fallback ready |
| **OAuth token expiry** | Medium | Implement refresh logic, monitor errors |
| **Drive storage limits** | Medium | Monitor usage, plan for workspace upgrade |
| **JIRA API rate limits** | Low | Batch updates, implement backoff |
| **Network failures** | Medium | Retry logic with exponential backoff |
| **File naming conflicts** | Low | Use GAT number + slug for uniqueness |
| **MCP server deprecated** | High | Choose actively maintained server, have fallback |

## Success Metrics

### Quantitative
- [ ] 100% of new articles (GAT-304+) have Drive links in JIRA
- [ ] 0 upload failures per 100 articles
- [ ] < 30 seconds per file upload
- [ ] 100% team member access to Drive folders

### Qualitative
- [ ] Team finds Drive integration useful
- [ ] No manual file sharing requests
- [ ] JIRA tickets feel "complete" with all resources
- [ ] Workflow is seamless (no extra steps)

## Next Steps

1. **Immediate** (This Week):
   - Install `piotr-agier/google-drive-mcp` server
   - Set up OAuth credentials
   - Test basic upload operations

2. **Short-term** (Next 2 Weeks):
   - Integrate MCP into workflow scripts
   - Test with GAT-304+ articles
   - Update documentation

3. **Long-term** (Next Month):
   - Backfill links for GAT-273+ (optional)
   - Monitor usage and costs
   - Gather team feedback
   - Consider n8n automation (future)

## Related Resources

- **JIRA Ticket**: https://jaxondigital.atlassian.net/browse/GAT-288
- **Workflow Doc**: `/Users/bgerby/Desktop/medium-article-review-workflow.md`
- **Scripts**:
  - `/Users/bgerby/Desktop/extract-medium-articles.py`
  - `/Users/bgerby/Desktop/generate-article-audio.py`
- **MCP Servers**:
  - https://github.com/piotr-agier/google-drive-mcp
  - https://github.com/isaacphi/mcp-gdrive
  - https://github.com/felores/gdrive-mcp-server

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
