"""Validate the risk register CSV schema and supported categorical values."""

import pandas as pd
import sys

REQUIRED_COLUMNS = ["Issue Title", "Description", "Likelihood", "Severity", "Reach", "Mitigations", "Ownership", "Examples", "Tags", "Issue", "Updates", "Maintainer Notes"]
VALID_LEVELS = {"Very Low", "Low", "Medium", "High", "Very High", "Unknown"}

def validate():
    """Check the register CSV for required columns and valid field contents."""
    errors = []
    
    try:
        df = pd.read_csv("register/risks.csv")
    except Exception as e:
        print(f"Could not read CSV: {e}")
        sys.exit(1)

    # Check columns
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        errors.append(f"Missing columns: {missing}")

    # Check required fields aren't empty
    for col in ["Issue Title", "Description", "Likelihood", "Severity", "Reach"]:
        if col in df.columns and df[col].isnull().any():
            errors.append(f"Column '{col}' has empty values")

    # Check categorical fields are valid
    for col in ["Likelihood", "Severity", "Reach"]:
        if col in df.columns:
            invalid = df[~df[col].isin(VALID_LEVELS)][col].unique()
            if len(invalid) > 0:
                errors.append(
                    f"Invalid values in '{col}': {invalid}. Must be Very Low, Low, Medium, High, Very High, or Unknown."
                )

    if errors:
        print("Validation failed:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print(f"CSV valid — {len(df)} risks in register")

if __name__ == "__main__":
    validate()
