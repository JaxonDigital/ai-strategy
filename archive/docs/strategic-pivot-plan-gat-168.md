# Strategic Pivot Plan: Transform Jaxon Digital into Product-Led AI Business
**JIRA Epic:** GAT-168
**Created:** October 12, 2025

## Core Vision
Transform from services-heavy Optimizely consultancy to product-led business with passive revenue streams. Build autonomous agents once, sell many times. Own the "Autonomous Operations for Optimizely" category.

**Key Principle:** Inbound demand - clients come to us begging for what we offer, not the opposite.

## 12-Month Revenue Target
- **50% Services** ($500K): Traditional retainer/hourly work (with AI assistance reducing delivery costs)
- **25% Managed Services** ($250K): White-glove agent operations (3-5 clients at $50-80K/year)
- **25% Platform/SaaS** ($250K): Enterprise self-service (5-10 clients at $25-50K/year)

## Three-Tier Offering

### 1. Traditional Services ($500K/year)
- Keep existing retainer clients happy
- Use AI/agents internally to reduce delivery costs and increase margins
- **CRITICAL:** ALL work must build toward platform/agents (no "straight non-AI work")
- Use as testing ground for agent capabilities

### 2. Managed Agent Operations ($250K/year)
**Target:** 3-5 existing clients at $50-80K/year
**Model:** White-glove setup, custom configuration, ongoing operations
- We configure agents for client's specific needs
- We operate and monitor agents 24/7
- We report on performance and cost savings
- We continuously optimize and improve
- **IP Strategy:** Jaxon retains IP, client gets perpetual license to use
- Custom work subsidizes product development

### 3. Platform/SaaS - Enterprise Tier ($250K/year)
**Target:** 5-10 clients at $25-50K/year ($2-4K/month)
**Model:** Self-service onboarding with enterprise-grade hosting
- Multi-tenant hosted MCPs (DXP, Log Analyzer, CMS)
- Pre-built agents (deployment, monitoring, content operations)
- Self-service dashboard for configuration
- Enterprise support (responsive, not white-glove)
- Client configures, we host, we support
- SLAs, security, compliance, audit logs

## Positioning Strategy

### Optimizely OPAL Differentiation
**VALIDATED AT OPTICON 2025 (October 2025)**

**Key Insight:** Both target marketing departments, but different pain points within marketing.

- **OPAL Focus:** Marketing Campaign Operations
  - Campaign content creation, A/B testing, experimentation
  - UI variations, personalization at scale
  - "Agentic editing" for campaign content (future)
  - Competes with ChatGPT Enterprise, Copilot
  - Requires Opti ID + Optimizely Graph (vendor lock-in)
  - **Target users:** Marketing campaign managers, content creators for campaigns

- **Jaxon Focus:** Website Operations for Marketing Teams
  - Deployment automation (Thursday night deployments)
  - Bulk content operations (pricing updates, product migrations)
  - Site monitoring, log analysis, infrastructure health
  - Content management at scale (update 50 pages, not write 1 campaign)
  - No direct competitors in Optimizely ecosystem
  - Open MCPs, MCP protocol (less proprietary)
  - **Target users:** Marketing web managers, digital experience teams, marketing ops managing websites

- **Relationship:** Complementary, same audience but different jobs ✅ CONFIRMED
  - Both sell to marketing departments
  - OPAL: "I need to run a campaign with 10 variations"
  - Jaxon: "I need to deploy on Thursday night" or "I need to update 500 product prices"
  - Different pain points, different workflows

- **CMS MCP: Critical Differentiator**
  - **Real Example:** Client needs bulk pricing update for 2026 (hundreds of products)
  - **OPAL approach:** Agentic editing for campaign content (1-10 pages)
  - **Jaxon CMS MCP:** Bulk content operations at scale (hundreds/thousands of items)
  - **Use case:** Marketing teams responsible for website content, not just campaigns

- **Target Client Profile:**
  - Marketing stakeholders who OWN the website
  - Responsible for content updates, site operations
  - NOT heavily involved in campaigns/experimentation
  - Pain: Operational burden of website management (deployments, bulk updates, monitoring)

- **Acquisition Angle:** Jaxon solves website operations pain that marketing teams feel but OPAL doesn't address

### Market Position
- Own category: "Autonomous Operations for DXP Platforms"
- Starting point: Dominate Optimizely agent space
- Expansion Path A: Custom agents for existing clients (retain IP, productize)
- Expansion Path B: Pick another platform vertical (Sitecore? Contentful? Azure DevOps?)

### IP Strategy
- **DXP MCP:** Open source (thought leadership, community building)
- **Future MCPs:** Selective open source (case-by-case basis)
- **Agent Orchestration:** Proprietary
- **Client Contracts:** Jaxon retains IP, client gets perpetual license
- Build once for Client A, sell many times to Clients B, C, D

