# Article Review: How Optimizely MCP Learns Your CMS (and Remembers It)

**JIRA Ticket:** GAT-333
**Author:** Johnny Mullaney (Platinum Optimizely MVP, Solutions Architect at First Three Things Ltd)
**Published:** October 20, 2025
**Article URL:** https://johnnymullaney.com/2025/10/20/how-optimizely-mcp-learns-your-cms-and-remembers-it/
**Series:** Part 2 of 4-part series on "Discovery-First MCP for Optimizely CMS"

---

## PRIORITY: HIGH

**Relevance Rating:** 🔥 CRITICAL - Direct competitor/peer building similar solution

---

## Executive Summary

Johnny Mullaney (Optimizely Platinum MVP) has built and is documenting a **production-quality MCP server for Optimizely SaaS CMS** that uses GraphQL introspection to dynamically learn and navigate any CMS schema. This is Part 2 of a 4-part technical deep-dive series.

**Why This Matters to Jaxon Digital:**
1. **Validates our market positioning** - A respected Optimizely MVP is building the exact same thing we identified as a strategic opportunity
2. **Competitive intelligence** - Shows what others in the Optimizely ecosystem are building
3. **Technical architecture insights** - His discovery-first approach could inform our own MCP design decisions
4. **Market timing confirmation** - October 2025 publication suggests we're right on time with our Q4 strategy
5. **Partnership/collaboration potential** - Johnny is a known entity in the Optimizely community

---

## Key Technical Insights

### 1. Discovery-First Architecture
**What:** MCP doesn't hardcode content types - it introspects the GraphQL API to learn the schema dynamically

**How:**
- Uses GraphQL's standard `getIntrospectionQuery()` to fetch full schema
- Returns everything: object types, interfaces, enums, input objects, directives
- Nested type references up to 9 levels deep

**Code Example:**
```typescript
async introspect(): Promise<IntrospectionQuery> {
  return await this.query<IntrospectionQuery>(
    getIntrospectionQuery(),
    undefined,
    {
      cacheKey: 'graphql:introspection',
      cacheTtl: 3600 // 1 hour cache
    }
  );
}
```

**Jaxon Relevance:** Our MCPs currently hardcode content types. This approach would make them more flexible and reusable across different Optimizely implementations.

---

### 2. Type Map for Fast Lookup
**What:** Indexes all discovered types in a Map for instant access without re-parsing schema

**Benefits:**
- Identify which types represent content vs components
- Traverse relationships between nested objects
- Dynamically generate valid GraphQL queries without templates

**Implementation:**
```typescript
this.schema.__schema.types.forEach(type => {
  this.typeMap.set(type.name, type);
});
```

**Jaxon Relevance:** Performance optimization - reduces latency for AI agent interactions with CMS

---

### 3. Multi-Tier Caching Strategy
**Three Cache Levels:**

1. **Base Cache** - 5-minute TTL, in-memory key/value for all tools/logic
2. **Discovery Cache** - 5-60 min TTL, holds schema introspection and type maps, auto-invalidates on schema version change
3. **Fragment Cache** - Stores generated GraphQL fragments in memory AND on disk, survives restarts

**Performance Impact:**
- **Cold start:** 1,247ms (schema introspection) + 124ms (fragment generation) + 287ms (query) = ~1.6 seconds
- **Warm cache:** 78ms (query execution only) = **95% faster**

**Jaxon Relevance:** Critical for production agents - need sub-second response times for good AI UX

---

### 4. Dynamic GraphQL Fragment Generation
**What:** Auto-generates GraphQL fragments based on discovered content types

**Example Flow:**
```typescript
// User calls:
await get({ identifier: "/articles/my-article/" });

// Behind the scenes:
1. Initialize schema (cached after first call)
2. Detect identifier type ("path")
3. Find content, identify type ("ArticlePage")
4. Generate or reuse fragment for ArticlePage
5. Build and execute full query with fragment
```

**Jaxon Relevance:** Enables our agents to work with custom content types without manual configuration

---

### 5. Real Production Example
**Article shows full request/response cycle:**
- Metadata extraction (key, displayName, types, URL, publish dates, status)
- Content fields (Title, Heading, Body HTML)
- Media assets (PromoImage with CDN URL)
- SEO settings (MetaTitle, MetaDescription)

**Jaxon Relevance:** This is production-ready code handling real CMS complexity, not a proof-of-concept

