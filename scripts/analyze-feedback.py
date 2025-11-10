#!/usr/bin/env python3.11
"""
Analyze feedback log to generate insights and improvement recommendations.

Usage:
    # Generate weekly summary
    python3 analyze-feedback.py --period week

    # Generate monthly summary
    python3 analyze-feedback.py --period month

    # Generate full history report
    python3 analyze-feedback.py --period all

    # Save report to file
    python3 analyze-feedback.py --period week --output feedback/reports/2025-10-30-weekly-summary.md

Examples:
    python3 analyze-feedback.py --period week
    python3 analyze-feedback.py --period month --output feedback/reports/monthly-$(date +%Y-%m).md
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict, Counter

# Constants
FEEDBACK_LOG = "/Users/bgerby/Documents/dev/ai/feedback/article-feedback-log.jsonl"

def load_feedback(since_date: datetime = None) -> List[Dict]:
    """Load feedback entries from JSONL log, optionally filtered by date."""
    entries = []

    if not os.path.exists(FEEDBACK_LOG):
        return entries

    with open(FEEDBACK_LOG, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('{"_comment"') or line.startswith('{"_schema"'):
                continue  # Skip schema documentation

            try:
                entry = json.loads(line)

                # Filter by date if specified
                if since_date:
                    entry_date = datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))
                    if entry_date < since_date:
                        continue

                entries.append(entry)
            except json.JSONDecodeError:
                continue

    return entries

def calculate_accuracy_metrics(entries: List[Dict]) -> Dict:
    """Calculate priority prediction accuracy metrics."""
    total_priority_feedback = 0
    correct_predictions = 0
    too_high_predictions = 0
    too_low_predictions = 0

    priority_distribution = Counter()

    for entry in entries:
        if entry.get("feedback_type", "").startswith("priority_"):
            total_priority_feedback += 1

            original = entry.get("original_priority", "UNKNOWN")
            priority_distribution[original] += 1

            feedback_type = entry["feedback_type"]

            if feedback_type == "priority_correct":
                correct_predictions += 1
            elif feedback_type == "priority_too_high":
                too_high_predictions += 1
            elif feedback_type == "priority_too_low":
                too_low_predictions += 1

    accuracy = (correct_predictions / total_priority_feedback * 100) if total_priority_feedback > 0 else 0

    return {
        "total": total_priority_feedback,
        "correct": correct_predictions,
        "too_high": too_high_predictions,
        "too_low": too_low_predictions,
        "accuracy_percent": accuracy,
        "original_distribution": dict(priority_distribution)
    }

def analyze_quality_metrics(entries: List[Dict]) -> Dict:
    """Analyze audio quality and content value metrics."""
    quality_ratings = []
    content_ratings = []
    listening_completions = []
    listened_count = 0

    for entry in entries:
        if entry.get("feedback_type") == "quality_rating":
            metadata = entry.get("metadata", {})

            if metadata.get("audio_listened"):
                listened_count += 1

            if "audio_quality_rating" in metadata:
                quality_ratings.append(metadata["audio_quality_rating"])

            if "content_value_rating" in metadata:
                content_ratings.append(metadata["content_value_rating"])

            if "listening_completion" in metadata:
                listening_completions.append(metadata["listening_completion"])

    avg_quality = sum(quality_ratings) / len(quality_ratings) if quality_ratings else 0
    avg_content = sum(content_ratings) / len(content_ratings) if content_ratings else 0
    avg_completion = sum(listening_completions) / len(listening_completions) if listening_completions else 0

    return {
        "total_quality_feedback": len(set(quality_ratings + content_ratings + listening_completions)),
        "episodes_listened": listened_count,
        "avg_audio_quality": avg_quality,
        "avg_content_value": avg_content,
        "avg_listening_completion": avg_completion
    }

def analyze_action_outcomes(entries: List[Dict]) -> Dict:
    """Analyze action item completion metrics."""
    tickets_with_actions = set()
    total_actions_completed = 0
    action_items = []

    for entry in entries:
        if entry.get("feedback_type") == "action_outcome":
            tickets_with_actions.add(entry["ticket_id"])
            completed = entry.get("metadata", {}).get("action_items_completed", [])
            total_actions_completed += len(completed)
            action_items.extend(completed)

    return {
        "tickets_with_completed_actions": len(tickets_with_actions),
        "total_actions_completed": total_actions_completed,
        "sample_actions": action_items[:10]  # Show first 10
    }

def identify_patterns(entries: List[Dict]) -> List[str]:
    """Identify systematic misclassification patterns."""
    patterns = []

    # Group corrections by reason keywords
    too_high_reasons = []
    too_low_reasons = []

    for entry in entries:
        feedback_type = entry.get("feedback_type", "")
        reason = entry.get("reason", "").lower()

        if feedback_type == "priority_too_high":
            too_high_reasons.append(reason)
        elif feedback_type == "priority_too_low":
            too_low_reasons.append(reason)

    # Detect common themes
    if len(too_high_reasons) >= 3:
        # Look for common words
        common_words = set()
        for reason in too_high_reasons:
            words = set(reason.split())
            if not common_words:
                common_words = words
            else:
                common_words &= words

        if common_words:
            patterns.append(f"Over-rating pattern: Articles with '{', '.join(list(common_words)[:3])}' consistently rated too HIGH")

    if len(too_low_reasons) >= 3:
        patterns.append(f"Under-rating pattern: {len(too_low_reasons)} articles rated too LOW - may need criteria adjustment")

    return patterns

def generate_recommendations(accuracy_metrics: Dict, quality_metrics: Dict,
                            action_metrics: Dict, patterns: List[str]) -> List[str]:
    """Generate actionable recommendations based on analysis."""
    recommendations = []

    # Accuracy recommendations
    if accuracy_metrics["accuracy_percent"] < 85:
        recommendations.append(
            f"⚠️ Priority accuracy at {accuracy_metrics['accuracy_percent']:.1f}% (target: 90%+). "
            f"Consider reviewing strategic context criteria."
        )

    if accuracy_metrics["too_high"] > accuracy_metrics["too_low"] * 2:
        recommendations.append(
            "📊 System is over-rating articles (too optimistic). "
            "Consider adding more LOW priority examples to strategic context."
        )
    elif accuracy_metrics["too_low"] > accuracy_metrics["too_high"] * 2:
        recommendations.append(
            "📊 System is under-rating articles (too conservative). "
            "Review HIGH priority criteria - may be too restrictive."
        )

    # Quality recommendations
    if quality_metrics["avg_audio_quality"] > 0 and quality_metrics["avg_audio_quality"] < 4:
        recommendations.append(
            f"🎧 Audio quality averaging {quality_metrics['avg_audio_quality']:.1f}/5. "
            "Review TTS settings and content cropping."
        )

    if quality_metrics["avg_listening_completion"] > 0 and quality_metrics["avg_listening_completion"] < 0.7:
        recommendations.append(
            f"⏭️ Listening completion at {quality_metrics['avg_listening_completion']*100:.0f}%. "
            "Content may be too long or not engaging enough."
        )

    # Action recommendations
    if action_metrics["total_actions_completed"] < 5:
        recommendations.append(
            "📋 Low action item completion tracking. Consider setting up weekly review process."
        )

    # Pattern recommendations
    for pattern in patterns:
        recommendations.append(f"🔍 Pattern detected: {pattern}")

    if not recommendations:
        recommendations.append("✅ System performing well. Continue current validation process.")

    return recommendations

def generate_report(entries: List[Dict], period: str) -> str:
    """Generate markdown report from feedback entries."""
    if not entries:
        return f"# Feedback Analysis Report ({period})\n\n**No feedback data available for this period.**"

    # Calculate metrics
    accuracy_metrics = calculate_accuracy_metrics(entries)
    quality_metrics = analyze_quality_metrics(entries)
    action_metrics = analyze_action_outcomes(entries)
    patterns = identify_patterns(entries)
    recommendations = generate_recommendations(accuracy_metrics, quality_metrics, action_metrics, patterns)

    # Generate report
    report = f"""# Article Assessment Feedback Analysis

