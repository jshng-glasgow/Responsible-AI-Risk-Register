from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def read_text(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8")


class TestIssueTemplateContracts:
    def test_new_risk_template_matches_issue_to_csv_parser_fields(self):
        template = read_text(".github/ISSUE_TEMPLATE/new-risk.yml")
        script = read_text(".github/scripts/issue_to_csv.py")

        for label in [
            "Risk",
            "Likelihood",
            "Severity",
            "Reach",
            "Mitigations",
            "Ownership",
            "Examples",
            "Tags",
            "Other Tags",
        ]:
            assert f"label: {label}" in template
            assert f'"{label}"' in script

    def test_update_risk_template_matches_update_csv_parser_fields(self):
        template = read_text(".github/ISSUE_TEMPLATE/update-risk.yml")
        script = read_text(".github/scripts/update_csv.py")

        for label in [
            "Issue Number",
            "Risk",
            "Likelihood",
            "Severity",
            "Reach",
            "Mitigations",
            "Ownership",
            "Examples",
            "Tags",
            "Other Tags",
        ]:
            assert f"label: {label}" in template
            assert f'"{label}"' in script


class TestWorkflowContracts:
    def test_workshop_direct_publish_regenerates_and_deploys_site(self):
        workflow = read_text(".github/workflows/issue-to-csv.yml")

        assert "WORKSHOP_AUTO_PUBLISH_NEW_RISKS == 'true'" in workflow
        assert "python .github/scripts/issue_to_csv.py" in workflow
        assert "python .github/scripts/render_table.py" in workflow
        assert "git add register/risks.csv docs/index.html docs/risks.json" in workflow
        assert "peaceiris/actions-gh-pages@v3" in workflow

    def test_render_workflow_still_tracks_site_generation_inputs(self):
        workflow = read_text(".github/workflows/render-table.yml")

        for path in [
            "register/risks.csv",
            ".github/scripts/render_table.py",
            "docs/app.js",
            "docs/styles.css",
        ]:
            assert f"- '{path}'" in workflow

    def test_test_workflow_runs_pytest_suite(self):
        workflow = read_text(".github/workflows/test.yml")
        requirements = read_text("requirements-dev.txt")

        assert "pip install -r requirements-dev.txt" in workflow
        assert "pytest tests/" in workflow
        for dependency in ["pandas", "pytest", "beautifulsoup4"]:
            assert dependency in requirements
