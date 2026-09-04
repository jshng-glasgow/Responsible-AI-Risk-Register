# Test Suite for the Responsible AI Risk Register

This directory contains the test suite for the project scripts.

## Running Tests

Install dependencies:
```bash
pip install pytest beautifulsoup4 pandas
```

Run tests:
```bash
pytest tests/
```

## Test Coverage

- `test_issue_to_csv.py`: Tests parsing GitHub issue bodies and appending new risks to the CSV.
- `test_resource_to_csv.py`: Tests parsing resource issue bodies and adding or replacing resource CSV rows.
- `test_validate_resources.py`: Tests the resource CSV schema and supported field formats.
- `test_update_csv.py`: Tests parsing and updating existing risks in the CSV.
- `test_validate_csv.py`: Tests validation of the risks CSV file.
- `test_render_table.py`: Tests generation of HTML table from the CSV.

## Notes

- Tests use temporary directories to avoid modifying the actual data.
- Scripts have been modified to wrap main execution in `if __name__ == "__main__"` to allow importing without running.
