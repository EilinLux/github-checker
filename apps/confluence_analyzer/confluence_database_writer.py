"""Confluence V2 Database Writer - Writes data directly to Confluence Database via API v2."""
import json
from base64 import b64encode
from datetime import datetime
import traceback
import pandas as pd
import requests


class ConfluenceV2DatabaseWriter:
    """
    Writes rows directly to a Confluence database using REST API v2.
    Handles authentication and ADF (Atlassian Document Format) conversion.
    """

    def __init__(self, url, username, token, debug=False):
        """
        Initialize the Confluence Database Writer.

        Args:
            url: Base Confluence URL (e.g., https://your-domain.atlassian.net/)
            username: Confluence API username (usually email)
            token: Confluence API token
            debug: Enable debug logging
        """
        self.api_url = f"{url.rstrip('/')}/wiki/api/v2"

        auth_string = f"{username}:{token}"
        encoded_auth = b64encode(auth_string.encode()).decode('ascii')

        self.headers = {
            "Authorization": f"Basic {encoded_auth}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        self.debug = debug

    def _log(self, message):
        """Log debug messages if debug mode is enabled."""
        if self.debug:
            print(f"[DEBUG:V2_API] {datetime.now().strftime('%H:%M:%S')} - {message}")

    def _create_adf_text(self, text):
        """
        Convert a string to Atlassian Document Format (ADF).

        Args:
            text: Plain text to convert

        Returns:
            Dictionary in ADF format for Confluence API v2
        """
        return {
            "version": 1,
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": str(text)}]
                }
            ]
        }

    def write_database_rows(self, df: pd.DataFrame, database_id: str, field_ids: dict):
        """
        Write DataFrame rows to Confluence database.

        Args:
            df: DataFrame with columns matching field_ids keys
            database_id: ID of the target database page
            field_ids: Dictionary mapping field names to their IDs in Confluence
                      Expected keys: Utente, ORGANIZATION NAME, REPO NAME, LINK

        Returns:
            Tuple of (inserted_count, failed_count)
        """
        print(f"\n--- Starting Direct Write to Confluence Database (ID: {database_id}) ---")

        insert_count = 0
        failed_count = 0

        for index, row in df.iterrows():
            fields_data = {}
            try:
                # Map DataFrame columns to Confluence database fields using ADF
                fields_data[field_ids["Utente"]] = self._create_adf_text(row['Utente'])
                fields_data[field_ids["ORGANIZATION NAME"]] = self._create_adf_text(row['ORGANIZATION NAME'])
                fields_data[field_ids["REPO NAME"]] = self._create_adf_text(row['REPO NAME'])
                fields_data[field_ids["LINK"]] = self._create_adf_text(row['LINK'])

            except KeyError as e:
                print(f"❌ ERROR: Column {e} not found in DataFrame. Check your field configuration.")
                failed_count += 1
                continue

            # Build payload for API request
            payload = {
                "type": "database-row",
                "container": {"id": database_id, "type": "custom-content"},
                "fields": fields_data
            }

            # Send request to Confluence API
            try:
                response = requests.post(
                    f"{self.api_url}/custom-content",
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()

                insert_count += 1
                self._log(f"Row inserted for User: {row['Utente']}, Status: {response.status_code}")

            except requests.exceptions.HTTPError as err:
                failed_count += 1
                print(f"❌ HTTP Error for User {row['Utente']}. Status: {response.status_code}")
                self._log(f"API Response: {response.text}")
            except Exception as e:
                failed_count += 1
                print(f"❌ Unknown Error for User {row['Utente']}: {e}")

        print(f"\n✅ Write operation completed. Inserted: {insert_count}. Failed: {failed_count}.")
        if failed_count > 0:
            print("⚠️ Failures often indicate incorrect field IDs or insufficient token permissions.")

        return insert_count, failed_count
