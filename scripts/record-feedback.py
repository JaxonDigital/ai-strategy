#!/usr/bin/env python3.11
"""
Record feedback for article assessments to enable continuous improvement.

Usage:
    # Record priority correction
    python3 record-feedback.py GAT-482 correct "Confirmed HIGH priority"
    python3 record-feedback.py GAT-484 too-high "Not immediately applicable, should be MEDIUM"
    python3 record-feedback.py GAT-485 too-low "Actually very relevant, should be HIGH"

    # Record quality rating
    python3 record-feedback.py GAT-482 quality --audio-rating 5 --content-rating 5 --listened

    # Record action outcome
    python3 record-feedback.py GAT-482 action --completed "Research LangGraph" --completed "Review subagent patterns"

Examples:
    python3 record-feedback.py GAT-482 correct "Direct MCP relevance confirmed"
    python3 record-feedback.py GAT-484 too-high "LocalStorage too niche for current priorities"
    python3 record-feedback.py GAT-482 quality --audio-rating 5 --listened --completion 1.0
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Constants
FEEDBACK_LOG = "/Users/bgerby/Documents/dev/ai/feedback/article-feedback-log.jsonl"
STRATEGIC_CONTEXT_PATH = "/Users/bgerby/Documents/dev/pivot/sprint-0/STRATEGIC_CONTEXT.md"

def get_strategic_context_version() -> str:
    """Get current strategic context version from file modification date."""
    if os.path.exists(STRATEGIC_CONTEXT_PATH):
        mtime = os.path.getmtime(STRATEGIC_CONTEXT_PATH)
        return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
    return "unknown"

def get_article_metadata(ticket_id: str) -> Optional[Dict]:
    """
    Try to fetch article URL and original assessment from assessment files.
    Returns dict with url, original_priority, original_stars if found.
    """
    # Search in assessments directory for the ticket
    assessment_dir = Path("/Users/bgerby/Documents/dev/ai/assessments")

    if not assessment_dir.exists():
        return None

    # Look through assessment files (most recent first)
    assessment_files = sorted(assessment_dir.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)

    for assessment_file in assessment_files:
        try:
            with open(assessment_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Look for ticket ID
            if ticket_id not in content:
                continue

            # Extract metadata using simple parsing
            # Format: ### GAT-XXX - Title
            # **Priority:** HIGH ⭐⭐⭐⭐⭐
            # **Article URL:** https://...

            import re

            # Find the section for this ticket
            pattern = rf'### {ticket_id}.*?\n\*\*Priority:\*\* (HIGH|MEDIUM|LOW) (⭐+).*?\n\*\*Article URL:\*\* (https?://\S+)'
            match = re.search(pattern, content, re.DOTALL)

            if match:
                priority = match.group(1)
                stars = len(match.group(2))
                url = match.group(3)

                return {
                    "url": url,
                    "original_priority": priority,
                    "original_stars": stars
                }
        except Exception as e:
            continue

    return None

def record_priority_feedback(ticket_id: str, feedback_type: str, reason: str,
                            confidence: Optional[float] = None) -> Dict:
    """Record priority correction feedback."""
    # Map feedback types to corrections
    priority_map = {
        "correct": None,  # No correction needed
        "too-high": "MEDIUM",  # Default downgrade (might be LOW)
        "too-low": "HIGH"  # Default upgrade (might be MEDIUM)
    }

    # Get article metadata
    metadata = get_article_metadata(ticket_id)

    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "ticket_id": ticket_id,
        "feedback_type": f"priority_{feedback_type.replace('-', '_')}",
        "reason": reason,
        "strategic_context_version": get_strategic_context_version(),
        "user": os.environ.get("USER", "unknown")
    }

    if metadata:
        entry["article_url"] = metadata["url"]
        entry["original_priority"] = metadata["original_priority"]
        entry["original_stars"] = metadata["original_stars"]

        # Set corrected priority if it's a correction
        if feedback_type != "correct":
            entry["corrected_priority"] = priority_map[feedback_type]

    if confidence is not None:
        entry["confidence"] = confidence

    return entry

def record_quality_feedback(ticket_id: str, audio_rating: Optional[int] = None,
                           content_rating: Optional[int] = None,
                           listened: bool = False,
                           completion: Optional[float] = None) -> Dict:
    """Record audio quality and content value feedback."""
    metadata = get_article_metadata(ticket_id)

    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "ticket_id": ticket_id,
        "feedback_type": "quality_rating",
        "user": os.environ.get("USER", "unknown"),
        "metadata": {}
    }

    if metadata:
        entry["article_url"] = metadata["url"]

    if listened:
        entry["metadata"]["audio_listened"] = True

    if completion is not None:
        entry["metadata"]["listening_completion"] = completion

    if audio_rating is not None:
        entry["metadata"]["audio_quality_rating"] = audio_rating

    if content_rating is not None:
        entry["metadata"]["content_value_rating"] = content_rating

    return entry

def record_action_feedback(ticket_id: str, completed_items: List[str]) -> Dict:
    """Record action item completion feedback."""
    metadata = get_article_metadata(ticket_id)

    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "ticket_id": ticket_id,
        "feedback_type": "action_outcome",
        "user": os.environ.get("USER", "unknown"),
        "metadata": {
            "action_items_completed": completed_items
        }
    }

    if metadata:
        entry["article_url"] = metadata["url"]

    return entry

def append_feedback(entry: Dict) -> None:
    """Append feedback entry to JSONL log."""
    # Ensure feedback directory exists
    os.makedirs(os.path.dirname(FEEDBACK_LOG), exist_ok=True)

    # Skip schema documentation lines (first line)
    with open(FEEDBACK_LOG, 'a', encoding='utf-8') as f:
        json.dump(entry, f, ensure_ascii=False)
        f.write('\n')

def add_jira_label(ticket_id: str, label: str) -> None:
    """Add JIRA label to ticket for visibility."""
    try:
        import subprocess

        # Read JIRA API token
        token_file = os.path.expanduser("~/.jira.d/.pass")
        if os.path.exists(token_file):
            with open(token_file, 'r') as f:
                token = f.read().strip()

            env = os.environ.copy()
            env["JIRA_API_TOKEN"] = token

            subprocess.run(
                ["jira", "issue", "label", "add", "-p", "GAT", ticket_id, label],
                env=env,
                capture_output=True,
                timeout=10
            )
    except Exception:
        # Silently fail - JIRA labeling is optional
        pass

def main():
    parser = argparse.ArgumentParser(
        description="Record feedback for article assessments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument("ticket_id", help="JIRA ticket ID (e.g., GAT-482)")
    parser.add_argument("feedback_type",
                       choices=["correct", "too-high", "too-low", "quality", "action"],
                       help="Type of feedback to record")

    # Priority feedback arguments
    parser.add_argument("reason", nargs="?",
                       help="Reason for correction (required for priority feedback)")
    parser.add_argument("--confidence", type=float,
                       help="Confidence in correction (0.0-1.0)")

    # Quality feedback arguments
    parser.add_argument("--audio-rating", type=int, choices=range(1, 6),
                       help="Audio quality rating (1-5)")
    parser.add_argument("--content-rating", type=int, choices=range(1, 6),
                       help="Content value rating (1-5)")
    parser.add_argument("--listened", action="store_true",
                       help="Audio episode was listened to")
    parser.add_argument("--completion", type=float,
                       help="Listening completion percentage (0.0-1.0)")

    # Action feedback arguments
    parser.add_argument("--completed", action="append",
                       help="Action item that was completed (can specify multiple)")

    args = parser.parse_args()

    # Validate arguments
    if args.feedback_type in ["correct", "too-high", "too-low"]:
        if not args.reason:
            parser.error(f"{args.feedback_type} feedback requires a reason")

        entry = record_priority_feedback(
            args.ticket_id, args.feedback_type, args.reason, args.confidence
        )

        # Add JIRA label
        add_jira_label(args.ticket_id, f"priority:{args.feedback_type}")

    elif args.feedback_type == "quality":
        if not any([args.audio_rating, args.content_rating, args.listened]):
            parser.error("quality feedback requires at least one quality metric")

        entry = record_quality_feedback(
            args.ticket_id, args.audio_rating, args.content_rating,
            args.listened, args.completion
        )

    elif args.feedback_type == "action":
        if not args.completed:
            parser.error("action feedback requires at least one --completed item")

        entry = record_action_feedback(args.ticket_id, args.completed)

    # Append to log
    append_feedback(entry)

    # Print confirmation
    print(f"✓ Feedback recorded for {args.ticket_id}")
    print(f"  Type: {entry['feedback_type']}")
    if "reason" in entry:
        print(f"  Reason: {entry['reason']}")
    if "metadata" in entry:
        for key, value in entry["metadata"].items():
            print(f"  {key}: {value}")

    print(f"\nFeedback log: {FEEDBACK_LOG}")

if __name__ == "__main__":
    main()