## Current State (October 2025)

### What's Real and Working Today
- ✅ **DXP MCP:** Open source, production use (internal + external users), local execution
- ✅ **Log Analyzer MCP:** Private repo, production use (internal), local execution
- ✅ **HTTP/SSE support:** Added to both MCPs for n8n integration
- ⚠️ **CMS MCP:** Built v1, but stale (not actively used) - **CRITICAL TO REFRESH**
  - Real client need: Bulk pricing update for 2026 (hundreds of products)
  - Differentiator from OPAL (campaign content vs operational content)
  - Marketing teams need this for website management

### What's In Progress
- 🚧 **Production Deployment Agent (n8n):** Solves off-hours deployment babysitting + log analysis
- 🚧 Not in production yet, plan to use for all client deployments moving forward
- 🚧 Blog post drafted: "Clockwork Deployments to AI" (ready to publish when agent is production-ready)

### What Doesn't Exist Yet
- ❌ Hosted MCP infrastructure (multi-tenant or otherwise)
- ❌ Production-ready agent operations
- ❌ Managed service platform
- ❌ Multiple agents running autonomously

### The Reality
"We are at the beginning of some very cool and very real stuff but there is a lot of work to go to make everything all production ready"

**BUT:** AI/MCP ecosystem is moving rapidly. First-mover advantage is critical. Must establish position NOW before competitors claim it.

## Execution Timeline

### Sprint 1 (Next 2-4 weeks)
- [ ] Complete deployment agent testing
- [ ] First autonomous production deployment (internal)
- [ ] Publish "Clockwork Deployments to AI" blog post
- [ ] Deploy agent for 1-2 existing clients
- [ ] Gather initial metrics (hours saved, deployment success rate)

### Sprint 2 (Weeks 4-8)
- [ ] Build hosted MCP infrastructure (Azure Container Apps)
- [ ] Multi-tenant architecture operational
- [ ] Security, audit logging, secret management
- [ ] Package "Managed Agent Operations" offering
- [ ] Finalize pricing/packaging for all three tiers
- [ ] Create sales materials (decks, pricing sheets, SOWs)

### Sprint 3 (Weeks 8-16)
- [ ] Offer managed services to all existing retainer clients
- [ ] Build 2-3 additional agent types (monitoring, content, etc.)
- [ ] Refresh and release CMS MCP
- [ ] Publish first case study (deployment agent success)
- [ ] Launch self-service platform MVP
- [ ] Outbound strategy for 5-10 platform customers

### 6-Month Milestone (April 2026)
- Existing client base migrated to managed or platform tier
- Platform proven, documented, productized
- Marketing materials complete (case studies, demo videos, pricing)
- Active outbound/inbound strategy for platform customers
- Revenue starting to shift toward managed/platform tiers

### 12-Month Success Criteria (October 2026)
- ✅ Revenue split achieved: 50% services / 25% managed / 25% platform
- ✅ 3-5 clients on managed service tier ($50-80K/year each)
- ✅ 5-10 clients on platform/SaaS tier ($25-50K/year each)
- ✅ Multiple agent types in production (deployment, monitoring, content, security)
- ✅ Positioned as "the Optimizely AI operations company"
- ✅ Inbound demand from blog content, open source presence, ecosystem
- ✅ Acquisition-ready: Clear product, recurring revenue, proven with multiple clients

## Critical Success Factors

### Speed to Market
- AI/MCP ecosystem moving rapidly
- First-mover advantage is critical
- Competitors entering Optimizely agent space
- Must establish position NOW before others claim it
- Example: We held back on CMS MCP, someone else created one
- DXP MCP: Released quickly, 14,000+ downloads, established thought leadership

### Product vs Services Balance
- Every client engagement produces reusable components
- Resist temptation to do "straight non-AI work"
- ALL traditional work must advance the platform
- Use retainer work as testing ground for agent capabilities

### Agent-First Development Methodology
**Top-Down Approach (NOT Bottom-Up)**

**✅ Correct Way: Start with Agent/Workflow, Work Down to MCP**
1. Identify real client problem (e.g., bulk pricing update)
2. Build n8n workflow/agent to solve it
3. Discover what MCP capabilities are missing
4. Build ONLY what's needed for that workflow
5. Client pays for agent, we retain IP on MCP improvements
6. Productize for next client

**❌ Wrong Way: Start with MCP, Hope Someone Uses It**
1. Build MCP features speculatively
2. Hope someone finds use for them
3. Risk building features nobody needs
4. No immediate revenue, speculative R&D

