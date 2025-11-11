#!/usr/bin/env python3.11
"""
Generate strategic relevance assessment for article PDFs using OpenAI API.

This script reads PDFs from a directory, analyzes their relevance to Jaxon Digital's
AI agent initiatives, and generates a comprehensive markdown assessment document.

Usage:
    export OPENAI_API_KEY="sk-proj-..."
    python3 generate-article-assessment.py <pdf_dir> <metadata_json> <output_md>

Arguments:
    pdf_dir: Directory containing article PDFs
    metadata_json: JSON file with article metadata (from monitor/extract scripts)
    output_md: Output path for assessment markdown file

Example:
    python3 generate-article-assessment.py \
        /Users/bgerby/Documents/dev/ai/pdfs/optimizely-articles-2025-10-23/ \
        /tmp/optimizely-articles.json \
        /Users/bgerby/Documents/dev/ai/assessments/optimizely-articles-relevance-assessment-2025-10-23.md
"""

import os
import sys
import json
import subprocess
import re
import time
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Check for OpenAI package
try:
    from openai import OpenAI
    import openai
except ImportError:
    print("Error: openai package not installed. Install with: pip3 install openai")
    sys.exit(1)

def openai_api_call_with_retry(api_call_func, max_retries=5):
    """
    Wrapper for OpenAI API calls with exponential backoff for rate limits.

    Args:
        api_call_func: Function that makes the OpenAI API call
        max_retries: Maximum number of retry attempts (default: 5)

    Returns:
        Result from api_call_func

    Raises:
        Last exception if all retries fail
    """
    for attempt in range(max_retries):
        try:
            return api_call_func()
        except openai.RateLimitError as e:
            if attempt == max_retries - 1:
                # Last attempt failed, re-raise
                raise
            # Exponential backoff with jitter
            delay = (2 ** attempt) + random.uniform(0, 1)
            print(f"  ⚠️  Rate limit hit, retrying in {delay:.1f}s (attempt {attempt + 1}/{max_retries})")
            time.sleep(delay)
        except openai.APIError as e:
            # API errors (500, 503, etc.) - retry with backoff
            if attempt == max_retries - 1:
                raise
            delay = (2 ** attempt) + random.uniform(0, 1)
            print(f"  ⚠️  API error, retrying in {delay:.1f}s (attempt {attempt + 1}/{max_retries})")
            time.sleep(delay)
        except Exception as e:
            # Other errors, don't retry
            raise

# Path to canonical strategic context in Pivot project
PIVOT_STRATEGIC_CONTEXT_PATH = "/Users/bgerby/Documents/dev/pivot/sprint-0/STRATEGIC_CONTEXT.md"

def load_strategic_context() -> str:
    """
    Load strategic context from canonical Pivot project source with fallback.

    Returns:
        Strategic context string for AI analysis
    """
    try:
        if os.path.exists(PIVOT_STRATEGIC_CONTEXT_PATH):
            with open(PIVOT_STRATEGIC_CONTEXT_PATH, 'r', encoding='utf-8') as f:
                content = f.read()

                # Extract "For AI Analysis & Content Review" section (lines 309-353)
                match = re.search(
                    r'## For AI Analysis & Content Review.*?(?=\n---)',
                    content,
                    re.DOTALL
                )

                if match:
                    context = match.group(0)
                    print("✓ Loaded strategic context from Pivot project")
                    return f"""
Jaxon Digital Strategic Context (Source: Pivot Project)

NOTE: Jaxon Digital is transforming from an Optimizely implementation partner
to a SaaS platform for AI Operations (October 2025 - 6 month transformation).

{context}

**Current Focus:**
- Building AI Operations Platform (SaaS model)
- Agent orchestration with LangGraph + n8n
- Agent #19 (Early Warning System) as top priority
- Product-led growth targeting agencies first
- Multi-tenant platform architecture
- Subscription billing and managed services
"""

        # Fallback to legacy context
        print("⚠ Pivot context not found, using legacy strategic context")
        return JAXON_STRATEGIC_CONTEXT_LEGACY

    except Exception as e:
        print(f"⚠ Error loading Pivot context: {e}, using legacy strategic context")
        return JAXON_STRATEGIC_CONTEXT_LEGACY

