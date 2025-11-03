# GAT-171: Strategic Enablement - Go-to-Market, Positioning, Team & Legal

**Epic Link:** https://jaxondigital.atlassian.net/browse/GAT-171
**Parent:** GAT-168 (Strategic Pivot Plan)
**Created:** October 13, 2025

## Overview

Strategic enablement work to support the services-to-product pivot (GAT-168). While execution teams build the technical platform (MCPs, agents, hosting), we need to enable the business side: positioning, marketing, sales, team learning, legal frameworks, and public-facing messaging.

**Key Principle:** Strategy work happens here, execution happens in parallel elsewhere.

---

## Workstream 1: Positioning & Messaging

**Goal:** Define who we are, what we sell, and how we talk about it consistently across all touchpoints.

### Core Questions to Answer

1. **Who is Jaxon Digital?** (Identity/category)
   - Are we: "Optimizely agency with AI" or "AI operations company for DXP"?
   - Category positioning: What bucket do prospects put us in?
   - Elevator pitch: 1-2 sentences that make sense to strangers

2. **What do we sell?** (Offering)
   - Three tiers: Traditional Services, Managed Agent Operations, Platform/SaaS
   - How do we describe each tier in prospect-friendly language?
   - What's the "headline offering" that gets attention?

3. **Who do we sell to?** (Audience)
   - Primary: Marketing teams who own website operations
   - Secondary: IT/DevOps teams managing DXP infrastructure
   - Personas: Job titles, pain points, buying authority

4. **Why us vs alternatives?** (Differentiation)
   - vs Traditional Optimizely agencies (human hours vs autonomous agents)
   - vs Generic AI automation platforms (domain expertise vs generic tools)
   - vs Optimizely OPAL (operations vs campaigns)
   - vs DIY/in-house (proven patterns vs starting from scratch)
   - vs Other CMS MCPs (enterprise DXP/PaaS vs headless SaaS focus)

5. **What's our proof?** (Credibility)
   - Open source DXP MCP (14K+ downloads, 4 continents)
   - **Microsoft MCP adoption** (Microsoft added native MCP support to Windows - validates technology choice)
   - Real production deployments (our own + client Thursday night deployments)
   - Deep Optimizely expertise (Gold Partner, 8 years, 30+ sites)
   - Technical thought leadership (blog posts, GitHub community)
   - **Early MCP ecosystem leader** (building MCPs while Microsoft adoption just starting)

### Deliverables

**Phase 1: Core Positioning Document**
- [ ] Positioning statement (who/what/why)
- [ ] Value proposition for each tier
- [ ] Differentiation matrix (us vs alternatives)
- [ ] Messaging framework (key messages, proof points, objection handling)
- [ ] Audience personas (3-5 detailed profiles)

**Phase 2: Apply to Touchpoints**
- [ ] **LinkedIn Company Page** - Update company description, featured content
- [ ] **LinkedIn Personal Profiles** - Brian's profile, team member profiles
- [ ] **Optimizely Partner Page** - Update partner profile with AI positioning
- [ ] **Website Copy** - Homepage, About, Services pages (for Optimizely transition)
- [ ] **MCP README Files** - DXP MCP, Log Analyzer MCP, CMS MCP
- [ ] **Sales One-Pager** - 1-page PDF for sales conversations
- [ ] **Pitch Deck** - 10-15 slides for prospect meetings

**Phase 3: Content Strategy**
- [ ] Blog post calendar (topics, cadence, distribution)
- [ ] Case study template (for bulk pricing agent, deployment agent)
- [ ] Social media guidelines (what to share, how to talk about it)

### Key Decisions Needed

**Positioning Choice:**
- Option A: "AI-powered Optimizely agency" (safe, familiar)
- Option B: "Autonomous operations platform for Optimizely" (bold, differentiated)
- Option C: "We make your DXP run itself" (outcome-focused)

**Messaging Tone:**
- Technical vs business-friendly?
- Bold/provocative vs conservative/safe?
- "We're the future" vs "We're proven and reliable"

**OPAL Positioning:**
- Acknowledge OPAL explicitly? ("OPAL for campaigns, Jaxon for operations")
- Ignore OPAL entirely? (Different swim lanes)
- Partner positioning? ("Complements Optimizely OPAL")

