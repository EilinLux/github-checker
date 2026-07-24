# Project Structure

Complete guide to the reorganized GitHub Repository Analyzer project.

## Directory Overview

```
github-checker/
│
├── README.md                      # Project overview
├── SETUP.md                       # Complete setup guide
├── PROJECT_STRUCTURE.md           # This file
├── requirements.txt               # Python dependencies
├── pyproject.toml                 # Python package configuration
│
├── .env.example                   # Environment variables template
├── .gitignore                     # Git ignore rules (security)
│
├── commons/                       # ⭐ SHARED UTILITIES (used by multiple apps)
│   ├── __init__.py
│   ├── auth/                      # GitHub App authentication
│   │   ├── __init__.py
│   │   ├── README.md
│   │   └── github_auth.py         # JWT, token, client creation
│   │
│   ├── excel_writer/              # Excel report generation
│   │   ├── __init__.py
│   │   ├── README.md
│   │   └── writer.py              # Multi-sheet Excel writing
│   │
│   └── github_api/                # GitHub API utilities (placeholder)
│       └── __init__.py
│
├── apps/                          # ⭐ APPLICATIONS (specific use cases)
│   ├── __init__.py
│   │
│   ├── main_analyzer/             # Main GitHub repository analyzer
│   │   ├── __init__.py
│   │   ├── README.md
│   │   ├── main.py                # Entry point
│   │   ├── github_analyzer.py      # RepoAnalyzer class
│   │   └── org_retrieval.py        # Organization discovery
│   │
│   ├── owner_analyzer/            # Owner & team analysis
│   │   ├── __init__.py
│   │   ├── README.md
│   │   └── owner_analyzer.py       # Team analysis logic
│   │
│   ├── confluence_analyzer/       # GitHub to Confluence sync
│   │   ├── __init__.py
│   │   ├── README.md
│   │   ├── main.py                # Entry point
│   │   ├── confluence_analyzer.py  # Repository analyzer logic
│   │   └── confluence_database_writer.py # Confluence API v2 writer
│   │
│   ├── compare_tools/             # Repository comparison
│   │   ├── __init__.py
│   │   ├── README.md
│   │   ├── compare.py             # Comparison logic
│   │   └── compare_excel.py        # Excel comparison reports
│   │
│   └── repo_creator/              # Repository creation
│       ├── __init__.py
│       ├── README.md
│       └── create_new_repo.py      # Repo creation utilities
│
├── config/                        # ⭐ CONFIGURATION FILES
│   ├── README.md
│   ├── output_fields.json         # Fields for reports (edit this)
│   ├── installations.yaml         # Organizations to analyze (auto-generated)
│   │
│   └── templates/                 # Configuration templates
│       ├── installations.example.yaml
│       └── output_fields.example.json
│
└── output/                        # Generated reports (git-ignored)
    ├── github_report_*.xlsx       # Excel reports
    └── [generated at runtime]
```

## How to Use Each Component

### Commons (Shared Utilities)

These are used by multiple applications:

```python
# Authentication (used by all apps)
from commons.auth import get_github_client
client = get_github_client(app_id, key_path, installation_id)

# Excel writing (used by multiple report generators)
from commons.excel_writer import write_excel_report
write_excel_report(dfs_dict, output_path)
```

### Apps (Specific Tools)

Each app is independent and has its own entry point. Use `uv run` to execute:

```bash
# Main analyzer
uv run python apps/main_analyzer/main.py

# Owner analysis
uv run python apps/owner_analyzer/owner_analyzer.py

# Confluence analyzer (GitHub to Confluence sync)
uv run python apps/confluence_analyzer/main.py

# Comparison tools
uv run python apps/compare_tools/compare.py
uv run python apps/compare_tools/compare_excel.py

# Repository creator
uv run python apps/repo_creator/create_new_repo.py
```

## File Organization Rules

### ✅ In commons/
- Code used by **2 or more applications**
- Authentication, utilities, helpers
- Shared business logic

### ✅ In apps/
- Application-specific entry points
- Single-use features
- Feature-specific logic
- Scripts that serve one purpose

### ✅ In config/
- User configuration files
- Example/template files
- Field definitions
- Installation lists

### ✅ In root
- Main README (overview)
- SETUP.md (installation guide)
- PROJECT_STRUCTURE.md (this file)
- .env.example (config template)
- requirements.txt (dependencies)
- pyproject.toml (package info)
- .gitignore (security)

## Key Principles

