# Main Repository Analyzer

Comprehensive GitHub repository analysis tool that analyzes both organization-level and repository-level metrics using GitHub App authentication.

## Features

- **Organization Analysis**: Collects organization details, members, roles, and security settings
- **Repository Analysis**: Parallel processing of repository metrics
- **Multi-metric Analysis**:
  - Team permissions and collaborator details
  - Branch protection status
  - README presence
  - License information
  - Dependabot and SonarQube/Codacy status
  - PR merge times
  - Webhook counts
  - Code languages
  - And more...
- **Parallel Processing**: Uses ThreadPoolExecutor for efficient analysis of multiple repositories
- **Excel Export**: Generates multi-sheet Excel reports with auto-formatted columns
- **Debug Mode**: Optional detailed logging for troubleshooting

## Prerequisites

- GitHub App installed with appropriate permissions
- Python 3.8+
- Dependencies listed in `requirements.txt`

## Installation

```bash
# From project root
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration

### Environment Variables (.env)

Create a `.env` file in the project root:

```ini
GITHUB_APP_ID=your_app_id
GITHUB_PRIVATE_KEY_PATH=./config.pem
GITHUB_INSTALLATION_ID=your_installation_id
GITHUB_ORGANIZATION_NAME=optional_org_name
DEBUG_MODE=False
OUTPUT_DIR=output
```

### Output Fields Configuration

Edit `config/output_fields.json` to specify which fields to include in reports:

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

### Installation File

The `installations.yaml` file contains all organizations to analyze. Generate it using:

```bash
python apps/main_analyzer/find_installations.py
```

## Usage

### Run the Main Analysis

```bash
python apps/main_analyzer/main.py
```

This will:
1. Load configuration from `.env` and `config/output_fields.json`
2. Read organizations from `installations.yaml`
3. Authenticate with GitHub API for each organization
4. Analyze all repositories in parallel
5. Generate an Excel report in the `output/` directory

### Output

The script generates a multi-sheet Excel file containing:
- **Report_Organizzazioni**: Organization-level data (members, roles, security settings)
- **Report_Repositories**: Repository-level data (metrics, permissions, status)

## Available Output Fields

### Repository Fields

- Nome Repo - Full repository name
- Descrizione - Repository description
- Licenza - License information
- Archiviata - Archived status
- Data Ultimo Commit - Last commit date
- Stato README - README presence
- Branch Default - Default branch name
- Stato Protezione Branch Default - Branch protection status
- Permessi Lettura (Collaboratori Diretti) - Read-only collaborators
- Permessi Scrittura (Collaboratori Diretti) - Write-permission collaborators
- Permessi per Team (Team: Livello) - Team permissions
- Numero Webhooks Attivi - Active webhooks count
- Tempo Medio Merge PR (Ult. 50) - Average PR merge time
- Numero Issue Aperte - Open issues count
- Numero Pull Request Aperte - Open PRs count
- Dependabot Attivo - Dependabot status
- Top Contributori - Top 100 contributors
- Linguaggi Principali - Programming languages
- Codacy/SonarQube Attivo - Code quality tool status
- Branch (Nomi) - Branch names
- Numero File per Branch - File count per branch
- Dimensione (MB) - Repository size

### Organization Fields

- Organizzazione - Organization name
- 2FA Obbligatoria - Two-factor authentication requirement
- Email Billing - Billing email
- Default Repo Permission - Default repository permission
- Totale Repo (Privati) - Total private repositories
- Totale Repo (Pubblici) - Total public repositories
- User - Team member login
- Role - Member role (Admin/Member)

## Architecture

```
apps/main_analyzer/
├── __init__.py
├── README.md (this file)
├── main.py                 # Main entry point
├── github_analyzer.py       # RepoAnalyzer class
└── utils/
    └── config_loader.py    # Configuration utilities
```

## Performance Notes

- Default 10 workers for parallel processing (configurable)
- Rate limit tracking for API optimization
- Thread-safe debug logging
- Handles both organizations and user repositories

## Error Handling

- Graceful handling of rate limits
- Detailed error messages for API failures
- Debug mode for troubleshooting
- Skips repositories with permission errors

## Troubleshooting

### GitHub App Authentication Issues
- Verify GitHub App ID in `.env`
- Check private key file path and permissions
- Ensure installation ID is correct
- Verify app is installed on the target organization

### Rate Limiting
- Check API rate limit status with `DEBUG_MODE=True`
- Reduce `max_workers` in configuration
- Wait for rate limit reset

### Missing Data
- Check output_fields.json configuration
- Verify GitHub App has required permissions
- Check organizations in installations.yaml

## See Also

- [commons/auth](../../commons/auth/README.md) - Authentication module
- [commons/excel_writer](../../commons/excel_writer/README.md) - Excel export utilities
