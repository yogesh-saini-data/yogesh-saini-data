"""
github_api.py — GitHub REST API client for the Profile README generator.

This module handles ALL communication with GitHub's API. No other module
should make HTTP requests directly. This separation means:
    - If GitHub changes their API, we only fix this file
    - We can mock this module in tests without touching business logic
    - Rate limiting and error handling are centralized

GitHub REST API docs: https://docs.github.com/en/rest

Rate Limits:
    - Unauthenticated: 60 requests/hour (identified by IP)
    - Authenticated (GITHUB_TOKEN): 5,000 requests/hour
    
    For a typical profile with <100 repos, we need ~2-3 API calls total:
        1. GET /users/{username}           → profile info
        2. GET /users/{username}/repos     → repos (may need 1-2 pages)
        3. GET /users/{username}/events    → recent activity (optional)
    
    So even unauthenticated is fine for most users, but we support
    authentication to be safe.
"""

import requests
from utils import setup_logging, get_github_token

# GitHub API base URL — all endpoints are relative to this
BASE_URL = "https://api.github.com"

# Maximum repos per page (GitHub's limit is 100)
PER_PAGE = 100

logger = setup_logging()


def _get_headers() -> dict:
    """
    Build HTTP headers for GitHub API requests.
    
    Returns:
        A dictionary of headers including:
        - Accept: application/vnd.github.v3+json (request API v3 format)
        - User-Agent: required by GitHub (they reject requests without one)
        - Authorization: Bearer token if GITHUB_TOKEN is available
    
    Why 'application/vnd.github.v3+json'?
        This tells GitHub we want the stable v3 REST API response format.
        Without it, GitHub might return a different format in the future.
    """
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "GitHub-Profile-README-Generator",
    }

    token = get_github_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"
        logger.debug("Using authenticated GitHub API requests")
    else:
        logger.debug(
            "No GITHUB_TOKEN found — using unauthenticated requests "
            "(60 requests/hour limit)"
        )

    return headers


def _make_request(url: str, params: dict | None = None) -> dict | list:
    """
    Make an HTTP GET request to the GitHub API with error handling.
    
    Args:
        url: Full URL to request.
        params: Optional query parameters.
    
    Returns:
        Parsed JSON response (dict or list).
    
    Raises:
        requests.HTTPError: On 4xx/5xx responses, with helpful messages.
        requests.ConnectionError: On network failures.
        requests.Timeout: If the request takes too long.
    
    Why centralize this?
        Every API call needs the same error handling: rate limits,
        network errors, auth failures. Writing it once here means
        we can't forget to handle an error in a new API call.
    """
    try:
        response = requests.get(
            url,
            headers=_get_headers(),
            params=params,
            timeout=30,  # 30 seconds — generous but not infinite
        )

        # Check for rate limiting (HTTP 403 with specific header)
        if response.status_code == 403:
            remaining = response.headers.get("X-RateLimit-Remaining", "?")
            reset_time = response.headers.get("X-RateLimit-Reset", "?")
            raise requests.HTTPError(
                f"GitHub API rate limit exceeded. "
                f"Remaining: {remaining}. "
                f"Resets at Unix timestamp: {reset_time}. "
                f"Tip: Set GITHUB_TOKEN environment variable to get "
                f"5,000 requests/hour instead of 60.",
                response=response,
            )

        # Check for user not found (404)
        if response.status_code == 404:
            raise requests.HTTPError(
                f"GitHub user not found. Check the username in "
                f"config/profile_config.json. URL: {url}",
                response=response,
            )

        # Raise for any other HTTP error (4xx, 5xx)
        response.raise_for_status()

        return response.json()

    except requests.ConnectionError:
        raise requests.ConnectionError(
            "Could not connect to GitHub API. "
            "Check your internet connection."
        )
    except requests.Timeout:
        raise requests.Timeout(
            "GitHub API request timed out after 30 seconds. "
            "Try again later."
        )


def fetch_profile(username: str) -> dict:
    """
    Fetch a GitHub user's profile information.
    
    API endpoint: GET /users/{username}
    Docs: https://docs.github.com/en/rest/users/users#get-a-user
    
    Args:
        username: GitHub username to look up.
    
    Returns:
        A dictionary with cleaned-up profile data:
        {
            "username": "yogesh-saini-data",
            "name": "Yogesh Saini",        # or username if not set
            "bio": "...",                    # or empty string
            "avatar_url": "https://...",
            "followers": 10,
            "following": 5,
            "public_repos": 27,
            "profile_url": "https://github.com/yogesh-saini-data",
            "created_at": "2020-01-01T00:00:00Z",
            "location": "...",               # or empty string
            "company": "...",                # or empty string
            "blog": "...",                   # or empty string
        }
    
    Why do we clean/transform the API response?
        GitHub's API returns ~30+ fields, many of which we don't need
        (like gravatar_id, node_id, etc.). By extracting only what we
        use, our downstream code is simpler and we're not coupled to
        GitHub's full response schema.
    """
    logger.info(f"Fetching GitHub profile for '{username}'...")

    url = f"{BASE_URL}/users/{username}"
    data = _make_request(url)

    profile = {
        "username": data.get("login", username),
        "name": data.get("name") or data.get("login", username),
        "bio": data.get("bio") or "",
        "avatar_url": data.get("avatar_url", ""),
        "followers": data.get("followers", 0),
        "following": data.get("following", 0),
        "public_repos": data.get("public_repos", 0),
        "profile_url": data.get("html_url", f"https://github.com/{username}"),
        "created_at": data.get("created_at", ""),
        "location": data.get("location") or "",
        "company": data.get("company") or "",
        "blog": data.get("blog") or "",
    }

    logger.info(
        f"Profile loaded: {profile['name']} "
        f"({profile['public_repos']} public repos, "
        f"{profile['followers']} followers)"
    )

    return profile


