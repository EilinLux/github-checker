# GitHub Authentication Module

Secure authentication utilities for GitHub App integration using JWT tokens.

## Features

- **JWT Token Generation**: Create signed JWT tokens for GitHub App authentication
- **Installation Token Retrieval**: Get temporary access tokens for specific GitHub App installations
- **PyGithub Client Creation**: Initialize authenticated PyGithub client automatically
- **Organization Discovery**: Fetch all organizations where the app is installed

## Usage

### Basic Authentication Flow

```python
from commons.auth import get_github_client

# Create authenticated client
client = get_github_client(
    app_id="YOUR_APP_ID",
    private_key_path="./config.pem",
    installation_id="YOUR_INSTALLATION_ID"
)

# Use the client
org = client.get_organization("your-org")
repos = org.get_repos()
```

### Get All Installations

```python
from commons.auth import get_all_org_installations

installations = get_all_org_installations(
    app_id="YOUR_APP_ID",
    private_key_path="./config.pem"
)
```

## Functions

### `get_github_client(app_id, private_key_path, installation_id)`
Creates and returns an authenticated PyGithub client.

**Parameters:**
- `app_id` (str): GitHub App ID
- `private_key_path` (str): Path to the private key .pem file
- `installation_id` (str): Installation ID of the app

**Returns:** PyGithub `Github` client object

### `get_installation_token(app_id, private_key_content, installation_id)`
Retrieves a temporary access token for a specific installation.

**Parameters:**
- `app_id` (str): GitHub App ID
- `private_key_content` (str): Content of the private key
- `installation_id` (str): Installation ID

**Returns:** Access token string

### `get_github_app_jwt(app_id, private_key_path)`
Generates a JWT token for GitHub App authentication.

**Parameters:**
- `app_id` (str): GitHub App ID
- `private_key_path` (str): Path to the private key .pem file

**Returns:** JWT token string

### `get_all_org_installations(app_id, private_key_path)`
Fetches all organizations where the GitHub App is installed.

**Returns:** List of installation dicts with `id` and `org_name`

## Configuration

See the root `.env.example` file for required environment variables:

```
GITHUB_APP_ID=<your_app_id>
GITHUB_PRIVATE_KEY_PATH=<path_to_pem_file>
GITHUB_INSTALLATION_ID=<installation_id>
```

## Security Notes

- Never commit `.pem` private key files to version control
- Keep the `.env` file with credentials out of repositories
- Use environment variables for all sensitive data
- The private key should have restrictive file permissions (600)
