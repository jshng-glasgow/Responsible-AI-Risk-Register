import os
import sys
from unittest.mock import patch

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".github", "scripts"))

from issue_to_csv import combine_tags, normalise_issue_refs, parse_issue, split_tags, upsert_csv


class TestIssueToCSV:
    def test_parse_issue_complete(self):
        body = """### Description
Test risk description

### Likelihood
High

### Severity
Medium

### Reach
Low

### Mitigations
Some mitigations

### Ownership
Test owner

### Examples
Test examples

### Related Risks
#12, 48

### Tags
Economic, Environmental

### Other Tags
Local Practice
"""
        values = parse_issue(body)
        assert values["Description"] == "Test risk description"
        assert values["Likelihood"] == "High"
        assert values["Severity"] == "Medium"
        assert values["Reach"] == "Low"
        assert values["Mitigations"] == "Some mitigations"
        assert values["Ownership"] == "Test owner"
        assert values["Examples"] == "Test examples"
        assert values["Related Risks"] == "#12, #48"
        assert values["Tags"] == "Economic, Environmental, Local Practice"

    def test_parse_issue_no_response(self):
        body = """### Description
Test risk

### Likelihood
_No response_

### Severity
Medium

### Reach
Unknown

### Mitigations


### Ownership
_No response_

### Examples
Examples

### Related Risks
_No response_

### Tags
_No response_

### Other Tags
"""
        values = parse_issue(body)
        assert values["Description"] == "Test risk"
        assert values["Likelihood"] == ""
        assert values["Severity"] == "Medium"
        assert values["Reach"] == "Unknown"
        assert values["Mitigations"] == ""
        assert values["Ownership"] == ""
        assert values["Examples"] == "Examples"
        assert values["Related Risks"] == ""
        assert values["Tags"] == ""

    def test_split_tags_supports_commas_and_newlines(self):
        assert split_tags("Economic, Environmental\nGovernance") == ["Economic", "Environmental", "Governance"]

    def test_combine_tags_deduplicates(self):
        assert combine_tags("Economic, Environmental", "Environmental, Local Practice") == "Economic, Environmental, Local Practice"

    def test_normalise_issue_refs_deduplicates_and_formats(self):
        assert normalise_issue_refs("12, #12\n48") == "#12, #48"

    def test_upsert_csv_new_file(self, tmp_path):
        test_csv = tmp_path / "risks.csv"

        with patch("issue_to_csv.CSV_PATH", str(test_csv)):
            values = {
                "Description": "Test risk",
                "Likelihood": "High",
                "Severity": "Medium",
                "Reach": "Low",
                "Mitigations": "Mitigations",
                "Ownership": "Owner",
                "Examples": "Examples",
                "Related Risks": "#20, #25",
                "Tags": "Environmental, Training and Development",
            }
            upsert_csv(values, "123", "Test issue title")

            df = pd.read_csv(str(test_csv))
            assert len(df) == 1
            assert df.iloc[0]["Description"] == "Test risk"
            assert df.iloc[0]["Issue Title"] == "Test issue title"
            assert df.iloc[0]["Issue"] == "#123"
            assert df.iloc[0]["Updates"] == "#123"
            assert df.iloc[0]["Reach"] == "Low"
            assert df.iloc[0]["Related Risks"] == "#20, #25"
            assert df.iloc[0]["Tags"] == "Environmental, Training and Development"
            assert pd.isna(df.iloc[0]["Maintainer Notes"]) or df.iloc[0]["Maintainer Notes"] == ""

    def test_upsert_csv_existing_issue_updates_tags_without_duplicates(self, tmp_path):
        test_csv = tmp_path / "risks.csv"
        existing_df = pd.DataFrame(
            {
                "Issue Title": [""],
                "Description": ["Existing risk"],
                "Likelihood": ["Low"],
                "Severity": ["High"],
                "Reach": ["Medium"],
                "Mitigations": ["Existing mitigations"],
                "Ownership": ["Existing owner"],
                "Examples": ["Existing examples"],
                "Related Risks": ["#11"],
                "Tags": ["Environmental"],
                "Issue": ["#124"],
                "Updates": ["#124"],
                "Maintainer Notes": ["Keep this note"],
            }
        )
        existing_df.to_csv(str(test_csv), index=False)

        with patch("issue_to_csv.CSV_PATH", str(test_csv)):
            values = {
                "Description": "Existing risk revised",
                "Likelihood": "High",
                "Severity": "Medium",
                "Reach": "Very High",
                "Mitigations": "New mitigations",
                "Ownership": "New owner",
                "Examples": "New examples",
                "Related Risks": "#11, #20",
                "Tags": "Research Integrity",
            }
            upsert_csv(values, "124", "Existing issue title")

            df = pd.read_csv(str(test_csv))
            assert len(df) == 1
            assert df.iloc[0]["Description"] == "Existing risk revised"
            assert df.iloc[0]["Issue Title"] == "Existing issue title"
            assert df.iloc[0]["Issue"] == "#124"
            assert df.iloc[0]["Updates"] == "#124"
            assert df.iloc[0]["Reach"] == "Very High"
            assert df.iloc[0]["Related Risks"] == "#11, #20"
            assert df.iloc[0]["Tags"] == "Research Integrity"
            assert df.iloc[0]["Maintainer Notes"] == "Keep this note"
