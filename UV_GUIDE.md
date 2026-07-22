# uv Package Manager Guide

This project uses **uv** for dependency and Python version management. This guide explains how to use `uv` effectively.

## What is uv?

`uv` is a fast Python package installer and resolver written in Rust. It replaces `pip`, `venv`, and `pipenv` with a single, unified tool.

**Key benefits:**
- ⚡ **10-100x faster** than pip
- 🔄 **No need to manage virtual environments manually** - uv does it automatically
- 🐍 **Automatic Python installation** - if Python isn't installed, uv installs it for you
- 📦 **Deterministic builds** - uses `uv.lock` for reproducible environments
- 🚀 **Modern Python tooling** - integrates with `pyproject.toml`

## Installation

### macOS/Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows (PowerShell)
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Homebrew (macOS)
```bash
brew install uv
```

### Using pip (if Python exists)
```bash
pip install uv
```

### Verify Installation
```bash
uv --version
```

## Basic Commands

### Install Project Dependencies
```bash
uv sync
```
This command:
- Installs Python 3.8+ (if not found)
- Creates/updates the virtual environment (`.venv/`)
- Installs all dependencies from `pyproject.toml`
- Generates `uv.lock` for reproducibility

### Run Python Scripts
```bash
# Run a script with dependencies available
uv run python apps/main_analyzer/main.py

# Run with environment variables
uv run env GITHUB_ORGANIZATION_NAME=my-org python apps/main_analyzer/main.py
```

### Install Additional Packages
```bash
# Add a new dependency
uv add requests

# Add a development dependency
uv add --dev pytest
```

### View Installed Packages
```bash
uv pip list
```

### Update Dependencies
```bash
# Update all dependencies
uv sync --upgrade

# Update specific package
uv add --upgrade requests
```

### Remove Dependencies
```bash
uv remove requests
```

## Project-Specific Usage

### First Time Setup
```bash
# 1. Clone the project
cd github-checker

# 2. Install everything (Python + dependencies)
uv sync

# 3. Configure credentials
cp .env.example .env
nano .env  # Add your GitHub App credentials

# 4. Run the analyzer
uv run python apps/main_analyzer/main.py
```

### Regular Usage
```bash
# Main analyzer
uv run python apps/main_analyzer/main.py

# With environment variables (override .env)
uv run env GITHUB_ORGANIZATION_NAME=my-org python apps/main_analyzer/main.py

# Owner analyzer
uv run python apps/owner_analyzer/owner_analyzer.py

# Comparison tools
uv run python apps/compare_tools/compare.py

# Create new repository
uv run python apps/repo_creator/create_new_repo.py
```

### Development & Testing
```bash
# Install with development dependencies
uv sync --extra dev

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=commons --cov=apps

# Format code
uv run black .

# Lint code
uv run flake8 .

# Type checking
uv run mypy commons apps
```

## Virtual Environment Management

### Automatic Virtual Environment
`uv` automatically creates and manages `.venv/` in your project directory.

```bash
# View .venv location
uv python --version

# Activate manually (optional - uv run handles this)
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate      # Windows

# Deactivate
deactivate
```

### Python Version Management
```bash
# Use specific Python version
uv sync --python 3.10

# Set default Python for project
# Add to pyproject.toml:
# [tool.uv]
# python-version = "3.10"

# List available Python versions
uv python list
```

## uv.lock File

The `uv.lock` file is **automatically generated** and contains exact versions of all dependencies.

**Why it matters:**
- Ensures reproducible builds across machines
- Should be committed to version control (git)
- Automatically updated when you use `uv add` or `uv sync --upgrade`

```bash
# Never edit uv.lock manually - it's auto-generated

# To update lock file (without installing)
uv lock --upgrade
```

## Configuration (pyproject.toml)

This project uses `pyproject.toml` for dependency management. Key sections:

```toml
[project]
name = "github-checker"
version = "1.0.0"
requires-python = ">=3.8"
dependencies = [
    "pygithub>=1.55",
    "pandas>=1.3.0",
    # ... more dependencies
]

[project.optional-dependencies]
dev = [
    "pytest>=6.2.0",
    "black>=21.6b0",
    # ... dev dependencies
]
```

To use optional dependencies:
```bash
uv sync --extra dev
```

## Troubleshooting

### Python Not Found
```bash
# uv should auto-install Python
uv sync

# If it doesn't, manually specify
uv sync --python 3.10
```

### Dependency Conflicts
```bash
# Clear cache and reinstall
rm -rf .venv
uv sync
```

### Specific Package Version
```bash
# Add with specific version
uv add "requests==2.28.0"

# Update to latest
uv add --upgrade requests
```

### Check Python Environment
```bash
# See which Python is being used
uv python --version

# Verify venv location
ls -la .venv
```

### Virtual Environment Issues
```bash
# Recreate .venv
rm -rf .venv
uv sync

# Or force recreation
uv venv --python 3.10
```

## Comparison: Before vs After

| Task | Old (pip/venv) | New (uv) |
|------|----------------|----------|
| Create environment | `python -m venv venv` | (automatic) |
| Activate | `source venv/bin/activate` | (unnecessary) |
| Install deps | `pip install -r requirements.txt` | `uv sync` |
| Run script | `python script.py` | `uv run python script.py` |
| Add package | `pip install requests` | `uv add requests` |
| Update all | `pip install -r requirements.txt --upgrade` | `uv sync --upgrade` |

## Advanced Topics

### Workspace Management
```bash
# uv supports monorepos - see https://docs.astral.sh/uv/concepts/workspaces/
```

### Python Installation Caching
```bash
# uv caches downloaded Python versions
# Location: ~/.cache/uv (on Unix) or %APPDATA%\uv (on Windows)

# Clear cache if needed
rm -rf ~/.cache/uv
```

### Build System
```bash
# Build project wheel
uv build

# Build sdist
uv build --sdist
```

## Performance Tips

1. **Use uv.lock**: Commit it to git for faster CI/CD builds
2. **Parallel installation**: uv installs packages in parallel by default
3. **Cache Python**: First install downloads Python, subsequent uses are cached
4. **Use --upgrade sparingly**: Only when you need latest versions

## Resources

- **Official Docs**: https://docs.astral.sh/uv/
- **GitHub Repository**: https://github.com/astral-sh/uv
- **Comparison to Other Tools**: https://docs.astral.sh/uv/pip/

## Getting Help

```bash
# View all commands
uv --help

# Help for specific command
uv sync --help
uv add --help
uv run --help
```

---

**For this project:**
- Use `uv sync` for first-time setup
- Use `uv run python <script>` to run applications
- Use `uv add` to add new dependencies
- Always commit `uv.lock` to version control