**Why Top-Down Works:**
- Client-funded R&D (they pay for agent development)
- Every MCP feature is proven useful (not speculative)
- Immediate revenue + IP retention = best of both worlds
- Validates product-market fit before scaling

**Example:** GAT-170 (Bulk Pricing Update Agent)
- Client needs bulk pricing update for 2026
- Build agent first, extend CMS MCP as needed
- Client pays for agent, we keep MCP improvements
- Productize as "Bulk Content Operations Agent" for Platform tier

### Revenue Model Transformation
- Success = passive income streams
- Get paid for building agents once, selling many times
- Exponential gains vs 1-for-1 hourly work
- Platform revenue while you sleep
- **Goal:** "I would love to be able to host this deployment agent in a saas form of some sort, have people sign up to use it with some payment model and we get paid for every time it runs or by month or by x but we get exponential gains"

### Market Ownership
- Define unique view of autonomous DXP operations
- Own that market outright
- Become THE authority clients seek out
- No begging for work - create demand pull
- "I want customers coming to us begging for what we have to offer, not the opposite"

## Acquisition Strategy

**Target Acquirer:** Optimizely (or other DXP platform vendor)
**Timeline:** 18-24 months to acquisition readiness

**Why We're Attractive:**
- Solving operations pain point they haven't tackled (complement to OPAL)
- Proven product with recurring revenue (not just services)
- Active ecosystem/community around open source MCPs
- De-risked with multiple enterprise clients
- Clear differentiation: They do AI for marketers (OPAL), we do AI for operations

**Alternative Path:**
Become independent platform business (like how Netlify dominates Jamstack deployments) - cross-platform DXP operations

## Expansion Strategy

### Phase 1: Dominate Optimizely
- Build full suite of Optimizely agents (deployment, monitoring, content, security, etc.)
- Own "Autonomous Operations for Optimizely" category
- Become the default choice for Optimizely + AI

### Phase 2: Expand Scope
**Option A:** Custom agents for existing clients
- Build bespoke agents for client-specific systems
- Retain IP, productize for others
- "We work with some customers to build things for them but we keep the ip to be able to productize them for others"

**Option B:** Pick another platform vertical
- Apply same playbook to Sitecore, Contentful, Adobe, etc.
- "We dominate that space and then create other custom agents for clients or we pick another market to dominate"

**Option C:** Cross-platform DXP operations
- Abstract away platform-specific details
- Become THE autonomous operations platform for any DXP

## Key Decisions Made

### Revenue Split (12 months)
50% Services / 25% Managed / 25% Platform

### Platform Pricing
NOT high-volume/low-price (25-50 customers at $5-10K/year)
YES enterprise/lower-volume (5-10 customers at $25-50K/year)
- Aligns with Jaxon's DNA (enterprise relationships, not SMB)
- "We probably need to have less customers that pay more"

### Client Acquisition
- First clients: Existing retainer clients (trust already established)
- Second clients: Existing Optimizely customers looking to streamline operations or interested in AI
- NOT focusing on: High-volume new client acquisition (not Jaxon's strength)
- "Landing just 1 for us is a big deal"

### Services vs Product Evolution
**Phase 1 (Now - 6 months):** Services-led product development
- Build for internal use, deploy for clients as managed service
- Charge setup + recurring, retain IP

**Phase 2 (6-12 months):** Productization
- Extract common patterns, build self-service layer
- Two tiers: Managed (white-glove) + Self-Service (enterprise)

**Phase 3 (12-24 months):** Platform scale
- Self-service becomes dominant revenue stream
- Usage-based pricing
- Majority of revenue is recurring platform fees

### Technology Choices
- **Agent Runtime:** Multiple platforms (n8n primary, python-a2a for some use cases, OpenAI Agent Builder for others)
- **MCP Hosting:** Azure Container Apps (multi-tenant)
- **IP Strategy:** Selective open source (DXP MCP already open, orchestration proprietary)

## Next Actions
1. ✅ Review and approve this strategic plan
2. [ ] Break into actionable tickets (infrastructure, product, marketing)
3. [ ] Assign owners and timelines
4. [ ] Begin Sprint 1 execution (deployment agent to production)
5. [ ] Weekly check-ins on progress toward 12-month targets
6. [ ] Research Optimizely OPAL (capabilities, agent model, positioning)

## Related Tickets
- GAT-157: Review python-a2a article (production MCP deployment pattern) - **High Priority**
- GAT-166: Hosting Architecture Decision (Azure Container Apps multi-tenant)
- Additional tickets to be created for Sprint 1-3 work

---

**This is the transformation:** From Optimizely consultancy to AI operations platform. From trading hours for dollars to building assets that generate passive revenue. From chasing clients to owning a market.

Let's build it.
