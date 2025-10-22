#!/usr/bin/env node
/**
 * Medium scraper using persistent browser profile
 * This will save your login between runs
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const OUTPUT_DIR = path.join(__dirname, 'scraped-articles');
const PROFILE_DIR = path.join(__dirname, '.browser-profile');

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

async function scrape() {
  console.log('🚀 Starting Medium scraper with persistent profile...\n');

  // Create directories
  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }

  // Launch browser with persistent context
  const context = await chromium.launchPersistentContext(PROFILE_DIR, {
    headless: false,
    slowMo: 100,
    viewport: { width: 1400, height: 900 }
  });

  const page = context.pages()[0] || await context.newPage();

  try {
    // Check if logged in
    console.log('🔍 Checking Medium login...');
    await page.goto('https://medium.com/', { timeout: 60000 });
    await page.waitForTimeout(5000);

    const isLoggedIn = await page.evaluate(() => {
      const html = document.body.innerHTML;
      return html.includes('Your library') ||
             html.includes('user-menu') ||
             document.querySelector('[data-testid="user-menu"]') !== null;
    });

    if (!isLoggedIn) {
      console.log('\n⚠️  Please log in to Medium in the browser window.');
      console.log('⏱  The browser will stay open for 60 seconds for you to log in...\n');
      await page.waitForTimeout(60000);
    } else {
      console.log('✅ Already logged in!\n');
    }

    // Scrape articles one by one with delays
    const results = [];
    for (let i = 0; i < ARTICLES.length; i++) {
      const article = ARTICLES[i];

      console.log(`\n${'='.repeat(70)}`);
      console.log(`[${i + 1}/${ARTICLES.length}] ${article.filename}`);
      console.log(`${'='.repeat(70)}\n`);

      try {
        console.log(`🌐 Navigating to article...`);
        await page.goto(article.url, { timeout: 60000 });

        // Wait longer for content to load
        console.log(`⏳ Waiting for content...`);
        await page.waitForTimeout(5000);

        // Scroll slowly
        console.log(`📜 Scrolling...`);
        for (let scroll = 0; scroll < 5; scroll++) {
          await page.evaluate(() => window.scrollBy(0, window.innerHeight));
          await page.waitForTimeout(1000);
        }

        // Extract
        const data = await page.evaluate(() => {
          const article = document.querySelector('article');
          return {
            title: document.querySelector('h1')?.innerText || '',
            author: document.querySelector('[rel="author"]')?.innerText || '',
            content: article ? article.innerText : document.body.innerText,
            hasError: document.body.innerText.includes('500') ||
                     document.body.innerText.includes('something went wrong')
          };
        });

        if (data.hasError) {
          console.log(`⚠️  Page returned an error`);
          results.push({ ...article, success: false, error: 'Page error' });
          continue;
        }

        // Save
        const output = `# ${data.title}

**Author:** ${data.author}
**URL:** ${article.url}
**Scraped:** ${new Date().toISOString()}

---

${data.content}
`;

        const filepath = path.join(OUTPUT_DIR, article.filename);
        fs.writeFileSync(filepath, output, 'utf-8');

        console.log(`✅ Saved! (${data.content.length} chars)`);
        console.log(`   Title: ${data.title.substring(0, 50)}...`);

        results.push({ ...article, success: true, length: data.content.length });

        // Longer delay between articles to avoid rate limiting
        if (i < ARTICLES.length - 1) {
          console.log(`⏳ Waiting 10 seconds before next article...`);
          await page.waitForTimeout(10000);
        }

      } catch (err) {
        console.log(`❌ Failed: ${err.message}`);
        results.push({ ...article, success: false, error: err.message });
      }
    }

    // Summary
    console.log(`\n\n${'='.repeat(70)}`);
    console.log('📊 SUMMARY');
    console.log(`${'='.repeat(70)}\n`);

    const success = results.filter(r => r.success);
    console.log(`✅ Success: ${success.length}/${ARTICLES.length}`);
    success.forEach(r => console.log(`   • ${r.filename} (${r.length} chars)`));

    const failed = results.filter(r => !r.success);
    if (failed.length > 0) {
      console.log(`\n❌ Failed: ${failed.length}`);
      failed.forEach(r => console.log(`   • ${r.filename}: ${r.error}`));
    }

  } finally {
    console.log('\n\n Browser will close in 10 seconds...');
    await page.waitForTimeout(10000);
    await context.close();
  }
}

scrape()
  .then(() => {
    console.log('✅ Done!');
    process.exit(0);
  })
  .catch(err => {
    console.error('❌ Error:', err);
    process.exit(1);
  });
