# AI-Powered E2E Testing with Playwright MCP + GitHub MCP

**Status**: Complete
**Date**: October 7, 2025
**Source**: Kailash Pathak article (Sept 2025) - practical implementation guide
**Relevance**: MCP orchestration workflow, testing automation, DevOps integration
**Experience Level**: We've used both Playwright MCP and GitHub MCP

## Executive Summary

This article demonstrates a **production-ready workflow combining Playwright MCP and GitHub MCP** to fully automate E2E testing from code generation → git operations → CI/CD execution. The workflow reduces manual effort from hours to minutes by using AI (GitHub Copilot) to generate structured test code, then GitHub MCP to automate branch creation, code push, and GitHub Actions triggering.

**Key Innovation**: MCP **orchestration** - multiple MCP servers working together to automate an entire workflow, not just isolated tasks.

**For Jaxon Digital**: This validates our "hybrid agent testing playbook" and demonstrates how MCP can automate DevOps workflows for clients, not just development tasks. Directly applicable to Optimizely testing workflows.

---

## The Problem Being Solved

### Traditional E2E Testing Pain Points

**Manual tasks consuming significant time**:
1. Writing boilerplate test framework code
2. Creating Page Object Model (POM) structure
3. Setting up git repository and branches
4. Pushing code to GitHub
5. Configuring GitHub Actions workflows
6. Manually triggering CI/CD pipelines

**Time cost**: Hours to days for setup + ongoing maintenance

**Error-prone**: Manual git operations, copy-paste errors, CI/CD config mistakes

---

## The MCP-Powered Solution

### Architecture: Two MCPs, One Workflow

```
┌─────────────────────────────────────────────────────────┐
│                    VS Code + Copilot                     │
│                  (AI Orchestration Layer)                │
└────────┬──────────────────────────────────┬─────────────┘
         │                                  │
         ▼                                  ▼
┌────────────────────┐          ┌─────────────────────────┐
│  Playwright MCP    │          │    GitHub MCP           │
│                    │          │                         │
│  - Generate tests  │          │  - Create branches      │
│  - Page Objects    │          │  - Push code            │
│  - Browser actions │          │  - Trigger workflows    │
│  - Test execution  │          │  - Query CI/CD status   │
└────────────────────┘          └─────────────────────────┘
```

**Key Insight**: The AI agent (Copilot) coordinates between **two MCPs** to execute a multi-step workflow spanning development AND operations.

---

## The Workflow: Step-by-Step

### Phase 1: Setup (One-Time)

#### Playwright MCP Setup

**Method 1: CLI Command (Quickest)**
```bash
# For VS Code Stable
code --add-mcp '{"name":"playwright","command":"npx","args":["@playwright/mcp@latest"]}'

# For VS Code Insiders
code-insiders --add-mcp '{"name":"playwright","command":"npx","args":["@playwright/mcp@latest"]}'
```

**Method 2: Manual settings.json**
```json
{
  "mcp": {
    "servers": {
      "playwright": {
        "command": "npx",
        "args": ["@playwright/mcp@latest"]
      }
    }
  }
}
```

**Playwright MCP Tools Available**:
- `start_codegen_session` - Start recording browser actions
- `end_codegen_session` - Generate test file from session
- `playwright_navigate` - Navigate to URL
- `playwright_screenshot` - Take screenshot
- `playwright_click` - Click element
- `playwright_fill` - Fill form field
- `playwright_select` - Select dropdown
- `playwright_evaluate` - Execute JavaScript
- Plus iframe interactions, hover, etc.

---

#### GitHub MCP Setup

**Prerequisites**:
- Docker installed
- GitHub Personal Access Token (PAT) with repo permissions

**Configuration in settings.json**:
```json
{
  "mcp": {
    "servers": {
      "github": {
        "command": "docker",
        "args": [
          "run",
          "-i",
          "--rm",
          "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
          "mcp/github"
        ],
        "env": {
          "GITHUB_PERSONAL_ACCESS_TOKEN": "${input:github_token}"
        }
      }
    }
  }
}
```

**How it works**:
- Runs GitHub MCP in Docker container
- Passes PAT as environment variable
- `${input:github_token}` prompts for token (stored securely)