def fetch_repositories(username: str) -> list[dict]:
    """
    Fetch ALL public repositories for a GitHub user.
    
    API endpoint: GET /users/{username}/repos
    Docs: https://docs.github.com/en/rest/repos/repos#list-repositories-for-a-user
    
    Handles pagination:
        GitHub returns a maximum of 100 repos per request. If a user has
        more than 100 repos, we need multiple requests (pages). We keep
        requesting the next page until we get fewer results than PER_PAGE,
        which means we've reached the last page.
    
    Args:
        username: GitHub username.
    
    Returns:
        A list of dictionaries, each containing cleaned repository data:
        [
            {
                "name": "my-project",
                "description": "A cool project",
                "url": "https://github.com/user/my-project",
                "stars": 42,
                "forks": 7,
                "language": "Python",
                "created_at": "2023-01-15T...",
                "updated_at": "2024-06-20T...",
                "size": 1024,
                "is_fork": false,
                "is_archived": false,
                "topics": ["python", "automation"],
            },
            ...
        ]
    """
    logger.info(f"Fetching repositories for '{username}'...")

    all_repos = []
    page = 1

    while True:
        url = f"{BASE_URL}/users/{username}/repos"
        params = {
            "per_page": PER_PAGE,
            "page": page,
            "sort": "updated",      # most recently updated first
            "direction": "desc",
        }

        repos_page = _make_request(url, params=params)

        if not repos_page:
            # Empty page means we've fetched everything
            break

        for repo in repos_page:
            cleaned = {
                "name": repo.get("name", ""),
                "description": repo.get("description") or "No description provided.",
                "url": repo.get("html_url", ""),
                "stars": repo.get("stargazers_count", 0),
                "forks": repo.get("forks_count", 0),
                "language": repo.get("language") or "Not specified",
                "created_at": repo.get("created_at", ""),
                "updated_at": repo.get("updated_at", ""),
                "size": repo.get("size", 0),
                "is_fork": repo.get("fork", False),
                "is_archived": repo.get("archived", False),
                "topics": repo.get("topics", []),
            }
            all_repos.append(cleaned)

        logger.debug(f"Page {page}: fetched {len(repos_page)} repositories")

        # If we got fewer than PER_PAGE, we've reached the last page
        if len(repos_page) < PER_PAGE:
            break

        page += 1

    logger.info(f"Found {len(all_repos)} repositories total")
    return all_repos


def fetch_recent_activity(username: str, max_events: int = 10) -> list[dict]:
    """
    Fetch recent public activity events for a GitHub user.
    
    API endpoint: GET /users/{username}/events/public
    Docs: https://docs.github.com/en/rest/activity/events#list-public-events-for-a-user
    
    Limitations (documented honestly):
        - GitHub only keeps events for the last 90 days
        - Only the last 300 events are available
        - Some event types may not be included
        - This does NOT represent total contributions — it's just recent
          public activity visible through the Events API
    
    Args:
        username: GitHub username.
        max_events: Maximum number of events to return.
    
    Returns:
        A list of simplified event dictionaries:
        [
            {
                "type": "PushEvent",
                "repo": "user/repo-name",
                "created_at": "2024-06-20T...",
            },
            ...
        ]
    """
    logger.info(f"Fetching recent activity for '{username}'...")

    url = f"{BASE_URL}/users/{username}/events/public"
    params = {"per_page": min(max_events, 100)}

    try:
        events = _make_request(url, params=params)
    except requests.HTTPError:
        # Activity endpoint can sometimes fail — it's optional data
        logger.warning(
            "Could not fetch recent activity. "
            "This is optional data — continuing without it."
        )
        return []

    activity = []
    for event in events[:max_events]:
        activity.append({
            "type": event.get("type", "Unknown"),
            "repo": event.get("repo", {}).get("name", "Unknown"),
            "created_at": event.get("created_at", ""),
        })

    logger.info(f"Fetched {len(activity)} recent activity events")
    return activity


def fetch_all_data(username: str) -> dict:
    """
    Fetch all GitHub data needed for the README in one call.
    
    This is the main function other modules should use. It bundles
    profile, repositories, and activity into a single dictionary.
    
    Args:
        username: GitHub username.
    
    Returns:
        {
            "profile": { ... },
            "repositories": [ ... ],
            "activity": [ ... ],
        }
    
    Why bundle everything?
        The orchestrator (generate_readme.py) just calls this one function
        and gets everything it needs. This keeps the orchestrator simple
        and means we can change how data is fetched (e.g., add caching)
        without changing the orchestrator.
    """
    profile = fetch_profile(username)
    repositories = fetch_repositories(username)
    activity = fetch_recent_activity(username)

    return {
        "profile": profile,
        "repositories": repositories,
        "activity": activity,
    }
