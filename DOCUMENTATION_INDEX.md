# Documentation Index

Complete guide to all documentation in the GitHub Repository Analyzer project.

---

## 📖 Documentation by Category

### Project Overview & Setup

| Document | Time | Purpose | For Whom |
|----------|------|---------|----------|
| [README.md](README.md) | 5 min | Project overview and features | Everyone |
| [QUICKSTART.md](QUICKSTART.md) | 5 min | Get up and running in 5 minutes | New users |
| [SETUP.md](SETUP.md) | 15 min | Complete setup and configuration guide | New users, DevOps |
| [UV_GUIDE.md](UV_GUIDE.md) | 10 min | uv package manager usage and commands | Developers |
| [REORGANIZATION_SUMMARY.md](REORGANIZATION_SUMMARY.md) | 10 min | What changed in the reorganization | Current users |

### Architecture & Design

| Document | Audience | Purpose |
|----------|----------|---------|
| [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) | Developers | Complete architecture guide and module organization |
| [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) | Everyone | This file - navigation guide |

### Configuration

| Document | Audience | Purpose |
|----------|----------|---------|
| [config/README.md](config/README.md) | Users | Configuration options and available fields |
| [.env.example](.env.example) | Users | Environment variable template |

### Module Documentation

#### Shared Utilities (commons/)

| Module | Document | Purpose |
|--------|----------|---------|
| **auth** | [commons/auth/README.md](commons/auth/README.md) | GitHub App authentication |
| **excel_writer** | [commons/excel_writer/README.md](commons/excel_writer/README.md) | Excel report generation |

#### Applications (apps/)

| Application | Document | Purpose |
|-------------|----------|---------|
| **main_analyzer** | [apps/main_analyzer/README.md](apps/main_analyzer/README.md) | Repository analysis tool |
| **owner_analyzer** | [apps/owner_analyzer/README.md](apps/owner_analyzer/README.md) | Team analysis tool |
| **compare_tools** | [apps/compare_tools/README.md](apps/compare_tools/README.md) | Repository comparison |
| **repo_creator** | [apps/repo_creator/README.md](apps/repo_creator/README.md) | Repository creation |

---

## 📍 Where to Find Information

### "I want to..."

#### Install and run the project
1. Read [QUICKSTART.md](QUICKSTART.md) (5 min)
2. Follow [SETUP.md](SETUP.md) (15 min)
3. Run `uv run python apps/main_analyzer/main.py`