**SaaS vs PaaS Focus:**
- **Primary: Optimizely DXP/PaaS** (enterprise, includes hosting, Azure-based, all current clients)
- **Secondary: Optimizely SaaS/Headless** (support planned, but knowledge/customers all PaaS now)
- **Differentiation:** Enterprise operations at scale vs individual headless CMS management
- **Market segmentation:** Most competitors target SaaS/headless, Jaxon targets DXP/PaaS enterprise

### Competitive Landscape (CMS MCPs)

**Discovery (Oct 13, 2025):** Johnny Mullaney (First3Things) has competing CMS MCP gaining visibility

**Key Findings:**
- **Target Market:** Johnny targets Optimizely SaaS (headless/Content Graph), Jaxon targets DXP/PaaS
- **Architecture:** Johnny uses stdio/local (despite "multi-tenant" claims), Jaxon building HTTP/SSE multi-tenant
- **Maturity:** Johnny is beta/active development, Jaxon has v1 but needs refresh
- **Client Overlap:** MINIMAL - All Jaxon clients are DXP/PaaS, Johnny targets SaaS/headless

**Strategic Implications:**
1. **Not direct competitors** - Different market segments (enterprise PaaS vs headless SaaS)
2. **Should support both eventually** - But PaaS is current focus (all clients, all knowledge)
3. **Differentiation:** Enterprise bulk operations at scale vs single-instance headless management
4. **Positioning:** "Enterprise DXP Operations" (not just "CMS automation")

**Action Items:**
- GAT-188: Competitive analysis (market segmentation, threat assessment)
- GAT-189: Feature comparison (identify gaps and opportunities)
- GAT-190: Code review (learn from implementation patterns)
- Emphasize DXP/PaaS enterprise focus in all positioning

---

## Workstream 2: Marketing & Sales Strategy

**Goal:** Get existing clients to spend more + attract net-new clients.

### Part A: Existing Client Upsell Strategy

**Objective:** Convert existing retainer clients to Managed Agent Operations ($50-80K/year)

**Target Clients:**
- [List current retainer clients]
- Which are best candidates for AI services?
- Which have pain points we can solve? (deployments, bulk content ops, monitoring)

**Approach:**
1. **Pilot Program** (Q4 2025)
   - Pick 1-2 friendly clients for "AI Retainer Pilot"
   - Offer discounted rate for early adopters
   - Use as case studies for other clients

2. **Annual Renewal Pitch** (Q1 2026)
   - As retainers renew, present "AI-focused retainer" option
   - Show cost savings: Autonomous ops vs human hours
   - Emphasize innovation: "Be ahead of the curve"

3. **Specific Pain Point Campaigns**
   - Deployment automation: "Get your Thursday nights back"
   - Bulk content operations: "2026 pricing update in 30 minutes"
   - Monitoring: "Know about errors before your customers do"

