"""Validate the risk register CSV schema and supported categorical values."""

import re
import sys

import pandas as pd

REQUIRED_COLUMNS = [
    "Issue Title",
    "Description",
    "Likelihood",
    "Severity",
    "Reach",
    "Mitigations",
    "Ownership",
    "Best Practice Examples",
    "Related Risks",
    "Tags",
    "Issue",
    "Updates",
    "Maintainer Notes",
]
VALID_LEVELS = {"Very Low", "Low", "Medium", "High", "Very High", "Unknown"}
ISSUE_REF_LIST_PATTERN = re.compile(r"^#\d+(?:,\s*#\d+)*$")


def is_valid_issue_ref_list(value):
    """Return whether a CSV cell contains comma-separated ``#123`` issue refs."""
    if pd.isna(value) or value == "":
        return True
    return bool(ISSUE_REF_LIST_PATTERN.fullmatch(str(value).strip()))


def validate():
    """Check the register CSV for required columns and valid field contents."""
    errors = []

    try:
        df = pd.read_csv("register/risks.csv")
    except Exception as e:
        print(f"Could not read CSV: {e}")
        sys.exit(1)

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        errors.append(f"Missing columns: {missing}")

    for col in ["Issue Title", "Description", "Likelihood", "Severity", "Reach"]:
        if col in df.columns and df[col].isnull().any():
            errors.append(f"Column '{col}' has empty values")

    for col in ["Likelihood", "Severity", "Reach"]:
        if col in df.columns:
            invalid = df[~df[col].isin(VALID_LEVELS)][col].unique()
            if len(invalid) > 0:
                errors.append(
                    f"Invalid values in '{col}': {invalid}. Must be Very Low, Low, Medium, High, Very High, or Unknown."
                )

    for col in ["Issue", "Updates", "Related Risks"]:
        if col in df.columns:
            invalid_rows = df[~df[col].apply(is_valid_issue_ref_list)]
            if not invalid_rows.empty:
                errors.append(
                    f"Invalid issue references in '{col}'. Use comma-separated values like #12 or #12, #48."
                )

    if errors:
        print("Validation failed:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print(f"CSV valid - {len(df)} risks in register")


if __name__ == "__main__":
    validate()
