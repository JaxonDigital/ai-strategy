# Context Engineering for AI Agents - Best Practices

**Date**: October 6, 2025
**Ticket**: GAT-50
**Status**: Article was paywalled - providing knowledge-based best practices

---

## What is Context Engineering?

Context engineering is the practice of **structuring, optimizing, and managing the information** you provide to AI agents to maximize their effectiveness, accuracy, and efficiency.

**Key Principle**: The quality of AI output is directly proportional to the quality and structure of the context you provide.

---

## Core Principles

### 1. Clarity Over Brevity
- Be explicit about what you want
- Don't assume the AI "knows what you mean"
- State objectives clearly upfront

**Bad**: "Check the deployment"
**Good**: "Check deployment status for pre-production environment, analyze any errors in the last hour, and determine if rollback is needed"

---

### 2. Structure Your Context
Use clear hierarchical structure:

```
ROLE: You are a deployment health analyst
CONTEXT: Pre-production deployment started at 2:30pm
DATA: [deployment logs, error counts, metrics]
TASK: Determine root cause of errors and recommend action
OUTPUT FORMAT: JSON with fields: root_cause, severity, recommendation
```

---

### 3. Provide Relevant Examples
Include examples of good output:

```
Your response should look like this:
{
  "root_cause": "Database connection timeout due to migration lock",
  "severity": "high",
  "recommendation": "Rollback deployment and optimize migration script"
}
```

---

## Best Practices for Production AI Agents

### 1. Token Optimization

**Problem**: Context windows are limited and expensive

**Solutions**:
- **Summarize historical context**: Don't send entire log files
- **Chunk and filter**: Only send relevant portions
- **Use references**: "See previous analysis from [timestamp]" instead of repeating

**Example**:
```
❌ Bad: Include all 10,000 log lines
✅ Good: Include last 50 error lines + summary of patterns
```

---

### 2. Prompt Layering

**Structure prompts in layers**:

**Layer 1 - System Role** (stays constant):
```
You are a deployment health analyst for e-commerce infrastructure.
Your goal is to identify issues quickly and provide actionable recommendations.
```

**Layer 2 - Task Context** (changes per request):
```
Current situation: Pre-production deployment showing 47 errors
Time window: Last 30 minutes
Previous state: 0 errors before deployment
```

**Layer 3 - Specific Instructions** (what to do now):
```
Analyze the error pattern below and determine:
1. Root cause
2. Impact severity (critical/high/medium/low)
3. Recommended action (rollback/fix/monitor)
```

---

### 3. Context Windowing

**For ongoing conversations/monitoring**:

**Sliding Window Approach**:
- Keep last N interactions in context
- Summarize older interactions
- Reference patterns without full detail

**Example for deployment monitoring**:
```
Context:
- Current: 47 errors detected at 3:45pm
- Recent history summary: 3 deployments today, 2 successful, 1 (current) failing
- Pattern: Database timeouts common in afternoon (high traffic)

[Only last 100 error lines, not all 500]
```

---

### 4. Contextual Constraints

**Always include constraints to prevent hallucination**:

```
CONSTRAINTS:
- Only use data provided in this prompt
- If information is missing, state "Data not available"
- Do not make assumptions about system behavior
- Cite specific log lines when identifying issues
```

---

## Techniques for Hybrid n8n + AI Agents

### Technique 1: Context Accumulation in n8n

**Problem**: Each AI call is stateless

**Solution**: Build context across workflow steps

```
n8n Workflow:
1. Get deployment status (MCP) → Store in variable
2. Get recent errors (MCP) → Store in variable
3. Get system metrics (MCP) → Store in variable
4. Combine all into structured context
5. Send to AI with full context
```

**Context Template**:
```javascript
{
  "deployment": {
    "status": "{{ $json.deployment_status }}",
    "started_at": "{{ $json.deployment_time }}",
    "environment": "pre-production"
  },
  "errors": {
    "count": {{ $json.error_count }},
    "sample": {{ $json.error_samples }},
    "timeframe": "last 30 minutes"
  },
  "metrics": {
    "cpu": "{{ $json.cpu_usage }}",
    "memory": "{{ $json.memory_usage }}",
    "database_connections": {{ $json.db_connections }}
  },
  "task": "Analyze and determine root cause"
}
```

---

### Technique 2: Dynamic Context Selection

**Problem**: Not all context is always relevant

**Solution**: Use n8n logic to select relevant context

```
IF error_type == "database"
  THEN include: database_metrics, recent_migrations, connection_pool_status
ELSE IF error_type == "network"
  THEN include: network_metrics, DNS_status, firewall_logs
ELSE
  THEN include: general_system_metrics
```

---

### Technique 3: Context Caching

**Problem**: Repeatedly sending same context wastes tokens

**Solution**: Reference cached context

```
SYSTEM_CONTEXT (cached, reused):
- Infrastructure overview
- Normal operating parameters
- Standard troubleshooting procedures

DYNAMIC_CONTEXT (changes each call):
- Current error details
- Recent changes
- Real-time metrics
```

---

