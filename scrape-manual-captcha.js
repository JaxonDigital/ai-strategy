#!/usr/bin/env node
/**
 * Semi-automated scraper that pauses for manual CAPTCHA solving
 * You solve the CAPTCHA, script handles the rest
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const readline = require('readline');

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

// Create readline interface for user input
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

function askQuestion(query) {
  return new Promise(resolve => rl.question(query, resolve));
}

async function scrape() {
  console.log('🚀 Semi-Automated Medium Scraper\n');
  console.log('📋 How it works:');
  console.log('   1. Browser opens to each article');
  console.log('   2. If you see a CAPTCHA, solve it');
  console.log('   3. Press ENTER when the article loads');
  console.log('   4. Script saves and moves to next\n');

  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }

  const context = await chromium.launchPersistentContext(PROFILE_DIR, {
    headless: false,
    slowMo: 100,
    viewport: { width: 1400, height: 900 }
  });

  const page = context.pages()[0] || await context.newPage();

  try {
    const results = [];

    for (let i = 0; i < ARTICLES.length; i++) {
      const article = ARTICLES[i];

      console.log(`\n${'='.repeat(70)}`);
      console.log(`📄 Article ${i + 1}/${ARTICLES.length}: ${article.filename}`);
      console.log(`${'='.repeat(70)}\n`);

      try {
        console.log(`🌐 Loading: ${article.url}\n`);
        await page.goto(article.url, { timeout: 60000 });
        await page.waitForTimeout(2000);

        // Check if CAPTCHA present
        const hasCaptcha = await page.evaluate(() => {
          return document.body.innerText.includes('Verifying you are human') ||
                 document.body.innerText.includes('Cloudflare');
        });

        if (hasCaptcha) {
          console.log('⚠️  CAPTCHA detected! Please solve it in the browser window.\n');
        }

        // Wait for user to confirm article is loaded
        await askQuestion('✅ Press ENTER when the article has loaded... ');

        // Give it a moment to fully render
        console.log('\n📜 Scrolling through article...');
        for (let scroll = 0; scroll < 10; scroll++) {
          await page.evaluate(() => window.scrollBy(0, window.innerHeight * 0.8));
          await page.waitForTimeout(500);
        }

        await page.waitForTimeout(1000);

        // Extract content
        console.log('📖 Extracting content...');
        const data = await page.evaluate(() => {
          const article = document.querySelector('article');
          const title = document.querySelector('h1')?.innerText || 'No title';
          const author = document.querySelector('[rel="author"]')?.innerText ||
                        document.querySelector('[data-testid="authorName"]')?.innerText || '';
          const content = article ? article.innerText : document.body.innerText;
          const readingTime = document.querySelector('[data-testid="storyReadTime"]')?.innerText || '';

          const isCaptcha = content.includes('Verifying you are human') ||
                           content.includes('Cloudflare');

          return { title, author, content, readingTime, isCaptcha };
        });

        if (data.isCaptcha) {
          console.log('❌ Still showing CAPTCHA page. Skipping...\n');
          results.push({ ...article, success: false, error: 'CAPTCHA not solved' });
          continue;
        }

        // Format and save
        const output = `# ${data.title}

**Author:** ${data.author}
**URL:** ${article.url}
**Scraped:** ${new Date().toISOString()}
${data.readingTime ? `**Reading Time:** ${data.readingTime}` : ''}

---

${data.content}
`;

        const filepath = path.join(OUTPUT_DIR, article.filename);
        fs.writeFileSync(filepath, output, 'utf-8');

        console.log(`✅ Saved successfully!`);
        console.log(`   Title: ${data.title.substring(0, 60)}...`);
        console.log(`   Author: ${data.author}`);
        console.log(`   Content: ${data.content.length} characters\n`);

        results.push({ ...article, success: true, length: data.content.length });

        // Brief pause before next article
        if (i < ARTICLES.length - 1) {
          console.log('⏳ Moving to next article in 3 seconds...\n');
          await page.waitForTimeout(3000);
        }

      } catch (err) {
        console.log(`❌ Error: ${err.message}\n`);
        results.push({ ...article, success: false, error: err.message });
      }
    }

    // Summary
    console.log(`\n\n${'='.repeat(70)}`);
    console.log('📊 FINAL SUMMARY');
    console.log(`${'='.repeat(70)}\n`);

    const success = results.filter(r => r.success);
    const failed = results.filter(r => !r.success);

    console.log(`✅ Successfully scraped: ${success.length}/${ARTICLES.length}`);
    success.forEach(r => {
      console.log(`   • ${r.filename} (${r.length} chars)`);
    });

    if (failed.length > 0) {
      console.log(`\n❌ Failed: ${failed.length}/${ARTICLES.length}`);
      failed.forEach(r => {
        console.log(`   • ${r.filename}: ${r.error}`);
      });
    }

    console.log(`\n📁 Articles saved to: ${OUTPUT_DIR}\n`);

  } finally {
    rl.close();
    console.log('Closing browser in 5 seconds...');
    await page.waitForTimeout(5000);
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
    rl.close();
    process.exit(1);
  });
