import os
import sys
from io import StringIO
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".github", "scripts"))

from validate_csv import validate


class TestValidateCSV:
    def test_valid_csv(self, tmp_path):
        csv_content = """Issue Title,Description,Likelihood,Severity,Reach,Mitigations,Ownership,Examples,Tags,Issue,Updates,Maintainer Notes
"Issue one","Test risk",High,Medium,Low,"Mitigation text","Owner","Examples","Environmental","#1","#1",""
"""
        register_dir = tmp_path / "register"
        register_dir.mkdir()
        csv_file = register_dir / "risks.csv"
        csv_file.write_text(csv_content)

        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                validate()
                output = mock_stdout.getvalue()
                assert "CSV valid" in output
        finally:
            os.chdir(original_cwd)

    def test_missing_columns(self, tmp_path):
        csv_content = """Issue Title,Description,Likelihood,Reach,Mitigations,Ownership,Examples,Tags,Issue,Updates,Maintainer Notes
"Issue one","Test risk",High,Low,"Mitigation","Owner","Examples","Environmental","#1","#1",""
"""
        register_dir = tmp_path / "register"
        register_dir.mkdir()
        csv_file = register_dir / "risks.csv"
        csv_file.write_text(csv_content)

        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            with pytest.raises(SystemExit):
                validate()
        finally:
            os.chdir(original_cwd)

    def test_empty_required_field(self, tmp_path):
        csv_content = """Issue Title,Description,Likelihood,Severity,Reach,Mitigations,Ownership,Examples,Tags,Issue,Updates,Maintainer Notes
"Issue one","",High,Medium,Low,"Mitigation","Owner","Examples","Environmental","#1","#1",""
"""
        register_dir = tmp_path / "register"
        register_dir.mkdir()
        csv_file = register_dir / "risks.csv"
        csv_file.write_text(csv_content)

        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            with pytest.raises(SystemExit):
                validate()
        finally:
            os.chdir(original_cwd)

    def test_invalid_likelihood(self, tmp_path):
        csv_content = """Issue Title,Description,Likelihood,Severity,Reach,Mitigations,Ownership,Examples,Tags,Issue,Updates,Maintainer Notes
"Issue one","Test risk",Invalid,Medium,Low,"Mitigation","Owner","Examples","Environmental","#1","#1",""
"""
        register_dir = tmp_path / "register"
        register_dir.mkdir()
        csv_file = register_dir / "risks.csv"
        csv_file.write_text(csv_content)

        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            with pytest.raises(SystemExit):
                validate()
        finally:
            os.chdir(original_cwd)

    def test_invalid_severity(self, tmp_path):
        csv_content = """Issue Title,Description,Likelihood,Severity,Reach,Mitigations,Ownership,Examples,Tags,Issue,Updates,Maintainer Notes
"Issue one","Test risk",High,Invalid,Low,"Mitigation","Owner","Examples","Environmental","#1","#1",""
"""
        register_dir = tmp_path / "register"
        register_dir.mkdir()
        csv_file = register_dir / "risks.csv"
        csv_file.write_text(csv_content)

        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            with pytest.raises(SystemExit):
                validate()
        finally:
            os.chdir(original_cwd)

    def test_invalid_reach(self, tmp_path):
        csv_content = """Issue Title,Description,Likelihood,Severity,Reach,Mitigations,Ownership,Examples,Tags,Issue,Updates,Maintainer Notes
"Issue one","Test risk",High,Medium,Invalid,"Mitigation","Owner","Examples","Environmental","#1","#1",""
"""
        register_dir = tmp_path / "register"
        register_dir.mkdir()
        csv_file = register_dir / "risks.csv"
        csv_file.write_text(csv_content)

        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            with pytest.raises(SystemExit):
                validate()
        finally:
            os.chdir(original_cwd)
