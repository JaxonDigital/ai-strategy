#!/usr/bin/env node
/**
 * Medium Article Scraper using Playwright
 * Usage: node scrape-medium.js <url> [output-file]
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function scrapeArticle(url, outputFile) {
  const browser = await chromium.launch({
    headless: false, // Set to false so you can see what's happening and log in if needed
    slowMo: 100
  });

  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });

  const page = await context.newPage();

  try {
    console.log(`Navigating to: ${url}`);
    await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });

    // Wait a bit for any dynamic content
    await page.waitForTimeout(2000);

    // Check if we hit a paywall or login
    const pageTitle = await page.title();
    console.log(`Page title: ${pageTitle}`);

    // Try to extract article content
    // Medium articles are usually in <article> tags or specific divs
    const articleContent = await page.evaluate(() => {
      // Try different selectors for Medium article content
      const selectors = [
        'article',
        '[data-testid="article-content"]',
        '.postArticle-content',
        'section[data-field="body"]',
        'div[class*="article"]'
      ];

      for (const selector of selectors) {
        const element = document.querySelector(selector);
        if (element) {
          return {
            title: document.querySelector('h1')?.innerText || '',
            author: document.querySelector('[rel="author"]')?.innerText ||
                    document.querySelector('[data-testid="authorName"]')?.innerText || '',
            content: element.innerText || element.textContent,
            selector: selector
          };
        }
      }

      // Fallback: get all text from body
      return {
        title: document.querySelector('h1')?.innerText || '',
        author: '',
        content: document.body.innerText,
        selector: 'body (fallback)'
      };
    });

    console.log(`Found content using selector: ${articleContent.selector}`);
    console.log(`Title: ${articleContent.title}`);
    console.log(`Author: ${articleContent.author}`);
    console.log(`Content length: ${articleContent.content.length} characters`);

    // Check if we need to scroll to load more content
    const hasMoreContent = await page.evaluate(() => {
      return document.body.scrollHeight > window.innerHeight;
    });

    if (hasMoreContent) {
      console.log('Scrolling to load full content...');
      await page.evaluate(async () => {
        await new Promise((resolve) => {
          let totalHeight = 0;
          const distance = 100;
          const timer = setInterval(() => {
            const scrollHeight = document.body.scrollHeight;
            window.scrollBy(0, distance);
            totalHeight += distance;

            if (totalHeight >= scrollHeight) {
              clearInterval(timer);
              resolve();
            }
          }, 100);
        });
      });

      await page.waitForTimeout(1000);

      // Re-extract content after scrolling
      const fullContent = await page.evaluate(() => {
        const article = document.querySelector('article') || document.body;
        return article.innerText || article.textContent;
      });

      articleContent.content = fullContent;
      console.log(`Updated content length: ${fullContent.length} characters`);
    }

    // Format the output
    const output = `# ${articleContent.title}

**Author:** ${articleContent.author}
**URL:** ${url}
**Scraped:** ${new Date().toISOString()}

---

${articleContent.content}
`;

    // Save to file
    const filename = outputFile || `medium-article-${Date.now()}.md`;
    fs.writeFileSync(filename, output, 'utf-8');
    console.log(`\n✓ Saved to: ${filename}`);
    console.log(`\nFirst 500 characters of content:\n${articleContent.content.substring(0, 500)}...\n`);

    // Keep browser open for 5 seconds so you can see the page
    console.log('\nBrowser will close in 5 seconds...');
    await page.waitForTimeout(5000);

  } catch (error) {
    console.error('Error scraping article:', error.message);

    // Take a screenshot for debugging
    const screenshotPath = `error-screenshot-${Date.now()}.png`;
    await page.screenshot({ path: screenshotPath, fullPage: true });
    console.log(`Screenshot saved to: ${screenshotPath}`);

  } finally {
    await browser.close();
  }
}

// CLI usage
const url = process.argv[2];
const outputFile = process.argv[3];

if (!url) {
  console.error('Usage: node scrape-medium.js <url> [output-file]');
  process.exit(1);
}

scrapeArticle(url, outputFile)
  .then(() => console.log('Done!'))
  .catch(err => {
    console.error('Fatal error:', err);
    process.exit(1);
  });
