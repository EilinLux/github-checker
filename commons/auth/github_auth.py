import time
import jwt
import requests
from github import Github
import sys


def get_github_app_jwt(app_id, private_key_path):
    """Generates the JWT for GitHub App authentication."""
    try:
        with open(private_key_path, 'r') as f:
            private_key = f.read()
    except FileNotFoundError:
        print(f"ERROR: Private key file not found at {private_key_path}")
        sys.exit(1)

    payload = {
        "iat": int(time.time()),
        "exp": int(time.time()) + (10 * 60),
        "iss": app_id
    }

    try:
        token = jwt.encode(payload, private_key, algorithm="RS256")
        return token
    except Exception as e:
        print(f"Error encoding JWT: {e}")
        sys.exit(1)


def get_all_org_installations(app_id, private_key_path):
    """Fetches all organization installations for the GitHub App."""
    jwt_token = get_github_app_jwt(app_id, private_key_path)

    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    url = "https://api.github.com/app/installations"
    print("Fetching all app installations from GitHub API...")

    org_installations = []

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        installations = response.json()
        print(f"Found {len(installations)} total installations.")

        for inst in installations:
            if inst.get("account", {}).get("type") == "Organization":
                org_installations.append({
                    "id": inst["id"],
                    "org_name": inst["account"]["login"]
                })

        print(f"Found {len(org_installations)} organization installations.")
        return org_installations

    except requests.exceptions.RequestException as e:
        print(f"ERROR during API call: {e}")
        if e.response is not None:
            print(f"Error details: {e.response.text}")
        sys.exit(1)


def load_private_key(path):
    """Load private key from file."""
    try:
        with open(path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(f"ERROR: Private key file not found at: {path}")
        raise
    except Exception as e:
        print(f"ERROR: Could not read private key: {e}")
        raise


def generate_app_jwt(app_id, private_key):
    """Generate JWT for GitHub App authentication."""
    payload = {
        'iat': int(time.time()),
        'exp': int(time.time()) + (10 * 60),
        'iss': app_id
    }
    return jwt.encode(payload, private_key, algorithm='RS256')


def get_installation_token(app_id, private_key_content, installation_id):
    """Get temporary access token for a specific GitHub App installation."""
    print("Generating GitHub installation token...")
    _jwt = generate_app_jwt(app_id, private_key_content)

    headers = {
        'Authorization': f'Bearer {_jwt}',
        'Accept': 'application/vnd.github.v3+json'
    }
    url = f'https://api.github.com/app/installations/{installation_id}/access_tokens'

    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        token = response.json()["token"]
        print("Installation token obtained successfully.")
        return token
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Could not obtain installation token. Details: {e}")
        if e.response is not None:
            print(f"Response: {e.response.text}")
        raise


def get_github_client(app_id, private_key_path, installation_id):
    """Create and return authenticated PyGithub client using GitHub App credentials."""
    private_key = load_private_key(private_key_path)
    token = get_installation_token(app_id, private_key, installation_id)
    return Github(token)
