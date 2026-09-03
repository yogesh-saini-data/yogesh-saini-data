"""
renderer.py — Template rendering engine for the Profile README.

This module reads README.template.md and replaces dynamic placeholder
sections with generated markdown content. It does NOT make API calls
or perform calculations — it only formats and assembles content.

Template System:
    The template uses HTML comment markers to identify dynamic sections:
    
        <!-- SECTION_NAME_START -->
        (this content gets replaced)
        <!-- SECTION_NAME_END -->
    
    Everything OUTSIDE these markers is preserved exactly as-is.
    This means you can edit the static parts of your README (intro,
    about me, contact info) directly in the template without touching
    Python code.
    
    Why HTML comments?
        - They're invisible when GitHub renders the markdown
        - They don't interfere with the document structure
        - They're easy to find with regex
        - They're a common pattern in GitHub profile READMEs
"""

import re
from pathlib import Path

from utils import setup_logging, format_date, get_current_timestamp

logger = setup_logging()


def load_template(template_path: str | Path) -> str:
    """
    Load the README template file.
    
    Args:
        template_path: Path to README.template.md.
    
    Returns:
        The template content as a string.
    
    Raises:
        FileNotFoundError: If the template doesn't exist.
    """
    template_path = Path(template_path)

    if not template_path.exists():
        raise FileNotFoundError(
            f"Template not found: {template_path}\n"
            f"Create README.template.md in the project root."
        )

    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


def replace_section(content: str, section_name: str, replacement: str) -> str:
    """
    Replace content between section markers in the template.
    
    Finds:
        <!-- SECTION_NAME_START -->
        ...anything here...
        <!-- SECTION_NAME_END -->
    
    And replaces the content between the markers (keeping the markers).
    
    Args:
        content: The full template/README content.
        section_name: The marker name (e.g., "GITHUB_STATS").
        replacement: The new content to insert.
    
    Returns:
        The content with the section replaced.
    
    How the regex works:
        (<!-- SECTION_START -->)  → Group 1: opening marker (preserved)
        .*?                      → Non-greedy match of everything between
        (<!-- SECTION_END -->)   → Group 2: closing marker (preserved)
        
        re.DOTALL makes '.' match newlines too, so multi-line content
        between markers is matched correctly.
    """
    start_marker = f"<!-- {section_name}_START -->"
    end_marker = f"<!-- {section_name}_END -->"

    pattern = re.compile(
        rf"({re.escape(start_marker)})\s*.*?\s*({re.escape(end_marker)})",
        re.DOTALL,
    )

    if not pattern.search(content):
        logger.warning(
            f"Section markers not found in template: "
            f"{start_marker} / {end_marker}"
        )
        return content

    # Replace with: opening marker + newline + content + newline + closing marker
    replaced = pattern.sub(
        rf"\1\n{replacement}\n\2",
        content,
    )

    return replaced


def render_statistics(stats: dict) -> str:
    """
    Render the GitHub statistics section as markdown.
    
    Args:
        stats: Statistics dict from metrics.calculate_statistics().
    
    Returns:
        Formatted markdown string.
    """
    lines = []

    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| 📁 Public Repositories | {stats['total_repos']} |")
    lines.append(f"| ⭐ Total Stars | {stats['total_stars']} |")
    lines.append(f"| 🍴 Total Forks | {stats['total_forks']} |")
    lines.append(f"| 👥 Followers | {stats['followers']} |")
    lines.append(f"| 👤 Following | {stats['following']} |")

    if stats.get("most_starred_repo") and stats["most_starred_repo"]["stars"] > 0:
        repo = stats["most_starred_repo"]
        lines.append(
            f"| 🏆 Most Starred | [{repo['name']}]({repo['url']}) "
            f"({repo['stars']} ⭐) |"
        )

    if stats.get("most_recent_repo"):
        repo = stats["most_recent_repo"]
        updated = format_date(repo["updated_at"])
        lines.append(
            f"| 🔄 Most Recent | [{repo['name']}]({repo['url']}) "
            f"(updated {updated}) |"
        )

    return "\n".join(lines)


def render_languages(language_stats: list[dict]) -> str:
    """
    Render the technologies/languages section as markdown.
    
    Args:
        language_stats: List from metrics.calculate_language_stats().
    
    Returns:
        Formatted markdown string, or a note if no languages found.
    
    Uses simple text representation instead of complex charts to keep
    the README lightweight and universally readable.
    """
    if not language_stats:
        return "_No language data available yet. Languages will appear as repositories with code are added._"

    lines = []
    lines.append("| Language | Repositories | Usage |")
    lines.append("|----------|:------------:|-------|")

    for lang in language_stats:
        # Create a simple visual bar using block characters
        bar_length = max(1, int(lang["percentage"] / 5))  # Scale to ~20 chars max
        bar = "█" * bar_length
        lines.append(
            f"| {lang['language']} | {lang['count']} | "
            f"{bar} {lang['percentage']}% |"
        )

    return "\n".join(lines)


