import os
import sys
from io import StringIO
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".github", "scripts"))

from validate_resources import validate


VALID_CSV = """Resource Title,URL,Organisation / Authors,Year,Type,Relevance,Tags,Related Risks,Notes,Issue,Maintainer Notes
Example Policy,https://example.org/policy,Example Org,2026,Policy,Useful resource,Governance,#12,,#100,
"""


def write_resource_csv(tmp_path, content):
    resource_dir = tmp_path / "resources"
    resource_dir.mkdir()
    (resource_dir / "resources.csv").write_text(content)


class TestValidateResources:
    def test_valid_resource_csv(self, tmp_path):
        write_resource_csv(tmp_path, VALID_CSV)
        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            with patch("sys.stdout", new_callable=StringIO) as stdout:
                validate()
            assert "Resource CSV valid" in stdout.getvalue()
        finally:
            os.chdir(original_cwd)

    def test_blank_year_is_valid(self, tmp_path):
        write_resource_csv(tmp_path, VALID_CSV.replace(",2026,Policy,", ",,Policy,"))
        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            validate()
        finally:
            os.chdir(original_cwd)

    @pytest.mark.parametrize(
        "old_value,new_value",
        [
            (",2026,Policy,", ",twenty-six,Policy,"),
            (",2026,Policy,", ",2026,Unknown type,"),
            (",#12,,#100,", ",risk-12,,#100,"),
        ],
    )
    def test_invalid_resource_values(self, tmp_path, old_value, new_value):
        write_resource_csv(tmp_path, VALID_CSV.replace(old_value, new_value))
        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            with pytest.raises(SystemExit):
                validate()
        finally:
            os.chdir(original_cwd)

    def test_duplicate_urls(self, tmp_path):
        duplicate_row = "Another title,https://example.org/policy/,Other Org,2025,Guidance,Other resource,,,,,\n"
        write_resource_csv(tmp_path, VALID_CSV + duplicate_row)
        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            with pytest.raises(SystemExit):
                validate()
        finally:
            os.chdir(original_cwd)
