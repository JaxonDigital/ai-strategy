# How n8n Works - Architecture Analysis

**Date**: October 6, 2025
**Ticket**: GAT-42
**Source**: https://businessworkflow.org/how-n8n-works/

---

## Executive Summary

n8n is a **node-based workflow automation platform** that enables visual workflow creation through drag-and-drop interfaces. With 1,250+ pre-built integrations and open-source flexibility, it's positioned as a developer-friendly alternative to proprietary platforms like Zapier.

**Key for Jaxon Digital**: n8n is the **execution engine** for our hybrid agent approach - it handles the reliable, deterministic workflow logic while AI handles the intelligence and decision-making.

---

## Core Architecture

### Node-Based Design
```
Workflow = Connected Nodes
    ↓
[Trigger Node] → [Action Node] → [Logic Node] → [Action Node]
    ↓
Execution follows node connections
```

**Principle**: Each node = a discrete unit of work (fetch data, transform, send, decide)

---

### Three Node Categories

#### 1. Trigger Nodes
**Purpose**: Start workflows

**Types**:
- **Time-based**: Cron schedules (every hour, daily, etc.)
- **Event-based**: Webhooks, file changes, email received
- **Manual**: Button click (for testing/one-off executions)

**Example**:
```
Schedule Trigger (every 5 minutes)
    ↓
Check deployment health
```

---

#### 2. Action Nodes
**Purpose**: Do work (the "hands" of the workflow)

**Examples**:
- HTTP Request (call APIs)
- Database operations (insert, update, query)
- Send email/Slack message
- File operations
- Data transformations

**Count**: 1,250+ pre-built integrations

**Example**:
```
HTTP Request Node
    ↓
Fetch deployment status from Azure
    ↓
Output: { "status": "running", "errors": 47 }
```

---

#### 3. Logic Nodes
**Purpose**: Make decisions, control flow

**Types**:
- **IF**: Conditional branching
- **Switch**: Multiple conditions
- **Merge**: Combine data from multiple paths
- **Loop**: Iterate over arrays
- **Set**: Transform/filter data

**Example**:
```
IF Node: errors > 10
    ↓ TRUE
Trigger AI investigation
    ↓ FALSE
Log "healthy"
```

---

## Data Flow

### JSON-Based Transfer
All data flows between nodes as JSON:

```javascript
// Output from HTTP Request Node
{
  "json": {
    "deployment_id": "d123",
    "status": "running",
    "errors": 47,
    "timestamp": "2025-10-06T15:30:00Z"
  }
}

// Next node can reference: $json.errors
```

### Expression System
Access and transform data using expressions:

```javascript
// Reference previous node data
{{ $json.errors }}

// Transform
{{ $json.errors > 10 ? "critical" : "ok" }}

// Functions
{{ $now() }}
{{ $min($json.values) }}
```

---

## Workflow Execution

### How Execution Works

```
1. Trigger fires (schedule, webhook, etc.)
    ↓
2. First node executes, outputs JSON
    ↓
3. Connected nodes receive JSON input
    ↓
4. Each node processes and outputs
    ↓
5. Execution follows node connections
    ↓
6. Workflow completes (or errors)
```

### Execution Modes

**1. Manual Execution** (for testing)
- Click "Execute Workflow" button
- See results in real-time
- Debug with step-by-step data inspection

**2. Active Execution** (production)
- Workflow runs automatically on triggers
- Logs stored for review
- Errors can retry or alert

---

## Integration Capabilities

### Pre-Built Integrations (1,250+)

**Categories**:
- **Productivity**: Google Workspace, Microsoft 365, Slack
- **Development**: GitHub, GitLab, Jira
- **Cloud**: AWS, Azure, GCP
- **Database**: PostgreSQL, MySQL, MongoDB
- **CRM**: Salesforce, HubSpot
- **E-commerce**: Shopify, WooCommerce
- **Marketing**: Mailchimp, ActiveCampaign

### Custom Integrations

