#!/bin/bash
cd /Users/bgerby/Desktop/medium-articles-10-11

AUTH=$(echo -n 'bgerby@jaxondigital.com:'$(cat ~/.jira.d/.pass) | base64)

# Attach each PDF to corresponding JIRA ticket
curl -s -X POST -H "X-Atlassian-Token: no-check" -H "Authorization: Basic $AUTH" -F "file=@02-150-year-market-map-crash-predictions.pdf" "https://jaxondigital.atlassian.net/rest/api/3/issue/GAT-135/attachments" > /dev/null && echo "GAT-135 ✓"

curl -s -X POST -H "X-Atlassian-Token: no-check" -H "Authorization: Basic $AUTH" -F "file=@03-n8n-ai-automations-part-2.pdf" "https://jaxondigital.atlassian.net/rest/api/3/issue/GAT-136/attachments" > /dev/null && echo "GAT-136 ✓"

curl -s -X POST -H "X-Atlassian-Token: no-check" -H "Authorization: Basic $AUTH" -F "file=@04-build-ai-rig-local-llms.pdf" "https://jaxondigital.atlassian.net/rest/api/3/issue/GAT-137/attachments" > /dev/null && echo "GAT-137 ✓"

curl -s -X POST -H "X-Atlassian-Token: no-check" -H "Authorization: Basic $AUTH" -F "file=@05-llms-mcp-embeddings-context-windows.pdf" "https://jaxondigital.atlassian.net/rest/api/3/issue/GAT-138/attachments" > /dev/null && echo "GAT-138 ✓"

curl -s -X POST -H "X-Atlassian-Token: no-check" -H "Authorization: Basic $AUTH" -F "file=@06-15-next-gen-ai-tools-2030.pdf" "https://jaxondigital.atlassian.net/rest/api/3/issue/GAT-139/attachments" > /dev/null && echo "GAT-139 ✓"

curl -s -X POST -H "X-Atlassian-Token: no-check" -H "Authorization: Basic $AUTH" -F "file=@07-ai-producing-garbage-code.pdf" "https://jaxondigital.atlassian.net/rest/api/3/issue/GAT-140/attachments" > /dev/null && echo "GAT-140 ✓"

curl -s -X POST -H "X-Atlassian-Token: no-check" -H "Authorization: Basic $AUTH" -F "file=@08-agentic-ai-frameworks-comparison.pdf" "https://jaxondigital.atlassian.net/rest/api/3/issue/GAT-141/attachments" > /dev/null && echo "GAT-141 ✓"

curl -s -X POST -H "X-Atlassian-Token: no-check" -H "Authorization: Basic $AUTH" -F "file=@09-google-url-context-grounding.pdf" "https://jaxondigital.atlassian.net/rest/api/3/issue/GAT-142/attachments" > /dev/null && echo "GAT-142 ✓"

curl -s -X POST -H "X-Atlassian-Token: no-check" -H "Authorization: Basic $AUTH" -F "file=@10-claude-code-template-library.pdf" "https://jaxondigital.atlassian.net/rest/api/3/issue/GAT-143/attachments" > /dev/null && echo "GAT-143 ✓"

curl -s -X POST -H "X-Atlassian-Token: no-check" -H "Authorization: Basic $AUTH" -F "file=@11-ai-film-festival-screening.pdf" "https://jaxondigital.atlassian.net/rest/api/3/issue/GAT-144/attachments" > /dev/null && echo "GAT-144 ✓"

curl -s -X POST -H "X-Atlassian-Token: no-check" -H "Authorization: Basic $AUTH" -F "file=@12-build-ai-sidekick-claude-agents.pdf" "https://jaxondigital.atlassian.net/rest/api/3/issue/GAT-145/attachments" > /dev/null && echo "GAT-145 ✓"

curl -s -X POST -H "X-Atlassian-Token: no-check" -H "Authorization: Basic $AUTH" -F "file=@13-99-percent-ai-startups-dead-2026.pdf" "https://jaxondigital.atlassian.net/rest/api/3/issue/GAT-146/attachments" > /dev/null && echo "GAT-146 ✓"

curl -s -X POST -H "X-Atlassian-Token: no-check" -H "Authorization: Basic $AUTH" -F "file=@14-brutal-truth-ai-side-hustles.pdf" "https://jaxondigital.atlassian.net/rest/api/3/issue/GAT-147/attachments" > /dev/null && echo "GAT-147 ✓"

curl -s -X POST -H "X-Atlassian-Token: no-check" -H "Authorization: Basic $AUTH" -F "file=@15-conversation-design-playbook-2025.pdf" "https://jaxondigital.atlassian.net/rest/api/3/issue/GAT-148/attachments" > /dev/null && echo "GAT-148 ✓"

echo "All PDFs attached successfully!"
