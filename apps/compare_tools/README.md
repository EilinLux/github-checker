# Compare Tools

Analyzes and compares permission reports to identify access control anomalies and inconsistencies.

## Features

- Compares main analysis reports with team reports
- Identifies implicit vs. explicit repository access
- Highlights owners with only organization-level access
- Flags non-owners with direct repository access
- Interactive file selection
- Detailed console output

## Available Tools

### compare.py
Analyzes permission differences between organization owners and direct collaborators.

Compares three user lists:
1. **Organization owners** (admin role at org level)
2. **Repository collaborators** (direct access)
3. **Team members** (access via team membership)

Reports findings as:
- Owners with implicit access only (org-level only)
- Non-owners with explicit access (via team or direct collaboration)

## Usage

```bash
# Run the compare tool (interactive)
uv run python apps/compare_tools/compare.py
```

## Workflow

1. Runs main analysis first:
   ```bash
   uv run python apps/main_analyzer/main.py
   ```

2. Runs team analysis:
   ```bash
   uv run python apps/owner_analyzer/owner_analyzer.py
   ```

3. Then compares the two reports:
   ```bash
   uv run python apps/compare_tools/compare.py
   ```
   - Prompts for main report file: `output/github_report_AGGREGATED_*.xlsx`
   - Prompts for team report file: `output/github_TEAMS_report_*.xlsx`

## Output

Console output with three sections:

**1. Full Owner List**
- All organization owners found across analyzed organizations

**2. Implicit Access Owners**
- Owners with admin privileges only from organization membership
- No explicit team or collaborator assignment
- Indicates potential access control gaps

**3. Non-Owner Explicit Access**
- Users with repository access who are not organization owners
- Access via team membership or direct collaboration
- Shows delegation patterns

## Example Output

```
--- 1. Elenco Completo Proprietari (Tutta la Lista A) ---
ℹ️ Info: Trovati 15 Proprietari (admin) totali per le organizzazioni analizzate:
   1. user-1
   2. user-2
   ...

--- 2. Proprietari con Accesso Implicito (A - (B U C)) ---
🔥 ATTENZIONE: Trovati 3 Proprietari con Accesso Implicito:
   1. implicit-owner-1
   2. implicit-owner-2
   ...

--- 3. Accesso Esplicito (Non-Proprietari) ((B U C) - A) ---
ℹ️ Info: Trovati 8 utenti con Accesso Esplicito che NON sono Proprietari:
   1. contractor-1
   2. team-member-2
   ...
```

## Use Cases

- Auditing access control compliance
- Identifying access control policy violations
- Finding owners who are over-privileged
- Understanding contractor/external access
- Security reviews and governance

## Troubleshooting

**"File not found"**
- Ensure the Excel report files exist in the `output/` directory
- Run main_analyzer and owner_analyzer first to generate reports

**"Sheet not found"**
- Verify the report contains:
  - Main report: `Report_Organizzazioni` and `Report_Repositories` sheets
  - Team report: `Report_Teams` sheet

**"No data found"**
- Ensure the Excel files contain data
- Check that the column names match expected format

## See Also

- [Main Analyzer](../main_analyzer/README.md) - Generate main reports
- [Owner Analyzer](../owner_analyzer/README.md) - Generate team reports
- [QUICKSTART.md](../../QUICKSTART.md#-compare-tools---permission-comparison) - Quick start guide
