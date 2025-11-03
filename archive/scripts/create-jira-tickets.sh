#!/bin/bash

# Set JIRA API token
export JIRA_API_TOKEN=$(cat ~/.jira.d/.pass)

# Articles data (title|||URL format)
declare -a articles=(
  "I'm a middle-aged developer, and my time to shine has sunset|||https://medium.com/@jeffreybakker/im-a-middle-aged-developer-and-my-time-to-shine-has-sunset-a1b5d5c6ff2d"
  "The Future No One Wants to Admit: 7 Predictions About AI That Will Change Everything|||https://medium.com/@Definecode/the-future-no-one-wants-to-admit-7-predictions-about-ai-that-will-change-everything-23c5b311b4de"
  "5 Essential MCP Servers That Give Claude & Cursor Real Superpowers (2025)|||https://medium.com/@prithwish.nath/5-essential-mcp-servers-that-give-claude-cursor-real-superpowers-2025-509a822dd4fd"
  "The 4 characteristics of successful AI chat integrations|||https://medium.com/@waleedk/the-4-characteristics-of-successful-ai-chat-integrations-5cef0bfd2595"
  "The 15 Biggest Wastes of Money (According to ChatGPT)|||https://medium.com/@christinapiccoli/the-15-biggest-wastes-of-money-according-to-chatgpt-7c14c01b5783"
  "This Ridiculous XP System Made Me Run Further, Read More, and Work Harder|||https://medium.com/@chrisdunlop_37984/this-ridiculous-xp-system-made-me-run-further-read-more-and-work-harder-717fbef09899"
  "Google's New AI – Nano Banana: Top 10 Use Cases That Will Blow Your Mind|||https://medium.com/@yasassandeepa007/googles-new-ai-nano-banana-top-10-use-cases-that-will-blow-your-mind-63a19f1b28d7"
  "These 9 Google MCP Servers Will Take Your Automated Workflow (To The Next Level)|||https://medium.com/@joe.njenga/these-9-google-mcp-servers-will-take-your-automated-workflow-to-the-next-level-3b3f190aa713"
  "Microsoft Just Declared War on the GPU Mafia: Meet bitnet.cpp|||https://medium.com/@algoinsights/microsoft-just-declared-war-on-the-gpu-mafia-meet-bitnet-cpp-e6ddad8b54ba"
  "The One Thing Nobody's Talking About With Startups and AI|||https://medium.com/@aarondinin/the-one-thing-nobodys-talking-about-with-startups-and-ai-658cfa8e8900"
  "Build Your Private Language Model: Local and Specialized For Your Tasks.|||https://medium.com/@erdogant/build-your-private-language-model-local-and-specialized-for-your-tasks-f94a3f611869"
  "7 Websites I Visit Every Day in 2025|||https://medium.com/@tosny/7-websites-i-visit-every-day-in-2025-ef54332a2003"
  "Apple Engineers Don't Have an AI Problem|||https://medium.com/@tipsnguts/apple-engineers-dont-have-an-ai-problem-9ae6b0854241"
  "I Tested Newly Released GLM 4.6 (And Discovered a Cheaper Way to Code Like a Beast )|||https://medium.com/@joe.njenga/i-tested-newly-released-glm-4-6-and-discovered-a-cheaper-way-to-code-like-a-beast-7567233b617d"
  "Anime.js — Open-Source, MIT-licensed Web Animation Engine|||https://medium.com/@civillearning/anime-js-open-source-mit-licensed-web-animation-engine-9e140277baee"
)

PDF_DIR="/Users/bgerby/Desktop/pdfs/10-10"

# Create tickets
for i in "${!articles[@]}"; do
  num=$((i + 1))
  IFS='|||' read -r title url <<< "${articles[$i]}"

  echo "Creating ticket $num: $title"

  # Create description with URL
  description="Source: $url

Article from Medium Daily Digest (10/10/2025)"

  # Create the JIRA ticket
  ticket=$(jira issue create -p GAT -t Task -s "$title" -b "$description" --plain 2>&1 | grep -oE 'GAT-[0-9]+' | head -1)

  if [ -z "$ticket" ]; then
    echo "  ❌ Failed to create ticket for: $title"
    continue
  fi

  echo "  ✅ Created: $ticket"

  # Attach PDF if it exists
  pdf_file="$PDF_DIR/$num.pdf"
  if [ -f "$pdf_file" ]; then
    echo "  📎 Attaching PDF: $num.pdf"
    curl -X POST \
      -H "Authorization: Basic $(echo -n "bgerby@jaxondigital.com:$JIRA_API_TOKEN" | base64)" \
      -H "X-Atlassian-Token: no-check" \
      -F "file=@$pdf_file" \
      "https://jaxondigital.atlassian.net/rest/api/3/issue/$ticket/attachments" \
      > /dev/null 2>&1

    if [ $? -eq 0 ]; then
      echo "  ✅ PDF attached"
    else
      echo "  ❌ Failed to attach PDF"
    fi
  else
    echo "  ℹ️  No PDF found ($num.pdf)"
  fi

  echo ""
  sleep 1  # Rate limiting
done

echo "Done! Created tickets for ${#articles[@]} articles."