# Legacy strategic context (fallback for when Pivot project unavailable)
JAXON_STRATEGIC_CONTEXT_LEGACY = """
Jaxon Digital is an Optimizely implementation partner focused on AI agent initiatives:

**Current Focus:**
- Custom MCP (Model Context Protocol) development for Optimizely DXP operations
- Building production agents for CMS, Commerce, and DevOps automation
- Managed agent operations service ($8-20K/month)
- Custom system integrations ($40-100K per MCP)

**Technology Stack:**
- Custom MCPs for Optimizely-specific operations
- n8n for workflow orchestration
- Multi-MCP orchestration for complex workflows
- Event-driven proactive monitoring agents

**Relevance Criteria:**

HIGH Priority (⭐⭐⭐⭐⭐):
- Direct MCP development insights or competitive intelligence
- AI agent architecture and production patterns
- Optimizely platform integration strategies
- Competitive analysis (e.g., other developers building Optimizely MCPs)
- Event-driven automation and proactive monitoring

MEDIUM Priority (⭐⭐⭐):
- Optimizely platform features and capabilities
- DevOps automation and deployment workflows
- CMS/Commerce enhancements
- General AI/ML trends applicable to our work
- Client education topics

LOW Priority (⭐):
- Niche technical implementations not applicable to our clients
- Off-topic content (health, finance, etc.)
- Basic tutorials or beginner content
- Peripheral technologies unrelated to our stack
"""

# Load strategic context at module initialization
JAXON_STRATEGIC_CONTEXT = load_strategic_context()

def clean_text_for_analysis(text: str) -> str:
    """Clean extracted PDF text for better analysis."""
    # Remove login/signup prompts
    text = re.sub(r'(Sign up|Log in|Sign In|Create an account).*?(Medium|Optimizely)', '', text, flags=re.IGNORECASE | re.DOTALL)

    # Remove "Member-only story" banners
    text = re.sub(r'Member-only story.*?\n', '', text, flags=re.IGNORECASE)

    # Remove social sharing prompts
    text = re.sub(r'Share this article.*?\n', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Follow.*?for more.*?\n', '', text, flags=re.IGNORECASE)

    # Remove footer navigation
    text = re.sub(r'(Home|About|Contact|Privacy Policy|Terms of Service).*?$', '', text, flags=re.IGNORECASE | re.MULTILINE)

    # Remove excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)

    # Remove page numbers
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)

    return text.strip()

