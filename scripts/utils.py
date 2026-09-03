"""
utils.py — Shared utilities for the GitHub Profile README generator.

Provides:
    - Configuration loading from JSON
    - Logging setup with consistent formatting
    - Date/time formatting helpers

Why a separate utils module?
    These are cross-cutting concerns used by multiple modules (API client,
    renderer, orchestrator). Keeping them here avoids circular imports and
    keeps other modules focused on their core responsibility.
"""

import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def get_project_root() -> Path:
    """
    Return the project root directory.
    
    The project root is the parent of the 'scripts/' directory where this
    file lives. This lets us find config files and templates regardless of
    where the script is invoked from.
    
    Example:
        If this file is at /repo/scripts/utils.py
        Then project root is /repo/
    """
    return Path(__file__).resolve().parent.parent


def load_config(config_path: str | None = None) -> dict:
    """
    Load the profile configuration from a JSON file.
    
    Args:
        config_path: Optional path to the config file. If not provided,
                     defaults to config/profile_config.json relative to
                     the project root.
    
    Returns:
        A dictionary containing the configuration values.
    
    Raises:
        FileNotFoundError: If the config file doesn't exist.
        json.JSONDecodeError: If the config file contains invalid JSON.
    
    Why JSON for config?
        JSON is simple, widely understood, and doesn't require additional
        dependencies. YAML would need PyYAML, TOML is built-in from
        Python 3.11+ but JSON is the most universally familiar format,
        especially for developers who work with APIs.
    """
    if config_path is None:
        config_path = get_project_root() / "config" / "profile_config.json"
    else:
        config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}\n"
            f"Create it by copying the example in config/profile_config.json"
        )

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    # Validate required fields
    if "username" not in config:
        raise ValueError(
            "Configuration must include 'username'. "
            "Set it to your GitHub username in config/profile_config.json"
        )

    if not config["username"] or config["username"] == "YOUR_GITHUB_USERNAME":
        raise ValueError(
            "Please set 'username' to your actual GitHub username "
            "in config/profile_config.json"
        )

    return config


def setup_logging(verbose: bool = False) -> logging.Logger:
    """
    Configure and return a logger with consistent formatting.
    
    Args:
        verbose: If True, set log level to DEBUG. Otherwise, INFO.
    
    Returns:
        A configured Logger instance.
    
    Why use the logging module instead of print()?
        - Log levels (DEBUG, INFO, WARNING, ERROR) let us filter output
        - Timestamps help debug CI/CD runs
        - In GitHub Actions, log output is captured and searchable
        - We can add file logging later without changing every call site
    """
    logger = logging.getLogger("profile_readme")

    # Avoid adding handlers multiple times if called repeatedly
    if logger.handlers:
        return logger

    level = logging.DEBUG if verbose else logging.INFO
    logger.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


def format_date(date_string: str) -> str:
    """
    Convert an ISO 8601 date string to a human-readable format.
    
    GitHub API returns dates like: "2024-01-15T10:30:00Z"
    We convert to: "January 15, 2024"
    
    Args:
        date_string: An ISO 8601 date string from the GitHub API.
    
    Returns:
        A formatted date string, or "Unknown" if parsing fails.
    """
    try:
        dt = datetime.fromisoformat(date_string.replace("Z", "+00:00"))
        return dt.strftime("%B %d, %Y")
    except (ValueError, AttributeError):
        return "Unknown"


def get_current_timestamp() -> str:
    """
    Return the current date/time formatted for the README "Last Updated" section.
    
    Uses UTC to ensure consistency regardless of where the script runs
    (your local machine vs GitHub Actions servers in different regions).
    
    Returns:
        A string like "September 03, 2026 (UTC)"
    """
    now = datetime.now(timezone.utc)
    return now.strftime("%B %d, %Y") + " (UTC)"


def get_github_token() -> str | None:
    """
    Retrieve the GitHub token from the environment.
    
    Returns:
        The token string, or None if not set.
    
    Why use an environment variable?
        - Tokens should NEVER be hard-coded in source files
        - Environment variables are the standard way to pass secrets
        - GitHub Actions automatically provides GITHUB_TOKEN
        - Locally, you can set it via: $env:GITHUB_TOKEN = "your_token"
    
    Do we always need a token?
        No! GitHub's REST API allows unauthenticated requests for public
        data. But unauthenticated requests are limited to 60/hour, while
        authenticated requests get 5,000/hour. For a profile with many
        repos, authentication avoids rate-limit failures.
    """
    return os.environ.get("GITHUB_TOKEN")
