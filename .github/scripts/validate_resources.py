"""Validate the resource register CSV schema and field values."""

import re
import sys

import pandas as pd


REQUIRED_COLUMNS = [
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
REQUIRED_VALUES = ["Resource Title", "URL", "Type", "Relevance"]
VALID_TYPES = {"Policy", "Position paper", "Guidance", "Case study", "Report", "Other"}
ISSUE_REF_LIST_PATTERN = re.compile(r"^#\d+(?:,\s*#\d+)*$")
YEAR_PATTERN = re.compile(r"^\d{4}$")


def is_valid_issue_ref_list(value):
    if pd.isna(value) or value == "":
        return True
    return bool(ISSUE_REF_LIST_PATTERN.fullmatch(str(value).strip()))


def validate():
    """Check the resource CSV for required columns and valid field contents."""
    errors = []
    try:
        dataframe = pd.read_csv("resources/resources.csv", dtype=str)
    except Exception as error:
        print(f"Could not read resource CSV: {error}")
        sys.exit(1)

    missing = [column for column in REQUIRED_COLUMNS if column not in dataframe.columns]
    if missing:
        errors.append(f"Missing columns: {missing}")

    for column in REQUIRED_VALUES:
        if column in dataframe.columns and dataframe[column].isnull().any():
            errors.append(f"Column '{column}' has empty values")

    if "Year" in dataframe.columns:
        invalid_years = dataframe[
            dataframe["Year"].notna() & ~dataframe["Year"].astype(str).str.fullmatch(YEAR_PATTERN)
        ]["Year"].unique()
        if len(invalid_years) > 0:
            errors.append(f"Invalid years: {invalid_years}. Use a four-digit year.")

    if "Type" in dataframe.columns:
        invalid_types = dataframe[~dataframe["Type"].isin(VALID_TYPES)]["Type"].unique()
        if len(invalid_types) > 0:
            errors.append(f"Invalid resource types: {invalid_types}")

    for column in ["Issue", "Related Risks"]:
        if column in dataframe.columns:
            invalid_rows = dataframe[~dataframe[column].apply(is_valid_issue_ref_list)]
            if not invalid_rows.empty:
                errors.append(f"Invalid issue references in '{column}'")

    if "URL" in dataframe.columns:
        normalised_urls = dataframe["URL"].astype(str).str.rstrip("/").str.casefold()
        if normalised_urls.duplicated().any():
            errors.append("Duplicate resource URLs")
        if (~dataframe["URL"].astype(str).str.match(r"^https?://")).any():
            errors.append("Resource URLs must start with http:// or https://")

    if errors:
        print("Resource validation failed:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    print(f"Resource CSV valid - {len(dataframe)} resources")


if __name__ == "__main__":
    validate()