**Period:** {period.title()}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Total Feedback Entries:** {len(entries)}

---

## Priority Accuracy Metrics

| Metric | Value |
|--------|-------|
| **Total Priority Validations** | {accuracy_metrics['total']} |
| **Correct Predictions** | {accuracy_metrics['correct']} ({accuracy_metrics['accuracy_percent']:.1f}%) |
| **Over-rated (Too High)** | {accuracy_metrics['too_high']} |
| **Under-rated (Too Low)** | {accuracy_metrics['too_low']} |

### Original Priority Distribution
"""

    for priority, count in sorted(accuracy_metrics['original_distribution'].items()):
        percentage = (count / accuracy_metrics['total'] * 100) if accuracy_metrics['total'] > 0 else 0
        report += f"- **{priority}**: {count} articles ({percentage:.1f}%)\n"

    report += f"""
**Accuracy Status:** {"✅ Good" if accuracy_metrics['accuracy_percent'] >= 90 else "⚠️ Needs Improvement" if accuracy_metrics['accuracy_percent'] >= 80 else "❌ Poor"}

---

## Audio Quality & Content Value

| Metric | Value |
|--------|-------|
| **Total Quality Feedback** | {quality_metrics['total_quality_feedback']} |
| **Episodes Listened** | {quality_metrics['episodes_listened']} |
| **Avg Audio Quality** | {quality_metrics['avg_audio_quality']:.1f}/5.0 |
| **Avg Content Value** | {quality_metrics['avg_content_value']:.1f}/5.0 |
| **Avg Listening Completion** | {quality_metrics['avg_listening_completion']*100:.0f}% |

