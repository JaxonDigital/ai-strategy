# GAT-170: Build Bulk Pricing Update Agent (Extend CMS MCP As Needed)

**Epic Link:** https://jaxondigital.atlassian.net/browse/GAT-170
**Parent:** GAT-168 (Strategic Pivot Plan)
**Sprint:** Sprint 3 (weeks 8-16)
**Approach:** Agent-first, MCP-second (top-down design)

## Overview

Build production agent/workflow to solve real client problem: bulk pricing update for 2026. Extend CMS MCP only as needed to support this workflow. This validates the agent-first approach: start with client problem, work down to MCP capabilities, not the reverse.

## Strategic Importance

### Why This Matters

**Differentiator from OPAL:**
- OPAL: Campaign content creation (1-10 pages)
- Jaxon: Operational content management (hundreds/thousands of items)
- Same audience (marketing), different pain point

**Revenue Model:**
- Client pays for agent/workflow (immediate revenue)
- We build MCP capabilities as needed (R&D funded by client)
- Retain IP on both agent + MCP improvements
- Productize for next client (passive revenue)

**Proves Strategic Pivot:**
- Real client paying for AI agent work
- NOT speculative MCP development
- Validates "all work builds toward platform" principle

## Real Client Use Case

**Client Need:** Bulk pricing update for 2026
- Hundreds of products on website
- All new pricing effective January 2026
- Currently: Manual updates, error-prone, time-consuming
- With Agent: Upload CSV, agent updates everything, audit trail

## Approach: Top-Down (Agent-First)

### Why Not Bottom-Up?

**❌ Bottom-Up (Old Way):**
1. Build MCP features first
2. Hope someone finds use for them
3. Risk: Build features nobody needs
4. No immediate revenue

**✅ Top-Down (New Way):**
1. Start with real client problem
2. Build n8n workflow to solve it
3. Discover what MCP capabilities are missing
4. Build ONLY what's needed
5. Result: Every MCP feature is proven useful
6. Client pays for the work

## Phases

### Phase 1: Design the Workflow
**Goal:** Understand the problem before writing code

**Tasks:**
- [ ] Interview client about pricing update process
  - How many products?
  - What fields need updating? (price, compare-at price, effective date, etc.)
  - What's the data source? (CSV, Excel, database export?)
  - What's the validation logic? (min/max prices, margin checks, etc.)
  - What could go wrong? (missing products, invalid prices, etc.)

- [ ] Map current manual process
  - How long does it take today?
  - What errors happen?
  - What would "success" look like?

- [ ] Design n8n workflow (on paper)
  - Input: CSV with product IDs + new pricing data
  - Steps: Validate → Dry-run → Preview → Apply → Verify → Notify
  - Output: All products updated, audit log, success/failure report

- [ ] Identify CMS MCP capabilities needed
  - What can current CMS MCP do?
  - What's missing?
  - Specific API calls needed

**Success Criteria:** Client approves workflow design, gaps identified

---

### Phase 2: Build MVP Workflow (Use Existing Capabilities)
**Goal:** Prove workflow with what CMS MCP can already do

**Tasks:**
- [ ] Set up n8n instance (local or n8n Cloud)
- [ ] Build workflow using existing CMS MCP capabilities
- [ ] Test with small dataset (10 products)
- [ ] Document what works
- [ ] Document what doesn't work (the gaps)

**Success Criteria:**
- Can update 10 products successfully
- Clear list of CMS MCP gaps preventing scale

---

### Phase 3: Extend CMS MCP (Only What's Needed)
**Goal:** Add missing capabilities to CMS MCP, nothing more