## Prompt Templates for Common Agent Tasks

### Template 1: Investigation/Analysis

```
ROLE: You are an expert deployment analyst

CONTEXT:
- System: {{ system_name }}
- Environment: {{ environment }}
- Current State: {{ current_state }}
- Normal State: {{ normal_state }}

DATA:
{{ error_logs }}
{{ metrics }}

TASK:
Analyze the data and determine:
1. Root cause of the issue
2. Severity level (critical/high/medium/low)
3. Recommended action (with specific steps)

CONSTRAINTS:
- Only use data provided above
- Cite specific log lines or metrics
- If uncertain, state confidence level

OUTPUT FORMAT:
{
  "root_cause": "string",
  "severity": "string",
  "confidence": "high|medium|low",
  "recommendation": "string with specific steps"
}
```

---

### Template 2: Decision Making

```
ROLE: You are an automation decision engine

CONTEXT:
- Situation: {{ situation_description }}
- Available Actions: {{ available_actions }}
- Risk Tolerance: {{ risk_level }}

DECISION CRITERIA:
- If severity == "critical" → Auto-rollback
- If severity == "high" AND confidence == "high" → Recommend rollback
- If severity == "medium" → Monitor and alert
- If severity == "low" → Log only

DATA:
{{ analysis_results }}

TASK:
Based on the criteria above, decide the action and explain reasoning.

OUTPUT:
{
  "action": "rollback|monitor|log",
  "reasoning": "string",
  "human_approval_required": boolean
}
```

---

### Template 3: Content Generation/Optimization

```
ROLE: You are a content optimization specialist

CONTEXT:
- Content Type: {{ content_type }}
- Target Audience: {{ audience }}
- Current Performance: {{ metrics }}
- Brand Guidelines: {{ guidelines_summary }}

CURRENT CONTENT:
{{ content_text }}

TASK:
Optimize this content for:
1. SEO (target keyword: {{ keyword }})
2. Readability (Flesch score > 60)
3. Brand compliance

CONSTRAINTS:
- Maintain core message
- Keep length within {{ min_length }}-{{ max_length }} words
- Use active voice
- Include call-to-action

OUTPUT FORMAT:
{
  "optimized_content": "string",
  "changes_made": ["list of changes"],
  "seo_score": "estimated 1-10",
  "compliance_check": "pass|fail with reasons"
}
```

---

## Optimization Strategies

### Strategy 1: Progressive Context Loading

**Don't front-load everything**:

```
Call 1: Basic analysis (minimal context)
  → If conclusive: Done
  → If uncertain: Load more context

Call 2: Deep analysis (additional context)
  → If conclusive: Done
  → If still uncertain: Load comprehensive context

Call 3: Comprehensive analysis (full context)
  → Must reach conclusion
```

**Saves tokens when issues are simple**

---

### Strategy 2: Context Compression

**Summarize instead of including raw data**:

```
❌ Bad (1000 tokens):
[Include all 100 error log lines]

✅ Good (100 tokens):
Error Summary:
- Total: 47 errors in 30 min
- Pattern: 42 "DatabaseTimeout" (89%)
- Other: 3 "NetworkError", 2 "MemoryWarning"
- Timing: All occurred 3:45-3:48pm (3-minute window)
- Sample: "Connection pool exhausted, waited 30s for connection"
```

---

### Strategy 3: Structured Data Over Text

**Use JSON/structured formats**:

```
❌ Bad (verbose):
"The deployment started at 3:30pm and there were 47 errors detected.
The errors seem to be related to database timeouts..."

✅ Good (compact):
{
  "deployment": {"start": "15:30", "errors": 47},
  "pattern": "database_timeout",
  "frequency": "89%"
}
```

---

## Measuring Context Quality

### Metrics to Track

**1. Accuracy Rate**
- % of AI responses that are correct
- Target: >85% for production agents

**2. Token Efficiency**
- Average tokens per request
- Trend: Should decrease as you optimize

**3. Response Relevance**
- % of responses that are actionable
- Target: >90%

**4. Hallucination Rate**
- % of responses with false information
- Target: <5%

---

## Common Mistakes to Avoid

### Mistake 1: Assuming Context

❌ **Bad**:
```
"Check if the issue from yesterday is fixed"
```

✅ **Good**:
```
"Check if the database timeout issue (first detected on Oct 5 at 2pm,
ticket #1234, root cause: migration lock) is now resolved"
```

---

### Mistake 2: Overloading Context

❌ **Bad**:
```
[Send entire system documentation + all logs + all metrics]
```

✅ **Good**:
```
Relevant Documentation Section: Database Connection Pooling
Recent Logs: Last 50 error lines
Key Metrics: Database connections, query time, pool usage
```

---

### Mistake 3: Inconsistent Format

❌ **Bad**:
```
Sometimes JSON, sometimes plain text, sometimes markdown
```

✅ **Good**:
```
Always use consistent structured format:
- Context section
- Data section
- Task section
- Output format specification
```

---

### Mistake 4: No Validation

❌ **Bad**:
```
Accept any AI response as truth
```

