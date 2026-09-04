import json
import os
import sys

from bs4 import BeautifulSoup


RESOURCE_CSV_CONTENT = """Resource Title,URL,Organisation / Authors,Year,Type,Relevance,Tags,Related Risks,Notes,Issue,Maintainer Notes
"Example resource","https://example.org/resource","Example Org",2026,Guidance,"Useful resource","Governance, Research Integrity","#1","Notes","#10",""
"Undated resource","https://example.org/undated","Example Org",,Report,"Another useful resource","","","","",""
"""


def write_resource_csv(tmp_path):
    resource_file = tmp_path / "resources" / "resources.csv"
    resource_file.parent.mkdir()
    resource_file.write_text(RESOURCE_CSV_CONTENT)


class TestRenderTable:
    def test_render_table_creates_html_and_json(self, tmp_path):
        csv_content = """Issue Title,Description,Likelihood,Severity,Reach,Mitigations,Ownership,Best Practice Examples,Related Risks,Tags,Issue,Updates,Maintainer Notes
"Issue one","Test risk",High,Medium,Low,"Mitigation text","Owner","Examples","#3, #4","environmental, research integrity","#1","#1",""
"Issue two","Another risk",Low,High,Very High,"Another mitigation","Another owner","Another examples","","training and skills","#2","#2, #5","Synthesised from issues #2 and #5"
"""
        csv_file = tmp_path / "register" / "risks.csv"
        csv_file.parent.mkdir()
        csv_file.write_text(csv_content)
        write_resource_csv(tmp_path)

        html_file = tmp_path / "docs" / "index.html"
        json_file = tmp_path / "docs" / "risks.json"
        resource_json_file = tmp_path / "docs" / "resources.json"

        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            script_path = os.path.join(original_cwd, '.github', 'scripts', 'render_table.py')
            with open(script_path, 'r', encoding='utf-8') as f:
                script_code = f.read()
            exec(script_code, {'__name__': '__main__'})

            assert html_file.exists()
            assert json_file.exists()
            assert resource_json_file.exists()

            with open(str(html_file), 'r', encoding='utf-8') as f:
                html_content = f.read()
            with open(str(json_file), 'r', encoding='utf-8') as f:
                json_content = json.load(f)
            with open(str(resource_json_file), 'r', encoding='utf-8') as f:
                resource_json_content = json.load(f)

            soup = BeautifulSoup(html_content, 'html.parser')
            assert soup.title.string == "Responsible AI Risk Register"
            assert soup.find(id="register-root") is not None
            assert soup.find(id="search-input") is not None
            assert soup.find(id="tag-filter") is not None
            assert soup.find(id="resources-tab")["href"] == "#resources"
            assert soup.find(id="resource-year-filter") is not None
            assert soup.find(id="resource-type-filter") is not None
            assert soup.find(id="resource-tag-filter") is not None
            card_template = soup.find("template", id="risk-card-template")
            template_content = BeautifulSoup(card_template.decode_contents(), "html.parser")
            disclosure = template_content.find("details", class_="risk-details")
            assert disclosure is not None
            assert not disclosure.has_attr("open")
            assert disclosure.find("summary", class_="card-summary") is not None
            assert disclosure.find(class_="card-title")["role"] == "heading"
            assert disclosure.find(class_="impact-badges") is not None
            assert disclosure.find(class_="tag-badges") is not None
            assert [label.get_text(strip=True) for label in disclosure.select(".meta-label")] == ["Impact:", "Tags:"]
            assert disclosure.find("dl", class_="card-grid") is not None
            assert disclosure.find("footer", class_="card-footer") is not None
            assert disclosure.find("a", class_="update-button").get_text(strip=True) == "Propose an update"
            resource_template = soup.find("template", id="resource-card-template")
            resource_template_content = BeautifulSoup(resource_template.decode_contents(), "html.parser")
            assert resource_template_content.find(class_="resource-detail-badges") is not None
            assert resource_template_content.find(class_="resource-tag-badges") is not None
            stylesheet = soup.find("link", rel="stylesheet")
            assert stylesheet["href"].startswith("./styles.css?v=")
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
            assert len(resource_json_content) == 2
            assert resource_json_content[0]["Resource Title"] == "Example resource"
            assert resource_json_content[0]["Year"] == "2026"
            assert resource_json_content[1]["Year"] == ""
            assert resource_json_content[0]["related_risk_urls"][0]["label"] == "#1"
            assert resource_json_content[0]["issue_url"].endswith("/issues/10")
        finally:
            os.chdir(original_cwd)

    def test_render_table_with_newlines(self, tmp_path):
        csv_content = """Issue Title,Description,Likelihood,Severity,Reach,Mitigations,Ownership,Best Practice Examples,Related Risks,Tags,Issue,Updates,Maintainer Notes
"Issue one","Test risk\nwith newline",High,Medium,Low,"Mitigation\ntext","Owner","Examples","","environmental","#1","#1",""
"""
        csv_file = tmp_path / "register" / "risks.csv"
        csv_file.parent.mkdir()
        csv_file.write_text(csv_content)
        write_resource_csv(tmp_path)

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
