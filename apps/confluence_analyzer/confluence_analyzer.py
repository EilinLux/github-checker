"""GitHub Repository Analyzer for Confluence - Analyzes repos and syncs to Confluence Database."""
import os
import sys
import time
import json
import traceback
from datetime import datetime

import pandas as pd
from github import Github, UnknownObjectException, RateLimitExceededException

from confluence_database_writer import ConfluenceV2DatabaseWriter


class ConfluenceRepositoryAnalyzer:
    """
    Analyzes GitHub repositories and writes access information to Confluence database.
    """

    def __init__(self, token, organization_name=None, debug=False):
        """
        Initialize the analyzer.

        Args:
            token: GitHub API token (PAT or from GitHub App)
            organization_name: Optional specific organization to analyze
            debug: Enable debug logging
        """
        if not token or "ghp_" not in token:
            raise ValueError("Please provide a valid GITHUB_TOKEN.")

        self.g = Github(token)
        self.repos_data = []
        self.debug = debug

        try:
            self.current_user = self.g.get_user().login
        except Exception:
            self.current_user = "Unknown User (Invalid Token)"

    def _log(self, message):
        """Log debug messages if debug mode is enabled."""
        if self.debug:
            print(f"[DEBUG:GITHUB] {datetime.now().strftime('%H:%M:%S')} - {message}")

    def _get_rate_limit(self):
        """
        Check GitHub API rate limit and wait if necessary.
        """
        print("Checking GitHub API rate limit...")

        try:
            core_limit = self.g.get_rate_limit().rate
        except AttributeError:
            core_limit = self.g.get_rate_limit().core

        # If less than 100 calls remaining, wait for reset
        if core_limit.remaining < 100:
            reset_time = core_limit.reset.timestamp()
            sleep_time = reset_time - time.time() + 5
            if sleep_time > 0:
                print(f"\n--- Rate limit reached. Waiting {int(sleep_time)} seconds... ---")
                time.sleep(sleep_time)
                print("--- Resuming analysis. ---")

        print(f"Remaining Core rate limit: {core_limit.remaining}")

    def _get_direct_collaborator_permissions(self, repo):
        """
        Extract direct collaborators and their permissions.

        Returns:
            Tuple of (read_list, write_list)
        """
        collaborators_read = []
        collaborators_write = []
        try:
            for user in repo.get_collaborators():
                permissions = user.permissions
                if permissions.push or permissions.admin:
                    collaborators_write.append(user.login)
                elif permissions.pull:
                    collaborators_read.append(user.login)
        except Exception:
            return ["N/A"], ["N/A"]

        return collaborators_read, collaborators_write

    def get_repo_details(self):
        """
        Collect repository details and denormalize data (one row per user-repo access).
        Exports to CSV and Excel formats.
        """
        self.repos_data = []
        repositories_to_analyze = []

        # Find repositories to analyze
        try:
            user = self.g.get_user()

            if os.getenv("ORGANIZATION_NAME"):
                print(f"Accessing specific organization: {os.getenv('ORGANIZATION_NAME')}...")
                org = self.g.get_organization(os.getenv("ORGANIZATION_NAME"))
                repositories_to_analyze.extend(list(org.get_repos()))
            else:
                print("Analyzing all accessible organizations and personal repositories...")
                for org in user.get_orgs():
                    try:
                        repositories_to_analyze.extend(list(org.get_repos()))
                    except Exception:
                        print(f"   ⚠️ Unable to access repos in {org.login} (insufficient permissions).")
                repositories_to_analyze.extend(list(user.get_repos(visibility='all')))

            print(f"Total unique repositories to analyze: {len(repositories_to_analyze)}")

        except Exception as e:
            raise ValueError(f"Error accessing GitHub/Organization: {e}")

        # Detailed analysis and denormalization
        for repo in repositories_to_analyze:
            try:
                self._get_rate_limit()
                self._log(f"Analyzing repository: {repo.full_name}")

                collaborators_read, collaborators_write = self._get_direct_collaborator_permissions(repo)

                writers_list = collaborators_write if collaborators_write else ['No Direct Collaborator']

                for each_writer in writers_list:
                    repo_info = {
                        "Utente Autenticato": self.current_user,
                        "Organizzazione": repo.organization.login if repo.organization else "User",
                        "Nome Repo": repo.name,
                        "Link (HTML)": f'<a href="{repo.html_url}" target="_blank">{repo.full_name}</a>',
                        "Link (Puro)": repo.html_url,
                        "Accesso": each_writer,
                        "Descrizione": repo.description or "-",
                    }
                    self.repos_data.append(repo_info)

            except RateLimitExceededException:
                print("\nFATAL: GitHub API rate limit exceeded. Please try again later.")
                break
            except Exception as e:
                print(f"ERROR analyzing {repo.full_name}: {e}")
                continue

        # Create DataFrame and export
        df_full = pd.DataFrame(self.repos_data)

        if not df_full.empty:
            # Export to CSV
            output_dir = os.getenv("OUTPUT_DIR", "output")
            os.makedirs(output_dir, exist_ok=True)

            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            csv_file = f"{output_dir}/report_repository_{timestamp}.csv"
            df_full.to_csv(csv_file, index=False)
            print(f"\n✅ CSV Report saved: {csv_file}")

            # Export to Excel
            excel_file = f"{output_dir}/report_repository_{timestamp}.xlsx"
            self._export_to_excel(df_full, excel_file)

            # Prepare filtered DataFrame for Confluence
            df_confluence = df_full[[
                "Accesso",
                "Organizzazione",
                "Nome Repo",
                "Link (Puro)"
            ]].copy()

            df_confluence.columns = ["Utente", "ORGANIZATION NAME", "REPO NAME", "LINK"]
            df_confluence.drop_duplicates(subset=["Utente", "REPO NAME", "ORGANIZATION NAME"], inplace=True)

            return df_confluence
        else:
            print("\n⚠️ No repositories found.")
            return pd.DataFrame()

    def _export_to_excel(self, df, output_file):
        """
        Export DataFrame to Excel with formatting.

        Args:
            df: DataFrame to export
            output_file: Output file path
        """
        try:
            with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='GitHub Report', index=False)

                workbook = writer.book
                worksheet = writer.sheets['GitHub Report']

                # Auto-adjust column widths
                for idx, col in enumerate(df.columns):
                    max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
                    max_len = min(max_len, 50)
                    worksheet.set_column(idx, idx, max_len)

            print(f"✅ Excel Report saved: {output_file}")
        except Exception as e:
            print(f"❌ Error saving Excel file: {traceback.format_exc()}")

    def write_to_confluence_database(self, df: pd.DataFrame, database_id: str, field_ids: dict):
        """
        Write DataFrame directly to Confluence database.

        Args:
            df: DataFrame with filtered columns
            database_id: Confluence database page ID
            field_ids: Mapping of field names to field IDs
        """
        if df.empty:
            print("\n⚠️ DataFrame is empty. No data to write to Confluence.")
            return

        print("\n--- Starting Write to Confluence Database (API V2) ---")
        try:
            writer = ConfluenceV2DatabaseWriter(
                url=os.getenv("CONFLUENCE_URL"),
                username=os.getenv("CONFLUENCE_USERNAME"),
                token=os.getenv("CONFLUENCE_TOKEN"),
                debug=self.debug
            )

            writer.write_database_rows(df, database_id, field_ids)

        except Exception as e:
            print(f"\n❌ CRITICAL ERROR during Confluence write: {traceback.format_exc()}")
