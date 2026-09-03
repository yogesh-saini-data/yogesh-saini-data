"""
test_generate_readme.py — Integration test for end-to-end README generation.
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add scripts to path
scripts_dir = Path(__file__).resolve().parent.parent / "scripts"
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

from generate_readme import main


@patch("sys.argv", ["generate_readme.py", "--dry-run"])
@patch("github_api.fetch_all_data")
def test_generate_readme_dry_run(mock_fetch):
    mock_fetch.return_value = {
        "profile": {
            "username": "yogesh-saini-data",
            "name": "Yogesh Saini",
            "followers": 0,
            "following": 0,
            "public_repos": 1,
            "created_at": "2026-01-01T00:00:00Z",
        },
        "repositories": [
            {
                "name": "sample-repo",
                "description": "Sample",
                "url": "https://github.com/test/sample-repo",
                "stars": 2,
                "forks": 0,
                "language": "Python",
                "updated_at": "2026-01-01T00:00:00Z",
                "size": 50,
                "is_fork": False,
                "is_archived": False,
            }
        ],
        "activity": [],
    }

    # Should run without throwing exception
    main()
