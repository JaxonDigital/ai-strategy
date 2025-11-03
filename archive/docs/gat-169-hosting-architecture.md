# GAT-169: Multi-Tenant Hosting Architecture (MCPs + Agents)

**Epic Link:** https://jaxondigital.atlassian.net/browse/GAT-169
**Parent:** GAT-168 (Strategic Pivot Plan)
**Sprint:** Sprint 2 (weeks 4-8)

## Overview

Build production hosting infrastructure to support both Managed Services and Platform/SaaS tiers. Architecture separates MCPs (shared multi-tenant) from agents (per-client instances) for cost efficiency and scalability.

## Architecture Decision

### MCPs: Shared Multi-Tenant Service
- **Deployment:** One shared instance of DXP MCP + Log Analyzer MCP serves all clients
- **Transport:** SSE over HTTP (already implemented)
- **Isolation:** Tenant isolation via API authentication + data separation
- **Platform Options:**
  - Start: Railway or Render (fast to ship, $20-50/month)
  - Scale: Azure Container Apps (enterprise-grade)

### Agents: Per-Client Instances
- **Deployment:** Each client gets dedicated n8n instance
- **Communication:** Agents connect to shared MCPs via HTTP/SSE
- **Platform Options:**
  - Start: n8n Cloud (managed, $20-100/month per client)
  - Scale: Self-hosted n8n on Azure (cost control)

### Architecture Diagram
```
┌─────────────────────────────────────────┐
│  Jaxon MCP Platform (Multi-Tenant)      │
│  ┌────────────┐  ┌───────────────┐      │
│  │  DXP MCP   │  │ Log Analyzer  │      │
│  │  (Shared)  │  │  MCP (Shared) │      │
│  └────────────┘  └───────────────┘      │
│         ↑                ↑               │
│         │ SSE/HTTP       │               │
└─────────┼────────────────┼───────────────┘
          │                │
    ┌─────┴────────────────┴─────┐
    │   API Authentication       │
    │   (Per-Tenant Keys)        │
    └─────┬────────────┬─────────┘
          ↓            ↓
┌──────────────┐  ┌──────────────┐
│  Client A    │  │  Client B    │
│  n8n Agent   │  │  n8n Agent   │
│  (Dedicated) │  │  (Dedicated) │
└──────────────┘  └──────────────┘
```

## Deliverables

### 1. MCP Multi-Tenant Platform
- [ ] Docker images for DXP MCP + Log Analyzer MCP
- [ ] Tenant authentication system (API keys per client)
- [ ] Database schema for tenant isolation
- [ ] CI/CD pipeline for deployments
- [ ] Monitoring and logging (Azure App Insights or equivalent)
- [ ] Cost tracking per tenant (usage metrics)
- [ ] Rate limiting and DDoS protection
- [ ] Health checks and auto-healing

### 2. Agent Deployment System
- [ ] n8n instance provisioning workflow (automated)
- [ ] Pre-built workflow templates
  - Deployment agent
  - Monitoring agent
  - Future agents (content, security, etc.)
- [ ] Connection configuration (agent → MCP authentication)
- [ ] Client self-service dashboard (for Platform tier)
  - View agent status
  - Configure credentials
  - View usage/costs
  - Access logs/metrics

### 3. Security & Compliance
- [ ] Secrets management (Azure Key Vault or equivalent)
- [ ] API key rotation process
- [ ] Audit logging (who accessed what, when)
- [ ] Tenant data isolation verification (security audit)
- [ ] Network security (HTTPS, firewall rules)
- [ ] Compliance documentation (SOC2 prep)

### 4. Documentation
- [ ] Architecture diagrams (tenant isolation, data flow, security model)
- [ ] Deployment runbooks
  - Provision new MCP tenant
  - Provision new agent instance
  - Connect agent to MCPs
  - Troubleshooting guide
- [ ] Cost analysis
  - Per-tenant costs (compute, storage, bandwidth)
  - Breakeven analysis (at 5/10/20 clients)
  - Pricing recommendations
