#!/bin/bash
cd /Users/bgerby/Desktop/medium-articles-10-12

AUTH=$(echo -n 'bgerby@jaxondigital.com:'$(cat ~/.jira.d/.pass) | base64)

# Attach each PDF to corresponding JIRA ticket (GAT-151 through GAT-165)
curl -s -X POST -H "X-Atlassian-Token: no-check" -H "Authorization: Basic $AUTH" -F "file=@01-openai-nuked-startups.pdf" "https://jaxondigital.atlassian.net/rest/api/3/issue/GAT-151/attachments" > /dev/null && echo "GAT-151 ✓"

curl -s -X POST -H "X-Atlassian-Token: no-check" -H "Authorization: Basic $AUTH" -F "file=@02-claude-code-memory.pdf" "https://jaxondigital.atlassian.net/rest/api/3/issue/GAT-152/attachments" > /dev/null && echo "GAT-152 ✓"

curl -s -X POST -H "X-Atlassian-Token: no-check" -H "Authorization: Basic $AUTH" -F "file=@03-mcp-stdio-vs-sse.pdf" "https://jaxondigital.atlassian.net/rest/api/3/issue/GAT-153/attachments" > /dev/null && echo "GAT-153 ✓"

curl -s -X POST -H "X-Atlassian-Token: no-check" -H "Authorization: Basic $AUTH" -F "file=@04-mcp-servers-ddd.pdf" "https://jaxondigital.atlassian.net/rest/api/3/issue/GAT-154/attachments" > /dev/null && echo "GAT-154 ✓"

curl -s -X POST -H "X-Atlassian-Token: no-check" -H "Authorization: Basic $AUTH" -F "file=@05-a2a-mcp-10-minutes.pdf" "https://jaxondigital.atlassian.net/rest/api/3/issue/GAT-155/attachments" > /dev/null && echo "GAT-155 ✓"

curl -s -X POST -H "X-Atlassian-Token: no-check" -H "Authorization: Basic $AUTH" -F "file=@06-mcp-sse-streamable.pdf" "https://jaxondigital.atlassian.net/rest/api/3/issue/GAT-156/attachments" > /dev/null && echo "GAT-156 ✓"

curl -s -X POST -H "X-Atlassian-Token: no-check" -H "Authorization: Basic $AUTH" -F "file=@07-production-mcp-no-claude.pdf" "https://jaxondigital.atlassian.net/rest/api/3/issue/GAT-157/attachments" > /dev/null && echo "GAT-157 ✓"

curl -s -X POST -H "X-Atlassian-Token: no-check" -H "Authorization: Basic $AUTH" -F "file=@08-ai-garbage-code.pdf" "https://jaxondigital.atlassian.net/rest/api/3/issue/GAT-158/attachments" > /dev/null && echo "GAT-158 ✓"

curl -s -X POST -H "X-Atlassian-Token: no-check" -H "Authorization: Basic $AUTH" -F "file=@09-mcp-document-extraction.pdf" "https://jaxondigital.atlassian.net/rest/api/3/issue/GAT-159/attachments" > /dev/null && echo "GAT-159 ✓"

curl -s -X POST -H "X-Atlassian-Token: no-check" -H "Authorization: Basic $AUTH" -F "file=@10-ai-tools-solopreneur.pdf" "https://jaxondigital.atlassian.net/rest/api/3/issue/GAT-160/attachments" > /dev/null && echo "GAT-160 ✓"

curl -s -X POST -H "X-Atlassian-Token: no-check" -H "Authorization: Basic $AUTH" -F "file=@11-ai-interface-outgrows.pdf" "https://jaxondigital.atlassian.net/rest/api/3/issue/GAT-161/attachments" > /dev/null && echo "GAT-161 ✓"

curl -s -X POST -H "X-Atlassian-Token: no-check" -H "Authorization: Basic $AUTH" -F "file=@12-whatsapp-bot-n8n.pdf" "https://jaxondigital.atlassian.net/rest/api/3/issue/GAT-162/attachments" > /dev/null && echo "GAT-162 ✓"

curl -s -X POST -H "X-Atlassian-Token: no-check" -H "Authorization: Basic $AUTH" -F "file=@13-openai-killed-automation.pdf" "https://jaxondigital.atlassian.net/rest/api/3/issue/GAT-163/attachments" > /dev/null && echo "GAT-163 ✓"

curl -s -X POST -H "X-Atlassian-Token: no-check" -H "Authorization: Basic $AUTH" -F "file=@14-useless-skill.pdf" "https://jaxondigital.atlassian.net/rest/api/3/issue/GAT-164/attachments" > /dev/null && echo "GAT-164 ✓"

curl -s -X POST -H "X-Atlassian-Token: no-check" -H "Authorization: Basic $AUTH" -F "file=@15-windsurf-updates.pdf" "https://jaxondigital.atlassian.net/rest/api/3/issue/GAT-165/attachments" > /dev/null && echo "GAT-165 ✓"

echo ""
echo "All 15 PDFs attached successfully!"
