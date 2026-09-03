"""
metrics.py — Statistics and ranking calculations for the Profile README.

This module contains PURE FUNCTIONS: they take data in, return results out.
No API calls, no file I/O, no side effects. This makes them:
    - Easy to test (just pass in test data)
    - Easy to understand (input → output)
    - Easy to modify (change the formula without touching API code)

All functions expect the data format returned by github_api.py.
"""

from datetime import datetime, timezone


def calculate_statistics(profile: dict, repositories: list[dict]) -> dict:
    """
    Calculate aggregate statistics across all repositories.
    
    Args:
        profile: Profile data from github_api.fetch_profile().
        repositories: List of repo dicts from github_api.fetch_repositories().
    
    Returns:
        {
            "total_repos": 27,
            "total_stars": 150,
            "total_forks": 42,
            "active_repos": 25,       # not archived
            "archived_repos": 2,
            "forked_repos": 3,
            "original_repos": 24,      # not forked
            "followers": 100,
            "following": 50,
            "most_starred_repo": {"name": "...", "stars": 50, "url": "..."},
            "most_recent_repo": {"name": "...", "updated_at": "...", "url": "..."},
            "account_age_days": 365,
        }
    """
    total_stars = sum(r["stars"] for r in repositories)
    total_forks = sum(r["forks"] for r in repositories)
    active_repos = [r for r in repositories if not r["is_archived"]]
    archived_repos = [r for r in repositories if r["is_archived"]]
    forked_repos = [r for r in repositories if r["is_fork"]]
    original_repos = [r for r in repositories if not r["is_fork"]]

    # Find most starred repository
    most_starred = None
    if repositories:
        top = max(repositories, key=lambda r: r["stars"])
        most_starred = {
            "name": top["name"],
            "stars": top["stars"],
            "url": top["url"],
        }

    # Find most recently updated repository
    most_recent = None
    if repositories:
        latest = max(repositories, key=lambda r: r["updated_at"])
        most_recent = {
            "name": latest["name"],
            "updated_at": latest["updated_at"],
            "url": latest["url"],
        }

    # Calculate account age
    account_age_days = 0
    if profile.get("created_at"):
        try:
            created = datetime.fromisoformat(
                profile["created_at"].replace("Z", "+00:00")
            )
            now = datetime.now(timezone.utc)
            account_age_days = (now - created).days
        except (ValueError, TypeError):
            account_age_days = 0

    return {
        "total_repos": len(repositories),
        "total_stars": total_stars,
        "total_forks": total_forks,
        "active_repos": len(active_repos),
        "archived_repos": len(archived_repos),
        "forked_repos": len(forked_repos),
        "original_repos": len(original_repos),
        "followers": profile.get("followers", 0),
        "following": profile.get("following", 0),
        "most_starred_repo": most_starred,
        "most_recent_repo": most_recent,
        "account_age_days": account_age_days,
    }


def calculate_language_stats(repositories: list[dict]) -> list[dict]:
    """
    Calculate programming language usage across repositories.
    
    Counts how many repositories use each language. We use repo count
    (not bytes of code) because:
        - The GitHub REST API doesn't return per-language byte counts
          in the /repos endpoint (you'd need a separate API call per repo)
        - Repo count is simpler and still gives a useful signal
        - We don't want to make N extra API calls for N repos
    
    Args:
        repositories: List of repo dicts from github_api.fetch_repositories().
    
    Returns:
        A sorted list (most-used first) of:
        [
            {"language": "Python", "count": 12, "percentage": 44.4},
            {"language": "JavaScript", "count": 8, "percentage": 29.6},
            ...
        ]
    
    Note: Repos with language "Not specified" are excluded from the
    percentage calculation since they don't tell us anything about
    language usage.
    """
    language_counts: dict[str, int] = {}

    for repo in repositories:
        lang = repo.get("language", "Not specified")
        if lang and lang != "Not specified":
            language_counts[lang] = language_counts.get(lang, 0) + 1

    total = sum(language_counts.values())
    if total == 0:
        return []

    # Sort by count (descending), then alphabetically for ties
    sorted_langs = sorted(
        language_counts.items(),
        key=lambda x: (-x[1], x[0]),
    )

    return [
        {
            "language": lang,
            "count": count,
            "percentage": round((count / total) * 100, 1),
        }
        for lang, count in sorted_langs
    ]


