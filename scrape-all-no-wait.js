#!/usr/bin/env node
/**
 * Batch scraper for Medium articles - No interactive prompts
 * Usage: node scrape-all-no-wait.js
 *
 * This will open a browser window. If you need to log in:
 * 1. Log in to Medium in the browser window that opens
 * 2. The script will wait 30 seconds on the first page for you to log in
 * 3. Then it will start scraping automatically
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const OUTPUT_DIR = path.join(__dirname, 'scraped-articles');

// Articles to scrape
const ARTICLES = [
  {
    url: 'https://medium.com/@alirezarezvani/10-game-changing-claude-md-entries-that-turned-my-claude-code-sessions-into-a-coding-superpower-eddf63f5ddf6',
    filename: '01-claude-md-entries.md'
  },
  {
    url: 'https://medium.com/@civillearning/pepper-building-real-time-proactive-ai-assistants-with-event-driven-architecture-3a5252c17a62',
    filename: '02-pepper-ai-assistants.md'
  },
  {
    url: 'https://medium.com/@dipaksahirav/the-future-of-coding-is-here-54d97ae1ef7f',
    filename: '03-future-of-coding.md'
  },
  {
    url: 'https://medium.com/@joe.njenga/13-mcp-servers-for-data-wranglers-to-turn-data-to-gold-3752c5aa5414',
    filename: '04-mcp-servers-data-wranglers.md'
  },
  {
    url: 'https://medium.com/@kalashvasaniya1/openai-just-killed-n8n-1f408ecf84fb',
    filename: '05-openai-killed-n8n.md'
  },
  {
    url: 'https://medium.com/@kalashvasaniya1/steal-these-10-000-n8n-automations-for-free-4bab1bc50850',
    filename: '06-n8n-automations-free.md'
  },
  {
    url: 'https://medium.com/@kefpreneur/i-built-a-5-digital-product-with-claude-ai-in-24-hours-388bee038d2a',
    filename: '07-claude-digital-product.md'
  },
  {
    url: 'https://medium.com/@korsh1968/these-40-professions-will-be-axed-by-ai-2d7bc9cf6128',
    filename: '08-professions-axed-by-ai.md'
  },
  {
    url: 'https://medium.com/@platform.engineers/how-ai-agents-cut-cloud-costs-by-60-the-platform-engineers-guide-to-autonomous-finops-e2a1cc9367b1',
    filename: '09-ai-agents-cloud-costs.md'
  },
  {
    url: 'https://medium.com/@simranjeetsingh1497/google-nano-banana-full-guide-gemini-2-5-flash-api-and-100-nano-banana-prompts-be5b870c8b37',
    filename: '10-google-nano-banana.md'
  },
  {
    url: 'https://medium.com/@yousseftaghlabi/copilot-vision-vs-figma-mcp-the-battle-for-the-future-of-design-systems-dc0016060871',
    filename: '11-copilot-vs-figma-mcp.md'
  },
  {
    url: 'https://medium.com/gitconnected/the-guide-to-mcp-i-never-had-f79091cf99f8',
    filename: '12-guide-to-mcp.md'
  }
];

async function scrapeAllArticles() {
  console.log('🚀 Starting batch scraper for Medium articles...\n');
  console.log('⏰ Browser will open. If you need to log in, you have 30 seconds.\n');

  // Create output directory
  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
    console.log(`📁 Created output directory: ${OUTPUT_DIR}\n`);
  }

  const browser = await chromium.launch({
    headless: false,
    slowMo: 50
  });

  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport: { width: 1400, height: 900 }
  });

  const page = await context.newPage();

  try {
    // Go to Medium homepage and wait for login
    console.log('📱 Opening Medium.com...');
    console.log('   If you need to log in, do it now. Waiting 30 seconds...\n');

    await page.goto('https://medium.com/', { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForTimeout(30000); // Wait 30 seconds for user to log in

    console.log('✅ Starting to scrape articles...\n');

    // Process each article
    const results = [];
    for (let i = 0; i < ARTICLES.length; i++) {
      const article = ARTICLES[i];
      const progress = `[${i + 1}/${ARTICLES.length}]`;

      console.log(`\n${'='.repeat(80)}`);
      console.log(`${progress} Processing: ${article.filename}`);
      console.log(`URL: ${article.url}`);
      console.log(`${'='.repeat(80)}\n`);

      try {
        // Navigate to article
        console.log('🌐 Loading article...');
        await page.goto(article.url, { waitUntil: 'domcontentloaded', timeout: 60000 });
        await page.waitForTimeout(3000);

        // Scroll to load all content
        console.log('📜 Scrolling to load full content...');
        await page.evaluate(async () => {
          await new Promise((resolve) => {
            let totalHeight = 0;
            const distance = 300;
            const timer = setInterval(() => {
              const scrollHeight = document.body.scrollHeight;
              window.scrollBy(0, distance);
              totalHeight += distance;
              if (totalHeight >= scrollHeight) {
                clearInterval(timer);
                setTimeout(resolve, 1000);
              }
            }, 150);
          });
        });

        // Extract content
        console.log('📖 Extracting article content...');
        const articleData = await page.evaluate(() => {
          const article = document.querySelector('article');
          const title = document.querySelector('h1')?.innerText || '';
          const author = document.querySelector('[rel="author"]')?.innerText ||
                        document.querySelector('[data-testid="authorName"]')?.innerText || '';
          const content = article ? (article.innerText || article.textContent) : document.body.innerText;
          const readingTime = document.querySelector('[data-testid="storyReadTime"]')?.innerText || '';

          return { title, author, content, readingTime };
        });

        // Check if we got the full content
        const isMemberOnly = articleData.content.includes('Member-only story');
        const contentLength = articleData.content.length;

        // Format output
        const output = `# ${articleData.title}

**Author:** ${articleData.author}
**URL:** ${article.url}
**Scraped:** ${new Date().toISOString()}
${articleData.readingTime ? `**Reading Time:** ${articleData.readingTime}` : ''}

---

${articleData.content}
`;

        // Save to file
        const outputPath = path.join(OUTPUT_DIR, article.filename);
        fs.writeFileSync(outputPath, output, 'utf-8');

        console.log(`✅ SUCCESS!`);
        console.log(`   Title: ${articleData.title.substring(0, 60)}...`);
        console.log(`   Author: ${articleData.author}`);
        console.log(`   Content length: ${contentLength} characters`);
        if (isMemberOnly && contentLength < 2000) {
          console.log(`   ⚠️  Warning: May be partial content (member-only)`);
        }
        console.log(`   Saved to: ${outputPath}`);

        results.push({
          url: article.url,
          filename: article.filename,
          success: true,
          length: contentLength,
          memberOnly: isMemberOnly && contentLength < 2000
        });

        // Small delay between articles
        await page.waitForTimeout(2000);

      } catch (error) {
        console.error(`❌ FAILED: ${error.message}`);
        results.push({
          url: article.url,
          filename: article.filename,
          success: false,
          error: error.message
        });
      }
    }

    // Print summary
    console.log(`\n\n${'='.repeat(80)}`);
    console.log('📊 SCRAPING SUMMARY');
    console.log(`${'='.repeat(80)}\n`);

    const successful = results.filter(r => r.success);
    const failed = results.filter(r => !r.success);
    const partialContent = results.filter(r => r.success && r.memberOnly);

    console.log(`✅ Successful: ${successful.length}/${ARTICLES.length}`);
    console.log(`❌ Failed: ${failed.length}/${ARTICLES.length}`);
    if (partialContent.length > 0) {
      console.log(`⚠️  Partial content (may need login): ${partialContent.length}/${ARTICLES.length}`);
    }

    if (successful.length > 0) {
      console.log('\n✅ Successfully scraped:');
      successful.forEach(r => {
        const warning = r.memberOnly ? ' ⚠️ (partial)' : '';
        console.log(`   • ${r.filename} (${r.length} chars)${warning}`);
      });
    }

    if (failed.length > 0) {
      console.log('\n❌ Failed to scrape:');
      failed.forEach(r => {
        console.log(`   • ${r.filename}: ${r.error}`);
      });
    }

    console.log(`\n📁 All articles saved to: ${OUTPUT_DIR}`);

    if (partialContent.length > 0) {
      console.log(`\n⚠️  Note: ${partialContent.length} article(s) may have partial content.`);
      console.log('   If you have a Medium membership, try running the script again while logged in.');
    }

  } catch (error) {
    console.error('\n❌ Fatal error:', error);
  } finally {
    console.log('\n\nBrowser will close in 10 seconds...');
    await page.waitForTimeout(10000);
    await browser.close();
  }
}

scrapeAllArticles()
  .then(() => {
    console.log('\n✅ Batch scraping complete!');
    process.exit(0);
  })
  .catch(err => {
    console.error('\n❌ Fatal error:', err);
    process.exit(1);
  });