**HTTP Request Node** (Universal Connector):
```javascript
{
  "method": "GET",
  "url": "https://api.example.com/data",
  "authentication": "Bearer Token",
  "headers": {
    "Content-Type": "application/json"
  }
}
```

**Function Node** (Custom Code):
```javascript
// JavaScript execution within workflow
const items = $input.all();
const processed = items.map(item => ({
  ...item.json,
  computed: item.json.value * 2
}));
return processed;
```

---

## Self-Hosting vs Cloud

### Self-Hosted (Free)
**Pros**:
- No cost (open source)
- Full control
- No execution limits
- Data stays on your infrastructure

**Cons**:
- Manage updates
- Handle scaling
- Maintain security

**Deployment**:
```bash
# Docker (recommended)
docker run -it --rm \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n

# Or npm
npm install -g n8n
n8n
```

---

### Cloud ($20-50/month)
**Pros**:
- Managed updates
- Automatic scaling
- Built-in monitoring
- Support

**Cons**:
- Monthly cost
- Execution limits (varies by tier)
- Data on n8n servers

---

## Key Strengths

### 1. Visual + Code
**No-code interface** for 80% of tasks
**Code capability** when you need it (Function nodes, expressions)

**Best of both worlds**: Accessible to non-developers, powerful for developers

---

### 2. Fair-Code License
Open source with conditions:
- Self-hosted: Free forever
- Can modify and customize
- Cannot offer as competing SaaS

**For Jaxon Digital**: We can customize, deploy for clients, charge for services (but not sell n8n-as-a-service)

---

### 3. Transparent Data Flow
See exactly what data flows between nodes:
- Click any node → see input/output
- Debug with real data
- Understand exactly what happened

**Benefit**: Easier to troubleshoot than black-box tools

---

### 4. Error Handling
Built-in retry logic:
```
Node fails
    ↓
Retry 3 times with exponential backoff
    ↓
If still fails: Stop workflow OR continue on error
    ↓
Send alert with full error context
```

**Reliability**: Production-grade error handling out of the box

---

## Limitations & Considerations

### 1. Complexity at Scale
**Simple workflows**: Easy to build and maintain
**Complex workflows**: Can become difficult to manage

**200+ node workflow** = hard to visualize and debug

**Solution**: Break into smaller sub-workflows (n8n supports this)

---

### 2. Learning Curve
**Basic workflows**: 1-2 hours to learn
**Advanced features**: Requires understanding of:
- Expression syntax
- Data structures (JSON)
- API concepts
- Error handling patterns

**For Clients**: We need to train OR manage workflows for them

---

### 3. Performance Limits
**Self-hosted**: Limited by your infrastructure
**Cloud**: Limited by tier (executions/month)

**Example**:
- Starter ($20/month): 2,500 executions/month
- Pro ($50/month): 10,000 executions/month

**For High-Volume Clients**: Self-hosted likely required

---

### 4. No Native AI (Yet)
n8n can CALL AI APIs but doesn't have native AI reasoning

**Current Approach**:
```
n8n Workflow
    ↓
HTTP Request to Claude API
    ↓
Parse AI response
    ↓
Act on result
```

**This is why we need the hybrid approach**: n8n + AI + MCP

---

## Comparison with Other Platforms

| Feature | n8n | Zapier | Power Automate | Make (Integromat) |
|---------|-----|--------|----------------|-------------------|
| **Pricing** | Free (self-hosted) | $20+/month | $15+/month | $9+/month |
| **Execution Limits** | None (self-hosted) | Tier-based | Tier-based | Tier-based |
| **Custom Code** | ✅ JavaScript | ❌ Limited | ✅ Limited | ✅ Limited |
| **Self-Hosting** | ✅ Yes | ❌ No | ❌ No | ❌ No |
| **Visual Design** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Open Source** | ✅ Yes | ❌ No | ❌ No | ❌ No |
| **Integrations** | 1,250+ | 5,000+ | 1,000+ | 1,500+ |
| **Learning Curve** | Medium | Low | Medium | Medium-High |

**n8n's Niche**: Developer-friendly, self-hostable, no execution limits

