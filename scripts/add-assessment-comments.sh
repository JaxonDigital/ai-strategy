#!/bin/bash
# Add assessment comments to JIRA tickets from the recent batch (GAT-479 to GAT-491)

set -e

JIRA_API_TOKEN="`cat ~/.jira.d/.pass`"
export JIRA_API_TOKEN

ASSESSMENTS_DIR="/Users/bgerby/Documents/dev/ai/assessments"

echo "=== ADDING ASSESSMENT COMMENTS TO JIRA TICKETS ==="
echo ""

# Function to extract assessment from markdown file by title
extract_assessment() {
  local title_normalized="$1"
  local assessment_file="$2"

  # Use awk to extract the full assessment section (BSD-compatible)
  awk -v title="$title_normalized" '
    BEGIN { IGNORECASE=1; found=0; in_section=0 }

    # Match article header
    /^### ARTICLE-/ {
      # Extract title using BSD-compatible string operations
      article_line = $0
      # Remove the prefix "### ARTICLE-XX - "
      sub(/^### ARTICLE-[0-9]+ - /, "", article_line)

      if (article_line != "") {
        article_title = tolower(article_line)
        gsub(/[^a-z0-9 ]/, "", article_title)
        gsub(/  +/, " ", article_title)

        # Check if this matches our title
        if (index(article_title, title) > 0 || index(title, article_title) > 0) {
          found = 1
          in_section = 1
        }
      }
      next
    }

    # Stop at next article or section
    in_section == 1 && (/^### ARTICLE-/ || /^## /) {
      exit
    }

    # Print content if in the right section
    in_section == 1 {
      print
    }
  ' "$assessment_file"
}

# Tickets and their normalized titles for matching (ticket:title format)
tickets=(
  "GAT-479:i spent 40 hours testing perplexitys secret 42 page work guide"
  "GAT-480:dexter ai the self improving financial research assistant that thinks like an analyst"
  "GAT-481:building a documentation generator your agents first useful job"
  "GAT-482:claude code v2 0 28"
  "GAT-483:the most expensive context engineering mistake every cto makes"
  "GAT-485:building a text to sql chatbot with rag langchain fastapi and streamlit"
  "GAT-486:why ctos should fear shadow agents more than they ever feared shadow it"
  "GAT-487:9 ai skills you must learn before everyone else does or get left behind"
  "GAT-488:i tried running an mcp server on aws lambda heres what happened"
  "GAT-489:libra ai an open source alternative to v0 and lovable"
  "GAT-491:meet nico who sold an ai tool built in 48 hours for 65k and then another one built in 1 week"
)

added=0
skipped=0

for item in "${tickets[@]}"; do
  ticket_id="${item%%:*}"
  title_normalized="${item#*:}"

  echo "Processing $ticket_id..."

  # Find matching assessment across all files
  assessment_text=""
  for assessment_file in "$ASSESSMENTS_DIR"/medium-articles-relevance-assessment-2025-10-*.md; do
    if [ ! -f "$assessment_file" ]; then
      continue
    fi

    assessment_text=$(extract_assessment "$title_normalized" "$assessment_file")

    if [ -n "$assessment_text" ]; then
      echo "  ✓ Found assessment in $(basename "$assessment_file")"
      break
    fi
  done

  if [ -z "$assessment_text" ]; then
    echo "  ✗ No assessment found"
    skipped=$((skipped + 1))
    continue
  fi

  # Create formatted comment
  comment="# Article Assessment

$assessment_text

---
*Assessment auto-generated from relevance analysis*"

  # Write to temp file
  echo "$comment" > "/tmp/jira_comment_${ticket_id}.txt"

  # Add comment to ticket
  if jira issue comment add "$ticket_id" "$(cat /tmp/jira_comment_${ticket_id}.txt)" --no-input -p GAT 2>/dev/null; then
    echo "  ✓ Added assessment comment"
    added=$((added + 1))
  else
    echo "  ✗ Failed to add comment"
    skipped=$((skipped + 1))
  fi

  rm "/tmp/jira_comment_${ticket_id}.txt"

  # Rate limiting
  sleep 1
done

echo ""
echo "=== COMPLETE ==="
echo "Assessment comments added: $added"
echo "Skipped: $skipped"
