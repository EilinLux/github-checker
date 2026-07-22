# Excel Writer Module

Utility for writing pandas DataFrames to formatted Excel files with automatic column sizing.

## Features

- **Multi-sheet Support**: Write multiple DataFrames as separate sheets in one workbook
- **Auto Column Sizing**: Automatically adjusts column widths based on content
- **Date-based Filenames**: Generate timestamped output files for easy organization
- **Error Handling**: Graceful error handling with detailed error messages

## Usage

### Basic Example

```python
from commons.excel_writer import get_output_filepath, write_excel_report
import pandas as pd

# Create sample data
org_df = pd.DataFrame({
    'Organization': ['org1', 'org2'],
    'Repos Count': [10, 15]
})

repo_df = pd.DataFrame({
    'Repository': ['repo1', 'repo2'],
    'Language': ['Python', 'JavaScript']
})

# Prepare multiple sheets
dfs_to_write = {
    'Report_Organizations': org_df,
    'Report_Repositories': repo_df
}

# Get output path with timestamp
output_file = get_output_filepath('reports')

# Write the Excel file
write_excel_report(dfs_to_write, output_file)
```

## Functions

### `get_output_filepath(output_dir)`
Generate a unique timestamped filepath for the report.

**Parameters:**
- `output_dir` (str): Directory where the file will be saved

**Returns:** Full file path with timestamp (e.g., `reports/github_report_AGGREGATED_20240722_153045.xlsx`)

**Side Effect:** Creates the output directory if it doesn't exist

### `write_excel_report(dfs_to_write, output_file)`
Write multiple DataFrames to an Excel file as separate sheets.

**Parameters:**
- `dfs_to_write` (dict): Dictionary mapping sheet names to pandas DataFrames
- `output_file` (str): Full path where the Excel file will be saved

**Features:**
- Skips empty DataFrames automatically
- Sets column widths based on content length (max 75 characters)
- Adds padding for readability
- Prints progress information

## Dependencies

- pandas
- xlsxwriter

## Notes

- Column widths are capped at 75 characters to prevent excessive width
- Empty DataFrames are skipped with a warning
- All column names become sheet headers in the Excel file
- The function preserves the order of sheets as specified in the dictionary