---

## How n8n Fits Our Hybrid Agent Architecture

### Current Architecture
```
n8n Workflow (deterministic automation)
    +
AI Node (Claude API for intelligence)
    +
MCPs (tools AI can use)
    =
Hybrid Intelligent Agent
```

### n8n's Role

**1. Orchestration Engine**
```
n8n controls the WHEN and WHAT:
- WHEN: Trigger on schedule, event, webhook
- WHAT: Fetch data, call APIs, execute actions

AI controls the HOW and WHY:
- HOW: Analyze data, determine approach
- WHY: Root cause, recommendations
```

---

**2. Reliability Layer**
```
n8n provides:
- Retry logic
- Error handling
- Execution logs
- Scheduling
- Data transformation

AI provides:
- Analysis
- Decision-making
- Pattern recognition
- Natural language understanding
```

---

**3. Integration Hub**
```
n8n connects to:
- Azure (deployment status)
- GitHub (code changes)
- Jira (ticket creation)
- Slack (notifications)
- Optimizely (CMS operations)

AI analyzes data from all sources:
- Correlates deployment + errors
- Links code changes to issues
- Generates human-readable reports
```

---

## Workflow Design Patterns for Hybrid Agents

### Pattern 1: Investigation Agent
```
[Schedule Trigger: Every 5 minutes]
    ↓
[HTTP Request: Get deployment status]
    ↓
[IF: errors > 10]
    ↓ TRUE
[HTTP Request: Get logs]
    ↓
[HTTP Request: Call Claude API with logs + context]
    ↓
[Parse: Extract root_cause, severity, recommendation]
    ↓
[Slack: Post AI analysis]
    ↓
[Jira: Create ticket if severity = critical]
```

**n8n Role**: Schedule, fetch data, route based on logic, execute actions
**AI Role**: Analyze logs, determine root cause, recommend action

---

### Pattern 2: Decision Agent
```
[Webhook Trigger: Deployment complete]
    ↓
[HTTP Request: Get deployment metrics]
    ↓
[HTTP Request: Get error count]
    ↓
[Set: Build context object]
    ↓
[HTTP Request: Call Claude API for decision]
    ↓
[Switch: Based on AI decision]
    ├─ "rollback" → [API: Execute rollback]
    ├─ "monitor" → [Slack: Alert team to watch]
    └─ "approve" → [Slack: Deployment successful]
```

**n8n Role**: Gather context, execute decided action
**AI Role**: Decide which action based on metrics

---

### Pattern 3: Self-Healing Agent
```
[Error Hook Trigger: Workflow failure]
    ↓
[HTTP Request: Get workflow details]
    ↓
[HTTP Request: Get error logs]
    ↓
[HTTP Request: Call Claude API with workflow + error]
    ↓
[Parse: Get suggested fix]
    ↓
[IF: AI confidence > 90%]
    ↓ TRUE
[API: Update workflow with fix]
    ↓
[API: Retry workflow]
    ↓ FALSE
[Slack: Request human review]
```

**n8n Role**: Error detection, workflow modification
**AI Role**: Diagnose error, suggest fix

---

## Best Practices for Our Clients

### 1. Start Simple, Add Intelligence
**Phase 1**: Build deterministic workflow in n8n
```
Schedule → Fetch → Check Threshold → Alert
```

**Phase 2**: Add AI for edge cases
```
Schedule → Fetch → IF threshold exceeded → AI Analysis → Smart Alert
```

**Benefit**: Prove value before adding AI costs

---

### 2. Use Sub-Workflows
**Problem**: Complex workflows become unmaintainable

**Solution**: Break into reusable sub-workflows
```
Main Workflow:
- Deployment Monitor

Sub-Workflows:
- Get Deployment Data
- AI Investigation
- Send Notifications
- Create Ticket
```

**Benefit**: Modular, testable, reusable

---

### 3. Environment Variables
**Don't hardcode** credentials, URLs, thresholds

