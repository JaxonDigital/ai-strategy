#!/usr/bin/env python3
"""
Generate Medium recommendation adjustments based on article relevance assessment.

Analyzes which authors, publications, and topics produce HIGH vs LOW priority content
and generates specific actionable recommendations for improving Medium's daily digest.

Usage:
    python3 generate-medium-recommendations.py ASSESSMENT_FILE METADATA_JSON [PDF_DIR]

Arguments:
    ASSESSMENT_FILE  - Path to relevance assessment markdown
    METADATA_JSON    - Path to article metadata JSON (from extract-medium-articles.py)
    PDF_DIR          - Optional: Directory containing article PDFs for metadata extraction

Output:
    Prints recommendation analysis to console with specific actions:
    - Authors to follow (from HIGH priority articles)
    - Publications to follow (from HIGH priority articles)
    - Topics to add (based on HIGH priority content)
    - Topics to unfollow (producing only LOW priority articles)
    - Articles to mute (specific LOW priority articles)
"""

import sys
import json
import re
import os
import subprocess
from collections import defaultdict, Counter
from datetime import datetime

def parse_assessment(assessment_path):
    """Parse relevance assessment markdown to get priority ratings per article."""
    with open(assessment_path, 'r') as f:
        content = f.read()

    articles = []

    # Match article sections - supports two formats:
    # Old format: ### N. Article Title (PRIORITY: HIGH/MEDIUM/LOW)
    # New format: ### ARTICLE-NN - Title
    #             **Priority:** HIGH ⭐⭐⭐⭐⭐

    # Try new format first (from generate-article-assessment.py)
    new_pattern = r'###\s+ARTICLE-(\d+)\s+-\s+(.+?)$'

    for match in re.finditer(new_pattern, content, re.MULTILINE):
        article_num = int(match.group(1))
        title = match.group(2).strip()

        # Extract the article section content
        start_pos = match.end()
        # Find next article or end of file
        next_match = re.search(r'###\s+ARTICLE-\d+', content[start_pos:])
        if next_match:
            end_pos = start_pos + next_match.start()
        else:
            # Also look for section breaks (--- or ##)
            section_match = re.search(r'\n##\s+', content[start_pos:])
            if section_match:
                end_pos = start_pos + section_match.start()
            else:
                end_pos = len(content)

        section_content = content[start_pos:end_pos]

        # Extract priority from **Priority:** line
        priority_match = re.search(r'\*\*Priority:\*\*\s+(HIGH|MEDIUM|LOW)', section_content)
        priority = priority_match.group(1) if priority_match else "UNKNOWN"

        # Extract relevance summary
        relevance_match = re.search(r'\*\*Relevance Summary:\*\*\s*(.+?)(?=\n\*\*|###|$)', section_content, re.DOTALL)
        relevance = relevance_match.group(1).strip() if relevance_match else ""

        articles.append({
            'number': article_num,
            'title': title,
            'priority': priority,
            'relevance': relevance
        })

    # If no new format matches found, try old format for backward compatibility
    if not articles:
        old_pattern = r'###\s+(\d+)\.\s+(.+?)\s+\(PRIORITY:\s+(HIGH|MEDIUM|LOW)\)'

        for match in re.finditer(old_pattern, content):
            article_num = int(match.group(1))
            title = match.group(2).strip()
            priority = match.group(3)

            # Extract the article section content
            start_pos = match.end()
            # Find next article or end of file
            next_match = re.search(r'###\s+\d+\.', content[start_pos:])
            if next_match:
                end_pos = start_pos + next_match.start()
            else:
                end_pos = len(content)

            section_content = content[start_pos:end_pos]

            # Extract relevance reasoning
            relevance_match = re.search(r'\*\*Relevance:\*\*\s*(.+?)(?=\*\*|###|$)', section_content, re.DOTALL)
            relevance = relevance_match.group(1).strip() if relevance_match else ""

            articles.append({
                'number': article_num,
                'title': title,
                'priority': priority,
                'relevance': relevance
            })

    return articles

