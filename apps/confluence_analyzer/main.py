#!/usr/bin/env python3
"""
Confluence Analyzer - Main Entry Point

Analyzes GitHub repositories and synchronizes access permissions to Confluence Database.

Usage:
    uv run python apps/confluence_analyzer/main.py

Configuration:
    Set environment variables in .env file:
    - GITHUB_TOKEN: GitHub API token
    - ORGANIZATION_NAME: (optional) Specific organization to analyze
    - CONFLUENCE_URL: Confluence instance URL
    - CONFLUENCE_USERNAME: Confluence API username
    - CONFLUENCE_TOKEN: Confluence API token
    - CONFLUENCE_DATABASE_PAGE_ID: Database page ID
    - CONFLUENCE_FIELD_IDS: JSON mapping of field names to IDs
    - DEBUG_MODE: Enable debug logging (optional)
    - OUTPUT_DIR: Output directory for reports (optional)
"""
import os
import sys
import json
import traceback
from dotenv import load_dotenv

from confluence_analyzer import ConfluenceRepositoryAnalyzer


def main():
    """Main entry point for Confluence Analyzer."""
    # Load environment variables
    load_dotenv()

    # Get configuration from environment
    github_token = os.getenv("GITHUB_TOKEN")
    organization_name = os.getenv("ORGANIZATION_NAME", "")
    confluence_url = os.getenv("CONFLUENCE_URL")
    confluence_username = os.getenv("CONFLUENCE_USERNAME")
    confluence_token = os.getenv("CONFLUENCE_TOKEN")
    confluence_database_id = os.getenv("CONFLUENCE_DATABASE_PAGE_ID")
    confluence_field_ids_str = os.getenv("CONFLUENCE_FIELD_IDS", "{}")
    debug_mode = os.getenv("DEBUG_MODE", "False").lower() == "true"

    # Validate required configuration
    if not github_token:
        print("❌ FATAL: GITHUB_TOKEN not found in environment variables.")
        print("   Please set it in .env file")
        sys.exit(1)

    if not confluence_url or not confluence_username or not confluence_token:
        print("❌ FATAL: Missing Confluence configuration.")
        print("   Required: CONFLUENCE_URL, CONFLUENCE_USERNAME, CONFLUENCE_TOKEN")
        sys.exit(1)

    if not confluence_database_id:
        print("❌ FATAL: CONFLUENCE_DATABASE_PAGE_ID not found.")
        print("   Please set it in .env file")
        sys.exit(1)

    # Parse field IDs
    try:
        confluence_field_ids = json.loads(confluence_field_ids_str)
    except json.JSONDecodeError:
        print("❌ FATAL: CONFLUENCE_FIELD_IDS is not valid JSON.")
        print(f"   Value: {confluence_field_ids_str}")
        sys.exit(1)

    # Corretto con gli SPAZI invece degli UNDERSCORE per combaciare con i nomi reali
    required_fields = {"Utente", "ORGANIZATION NAME", "REPO NAME", "LINK"}

    if not required_fields.issubset(confluence_field_ids.keys()):
        missing = required_fields - set(confluence_field_ids.keys())
        print("❌ FATAL: Missing required field IDs in CONFLUENCE_FIELD_IDS.")
        print(f"   Missing: {missing}")
        print(f"   Found: {set(confluence_field_ids.keys())}")
        sys.exit(1)

    try:
        # Initialize analyzer
        print("=== Confluence GitHub Repository Analyzer ===\n")
        analyzer = ConfluenceRepositoryAnalyzer(
            token=github_token,
            organization_name=organization_name if organization_name else None,
            debug=debug_mode
        )

        # Analyze repositories and export
        print("Starting GitHub analysis...\n")
        df_filtered = analyzer.get_repo_details()

        if not df_filtered.empty:
            # Write to Confluence Database
            analyzer.write_to_confluence_database(
                df_filtered,
                confluence_database_id,
                confluence_field_ids
            )
            print("\n✅ Analysis and sync completed successfully!")
        else:
            print("\n⚠️ No repositories found for analysis.")

    except ValueError as e:
        print(f"\n❌ FATAL CONFIGURATION ERROR:\n{e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR:\n{traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main()
