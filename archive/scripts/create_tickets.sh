#!/bin/bash

export JIRA_API_TOKEN=$(cat ~/.jira.d/.pass)

# Track results
declare -a tickets
declare -a failed

while IFS='|||' read -r title url; do
  # Clean up title (remove special characters that might cause issues)
  clean_title=$(echo "$title" | sed 's/["'\''`]//g')
  
  # Create description with URL
  description="Medium article from Oct 10, 2025 digest

Article URL: $url"
  
  # Create ticket
  echo "Creating ticket for: $clean_title"
  
  result=$(jira issue create -p GAT -t Task -s "Review: $clean_title" -b "$description" 2>&1)
  
  if [[ $result =~ GAT-[0-9]+ ]]; then
    ticket_key=$(echo "$result" | grep -o 'GAT-[0-9]*' | head -1)
    tickets+=("$ticket_key: $clean_title")
    echo "✓ Created: $ticket_key"
  else
    failed+=("$clean_title")
    echo "✗ Failed: $clean_title"
    echo "  Error: $result"
  fi
  
  # Small delay to avoid rate limiting
  sleep 1
done < articles-clean.txt

# Summary
echo ""
echo "=========================================="
echo "Summary"
echo "=========================================="
echo "Total articles processed: $(wc -l < articles-clean.txt)"
echo "Tickets created: ${#tickets[@]}"
echo "Failed: ${#failed[@]}"
echo ""

if [ ${#tickets[@]} -gt 0 ]; then
  echo "Created tickets:"
  printf '%s\n' "${tickets[@]}"
fi

if [ ${#failed[@]} -gt 0 ]; then
  echo ""
  echo "Failed articles:"
  printf '%s\n' "${failed[@]}"
fi