def extract_author_from_pdf(pdf_path):
    """Extract author name from PDF using pdftotext."""
    if not os.path.exists(pdf_path):
        return None

    try:
        # Extract first page text
        result = subprocess.run(
            ['pdftotext', '-l', '1', pdf_path, '-'],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            return None

        text = result.stdout

        # Common patterns for author names on Medium
        # Pattern 1: "Written by AuthorName" or "By AuthorName"
        match = re.search(r'(?:Written by|By)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', text)
        if match:
            return match.group(1)

        # Pattern 2: Author name usually appears near top, look for capitalized names
        lines = text.split('\n')[:10]  # First 10 lines
        for line in lines:
            # Skip common headers
            if any(skip in line for skip in ['Medium', 'Member-only', 'Open in app', 'Sign up', 'Sign in']):
                continue
            # Look for names (2-3 capitalized words)
            match = re.search(r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})$', line.strip())
            if match:
                name = match.group(1)
                # Exclude common false positives
                if name not in ['The Context', 'Context Layer', 'Model Context']:
                    return name

        return None

    except Exception as e:
        print(f"Warning: Failed to extract author from {pdf_path}: {e}", file=sys.stderr)
        return None

def extract_publication_from_url(url):
    """Extract publication name from Medium URL."""
    # Pattern: medium.com/publication-name/article-slug
    match = re.search(r'medium\.com/([^/@][^/]+)/', url)
    if match:
        pub_slug = match.group(1)
        # Convert slug to title case
        return ' '.join(word.capitalize() for word in pub_slug.split('-'))

    # Personal blog format: medium.com/@author/article
    if '/@' in url:
        return None  # Personal blog, not a publication

    return None

def extract_topics_from_content(articles):
    """Extract potential Medium topics from article titles and content."""
    # Keywords that suggest specific topics
    topic_keywords = {
        'Model Context Protocol': ['mcp', 'model context protocol', 'context protocol'],
        'Agentic AI': ['agentic ai', 'ai agents', 'autonomous agents'],
        'Software Development': ['coding', 'programming', 'developer', 'development'],
        'Machine Learning': ['machine learning', 'ml', 'neural network'],
        'DevOps': ['devops', 'deployment', 'cicd', 'kubernetes'],
        'Web Development': ['react', 'javascript', 'frontend', 'backend'],
        'Data Science': ['data science', 'data analysis', 'analytics'],
        'Cloud Computing': ['aws', 'azure', 'cloud', 'serverless'],
    }

    topic_scores = defaultdict(int)

    for article in articles:
        text = (article['title'] + ' ' + article.get('relevance', '')).lower()

        # Weight by priority
        weight = {'HIGH': 3, 'MEDIUM': 1, 'LOW': -1}.get(article['priority'], 0)

        for topic, keywords in topic_keywords.items():
            if any(keyword in text for keyword in keywords):
                topic_scores[topic] += weight

    return topic_scores

