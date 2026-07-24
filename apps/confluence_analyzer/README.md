# Confluence Analyzer

Analyzes GitHub repositories and synchronizes access permissions directly to a Confluence Database in real-time.

## Features

- **GitHub Analysis:** Extracts repository information and access permissions
- **Confluence Integration:** Writes directly to Confluence Database (API v2)
- **Bulk Data Sync:** Synchronizes multiple repositories and team members
- **Real-time Updates:** Creates new database rows for each repository-user access
- **Dual Export:** Generates both CSV and Excel reports
- **Rate Limit Handling:** Manages GitHub API rate limits gracefully
- **Error Recovery:** Tracks failed uploads and provides detailed error reporting

## Usage

```bash
uv run python apps/confluence_analyzer/main.py
```

## Configuration

Set these environment variables in `.env`:

**GitHub Configuration (Required):**
- `GITHUB_APP_ID` - Your GitHub App ID
- `GITHUB_INSTALLATION_ID` - Installation ID from the app's installation URL
- `GITHUB_PRIVATE_KEY_PATH` - Path to your GitHub App private key (.pem file)

**Organization (Optional):**
- `ORGANIZATION_NAME` - Specific organization to analyze (leave blank to analyze all accessible organizations)

**Confluence Configuration (Required):**
- `CONFLUENCE_URL` - Your Confluence instance URL (e.g., https://your-domain.atlassian.net/)
- `CONFLUENCE_USERNAME` - Confluence API username (usually your email)
- `CONFLUENCE_TOKEN` - Confluence API token (from user settings)
- `CONFLUENCE_DATABASE_PAGE_ID` - ID of the database page where data will be written
- `CONFLUENCE_FIELD_IDS` - JSON mapping of field names to field IDs (see below)

**Output Configuration (Optional):**
- `OUTPUT_DIR` - Directory for output reports (default: output)
- `DEBUG_MODE` - Enable debug logging (default: False)

### Confluence Field IDs

You need to obtain the field IDs from your Confluence database. To find them:

1. Open your Confluence database page
2. Open browser developer tools (F12)
3. Look for API calls to find field IDs, or contact Confluence admin

Example field mapping in `.env`:

```ini
CONFLUENCE_FIELD_IDS={
  "Utente": "cf17870d-c99a-56da-9729-7259b9a8a0f3",
  "ORGANIZATION NAME": "3f559efa-b2d3-5031-b1f6-93a71be00888",
  "REPO NAME": "b652ea69-062f-4bce-abb2-3c8a6dadbecd",
  "LINK": "653c36a4-e1c2-49fa-9c16-c744849c2833"
}
```

## Output

Generates multiple output files:

1. **CSV Report:** `output/report_repository_TIMESTAMP.csv`
   - Comprehensive repository and access data
   - Compatible with spreadsheet applications

2. **Excel Report:** `output/report_repository_TIMESTAMP.xlsx`
   - Formatted spreadsheet with columns and sizing
   - Full dataset with repository metadata

3. **Confluence Database:**
   - Direct integration with your Confluence database
   - Each row represents one user's access to a repository
   - Real-time synchronization

## Example

```bash
# Run with default settings
uv run python apps/confluence_analyzer/main.py

# Run with debug output
uv run env DEBUG_MODE=True python apps/confluence_analyzer/main.py

# Analyze specific organization
uv run env ORGANIZATION_NAME=MyOrg python apps/confluence_analyzer/main.py
```

## Output Format

The analyzer denormalizes data into rows with the following columns:

| Field | Description |
|-------|-------------|
| Utente | Username of the collaborator with write access |
| ORGANIZATION NAME | GitHub organization name |
| REPO NAME | Repository name |
| LINK | Direct link to the repository |
| Descrizione | Repository description |
| Accesso | Type of access (push, pull, admin) |

## Rate Limiting

The analyzer monitors GitHub API rate limits and automatically waits when necessary:
- Checks remaining API calls before each request
- Pauses if less than 100 calls remain
- Resumes automatically after rate limit reset

## Error Handling

The tool provides detailed error reporting:
- Failed Confluence API writes are logged with HTTP status codes
- Missing field IDs are reported clearly
- Database sync failures don't stop the analysis process
- All errors are recorded for troubleshooting

## Use Cases

- **Access Audits:** Review who has access to critical repositories
- **Compliance Reporting:** Generate access reports for regulatory requirements
- **Knowledge Base:** Maintain a Confluence database of all GitHub access
- **Team Onboarding:** Quickly see what repositories teams have access to
- **Permission Management:** Track and manage repository permissions centrally

## See Also

- [Main Analyzer](../main_analyzer/README.md) - Repository metrics analysis
- [Owner Analyzer](../owner_analyzer/README.md) - Team structure analysis
- [commons/auth](../../commons/auth/README.md) - Authentication details

## Troubleshooting

### "Token not valid" Error
- Verify your GitHub token in `.env`
- Ensure your token has the correct scopes

### Confluence API Errors
- Verify your Confluence credentials and token
- Check that field IDs match your database structure
- Ensure your token has write permissions to the database

### Rate Limit Issues
- Wait for the rate limit reset time shown in the output
- Consider running during off-peak hours for large organizations

## Development

To extend this analyzer:

1. **Add new fields:** Update `CONFLUENCE_FIELD_IDS` and corresponding DataFrame columns
2. **Change report format:** Modify the DataFrame structure in `confluence_analyzer.py`
3. **Add filters:** Implement repository filtering logic in the `get_repo_details()` method
