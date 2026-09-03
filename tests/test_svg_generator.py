"""
test_svg_generator.py — Unit tests for svg_generator module.
"""

import sys
from pathlib import Path

# Add scripts to path
scripts_dir = Path(__file__).resolve().parent.parent / "scripts"
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

from svg_generator import (
    generate_stats_card_svg,
    generate_activity_card_svg,
    generate_languages_card_svg,
)


def test_generate_stats_card_svg():
    stats = {"total_repos": 5, "total_stars": 12, "total_forks": 3, "followers": 2, "account_age_days": 100}
    svg = generate_stats_card_svg(stats)
    assert "<svg" in svg
    assert "Public Repositories:" in svg
    assert "5" in svg


def test_generate_activity_card_svg():
    activity = {"total_events": 10, "event_types": {"PullRequestEvent": 4, "PushEvent": 6}}
    svg = generate_activity_card_svg(activity)
    assert "<svg" in svg
    assert "Pull Requests:" in svg
    assert "4" in svg


def test_generate_languages_card_svg():
    langs = [{"language": "Python", "count": 3, "percentage": 75.0}]
    svg = generate_languages_card_svg(langs)
    assert "<svg" in svg
    assert "Python" in svg
    assert "75.0%" in svg
