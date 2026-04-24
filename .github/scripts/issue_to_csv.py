"""Sync a newly submitted risk issue into the risk register CSV."""

import csv
import os
import re
import sys


FIELDS = [
    "Description",
    "Likelihood",
    "Severity",
    "Reach",
    "Mitigations",
    "Ownership",
    "Examples",
    "Related Risks",
    "Tags",
    "Other Tags",
]
CSV_PATH = "register/risks.csv"
ISSUE_REF_PATTERN = re.compile(r"#?\d+")


def parse_issue(body):
    """Extract supported issue form fields from a GitHub issue body."""
    values = {}
    sections = body.split("### ")
    for section in sections:
        if not section.strip():
            continue
        lines = section.strip().split("\n", 1)
        field = lines[0].strip()
        content = lines[1].strip() if len(lines) > 1 else ""
        if field in FIELDS:
            values[field] = "" if content in ("_No response_", "") else content
    values["Related Risks"] = normalise_issue_refs(values.get("Related Risks", ""))
    values["Tags"] = combine_tags(values.get("Tags", ""), values.get("Other Tags", ""))
    values.pop("Other Tags", None)
    return values


def split_tags(raw_value):
    """Split comma- or newline-separated tag input into clean tag values."""
    if not raw_value or raw_value in ("_No response_", "No changes"):
        return []
    parts = re.split(r",|\n", raw_value)
    return [part.strip() for part in parts if part.strip()]


def normalise_issue_refs(raw_value):
    """Convert issue references into a deduplicated ``#123`` comma-separated list."""
    if not raw_value or raw_value in ("_No response_", "No changes"):
        return ""

    refs = []
    for match in ISSUE_REF_PATTERN.findall(raw_value):
        ref = f"#{match.lstrip('#')}"
        if ref not in refs:
            refs.append(ref)

    return ", ".join(refs)


def combine_tags(selected_tags, other_tags):
    """Merge selected and free-text tags while preserving input order."""
    tags = []
    for tag in split_tags(selected_tags) + split_tags(other_tags):
        if tag not in tags:
            tags.append(tag)
    return ", ".join(tags)


def upsert_csv(values, issue_number, issue_title):
    """Insert or update the matching risk row for the submitted issue."""
    issue_ref = f"#{issue_number}"
    fieldnames = [
        "Issue Title",
        "Description",
        "Likelihood",
        "Severity",
        "Reach",
        "Mitigations",
        "Ownership",
        "Examples",
        "Related Risks",
        "Tags",
        "Issue",
        "Updates",
        "Maintainer Notes",
    ]
    rows = []

    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, newline="", encoding="utf-8") as existing_file:
            rows = list(csv.DictReader(existing_file))

    row_data = {
        field: values.get(field, "")
        for field in [
            "Description",
            "Likelihood",
            "Severity",
            "Reach",
            "Mitigations",
            "Ownership",
            "Examples",
            "Related Risks",
            "Tags",
        ]
    }
    row_data["Issue Title"] = issue_title or ""
    row_data["Issue"] = issue_ref
    row_data["Updates"] = issue_ref
    row_data["Maintainer Notes"] = ""

    updated = False
    for row in rows:
        if row.get("Issue") == issue_ref:
            existing_updates = row.get("Updates", issue_ref) or issue_ref
            existing_notes = row.get("Maintainer Notes", "")
            row.update(row_data)
            row["Updates"] = existing_updates
            row["Maintainer Notes"] = existing_notes
            updated = True
            break

    if not updated:
        rows.append(row_data)

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    body = os.environ.get("ISSUE_BODY", "")
    issue_number = os.environ.get("ISSUE_NUMBER", "")
    issue_title = os.environ.get("ISSUE_TITLE", "")

    values = parse_issue(body)

    if not values.get("Description"):
        print("Could not parse description from issue body - skipping")
        sys.exit(1)

    upsert_csv(values, issue_number, issue_title)
    print(f"Synced risk from issue #{issue_number} to register")