**Tasks:**
- [ ] Audit existing CMS MCP v1 codebase
- [ ] Prioritize gaps (what's blocking bulk pricing update?)
- [ ] Implement missing capabilities:
  - Bulk read operations (get multiple products efficiently)
  - Bulk write operations (update multiple items in one call)
  - Field-level updates (change price without touching other fields)
  - Dry-run mode (preview changes without applying)
  - Transaction support (rollback on error)
  - Rate limiting (don't overwhelm CMS API)

- [ ] Add HTTP/SSE transport (if not already there)
- [ ] Test with n8n workflow
- [ ] Document new capabilities

**Success Criteria:**
- CMS MCP can support bulk pricing workflow
- No "nice to have" features built (only what's needed)

---

### Phase 4: Production Workflow
**Goal:** Build complete, production-ready workflow

**Tasks:**
- [ ] Enhanced n8n workflow with full capabilities:
  - CSV upload and parsing
  - Data validation (price ranges, required fields)
  - Dry-run preview (show what will change)
  - User confirmation step
  - Bulk update execution
  - Progress tracking (N of M complete)
  - Error handling (rollback on failure)
  - Success verification (confirm all updates)
  - Audit logging (who, what, when)
  - Slack/email notifications

- [ ] Build admin UI (simple web form or Slack bot)
  - Upload CSV
  - View dry-run results
  - Approve/reject changes
  - Monitor progress
  - View audit logs

- [ ] Testing
  - Test with 500+ products in staging
  - Load testing (can it handle 1000+ items?)
  - Error scenarios (bad data, API failures, network issues)
  - Rollback testing

**Success Criteria:**
- Can update 500+ products reliably
- Zero data loss, full audit trail
- Client can self-service (with guardrails)

---

### Phase 5: Deploy for Client (2026 Pricing Update)
**Goal:** Solve the real problem, gather metrics, create case study

**Tasks:**
- [ ] Production deployment
  - Deploy CMS MCP to hosted infrastructure (GAT-169)
  - Deploy n8n workflow
  - Configure client credentials
  - Set up monitoring

- [ ] Client training
  - How to upload CSV
  - How to review dry-run
  - How to approve changes
  - What to do if something goes wrong

- [ ] Execute 2026 pricing update
  - Client uploads pricing CSV
  - Dry-run and preview
  - Client approves
  - Agent executes
  - Verify success

- [ ] Gather metrics
  - Time saved vs manual process
  - Errors avoided
  - Accuracy improvement
  - Client satisfaction

**Success Criteria:**
- 2026 pricing update completed successfully
- Client testimonial obtained
- Metrics documented for case study

---

### Phase 6: Productize & Market
**Goal:** Turn this into reusable product for other clients

**Tasks:**
- [ ] Extract reusable patterns
  - Generic "Bulk Content Update Agent" template
  - Works for pricing, but also: inventory, descriptions, images, etc.
  - Configurable for different content types

- [ ] Create case study
  - "How we updated 500 product prices in 30 minutes with AI"
  - Before/after metrics
  - Client testimonial
  - Technical architecture (without revealing secrets)

- [ ] Blog post
  - Position vs OPAL: "Operational content vs campaign content"
  - Why marketing teams need bulk operations
  - How we built it (agent-first approach)

- [ ] Open source decision
  - Keep CMS MCP improvements private? Or open source?
  - Agent/workflow: Always proprietary (this is the product)

- [ ] Add to Platform tier offering
  - "Bulk Content Operations Agent" as standard feature
  - Include in self-service dashboard
  - Pricing: Included in $25-50K/year platform tier

**Success Criteria:**
- Reusable template documented
- Case study published
- Second client interested in bulk operations agent
- Added to Platform tier offering

## Technical Architecture

### Components

```
┌─────────────────────────────────────────┐
│  Client (Marketing Team)                │
│  ┌──────────────────────────────┐       │
│  │ Upload CSV                    │       │
│  │ Review Dry-Run                │       │
│  │ Approve Changes               │       │
│  └──────────────────────────────┘       │
└─────────────┬───────────────────────────┘
              │
              ↓
┌─────────────────────────────────────────┐
│  n8n Bulk Pricing Agent                 │
│  ┌──────────────────────────────┐       │
│  │ Parse CSV                     │       │
│  │ Validate Data                 │       │
│  │ Call CMS MCP (dry-run)        │       │
│  │ Show Preview                  │       │
│  │ Wait for Approval             │       │
│  │ Call CMS MCP (execute)        │       │
│  │ Verify Success                │       │
│  │ Send Notifications            │       │
│  └──────────────────────────────┘       │
└─────────────┬───────────────────────────┘
              │ HTTP/SSE
              ↓
┌─────────────────────────────────────────┐
│  CMS MCP (Extended)                     │
│  ┌──────────────────────────────┐       │
│  │ Bulk Read Products            │       │
│  │ Validate Changes              │       │
│  │ Dry-Run Mode (preview)        │       │
│  │ Bulk Update (atomic)          │       │
│  │ Rollback on Error             │       │
│  │ Audit Logging                 │       │
│  └──────────────────────────────┘       │
└─────────────┬───────────────────────────┘
              │ Optimizely Content API
              ↓
┌─────────────────────────────────────────┐
│  Optimizely CMS                         │
│  (Client's Content Database)            │
└─────────────────────────────────────────┘
```

### Key Technical Decisions

**Why n8n for the agent?**
- Visual workflow builder (easy to modify)
- Built-in error handling and retries
- Can connect to CMS MCP via HTTP/SSE
- Client can see the workflow (transparency)

**Why extend CMS MCP vs building in n8n?**
- CMS MCP is the reusable component (productizable)
- n8n workflow is the client-specific orchestration
- Other agents can use same CMS MCP capabilities

**Why dry-run mode is critical?**
- Bulk operations are scary (what if something breaks?)
- Preview builds trust
- Catches errors before they're applied

## Success Metrics

### Client Success
- ✅ 2026 pricing update completed on time
- ✅ Zero pricing errors
- ✅ Time saved: 80%+ vs manual process
- ✅ Client would recommend to others

### Business Success
- ✅ Client pays for development (immediate revenue)
- ✅ IP retained for productization
- ✅ Reusable for other bulk operations (inventory, descriptions, etc.)
- ✅ Included in Platform tier ($25-50K/year recurring)

### Technical Success
- ✅ CMS MCP production-ready (hosted, monitored)
- ✅ Agent-first approach validated (top-down works)
- ✅ Can provision bulk operations agent for new client in <1 day

### Strategic Success
- ✅ Differentiated from OPAL (operational vs campaign)
- ✅ Proves "all work builds platform" principle
- ✅ Case study for sales/marketing
- ✅ Blog post establishes thought leadership

## Risks & Mitigations

**Risk:** Optimizely CMS API can't handle bulk operations efficiently
**Mitigation:** Test with staging data early, optimize queries, add caching if needed

**Risk:** Client data has edge cases we didn't anticipate
**Mitigation:** Start with small dataset, iterate based on real data

**Risk:** Pricing update fails mid-execution (partial update)
**Mitigation:** Transaction support in CMS MCP, rollback capability, dry-run first

**Risk:** Building too much (scope creep into "nice to have" features)
**Mitigation:** Strict focus on bulk pricing use case, say no to extras

**Risk:** CMS MCP v1 codebase is too stale to extend
**Mitigation:** Budget for rewrite if needed, but try to salvage what's there first

## Timeline

**Week 1-2: Phase 1 (Design)**
- Client interviews, workflow design
- Gap analysis (what CMS MCP needs)

**Week 3-4: Phase 2 (MVP)**
- Build workflow with existing capabilities
- Document gaps

**Week 5-7: Phase 3 (Extend CMS MCP)**
- Implement missing capabilities
- Test with workflow

**Week 8-10: Phase 4 (Production Workflow)**
- Complete n8n workflow
- Build admin UI
- Testing

**Week 11-12: Phase 5 (Deploy)**
- Production deployment
- Client training
- Execute 2026 pricing update

**Week 13-14: Phase 6 (Productize)**
- Case study, blog post
- Reusable template
- Add to Platform offering

**Total: 14 weeks (fits in Sprint 3: weeks 8-16 of overall plan)**

## Related Tickets

- **GAT-168:** Strategic Pivot Plan (parent epic)
- **GAT-169:** Hosting Architecture (CMS MCP needs to be hosted)
- **GAT-157:** python-a2a article (production agent patterns)

## Next Actions

1. Get client approval to proceed (pricing update agent)
2. Schedule client interview (understand requirements)
3. Audit CMS MCP v1 codebase (what exists today?)
4. Design workflow on paper (before writing code)
5. Begin Phase 1

---

**Key Insight:** This ticket validates the strategic pivot. Client pays for agent development, we retain IP for productization, and every MCP feature we build is proven useful. This is how we build a product while doing services.
