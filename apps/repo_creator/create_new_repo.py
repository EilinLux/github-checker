import os
import sys
import time
import jwt  # pip install PyJWT
import requests
from dotenv import load_dotenv

# --- 1. Load Configuration ---
load_dotenv()
APP_ID = os.getenv("GITHUB_APP_ID")
KEY_PATH = os.getenv("GITHUB_PRIVATE_KEY_PATH", "./config.pem")
INSTALLATION_ID = os.getenv("GITHUB_INSTALLATION_ID")
ORG_NAME = os.getenv("REPO_CREATOR_ORG_NAME")

# Config for the NEW Repository (from .env)
NEW_REPO_CONFIG = {
    "name": os.getenv("REPO_CREATOR_NAME", "new-repository"),
    "description": os.getenv("REPO_CREATOR_DESCRIPTION", "Repository created by automation"),
    "private": os.getenv("REPO_CREATOR_PRIVATE", "true").lower() == "true",
    "has_issues": True,
    "auto_init": False
}

def load_private_key():
    try:
        with open(KEY_PATH, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Private key not found at {KEY_PATH}")
        sys.exit(1)

# --- 2. Generate JWT (Your existing logic) ---
def generate_app_jwt(app_id, private_key):
    now = int(time.time())
    payload = {
        'iat': now - 60,
        'exp': now + (10 * 60),
        'iss': app_id
    }
    return jwt.encode(payload, private_key, algorithm='RS256')

# --- 3. Get Installation Access Token (New Logic) ---
def get_installation_access_token(jwt_token, installation_id):
    """
    Exchanges the JWT for a token specific to this Installation ID.
    """
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json"
    }
    
    response = requests.post(url, headers=headers)
    
    if response.status_code == 201:
        token_data = response.json()
        print("✅ Successfully acquired Installation Access Token")
        return token_data["token"]
    else:
        print(f"❌ Failed to get access token: {response.status_code}")
        print(response.json())
        sys.exit(1)

# --- 4. Create Repository (New Logic) ---
def create_repository(access_token, org_name, repo_config):
    """
    Creates a repository in the Organization using the Access Token.
    """
    url = f"https://api.github.com/orgs/{org_name}/repos"
    
    headers = {
        "Authorization": f"Token {access_token}", # Note: 'Token' or 'Bearer' works here
        "Accept": "application/vnd.github+json"
    }
    
    print(f"Attempting to create repo '{repo_config['name']}' in org '{org_name}'...")
    
    response = requests.post(url, headers=headers, json=repo_config)
    
    if response.status_code == 201:
        data = response.json()
        print(f"\n🚀 Success! Repository created.")
        print(f"URL: {data['html_url']}")
        print(f"Clone URL: {data['clone_url']}")
    else:
        print(f"\n❌ Failed to create repository: {response.status_code}")
        print(response.json())

# --- Main Execution ---
if __name__ == "__main__":
    # Validate Inputs
    if not all([APP_ID, INSTALLATION_ID, ORG_NAME]):
        print("Error: Missing required variables in .env file:")
        print("  - GITHUB_APP_ID")
        print("  - GITHUB_INSTALLATION_ID")
        print("  - REPO_CREATOR_ORG_NAME")
        print("\nAlso configure repository details:")
        print("  - REPO_CREATOR_NAME (optional, defaults to 'new-repository')")
        print("  - REPO_CREATOR_DESCRIPTION (optional)")
        print("  - REPO_CREATOR_PRIVATE (optional, defaults to 'true')")
        sys.exit(1)

    print(f"Creating repository in organization: {ORG_NAME}")
    print(f"Repository name: {NEW_REPO_CONFIG['name']}")
    print(f"Visibility: {'Private' if NEW_REPO_CONFIG['private'] else 'Public'}")
    print()

    # 1. Sign JWT
    private_key = load_private_key()
    jwt_token = generate_app_jwt(APP_ID, private_key)

    # 2. Get Access Token
    access_token = get_installation_access_token(jwt_token, INSTALLATION_ID)

    # 3. Create Repo
    create_repository(access_token, ORG_NAME, NEW_REPO_CONFIG)