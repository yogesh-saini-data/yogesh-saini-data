"""
test_metrics.py — Unit tests for metrics calculation module.
"""

import sys
from pathlib import Path

# Add scripts to path
scripts_dir = Path(__file__).resolve().parent.parent / "scripts"
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

from metrics import (
    calculate_statistics,
    calculate_language_stats,
    rank_repositories,
    summarize_activity,
)


def test_calculate_statistics():
    profile = {"followers": 10, "following": 2, "created_at": "2020-01-01T00:00:00Z"}
    repos = [
        {
            "name": "r1",
            "stars": 10,
            "forks": 2,
            "is_archived": False,
            "is_fork": False,
            "updated_at": "2024-01-01T00:00:00Z",
            "url": "http://r1",
        },
        {
            "name": "r2",
            "stars": 5,
            "forks": 1,
            "is_archived": True,
            "is_fork": False,
            "updated_at": "2025-01-01T00:00:00Z",
            "url": "http://r2",
        },
    ]

    stats = calculate_statistics(profile, repos)

    assert stats["total_repos"] == 2
    assert stats["total_stars"] == 15
    assert stats["total_forks"] == 3
    assert stats["active_repos"] == 1
    assert stats["archived_repos"] == 1
    assert stats["most_starred_repo"]["name"] == "r1"


def test_calculate_language_stats():
    repos = [
        {"language": "Python"},
        {"language": "Python"},
        {"language": "JavaScript"},
        {"language": "Not specified"},
    ]

    langs = calculate_language_stats(repos)

    assert len(langs) == 2
    assert langs[0]["language"] == "Python"
    assert langs[0]["count"] == 2
    assert langs[0]["percentage"] == 66.7
    assert langs[1]["language"] == "JavaScript"
    assert langs[1]["count"] == 1


def test_rank_repositories():
    repos = [
        {
            "name": "low_star",
            "stars": 1,
            "forks": 0,
            "is_fork": False,
            "is_archived": False,
            "updated_at": "2020-01-01T00:00:00Z",
            "size": 10,
        },
        {
            "name": "high_star",
            "stars": 10,
            "forks": 2,
            "is_fork": False,
            "is_archived": False,
            "updated_at": "2020-01-01T00:00:00Z",
            "size": 10,
        },
    ]

    ranked = rank_repositories(repos)
    assert ranked[0]["name"] == "high_star"
    assert ranked[0]["score"] > ranked[1]["score"]
