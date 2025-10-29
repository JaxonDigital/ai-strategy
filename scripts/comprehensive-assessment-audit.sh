#!/bin/bash
# Comprehensive audit and fix for all JIRA Review tickets
# Adds missing assessment comments from assessment markdown files

set -e

JIRA_API_TOKEN="`cat ~/.jira.d/.pass`"
export JIRA_API_TOKEN

ASSESSMENTS_DIR="/Users/bgerby/Documents/dev/ai/assessments"

echo "=== COMPREHENSIVE JIRA TICKET ASSESSMENT AUDIT ==="
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

# Step 2: Parse all assessment files and build article database
echo "Step 2: Parsing all assessment files..."
> /tmp/article_database.txt  # Clear file

for assessment_file in "$ASSESSMENTS_DIR"/*.md; do
  if [ ! -f "$assessment_file" ]; then
    continue
  fi

  filename=$(basename "$assessment_file")
  echo "  Parsing $filename..."

  # Extract articles from this assessment file
  awk '
    /^### ARTICLE-/ {
      article_section = $0
      article_title = ""
      article_url = ""
      article_priority = ""
      article_content = ""
      in_article = 1
      next
    }

    in_article == 1 {
      # Accumulate content until next article or end
      if (/^### ARTICLE-/ || /^## /) {
        # Print previous article
        if (article_title != "") {
          # Normalize title for matching (lowercase, no special chars)
          gsub(/[^a-zA-Z0-9 ]/, "", article_title)
          article_title_normalized = tolower(article_title)
          gsub(/  +/, " ", article_title_normalized)

          # Output: title|url|priority|full_content
          print article_title_normalized "|" article_url "|" article_priority "|" article_content
        }

        # Start new article
        article_section = $0
        article_title = ""
        article_url = ""
        article_priority = ""
        article_content = ""
        in_article = (/^### ARTICLE-/)
        next
      }

      # Extract title from section header
      if (article_title == "" && article_section != "") {
        match(article_section, /### ARTICLE-[0-9]+ - (.+)$/, arr)
        if (arr[1] != "") {
          article_title = arr[1]
        }
      }

      # Extract URL
      if (/\*\*Article URL:\*\*/) {
        match($0, /\*\*Article URL:\*\* (.+)$/, arr)
        if (arr[1] != "") {
          article_url = arr[1]
        }
      }

      # Extract priority
      if (/\*\*Priority:\*\*/) {
        if (/HIGH/) article_priority = "HIGH"
        else if (/MEDIUM/) article_priority = "MEDIUM"
        else if (/LOW/) article_priority = "LOW"
      }

      # Accumulate full content
      article_content = article_content $0 "\n"
    }

    END {
      # Print last article
      if (in_article == 1 && article_title != "") {
        gsub(/[^a-zA-Z0-9 ]/, "", article_title)
        article_title_normalized = tolower(article_title)
        gsub(/  +/, " ", article_title_normalized)
        print article_title_normalized "|" article_url "|" article_priority "|" article_content
      }
    }
  ' "$assessment_file" >> /tmp/article_database.txt
done

TOTAL_ARTICLES=$(wc -l < /tmp/article_database.txt | tr -d ' ')
echo "✓ Loaded $TOTAL_ARTICLES articles from assessment files"
echo ""

# Step 3: Audit each ticket
echo "Step 3: Auditing tickets for completeness..."
> /tmp/missing_assessments.txt
> /tmp/audit_report.txt
checked=0
missing_assessments=0

while IFS= read -r ticket_id; do
  checked=$((checked + 1))
  echo "[$checked/$TOTAL_TICKETS] Checking $ticket_id..."

  # Get ticket details
  ticket_details=$(jira issue view "$ticket_id" 2>/dev/null)

  if [ $? -ne 0 ]; then
    echo "  ✗ Could not fetch ticket" | tee -a /tmp/audit_report.txt
    continue
  fi

  # Extract ticket title (remove "Review: " prefix)
  ticket_title=$(echo "$ticket_details" | grep -A 1 "^  #" | tail -1 | sed 's/^  Review: //' | sed 's/Review: //')

  # Check for assessment comment
  has_assessment=$(echo "$ticket_details" | grep -c "Relevance Summary:" || true)

  # Check for URL
  has_url=$(echo "$ticket_details" | grep -c "Article URL.*https://" || true)

  # Check for PDF
  has_pdf=$(echo "$ticket_details" | grep -c "PDF.*https://drive.google.com" || true)

  # Normalize ticket title for matching
  ticket_title_normalized=$(echo "$ticket_title" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9 ]//g' | sed 's/  */ /g')

  # Try to find matching article in database
  matching_article=$(grep -i "$ticket_title_normalized" /tmp/article_database.txt | head -1 || true)

  if [ -n "$matching_article" ]; then
    article_priority=$(echo "$matching_article" | cut -d'|' -f3)

    # Report status
    issues=""
    if [ "$has_url" -eq 0 ]; then
      issues="$issues missing-url"
    fi
    if [ "$has_pdf" -eq 0 ]; then
      issues="$issues missing-pdf"
    fi
    if [ "$has_assessment" -eq 0 ]; then
      issues="$issues missing-assessment"
      missing_assessments=$((missing_assessments + 1))
      echo "$ticket_id|$matching_article" >> /tmp/missing_assessments.txt
    fi

    if [ -n "$issues" ]; then
      echo "  ⚠ Issues:$issues (priority: $article_priority)" | tee -a /tmp/audit_report.txt
    else
      echo "  ✓ Complete (priority: $article_priority)" | tee -a /tmp/audit_report.txt
    fi
  else
    echo "  ⊙ No matching assessment found" | tee -a /tmp/audit_report.txt
  fi

done < /tmp/review_ticket_ids.txt

echo ""
echo "=== AUDIT SUMMARY ===" | tee -a /tmp/audit_report.txt
echo "Total tickets checked: $checked" | tee -a /tmp/audit_report.txt
echo "Missing assessment comments: $missing_assessments" | tee -a /tmp/audit_report.txt
echo ""
echo "Full audit report saved to: /tmp/audit_report.txt"
echo "Tickets needing assessments saved to: /tmp/missing_assessments.txt"
