#!/usr/bin/env python3
"""
Newsletter Article Processor for GAT Project
Extracts URLs from newsletter emails, checks for paywalls, creates Jira tickets

Usage: ./process-newsletter.py /path/to/email.eml
"""

import re
import sys
import urllib.request
import urllib.error
import base64
import email
from email import policy

def extract_urls_from_email(email_path):
    """Extract Medium article URLs from email file"""
    with open(email_path, 'rb') as f:
        msg = email.message_from_binary_file(f, policy=policy.default)

    urls = set()

    # Get email body (plain text or HTML)
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == 'text/plain' or content_type == 'text/html':
                try:
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    urls.update(extract_urls_from_text(body))
                except:
                    pass
    else:
        body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
        urls.update(extract_urls_from_text(body))

    # Clean URLs - remove tracking parameters and duplicates
    clean_urls = []
    for url in urls:
        # Remove query parameters
        clean_url = url.split('?')[0]
        # Remove Medium tracking fragments
        clean_url = clean_url.rstrip('>')
        if clean_url and clean_url not in clean_urls:
            clean_urls.append(clean_url)

    return clean_urls

def extract_urls_from_text(text):
    """Extract URLs from text content"""
    # Pattern for Medium URLs
    pattern = r'https?://medium\.com/[^\s<>"\'\)]+|https?://[a-zA-Z0-9-]+\.medium\.com/[^\s<>"\'\)]+'
    urls = re.findall(pattern, text)

    # Filter out non-article URLs
    filtered = []
    exclude_patterns = [
        '/plans', '/email-settings', '/@bgerby', '/me/',
        '/tag/', '/topics/', 'source=email'
    ]

    for url in urls:
        if not any(pattern in url for pattern in exclude_patterns):
            # Only include if it looks like an article (has @ author or publication)
            if '/@' in url or '/gitconnected/' in url or '/predict/' in url or '/ai-advances/' in url:
                filtered.append(url)

    return filtered

def check_paywall(url):
    """Check if URL is accessible or paywalled"""
    try:
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
        )
        response = urllib.request.urlopen(req, timeout=10)
        content = response.read().decode('utf-8', errors='ignore')

        # Check for paywall indicators
        is_paywalled = False
        paywall_indicators = [
            'member-only',
            'metered paywall',
            'become a member',
            'upgrade to read'
        ]

        for indicator in paywall_indicators:
            if indicator.lower() in content.lower():
                is_paywalled = True
                break

        # Try to extract title
        title_match = re.search(r'<title>([^<]+)</title>', content)
        title = title_match.group(1) if title_match else 'Unknown Title'
        title = title.replace(' - Medium', '').replace(' | by ', ' | ').strip()

        return {
            'url': url,
            'accessible': True,
            'paywalled': is_paywalled,
            'status': response.status,
            'title': title
        }
    except urllib.error.HTTPError as e:
        return {
            'url': url,
            'accessible': False,
            'paywalled': True,
            'status': e.code,
            'error': str(e),
            'title': 'Error accessing'
        }
    except Exception as e:
        return {
            'url': url,
            'accessible': False,
            'paywalled': True,
            'error': str(e),
            'title': 'Error accessing'
        }

def main():
    if len(sys.argv) < 2:
        print("Usage: ./process-newsletter.py /path/to/email.eml")
        sys.exit(1)

    email_path = sys.argv[1]

    print(f"📧 Processing email: {email_path}\n")

    # Extract URLs
    print("🔍 Extracting article URLs...")
    urls = extract_urls_from_email(email_path)
    print(f"Found {len(urls)} article URLs\n")

    if not urls:
        print("❌ No article URLs found in email")
        sys.exit(1)

    # Check each URL
    print("🌐 Checking article accessibility...\n")
    results = []

    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] Checking: {url[:80]}...")
        result = check_paywall(url)
        results.append(result)

        status_icon = '✅' if result['accessible'] and not result['paywalled'] else '🔒' if result.get('paywalled') else '❌'
        print(f"    {status_icon} {result['title'][:60]}")
        print()

    # Summary
    print("\n" + "="*80)
    print("📊 SUMMARY")
    print("="*80 + "\n")

    accessible = [r for r in results if r['accessible'] and not r['paywalled']]
    paywalled = [r for r in results if r.get('paywalled')]
    errors = [r for r in results if not r['accessible']]

    print(f"✅ Accessible articles: {len(accessible)}")
    print(f"🔒 Paywalled articles: {len(paywalled)}")
    print(f"❌ Errors: {len(errors)}\n")

    if paywalled:
        print("🔒 PAYWALLED ARTICLES (need PDFs):")
        print("-" * 80)
        for r in paywalled:
            print(f"  • {r['title']}")
            print(f"    {r['url']}\n")

    if accessible:
        print("✅ ACCESSIBLE ARTICLES:")
        print("-" * 80)
        for r in accessible:
            print(f"  • {r['title']}")
            print(f"    {r['url']}\n")

    # Save results to file
    output_file = email_path.replace('.eml', '-articles.txt')
    with open(output_file, 'w') as f:
        f.write("NEWSLETTER ARTICLES\n")
        f.write("=" * 80 + "\n\n")

        f.write("PAYWALLED (need PDFs):\n")
        for r in paywalled:
            f.write(f"{r['title']}\n{r['url']}\n\n")

        f.write("\nACCESSIBLE:\n")
        for r in accessible:
            f.write(f"{r['title']}\n{r['url']}\n\n")

    print(f"💾 Results saved to: {output_file}")

if __name__ == '__main__':
    main()