**GitHub MCP Capabilities**:
- Create/manage repositories
- Create/switch branches
- Push code
- Trigger GitHub Actions
- Query workflow status
- Create pull requests
- Manage issues

---

### Phase 2: AI-Driven Test Generation

#### Example Prompt (given in article)

```
Create a POM model for below steps using Playwright and JavaScript:

1. Open https://www.saucedemo.com/
2. Login with username and password
3. Add product "Sauce Labs Backpack" into the cart
4. Open the cart
5. Click on Checkout button
6. Fill random data in First Name, Last Name and Zip
7. Click on continue button
8. Click on Finish button
9. Verify message "Thank you for your order!"
```

#### What Copilot + Playwright MCP Does

**Automatically generates**:
1. Complete project structure:
   ```
   ├── tests/
   │   ├── saucedemo.spec.js
   ├── pages/
   │   ├── LoginPage.js
   │   ├── ProductsPage.js
   │   ├── CartPage.js
   │   ├── CheckoutPage.js
   ├── data/
   │   ├── testData.js
   ├── playwright.config.js
   ├── package.json
   ```

2. Page Object Model classes with proper selectors
3. Test spec using the page objects
4. Test data fixtures
5. Playwright configuration

**Result**: Production-ready POM framework in ~5 minutes

---

### Phase 3: Git Operations via GitHub MCP

#### Create Branch via Prompt

**Prompt**: "Create Branch with name 'e2eMCPTesting'"

**What happens**:
1. GitHub Copilot recognizes git operation intent
2. Calls GitHub MCP `create_branch` tool
3. Creates local branch
4. Switches to new branch

**Behind the scenes**:
```bash
# Equivalent manual commands:
git checkout -b e2eMCPTesting
```

---

#### Push Code via Prompt

**Prompt**: "Push the code on The remote repository URL https://github.com/<owner>/e2eMCPTesting"

**What GitHub MCP does**:
1. Adds remote if not exists
2. Stages all files
3. Creates commit with descriptive message
4. Pushes to remote branch

**Behind the scenes**:
```bash
# Equivalent manual commands:
git remote add origin <url>
git add .
git commit -m "Initial commit with e2e testing setup"
git push -u origin e2eMCPTesting
```

**Critical Security Point**: Requires GitHub PAT to be configured properly, otherwise push fails with authentication error.

---

### Phase 4: CI/CD Automation

#### Trigger GitHub Actions via Prompt

**Prompt**: "Run the test cases in GitHub Actions"

**What GitHub MCP does**:
1. Checks if GitHub Actions workflow exists
2. If not, creates `.github/workflows/playwright.yml`
3. Commits and pushes workflow file
4. Triggers workflow run

**Generated Workflow File**:
```yaml
name: Playwright Tests
on:
  push:
    branches: [ e2eMCPTesting ]
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - name: Install dependencies
        run: npm ci
      - name: Install Playwright
        run: npx playwright install --with-deps
      - name: Run tests
        run: npx playwright test
      - uses: actions/upload-artifact@v3
        if: always()
        with:
          name: playwright-report
          path: playwright-report/
```

**Result**: Tests execute in GitHub Actions within minutes

---

### Phase 5: CI/CD Interaction via Prompts

#### Example Interactions

**Prompt 1**: "Can you check for me in GitHub action is all test cases are passed in last code push"

**Response**:
- Queries GitHub Actions API via GitHub MCP
- Returns: "3 workflow runs. Latest (#3) currently running. Previous runs (#1, #2) completed successfully."
- Provides links to workflow runs

---

**Prompt 2**: "In GitHub action Re-run previous job"

**Response**:
- Triggers re-run of specified workflow

---

**Prompt 3**: "In GitHub action run the test cases only for webkit browser"

**Response**:
1. Modifies `playwright.config.js` to comment out Chrome/Firefox
2. Commits change
3. Pushes to branch
4. Triggers new workflow run
5. Confirms: "Tests now running for WebKit only"

**This is remarkable**: The AI agent modifies config, commits, pushes, and triggers CI/CD **all from a single natural language prompt**.

---

## Playwright MCP Tools Demonstrated

Based on the article screenshots, Playwright MCP provides:

