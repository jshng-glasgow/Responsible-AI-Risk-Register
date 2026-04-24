import os
import sys
from unittest.mock import patch

import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".github", "scripts"))

from update_csv import combine_tags, normalise_issue_refs, parse_issue, update_csv_row


class TestUpdateCSV:
    def test_parse_issue_complete(self):
        body = """### Issue Number
#123

### Description
Updated risk description

### Likelihood
High

### Severity
Medium

### Reach
Low

### Mitigations
Updated mitigations

### Ownership
Updated owner

### Examples
Updated examples

### Related Risks
12
#27

### Tags
Economic, Governance

### Other Tags
Lab Practice
"""
        values = parse_issue(body)
        assert values["Issue Number"] == "#123"
        assert values["Description"] == "Updated risk description"
        assert values["Likelihood"] == "High"
        assert values["Severity"] == "Medium"
        assert values["Reach"] == "Low"
        assert values["Mitigations"] == "Updated mitigations"
        assert values["Ownership"] == "Updated owner"
        assert values["Examples"] == "Updated examples"
        assert values["Related Risks"] == "#12, #27"
        assert values["Tags"] == "Economic, Governance, Lab Practice"

    def test_parse_issue_none_values(self):
        body = """### Issue Number
#123

### Description
Updated risk

### Likelihood
None

### Severity
_No response_

### Reach
No changes

### Mitigations

### Ownership
None

### Examples
Examples

### Related Risks
No changes

### Tags
No changes

### Other Tags
"""
        values = parse_issue(body)
        assert values["Issue Number"] == "#123"
        assert values["Description"] == "Updated risk"
        assert values["Likelihood"] is None
        assert values["Severity"] is None
        assert values["Reach"] is None
        assert values["Mitigations"] is None
        assert values["Ownership"] is None
        assert values["Examples"] == "Examples"
        assert values["Related Risks"] is None
        assert values["Tags"] is None

    def test_combine_tags_deduplicates(self):
        assert combine_tags("Economic, Governance", "Governance, Lab Practice") == "Economic, Governance, Lab Practice"

    def test_normalise_issue_refs_deduplicates_and_formats(self):
        assert normalise_issue_refs("12, #12\n48") == "#12, #48"

    def test_update_csv_row_success(self, tmp_path):
        test_csv = tmp_path / "risks.csv"
        existing_df = pd.DataFrame(
            {
                "Issue Title": ["Original issue title"],
                "Description": ["Original risk"],
                "Likelihood": ["Low"],
                "Severity": ["High"],
                "Reach": ["Medium"],
                "Mitigations": ["Original mitigations"],
                "Ownership": ["Original owner"],
                "Examples": ["Original examples"],
                "Related Risks": ["#77"],
                "Tags": ["Environmental"],
                "Issue": ["#123"],
                "Updates": ["#123"],
                "Maintainer Notes": [""],
            }
        )
        existing_df.to_csv(str(test_csv), index=False)

        with patch("update_csv.CSV_PATH", str(test_csv)):
            values = {
                "Issue Number": "#123",
                "Description": "Updated risk",
                "Likelihood": None,
                "Severity": "Medium",
                "Reach": "Very High",
                "Mitigations": None,
                "Ownership": "Updated owner",
                "Examples": None,
                "Related Risks": "#77, #80",
                "Tags": "Governance, Software Sustainability",
            }
            update_csv_row(values, "999")

            df = pd.read_csv(str(test_csv))
            assert len(df) == 1
            assert df.iloc[0]["Description"] == "Updated risk"
            assert df.iloc[0]["Issue Title"] == "Original issue title"
            assert df.iloc[0]["Likelihood"] == "Low"
            assert df.iloc[0]["Severity"] == "Medium"
            assert df.iloc[0]["Reach"] == "Very High"
            assert df.iloc[0]["Mitigations"] == "Original mitigations"
            assert df.iloc[0]["Ownership"] == "Updated owner"
            assert df.iloc[0]["Examples"] == "Original examples"
            assert df.iloc[0]["Related Risks"] == "#77, #80"
            assert df.iloc[0]["Tags"] == "Governance, Software Sustainability"
            assert pd.isna(df.iloc[0]["Maintainer Notes"]) or df.iloc[0]["Maintainer Notes"] == ""
            assert "#999" in str(df.iloc[0]["Updates"])

    def test_update_csv_row_issue_not_found(self, tmp_path):
        test_csv = tmp_path / "risks.csv"
        existing_df = pd.DataFrame(
            {
                "Issue Title": ["Original issue title"],
                "Description": ["Original risk"],
                "Likelihood": ["Low"],
                "Severity": ["High"],
                "Reach": ["Medium"],
                "Mitigations": ["Original mitigations"],
                "Ownership": ["Original owner"],
                "Examples": ["Original examples"],
                "Related Risks": [""],
                "Tags": [""],
                "Issue": ["#123"],
                "Updates": ["#123"],
                "Maintainer Notes": [""],
            }
        )
        existing_df.to_csv(str(test_csv), index=False)

        with patch("update_csv.CSV_PATH", str(test_csv)):
            values = {"Issue Number": "#999", "Description": "Updated risk"}
            with pytest.raises(SystemExit):
                update_csv_row(values, "888")

    def test_update_csv_row_no_csv(self, tmp_path):
        test_csv = tmp_path / "nonexistent.csv"

        with patch("update_csv.CSV_PATH", str(test_csv)):
            values = {"Issue Number": "#123", "Description": "Updated risk"}
            with pytest.raises(SystemExit):
                update_csv_row(values, "777")

    def test_update_csv_row_nan_column(self, tmp_path):
        test_csv = tmp_path / "risks.csv"
        existing_df = pd.DataFrame(
            {
                "Issue Title": ["Original issue title"],
                "Description": ["Original risk"],
                "Likelihood": ["Low"],
                "Severity": ["High"],
                "Reach": ["Medium"],
                "Mitigations": ["Original mitigations"],
                "Ownership": ["Original owner"],
                "Examples": [None],
                "Related Risks": [None],
                "Tags": [""],
                "Issue": ["#123"],
                "Updates": ["#123"],
                "Maintainer Notes": [""],
            }
        )
        existing_df.to_csv(str(test_csv), index=False)

        with patch("update_csv.CSV_PATH", str(test_csv)):
            values = {
                "Issue Number": "#123",
                "Description": None,
                "Likelihood": None,
                "Severity": None,
                "Reach": None,
                "Mitigations": None,
                "Ownership": None,
                "Examples": "https://example.com/skills",
                "Related Risks": None,
                "Tags": None,
            }
            update_csv_row(values, "999")

            df = pd.read_csv(str(test_csv))
            assert len(df) == 1
            assert df.iloc[0]["Examples"] == "https://example.com/skills"
            assert df.iloc[0]["Updates"] == "#123, #999"

    def test_updates_column_tracking(self, tmp_path):
        test_csv = tmp_path / "risks.csv"
        existing_df = pd.DataFrame(
            {
                "Issue Title": ["Test issue title"],
                "Description": ["Test risk"],
                "Likelihood": ["High"],
                "Severity": ["Medium"],
                "Reach": ["Low"],
                "Mitigations": ["Initial mitigations"],
                "Ownership": ["Owner"],
                "Examples": ["Example"],
                "Related Risks": ["#90"],
                "Tags": ["Governance"],
                "Issue": ["#50"],
                "Updates": ["#50"],
                "Maintainer Notes": [""],
            }
        )
        existing_df.to_csv(str(test_csv), index=False)

        with patch("update_csv.CSV_PATH", str(test_csv)):
            values_1 = {
                "Issue Number": "#50",
                "Description": "Test risk updated",
                "Likelihood": None,
                "Severity": None,
                "Reach": None,
                "Mitigations": None,
                "Ownership": None,
                "Examples": None,
                "Related Risks": None,
                "Tags": None,
            }
            update_csv_row(values_1, "100")

            values_2 = {
                "Issue Number": "#50",
                "Description": "Test risk updated again",
                "Likelihood": None,
                "Severity": None,
                "Reach": None,
                "Mitigations": None,
                "Ownership": None,
                "Examples": None,
                "Related Risks": None,
                "Tags": None,
            }
            update_csv_row(values_2, "200")

            df = pd.read_csv(str(test_csv))
            assert len(df) == 1
            assert df.iloc[0]["Updates"] == "#50, #100, #200"
            assert df.iloc[0]["Description"] == "Test risk updated again"

    def test_updates_column_not_duplicated_on_rerun(self, tmp_path):
        test_csv = tmp_path / "risks.csv"
        existing_df = pd.DataFrame(
            {
                "Issue Title": ["Test issue title"],
                "Description": ["Test risk"],
                "Likelihood": ["High"],
                "Severity": ["Medium"],
                "Reach": ["Low"],
                "Mitigations": ["Initial mitigations"],
                "Ownership": ["Owner"],
                "Examples": ["Example"],
                "Related Risks": [""],
                "Tags": [""],
                "Issue": ["#50"],
                "Updates": ["#50, #100"],
                "Maintainer Notes": [""],
            }
        )
        existing_df.to_csv(str(test_csv), index=False)

        with patch("update_csv.CSV_PATH", str(test_csv)):
            values = {
                "Issue Number": "#50",
                "Description": "Test risk updated",
                "Likelihood": None,
                "Severity": None,
                "Reach": None,
                "Mitigations": None,
                "Ownership": None,
                "Examples": None,
                "Related Risks": None,
                "Tags": None,
            }
            update_csv_row(values, "100")

            df = pd.read_csv(str(test_csv))
            assert df.iloc[0]["Updates"] == "#50, #100"
