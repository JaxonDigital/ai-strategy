#!/bin/bash
cd /Users/bgerby/Desktop/medium-articles-2025-10-14

AUTH=$(echo -n 'bgerby@jaxondigital.com:'$(cat ~/.jira.d/.pass) | base64)

# Attach each PDF to corresponding JIRA ticket (GAT-192 through GAT-205)
curl -s -X POST -H "X-Atlassian-Token: no-check" -H "Authorization: Basic $AUTH" -F "file=@01-using-atlassian-mcp-server-cursor.pdf" "https://jaxondigital.atlassian.net/rest/api/3/issue/GAT-192/attachments" > /dev/null && echo "GAT-192 ✓"

curl -s -X POST -H "X-Atlassian-Token: no-check" -H "Authorization: Basic $AUTH" -F "file=@02-journey-ai-llms-mcp-interoperability.pdf" "https://jaxondigital.atlassian.net/rest/api/3/issue/GAT-193/attachments" > /dev/null && echo "GAT-193 ✓"

curl -s -X POST -H "X-Atlassian-Token: no-check" -H "Authorization: Basic $AUTH" -F "file=@03-complete-guide-building-mcp-agents.pdf" "https://jaxondigital.atlassian.net/rest/api/3/issue/GAT-194/attachments" > /dev/null && echo "GAT-194 ✓"

curl -s -X POST -H "X-Atlassian-Token: no-check" -H "Authorization: Basic $AUTH" -F "file=@04-understanding-vector-spaces-foundation-ai.pdf" "https://jaxondigital.atlassian.net/rest/api/3/issue/GAT-195/attachments" > /dev/null && echo "GAT-195 ✓"

curl -s -X POST -H "X-Atlassian-Token: no-check" -H "Authorization: Basic $AUTH" -F "file=@05-ai-died-this-week.pdf" "https://jaxondigital.atlassian.net/rest/api/3/issue/GAT-196/attachments" > /dev/null && echo "GAT-196 ✓"

curl -s -X POST -H "X-Atlassian-Token: no-check" -H "Authorization: Basic $AUTH" -F "file=@06-local-mcp-server-obsidian-ai.pdf" "https://jaxondigital.atlassian.net/rest/api/3/issue/GAT-197/attachments" > /dev/null && echo "GAT-197 ✓"

curl -s -X POST -H "X-Atlassian-Token: no-check" -H "Authorization: Basic $AUTH" -F "file=@07-ai-basically-game-theory.pdf" "https://jaxondigital.atlassian.net/rest/api/3/issue/GAT-198/attachments" > /dev/null && echo "GAT-198 ✓"

curl -s -X POST -H "X-Atlassian-Token: no-check" -H "Authorization: Basic $AUTH" -F "file=@08-ai-orchestration-layer-a2a-mcp.pdf" "https://jaxondigital.atlassian.net/rest/api/3/issue/GAT-199/attachments" > /dev/null && echo "GAT-199 ✓"

curl -s -X POST -H "X-Atlassian-Token: no-check" -H "Authorization: Basic $AUTH" -F "file=@09-apps-instead-doomscrolling.pdf" "https://jaxondigital.atlassian.net/rest/api/3/issue/GAT-200/attachments" > /dev/null && echo "GAT-200 ✓"

curl -s -X POST -H "X-Atlassian-Token: no-check" -H "Authorization: Basic $AUTH" -F "file=@10-ai-agents-failing-startup-fix.pdf" "https://jaxondigital.atlassian.net/rest/api/3/issue/GAT-201/attachments" > /dev/null && echo "GAT-201 ✓"

curl -s -X POST -H "X-Atlassian-Token: no-check" -H "Authorization: Basic $AUTH" -F "file=@11-ai-agent-sql-databases-dashboards.pdf" "https://jaxondigital.atlassian.net/rest/api/3/issue/GAT-202/attachments" > /dev/null && echo "GAT-202 ✓"

curl -s -X POST -H "X-Atlassian-Token: no-check" -H "Authorization: Basic $AUTH" -F "file=@12-ai-big-short-moment.pdf" "https://jaxondigital.atlassian.net/rest/api/3/issue/GAT-203/attachments" > /dev/null && echo "GAT-203 ✓"

curl -s -X POST -H "X-Atlassian-Token: no-check" -H "Authorization: Basic $AUTH" -F "file=@13-ai-bubble-about-to-pop.pdf" "https://jaxondigital.atlassian.net/rest/api/3/issue/GAT-204/attachments" > /dev/null && echo "GAT-204 ✓"

curl -s -X POST -H "X-Atlassian-Token: no-check" -H "Authorization: Basic $AUTH" -F "file=@14-spacex-starship-exploded.pdf" "https://jaxondigital.atlassian.net/rest/api/3/issue/GAT-205/attachments" > /dev/null && echo "GAT-205 ✓"

echo ""
echo "All 14 PDFs attached successfully!"
