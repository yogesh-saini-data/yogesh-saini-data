"""
generate_readme.py — Main orchestrator for the GitHub Profile README generator.

This script coordinates the full pipeline:
    1. Parse command-line arguments (--dry-run, --config, --verbose)
    2. Load configuration
    3. Fetch data from GitHub API (or mock data for testing)
    4. Calculate metrics and rank repositories
    5. Render README from template
    6. Validate generated README
    7. Save to README.md (unless --dry-run is set)

Usage:
    python scripts/generate_readme.py
    python scripts/generate_readme.py --dry-run
    python scripts/generate_readme.py --verbose
"""

import argparse
import sys
from pathlib import Path

# Ensure scripts directory is on Python path
scripts_dir = Path(__file__).resolve().parent
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

from utils import setup_logging, load_config, get_project_root
from github_api import fetch_all_data
from metrics import (
    calculate_statistics,
    calculate_language_stats,
    rank_repositories,
    summarize_activity,
)
from renderer import render_readme, validate_readme


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate GitHub Profile README automatically."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate README and show summary without overwriting README.md",
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to custom configuration JSON file",
    )
    parser.add_argument(
        "--template",
        type=str,
        default=None,
        help="Path to custom README template file",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Path to output README file (default: README.md in project root)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable detailed debug logging",
    )
    return parser.parse_args()


def main():
    """Main execution function."""
    # Ensure stdout handles UTF-8 (emojis in README) on Windows platforms
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    args = parse_args()
    logger = setup_logging(verbose=args.verbose)

    logger.info("==========================================")
    logger.info("Starting GitHub Profile README Generator")
    logger.info("==========================================")

    root = get_project_root()
    template_path = Path(args.template) if args.template else root / "README.template.md"
    output_path = Path(args.output) if args.output else root / "README.md"

    if args.dry_run:
        logger.info("[DRY RUN MODE] No files will be modified.")

    try:
        # Step 1: Load config
        logger.info("Loading configuration...")
        config = load_config(args.config)
        username = config["username"]
        logger.info(f"Target GitHub username: {username}")

        # Step 2: Fetch data from GitHub API
        data = fetch_all_data(username)

        # Step 3: Calculate metrics
        logger.info("Calculating metrics and statistics...")
        stats = calculate_statistics(data["profile"], data["repositories"])
        language_stats = calculate_language_stats(data["repositories"])
        ranked_repos = rank_repositories(
            data["repositories"],
            include_forks=config.get("include_forks", False),
            include_archived=config.get("include_archived", False),
        )
        activity_summary = summarize_activity(data["activity"])

        # Step 4: Render README
        readme_content = render_readme(
            template_path=template_path,
            stats=stats,
            language_stats=language_stats,
            ranked_repos=ranked_repos,
            activity_summary=activity_summary,
            config=config,
        )

        # Step 5: Validate README
        logger.info("Validating generated README...")
        validation_errors = validate_readme(readme_content)
        if validation_errors:
            logger.error("Validation failed:")
            for err in validation_errors:
                logger.error(f"  - {err}")
            sys.exit(1)

        logger.info("README validation passed successfully.")

        # Step 6: Output / Save
        if args.dry_run:
            logger.info("[DRY RUN] Generated README Preview:")
            logger.info("------------------------------------------")
            print(readme_content)
            logger.info("------------------------------------------")
            logger.info("[DRY RUN] Finished without writing file.")
        else:
            logger.info(f"Saving generated README to {output_path}...")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(readme_content)
            logger.info("README.md updated successfully!")

    except Exception as e:
        logger.exception(f"Fatal error generating README: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