def render_projects(ranked_repos: list[dict], max_projects: int = 5) -> str:
    """
    Render the featured projects section as markdown.
    
    Args:
        ranked_repos: Ranked repos from metrics.rank_repositories().
        max_projects: Maximum number of projects to display.
    
    Returns:
        Formatted markdown string with project cards.
    """
    if not ranked_repos:
        return "_No projects to display yet. Projects will appear as repositories are created._"

    projects = ranked_repos[:max_projects]
    lines = []

    for project in projects:
        name = project["name"]
        description = project["description"]
        url = project["url"]
        stars = project["stars"]
        forks = project["forks"]
        language = project["language"]

        lines.append(f"### [{name}]({url})")
        lines.append(f"")
        lines.append(f"{description}")
        lines.append(f"")

        # Build metadata line
        meta_parts = []
        if language != "Not specified":
            meta_parts.append(f"💻 {language}")
        meta_parts.append(f"⭐ {stars}")
        meta_parts.append(f"🍴 {forks}")

        lines.append(" · ".join(meta_parts))
        lines.append("")

    return "\n".join(lines)


def render_activity(activity_summary: dict) -> str:
    """
    Render the recent activity section as markdown.
    
    Args:
        activity_summary: Summary from metrics.summarize_activity().
    
    Returns:
        Formatted markdown string.
    
    Important: We clearly label this as "recent public activity" to
    avoid misleading anyone about the completeness of the data.
    """
    if activity_summary["total_events"] == 0:
        return "_No recent public activity to display._"

    lines = []

    # Event type summary
    lines.append(f"**{activity_summary['total_events']}** recent public events")
    lines.append("")

    # Show recent events as a clean list
    event_type_labels = {
        "PushEvent": "🔨 Pushed code to",
        "PullRequestEvent": "🔀 Pull request on",
        "CreateEvent": "✨ Created",
        "IssuesEvent": "📋 Issue activity on",
        "WatchEvent": "⭐ Starred",
        "ForkEvent": "🍴 Forked",
        "DeleteEvent": "🗑️ Deleted from",
        "IssueCommentEvent": "💬 Commented on",
        "ReleaseEvent": "🚀 Released in",
    }

    for event in activity_summary["recent_events"]:
        event_type = event["type"]
        repo = event["repo"]
        label = event_type_labels.get(event_type, f"📌 {event_type} on")
        date = format_date(event["created_at"])
        lines.append(f"- {label} **{repo}** ({date})")

    lines.append("")
    lines.append(
        "_Activity is based on public events from the last 90 days "
        "via the GitHub Events API._"
    )

    return "\n".join(lines)


def render_last_updated() -> str:
    """Render the 'Last Updated' timestamp."""
    timestamp = get_current_timestamp()
    return f"_🕐 Last updated: {timestamp}_"


def render_readme(
    template_path: str | Path,
    stats: dict,
    language_stats: list[dict],
    ranked_repos: list[dict],
    activity_summary: dict,
    config: dict,
) -> str:
    """
    Render the complete README by replacing all dynamic sections.
    
    This is the main function that other modules should call. It:
    1. Loads the template
    2. Renders each section individually
    3. Replaces the corresponding markers
    4. Returns the final README content
    
    Args:
        template_path: Path to README.template.md.
        stats: From metrics.calculate_statistics().
        language_stats: From metrics.calculate_language_stats().
        ranked_repos: From metrics.rank_repositories().
        activity_summary: From metrics.summarize_activity().
        config: Profile configuration dict.
    
    Returns:
        The complete README content as a string.
    """
    logger.info("Rendering README from template...")

    content = load_template(template_path)

    # Replace each dynamic section based on config
    if config.get("show_statistics", True):
        stats_md = render_statistics(stats)
        content = replace_section(content, "GITHUB_STATS", stats_md)
    else:
        content = replace_section(content, "GITHUB_STATS", "")

    if config.get("show_languages", True):
        langs_md = render_languages(language_stats)
        content = replace_section(content, "TECHNOLOGIES", langs_md)
    else:
        content = replace_section(content, "TECHNOLOGIES", "")

    if config.get("show_projects", True):
        max_projects = config.get("max_projects", 5)
        projects_md = render_projects(ranked_repos, max_projects)
        content = replace_section(content, "PROJECTS", projects_md)
    else:
        content = replace_section(content, "PROJECTS", "")

    if config.get("show_activity", True):
        activity_md = render_activity(activity_summary)
        content = replace_section(content, "ACTIVITY", activity_md)
    else:
        content = replace_section(content, "ACTIVITY", "")

    # Always update the timestamp
    timestamp_md = render_last_updated()
    content = replace_section(content, "LAST_UPDATED", timestamp_md)

    logger.info("README rendered successfully")
    return content


def validate_readme(content: str) -> list[str]:
    """
    Validate the generated README content.
    
    Checks:
        1. Not empty
        2. Has a heading (starts with #)
        3. No unresolved placeholder markers (START/END without content)
        4. Reasonable length
    
    Args:
        content: The generated README content.
    
    Returns:
        A list of validation error strings. Empty list = valid.
    """
    errors = []

    if not content or not content.strip():
        errors.append("README is empty")
        return errors

    if not content.strip().startswith("#"):
        errors.append("README should start with a heading (#)")

    # Check for any remaining empty sections (START immediately followed by END)
    empty_sections = re.findall(
        r"<!-- (\w+)_START -->\s*<!-- \1_END -->",
        content,
    )
    if empty_sections:
        for section in empty_sections:
            errors.append(f"Section '{section}' appears to be empty")

    # Sanity check: README should be at least a few lines
    line_count = len(content.strip().split("\n"))
    if line_count < 5:
        errors.append(
            f"README seems too short ({line_count} lines). "
            f"Expected at least 5 lines."
        )

    return errors
