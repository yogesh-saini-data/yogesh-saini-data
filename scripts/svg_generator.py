"""
svg_generator.py — Custom SVG card builder for GitHub Profile README.

Generates self-contained, beautifully styled SVG cards directly from Python.
Because these SVGs are generated locally by our CI/CD pipeline, they are:
    - 100% reliable (no third-party server rate limits or downtime)
    - Fully custom-styled with dark mode gradient aesthetics
    - Embedded directly into the GitHub profile README via standard markdown images
"""

from pathlib import Path


def generate_stats_card_svg(stats: dict) -> str:
    """
    Generate an SVG card displaying key profile statistics.
    """
    total_repos = stats.get("total_repos", 0)
    total_stars = stats.get("total_stars", 0)
    total_forks = stats.get("total_forks", 0)
    followers = stats.get("followers", 0)
    account_age = stats.get("account_age_days", 0)

    svg = f"""<svg width="450" height="200" viewBox="0 0 450 200" fill="none" xmlns="http://www.w3.org/2000/svg">
  <style>
    .bg {{ fill: #1a1b26; rx: 10px; }}
    .border {{ stroke: #414868; stroke-width: 1px; fill: none; rx: 10px; }}
    .title {{ font-family: 'Segoe UI', Ubuntu, sans-serif; font-weight: 700; font-size: 18px; fill: #7aa2f7; }}
    .icon {{ font-size: 16px; }}
    .label {{ font-family: 'Segoe UI', Ubuntu, sans-serif; font-size: 14px; fill: #a9b1d6; }}
    .value {{ font-family: 'Segoe UI', Ubuntu, sans-serif; font-weight: 600; font-size: 14px; fill: #7dcfff; }}
  </style>

  <rect width="450" height="200" class="bg" />
  <rect width="449" height="199" x="0.5" y="0.5" class="border" />

  <!-- Title -->
  <text x="25" y="35" class="title">⚡ GitHub Overview Stats</text>
  <line x1="25" y1="48" x2="425" y2="48" stroke="#3b4261" stroke-width="1" />

  <!-- Stat Items -->
  <g transform="translate(25, 75)">
    <text class="label" x="0" y="0">📁 Public Repositories:</text>
    <text class="value" x="380" y="0" text-anchor="end">{total_repos}</text>

    <text class="label" x="0" y="25">⭐ Total Stars Earned:</text>
    <text class="value" x="380" y="25" text-anchor="end">{total_stars}</text>

    <text class="label" x="0" y="50">🍴 Total Forks:</text>
    <text class="value" x="380" y="50" text-anchor="end">{total_forks}</text>

    <text class="label" x="0" y="75">👥 Followers:</text>
    <text class="value" x="380" y="75" text-anchor="end">{followers}</text>

    <text class="label" x="0" y="100">⏳ Account Age:</text>
    <text class="value" x="380" y="100" text-anchor="end">{account_age} days</text>
  </g>
</svg>"""

    return svg


def generate_activity_card_svg(activity_summary: dict) -> str:
    """
    Generate an SVG card displaying recent activity breakdown and event metrics.
    """
    total_events = activity_summary.get("total_events", 0)
    event_types = activity_summary.get("event_types", {})

    prs = event_types.get("PullRequestEvent", 0)
    pushes = event_types.get("PushEvent", 0)
    creates = event_types.get("CreateEvent", 0)
    issues = event_types.get("IssuesEvent", 0)
    other = sum(v for k, v in event_types.items() if k not in ["PullRequestEvent", "PushEvent", "CreateEvent", "IssuesEvent"])

    svg = f"""<svg width="450" height="200" viewBox="0 0 450 200" fill="none" xmlns="http://www.w3.org/2000/svg">
  <style>
    .bg {{ fill: #1a1b26; rx: 10px; }}
    .border {{ stroke: #414868; stroke-width: 1px; fill: none; rx: 10px; }}
    .title {{ font-family: 'Segoe UI', Ubuntu, sans-serif; font-weight: 700; font-size: 18px; fill: #bb9af7; }}
    .label {{ font-family: 'Segoe UI', Ubuntu, sans-serif; font-size: 14px; fill: #a9b1d6; }}
    .value {{ font-family: 'Segoe UI', Ubuntu, sans-serif; font-weight: 600; font-size: 14px; fill: #9ece6a; }}
    .curve {{ stroke: #7dcfff; stroke-width: 3px; fill: none; stroke-linecap: round; }}
  </style>

  <rect width="450" height="200" class="bg" />
  <rect width="449" height="199" x="0.5" y="0.5" class="border" />

  <!-- Title -->
  <text x="25" y="35" class="title">📈 Activity & Contribution Curve</text>
  <line x1="25" y1="48" x2="425" y2="48" stroke="#3b4261" stroke-width="1" />

  <!-- Stat Items -->
  <g transform="translate(25, 75)">
    <text class="label" x="0" y="0">🔀 Pull Requests:</text>
    <text class="value" x="380" y="0" text-anchor="end">{prs}</text>

    <text class="label" x="0" y="25">🔨 Code Pushes:</text>
    <text class="value" x="380" y="25" text-anchor="end">{pushes}</text>

    <text class="label" x="0" y="50">✨ Created Branches/Repos:</text>
    <text class="value" x="380" y="50" text-anchor="end">{creates}</text>

    <text class="label" x="0" y="75">📋 Issue Activity:</text>
    <text class="value" x="380" y="75" text-anchor="end">{issues}</text>

    <text class="label" x="0" y="100">🔥 Total Public Events (90d):</text>
    <text class="value" x="380" y="100" text-anchor="end">{total_events}</text>
  </g>
</svg>"""

    return svg


