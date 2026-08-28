import os
import sys
from unittest.mock import patch

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".github", "scripts"))

from resource_to_csv import combine_tags, normalise_issue_refs, normalise_year, parse_issue, upsert_csv


class TestResourceToCSV:
    def test_parse_issue_complete(self):
        body = """### Resource Title
Example Policy

### URL
https://example.org/policy

### Organisation / Authors
Example Org

### Year
2026

### Type
Policy

### Relevance
Useful policy example.

### Tags
Governance
Research Integrity

### Other Tags
Local Practice

### Related Risks
#12, 48

### Notes
Useful for maintainers.
"""
        values = parse_issue(body)

        assert values["Resource Title"] == "Example Policy"
        assert values["URL"] == "https://example.org/policy"
        assert values["Organisation / Authors"] == "Example Org"
        assert values["Year"] == "2026"
        assert values["Type"] == "Policy"
        assert values["Relevance"] == "Useful policy example."
        assert values["Tags"] == "Governance, Research Integrity, Local Practice"
        assert values["Related Risks"] == "#12, #48"
        assert values["Notes"] == "Useful for maintainers."

    def test_parse_issue_accepts_legacy_authors_label(self):
        values = parse_issue("### Organisation / authors\nLegacy Org")

        assert values["Organisation / Authors"] == "Legacy Org"

    def test_combine_tags_deduplicates(self):
        assert combine_tags("Governance, Research Integrity", "Governance") == "Governance, Research Integrity"

    def test_normalise_issue_refs_deduplicates(self):
        assert normalise_issue_refs("12, #12\n48") == "#12, #48"

    def test_normalise_year_uses_latest_legacy_year(self):
        assert normalise_year("2023 (updated 2024, 2025)") == "2025"

    def test_upsert_csv_adds_resource_and_issue(self, tmp_path):
        csv_path = tmp_path / "resources.csv"
        values = {
            "Resource Title": "Example Policy",
            "URL": "https://example.org/policy",
            "Organisation / Authors": "Example Org",
            "Year": "2026",
            "Type": "Policy",
            "Relevance": "Useful policy example.",
            "Tags": "Governance",
            "Related Risks": "#12",
            "Notes": "",
        }

        with patch("resource_to_csv.CSV_PATH", str(csv_path)):
            upsert_csv(values, "123")

        dataframe = pd.read_csv(csv_path)
        assert len(dataframe) == 1
        assert dataframe.iloc[0]["Resource Title"] == "Example Policy"
        assert dataframe.iloc[0]["Issue"] == "#123"
        assert dataframe.iloc[0]["Related Risks"] == "#12"

    def test_upsert_csv_replaces_matching_url_and_preserves_metadata(self, tmp_path):
        csv_path = tmp_path / "resources.csv"
        pd.DataFrame(
            {
                "Resource Title": ["Old title"],
                "URL": ["https://example.org/policy/"],
                "Organisation / Authors": ["Old Org"],
                "Year": ["2025"],
                "Type": ["Policy"],
                "Relevance": ["Old relevance"],
                "Tags": ["Governance"],
                "Related Risks": [""],
                "Notes": [""],
                "Issue": ["#100"],
                "Maintainer Notes": ["Reviewed"],
            }
        ).to_csv(csv_path, index=False)
        values = {
            "Resource Title": "New title",
            "URL": "https://example.org/policy",
            "Organisation / Authors": "New Org",
            "Year": "2026",
            "Type": "Guidance",
            "Relevance": "New relevance",
            "Tags": "Research Integrity",
            "Related Risks": "#12",
            "Notes": "Updated",
        }

        with patch("resource_to_csv.CSV_PATH", str(csv_path)):
            upsert_csv(values, "200")

        dataframe = pd.read_csv(csv_path)
        assert len(dataframe) == 1
        assert dataframe.iloc[0]["Resource Title"] == "New title"
        assert dataframe.iloc[0]["Issue"] == "#100"
        assert dataframe.iloc[0]["Maintainer Notes"] == "Reviewed"
