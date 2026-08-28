import json
import os
import sys

from bs4 import BeautifulSoup


class TestRenderTable:
    def test_render_table_creates_html_and_json(self, tmp_path):
        csv_content = """Issue Title,Description,Likelihood,Severity,Reach,Mitigations,Ownership,Best Practice Examples,Related Risks,Tags,Issue,Updates,Maintainer Notes
"Issue one","Test risk",High,Medium,Low,"Mitigation text","Owner","Examples","#3, #4","environmental, research integrity","#1","#1",""
"Issue two","Another risk",Low,High,Very High,"Another mitigation","Another owner","Another examples","","training and skills","#2","#2, #5","Synthesised from issues #2 and #5"
"""
        csv_file = tmp_path / "register" / "risks.csv"
        csv_file.parent.mkdir()
        csv_file.write_text(csv_content)

        html_file = tmp_path / "docs" / "index.html"
        json_file = tmp_path / "docs" / "risks.json"

        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            script_path = os.path.join(original_cwd, '.github', 'scripts', 'render_table.py')
            with open(script_path, 'r', encoding='utf-8') as f:
                script_code = f.read()
            exec(script_code, {'__name__': '__main__'})

            assert html_file.exists()
            assert json_file.exists()

            with open(str(html_file), 'r', encoding='utf-8') as f:
                html_content = f.read()
            with open(str(json_file), 'r', encoding='utf-8') as f:
                json_content = json.load(f)

            soup = BeautifulSoup(html_content, 'html.parser')
            assert soup.title.string == "SSI Generative AI Risk Register"
            assert soup.find(id="register-root") is not None
            assert soup.find(id="search-input") is not None
            assert soup.find(id="tag-filter") is not None
            app_script = soup.find("script", src=lambda src: src and src.startswith("./app.js?v="))
            assert app_script is not None
            assert "REGISTER_ASSET_VERSION" in html_content

            assert len(json_content) == 2
            assert json_content[0]["Issue Title"] == "Issue one"
            assert json_content[0]["Description"] == "Test risk"
            assert json_content[0]["Related Risks"] == "#3, #4"
            assert json_content[0]["Tags"] == "environmental, research integrity"
            assert json_content[0]["issue_url"].endswith("/issues/1")
            assert json_content[0]["related_risk_urls"][1]["label"] == "#4"
            assert json_content[1]["update_urls"][1]["label"] == "#5"
        finally:
            os.chdir(original_cwd)

    def test_render_table_with_newlines(self, tmp_path):
        csv_content = """Issue Title,Description,Likelihood,Severity,Reach,Mitigations,Ownership,Best Practice Examples,Related Risks,Tags,Issue,Updates,Maintainer Notes
"Issue one","Test risk\nwith newline",High,Medium,Low,"Mitigation\ntext","Owner","Examples","","environmental","#1","#1",""
"""
        csv_file = tmp_path / "register" / "risks.csv"
        csv_file.parent.mkdir()
        csv_file.write_text(csv_content)

        html_file = tmp_path / "docs" / "index.html"
        json_file = tmp_path / "docs" / "risks.json"

        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            script_path = os.path.join(original_cwd, '.github', 'scripts', 'render_table.py')
            with open(script_path, 'r', encoding='utf-8') as f:
                script_code = f.read()
            exec(script_code, {'__name__': '__main__'})

            with open(str(html_file), 'r', encoding='utf-8') as f:
                html_content = f.read()
            with open(str(json_file), 'r', encoding='utf-8') as f:
                json_content = json.load(f)

            assert "register-root" in html_content
            assert "with newline" in json_content[0]["Description"]
            assert json_content[0]["Mitigations"].replace("\r\n", "\n") == "Mitigation\ntext"
        finally:
            os.chdir(original_cwd)
