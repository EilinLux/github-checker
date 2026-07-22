# Owner Analyzer

Analyzes team structures, membership hierarchies, and access permissions across your organization.

## Features

- Team membership analysis
- Team hierarchy mapping (parent/child relationships)
- Role-based team member listing (maintainers vs. members)
- Repository access tracking via team assignment
- Parallel processing for fast analysis
- Comprehensive Excel reporting

## Usage

```bash
uv run python apps/owner_analyzer/owner_analyzer.py
```

## Configuration

Set these environment variables in `.env`:

**Required:**
- `GITHUB_APP_ID` - Your GitHub App ID
- `GITHUB_INSTALLATION_ID` - Installation ID from the app's installation URL
- `GITHUB_PRIVATE_KEY_PATH` - Path to your GitHub App private key (.pem file)

**Optional:**
- `MAX_WORKERS` - Number of parallel workers (default: 10, increase for faster processing)
- `DEBUG_MODE` - Enable debug logging (default: False)
- `OUTPUT_DIR` - Directory for output reports (default: output)

## Output

Generates Excel file: `output/github_TEAMS_report_TIMESTAMP.xlsx`

The report contains:
- Team name and slug
- Parent team (if nested)
- Team members and their roles
- Repository access levels (pull, push, admin)
- Organization assignment

## Example

```bash
# Run with default settings
uv run python apps/owner_analyzer/owner_analyzer.py

# Run with debug output
uv run env DEBUG_MODE=True python apps/owner_analyzer/owner_analyzer.py

# Run with custom number of workers
uv run env MAX_WORKERS=20 python apps/owner_analyzer/owner_analyzer.py
```

## Use Cases

- Auditing team membership and organization roles
- Understanding implicit vs. explicit repository access
- Identifying team hierarchies and organizational structure
- Preparing for access control reviews

## See Also

- [Main Analyzer](../main_analyzer/README.md) - Repository metrics analysis
- [Compare Tools](../compare_tools/README.md) - Permission comparison
- [commons/auth](../../commons/auth/README.md) - Authentication details
