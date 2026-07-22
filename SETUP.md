# Setup Instructions

Complete guide to set up and configure the GitHub Repository Analyzer.

## Table of Contents

1. [GitHub App Creation](#github-app-creation)
2. [Project Installation](#project-installation)
3. [Configuration](#configuration)
4. [First Run](#first-run)
5. [Troubleshooting](#troubleshooting)

## GitHub App Creation

### Step 1: Create the GitHub App

1. Go to your GitHub settings:
   - GitHub.com → Settings → Developer settings → GitHub Apps → New GitHub App

2. Fill in the application details:
   - **App name**: `Repository Analyzer Bot` (or your preferred name)
   - **Homepage URL**: `https://github.com` (can be any URL)
   - **Webhook**: Leave unchecked for now

3. Set Repository Permissions (read-only):
   - ✅ **Contents** - Read-only
   - ✅ **Metadata** - Read-only
   - ✅ **Pull Requests** - Read-only
   - ✅ **Administration** - Read-only (needed for branch protection)
   - ✅ **Security events** - Read-only (for Dependabot)

4. Set Organization Permissions:
   - ✅ **Members** - Read-only

5. Choose app visibility:
   - Select "Any account" to allow installation on any organization

6. Click **Create GitHub App**

### Step 2: Generate Private Key

1. On your GitHub App's settings page, scroll to **Private keys** section
2. Click **Generate a private key**
3. A `.pem` file will download - save it in the project root as `config.pem`
4. **NEVER commit this file to version control** (it's in `.gitignore`)

### Step 3: Install the GitHub App

1. On your app's settings page, click **Install App** in the left menu
2. Select the organization(s) you want to analyze
3. Grant access to "All repositories" or select specific ones
4. Note the **Installation ID** from the URL after installation

You'll need:
- App ID (from App settings)
- Installation ID (from installation page)
- Path to your `.pem` file

## Project Installation

### Step 1: Install uv

First, install the `uv` package manager if you don't have it:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (via PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via Homebrew (macOS)
brew install uv

# Or via pip (if you have Python)
pip install uv
```

See [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/) for more options.

### Step 2: Clone/Download Project

```bash
cd /path/to/github-checker
```

### Step 3: Install Dependencies

`uv` automatically manages Python and dependencies:

```bash
uv sync
```

This command will:
- Install Python 3.8+ if needed
- Create a virtual environment
- Install all dependencies from `pyproject.toml`

## Configuration

### Step 1: Create .env File

Copy the template and fill in your values:

```bash
cp .env.example .env
```

Edit `.env` with your GitHub App credentials:

```ini
GITHUB_APP_ID=123456
GITHUB_PRIVATE_KEY_PATH=./config.pem
GITHUB_INSTALLATION_ID=987654
DEBUG_MODE=False
OUTPUT_DIR=output
```

### Step 2: Verify Directory Structure

Ensure you have the required files:

```
github-checker/
├── .env                          # ← Create this with your credentials
├── config.pem                    # ← Private key (NOT in git)
├── requirements.txt
├── README.md
├── SETUP.md
├── .gitignore
├── commons/                      # Shared utilities
│   ├── auth/
│   ├── excel_writer/
│   └── github_api/
├── apps/                         # Individual applications
│   ├── main_analyzer/
│   ├── owner_analyzer/
│   ├── compare_tools/
│   └── repo_creator/
├── config/                       # Configuration files
│   ├── output_fields.json        # Fields to include in reports
│   ├── templates/
│   └── installations.example.yaml
└── output/                       # Generated reports (create if needed)
```

### Step 3: Configure Output Fields

Edit `config/output_fields.json` to select which fields to include in your reports:

```json
{
  "fields": [
    "Nome Repo",
    "Data Ultimo Commit",
    "Stato README",
    "Linguaggi Principali",
    "Permessi Scrittura (Collaboratori Diretti)"
  ]
}
```

See [apps/main_analyzer/README.md](apps/main_analyzer/README.md) for available field options.

## First Run

### Option 1: Analyze Organizations (Recommended)

1. First, discover all installations:

```bash
uv run python -m commons.auth.github_auth  # Lists all your app installations
```

2. Generate `installations.yaml`:

```bash
uv run python apps/main_analyzer/find_installations.py
```

3. Run the main analysis:

```bash
uv run python apps/main_analyzer/main.py
```

### Option 2: Quick Test

Test your configuration with a single organization:

```bash
uv run env GITHUB_ORGANIZATION_NAME=YourOrgName python apps/main_analyzer/main.py
```

## Output

After running successfully:

- Reports are saved in the `output/` directory
- Files are named: `github_report_AGGREGATED_YYYYMMDD_HHMMSS.xlsx`
- Reports contain two sheets:
  - `Report_Organizzazioni` - Organization-level data
  - `Report_Repositories` - Repository-level data

## Troubleshooting

### Authentication Failed

**Error**: "ERROR: Private key file not found"

**Solution**:
- Verify `GITHUB_PRIVATE_KEY_PATH` in `.env` is correct
- Ensure the file exists in the project root or specified path
- Check file permissions: `ls -la config.pem`

**Error**: "ERROR: GitHub_APP_ID or GITHUB_PRIVATE_KEY_PATH not set"

**Solution**:
- Verify `.env` file exists in the project root
- Check that values don't have quotes around them in `.env`
- Restart your terminal or IDE after creating `.env`

### Rate Limiting

**Error**: "API rate limit exceeded"

**Solutions**:
- Reduce `max_workers` in `commons/auth/README.md` configuration
- Add delays between API calls
- Check your rate limit: `curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/rate_limit`

### Missing Permissions

**Error**: "Insufficient permissions for this operation"

**Solution**:
- Verify your GitHub App has all required permissions (see [GitHub App Creation](#github-app-creation))
- Reinstall the app to apply new permissions
- Ensure the app is installed on the target organization

### Organization Not Found

**Error**: "ERROR: Organization 'YourOrg' not found or not accessible"

**Solutions**:
- Verify organization name is correct (case-sensitive)
- Ensure the GitHub App is installed on this organization
- Check `GITHUB_ORGANIZATION_NAME` in `.env`

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| No reports generated | Check `output_fields.json` is not empty |
| Empty reports | Verify app has access to all repositories |
| Slow performance | Reduce `max_workers` setting |
| Missing columns | Add fields to `config/output_fields.json` |

## Security Best Practices

⚠️ **IMPORTANT SECURITY NOTES**:

1. **Never commit these files**:
   - `.env` (environment variables with secrets)
   - `*.pem` (private keys)
   - `config.pem` (GitHub App private key)

2. **File permissions**:
   ```bash
   chmod 600 config.pem
   chmod 600 .env
   ```

3. **Credentials**:
   - Use environment variables, never hardcode
   - Rotate private keys periodically
   - Remove app if no longer needed

4. **Repository safety**:
   - `.gitignore` already excludes sensitive files
   - Always review before committing
   - Use `git status` to verify

## Next Steps

1. **Run your first analysis**:
   ```bash
   uv run python apps/main_analyzer/main.py
   ```

2. **Customize output**:
   - Edit `config/output_fields.json` for different reports
   - Adjust `max_workers` for performance

3. **Schedule regular runs**:
   - Use cron (Linux/Mac) or Task Scheduler (Windows)
   - Save reports with timestamps for tracking changes
   - Use `uv run python apps/main_analyzer/main.py` in your scheduling commands

## Support

For detailed information on specific modules:

- [GitHub Authentication](commons/auth/README.md)
- [Excel Export](commons/excel_writer/README.md)
- [Main Analyzer](apps/main_analyzer/README.md)

---

**Last Updated**: 2024
**Version**: 1.0