**Use n8n environment variables**:
```javascript
{{ $env.AZURE_API_KEY }}
{{ $env.ERROR_THRESHOLD }}
{{ $env.SLACK_WEBHOOK }}
```

**Benefit**: Easy to update, secure, portable

---

### 4. Error Handling Always
**Every API call should handle errors**:
```
HTTP Request Node
    ↓
Continue on Fail: TRUE
Error Output: Connected to error handler
    ↓
[Error Handler]
    ↓
Log error + Send alert
```

**Benefit**: Workflows don't silently fail

---

### 5. Test in Dev, Deploy to Prod
**n8n supports workflow export/import**:
```
1. Build in dev n8n instance
2. Test thoroughly
3. Export workflow (JSON)
4. Import to production instance
5. Update environment variables
6. Activate
```

**Benefit**: Safe deployment process

---

## Integration with Our MCP Strategy

### n8n + MCP = Powerful Combination

**Before MCP**:
```
n8n → HTTP Request → API endpoint
(generic, manual configuration)
```

**With MCP**:
```
n8n → AI Node → MCP tools (optimizely-dxp, log-analyzer, etc.)
(semantic, validated operations)
```

### Example: Deployment Monitoring

**Without MCP**:
```yaml
1. HTTP Request: Get deployment status
   URL: https://azure.api.com/deployments/{id}
   Auth: Manual token
   Parse: Manual JSON extraction

2. HTTP Request: Get logs
   URL: https://azure.api.com/logs
   Parse: Manual log parsing

3. IF errors > 10
   → Manual threshold logic
```

**With MCP**:
```yaml
1. AI Node with optimizely-dxp-mcp
   Prompt: "Check deployment health for {environment}"
   → MCP handles authentication, API calls, parsing

2. AI analyzes logs
   → MCP log-analyzer provides context

3. AI decides action
   → Returns structured response
```

**Benefit**: Less configuration, more intelligence

---

## Cost Analysis

### Self-Hosted n8n

**Infrastructure**:
- Small VM: $10-20/month (handles most clients)
- Medium VM: $50-100/month (high-volume clients)

**Maintenance**:
- Updates: 1-2 hours/month
- Monitoring: Included in managed services

**Total**: $10-100/month per client

---

### Cloud n8n

**Starter** ($20/month):
- 2,500 executions
- Good for: Low-volume monitoring

**Pro** ($50/month):
- 10,000 executions
- Good for: Medium-volume automation

**Total**: $20-50/month per client

---

### ROI for Hybrid Agents

**Deployment Health Monitor Example**:
```
Manual monitoring:
- DevOps engineer: $150/hr
- 10 hours/month monitoring/troubleshooting
- Cost: $1,500/month

Automated with n8n + AI:
- n8n: $50/month (cloud) or $20/month (self-hosted)
- AI API: $50-100/month
- Management: 1 hour/month = $150
- Cost: $250/month

Savings: $1,250/month = $15,000/year
```

**Client Value**: We charge $1,000/month (save them $500/month)
**Our Margin**: $750/month per client

---

## Recommendations for Jaxon Digital

### 1. Standardize on Self-Hosted n8n
**Why**:
- No execution limits
- Full control
- Better margins
- Client data stays on their infrastructure (enterprise requirement)

**Deployment**:
- Docker on client's cloud (Azure, AWS)
- Or, managed n8n on our infrastructure (for smaller clients)

---

### 2. Build Workflow Template Library
**Categories**:
- Deployment monitoring
- Content synchronization
- Cache invalidation
- Security monitoring
- Performance optimization

**Benefit**: Faster client delivery, proven patterns

---

### 3. Create n8n Training Program
**For Clients**:
- Basic: 2-hour intro (use existing workflows)
- Intermediate: 4-hour course (modify workflows)
- Advanced: 8-hour course (build new workflows)

**Pricing**: $500-2,000 per training
**Benefit**: Client self-sufficiency OR upsell opportunity

---