#### Understand the code structure
1. Study [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
2. Check `commons/` for shared utilities
3. Check `apps/` for specific applications

#### Configure reports differently
1. Read [config/README.md](config/README.md)
2. Edit `config/output_fields.json`
3. Choose from available fields listed

#### Use authentication in my own code
1. Read [commons/auth/README.md](commons/auth/README.md)
2. See examples: `from commons.auth import get_github_client`

#### Export data to Excel
1. Read [commons/excel_writer/README.md](commons/excel_writer/README.md)
2. Use: `from commons.excel_writer import write_excel_report`

#### Analyze repository owners and teams
1. Read [apps/owner_analyzer/README.md](apps/owner_analyzer/README.md)
2. Run: `python apps/owner_analyzer/owner_analyzer.py`

#### Compare multiple repositories
1. Read [apps/compare_tools/README.md](apps/compare_tools/README.md)
2. Run: `python apps/compare_tools/compare.py`

#### Create repositories programmatically
1. Read [apps/repo_creator/README.md](apps/repo_creator/README.md)
2. Run: `python apps/repo_creator/create_new_repo.py`

#### See what changed from the old structure
1. Read [REORGANIZATION_SUMMARY.md](REORGANIZATION_SUMMARY.md)
2. Check migration table for old vs. new locations

#### Schedule regular analyses
1. Read [SETUP.md](SETUP.md#6-run-analysis) - Scheduling section
2. Follow cron (Linux/Mac) or Task Scheduler (Windows) instructions

#### Troubleshoot authentication issues
1. Read [SETUP.md](SETUP.md#troubleshooting) - Troubleshooting section
2. Check [commons/auth/README.md](commons/auth/README.md#security-notes)

#### Get security guidance
1. Read [SETUP.md](SETUP.md#security-best-practices)
2. Review [.gitignore](.gitignore)
3. Check file permissions with `chmod 600 config.pem`

---

## 🎯 Documentation Paths by User Type

### New User (First Time)
```
1. README.md (overview)
   ↓
2. QUICKSTART.md (5 min setup)
   ↓
3. Run first analysis
   ↓
4. config/README.md (customize)
```

### Experienced User (Been Here Before)
```
1. SETUP.md (step-by-step)
   ↓
2. .env.example (fill in credentials)
   ↓
3. Run python apps/main_analyzer/main.py
   ↓
4. Check output/
```

### Developer (Contributing)
```
1. PROJECT_STRUCTURE.md (architecture)
   ↓
2. commons/ READMEs (shared utilities)
   ↓
3. apps/ READMEs (applications)
   ↓
4. Create new module following patterns
```

### DevOps (Deploying)
```
1. SETUP.md (complete setup)
   ↓
2. QUICKSTART.md (operations reference)
   ↓
3. SETUP.md#6-run-analysis (scheduling)
   ↓
4. Monitor output/ directory
```

---

## 📋 Document Cross-References

### README.md references:
- Links to: SETUP.md, Project Structure
- Referenced by: Everything

### SETUP.md references:
- Links to: QUICKSTART.md, commons/auth, commons/excel_writer
- Referenced by: README, QUICKSTART

### QUICKSTART.md references:
- Links to: SETUP.md, apps/main_analyzer
- Referenced by: README, PROJECT_STRUCTURE

### PROJECT_STRUCTURE.md references:
- Links to: All commons/ and apps/ READMEs
- Referenced by: SETUP, QUICKSTART

### commons/auth/README.md references:
- Links to: .env.example
- Referenced by: SETUP, all app READMEs

### commons/excel_writer/README.md references:
- Links to: All app READMEs that generate reports
- Referenced by: SETUP, apps documentation

### config/README.md references:
- Links to: apps/main_analyzer/README.md
- Referenced by: SETUP, QUICKSTART

---

## 📊 Documentation Statistics

| Type | Count | Files |
|------|-------|-------|
| **Project Docs** | 6 | README, SETUP, QUICKSTART, PROJECT_STRUCTURE, REORGANIZATION_SUMMARY, UV_GUIDE |
| **Module Docs** | 6 | Auth, Excel, Main, Owner, Compare, Creator |
| **Config Docs** | 1 | config/README.md |
| **Templates** | 2 | .env.example, config examples |
| **Total** | 15 | Comprehensive documentation |

---

## 🔍 Finding Specific Information

### GitHub App Setup
→ [SETUP.md](SETUP.md#github-app-creation)

### Installation Steps
→ [SETUP.md](SETUP.md#project-installation)

### Configuration Options
→ [config/README.md](config/README.md)

### Available Output Fields
→ [config/README.md](config/README.md#available-output-fields)

### Security Best Practices
→ [SETUP.md](SETUP.md#security-best-practices)

### Troubleshooting→ [SETUP.md](SETUP.md#troubleshooting)

### Module Architecture→ [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

### Using Shared Utilities→ [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md#how-to-use-each-component)

### Creating New Applications→ [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md#adding-new-features)

### Authentication API→ [commons/auth/README.md](commons/auth/README.md#functions)

### Excel Export API→ [commons/excel_writer/README.md](commons/excel_writer/README.md#functions)

---

## 📱 Command Reference

### Common Commands by Use Case

**First Setup (with uv):**
```bash
# Install dependencies (includes Python)
uv sync

# Copy environment template
cp .env.example .env

# Run main analysis
uv run python apps/main_analyzer/main.py
```

**Regular Use:**
```bash
# Run analysis
uv run python apps/main_analyzer/main.py

# Run comparison
uv run python apps/compare_tools/compare.py

# Run team analysis
uv run python apps/owner_analyzer/owner_analyzer.py
```

**Development:**
```bash
# Install with dev dependencies
uv sync --extra dev

# Run with debug output
uv run env DEBUG_MODE=True python apps/main_analyzer/main.py

# Run specific organization
uv run env GITHUB_ORGANIZATION_NAME=my-org python apps/main_analyzer/main.py

# Run tests
uv run pytest
```

**uv-Specific Commands:**
```bash
# Add a new dependency
uv add requests

# Update all dependencies
uv sync --upgrade

# View installed packages
uv pip list

# See uv help
uv --help
```

---

## ✅ Checklist for Getting Started

- [ ] Install `uv` from https://docs.astral.sh/uv/getting-started/installation/
- [ ] Read [README.md](README.md) (5 min)
- [ ] Read [QUICKSTART.md](QUICKSTART.md) (5 min)
- [ ] Read [UV_GUIDE.md](UV_GUIDE.md) (optional, 10 min)
- [ ] Run `uv sync` to install dependencies
- [ ] Create `.env` from `.env.example`
- [ ] Add GitHub App credentials to `.env`
- [ ] Run `uv run python apps/main_analyzer/main.py`
- [ ] Check `output/` for generated reports
- [ ] Read [config/README.md](config/README.md) for customization
- [ ] Read [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for architecture
- [ ] (Optional) Schedule regular runs with cron/Task Scheduler using `uv run`

---



 

**Version**: 1.0  
**Last Updated**: 2024  
**Status**: Complete and Ready to Use

---

## Next Steps

1. **Pick your starting point above** (based on time/role)
2. **Follow the recommended reading path**
3. **Run your first analysis**
4. **Customize as needed**
5. **Schedule regular reports**

Happy analyzing! 🚀
