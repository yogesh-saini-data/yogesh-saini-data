# GitHub Profile README Automation System

An automated, self-hosted GitHub Profile README generator written in Python and deployed using GitHub Actions CI/CD.

## 🚀 Overview

This repository continuously fetches public GitHub profile data, calculates repository & activity metrics, renders custom dark-mode SVG graphs (`assets/`), builds a clean profile `README.md` from `README.template.md`, and automatically commits updates via GitHub Actions.

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
Generate Custom SVG Cards (svg_generator.py -> assets/*.svg)
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

---

## 📋 How to Setup This System for Another GitHub Account

If you want to use this project for a **different GitHub account** (or share it with a friend), follow these steps:

### 1. Create Profile Repository
Create a new **Public** GitHub repository where the repository name **matches the target username**.
> *Example:* Username `john-doe` -> Repository `john-doe/john-doe`.

### 2. Copy Code & Update `config/profile_config.json`
Change `"username"` to the new GitHub username:
```json
{
  "username": "NEW_GITHUB_USERNAME",
  "max_projects": 5,
  "include_forks": false,
  "include_archived": false,
  "show_statistics": true,
  "show_languages": true,
  "show_activity": true,
  "show_projects": true
}
```

### 3. Customize Static Content in `README.template.md`
Update your bio, name, and social links in `README.template.md`. Keep the `<!-- SECTION_START -->` comment markers intact.

### 4. Enable Workflow Write Permissions on GitHub
Go to **Settings** -> **Actions** -> **General** -> **Workflow permissions** -> Select **Read and write permissions** -> **Save**.

### 5. Push & Run
Push the code to your repository:
```bash
git add .
git commit -m "feat: setup profile automation"
git push origin main
```
Go to the **Actions** tab on GitHub and click **Run workflow**!

---

## 💻 Local Setup & Development

### Setup Virtual Environment (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Run Dry-Run Mode

```powershell
python scripts/generate_readme.py --dry-run
```

### Generate README & SVG Cards Locally

```powershell
python scripts/generate_readme.py
```

### Run Test Suite

```powershell
python -m pytest tests/ -v
```

---

## 📜 License

Distributed under the MIT License. See [LICENSE](file:///c:/Users/YogeshSaini/Desktop/yogesh-saini-data/LICENSE) for details.