**Deliverables:**
- [ ] Client segmentation (who's ready for AI services?)
- [ ] Pilot program design (scope, pricing, timeline)
- [ ] Renewal pitch deck (AI retainer vs traditional retainer)
- [ ] Pain point campaigns (email templates, sales scripts)
- [ ] ROI calculator (time saved, cost savings)

### Part B: Net-New Client Acquisition

**Objective:** Attract 5-10 new clients for Platform/SaaS tier ($25-50K/year)

**Target Profile:**
- Mid-to-large companies with Optimizely **DXP/PaaS** (enterprise platform)
- Pain: DXP operational overhead (deployments, monitoring, bulk content operations)
- Buying authority: Marketing web managers, IT/DevOps, digital experience teams
- Annual Optimizely spend: $100K+ (indicates sophistication)
- **Note:** All current Jaxon clients are DXP/PaaS; expand to SaaS/headless later

**Channels:**

1. **Inbound (Primary Focus)**
   - Blog content (technical deep dives, case studies)
   - Open source MCPs (GitHub presence, downloads, community)
   - Speaking: Optimizely conferences, webinars
   - SEO: "Optimizely deployment automation", "AI for DXP operations"
   - LinkedIn: Thought leadership posts, company updates

2. **Outbound (Secondary)**
   - Warm intros: Existing client referrals, Optimizely partner network
   - LinkedIn outreach: Target personas at companies with Optimizely
   - Optimizely partner channel: Co-marketing with Optimizely

3. **Partnerships**
   - Optimizely SI partners: White-label agent operations?
   - Other DXP partners: Expand beyond Optimizely (Sitecore, Contentful)
   - Technology partners: n8n, Azure, AI vendors

**Deliverables:**
- [ ] Ideal customer profile (ICP) document
- [ ] Content marketing plan (blog topics, publishing cadence)
- [ ] SEO keyword strategy (what prospects search for)
- [ ] LinkedIn content calendar (thought leadership posts)
- [ ] Partner outreach strategy (Optimizely, SI partners)
- [ ] Inbound lead process (website → demo → close)

### Part C: Sales Process & Materials

**Sales Motion:**
1. **Discovery** - Understand pain points, current process, budget
2. **Demo** - Show agent in action (deployment agent, bulk content ops)
3. **Pilot/POC** - Small paid pilot to prove value
4. **Proposal** - SOW for managed services or platform subscription
5. **Close** - Sign contract, onboard to platform

**Materials Needed:**
- [ ] Sales playbook (discovery questions, qualification criteria)
- [ ] Demo scripts (what to show, how to position)
- [ ] Proposal templates (managed services SOW, platform subscription)
- [ ] Pricing calculator (inputs: # of deploys, # of products, etc.)
- [ ] Case studies (bulk pricing update, deployment automation)
- [ ] ROI calculator (show value vs cost)
- [ ] Competitive battlecards (us vs alternatives)

---

## Workstream 3: Team Learning & Development Plan

**Goal:** Entire team learns how to build and deliver AI agents + MCPs.

### Current Team Skills (Assumptions)

**Strong Areas:**
- Optimizely CMS/Commerce/DXP expertise
- Azure DevOps, CI/CD pipelines
- C#/.NET development
- Client services, project management

**Learning Needed:**
- MCP protocol and development
- n8n workflow design
- Agent orchestration patterns
- Prompt engineering for agents
- AI operations monitoring
- Hosting/DevOps for multi-tenant platforms

### Learning Tracks

**Track 1: MCP Development (Developers)**
- [ ] MCP protocol fundamentals
- [ ] Building custom MCPs (TypeScript/Node)
- [ ] SSE transport implementation
- [ ] Testing MCPs with Claude Desktop
- [ ] Production MCP patterns (python-a2a, hosting)
- **Resources:** Official MCP docs, GAT-157 (python-a2a article), existing DXP/Log Analyzer MCPs

**Track 2: Agent Development (Developers + PMs)**
- [ ] n8n fundamentals and workflow design
- [ ] Agent-first development methodology
- [ ] Connecting n8n to MCPs (HTTP/SSE)
- [ ] Error handling and retries
- [ ] Monitoring and observability
- **Resources:** n8n docs, GAT-170 (bulk pricing agent), deployment agent codebase

**Track 3: Prompt Engineering (Everyone)**
- [ ] Writing effective prompts for agents
- [ ] Chain-of-thought reasoning
- [ ] Tool use patterns
- [ ] Debugging agent behavior
- **Resources:** Anthropic prompt library, OpenAI cookbook

**Track 4: Operations & Hosting (DevOps)**
- [ ] Multi-tenant architecture patterns
- [ ] Container orchestration (Docker, Azure Container Apps)
- [ ] Secrets management (Azure Key Vault)
- [ ] Monitoring and logging (App Insights, Datadog)
- [ ] Cost tracking and optimization
- **Resources:** GAT-169 (hosting architecture), Railway/Render docs

**Track 5: AI Strategy & Sales (Leadership + Client-Facing)**
- [ ] AI landscape and trends
- [ ] Agent vs automation positioning
- [ ] Competitive landscape (OPAL, generic platforms)
- [ ] ROI storytelling and case studies
- [ ] Handling client concerns (security, reliability, cost)
- **Resources:** GAT-168 (strategic pivot plan), this document

### Learning Deliverables

- [ ] **Learning Path Documents** - One per track with resources, exercises, checkpoints
- [ ] **Internal Wiki/Docs** - Confluence or Notion workspace with all learning materials
- [ ] **Hands-On Labs** - Build a simple MCP, build a simple agent, deploy to Railway
- [ ] **Weekly Knowledge Shares** - Team members present what they learned
- [ ] **Certification/Checkpoints** - How do we know someone is ready to deliver?

### Team Development Approach

**Option A: Everyone Learns Everything (Slow but Comprehensive)**
- All team members go through all learning tracks
- Pros: Full team can support any aspect
- Cons: Time-consuming, not everyone needs every skill

**Option B: Role-Based Specialization (Fast but Siloed)**
- Developers focus on MCP/agent tracks
- PMs focus on workflow design and strategy
- DevOps focus on hosting and operations
- Pros: Faster to competency
- Cons: Risk of silos, dependencies on individuals

**Option C: T-Shaped (Recommended)**
- Everyone learns foundations (MCP basics, agent concepts, strategy)
- Deep specialization in 1-2 areas based on role
- Pros: Shared vocabulary, but efficient specialization
- Cons: Requires good coordination

**Recommendation:** Option C (T-Shaped)

---

## Workstream 4: Legal & Contracts

**Goal:** New agreements for AI services, IP retention, managed services model.

### Current Contract Structure (Assumptions)

**What We Probably Have:**
- Master Services Agreement (MSA) for retainer clients
- Statements of Work (SOWs) for projects
- Standard IP clauses (work-for-hire vs retained IP)
- Hosting/SLA language (if applicable)

**What We Need for AI Services:**

### New Legal Requirements

**1. IP Retention Language**
- **Critical:** Jaxon retains IP on MCPs and agent logic
- **Client gets:** Perpetual license to use for their operations
- **Why:** Allows us to productize for other clients
- **Language needed:** "Client-funded R&D with IP retention"

**Example Clause:**
> "Jaxon Digital retains all intellectual property rights to MCPs, agent workflows, and automation logic developed under this agreement. Client receives a perpetual, non-exclusive license to use such IP for Client's internal operations. Jaxon may reuse, modify, and license such IP to other clients."

**2. Managed Services SLA**
- **Uptime guarantees:** 99.9% for hosted MCPs? 99.5%?
- **Response times:** How fast do we respond to incidents?
- **Maintenance windows:** When can we take systems down?
- **Liability caps:** What's our maximum liability if things break?

**3. Data & Security**
- **Data handling:** Client provides API keys, we store securely
- **Multi-tenant isolation:** How do we guarantee tenant separation?
- **Compliance:** SOC2? GDPR? HIPAA? (depends on client needs)
- **Data retention:** How long do we keep logs, audit trails?

**4. Usage-Based Pricing Terms**
- **Metering:** How do we measure usage? (deployments, API calls, etc.)
- **Billing:** Monthly invoicing based on usage
- **Overages:** What happens if client exceeds limits?
- **Rate changes:** Can we adjust pricing? How much notice?

**5. Service Termination**
- **What happens to client data?** Export process, timelines
- **What happens to hosted agents?** Transition period, migration support
- **IP licensing post-termination:** Does license continue?

### Contract Templates Needed

**Template 1: Managed Agent Operations SOW**
- [ ] Scope: Which agents, which operations
- [ ] Pricing: Setup fee + monthly recurring
- [ ] IP retention clauses
- [ ] SLA terms (uptime, response times)
- [ ] Data/security provisions
- [ ] Termination terms

**Template 2: Platform/SaaS Subscription Agreement**
- [ ] Self-service tier terms
- [ ] Usage-based pricing
- [ ] Multi-tenant hosting terms
- [ ] SLA (lower than managed services?)
- [ ] Data handling and security
- [ ] Cancellation policy

**Template 3: Pilot/POC Agreement**
- [ ] Limited scope (test one agent)
- [ ] Fixed price or discounted rate
- [ ] Timeline (4-8 weeks typical)
- [ ] Success criteria
- [ ] Conversion to full engagement

**Template 4: MSA Updates**
- [ ] Update existing MSA to include AI services
- [ ] Add IP retention language
- [ ] Add managed services terms
- [ ] Add usage-based pricing framework

### Legal Review Process

- [ ] **Review with attorney:** Get professional review of IP, liability, SLA terms
- [ ] **E&O insurance:** Does current policy cover AI services? Do we need riders?
- [ ] **Client approval:** Will existing clients accept new terms? Grandfather old contracts?

---

## Workstream 5: Website Transition & Public Presence

**Goal:** Migrate website from Heroku to Optimizely with new AI positioning.

### Current State

**Website Status:**
- Current: Custom site on Heroku
- In Progress: Migrating to Optimizely (same content, not live yet)
- Challenge: Need to update messaging for AI pivot during migration

### Website Strategy

**Option A: Migrate First, Rebrand Later**
1. Migrate current content to Optimizely (make it live)
2. Then update messaging for AI positioning
3. Pros: Unblocks migration, reduces risk
4. Cons: Old messaging goes live on new platform

**Option B: Rebrand During Migration**
1. Write new messaging (AI positioning)
2. Apply to Optimizely site before launch
3. Launch with new positioning
4. Pros: One launch, fresh positioning
5. Cons: Delays migration, more complex

**Option C: Hybrid - Soft Launch Then Optimize**
1. Migrate current content to Optimizely (go live)
2. Add small "AI Services" section (soft launch)
3. Gradually update other pages with new messaging
4. Pros: Fast migration, iterative messaging
5. Cons: Inconsistent messaging for a period

**Recommendation:** Option C (Hybrid)
- Unblock website migration now
- Add small AI section to test messaging
- Iterate based on client/prospect feedback

### Website Content Needs

**Homepage:**
- [ ] Hero section: What we do in one sentence
- [ ] Value propositions: Why Jaxon for AI + Optimizely
- [ ] Social proof: Client logos, download stats, testimonials
- [ ] CTAs: "Book a Demo", "See Agent in Action", "Download MCP"

**Services Page:**
- [ ] Three-tier offering explanation
- [ ] Traditional Optimizely Services (existing work)
- [ ] Managed Agent Operations (new offering)
- [ ] Platform/SaaS (coming soon?)

**About Page:**
- [ ] Company story: Why we're building this
- [ ] Team bios: Emphasize AI + Optimizely expertise
- [ ] Partner status: Optimizely Gold Partner + AI innovation

**Case Studies / Work Page:**
- [ ] Deployment agent case study (when ready)
- [ ] Bulk pricing agent case study (when ready)
- [ ] Existing Optimizely work (show traditional expertise)

**Blog:**
- [ ] "Clockwork Deployments to AI" (when deployment agent is production)
- [ ] "How We Built [X] Agent for Optimizely"
- [ ] Technical deep dives on MCP development
- [ ] Strategic posts on AI + DXP

**Resources:**
- [ ] Open source MCPs (link to GitHub)
- [ ] Documentation for self-service users
- [ ] Guides: "Getting Started with DXP MCP"

### Other Public Presence

**GitHub:**
- [ ] DXP MCP README: Update with latest capabilities, usage stats
- [ ] Log Analyzer MCP README: Prepare for public release? Or keep private?
- [ ] CMS MCP README: Write for upcoming release
- [ ] Organization profile: Update bio with AI positioning

**LinkedIn:**
- [ ] **Company Page:**
  - Update "About" section with AI positioning
  - Featured content: Blog posts, case studies
  - Regular updates: Milestones, client wins (with permission)

- [ ] **Brian's Profile:**
  - Update headline: "Founder @ Jaxon Digital | Building Autonomous Operations for Optimizely"
  - About section: AI + DXP story
  - Featured content: Blog posts, strategic insights
  - Regular posts: Thought leadership on AI agents

- [ ] **Team Member Profiles:**
  - Update headlines to include AI focus
  - Showcase MCP/agent work in experience section
  - Encourage sharing company content

**Optimizely Partner Page:**
- [ ] Update partner profile with AI capabilities
- [ ] Highlight DXP MCP (open source contribution)
- [ ] Case studies (when available)
- [ ] Differentiation: "The AI operations partner"

**Social Media Strategy:**
- [ ] LinkedIn primary channel (B2B audience)
- [ ] Twitter/X for developer community?
- [ ] Posting cadence: 2-3x per week
- [ ] Content mix: 50% educational, 30% product updates, 20% company culture

---

## Execution Priorities

### Phase 1: Foundation (Weeks 1-2)
**Goal:** Core positioning and messaging framework

- [ ] Complete positioning document (who/what/why)
- [ ] Draft value propositions for three tiers
- [ ] Create differentiation matrix (us vs alternatives)
- [ ] Define target personas (3-5 profiles)
- **Deliverable:** Positioning doc that guides all other work

### Phase 2: Quick Wins (Weeks 2-4)
**Goal:** Update high-impact touchpoints

- [ ] Update LinkedIn profiles (Brian + company page)
- [ ] Update GitHub READMEs (DXP MCP especially)
- [ ] Create sales one-pager (for existing client conversations)
- [ ] Draft pilot program design (for friendly clients)
- **Deliverable:** Can talk about AI services confidently

### Phase 3: Client Engagement (Weeks 4-8)
**Goal:** Start conversations with existing clients

- [ ] Identify 2-3 pilot candidates
- [ ] Create pilot program pitch deck
- [ ] Draft pilot SOW template
- [ ] Schedule client meetings to present
- **Deliverable:** 1-2 clients agree to pilot

### Phase 4: Website & Content (Weeks 8-12)
**Goal:** Public launch of AI positioning

- [ ] Complete Optimizely website migration (with or without new messaging)
- [ ] Add AI services section
- [ ] Publish first case study
- [ ] Launch content marketing (blog posts)
- **Deliverable:** Website reflects AI positioning

### Phase 5: Scale & Optimize (Weeks 12-16)
**Goal:** Refine based on feedback, prepare for scale

- [ ] Finalize legal templates based on pilot learnings
- [ ] Create team learning paths
- [ ] Build inbound lead process
- [ ] Develop partner strategy
- **Deliverable:** Ready to handle multiple simultaneous clients

---

## Success Metrics

**Positioning & Messaging:**
- ✅ Consistent messaging across LinkedIn, website, READMEs
- ✅ Can explain "what we do" in one sentence
- ✅ Positive feedback from clients/prospects on positioning

**Marketing & Sales:**
- ✅ 2-3 existing clients agree to pilot AI services
- ✅ 5-10 inbound inquiries per quarter (from blog, GitHub, LinkedIn)
- ✅ 1-2 net-new clients closed on Platform tier

**Team Learning:**
- ✅ All team members understand agent-first methodology
- ✅ 2-3 team members can build MCPs independently
- ✅ 2-3 team members can build n8n agents independently

**Legal & Contracts:**
- ✅ Pilot SOW signed by at least one client
- ✅ IP retention language approved by attorney
- ✅ No contract blockers preventing client adoption

**Website & Presence:**
- ✅ Website migrated to Optimizely and live
- ✅ AI services clearly described
- ✅ Case studies published (deployment, bulk content)

---

## Related Tickets

- **GAT-168:** Strategic Pivot Plan (parent)
- **GAT-169:** Hosting Architecture (technical enablement)
- **GAT-170:** Bulk Pricing Agent (first case study, CMS MCP refresh)
- **GAT-157:** python-a2a article (technical learning)
- **GAT-187:** Microsoft MCP research follow-up (strategic validation)
- **GAT-188:** Competitive Analysis - Johnny's CMS MCP (market segmentation)
- **GAT-189:** Feature Comparison - Jaxon vs Johnny CMS MCP (gaps and opportunities)
- **GAT-190:** Code Review - Johnny's CMS MCP (technical learnings)

---

## Questions to Answer

**Positioning:**
1. What's our one-sentence positioning? (Who we are, what we do)
2. How do we describe Managed Services tier in prospect language?
3. Do we acknowledge OPAL or ignore it?
4. How do we position DXP/PaaS focus without excluding future SaaS opportunities?
5. How do we differentiate from other CMS MCPs targeting SaaS/headless?

**Sales:**
1. Which existing clients are best pilot candidates?
2. What discount (if any) for pilot program?
3. How do we handle clients who want traditional services only?

**Legal:**
1. Do we need attorney review before first pilot? Or can we use simplified agreement?
2. What SLA can we commit to before we have production data?
3. How do we handle IP with existing clients who funded MCP development?

**Website:**
1. Wait for new messaging or launch Optimizely site now?
2. How prominent should AI services be on homepage?
3. Do we "soft launch" AI services or big announcement?

**Team:**
1. Who owns each learning track? (Who teaches MCP development?)
2. How much time per week for learning vs client work?
3. Do we hire for AI skills or train existing team?

---

## Next Actions

1. Review this document and prioritize workstreams
2. Decide: Which workstream to tackle first? (Recommend: Positioning & Messaging)
3. Balance with Medium article reviews (alternate between strategy and learning)
4. Create sub-tickets for specific deliverables
5. Assign owners and timelines

---

**This is the "other half" of the strategic pivot.** GAT-168 defines what we're building (product, platform, agents). GAT-171 defines how we go to market, sell it, enable the team, and position ourselves.

Execution (building agents, hosting infrastructure) happens in parallel. Strategy work (this document) happens here.

Let's build the business while we build the platform.