✅ **Good**:
```
Validate AI responses against:
- Available data (did it cite real log lines?)
- Logical consistency (does reasoning make sense?)
- Constraints (did it follow output format?)
```

---

## Applying to Your Hybrid Agents

### For Deployment Health Agent

**Optimized Context Structure**:

```javascript
// n8n builds this context
const context = {
  // System role (constant)
  role: "Deployment health analyst for e-commerce platform",

  // Current situation (dynamic)
  deployment: {
    id: deploymentId,
    environment: "pre-production",
    started_at: timestamp,
    duration_minutes: calculateDuration()
  },

  // Error analysis (dynamic, filtered)
  errors: {
    total_count: errorCount,
    unique_types: getUniqueErrorTypes(),
    top_errors: getTop5Errors(), // Not all errors
    time_pattern: analyzeTimingPattern()
  },

  // System health (dynamic, summarized)
  metrics: {
    current: getCurrentMetrics(),
    baseline: getBaselineMetrics(),
    deviation: calculateDeviation()
  },

  // Task (specific)
  task: {
    action: "determine_root_cause",
    priority: "high",
    output_format: "structured_json"
  },

  // Constraints (validation)
  constraints: [
    "Cite specific error messages",
    "Compare to baseline metrics",
    "Confidence level required"
  ]
}

// Send to Claude
const prompt = buildPromptFromContext(context)
```

---

### For Performance Optimization Agent

**Progressive Context Loading**:

```javascript
// Step 1: Quick check
const quickContext = {
  role: "Performance analyst",
  metrics: {
    current_load_time: currentMetrics.load_time,
    baseline_load_time: baselineMetrics.load_time,
    threshold: performanceThreshold
  },
  task: "Is performance degraded? Yes/No"
}

const quickCheck = await callClaude(quickContext)

if (quickCheck.degraded === "Yes") {
  // Step 2: Deep analysis (only if needed)
  const deepContext = {
    ...quickContext,
    detailed_metrics: getDetailedMetrics(),
    recent_changes: getRecentDeployments(),
    resource_usage: getResourceMetrics(),
    task: "Determine root cause and recommend optimization"
  }

  const analysis = await callClaude(deepContext)
  return analysis
}
```

---

## Cost Optimization

### Token Cost Reduction Strategies

**1. Summarization**
- Reduce context by 80% through smart summarization
- Example: 1000-line log → 50-line summary

**2. Selective Context**
- Only include relevant data based on error type
- Saves 50-70% tokens on average

**3. Reference Instead of Repeat**
- Store common context externally
- Reference by ID instead of repeating
- Example: "Use troubleshooting guide #DB-001" vs. including full guide

**4. Batch Processing**
- Analyze multiple similar issues in one call
- Share context across related requests

**Expected Savings**:
- Without optimization: $0.10 per investigation
- With optimization: $0.02 per investigation
- **80% cost reduction**

---

## Testing Your Context Engineering

### Test Framework

**1. Accuracy Test**
```
Known Issue: Database timeout on Oct 5
Provide Context: Logs from that incident
Expected Output: Correctly identifies database timeout
Result: Pass/Fail
```

**2. Efficiency Test**
```
Measure: Tokens used to get correct answer
Target: <2000 tokens per investigation
Result: Track actual vs target
```

**3. Robustness Test**
```
Test: Provide incomplete/ambiguous data
Expected: AI should state "insufficient data"
Result: Does it hallucinate or ask for more?
```

---

## Implementation Checklist

For your hybrid n8n + AI agents:

- [ ] **Standardize context structure** across all agents
- [ ] **Create prompt templates** for each agent type
- [ ] **Implement progressive context loading** (start minimal, add as needed)
- [ ] **Add validation logic** (verify AI responses against data)
- [ ] **Track token usage** per agent per day
- [ ] **Measure accuracy** (log correct vs incorrect analyses)
- [ ] **Build context compression** (summarize instead of raw data)
- [ ] **Cache common context** (system docs, normal baselines)
- [ ] **Test edge cases** (missing data, ambiguous situations)
- [ ] **Document prompt patterns** (what works, what doesn't)

---

## Key Takeaways for Your Hybrid Agents

1. **Structure is everything**: Use consistent, hierarchical context format
2. **Less is more**: Start minimal, add context only when needed
3. **Validate always**: Don't trust AI blindly, verify against data
4. **Optimize relentlessly**: Track token usage, find savings
5. **Template your prompts**: Reusable patterns across agents
6. **Measure quality**: Accuracy, efficiency, relevance metrics
7. **Iterate based on results**: Learn from failures, improve prompts

---

## Next Steps

1. **Audit current prompts**: Review your existing n8n → AI workflows
2. **Identify improvements**: Where can you structure context better?
3. **A/B test**: Try optimized prompts vs current, measure difference
4. **Document winners**: Save successful prompt patterns
5. **Train team**: Share context engineering best practices

**Goal**: 80%+ accuracy, <2000 tokens per request, 90%+ actionable responses

This is the foundation for reliable, cost-effective production AI agents.