def extract_pdf_text(pdf_path: str) -> Optional[str]:
    """Extract text from PDF using pdftotext."""
    try:
        result = subprocess.run(
            ['pdftotext', pdf_path, '-'],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return clean_text_for_analysis(result.stdout)
        else:
            print(f"  ⚠ pdftotext failed for {pdf_path}: {result.stderr}")
            return None
    except subprocess.TimeoutExpired:
        print(f"  ⚠ Timeout extracting text from {pdf_path}")
        return None
    except Exception as e:
        print(f"  ⚠ Error extracting text from {pdf_path}: {e}")
        return None

def chunk_text(text: str, max_chars: int = 12000, overlap: int = 500) -> List[str]:
    """Split text into overlapping chunks for large documents."""
    if len(text) <= max_chars:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars

        # Try to break at paragraph boundary
        if end < len(text):
            paragraph_break = text.rfind('\n\n', start, end)
            if paragraph_break > start + (max_chars // 2):
                end = paragraph_break

        chunks.append(text[start:end])
        start = end - overlap  # Overlap to maintain context

    return chunks

def analyze_article(client: OpenAI, title: str, url: str, text: str, ticket_id: str) -> Dict:
    """Analyze a single article using OpenAI API."""
    # Chunk text if too large
    chunks = chunk_text(text, max_chars=12000)

    # For multi-chunk documents, analyze each chunk and synthesize
    if len(chunks) > 1:
        print(f"  → Article split into {len(chunks)} chunks for analysis")
        chunk_analyses = []

        for i, chunk in enumerate(chunks, 1):
            analysis = analyze_chunk(client, title, url, chunk, ticket_id, i, len(chunks))
            if analysis:
                chunk_analyses.append(analysis)
            time.sleep(1)  # Rate limiting

        # Synthesize chunk analyses
        return synthesize_analyses(client, title, url, chunk_analyses, ticket_id)
    else:
        # Single chunk - direct analysis
        return analyze_chunk(client, title, url, chunks[0], ticket_id, 1, 1)

def analyze_chunk(client: OpenAI, title: str, url: str, text: str, ticket_id: str,
                  chunk_num: int, total_chunks: int) -> Optional[Dict]:
    """Analyze a single text chunk."""
    chunk_context = f" (Part {chunk_num}/{total_chunks})" if total_chunks > 1 else ""

    prompt = f"""Analyze this article{chunk_context} for relevance to Jaxon Digital's AI agent initiatives.

Article: {title}
URL: {url}
Ticket: {ticket_id}

{JAXON_STRATEGIC_CONTEXT}

Article Content:
{text[:15000]}

Provide analysis in JSON format:
{{
  "priority": "HIGH|MEDIUM|LOW",
  "stars": 1-5,
  "relevance_summary": "2-3 sentence summary of why this matters to Jaxon",
  "key_insights": ["insight 1", "insight 2", ...],
  "strategic_implications": ["implication 1", "implication 2", ...],
  "action_items": ["action 1", "action 2", ...],
  "topics": ["topic1", "topic2", ...]
}}

Focus on:
- Specific technical details and approaches
- Competitive intelligence and market positioning
- Actionable insights for Jaxon's service offerings
- Client education opportunities
"""

    try:
        # Wrap API call with retry logic for rate limit handling
        def make_api_call():
            return client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a strategic analyst for Jaxon Digital, assessing article relevance to AI agent initiatives."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

        response = openai_api_call_with_retry(make_api_call)
        analysis = json.loads(response.choices[0].message.content)
        return analysis

    except Exception as e:
        print(f"  ⚠ OpenAI API error for {ticket_id}: {e}")
        return None

def synthesize_analyses(client: OpenAI, title: str, url: str,
                       chunk_analyses: List[Dict], ticket_id: str) -> Dict:
    """Synthesize multiple chunk analyses into unified assessment."""
    synthesis_prompt = f"""Synthesize these chunk analyses into a unified strategic assessment.

Article: {title}
URL: {url}
Ticket: {ticket_id}

Chunk Analyses:
{json.dumps(chunk_analyses, indent=2)}

{JAXON_STRATEGIC_CONTEXT}

Provide unified analysis in JSON format:
{{
  "priority": "HIGH|MEDIUM|LOW",
  "stars": 1-5,
  "relevance_summary": "2-3 sentence comprehensive summary",
  "key_insights": ["unified insight 1", "unified insight 2", ...],
  "strategic_implications": ["unified implication 1", ...],
  "action_items": ["unified action 1", ...],
  "topics": ["topic1", "topic2", ...]
}}

Combine insights from all chunks, prioritize most important points, remove duplicates.
"""

    try:
        # Wrap API call with retry logic for rate limit handling
        def make_api_call():
            return client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a strategic analyst synthesizing multi-part article analysis."},
                    {"role": "user", "content": synthesis_prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

        response = openai_api_call_with_retry(make_api_call)
        return json.loads(response.choices[0].message.content)

    except Exception as e:
        print(f"  ⚠ Synthesis error for {ticket_id}: {e}")
        # Fallback: merge chunk analyses naively
        return merge_chunk_analyses(chunk_analyses)

def merge_chunk_analyses(analyses: List[Dict]) -> Dict:
    """Naive merge of chunk analyses as fallback."""
    if not analyses:
        return {
            "priority": "LOW",
            "stars": 1,
            "relevance_summary": "Unable to analyze article.",
            "key_insights": [],
            "strategic_implications": [],
            "action_items": [],
            "topics": []
        }

    # Use first analysis as base
    merged = analyses[0].copy()

    # Merge lists from subsequent analyses
    for analysis in analyses[1:]:
        merged["key_insights"].extend(analysis.get("key_insights", []))
        merged["strategic_implications"].extend(analysis.get("strategic_implications", []))
        merged["action_items"].extend(analysis.get("action_items", []))
        merged["topics"].extend(analysis.get("topics", []))

    # Deduplicate
    merged["key_insights"] = list(set(merged["key_insights"]))[:5]
    merged["strategic_implications"] = list(set(merged["strategic_implications"]))[:5]
    merged["action_items"] = list(set(merged["action_items"]))[:5]
    merged["topics"] = list(set(merged["topics"]))

    return merged

def format_article_section(article: Dict, analysis: Dict) -> str:
    """Format a single article section in markdown."""
    stars = "⭐" * int(analysis.get("stars", 1))
    priority = analysis.get("priority", "LOW")

    section = f"""### {article.get("ticket_id", "UNKNOWN")} - {article.get("title", "Unknown Title")}

**Priority:** {priority} {stars}
**Article URL:** {article.get("url", "Unknown URL")}
**Author:** {article.get("author", "Unknown")}
**Published:** {article.get("published_date", "Unknown")}

**Relevance Summary:**
{analysis.get("relevance_summary", "No summary available.")}

**Key Insights:**
{chr(10).join(f"- {insight}" for insight in analysis.get("key_insights", []))}

**Strategic Implications:**
{chr(10).join(f"- {impl}" for impl in analysis.get("strategic_implications", []))}

**Action Items:**
{chr(10).join(f"- {action}" for action in analysis.get("action_items", []))}

**Topics:** {", ".join(analysis.get("topics", []))}

---

"""
    return section

def generate_assessment_document(articles: List[Dict], analyses: Dict,
                                output_path: str, source: str = "Articles"):
    """Generate complete assessment markdown document."""
    # Count priorities
    priority_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for analysis in analyses.values():
        priority = analysis.get("priority", "LOW")
        priority_counts[priority] = priority_counts.get(priority, 0) + 1

    # Sort articles by priority
    priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    sorted_articles = sorted(
        articles,
        key=lambda a: (
            priority_order.get(analyses.get(a.get("ticket_id", ""), {}).get("priority", "LOW"), 3),
            a.get("ticket_id", "")
        )
    )

    # Generate document
    date = datetime.now().strftime("%Y-%m-%d")
    doc = f"""# {source} Relevance Assessment

**Date:** {date}
**Total Articles:** {len(articles)}

## Summary Statistics

- **HIGH Priority:** {priority_counts['HIGH']} articles ⭐⭐⭐⭐⭐
- **MEDIUM Priority:** {priority_counts['MEDIUM']} articles ⭐⭐⭐
- **LOW Priority:** {priority_counts['LOW']} articles ⭐

## Assessment Methodology

Articles were analyzed against Jaxon Digital's strategic focus areas:
- Custom MCP development and AI agent architecture
- Optimizely platform integration and automation
- Competitive intelligence and market positioning
- Client education and service differentiation

---

## HIGH Priority Articles (⭐⭐⭐⭐⭐)

These articles have direct relevance to Jaxon's current initiatives and should be reviewed immediately.

"""

    # Add HIGH priority articles
    high_articles = [a for a in sorted_articles if analyses.get(a.get("ticket_id", ""), {}).get("priority") == "HIGH"]
    if high_articles:
        for article in high_articles:
            ticket_id = article.get("ticket_id", "UNKNOWN")
            if ticket_id in analyses:
                doc += format_article_section(article, analyses[ticket_id])
    else:
        doc += "No HIGH priority articles in this batch.\n\n---\n\n"

    # Add MEDIUM priority articles
    doc += """## MEDIUM Priority Articles (⭐⭐⭐)

These articles have moderate relevance and should be reviewed when time permits.

"""

    medium_articles = [a for a in sorted_articles if analyses.get(a.get("ticket_id", ""), {}).get("priority") == "MEDIUM"]
    if medium_articles:
        for article in medium_articles:
            ticket_id = article.get("ticket_id", "UNKNOWN")
            if ticket_id in analyses:
                doc += format_article_section(article, analyses[ticket_id])
    else:
        doc += "No MEDIUM priority articles in this batch.\n\n---\n\n"

    # Add LOW priority articles
    doc += """## LOW Priority Articles (⭐)

These articles have minimal relevance to Jaxon's current focus.

"""

    low_articles = [a for a in sorted_articles if analyses.get(a.get("ticket_id", ""), {}).get("priority") == "LOW"]
    if low_articles:
        for article in low_articles:
            ticket_id = article.get("ticket_id", "UNKNOWN")
            if ticket_id in analyses:
                doc += format_article_section(article, analyses[ticket_id])
    else:
        doc += "No LOW priority articles in this batch.\n\n"

    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(doc)

    print(f"\n✓ Assessment document written to: {output_path}")

def enrich_metadata_with_tickets(articles: List[Dict], state_file: str = "~/.optimizely-blog-state.json") -> List[Dict]:
    """Enrich article metadata with ticket IDs from state file."""
    state_path = os.path.expanduser(state_file)

    if not os.path.exists(state_path):
        print(f"  ⚠ Warning: State file not found at {state_path}")
        print(f"  Articles will use URL-based IDs instead of ticket numbers")
        return articles

    try:
        with open(state_path, 'r') as f:
            state = json.load(f)
    except Exception as e:
        print(f"  ⚠ Warning: Could not load state file: {e}")
        return articles

    # Get ticket mappings (URL -> ticket_id)
    created_tickets = state.get("created_tickets", {})
    url_to_ticket = state.get("url_to_ticket", {})

    enriched = []
    for i, article in enumerate(articles, 1):
        enriched_article = article.copy()
        url = article.get("url", "")
        guid = article.get("guid", "")

        # Try to find ticket ID from state file
        ticket_id = None

        # Check URL mapping first
        if url in url_to_ticket:
            ticket_id = url_to_ticket[url]
        elif guid in url_to_ticket:
            ticket_id = url_to_ticket[guid]

        # Check created_tickets (keyed by GUID)
        if not ticket_id and guid in created_tickets:
            ticket_id = created_tickets[guid].get("ticket_id")
        if not ticket_id and url in created_tickets:
            ticket_id = created_tickets[url].get("ticket_id")

        # Fallback: derive from sequential numbering
        if not ticket_id:
            ticket_id = f"ARTICLE-{i:02d}"

        enriched_article["ticket_id"] = ticket_id
        enriched_article["pdf_filename"] = f"{i:02d}-*.pdf"  # For globbing
        enriched_article["published_date"] = article.get("pub_date", "Unknown")
        enriched_article["author"] = article.get("author", "Unknown")

        enriched.append(enriched_article)

    return enriched

def main():
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)

    pdf_dir = sys.argv[1]
    metadata_json = sys.argv[2]
    output_md = sys.argv[3]

    # Check OpenAI API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Set it with: export OPENAI_API_KEY='sk-proj-...'")
        sys.exit(1)

    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)

    # Load metadata
    print(f"Loading article metadata from {metadata_json}...")
    try:
        with open(metadata_json, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
            articles = metadata.get("articles", [])
    except Exception as e:
        print(f"Error loading metadata: {e}")
        sys.exit(1)

    print(f"Found {len(articles)} articles in metadata")

    # Enrich with ticket IDs from state file (for Optimizely workflow)
    articles = enrich_metadata_with_tickets(articles)
    print(f"Enriched articles with ticket IDs\n")

    # Process each article
    analyses = {}
    for i, article in enumerate(articles, 1):
        ticket_id = article.get("ticket_id", f"UNKNOWN-{i}")
        title = article.get("title", "Unknown Title")
        url = article.get("url", "")
        pdf_filename = article.get("pdf_filename", f"{i:02d}-*.pdf")

        print(f"[{i}/{len(articles)}] {ticket_id}: {title[:50]}...")

        # Find PDF file
        pdf_pattern = Path(pdf_dir) / pdf_filename
        pdf_files = list(Path(pdf_dir).glob(pdf_filename if '*' in pdf_filename else f"*{pdf_filename}*"))

        if not pdf_files:
            print(f"  ⚠ PDF not found: {pdf_filename}")
            continue

        pdf_path = str(pdf_files[0])

        # Extract text
        text = extract_pdf_text(pdf_path)
        if not text:
            print(f"  ⚠ Could not extract text from PDF")
            continue

        print(f"  → Extracted {len(text)} characters")

        # Analyze with OpenAI
        analysis = analyze_article(client, title, url, text, ticket_id)
        if analysis:
            analyses[ticket_id] = analysis
            priority = analysis.get("priority", "UNKNOWN")
            print(f"  ✓ Analysis complete: {priority}")
        else:
            print(f"  ⚠ Analysis failed")

        # Rate limiting
        time.sleep(1)

    # Generate assessment document
    print(f"\n{'='*60}")
    print("GENERATING ASSESSMENT DOCUMENT")
    print(f"{'='*60}\n")

    source = "Optimizely World Articles" if "optimizely" in pdf_dir.lower() else "Medium Articles"
    generate_assessment_document(articles, analyses, output_md, source)

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Total articles: {len(articles)}")
    print(f"Successfully analyzed: {len(analyses)}")
    print(f"Failed: {len(articles) - len(analyses)}")

    priority_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for analysis in analyses.values():
        priority = analysis.get("priority", "LOW")
        priority_counts[priority] = priority_counts.get(priority, 0) + 1

    print(f"\nPriority breakdown:")
    print(f"  HIGH: {priority_counts['HIGH']}")
    print(f"  MEDIUM: {priority_counts['MEDIUM']}")
    print(f"  LOW: {priority_counts['LOW']}")

if __name__ == "__main__":
    main()