def rank_repositories(
    repositories: list[dict],
    include_forks: bool = False,
    include_archived: bool = False,
) -> list[dict]:
    """
    Rank repositories by a scoring algorithm to select "featured" projects.
    
    Scoring formula:
        score = (stars * 5) + (forks * 3) + recency_bonus + size_bonus
    
    Where:
        - stars * 5: Stars are the strongest quality signal
        - forks * 3: Forks indicate other developers found it useful
        - recency_bonus: Up to 10 points for repos updated within 90 days,
          linearly decaying to 0 for older repos. This ensures active
          projects rank higher than abandoned ones with a few stars.
        - size_bonus: Up to 5 points for repos with meaningful code
          (>100KB), so empty/tiny repos don't rank high.
    
    Args:
        repositories: List of repo dicts.
        include_forks: Whether to include forked repos in ranking.
        include_archived: Whether to include archived repos in ranking.
    
    Returns:
        Repositories sorted by score (highest first), each with an added
        "score" key.
    
    Why not just sort by stars?
        A repo with 10 stars from 3 years ago that hasn't been touched
        is less interesting for a profile than a repo with 2 stars that
        was updated yesterday. The scoring formula balances popularity
        with activity.
    """
    candidates = []

    for repo in repositories:
        # Filter based on configuration
        if not include_forks and repo["is_fork"]:
            continue
        if not include_archived and repo["is_archived"]:
            continue

        score = _calculate_repo_score(repo)
        ranked_repo = repo.copy()
        ranked_repo["score"] = score
        candidates.append(ranked_repo)

    # Sort by score descending
    candidates.sort(key=lambda r: r["score"], reverse=True)
    return candidates


def _calculate_repo_score(repo: dict) -> float:
    """
    Calculate a single repository's ranking score.
    
    This is a private helper for rank_repositories(). We extract it
    as a separate function to make the scoring formula easy to find,
    read, and modify.
    
    Args:
        repo: A single repository dictionary.
    
    Returns:
        A numeric score (higher = more prominent).
    """
    # Base score from popularity metrics
    star_score = repo.get("stars", 0) * 5
    fork_score = repo.get("forks", 0) * 3

    # Recency bonus: up to 10 points for recently updated repos
    recency_bonus = 0
    updated_at = repo.get("updated_at", "")
    if updated_at:
        try:
            updated = datetime.fromisoformat(
                updated_at.replace("Z", "+00:00")
            )
            now = datetime.now(timezone.utc)
            days_since_update = (now - updated).days
            # Linear decay: 10 points at 0 days, 0 points at 90+ days
            if days_since_update < 90:
                recency_bonus = 10 * (1 - days_since_update / 90)
        except (ValueError, TypeError):
            recency_bonus = 0

    # Size bonus: up to 5 points for repos with meaningful code
    size_bonus = 0
    size_kb = repo.get("size", 0)
    if size_kb > 100:       # More than 100 KB
        size_bonus = min(5, size_kb / 1000)  # Cap at 5 points

    return star_score + fork_score + recency_bonus + size_bonus


def summarize_activity(activity: list[dict]) -> dict:
    """
    Summarize recent activity events into a readable format.
    
    GitHub event types we care about:
        - PushEvent: Code was pushed
        - CreateEvent: Branch/tag/repo created
        - PullRequestEvent: PR opened/closed/merged
        - IssuesEvent: Issue opened/closed
        - WatchEvent: Starred a repo
        - ForkEvent: Forked a repo
    
    Args:
        activity: List of event dicts from github_api.fetch_recent_activity().
    
    Returns:
        {
            "total_events": 15,
            "event_types": {"PushEvent": 8, "PullRequestEvent": 4, ...},
            "active_repos": ["user/repo1", "user/repo2"],
            "recent_events": [
                {"type": "PushEvent", "repo": "user/repo", "created_at": "..."},
                ...
            ]
        }
    
    Limitations:
        - This only covers the last 90 days of public events
        - It does NOT represent total contributions
        - Private repository activity is not included
    """
    if not activity:
        return {
            "total_events": 0,
            "event_types": {},
            "active_repos": [],
            "recent_events": [],
        }

    # Count event types
    event_types: dict[str, int] = {}
    active_repos: set[str] = set()

    for event in activity:
        event_type = event.get("type", "Unknown")
        event_types[event_type] = event_types.get(event_type, 0) + 1
        repo_name = event.get("repo", "Unknown")
        if repo_name != "Unknown":
            active_repos.add(repo_name)

    return {
        "total_events": len(activity),
        "event_types": dict(
            sorted(event_types.items(), key=lambda x: -x[1])
        ),
        "active_repos": sorted(active_repos),
        "recent_events": activity[:5],  # Top 5 most recent
    }