### 1. Security First
- All sensitive files are in `.gitignore`:
  - `.env` (credentials)
  - `*.pem` (private keys)
  - `config.pem` (GitHub App key)
  - `output/` (generated reports may contain sensitive data)

- Never commit:
  - Private keys
  - API tokens or credentials
  - Real configuration files

### 2. Modularity
- Each utility in `commons/` is self-contained
- Each app in `apps/` is independent
- Minimal dependencies between modules
- Clear import paths

### 3. Configuration
- All credentials go in `.env` (git-ignored)
- Configuration templates in `config/templates/`
- User edits only `config/output_fields.json` and creates `.env`

### 4. Reusability
- `commons/` code imported by multiple apps
- Utilities can be tested independently
- Functions have clear interfaces

## Usage Examples

### Example 1: Using auth module

```python
# In any app that needs GitHub authentication
from commons.auth import get_github_client
from dotenv import load_dotenv

load_dotenv()
client = get_github_client(
    app_id=os.getenv("GITHUB_APP_ID"),
    private_key_path=os.getenv("GITHUB_PRIVATE_KEY_PATH"),
    installation_id=os.getenv("GITHUB_INSTALLATION_ID")
)
```

### Example 2: Using excel_writer

```python
# In any app that generates reports
from commons.excel_writer import write_excel_report, get_output_filepath
import pandas as pd

df1 = pd.DataFrame(...)  # Organization data
df2 = pd.DataFrame(...)  # Repository data

output_file = get_output_filepath("output")
write_excel_report({
    "Organizations": df1,
    "Repositories": df2
}, output_file)
```

### Example 3: Creating a new app

```bash
# Create app directory
mkdir apps/my_new_tool
touch apps/my_new_tool/__init__.py
touch apps/my_new_tool/README.md
touch apps/my_new_tool/main.py

# Use shared utilities
# from commons.auth import ...
# from commons.excel_writer import ...
```

## Dependency Graph

```
commons/auth          ← All apps that need GitHub access
commons/excel_writer  ← All apps that generate reports
commons/github_api    ← (Placeholder for future API utilities)

├── apps/main_analyzer
├── apps/owner_analyzer
├── apps/compare_tools
└── apps/repo_creator
```

## Configuration Flow

```
.env.example (template)
    ↓
.env (user creates, git-ignored)
    ↓
commons/auth (reads credentials)
    ↓
All apps (use authenticated client)
```

## What's New vs. Old

### Before
```
github-checker/
├── main.py
├── github_analyzer.py
├── owner_analyzer.py
├── compare.py
├── utils/auth.py
├── utils/excel_writer.py
└── [many files at root level]
```

### After
```
github-checker/
├── commons/              ← Reusable code
│   ├── auth/
│   └── excel_writer/
├── apps/                ← Individual tools
│   ├── main_analyzer/
│   ├── owner_analyzer/
│   ├── compare_tools/
│   └── repo_creator/
├── config/              ← Configuration
│   ├── templates/
│   └── README.md
├── SETUP.md             ← Documentation
├── PROJECT_STRUCTURE.md ← This guide
└── pyproject.toml       ← Package info
```

## Adding New Features

### To add a new utility to commons/

1. Create directory: `commons/my_utility/`
2. Add files:
   - `__init__.py`
   - `README.md`
   - Implementation files
3. Import in `commons/__init__.py`
4. Document in this file

### To add a new application to apps/

1. Create directory: `apps/my_new_tool/`
2. Add files:
   - `__init__.py`
   - `README.md`
   - `main.py` (entry point)
   - Implementation files
3. Import commons utilities as needed
4. Update this file with details

## Documentation Files

Each module has its own README:

- `README.md` - Project overview
- `SETUP.md` - Installation and setup
- `PROJECT_STRUCTURE.md` - This file
- `commons/auth/README.md` - Auth module docs
- `commons/excel_writer/README.md` - Excel writer docs
- `apps/main_analyzer/README.md` - Main app docs
- `apps/owner_analyzer/README.md` - Owner analyzer docs
- `apps/compare_tools/README.md` - Comparison tools docs
- `apps/repo_creator/README.md` - Repo creator docs
- `config/README.md` - Configuration guide

## Next Steps

1. Read [SETUP.md](SETUP.md) for installation instructions
2. Copy `.env.example` to `.env` and fill in your credentials
3. Run `python apps/main_analyzer/main.py` to test
4. Customize `config/output_fields.json` for your needs
5. Review app-specific README files for advanced usage

---

**Version**: 1.0  
**Last Updated**: 2024