### 4. Hybrid Workflow Certification
**Internal Process**:
1. Design workflow (architect)
2. Build in n8n (developer)
3. Test (QA)
4. AI integration (AI specialist)
5. Validate (end-to-end test)
6. Deploy (DevOps)
7. Monitor (support)

**Benefit**: Quality assurance, repeatable process

---

## Technical Specifications

### System Requirements (Self-Hosted)

**Minimum**:
- CPU: 2 cores
- RAM: 2GB
- Storage: 10GB
- Network: 1 Gbps

**Recommended**:
- CPU: 4 cores
- RAM: 8GB
- Storage: 50GB
- Network: 10 Gbps

**Database**: PostgreSQL (recommended) or SQLite (dev only)

---

### Security Considerations

**Authentication**:
- Basic auth (username/password)
- LDAP/SAML (enterprise)
- OAuth (for integrations)

**Encryption**:
- HTTPS required for production
- Credentials encrypted at rest
- Environment variables for secrets

**Access Control**:
- Role-based permissions
- Workflow-level access
- Audit logging

---

## Comparison to Our Current Approach

| Factor | Pure n8n | Our Hybrid (n8n + AI + MCP) |
|--------|----------|------------------------------|
| **Intelligence** | Rules-based only | AI-powered analysis |
| **Flexibility** | Requires reconfiguration | AI adapts to situations |
| **Cost** | $10-50/month | $100-200/month (includes AI) |
| **Reliability** | Very high | High (dependent on AI API) |
| **Debugging** | Easy (visual, logs) | Medium (need to check AI responses) |
| **Client Appeal** | "Automation" | "Intelligent agents" |
| **Pricing Power** | $500-1,000/month | $1,000-2,000/month |

**Bottom Line**: n8n is the foundation, AI is the differentiator

---

## Key Takeaways

### 1. n8n is Production-Ready
- 1,250+ integrations
- Enterprise security
- Self-hosted = no limits
- Active community + commercial support

**We can confidently build on this platform**

---

### 2. Visual + Code = Best of Both
- Non-technical users can understand workflows
- Developers can customize with code
- Transparent data flow

**Makes workflows client-friendly**

---

### 3. Open Source = Customizable
- We can modify source code if needed
- No vendor lock-in
- Fair-code license allows our use case

**Long-term safety for our business**

---

### 4. Hybrid Approach is Correct
n8n alone = smart automation
n8n + AI = intelligent agents

**n8n handles reliability, AI handles intelligence**

---

### 5. Scalable Business Model
```
Build once:
- Workflow template

Deploy many:
- 10 clients × $1,000/month = $10,000/month

Scale:
- Library of templates
- Faster delivery
- Higher margins
```

**This is how we scale to $1M+ recurring revenue**

---

## Next Steps

### This Week
- [ ] Deploy self-hosted n8n in dev environment
- [ ] Build 3 example workflows (deployment monitoring, content sync, error alerting)
- [ ] Test AI integration via HTTP Request nodes

### Next Week
- [ ] Create workflow template for deployment health monitoring
- [ ] Document standard patterns
- [ ] Identify pilot client for hybrid agent

### Month 2
- [ ] Build workflow library (5-10 templates)
- [ ] Develop training materials
- [ ] Productize hybrid agent offering

---

## Conclusion

**n8n is the right orchestration platform** for our hybrid agent approach because:

1. **Visual + Code**: Accessible to clients, powerful for developers
2. **Self-Hosted**: No limits, full control, better margins
3. **Integrations**: 1,250+ pre-built, custom via HTTP/Function nodes
4. **Reliable**: Error handling, retries, logging built-in
5. **Fair-Code**: We can use, customize, deploy for clients

**Combined with AI + MCPs**, we can build intelligent agents that:
- Monitor systems 24/7
- Investigate issues automatically
- Make smart decisions
- Execute actions safely
- Learn from patterns

**This is not just automation. This is intelligent operations.**

**Action**: Standardize on n8n, build template library, scale to clients.

---

**Ticket**: GAT-42
**Status**: Ready for Review
**Recommendation**: ADOPT - n8n is the correct orchestration platform for our hybrid agents