### Code Generation Tools
- `start_codegen_session` - Begin recording
- `end_codegen_session` - Generate test file
- `get_codegen_session` - Check session status
- `clear_codegen_session` - Reset without generating

### Browser Interaction Tools
- `playwright_navigate` - Go to URL
- `playwright_click` - Click element
- `playwright_fill` - Fill input field
- `playwright_select` - Select dropdown
- `playwright_hover` - Hover over element
- `playwright_screenshot` - Capture screenshot
- `playwright_iframe_click` - Click in iframe
- `playwright_iframe_fill` - Fill field in iframe
- `playwright_evaluate` - Execute JavaScript

**Total**: 26 cached tools shown in screenshot

---

## GitHub MCP Capabilities (Inferred from Article)

Based on demonstrated functionality:

### Repository Operations
- `create_repository` - Create new repo
- `get_repository` - Query repo info

### Branch Operations
- `create_branch` - Create and switch branch
- `get_branches` - List branches

### Commit & Push
- `create_commit` - Stage and commit files
- `push_code` - Push to remote

### GitHub Actions
- `create_workflow` - Generate workflow file
- `trigger_workflow` - Manual workflow dispatch
- `get_workflow_runs` - Query run history/status
- `rerun_workflow` - Re-trigger previous run

### Configuration
- `update_file` - Modify files (like playwright.config.js)

---

## Security Considerations (From Article)

### GitHub PAT Best Practices

**DO**:
- ✅ Create **fine-grained** Personal Access Tokens with minimal scope
- ✅ Store PATs as **encrypted secrets** in GitHub Actions
- ✅ Use `${input:github_token}` for secure local storage
- ✅ Set expiration dates on tokens
- ✅ Restrict token to specific repositories

**DON'T**:
- ❌ Store PATs in plain text in config files
- ❌ Commit PATs to repositories
- ❌ Use broad-scope tokens (full repo access)
- ❌ Share tokens across projects

### AI-Generated Code Review

**Critical**: "Never push AI-generated code blindly"

**Review for**:
- Skipped validations
- Insecure selectors (e.g., relying on IDs that could change)
- Weak test assertions
- Missing error handling
- Configurations that weaken reliability

**Example Risk**: AI might generate:
```javascript
// RISKY: Too generic
await page.click('button');

// BETTER: Specific and stable
await page.click('[data-test-id="checkout-button"]');
```

### Dependency Management

**Keep updated**:
- Playwright (@playwright/test)
- MCP servers (@playwright/mcp@latest, mcp/github)
- Docker images
- GitHub Actions

**Why**: Known vulnerabilities in outdated dependencies could expose CI/CD pipeline

### Access Controls