def generate_recommendations(assessment_path, metadata_path, pdf_dir=None):
    """Generate comprehensive recommendations for Medium follows."""

    # Parse assessment
    articles = parse_assessment(assessment_path)

    # Load metadata
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)

    # Map article numbers to metadata
    article_map = {a['number']: a for a in metadata['articles']}

    # Collect author and publication data
    author_scores = defaultdict(lambda: {'high': 0, 'medium': 0, 'low': 0, 'articles': []})
    publication_scores = defaultdict(lambda: {'high': 0, 'medium': 0, 'low': 0, 'articles': []})
    mute_candidates = []

    for article in articles:
        num = article['number']
        if num not in article_map:
            continue

        meta = article_map[num]
        priority = article['priority']

        # Extract author
        author = None
        if pdf_dir:
            # Find PDF by article number prefix (robust to filename variations)
            pdf_prefix = f"{num:02d}-"
            pdf_files = [f for f in os.listdir(pdf_dir) if f.startswith(pdf_prefix) and f.endswith('.pdf')]

            if pdf_files:
                pdf_path = os.path.join(pdf_dir, pdf_files[0])
                author = extract_author_from_pdf(pdf_path)

        if not author:
            # Try to extract from URL
            url_match = re.search(r'@([^/]+)', meta['url'])
            if url_match:
                author_slug = url_match.group(1)
                author = '@' + author_slug

        # Extract publication
        publication = extract_publication_from_url(meta['url'])

        # Track author scores
        if author:
            author_scores[author][priority.lower()] += 1
            author_scores[author]['articles'].append({
                'ticket': meta.get('ticket_id'),
                'title': article['title'],
                'priority': priority
            })

        # Track publication scores
        if publication:
            publication_scores[publication][priority.lower()] += 1
            publication_scores[publication]['articles'].append({
                'ticket': meta.get('ticket_id'),
                'title': article['title'],
                'priority': priority
            })

        # Track mute candidates (LOW priority with specific reasons)
        if priority == 'LOW':
            mute_candidates.append({
                'title': article['title'],
                'author': author,
                'relevance': article['relevance'][:150] + '...' if len(article['relevance']) > 150 else article['relevance'],
                'ticket': meta.get('ticket_id')
            })

    # Analyze topics
    topic_scores = extract_topics_from_content(articles)

    # Generate recommendations
    print("\n" + "="*70)
    print("MEDIUM RECOMMENDATION ANALYSIS")
    print("="*70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d')}")

    # Count priorities
    priority_counts = Counter(a['priority'] for a in articles)
    print(f"Articles Reviewed: {len(articles)} ({priority_counts['HIGH']} HIGH, {priority_counts['MEDIUM']} MEDIUM, {priority_counts['LOW']} LOW)")
    print()

    print("RECOMMENDED ACTIONS:")
    print()

    # Authors to follow (HIGH priority articles)
    follow_authors = [
        (author, data) for author, data in author_scores.items()
        if data['high'] >= 1  # At least 1 HIGH priority article
    ]
    follow_authors.sort(key=lambda x: x[1]['high'], reverse=True)

    if follow_authors:
        print("✅ FOLLOW THESE AUTHORS:")
        for i, (author, data) in enumerate(follow_authors, 1):
            print(f"  {i}. Follow {author}")

            # Reason
            article_count = data['high']
            article_word = "article" if article_count == 1 else "articles"
            high_articles = [a for a in data['articles'] if a['priority'] == 'HIGH']

            # Get first HIGH article for context
            first_article = high_articles[0]
            title_snippet = first_article['title'][:60] + '...' if len(first_article['title']) > 60 else first_article['title']

            print(f"     Reason: Wrote {article_count} HIGH priority {article_word} about {title_snippet}")

            # List tickets
            tickets = ', '.join(a['ticket'] for a in high_articles if a.get('ticket'))
            if tickets:
                print(f"     Articles: {tickets}")
            print()
    else:
        print("✅ FOLLOW THESE AUTHORS:")
        print("  (No new authors to recommend - no HIGH priority articles from new authors)")
        print()

    # Publications to follow
    follow_publications = [
        (pub, data) for pub, data in publication_scores.items()
        if data['high'] >= 1  # At least 1 HIGH priority article
    ]
    follow_publications.sort(key=lambda x: x[1]['high'], reverse=True)

    if follow_publications:
        print("📰 FOLLOW THESE PUBLICATIONS:")
        for i, (pub, data) in enumerate(follow_publications, 1):
            print(f"  {i}. Follow '{pub}'")

            article_count = data['high']
            article_word = "article" if article_count == 1 else "articles"
            print(f"     Reason: Published {article_count} HIGH priority {article_word}")

            tickets = ', '.join(
                a['ticket'] for a in data['articles']
                if a['priority'] == 'HIGH' and a.get('ticket')
            )
            if tickets:
                print(f"     Articles: {tickets}")
            print()
    else:
        print("📰 FOLLOW THESE PUBLICATIONS:")
        print("  (No publications identified - most articles are from personal blogs)")
        print()

    # Topics to add
    add_topics = [(topic, score) for topic, score in topic_scores.items() if score >= 3]
    add_topics.sort(key=lambda x: x[1], reverse=True)

    if add_topics:
        print("➕ ADD THESE TOPICS:")
        for i, (topic, score) in enumerate(add_topics, 1):
            print(f"  {i}. Follow topic '{topic}'")
            print(f"     Reason: {score} points from HIGH priority articles with {topic.lower()} content")
            print()
    else:
        print("➕ ADD THESE TOPICS:")
        print("  (Current topics appear to be working well)")
        print()

    # Topics to consider unfollowing (only LOW priority)
    # Note: This would require knowing current follows - placeholder for now
    print("❌ CONSIDER UNFOLLOWING:")
    print("  (Analysis requires current following list - review manually)")
    print("  Tip: Look for topics that only produced LOW priority articles")
    print()

    # Authors to watch (LOW priority content)
    if mute_candidates:
        # Group LOW priority articles by author
        author_low_priority = defaultdict(list)
        for article in mute_candidates:
            if article['author']:
                author_low_priority[article['author']].append(article)

        print("⚠️ AUTHORS TO WATCH (LOW PRIORITY CONTENT):")
        print("  Note: Medium allows muting authors/publications, not individual articles")
        print()

        # Authors with multiple LOW priority articles (strong signal)
        multiple_low = [(author, articles) for author, articles in author_low_priority.items() if len(articles) > 1]
        multiple_low.sort(key=lambda x: len(x[1]), reverse=True)

        if multiple_low:
            print("  📊 Consider Unfollowing (Multiple LOW priority articles):")
            for author, articles in multiple_low:
                print(f"    • {author} - {len(articles)} LOW priority articles")
                # Show first example
                print(f"      Example: '{articles[0]['title'][:50]}...'")
                print(f"      Reason: {articles[0]['relevance']}")
                if articles[0].get('ticket'):
                    print(f"      Ticket: {articles[0]['ticket']}")
                print()

        # Authors with single LOW priority articles (watch list)
        single_low = [(author, articles) for author, articles in author_low_priority.items() if len(articles) == 1]

        if single_low:
            print("  👀 Watch List (Single LOW priority article - may be one-off):")
            for author, articles in single_low[:3]:  # Show first 3
                article = articles[0]
                print(f"    • {author}")
                print(f"      Article: '{article['title'][:50]}...'")
                print(f"      Reason: {article['relevance']}")
                if article.get('ticket'):
                    print(f"      Ticket: {article['ticket']}")
                print()

            if len(single_low) > 3:
                print(f"    ... and {len(single_low) - 3} more authors with single LOW priority articles")
                print()
    else:
        print("⚠️ AUTHORS TO WATCH:")
        print("  (No LOW priority articles - all content was relevant)")
        print()

    # Summary of current following status (from screenshot)
    print("="*70)
    print("CURRENT FOLLOWING STATUS (for reference):")
    print("="*70)
    print("Writers: Medium Staff")
    print("Publications: The Context Layer")
    print("Topics: Artificial Intelligence, Technology, Self Improvement")
    print()
    print("💡 Tip: Visit https://medium.com/me/following/suggestions to refine")
    print("="*70)
    print()

def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    assessment_path = sys.argv[1]
    metadata_path = sys.argv[2]
    pdf_dir = sys.argv[3] if len(sys.argv) > 3 else None

    if not os.path.exists(assessment_path):
        print(f"Error: Assessment file not found: {assessment_path}", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(metadata_path):
        print(f"Error: Metadata file not found: {metadata_path}", file=sys.stderr)
        sys.exit(1)

    if pdf_dir and not os.path.exists(pdf_dir):
        print(f"Warning: PDF directory not found: {pdf_dir}", file=sys.stderr)
        print("Continuing without PDF metadata extraction...", file=sys.stderr)
        pdf_dir = None

    # Capture output to both stdout and file
    import io
    from contextlib import redirect_stdout

    # Extract date from assessment filename (e.g., medium-articles-relevance-assessment-2025-11-13.md)
    assessment_basename = os.path.basename(assessment_path)
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', assessment_basename)
    if date_match:
        file_date = date_match.group(1)
    else:
        # Fallback to current date if pattern not found
        file_date = datetime.now().strftime('%Y-%m-%d')

    # Create outputs directory if it doesn't exist
    outputs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'outputs')
    os.makedirs(outputs_dir, exist_ok=True)

    # Output file path
    output_file = os.path.join(outputs_dir, f'medium-recommendations-{file_date}.txt')

    # Capture output
    output_buffer = io.StringIO()
    with redirect_stdout(output_buffer):
        generate_recommendations(assessment_path, metadata_path, pdf_dir)

    # Get captured output
    output_text = output_buffer.getvalue()

    # Print to stdout
    print(output_text)

    # Write to file
    with open(output_file, 'w') as f:
        f.write(output_text)

    print(f"\n✓ Recommendations saved to: {output_file}", file=sys.stderr)

if __name__ == '__main__':
    main()
