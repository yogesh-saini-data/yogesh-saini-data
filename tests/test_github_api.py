"""
test_github_api.py — Unit tests for github_api.py module.
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Add scripts to path
scripts_dir = Path(__file__).resolve().parent.parent / "scripts"
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

from github_api import fetch_profile, fetch_repositories, fetch_recent_activity


@patch("github_api.requests.get")
def test_fetch_profile_success(mock_get):
    """Test parsing a valid profile response."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "login": "testuser",
        "name": "Test User",
        "bio": "Developer",
        "avatar_url": "https://avatar.url",
        "followers": 10,
        "following": 5,
        "public_repos": 3,
        "html_url": "https://github.com/testuser",
        "created_at": "2021-01-01T00:00:00Z",
    }
    mock_get.return_value = mock_response

    profile = fetch_profile("testuser")

    assert profile["username"] == "testuser"
    assert profile["name"] == "Test User"
    assert profile["public_repos"] == 3
    assert profile["followers"] == 10


@patch("github_api.requests.get")
def test_fetch_repositories_pagination(mock_get):
    """Test pagination handling for fetching repositories."""
    page1_response = MagicMock()
    page1_response.status_code = 200
    # Simulate page 1 returning 100 items (or 1 item in this simplified mock test)
    page1_response.json.return_value = [
        {
            "name": "repo1",
            "description": "Repo 1",
            "html_url": "https://github.com/test/repo1",
            "stargazers_count": 5,
            "forks_count": 1,
            "language": "Python",
            "created_at": "2022-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            "size": 500,
            "fork": False,
            "archived": False,
        }
    ]

    page2_response = MagicMock()
    page2_response.status_code = 200
    page2_response.json.return_value = []  # Empty page signals end

    mock_get.side_effect = [page1_response, page2_response]

    repos = fetch_repositories("testuser")
    assert len(repos) == 1
    assert repos[0]["name"] == "repo1"
    assert repos[0]["stars"] == 5
