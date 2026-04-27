"""Sync a newly submitted resource issue into resources/README.md."""

import os
import re
import sys


FIELDS = [
    "Resource Title",
    "URL",
    "Organisation / authors",
    "Year",
    "Type",
    "Relevance",
    "Tags",
    "Notes",
]
README_PATH = "resources/README.md"
TYPE_TO_HEADING = {
    "Policy": "Policies",
    "Position paper": "Position Papers",
    "Guidance": "Guidance and Frameworks",
    "Case study": "Case Studies and Reports",
    "Report": "Case Studies and Reports",
    "Other": "Other",
}
RESOURCE_HEADING_PATTERN = re.compile(r"^### \[(?P<title>.+)\]\((?P<url>.+)\)\s*$")


def parse_issue(body):
    """Extract supported resource issue form fields from a GitHub issue body."""
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

    return {field: clean_value(values.get(field, "")) for field in FIELDS}


def clean_value(value):
    """Collapse issue-form values into single-line markdown field content."""
    return " ".join(str(value).split())


def markdown_link_title(title):
    """Escape square brackets in markdown link text."""
    return title.replace("[", r"\[").replace("]", r"\]")


def markdown_url(url):
    """Escape closing parentheses in markdown link URLs."""
    return url.replace(")", "%29")


def target_heading(resource_type):
    """Return the resources README section for a submitted resource type."""
    return TYPE_TO_HEADING.get(resource_type, "Other")


def format_resource_entry(values):
    """Format a resource issue as a resources/README.md entry."""
    title = markdown_link_title(values["Resource Title"])
    url = markdown_url(values["URL"])
    return "\n".join(
        [
            f"### [{title}]({url})",
            "",
            f"- Organisation / authors: {values.get('Organisation / authors', '')}",
            f"- Year: {values.get('Year', '')}",
            f"- Type: {values.get('Type', '')}",
            f"- Relevance: {values.get('Relevance', '')}",
            f"- Tags: {values.get('Tags', '')}",
            f"- Notes: {values.get('Notes', '')}",
        ]
    )


def normalise_heading_url(raw_url):
    """Normalise a markdown heading URL for duplicate checks."""
    return raw_url.strip().strip("<>").replace("%29", ")")


def remove_existing_resource(lines, url):
    """Remove an existing resource block with the same URL, if present."""
    normalised_url = normalise_heading_url(url)
    index = 0
    while index < len(lines):
        match = RESOURCE_HEADING_PATTERN.match(lines[index])
        if match and normalise_heading_url(match.group("url")) == normalised_url:
            end = index + 1
            while end < len(lines) and not lines[end].startswith(("## ", "### ")):
                end += 1
            del lines[index:end]
            while index < len(lines) and lines[index] == "" and index + 1 < len(lines):
                if lines[index + 1].startswith(("## ", "### ")):
                    del lines[index]
                else:
                    break
            return lines
        index += 1
    return lines


def append_resource(content, values):
    """Append or replace a resource entry in the appropriate README section."""
    heading = target_heading(values["Type"])
    lines = remove_existing_resource(content.splitlines(), values["URL"])
    section_marker = f"## {heading}"

    try:
        section_index = next(index for index, line in enumerate(lines) if line.strip() == section_marker)
    except StopIteration:
        if lines and lines[-1] != "":
            lines.append("")
        lines.extend([section_marker, ""])
        section_index = len(lines) - 2

    insert_index = len(lines)
    for index in range(section_index + 1, len(lines)):
        if lines[index].startswith("## "):
            insert_index = index
            break

    entry_lines = format_resource_entry(values).splitlines()
    while insert_index > 0 and lines[insert_index - 1] == "":
        insert_index -= 1

    replacement = [""] + entry_lines + [""]
    lines[insert_index:insert_index] = replacement
    return "\n".join(lines).rstrip() + "\n"


def sync_resource(values):
    """Write a resource issue entry into resources/README.md."""
    with open(README_PATH, encoding="utf-8") as readme_file:
        content = readme_file.read()

    updated_content = append_resource(content, values)

    with open(README_PATH, "w", encoding="utf-8", newline="\n") as readme_file:
        readme_file.write(updated_content)


if __name__ == "__main__":
    body = os.environ.get("ISSUE_BODY", "")
    issue_number = os.environ.get("ISSUE_NUMBER", "")
    values = parse_issue(body)

    required_fields = ["Resource Title", "URL", "Type", "Relevance"]
    missing_fields = [field for field in required_fields if not values.get(field)]
    if missing_fields:
        print(f"Could not parse required resource fields: {', '.join(missing_fields)}")
        sys.exit(1)

    sync_resource(values)
    print(f"Synced resource from issue #{issue_number} to resources/README.md")