def generate_languages_card_svg(language_stats: list[dict]) -> str:
    """
    Generate an SVG card displaying language usage with visual progress bars.
    """
    colors = ["#7aa2f7", "#7dcfff", "#bb9af7", "#f7768e", "#e0af68", "#9ece6a"]

    bars_svg = ""
    y_offset = 65

    if not language_stats:
        bars_svg = """<text x="25" y="100" font-family="'Segoe UI', Ubuntu, sans-serif" font-size="14" fill="#a9b1d6">No language data available yet</text>"""
    else:
        for i, lang in enumerate(language_stats[:4]):
            name = lang["language"]
            pct = lang["percentage"]
            color = colors[i % len(colors)]
            bar_width = int((pct / 100) * 260)

            bars_svg += f"""
    <g transform="translate(25, {y_offset})">
      <text font-family="'Segoe UI', Ubuntu, sans-serif" font-size="13" fill="#a9b1d6" x="0" y="12">{name}</text>
      <rect x="110" y="2" width="240" height="12" fill="#24283b" rx="6" />
      <rect x="110" y="2" width="{max(bar_width, 10)}" height="12" fill="{color}" rx="6" />
      <text font-family="'Segoe UI', Ubuntu, sans-serif" font-weight="600" font-size="13" fill="{color}" x="380" y="12" text-anchor="end">{pct}%</text>
    </g>"""
            y_offset += 30

    svg = f"""<svg width="450" height="200" viewBox="0 0 450 200" fill="none" xmlns="http://www.w3.org/2000/svg">
  <style>
    .bg {{ fill: #1a1b26; rx: 10px; }}
    .border {{ stroke: #414868; stroke-width: 1px; fill: none; rx: 10px; }}
    .title {{ font-family: 'Segoe UI', Ubuntu, sans-serif; font-weight: 700; font-size: 18px; fill: #7dcfff; }}
  </style>

  <rect width="450" height="200" class="bg" />
  <rect width="449" height="199" x="0.5" y="0.5" class="border" />

  <!-- Title -->
  <text x="25" y="35" class="title">💻 Top Languages Used</text>
  <line x1="25" y1="48" x2="425" y2="48" stroke="#3b4261" stroke-width="1" />

  {bars_svg}
</svg>"""

    return svg


def save_svg_cards(stats: dict, activity_summary: dict, language_stats: list[dict], output_dir: Path):
    """
    Generate and save all SVG cards to the assets directory.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    stats_svg = generate_stats_card_svg(stats)
    activity_svg = generate_activity_card_svg(activity_summary)
    languages_svg = generate_languages_card_svg(language_stats)

    with open(output_dir / "stats_card.svg", "w", encoding="utf-8") as f:
        f.write(stats_svg)

    with open(output_dir / "activity_card.svg", "w", encoding="utf-8") as f:
        f.write(activity_svg)

    with open(output_dir / "languages_card.svg", "w", encoding="utf-8") as f:
        f.write(languages_svg)
