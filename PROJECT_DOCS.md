# GitHub Profile README Automation System

An automated, self-hosted GitHub Profile README generator written in Python and deployed using GitHub Actions CI/CD.

## 🚀 Overview

This repository continuously fetches public GitHub profile data, calculates repository & activity metrics, renders a clean profile `README.md` from `README.template.md`, and automatically commits updates via GitHub Actions.

```text
GitHub Profile Repository
        │
        ▼
GitHub Actions (Scheduled / Manual)
        │
        ▼
Python Application (generate_readme.py)
        │
        ▼
GitHub REST API
        │
        ▼
Fetch & Filter GitHub Data
        │
        ▼
Transform & Calculate Metrics (metrics.py)
        │
        ▼
Render Template (renderer.py & README.template.md)
        │
        ▼
Validate README Content
        │
        ▼
Git Diff Check → Commit & Push (if changed)
```

---

## 🛠️ Technology Stack & Architecture

- **Language:** Python 3.12+ (standard library + `requests`)
- **Testing:** `pytest`
- **CI/CD:** GitHub Actions
- **API:** GitHub REST API v3

### Project Structure
```text
yogesh-saini-data/
├── README.md                  # Generated profile README (Auto-updated)
├── README.template.md         # Customizable template with HTML markers
├── requirements.txt           # Python dependencies
├── LICENSE                    # MIT License
├── .gitignore                 # Excluded files
├── config/
│   └── profile_config.json    # User configuration
├── scripts/
│   ├── generate_readme.py     # Main orchestrator CLI
│   ├── github_api.py          # GitHub REST API client
│   ├── metrics.py             # Statistics & ranking algorithms
│   ├── renderer.py            # Template rendering & section replacement
│   └── utils.py               # Config loading & logging helpers
├── tests/
│   ├── test_github_api.py     # API mock tests
│   ├── test_metrics.py        # Calculation unit tests
│   ├── test_renderer.py       # Renderer tests
│   └── test_generate_readme.py# Integration tests
└── .github/
    └── workflows/
        ├── update-readme.yml  # Daily auto-update workflow
        └── validate.yml       # PR validation workflow
```

---

## 💻 Local Setup & Development

### 1. Setup Virtual Environment (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Run Dry-Run Mode (Safer testing without overwriting `README.md`)

```powershell
python scripts/generate_readme.py --dry-run
```

### 3. Generate README Locally

```powershell
python scripts/generate_readme.py
```

### 4. Run Test Suite

```powershell
python -m pytest tests/ -v
```

---

## ⚙️ Configuration (`config/profile_config.json`)

You can customize generation settings without editing Python code:

```json
{
  "username": "yogesh-saini-data",
  "max_projects": 5,
  "include_forks": false,
  "include_archived": false,
  "show_statistics": true,
  "show_languages": true,
  "show_activity": true,
  "show_projects": true
}
```

---

## 🔄 How CI/CD Automation & GitHub Actions Work

1. **`update-readme.yml` Schedule & Triggers:**
   - **Cron Schedule:** Runs daily at `00:00 UTC` (`0 0 * * *`).
   - **Manual Trigger:** Can be manually triggered from the **Actions** tab via `workflow_dispatch`.

2. **Authentication:**
   - Uses the auto-generated `GITHUB_TOKEN` provided by GitHub Actions:
     ```yaml
     env:
       GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
     ```
   - Requires minimal repository write permissions (`contents: write`).

3. **Preventing Infinite Loops:**
   - Uses `git diff --quiet README.md` to ensure a commit is made **only when content changes**.
   - Appends `[skip ci]` to the commit message: `chore: update profile README [skip ci]`.

---

## ❓ Frequently Asked Questions (Beginner-Friendly Concepts)

### Why is `README.template.md` separate from `README.md`?
`README.template.md` holds your static bio, intro, and placeholders (e.g. `<!-- GITHUB_STATS_START -->`). The Python script reads the template, computes the fresh data, injects it between the markers, and outputs `README.md`. This allows you to edit static text without touching code.

### Why do we need `GITHUB_TOKEN`?
Unauthenticated API requests to GitHub are limited to **60 requests/hour**. Providing `GITHUB_TOKEN` increases your limit to **5,000 requests/hour**, preventing rate-limit errors in CI/CD.

### How does Git diff prevent useless commits?
The workflow runs `git diff --quiet README.md`. If the generated markdown is identical to the current `README.md`, `git diff` exits quietly and the workflow skips `git commit` and `git push`.

---

## 📜 License

Distributed under the MIT License. See [LICENSE](file:///c:/Users/YogeshSaini/Desktop/yogesh-saini-data/LICENSE) for details.
