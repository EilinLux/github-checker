import os
import pandas as pd
import traceback
from datetime import datetime


def get_output_filepath(output_dir):
    """
    Create a unique file path for the aggregated report.

    Args:
        output_dir (str): Directory to save the report

    Returns:
        str: Full file path for the Excel report
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"github_report_AGGREGATED_{timestamp}.xlsx"
    return os.path.join(output_dir, filename)


def write_excel_report(dfs_to_write: dict, output_file: str):
    """
    Write a dictionary of DataFrames to an Excel file with multiple sheets.

    Args:
        dfs_to_write (dict): Dictionary mapping sheet names to DataFrames
        output_file (str): Full path to the output .xlsx file

    Example:
        dfs_to_write = {
            'Report_Organizations': org_df,
            'Report_Repositories': repo_df
        }
        write_excel_report(dfs_to_write, 'output/report.xlsx')
    """
    print(f"\nWriting multi-sheet Excel report to: {output_file}")
    try:
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            for sheet_name, df in dfs_to_write.items():
                if df.empty:
                    print(f"Skipping empty sheet: {sheet_name}")
                    continue

                print(f"Writing sheet: '{sheet_name}' ({len(df)} rows)...")

                df.to_excel(writer, sheet_name=sheet_name, index=False)

                worksheet = writer.sheets[sheet_name]

                for idx, col in enumerate(df.columns):
                    series = df[col]

                    max_len_content = series.astype(str).map(len).max() or 0
                    max_len_header = len(str(col))
                    max_len = max(max_len_content, max_len_header) + 2
                    max_len = min(max_len, 75)

                    worksheet.set_column(idx, idx, max_len)

        print(f"Excel report written successfully.")

    except Exception as e:
        print(f"ERROR: Could not write Excel file. {e}")
        print(traceback.format_exc())
