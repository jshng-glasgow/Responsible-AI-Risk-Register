import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".github", "scripts"))

from resource_to_readme import append_resource, parse_issue, target_heading


class TestResourceToReadme:
    def test_parse_issue_complete(self):
        body = """### Resource Title
Example Policy

### URL
https://example.org/policy

### Organisation / authors
Example Org

### Year
2026

### Type
Policy

### Relevance
Useful policy example.

### Tags
Governance, Research Integrity

### Notes
Useful for maintainers.
"""
        values = parse_issue(body)

        assert values["Resource Title"] == "Example Policy"
        assert values["URL"] == "https://example.org/policy"
        assert values["Organisation / authors"] == "Example Org"
        assert values["Year"] == "2026"
        assert values["Type"] == "Policy"
        assert values["Relevance"] == "Useful policy example."
        assert values["Tags"] == "Governance, Research Integrity"
        assert values["Notes"] == "Useful for maintainers."

    def test_type_maps_to_existing_resource_sections(self):
        assert target_heading("Policy") == "Policies"
        assert target_heading("Position paper") == "Position Papers"
        assert target_heading("Guidance") == "Guidance and Frameworks"
        assert target_heading("Case study") == "Case Studies and Reports"
        assert target_heading("Report") == "Case Studies and Reports"
        assert target_heading("Something else") == "Other"

    def test_append_resource_to_matching_section(self):
        content = """# Resources

## Policies

### [Existing](https://example.org/existing)

- Organisation / authors: Existing Org
- Year: 2025
- Type: Policy
- Relevance: Existing relevance
- Tags:
- Notes:

## Other
"""
        values = {
            "Resource Title": "Example Policy",
            "URL": "https://example.org/policy",
            "Organisation / authors": "Example Org",
            "Year": "2026",
            "Type": "Policy",
            "Relevance": "Useful policy example.",
            "Tags": "Governance",
            "Notes": "",
        }

        updated = append_resource(content, values)

        assert "### [Example Policy](https://example.org/policy)" in updated
        assert updated.index("### [Example Policy](https://example.org/policy)") < updated.index("## Other")
        assert "- Organisation / authors: Example Org" in updated

    def test_append_resource_replaces_existing_url(self):
        content = """# Resources

## Policies

### [Old Title](https://example.org/policy)

- Organisation / authors: Old Org
- Year: 2025
- Type: Policy
- Relevance: Old relevance
- Tags:
- Notes:

## Other
"""
        values = {
            "Resource Title": "New Title",
            "URL": "https://example.org/policy",
            "Organisation / authors": "New Org",
            "Year": "2026",
            "Type": "Policy",
            "Relevance": "New relevance",
            "Tags": "",
            "Notes": "Updated note",
        }

        updated = append_resource(content, values)

        assert "Old Title" not in updated
        assert "Old Org" not in updated
        assert updated.count("https://example.org/policy") == 1
        assert "### [New Title](https://example.org/policy)" in updated
