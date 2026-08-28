"""Sync a newly submitted resource issue into the resource register CSV."""

import csv
import os
import re
import sys


FIELDS = [
    "Resource Title",
    "URL",
    "Organisation / Authors",
    "Year",
    "Type",
    "Relevance",
    "Tags",
    "Other Tags",
    "Related Risks",
    "Notes",
]
CSV_COLUMNS = [
    "Resource Title",
    "URL",
    "Organisation / Authors",
    "Year",
    "Type",
    "Relevance",
    "Tags",
    "Related Risks",
    "Notes",
    "Issue",
    "Maintainer Notes",
]
LEGACY_FIELD_NAMES = {"Organisation / authors": "Organisation / Authors"}
CSV_PATH = "resources/resources.csv"
ISSUE_REF_PATTERN = re.compile(r"#?\d+")
YEAR_PATTERN = re.compile(r"^\d{4}$")


def parse_issue(body):
    """Extract supported resource issue form fields from a GitHub issue body."""
    values = {}
    for section in body.split("### "):
        if not section.strip():
            continue
        lines = section.strip().split("\n", 1)
        field = LEGACY_FIELD_NAMES.get(lines[0].strip(), lines[0].strip())
        content = lines[1].strip() if len(lines) > 1 else ""
        if field in FIELDS:
            values[field] = "" if content in ("_No response_", "") else content

    for field in ["Resource Title", "URL", "Organisation / Authors", "Type"]:
        values[field] = collapse_whitespace(values.get(field, ""))
    values["Year"] = normalise_year(values.get("Year", ""))
    values["Tags"] = combine_tags(values.get("Tags", ""), values.get("Other Tags", ""))
    values["Related Risks"] = normalise_issue_refs(values.get("Related Risks", ""))
    values["Relevance"] = values.get("Relevance", "")
    values["Notes"] = values.get("Notes", "")
    values.pop("Other Tags", None)
    return values


def collapse_whitespace(value):
    """Collapse a structured issue-form value to a single line."""
    return " ".join(str(value).split())


def normalise_year(value):
    """Return the latest four-digit year from legacy free-text responses."""
    collapsed_value = collapse_whitespace(value)
    years = re.findall(r"(?:19|20)\d{2}", collapsed_value)
    return years[-1] if years else collapsed_value


def split_tags(raw_value):
    """Split comma- or newline-separated tags into clean values."""
    if not raw_value or raw_value in ("_No response_", "No changes"):
        return []
    return [part.strip() for part in re.split(r",|\n", raw_value) if part.strip()]


def combine_tags(selected_tags, other_tags):
    """Merge selected and free-text tags while preserving input order."""
    tags = []
    for tag in split_tags(selected_tags) + split_tags(other_tags):
        if tag not in tags:
            tags.append(tag)
    return ", ".join(tags)


def normalise_issue_refs(raw_value):
    """Convert issue references into a deduplicated ``#123`` list."""
    refs = []
    for match in ISSUE_REF_PATTERN.findall(raw_value or ""):
        ref = f"#{match.lstrip('#')}"
        if ref not in refs:
            refs.append(ref)
    return ", ".join(refs)


def normalise_url(url):
    """Normalise URLs for duplicate matching without changing stored values."""
    return str(url).strip().rstrip("/").casefold()


def upsert_csv(values, issue_number):
    """Insert or replace a resource matched by URL while preserving editorial notes."""
    rows = []
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, newline="", encoding="utf-8") as existing_file:
            rows = list(csv.DictReader(existing_file))

    issue_ref = f"#{issue_number}" if issue_number else ""
    row_data = {field: values.get(field, "") for field in CSV_COLUMNS}
    row_data["Issue"] = issue_ref
    row_data["Maintainer Notes"] = ""

    submitted_url = normalise_url(values.get("URL", ""))
    for row in rows:
        if normalise_url(row.get("URL", "")) == submitted_url:
            existing_issue = row.get("Issue", "")
            existing_notes = row.get("Maintainer Notes", "")
            row.update(row_data)
            row["Issue"] = existing_issue or issue_ref
            row["Maintainer Notes"] = existing_notes
            break
    else:
        rows.append(row_data)

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    values = parse_issue(os.environ.get("ISSUE_BODY", ""))
    issue_number = os.environ.get("ISSUE_NUMBER", "")
    required_fields = ["Resource Title", "URL", "Type", "Relevance"]
    missing_fields = [field for field in required_fields if not values.get(field)]

    if missing_fields:
        print(f"Could not parse required resource fields: {', '.join(missing_fields)}")
        sys.exit(1)
    if values.get("Year") and not YEAR_PATTERN.fullmatch(values["Year"]):
        print("Year must be a four-digit value - skipping")
        sys.exit(1)

    upsert_csv(values, issue_number)
    print(f"Synced resource from issue #{issue_number} to resource register")
