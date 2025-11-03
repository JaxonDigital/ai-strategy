#!/bin/bash
# Check for duplicate URLs in JIRA before creating tickets
# Usage: ./check-duplicates.sh /path/to/urls.txt

if [ -z "$1" ]; then
    echo "Usage: $0 <url-file>"
    echo "Example: $0 /tmp/medium-urls.txt"
    exit 1
fi

URL_FILE="$1"

if [ ! -f "$URL_FILE" ]; then
    echo "Error: File not found: $URL_FILE"
    exit 1
fi

echo "Checking URLs from: $URL_FILE"
echo "Against JIRA project: GAT"
echo ""

python3 << EOF
import subprocess
import sys
import os

# Read the new URLs
url_file = "$URL_FILE"
with open(url_file, 'r') as f:
    new_urls = [line.strip() for line in f if line.strip()]

print(f"Found {len(new_urls)} URLs to check\n")

# Get all GAT tickets
api_token = open(os.path.expanduser('~/.jira.d/.pass')).read().strip()
result = subprocess.run(
    ['jira', 'issue', 'list', '-p', 'GAT', '--plain'],
    capture_output=True,
    text=True,
    env={'JIRA_API_TOKEN': api_token, 'PATH': os.environ['PATH']}
)

if result.returncode != 0:
    print("Error fetching JIRA tickets:")
    print(result.stderr)
    sys.exit(1)

existing_tickets = result.stdout

# For each new URL, check if it exists in any ticket
print("=== DUPLICATE CHECK ===\n")
duplicates = []
new_articles = []

for url in new_urls:
    # Extract article slug from URL (the part after the last /)
    slug = url.split('/')[-1].split('?')[0]

    # Check if this slug appears in any ticket summary
    found = False
    for line in existing_tickets.split('\n'):
        if slug in line or url in line:
            duplicates.append((url, line))
            print(f"⚠️  DUPLICATE: {url}")
            print(f"    Exists as: {line.strip()[:120]}")
            print()
            found = True
            break

    if not found:
        new_articles.append(url)
        print(f"✅ NEW: {url}")

print(f"\n=== SUMMARY ===")
print(f"New articles to create: {len(new_articles)}")
print(f"Duplicates found: {len(duplicates)}")

# Save only new URLs for ticket creation
if new_articles:
    output_file = url_file.replace('.txt', '-new-only.txt')
    with open(output_file, 'w') as f:
        for url in new_articles:
            f.write(url + '\n')
    print(f"\n✅ Saved {len(new_articles)} new URLs to {output_file}")
    print(f"\nNext step: Create tickets using URLs from {output_file}")
else:
    print("\n⚠️  No new articles to create tickets for!")

sys.exit(0 if new_articles else 1)
EOF
