#!/bin/bash
# Capture Medium articles as PDFs and attach to Jira tickets
# Usage: ./capture-and-attach-articles.sh YYYY-MM-DD START_TICKET

DATE=$1
START_TICKET=$2

if [ -z "$DATE" ] || [ -z "$START_TICKET" ]; then
    echo "Usage: $0 YYYY-MM-DD START_TICKET"
    echo "Example: $0 2025-10-14 GAT-192"
    exit 1
fi

FOLDER="/Users/bgerby/Desktop/medium-articles-${DATE}"
mkdir -p "$FOLDER"
cd "$FOLDER"

# Extract ticket number
TICKET_NUM=$(echo $START_TICKET | grep -o '[0-9]*$')
PROJECT=$(echo $START_TICKET | grep -o '^[A-Z]*')

echo "Processing articles from ${DATE}"
echo "Starting at ticket: ${START_TICKET}"
echo "Output folder: ${FOLDER}"
echo ""

# Read URLs from email extraction
mapfile -t URLS < /tmp/article-urls.txt

AUTH=$(echo -n 'bgerby@jaxondigital.com:'$(cat ~/.jira.d/.pass) | base64)

# Counter for PDF numbering
COUNTER=1

for URL in "${URLS[@]}"; do
    TICKET="${PROJECT}-${TICKET_NUM}"

    # Extract article title from URL
    SLUG=$(echo $URL | rev | cut -d'/' -f1 | rev | cut -d'-' -f1-5)
    FILENAME=$(printf "%02d-${SLUG}.pdf" $COUNTER)

    echo "[$COUNTER/14] Processing: $TICKET"
    echo "  URL: $URL"
    echo "  Saving: $FILENAME"

    # Use Playwright via Claude Code to save PDF
    # This would need to be done interactively with Claude
    # For now, create placeholder and instructions

    echo "  TODO: Save PDF using Playwright"
    echo "  mcp__playwright__playwright_navigate: $URL"
    echo "  mcp__playwright__playwright_save_as_pdf: $FILENAME"
    echo ""

    # Increment counters
    COUNTER=$((COUNTER + 1))
    TICKET_NUM=$((TICKET_NUM + 1))
done

echo "Next step: Run attachment script after PDFs are saved"
echo "  cd $FOLDER"
echo "  bash attach-to-jira.sh"
