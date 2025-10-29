#!/bin/bash
# Fix missing URLs and add assessments to JIRA tickets
# This script manually fixes tickets GAT-479 through GAT-491

set -e

JIRA_API_TOKEN="`cat ~/.jira.d/.pass`"
export JIRA_API_TOKEN

echo "=== FIXING JIRA TICKETS WITH MISSING URLS AND ASSESSMENTS ==="
echo ""

# Ticket data: TICKET_ID|ARTICLE_URL
declare -a tickets=(
  "GAT-479|https://medium.com/@yumaueno/i-spent-40-hours-testing-perplexitys-secret-42-page-work-guide-2e2fb0e6f8d3"
  "GAT-480|https://medium.com/@shahedk/dexter-ai-the-self-improving-financial-research-assistant-that-thinks-like-an-analyst-0c50dc8ca5c7"
  "GAT-481|https://medium.com/@lucianosphere/building-a-documentation-generator-your-agents-first-useful-job-b67c5db05b2d"
  "GAT-482|https://medium.com/@alirezarezvani/claude-code-v2-0-28-86f2126ad2d1"
  "GAT-483|https://medium.com/@alirezarezvani/the-most-expensive-context-engineering-mistake-every-cto-makes-6fca4d18d520"
  "GAT-485|https://medium.com/@ris3abh/building-a-text-to-sql-chatbot-with-rag-langchain-fastapi-and-streamlit-32c681a0d4ad"
  "GAT-486|https://medium.com/@howtoarchitect/why-ctos-should-fear-shadow-agents-more-than-they-ever-feared-shadow-it-64e0e0f9104f"
  "GAT-487|https://medium.com/@kamyar_mohseni/9-ai-skills-you-must-learn-before-everyone-else-does-or-get-left-behind-6cbea0993fc4"
  "GAT-488|https://medium.com/@ranthebuilder/i-tried-running-an-mcp-server-on-aws-lambda-heres-what-happened-7d2c73096c19"
  "GAT-489|https://medium.com/@moeinmoeinnia/libra-ai-an-open-source-alternative-to-v0-and-lovable-7da17b1b4d58"
  "GAT-491|https://medium.com/@yumaueno/meet-nico-who-sold-an-ai-tool-built-in-48-hours-for-65k-and-then-another-one-built-in-1-week-1d27d2351b19"
)

echo "Step 1: Fixing URLs in ticket descriptions..."
echo ""

for item in "${tickets[@]}"; do
  ticket="${item%%|*}"
  url="${item##*|}"

  echo "Processing $ticket..."

  # Get current description
  current_desc=$(jira issue view "$ticket" 2>/dev/null | sed -n '/Description/,/View this issue/p' | sed '1d;$d' | sed 's/^  //')

  if [ -z "$current_desc" ]; then
    echo "  ✗ Could not fetch ticket"
    continue
  fi

  # Check if URL needs fixing
  if echo "$current_desc" | grep -q "Article URL: Unknown\|Article URL:\*\* Unknown"; then
    # Build new description with correct URL
    new_desc=$(echo "$current_desc" | sed "s|Article URL: Unknown|**Article URL:** $url|g" | sed "s|Article URL:\*\* Unknown|**Article URL:** $url|g")

    # Write to temp file
    echo "$new_desc" > /tmp/jira_desc_$ticket.txt

    # Update ticket
    if jira issue edit "$ticket" -b "$(cat /tmp/jira_desc_$ticket.txt)" --no-input -p GAT 2>/dev/null; then
      echo "  ✓ Updated URL"
    else
      echo "  ✗ Update failed"
    fi

    rm /tmp/jira_desc_$ticket.txt
  else
    echo "  ⊙ URL already present"
  fi
done

echo ""
echo "=== URL FIXES COMPLETE ==="
echo ""
echo "Note: Assessment comments need to be added manually or via the Python script"
echo "once the JIRA CLI environment issue is resolved."
echo ""
echo "Created fix scripts:"
echo "  - /Users/bgerby/Documents/dev/ai/scripts/fix-jira-tickets.sh (this script)"
echo "  - /Users/bgerby/Documents/dev/ai/scripts/fix-missing-urls-and-assessments.py (Python version)"
echo "  - /Users/bgerby/Documents/dev/ai/scripts/audit-and-fix-jira-tickets.py (General purpose)"