---

## Action Item Outcomes

| Metric | Value |
|--------|-------|
| **Tickets with Completed Actions** | {action_metrics['tickets_with_completed_actions']} |
| **Total Actions Completed** | {action_metrics['total_actions_completed']} |

"""

    if action_metrics['sample_actions']:
        report += "**Sample Completed Actions:**\n"
        for action in action_metrics['sample_actions'][:5]:
            report += f"- {action}\n"
        report += "\n"

    report += "---\n\n## Identified Patterns\n\n"

    if patterns:
        for pattern in patterns:
            report += f"- {pattern}\n"
    else:
        report += "*No systematic patterns detected yet. Continue collecting feedback.*\n"

    report += "\n---\n\n## Recommendations\n\n"

    for rec in recommendations:
        report += f"- {rec}\n"

    report += f"""
---

## Next Steps

1. **Review misclassifications** - Examine tickets marked as too-high/too-low
2. **Update strategic context** - Incorporate learnings into STRATEGIC_CONTEXT.md
3. **Monitor trends** - Compare with next period to track improvement
4. **Implement recommendations** - Prioritize high-impact changes

**Feedback Log:** `{FEEDBACK_LOG}`
"""

    return report

def main():
    parser = argparse.ArgumentParser(
        description="Analyze feedback log and generate insights",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument("--period",
                       choices=["day", "week", "month", "all"],
                       default="week",
                       help="Time period to analyze (default: week)")

    parser.add_argument("--output",
                       help="Output file path (default: print to stdout)")

    args = parser.parse_args()

    # Calculate date range
    now = datetime.now()
    since_date = None

    if args.period == "day":
        since_date = now - timedelta(days=1)
    elif args.period == "week":
        since_date = now - timedelta(weeks=1)
    elif args.period == "month":
        since_date = now - timedelta(days=30)
    # "all" means since_date = None (no filter)

    # Load feedback
    entries = load_feedback(since_date)

    # Generate report
    report = generate_report(entries, args.period)

    # Output
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"✓ Report generated: {output_path}")
        print(f"  Period: {args.period}")
        print(f"  Entries analyzed: {len(entries)}")
    else:
        print(report)

if __name__ == "__main__":
    main()
