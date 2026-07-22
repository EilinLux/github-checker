# GitHub Repository Analyzer (GitHub App Auth)

This script analyzes repositories accessible by a **GitHub App installation**, extracts detailed metrics, and exports the report to both an Excel file and a Confluence page.

This version uses the more secure GitHub App authentication method (JWTs) instead of a Personal Access Token.

## Features

* **GitHub App Authentication:** Securely authenticates as a GitHub App installation.
* **GitHub Analysis:** Fetches a wide range of repository data (permissions, branches, commits, PRs, etc.).
* **Excel Export:** Saves the report as a formatted `.xlsx` file.
* **Confluence Export:** Publishes the same report as a table on a Confluence page.
* **External Configuration:**
    * **`.env`:** Securely stores all API keys, App IDs, and paths.
    * **`config.yaml`:** Easily configure which fields to include in the report.

## Quick Start (5 Minutes)

```bash
# 1. Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clone/download the project
cd github-checker

# 3. Install dependencies
uv sync

# 4. Copy and configure credentials
cp .env.example .env
# Edit .env with your GitHub App credentials

# 5. Run the analyzer
uv run python apps/main_analyzer/main.py
```

For detailed setup instructions, see [QUICKSTART.md](QUICKSTART.md) or [SETUP.md](SETUP.md).

## Setup & Installation

1.  **Create a GitHub App:**
    * Go to your GitHub Settings > Developer settings > GitHub Apps > New GitHub App.
    * Give it a name (e.g., "Repo Analyzer Bot").
    * Set a homepage URL (can be `https://github.com`).
    * **Set Repository Permissions:** This is critical. Grant **Read-only** access for:
        * Contents
        * Metadata
        * Pull Requests
        * Administration (needed for branch protection, webhooks, and collaborators)
        * Security events (for Dependabot)
    * Set **Organization Permissions:**
        * Members (Read-only)
    * Under "Where can this GitHub App be installed?", select "Any account".
    * Click "Create GitHub App".
    * On the app's page, **generate a private key** and download the `.pem` file. Save it in your project directory (e.g., as `github-app-key.pem`).

2.  **Install the GitHub App:**
    * From the app's settings page, go to "Install App" and install it on the organization(s) or user account(s) you want to analyze.
    * Grant it access to "All repositories" or "Only select repositories".

3.  **Install Dependencies with uv:**
    * Install `uv` (macOS/Linux):
        ```bash
        curl -LsSf https://astral.sh/uv/install.sh | sh
        ```
    * Or install via Homebrew (macOS):
        ```bash
        brew install uv
        ```
    * Then install project dependencies:
        ```bash
        uv sync
        ```

## Configuration

### 1. `.env` File 

Create a file named `.env` in the root directory. This now holds your App credentials.

```ini
# GITHUB APP CONFIGURATION
GITHUB_APP_ID=YOUR_APP_ID_HERE
GITHUB_INSTALLATION_ID=YOUR_INSTALLATION_ID_HERE
# Path to your .pem private key file, e.g., ./github-app-key.pem
GITHUB_PRIVATE_KEY_PATH=./github-app-key.pem

# Optional: Set this if you want to scan a single organization
# If blank, it will scan all repos the installation has access to.
ORGANIZATION_NAME=BIPxTech-Sunrise

# CONFLUENCE CONFIGURATION
CONFLUENCE_URL=[https://your-domain.atlassian.net/](https://your-domain.atlassian.net/)
CONFLUENCE_USERNAME=your-email@example.com
CONFLUENCE_TOKEN=YOUR_CONFLUENCE_API_TOKEN_HERE
CONFLUENCE_SPACE=YOUR_CONFLUENCE_SPACE_KEY

# OUTPUT CONFIGURATION
OUTPUT_DIR=reports
```


## 📚 Quick Navigation

### Getting Started (Pick Your Path)

**⏱️ 5 Minutes?**
→ Read [QUICKSTART.md](QUICKSTART.md)

**⏱️ 15 Minutes?**
→ Read [SETUP.md](SETUP.md)

**⏱️ 30 Minutes?**
→ Read [README.md](README.md) + [SETUP.md](SETUP.md) + [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

