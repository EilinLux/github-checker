# Repository Creator

Creates new repositories in your GitHub organization programmatically using GitHub App authentication.

## Features

- Automated repository creation via GitHub App
- Full repository configuration support
- Public/private visibility control
- Issue tracking toggle
- Batch repository creation support
- Detailed creation feedback

## Usage

```bash
uv run python apps/repo_creator/create_new_repo.py
```

## Configuration

Set these environment variables in `.env`:

**Required:**
- `GITHUB_APP_ID` - Your GitHub App ID
- `GITHUB_INSTALLATION_ID` - Installation ID from the app's installation URL
- `GITHUB_PRIVATE_KEY_PATH` - Path to your GitHub App private key (.pem file)
- `REPO_CREATOR_ORG_NAME` - Target organization where repository will be created

**Repository Details:**
- `REPO_CREATOR_NAME` - Repository name (default: "new-repository")
- `REPO_CREATOR_DESCRIPTION` - Repository description (default: "Repository created by automation")
- `REPO_CREATOR_PRIVATE` - Visibility setting (default: "true", set to "false" for public)

## Example Configuration

```ini
# .env file
GITHUB_APP_ID=123456
GITHUB_INSTALLATION_ID=987654
GITHUB_PRIVATE_KEY_PATH=./config.pem
REPO_CREATOR_ORG_NAME=DataWave

# Repository to create
REPO_CREATOR_NAME=cloud-services
REPO_CREATOR_DESCRIPTION=Cloud infrastructure and services
REPO_CREATOR_PRIVATE=true
```

## Running the Creator

```bash
# Create repository with configured values
uv run python apps/repo_creator/create_new_repo.py

# Create multiple repositories (edit .env, run multiple times)
REPO_CREATOR_NAME=service-a uv run python apps/repo_creator/create_new_repo.py
REPO_CREATOR_NAME=service-b uv run python apps/repo_creator/create_new_repo.py
```

## Output

The script will:
1. Authenticate using your GitHub App credentials
2. Display the repository configuration being created
3. Create the repository in the specified organization
4. Return the repository URL and clone URL on success
5. Display detailed error messages if creation fails

## Use Cases

- Automating repository provisioning
- Bulk repository creation in CI/CD pipelines
- Standardized repository setup with consistent configuration
- Infrastructure-as-code repository management

## Troubleshooting

**"Missing required variables in .env"**
- Ensure all required variables are set in your `.env` file
- Check that `REPO_CREATOR_ORG_NAME` is spelled correctly

**"Private key not found"**
- Verify `GITHUB_PRIVATE_KEY_PATH` points to a valid .pem file
- Check file permissions: `ls -la config.pem`

**"Failed to create repository: 422"**
- Repository name may already exist in the organization
- Repository name may contain invalid characters
- Check organization permissions for the GitHub App

## See Also

- [Main Analyzer](../main_analyzer/README.md) - Repository analysis
- [commons/auth](../../commons/auth/README.md) - Authentication details
- [QUICKSTART.md](../../QUICKSTART.md#-repository-creator---automated-repo-creation) - Quick start guide
