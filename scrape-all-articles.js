#!/usr/bin/env node
/**
 * Batch scraper for multiple Medium articles
 * Usage: node scrape-all-articles.js
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const SESSION_FILE = path.join(__dirname, '.medium-session.json');
const OUTPUT_DIR = path.join(__dirname, 'scraped-articles');

// Articles to scrape (from the email digest)
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
    viewport: { width: 1280, height: 720 }
  });

  // Load session if available
  if (fs.existsSync(SESSION_FILE)) {
    console.log('📦 Loading saved Medium session...');
    try {
      const sessionData = JSON.parse(fs.readFileSync(SESSION_FILE, 'utf-8'));
      await context.addCookies(sessionData.cookies);
      console.log('✓ Session loaded!\n');
    } catch (err) {
      console.log('⚠ Could not load session\n');
    }
  }

  const page = await context.newPage();

  try {
    // Check login status
    console.log('🔍 Checking Medium login status...');
    await page.goto('https://medium.com/', { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForTimeout(3000);

    const isLoggedIn = await page.evaluate(() => {
      return document.querySelector('[data-testid="user-menu"]') !== null ||
             document.querySelector('[aria-label="user menu"]') !== null ||
             document.body.innerText.includes('Your library');
    });

    if (!isLoggedIn) {
      console.log('\n⚠️  NOT LOGGED IN TO MEDIUM');
      console.log('📝 Please log in manually in the browser window.');
      console.log('   Once logged in, press ENTER in this terminal to continue...\n');

      await new Promise(resolve => {
        process.stdin.once('data', () => {
          console.log('✓ Continuing...\n');
          resolve();
        });
      });

      // Save session
      const cookies = await context.cookies();
      fs.writeFileSync(SESSION_FILE, JSON.stringify({ cookies }, null, 2));
      console.log('✓ Session saved!\n');
    } else {
      console.log('✓ Already logged in!\n');
    }

    // Process each article
    const results = [];
    for (let i = 0; i < ARTICLES.length; i++) {
      const article = ARTICLES[i];
      const progress = `[${i + 1}/${ARTICLES.length}]`;

      console.log(`\n${'='.repeat(80)}`);
      console.log(`${progress} Processing: ${article.filename}`);
      console.log(`${'='.repeat(80)}\n`);

      try {
        // Navigate to article
        await page.goto(article.url, { waitUntil: 'domcontentloaded', timeout: 60000 });
        await page.waitForTimeout(3000);

        // Scroll to load all content
        await page.evaluate(async () => {
          await new Promise((resolve) => {
            let totalHeight = 0;
            const distance = 200;
            const timer = setInterval(() => {
              const scrollHeight = document.body.scrollHeight;
              window.scrollBy(0, distance);
              totalHeight += distance;
              if (totalHeight >= scrollHeight) {
                clearInterval(timer);
                setTimeout(resolve, 500);
              }
            }, 100);
          });
        });

        // Extract content
        const articleData = await page.evaluate(() => {
          const article = document.querySelector('article');
          const title = document.querySelector('h1')?.innerText || '';
          const author = document.querySelector('[rel="author"]')?.innerText ||
                        document.querySelector('[data-testid="authorName"]')?.innerText || '';
          const content = article ? (article.innerText || article.textContent) : document.body.innerText;
          const readingTime = document.querySelector('[data-testid="storyReadTime"]')?.innerText || '';

          return { title, author, content, readingTime };
        });

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
        console.log(`   Title: ${articleData.title}`);
        console.log(`   Length: ${articleData.content.length} characters`);
        console.log(`   Saved to: ${outputPath}`);

        results.push({
          url: article.url,
          filename: article.filename,
          success: true,
          length: articleData.content.length
        });

        // Small delay between articles
        await page.waitForTimeout(1000);

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
    console.log('📊 SUMMARY');
    console.log(`${'='.repeat(80)}\n`);

    const successful = results.filter(r => r.success);
    const failed = results.filter(r => !r.success);

    console.log(`✅ Successful: ${successful.length}/${ARTICLES.length}`);
    console.log(`❌ Failed: ${failed.length}/${ARTICLES.length}\n`);

    if (successful.length > 0) {
      console.log('Successful articles:');
      successful.forEach(r => {
        console.log(`  ✓ ${r.filename} (${r.length} chars)`);
      });
    }

    if (failed.length > 0) {
      console.log('\nFailed articles:');
      failed.forEach(r => {
        console.log(`  ✗ ${r.filename}: ${r.error}`);
      });
    }

    console.log(`\n📁 All articles saved to: ${OUTPUT_DIR}\n`);

  } catch (error) {
    console.error('\n❌ Fatal error:', error);
  } finally {
    console.log('Browser will close in 5 seconds...');
    await page.waitForTimeout(5000);
    await browser.close();
  }
}

scrapeAllArticles()
  .then(() => {
    console.log('✅ Batch scraping complete!');
    process.exit(0);
  })
  .catch(err => {
    console.error('❌ Fatal error:', err);
    process.exit(1);
  });
