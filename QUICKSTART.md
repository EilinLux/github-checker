# Quick Start Guide

Get the GitHub Repository Analyzer up and running in 5 minutes.

## Prerequisites

- `uv` package manager ([install uv](https://docs.astral.sh/uv/getting-started/installation/))
  - `uv` includes Python 3.8+ and manages everything automatically
  - If you don't have Python installed, `uv` will install it for you
- GitHub App with private key (.pem file)
- GitHub organization where the app is installed

## 1. Clone/Download Project

```bash
cd github-checker
```

## 2. Install Dependencies

With `uv`, there's no need to manage virtual environments manually:

```bash
# uv handles Python installation and virtual environment automatically
uv sync
```

## 3. Configure Credentials

Create `.env` file from template:

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

Place your private key file:
```bash
cp /path/to/your/github-app-key.pem ./config.pem
```

## 4. Generate Installation List

```bash
uv run python apps/main_analyzer/org_retrieval.py
```

This creates `installations.yaml` with all your app installations.

## 5. Run Main Analysis

```bash
uv run python apps/main_analyzer/main.py
```

This analyzes all accessible repositories and generates detailed metrics including:
- Repository metadata (name, created date, language, etc.)
- Branch protection and security settings
- Commit activity and contributor counts
- Pull request metrics
- Permissions and collaboration details

## 6. Check Output

Reports are saved in `output/` as Excel files:
```
output/github_report_AGGREGATED_20240722_150230.xlsx
```

The report contains two sheets:
- **Report_Organizzazioni** - Organization and user admin roles
- **Report_Repositories** - Repository metrics and collaborators

## ✅ Main Analysis Complete!

Your analysis is complete. Check the output directory for your Excel report.

## Next Steps

### Customize Report Fields

Edit `config/output_fields.json` to choose which fields appear in reports:

```bash
# See available fields
cat config/templates/output_fields.example.json
```

### Analyze Specific Organization

Edit `.env`:
```ini
GITHUB_ORGANIZATION_NAME=my-org-name
```

Then run analysis again.

### Schedule Regular Reports

**Linux/Mac (cron)**:
```bash
# Edit crontab
crontab -e

# Add this line to run daily at 2 AM
0 2 * * * cd /path/to/github-checker && uv run python apps/main_analyzer/main.py
```

**Windows (Task Scheduler)**:
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (daily)
4. Set action: `uv` with arguments `run python apps/main_analyzer/main.py`
5. Working directory: `C:\path\to\github-checker`



## Additional Tools

### 🔍 Owner Analyzer - Team and User Analysis

Analyzes team membership, hierarchies, and team permissions across your organization.

```bash
uv run python apps/owner_analyzer/owner_analyzer.py
```

**What it does:**
- Scans all teams in your organization
- Maps team hierarchies (parent/child relationships)
- Lists team members and their roles (member vs. maintainer)
- Identifies repository access granted via team membership
- Generates Excel report with team structure

**Configuration in .env:**
```ini
# Parallel workers for faster processing (default: 10)
MAX_WORKERS=10
```

**Output:** `output/github_TEAMS_report_20240722_150230.xlsx`
- Contains team name, slug, parent team, members, roles, and repository access

**Use case:** Understanding who has access to repositories through team membership vs. direct collaboration.

### 📊 Compare Tools - Permission Comparison

Compares main analysis report with team report to identify permission anomalies.

```bash
uv run python apps/compare_tools/compare.py
```

**What it does:**
- Loads main analysis report (organizations + repositories)
- Loads team analysis report
- Identifies owners with implicit (organization-wide) access only
- Finds explicit collaborators who are not organization owners
- Flags permission inconsistencies

**Workflow:**
1. Prompts for main report file: `output/github_report_AGGREGATED_*.xlsx`
2. Prompts for team report file: `output/github_TEAMS_report_*.xlsx`
3. Compares and displays three lists:
   - All organization owners
   - Owners with only implicit access (via org membership)
   - Non-owners with explicit repository access (via teams/collaboration)

**Output:** Console report with three sections:
- Full owner list
- Implicit access owners
- Non-owner explicit access

**Use case:** Auditing access control to ensure it matches your security policy.

### 🚀 Repository Creator - Automated Repo Creation

Creates new repositories programmatically in your organization.

```bash
uv run python apps/repo_creator/create_new_repo.py
```

**What it does:**
- Authenticates as GitHub App
- Creates repository with specified configuration
- Sets visibility (public/private)
- Enables/disables issues
- Returns clone URL for immediate use

**Configuration in .env:**
```ini
# Target organization for new repository
REPO_CREATOR_ORG_NAME=MyOrganization

# Repository details
REPO_CREATOR_NAME=my-new-repo
REPO_CREATOR_DESCRIPTION=My repository description
REPO_CREATOR_PRIVATE=true  # Set to false for public repos
```

**Example:**
```bash
# Edit .env with your values:
REPO_CREATOR_ORG_NAME=DataWave
REPO_CREATOR_NAME=new-cloud-service
REPO_CREATOR_DESCRIPTION=Cloud service implementation
REPO_CREATOR_PRIVATE=true

# Run:
uv run python apps/repo_creator/create_new_repo.py
```

**Output:** 
- Success message with repository URL
- Clone URL for immediate use
- Error details if creation fails

**Use case:** Automating repository provisioning, bulk repository creation in CI/CD pipelines.

## Common Commands

```bash
# Run main analysis
uv run python apps/main_analyzer/main.py

# Run with debug output
uv run env DEBUG_MODE=True python apps/main_analyzer/main.py

# Analyze specific org (override .env)
uv run env GITHUB_ORGANIZATION_NAME=my-org python apps/main_analyzer/main.py

# Analyze teams and hierarchy
uv run python apps/owner_analyzer/owner_analyzer.py

# Compare permission reports
uv run python apps/compare_tools/compare.py

# Create new repository
uv run python apps/repo_creator/create_new_repo.py

# View installed packages
uv pip list

# Update all dependencies
uv sync --upgrade
```
## Troubleshooting

### Error: "Private key file not found"
- Verify `GITHUB_PRIVATE_KEY_PATH` in `.env`
- Ensure file exists: `ls -la config.pem`
- Check permissions: `chmod 600 config.pem`

### Error: "GITHUB_APP_ID or GITHUB_PRIVATE_KEY_PATH not set"
- Verify `.env` file exists in project root
- Check that lines don't have quotes around values

### Error: "OAuth token is invalid"
- Verify `GITHUB_INSTALLATION_ID` is correct
- Regenerate private key from GitHub App settings
- Reinstall the app if configuration changed

### No data in report
- Check `config/output_fields.json` is not empty
- Verify app is installed on target organization
- Try enabling `DEBUG_MODE=True` in `.env`

## Security Checklist

- ✅ `.env` is in `.gitignore`
- ✅ `*.pem` files are in `.gitignore`
- ✅ Private key has 600 permissions: `chmod 600 config.pem`
- ✅ Never commit `.env` or private keys
- ✅ Rotate private keys periodically
- ✅ Review `git status` before committing

## Documentation

- **Full Setup**: See [SETUP.md](SETUP.md)
- **Project Structure**: See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
- **uv Package Manager**: See [UV_GUIDE.md](UV_GUIDE.md)
- **Main Analyzer**: See [apps/main_analyzer/README.md](apps/main_analyzer/README.md)
- **Config Guide**: See [config/README.md](config/README.md)
- **Authentication**: See [commons/auth/README.md](commons/auth/README.md)

## Support

For detailed information:
1. Check the README in the specific app folder
2. Review SETUP.md for configuration
3. Look at .env.example for all options
4. Check commons/ modules for available utilities

---

**Time to first report**: ~5 minutes ⏱️
