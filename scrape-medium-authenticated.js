#!/usr/bin/env node
/**
 * Medium Article Scraper with Authentication
 * Usage: node scrape-medium-authenticated.js <url> [output-file]
 *
 * This script will:
 * 1. Open a browser
 * 2. Navigate to Medium and wait for you to log in (if needed)
 * 3. Navigate to the article
 * 4. Scrape the full content
 * 5. Save the authenticated session for future use
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const SESSION_FILE = path.join(__dirname, '.medium-session.json');

async function scrapeArticle(url, outputFile) {
  console.log('🚀 Starting Medium scraper with authentication support...\n');

  // Launch browser with persistent context to save login
  const browser = await chromium.launch({
    headless: false, // Keep visible so you can log in
    slowMo: 50
  });

  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport: { width: 1280, height: 720 }
  });

  // Load existing session if available
  if (fs.existsSync(SESSION_FILE)) {
    console.log('📦 Loading saved Medium session...');
    try {
      const sessionData = JSON.parse(fs.readFileSync(SESSION_FILE, 'utf-8'));
      await context.addCookies(sessionData.cookies);
      console.log('✓ Session loaded!\n');
    } catch (err) {
      console.log('⚠ Could not load session, will need to log in manually\n');
    }
  }

  const page = await context.newPage();

  try {
    // First, check if we're logged in by going to Medium homepage
    console.log('🔍 Checking Medium login status...');
    await page.goto('https://medium.com/', { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);

    const isLoggedIn = await page.evaluate(() => {
      // Check for common logged-in indicators
      return document.querySelector('[data-testid="user-menu"]') !== null ||
             document.querySelector('[aria-label="user menu"]') !== null ||
             document.body.innerText.includes('Your library');
    });

    if (!isLoggedIn) {
      console.log('\n⚠️  NOT LOGGED IN TO MEDIUM');
      console.log('📝 Please log in manually in the browser window.');
      console.log('   Once logged in, press ENTER in this terminal to continue...\n');

      // Wait for user to press Enter
      await new Promise(resolve => {
        process.stdin.once('data', () => {
          console.log('✓ Continuing...\n');
          resolve();
        });
      });

      // Save the session after login
      console.log('💾 Saving session for future use...');
      const cookies = await context.cookies();
      fs.writeFileSync(SESSION_FILE, JSON.stringify({ cookies }, null, 2));
      console.log('✓ Session saved!\n');
    } else {
      console.log('✓ Already logged in!\n');
    }

    // Now navigate to the article
    console.log(`📰 Navigating to article: ${url}`);
    await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(3000);

    const pageTitle = await page.title();
    console.log(`📄 Page title: ${pageTitle}`);

    // Check if we still hit a paywall
    const hasPaywall = await page.evaluate(() => {
      return document.body.innerText.includes('Member-only story') ||
             document.body.innerText.includes('Become a member to read');
    });

    if (hasPaywall) {
      console.log('\n⚠️  Article appears to be member-only.');
      console.log('   Make sure you have an active Medium membership.');
    }

    // Scroll to load all lazy-loaded content
    console.log('📜 Scrolling to load full content...');
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
            setTimeout(resolve, 1000);
          }
        }, 100);
      });
    });

    // Extract the article content
    console.log('📖 Extracting article content...');
    const articleData = await page.evaluate(() => {
      // Find the article element
      const article = document.querySelector('article');
      if (!article) {
        return {
          title: document.querySelector('h1')?.innerText || 'No title found',
          author: '',
          content: document.body.innerText,
          fullContent: false
        };
      }

      // Extract metadata
      const title = document.querySelector('h1')?.innerText || '';
      const author = document.querySelector('[rel="author"]')?.innerText ||
                     document.querySelector('[data-testid="authorName"]')?.innerText ||
                     '';

      // Get the article content
      const content = article.innerText || article.textContent;

      // Try to get reading time
      const readingTime = document.querySelector('[data-testid="storyReadTime"]')?.innerText || '';

      return {
        title,
        author,
        content,
        readingTime,
        fullContent: true
      };
    });

    console.log(`\n✓ Title: ${articleData.title}`);
    console.log(`✓ Author: ${articleData.author}`);
    console.log(`✓ Content length: ${articleData.content.length} characters`);
    if (articleData.readingTime) {
      console.log(`✓ Reading time: ${articleData.readingTime}`);
    }

    // Format and save the output
    const output = `# ${articleData.title}

**Author:** ${articleData.author}
**URL:** ${url}
**Scraped:** ${new Date().toISOString()}
${articleData.readingTime ? `**Reading Time:** ${articleData.readingTime}` : ''}

---

${articleData.content}
`;

    const filename = outputFile || `medium-article-${Date.now()}.md`;
    fs.writeFileSync(filename, output, 'utf-8');

    console.log(`\n✅ SUCCESS! Article saved to: ${filename}`);
    console.log(`\n📊 First 500 characters:\n`);
    console.log(articleData.content.substring(0, 500) + '...\n');

    // Keep browser open briefly
    console.log('Browser will close in 3 seconds...');
    await page.waitForTimeout(3000);

  } catch (error) {
    console.error('\n❌ Error scraping article:', error.message);
    const screenshotPath = `error-screenshot-${Date.now()}.png`;
    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log(`📸 Screenshot saved to: ${screenshotPath}`);
  } finally {
    await browser.close();
  }
}

// CLI usage
const url = process.argv[2];
const outputFile = process.argv[3];

if (!url) {
  console.error('Usage: node scrape-medium-authenticated.js <url> [output-file]');
  process.exit(1);
}

scrapeArticle(url, outputFile)
  .then(() => {
    console.log('✅ Done!');
    process.exit(0);
  })
  .catch(err => {
    console.error('❌ Fatal error:', err);
    process.exit(1);
  });