- [ ] Migration plan (move local MCPs to hosted)
  - Internal use first (Jaxon's own deployments)
  - Then existing clients
  - Then new Platform tier clients

## Success Criteria

- ✅ Can provision new client in <15 minutes (fully automated)
- ✅ Tenant data completely isolated (security audit confirms)
- ✅ Cost under $500/month for first 10 clients (on Railway/Render)
- ✅ Ready for first client deployment in Sprint 2 (4-8 weeks from now)
- ✅ Supports both Managed ($50-80K/year) and Platform ($25-50K/year) tiers
- ✅ 99.9% uptime SLA achievable
- ✅ Can scale to 50+ clients without architecture changes

## Platform Strategy

### Phase 1: MVP (First 2-3 Clients)
**Goal:** Prove the model, learn fast, iterate

**MCPs:**
- Platform: Railway or Render
- Why: Simple deployment, auto-scaling, great DX
- Cost: $20-50/month total (all clients share)

**Agents:**
- Platform: n8n Cloud (managed)
- Why: Zero ops, automatic updates
- Cost: $20-100/month per client

**Total Cost:** ~$100-350/month for 2-3 clients
**Revenue:** $150-240K/year (2-3 clients at $50-80K)
**Margin:** 95%+ (insanely profitable)

### Phase 2: Scale to Enterprise (5+ Clients)
**Goal:** Enterprise features, compliance, cost optimization

**MCPs:**
- Platform: Azure Container Apps
- Why: Enterprise SLAs, compliance, Microsoft ecosystem alignment
- Cost: ~$200-500/month (all clients share)

**Agents:**
- Platform: Self-hosted n8n on Azure
- Why: Cost control at scale ($10-20/month per client vs $100)
- Cost: ~$100-400/month for 20 clients

**When to Migrate:** When Platform tier has 5+ customers OR when enterprise client requires compliance

## Technical Decisions

### Why Separate MCPs from Agents?

**Pros:**
- MCPs are reusable (one deployment serves all agents)
- Independent scaling (MCP can scale separately)
- Easier updates (update MCP once, all clients benefit)
- True multi-tenancy (cost-efficient)
- Aligns with IP strategy (MCPs are the product)

**Cons:**
- More complex architecture (two services)
- Network latency (agent → MCP over HTTP)
- But: Already mitigated by SSE/HTTP transport

### Why SSE Transport?

- Standard web technology (widely supported)
- Already implemented in DXP + Log Analyzer MCPs
- Required for network-based MCP access
- Supports long-running operations (streaming)

### Why Azure Container Apps (eventually)?

- You already use Azure (familiar)
- Optimizely ecosystem is Azure-native (alignment story)
- Enterprise clients trust Microsoft
- Compliance features (SOC2, ISO, etc.)
- But: Start with Railway/Render to ship faster

## Risks & Mitigations

**Risk:** Multi-tenant security breach
**Mitigation:** Strict tenant isolation, regular security audits, API key rotation

**Risk:** Cost overruns at scale
**Mitigation:** Per-tenant cost tracking, alerts, auto-scaling limits

**Risk:** Single point of failure (MCPs down = all clients down)
**Mitigation:** High availability setup, health checks, auto-healing, backup instances

**Risk:** n8n Cloud vendor lock-in
**Mitigation:** Design workflows to be portable, plan self-hosted migration path

## Timeline

**Week 1-2:**
- Docker images for MCPs
- Deploy to Railway/Render
- Tenant authentication system
- Basic monitoring

**Week 3-4:**
- n8n Cloud setup
- Pre-built workflow templates
- First test client (internal use)
- Security audit

**Week 5-6:**
- Client self-service dashboard
- Documentation complete
- Cost tracking implemented
- Second test client (friendly existing client)

**Week 7-8:**
- Production-ready (security, monitoring, docs)
- First paying client migrated
- Announce availability to existing clients
- Sprint 2 complete ✅

## Related Tickets

- **GAT-168:** Strategic Pivot Plan (parent epic)
- **GAT-157:** Review python-a2a article (production MCP patterns)
- Future tickets: Specific agent implementations, CMS MCP refresh, etc.

## Next Actions

1. Choose MVP platform (Railway vs Render vs Azure)
2. Create Docker images for DXP MCP + Log Analyzer MCP
3. Set up tenant authentication
4. Deploy first test instance
5. Build n8n deployment agent workflow
6. Test with internal Jaxon deployments
7. Iterate based on learnings