**Restrict**:
- Who can trigger MCP-powered workflows
- Who has write access to MCP configurations
- What logs are captured (don't leak secrets)

---

## Strategic Implications for Jaxon Digital

### 1. MCP Orchestration Pattern Validated

**What we learned**: Combining multiple MCPs creates exponentially more value than single-MCP solutions.

**Application**:
- Optimizely MCP + GitHub MCP = Complete deployment automation
- Optimizely MCP + Slack MCP = Deployment notifications
- Optimizely MCP + Log Analyzer MCP = Post-deployment validation

**Service Offering**: "Multi-MCP Orchestration Workflows" ($30-50K)
- Design workflow combining 2-3 MCPs
- Implement prompt-driven automation
- Train client team on orchestration patterns

---

### 2. Testing as a Service Opportunity

**Proven Workflow**: Playwright MCP + GitHub MCP = End-to-end testing automation

**For Optimizely Clients**:

**Service**: "Optimizely E2E Testing Automation" ($25-40K)

**What we deliver**:
1. Playwright MCP configured for Optimizely testing
2. Page Object Models for common Optimizely UI patterns
3. GitHub MCP integration for CI/CD
4. Library of reusable test prompts
5. GitHub Actions workflows for scheduled testing

**Value Prop**: "AI-generated tests for every Optimizely deployment"

**Workflow**:
```
Developer: "Test the new product listing page"
   ↓
Copilot + Playwright MCP: Generates POM + test
   ↓
GitHub MCP: Commits, pushes, triggers CI/CD
   ↓
Results: Automated testing in 5 minutes
```

---

### 3. DevOps Automation Beyond Code

**Insight**: GitHub MCP automates **operational tasks**, not just development

**Capabilities demonstrated**:
- Branch creation
- Code push
- Workflow triggering
- Configuration modification
- Status checking
- Re-running jobs

**Jaxon Digital Application**:

**Client Pain Point**: "Deploying Optimizely changes requires 15 manual steps"

**Solution**: "Prompt-Driven Deployment Workflow"

**Example Prompt**: "Deploy content changes to Optimizely staging environment"

**What happens** (via orchestrated MCPs):
1. Optimizely MCP: Export content
2. GitHub MCP: Create deployment branch
3. GitHub MCP: Commit content export
4. GitHub MCP: Push to remote
5. GitHub MCP: Trigger deployment workflow
6. Slack MCP: Notify team of deployment status

**Time savings**: 30 minutes → 2 minutes

**Service**: "Prompt-Driven Deployment Automation" ($40-60K)

---

### 4. The "Hybrid Agent Testing Playbook" Validated

**Our existing document** (`hybrid-agent-testing-playbook.md`) proposed:
- Using Playwright MCP for test generation
- Combining multiple MCPs for workflows
- AI-driven test maintenance

**This article proves**:
- ✅ Playwright MCP works for production testing
- ✅ Multiple MCPs can orchestrate complex workflows
- ✅ Natural language prompts can replace manual DevOps tasks
- ✅ Workflow reduces time from hours to minutes

**Action**: Update our playbook with specific GitHub MCP integration patterns from this article

---

### 5. Security Framework for Client MCP Deployments

**Client Concern**: "Is it safe to let AI push code to GitHub?"

**Our Answer** (based on this article's security section):

**3-Layer Security Model**:

**Layer 1: Token Security**
- Fine-grained PATs with minimal scope
- Tokens stored as encrypted secrets
- Regular rotation (30-90 days)
- Separate tokens for dev/staging/prod

**Layer 2: Code Review Gate**
- AI generates → Human reviews → Push
- Automated checks for security issues
- Required approvals for production changes

**Layer 3: Audit & Rollback**
- All AI-generated commits tagged
- Easy rollback mechanism
- Audit logs of all MCP operations

**Service Component**: "MCP Security Assessment" ($8-12K)
- Review client's CI/CD security posture
- Design token management strategy
- Implement code review workflows
- Set up audit logging

---

### 6. The "Infrastructure as Prompts" Vision

**What this article demonstrates**: Infrastructure operations can be driven by natural language prompts, not just code.

**Examples from article**:
- "Create branch with name X" → Branch created
- "Push code to GitHub" → Code pushed
- "Run tests in GitHub Actions" → Workflow triggered
- "Run tests only for WebKit" → Config modified, pushed, executed

**This is bigger than testing**: It's a paradigm shift in DevOps.

**Jaxon Digital Positioning**: "Infrastructure as Prompts for Optimizely Operations"

**Vision**:
```
Project Manager: "Deploy the homepage redesign to staging"
   ↓
AI Agent: [Orchestrates 5 MCPs to execute deployment]
   ↓
Result: Deployment complete, validation tests passed
```

**This is the future we should be building toward.**

---

## Comparison: Manual vs. MCP-Powered Testing

### Traditional Manual Workflow

| Step | Time | Complexity |
|------|------|------------|
| 1. Set up Playwright project | 30 min | Medium |
| 2. Create folder structure | 15 min | Low |
| 3. Write Page Object Models | 2 hours | High |
| 4. Write test specs | 1 hour | Medium |
| 5. Configure playwright.config.js | 20 min | Medium |
| 6. Set up Git repository | 10 min | Low |
| 7. Create GitHub Actions workflow | 45 min | High |
| 8. Push code to GitHub | 5 min | Low |
| 9. Trigger and monitor CI/CD | 10 min | Low |
| **Total** | **~5 hours** | **High** |

### MCP-Powered Workflow

| Step | Time | Complexity |
|------|------|------------|
| 1. Write test scenario prompt | 2 min | Low |
| 2. AI generates complete framework | 3 min | Zero (automated) |
| 3. Review generated code | 5 min | Low |
| 4. Prompt: "Create branch" | 1 min | Zero |
| 5. Prompt: "Push code" | 1 min | Zero |
| 6. Prompt: "Run in GitHub Actions" | 1 min | Zero |
| 7. Monitor results | 2 min | Low |
| **Total** | **~15 minutes** | **Low** |

**Time Savings**: 95% reduction (5 hours → 15 minutes)

**Complexity Reduction**: Eliminates need for deep Playwright/GitHub Actions expertise

---

## Practical Prompts Library

Based on the article, here are production-ready prompts:

### Test Generation

```
Create a POM model for below steps using Playwright and JavaScript:
1. Open [URL]
2. [Action 1]
3. [Action 2]
...
N. Verify [expected outcome]
```

### Git Operations

```
Create branch with name "[branch-name]"

Push the code to the remote repository URL [github-url]

Commit these changes with message "[message]"
```

### CI/CD Operations

```
Run the test cases in GitHub Actions

Run the test cases only for [browser-name] browser

Re-run previous job in GitHub Actions

Check if all test cases passed in the last code push
```

### Configuration Changes

```
Update playwright.config.js to run tests only on [browser]

Add test for [specific scenario] to the existing test suite

Modify the [component] page object to include [new element]
```

---

## Limitations & When NOT to Use This Approach

### 1. Complex Custom Logic

**When AI struggles**:
- Complex authentication flows (OAuth, SAML)
- Multi-step business logic with edge cases
- Integration with proprietary APIs

**Solution**: Use MCP for scaffolding, manual code for complex logic

---

### 2. Non-Standard Test Patterns

**When POM doesn't fit**:
- Performance testing
- Visual regression testing
- API contract testing

**Solution**: Use Playwright MCP for UI tests, other tools for specialized testing

---

### 3. Highly Regulated Environments

**When automation is risky**:
- Production deployments requiring multiple approvals
- Compliance requirements for manual review
- Security-critical changes

**Solution**: Use MCP for lower environments, manual process for production

---

### 4. Legacy Applications

**When selectors are unstable**:
- Apps without test IDs or stable selectors
- Frequent UI changes
- Dynamic content rendering

**Solution**: Invest in adding data-testid attributes first, then use MCP

---

## Implementation Roadmap for Jaxon Digital

### Phase 1: Internal Proof of Concept (2 weeks)

**Goal**: Validate workflow with Optimizely test site

**Tasks**:
1. Set up Playwright MCP + GitHub MCP in VS Code
2. Create test GitHub repository
3. Generate sample Optimizely CMS tests via prompts
4. Push to GitHub via prompt
5. Run in GitHub Actions via prompt
6. Document learnings and pitfalls

**Deliverable**: Internal demo video + documentation

---

### Phase 2: Client Pilot (4-6 weeks, $25-35K)

**Goal**: Implement for one client's Optimizely environment

**Scope**:
- Set up Playwright MCP for client's Optimizely instance
- Configure GitHub MCP with client's GitHub org
- Create library of 10-15 common test scenarios
- Train 2-3 client team members on prompts
- Implement security controls (PAT management, code review)

**Success Metrics**:
- Test generation time reduced by 80%+
- Client team can independently create new tests
- Zero security incidents
- 95%+ test success rate in CI/CD

---

### Phase 3: Productize (Q1 2026)

**Goal**: Repeatable service offering

**Components**:
1. **"AI Testing Starter Kit"** ($15-25K)
   - Playwright + GitHub MCP setup
   - 20 pre-built test templates
   - Prompt library documentation
   - 2-day training workshop

2. **"Advanced Test Orchestration"** ($30-50K)
   - Multi-MCP workflows (Playwright + GitHub + Optimizely)
   - Custom test scenarios
   - Integration with client's existing CI/CD
   - Ongoing support (3 months)

3. **"Managed AI Testing Service"** ($5-10K/month)
   - We maintain MCP infrastructure
   - Monthly test scenario updates
   - Monitoring and issue resolution
   - Regular reporting

---

## Lessons Learned (From Article + Our Experience)

### What Works Well

1. **POM generation**: AI excels at creating structured Page Object Models
2. **Git automation**: GitHub MCP handles routine git operations flawlessly
3. **Workflow orchestration**: Multiple MCPs work together seamlessly
4. **Natural language interface**: Non-technical users can trigger complex workflows
5. **Rapid iteration**: Modifying tests is as easy as new prompt

### What Needs Human Oversight

1. **Selector quality**: AI-generated selectors may not be optimal
2. **Test coverage**: AI doesn't know business-critical paths
3. **Edge cases**: Complex scenarios require human test design
4. **Security review**: PATs and permissions need careful configuration
5. **Workflow design**: Multi-step orchestration needs upfront planning

### Best Practices

1. **Start simple**: Basic tests first, complex scenarios later
2. **Review everything**: Never blindly trust AI-generated code
3. **Use data-testid**: Add stable selectors to applications first
4. **Version control workflows**: Treat GitHub Actions like code
5. **Iterate on prompts**: Refine prompts based on output quality

---

## Competitive Analysis

### What Other Vendors Are Doing

**Testing Tool Vendors** (Selenium, Cypress, etc.):
- No MCP integration announced
- Some have AI code generation (Copilot integration)
- None have full DevOps orchestration like GitHub MCP

**CI/CD Platforms** (GitHub, GitLab, etc.):
- GitHub Actions + GitHub MCP = native advantage
- GitLab has no MCP story yet
- CircleCI, Jenkins, etc. - no MCP integration

**Optimizely Partners**:
- Not discussing AI-powered testing
- Traditional manual test approach
- No MCP awareness

**Our Advantage**: First mover in "MCP-orchestrated Optimizely testing"

---

## Open Questions & Next Steps

### Questions to Investigate

1. **Playwright MCP + Optimizely MCP**: Can we orchestrate both for "test + fix" workflows?
   - Example: Test fails → Optimizely MCP suggests content fix

2. **Cost at scale**: What's the compute cost for running AI-generated tests in CI/CD?
   - Need to measure: GitHub Actions minutes, LLM API calls

3. **Test maintenance**: How well do AI-generated tests hold up over time?
   - Track: How often do selectors break, false positive rate

4. **Client adoption**: Will non-technical users actually use prompt-driven testing?
   - Need: User research with actual client team members

### Next Steps

1. **Update hybrid-agent-testing-playbook.md** with GitHub MCP patterns
2. **Create internal demo** showing Playwright MCP + GitHub MCP workflow
3. **Document security framework** for client MCP deployments
4. **Develop prompt library** specific to Optimizely testing scenarios
5. **Reach out to article author** (Kailash Pathak) - potential collaboration/guest post?

---

## Conclusion

This article provides a **production-ready blueprint** for combining Playwright MCP and GitHub MCP to automate the entire E2E testing workflow. The key innovation is **MCP orchestration**—using multiple MCP servers together creates exponentially more value than isolated MCP usage.

### Key Takeaways

1. **MCP orchestration is real**: Multiple MCPs can work together seamlessly
2. **DevOps automation**: GitHub MCP extends AI beyond code generation into operations
3. **Prompt-driven infrastructure**: Natural language can replace manual DevOps tasks
4. **Time savings are massive**: 95% reduction in test setup time
5. **Security is manageable**: With proper PAT management and code review
6. **Client opportunity**: This workflow is directly applicable to Optimizely testing

### Strategic Positioning for Jaxon Digital

**We should be the first Optimizely partner to offer**:
- MCP-orchestrated testing workflows
- Prompt-driven Optimizely deployments
- Multi-MCP DevOps automation

**The future is "Infrastructure as Prompts"**—and we have the expertise to build it.

---

## References

- **Kailash Pathak** (Sept 2025): "AI Powered end to end (E2E) Testing with Playwright MCP and GitHub MCP" (Medium)
- Playwright MCP: Official Playwright MCP documentation
- GitHub MCP: Official GitHub MCP server
- Our previous work: `hybrid-agent-testing-playbook.md`

---

**Related Documents**:
- `hybrid-agent-testing-playbook.md` - Our existing testing strategy (now validated)
- `mcps-vs-agents-strategic-analysis.md` - MCP architecture overview
- `n8n-mcp-integration-analysis.md` - Alternative orchestration approach
- `q4-2025-revenue-strategy.md` - Service offering pricing
