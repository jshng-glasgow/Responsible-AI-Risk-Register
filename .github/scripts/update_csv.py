import os
import re
import sys

import pandas as pd


FIELDS = ["Issue Number", "Description", "Likelihood", "Severity", "Reach", "Mitigations", "Ownership", "Examples", "Tags", "Other Tags"]
CSV_PATH = "register/risks.csv"


def split_tags(raw_value):
    if not raw_value or raw_value in ("_No response_", "No changes", "None"):
        return []
    parts = re.split(r",|\n", raw_value)
    return [part.strip() for part in parts if part.strip()]


def combine_tags(selected_tags, other_tags):
    tags = []
    for tag in split_tags(selected_tags) + split_tags(other_tags):
        if tag not in tags:
            tags.append(tag)
    return ", ".join(tags)


def parse_issue(body):
    values = {}
    sections = body.split("### ")
    for section in sections:
        if not section.strip():
            continue
        lines = section.strip().split("\n", 1)
        field = lines[0].strip()
        content = lines[1].strip() if len(lines) > 1 else ""
        if field in FIELDS:
            values[field] = None if content in ("_No response_", "", "None", "No changes") else content

    combined_tags = combine_tags(values.get("Tags"), values.get("Other Tags"))
    values["Tags"] = combined_tags if combined_tags else None
    values.pop("Other Tags", None)
    return values


def update_csv_row(values, issue_number):
    file_exists = os.path.exists(CSV_PATH)
    if values["Issue Number"] and not file_exists:
        print(f"Trying to update issue #{values['Issue Number']} but CSV doesn't exist - skipping")
        sys.exit(1)
    updated_issue = values["Issue Number"].replace("#", "")
    risk_register = pd.read_csv(CSV_PATH)
    risk_register = risk_register.astype(object)
    row_mask = risk_register["Issue"] == f"#{updated_issue}"
    if not row_mask.any():
        print(f"Trying to update issue #{updated_issue} but it doesn't exist in CSV - skipping")
        sys.exit(1)

    row_index = risk_register[row_mask].index[0]

    for field in ["Description", "Likelihood", "Severity", "Reach", "Mitigations", "Ownership", "Examples", "Tags"]:
        if values.get(field) is not None:
            risk_register.loc[row_index, field] = values[field]

    update_issue = f"#{issue_number}"
    current_updates = risk_register.loc[row_index, "Updates"] if "Updates" in risk_register.columns else ""
    if pd.notna(current_updates) and current_updates:
        existing_updates = [item.strip() for item in str(current_updates).split(",") if item.strip()]
        if update_issue not in existing_updates:
            risk_register.loc[row_index, "Updates"] = f"{current_updates}, {update_issue}"
    else:
        risk_register.loc[row_index, "Updates"] = update_issue

    risk_register.to_csv(CSV_PATH, index=False)


if __name__ == "__main__":
    body = os.environ.get("ISSUE_BODY", "")
    issue_number = os.environ.get("ISSUE_NUMBER", "")

    values = parse_issue(body)

    if not values.get("Issue Number"):
        print("Could not parse issue number from issue body - skipping")
        sys.exit(1)

    update_csv_row(values, issue_number)
    print(f"Updated risk from issue {values['Issue Number']} in register")