---

## Competitive Analysis

### Johnny Mullaney's Position
- **Platinum Optimizely MVP** (highest tier)
- Solutions Architect at First Three Things Ltd (Dublin, Ireland)
- Deep Optimizely expertise (.NET, Azure, Commerce, CMS)
- Publishing detailed technical series = building thought leadership

### What This Tells Us
1. **We're not alone** - Smart people see the same opportunity
2. **Market validation** - If Johnny is investing time in this, there's demand
3. **Open source potential** - He's documenting publicly, may release code
4. **Community leadership** - MVPs influence Optimizely's product direction

### Differentiation Opportunities for Jaxon
- **Managed service model** - Johnny's approach seems more DIY/implementation-focused
- **Multi-MCP orchestration** - We have 3 MCPs (CMS, Commerce, Operations) vs his CMS-only approach
- **Production agent focus** - We're building complete agents (e.g., Deployment Agent), not just MCP servers
- **Client-specific customization** - We do $40-100K custom MCPs for proprietary systems

---

## Strategic Implications

### 1. Market Timing
✅ **We're right on schedule** - Q4 2025 is when this technology is hitting maturity

### 2. Competitive Landscape
⚠️ **More players entering** - Need to move quickly on client pilots and case studies

### 3. Technology Validation
✅ **GraphQL introspection approach is sound** - Consider adopting for our MCPs

### 4. Partnership Potential
💡 **Could we collaborate?** - Johnny is building infrastructure, we're building managed services (complementary)

### 5. Series Continuation
📚 **Part 3 coming** - Will cover Visual Builder pages (nested composition layer)
- **Action:** Monitor johnnymullaney.com for Parts 3 & 4
- **Create follow-up tickets** when published

---

## Action Items

### Immediate (This Week)
1. **Share with Jaxon engineering team** - Review Johnny's caching strategy and type map approach
2. **Evaluate GraphQL introspection** - Could we retrofit our existing MCPs to use discovery-first approach?
3. **Benchmark performance** - How do our MCPs compare to his 78ms warm cache queries?

### Short-Term (This Month)
4. **Monitor for Part 3** - Set up alert for johnnymullaney.com RSS feed
5. **Reach out to Johnny?** - Consider exploratory conversation (partnership, collaboration, mutual referrals)
6. **Update competitive analysis** - Add Johnny/FTT to our market landscape document

### Strategic (Q4 2025)
7. **Differentiation messaging** - Emphasize our managed service model vs DIY implementation
8. **Case study urgency** - Need client success story to establish credibility vs competitors
9. **Thought leadership response** - Should we be publishing similar technical content?

---

## Technical Debt / Research Questions

1. **How does our CMS MCP handle schema changes?** - Johnny auto-invalidates on version change
2. **Do we have fragment caching?** - His survives restarts via disk persistence
3. **What's our cold start vs warm cache performance?** - Need to measure and optimize
4. **Can we support "any CMS" like Johnny claims?** - Or are we Optimizely-specific?

---

## Quotes Worth Remembering

> "When the MCP connects to a CMS for the first time, it doesn't guess what types exist. It introspects the CMS's GraphQL API using the standard GraphQL introspection query."

> "The type map is a simple but powerful lookup table that indexes every discovered type by name. It lets MCP jump directly to any type's details without re-parsing the whole schema."

> "Once the MCP discovers your schema, it doesn't need to do it again. Full GraphQL introspection can take a second or more, so the server layers its caches to keep things instant after the first call."

---

## Series Context

**Part 1:** Introduction to "discovery-first" MCP concept
**Part 2:** This article - Schema discovery, type mapping, caching
**Part 3:** (Coming) Visual Builder pages and nested composition
**Part 4:** (Coming) TBD

**Recommendation:** Create JIRA tickets to review Parts 3 & 4 when published

---

## Overall Assessment

**Priority:** HIGH
**Actionability:** HIGH - Immediate technical insights + strategic competitive intelligence
**Urgency:** MEDIUM - Need to track series completion, but no immediate threat
**Relevance Score:** 9/10

This is essential reading for anyone on the Jaxon AI agent team. Johnny is building production-quality infrastructure that validates our market thesis while potentially offering partnership opportunities.

---

**Reviewed By:** Claude Code
**Review Date:** October 21, 2025
**Next Review:** When Part 3 publishes
