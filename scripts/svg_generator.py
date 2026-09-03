"""
svg_generator.py — Custom SVG card builder for GitHub Profile README.

Generates self-contained, beautifully styled SVG cards directly from Python.
Includes an SVG curve/sparkline graph for daily activity.
"""

from collections import Counter
from datetime import datetime
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

    return f"""<svg width="450" height="220" viewBox="0 0 450 220" fill="none" xmlns="http://www.w3.org/2000/svg">
  <style>
    .bg {{ fill: #1a1b26; rx: 10px; }}
    .border {{ stroke: #414868; stroke-width: 1px; fill: none; rx: 10px; }}
    .title {{ font-family: 'Segoe UI', Ubuntu, sans-serif; font-weight: 700; font-size: 18px; fill: #7aa2f7; }}
    .label {{ font-family: 'Segoe UI', Ubuntu, sans-serif; font-size: 14px; fill: #a9b1d6; }}
    .value {{ font-family: 'Segoe UI', Ubuntu, sans-serif; font-weight: 600; font-size: 14px; fill: #7dcfff; }}
  </style>

  <rect width="450" height="220" class="bg" />
  <rect width="449" height="219" x="0.5" y="0.5" class="border" />

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


def generate_activity_card_svg(activity_summary: dict) -> str:
    """
    Generate an SVG card displaying activity metrics and a visual daily activity curve line chart.
    """
    total_events = activity_summary.get("total_events", 0)
    event_types = activity_summary.get("event_types", {})
    recent_events = activity_summary.get("recent_events", [])

    prs = event_types.get("PullRequestEvent", 0)
    pushes = event_types.get("PushEvent", 0)

    # Build daily activity curve points
    daily_counts = Counter()
    for ev in recent_events:
        date_str = ev.get("created_at", "")[:10]  # YYYY-MM-DD
        if date_str:
            daily_counts[date_str] += 1

    # Create a 7-point curve (or mock default curve if few points exist)
    if daily_counts:
        sorted_dates = sorted(daily_counts.keys())[-7:]
        values = [daily_counts[d] for d in sorted_dates]
    else:
        values = [1, 2, 4, 3, 5, 4, 6]

    # Ensure at least 5 points for smooth curve
    while len(values) < 7:
        values.insert(0, 1)

    max_val = max(max(values), 1)
    
    # Calculate SVG coordinates for line chart (width: 380px, height: 50px, origin x=35, y=185)
    points = []
    chart_x_start = 35
    chart_width = 380
    chart_y_base = 185
    chart_height = 45

    step_x = chart_width / (len(values) - 1)
    for idx, val in enumerate(values):
        px = chart_x_start + (idx * step_x)
        py = chart_y_base - ((val / max_val) * chart_height)
        points.append((px, py))

    # Path d string for curve line
    path_d = f"M {points[0][0]:.1f},{points[0][1]:.1f}"
    for i in range(1, len(points)):
        # Smooth curve interpolation using cubic control points
        p0 = points[i - 1]
        p1 = points[i]
        cx1 = p0[0] + step_x / 2
        cy1 = p0[1]
        cx2 = p1[0] - step_x / 2
        cy2 = p1[1]
        path_d += f" C {cx1:.1f},{cy1:.1f} {cx2:.1f},{cy2:.1f} {p1[0]:.1f},{p1[1]:.1f}"

    # Area fill path under the line graph
    area_d = path_d + f" L {points[-1][0]:.1f},{chart_y_base} L {points[0][0]:.1f},{chart_y_base} Z"

    # Data dots
    dots_svg = "".join(
        f'<circle cx="{pt[0]:.1f}" cy="{pt[1]:.1f}" r="3" fill="#7dcfff" />'
        for pt in points
    )

    svg = f"""<svg width="450" height="220" viewBox="0 0 450 220" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="curveGradient" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#7dcfff" stop-opacity="0.5" />
      <stop offset="100%" stop-color="#7dcfff" stop-opacity="0.0" />
    </linearGradient>
  </defs>

  <style>
    .bg {{ fill: #1a1b26; rx: 10px; }}
    .border {{ stroke: #414868; stroke-width: 1px; fill: none; rx: 10px; }}
    .title {{ font-family: 'Segoe UI', Ubuntu, sans-serif; font-weight: 700; font-size: 18px; fill: #bb9af7; }}
    .label {{ font-family: 'Segoe UI', Ubuntu, sans-serif; font-size: 13px; fill: #a9b1d6; }}
    .value {{ font-family: 'Segoe UI', Ubuntu, sans-serif; font-weight: 600; font-size: 13px; fill: #9ece6a; }}
    .axis {{ stroke: #3b4261; stroke-width: 1px; stroke-dasharray: 2 2; }}
    .curve-line {{ stroke: #7dcfff; stroke-width: 3px; fill: none; stroke-linecap: round; }}
  </style>

  <rect width="450" height="220" class="bg" />
  <rect width="449" height="219" x="0.5" y="0.5" class="border" />

  <!-- Title -->
  <text x="25" y="35" class="title">📈 Activity &amp; Contribution Curve</text>
  <line x1="25" y1="48" x2="425" y2="48" stroke="#3b4261" stroke-width="1" />

  <!-- Top Stat Metrics -->
  <g transform="translate(25, 70)">
    <text class="label" x="0" y="0">🔀 Pull Requests: <tspan class="value">{prs}</tspan></text>
    <text class="label" x="180" y="0">🔨 Code Pushes: <tspan class="value">{pushes}</tspan></text>
    <text class="label" x="0" y="22">🔥 Recent Events: <tspan class="value">{total_events}</tspan></text>
  </g>

  <!-- Curve Chart Section -->
  <text x="25" y="125" class="label" font-weight="600" fill="#7aa2f7">Recent Daily Activity Trend</text>

  <!-- Grid lines -->
  <line x1="35" y1="140" x2="415" y2="140" class="axis" />
  <line x1="35" y1="185" x2="415" y2="185" stroke="#3b4261" stroke-width="1" />

  <!-- Area Fill under curve -->
  <path d="{area_d}" fill="url(#curveGradient)" />

  <!-- Curve Line -->
  <path d="{path_d}" class="curve-line" />

  <!-- Data Dots -->
  {dots_svg}
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
        bars_svg = """<text x="25" y="110" font-family="'Segoe UI', Ubuntu, sans-serif" font-size="14" fill="#a9b1d6">No language data available yet</text>"""
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

    return f"""<svg width="450" height="220" viewBox="0 0 450 220" fill="none" xmlns="http://www.w3.org/2000/svg">
  <style>
    .bg {{ fill: #1a1b26; rx: 10px; }}
    .border {{ stroke: #414868; stroke-width: 1px; fill: none; rx: 10px; }}
    .title {{ font-family: 'Segoe UI', Ubuntu, sans-serif; font-weight: 700; font-size: 18px; fill: #7dcfff; }}
  </style>

  <rect width="450" height="220" class="bg" />
  <rect width="449" height="219" x="0.5" y="0.5" class="border" />

  <!-- Title -->
  <text x="25" y="35" class="title">💻 Top Languages Used</text>
  <line x1="25" y1="48" x2="425" y2="48" stroke="#3b4261" stroke-width="1" />

  {bars_svg}
</svg>"""


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
