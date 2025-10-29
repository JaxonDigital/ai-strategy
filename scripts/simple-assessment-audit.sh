#!/bin/bash
# Simple audit: Query all Review tickets and check for assessment comments

set -e

JIRA_API_TOKEN="`cat ~/.jira.d/.pass`"
export JIRA_API_TOKEN

echo "=== SIMPLE JIRA TICKET ASSESSMENT AUDIT ==="
echo ""

# Step 1: Get all Review tickets
echo "Step 1: Querying all 'Review:' tickets from GAT project..."
jira issue list -p GAT --plain 2>/dev/null | grep "Review:" > /tmp/review_tickets_raw.txt || true

if [ ! -s /tmp/review_tickets_raw.txt ]; then
  echo "✗ No Review tickets found or JIRA query failed"
  exit 1
fi

# Extract ticket IDs
awk '{print $1}' /tmp/review_tickets_raw.txt > /tmp/review_ticket_ids.txt
TOTAL_TICKETS=$(wc -l < /tmp/review_ticket_ids.txt | tr -d ' ')
echo "✓ Found $TOTAL_TICKETS Review tickets"
echo ""

# Step 2: Check each ticket for assessment comments
echo "Step 2: Checking each ticket for assessment comments..."
> /tmp/missing_assessments_simple.txt
> /tmp/has_assessments_simple.txt
checked=0
missing=0
has_assessment=0

while IFS= read -r ticket_id; do
  checked=$((checked + 1))
  printf "[$checked/$TOTAL_TICKETS] $ticket_id... "

  # Get ticket details
  ticket_output=$(jira issue view "$ticket_id" 2>/dev/null)

  if [ $? -ne 0 ]; then
    echo "✗ Could not fetch"
    continue
  fi

  # Count comments
  comment_count=$(echo "$ticket_output" | grep -c "💭" || true)

  # Check for assessment-related keywords
  has_relevance=$(echo "$ticket_output" | grep -c "Relevance Summary:" || true)
  has_strategic=$(echo "$ticket_output" | grep -c "Strategic Implications:" || true)

  if [ "$has_relevance" -gt 0 ] || [ "$has_strategic" -gt 0 ]; then
    echo "✓ Has assessment ($comment_count comments)"
    echo "$ticket_id" >> /tmp/has_assessments_simple.txt
    has_assessment=$((has_assessment + 1))
  else
    echo "⚠ Missing assessment ($comment_count comments)"
    echo "$ticket_id" >> /tmp/missing_assessments_simple.txt
    missing=$((missing + 1))
  fi

done < /tmp/review_ticket_ids.txt

echo ""
echo "=== AUDIT SUMMARY ==="
echo "Total tickets checked: $checked"
echo "Has assessment comments: $has_assessment"
echo "Missing assessment comments: $missing"
echo ""
echo "Tickets with assessments: /tmp/has_assessments_simple.txt"
echo "Tickets missing assessments: /tmp/missing_assessments_simple.txt"
