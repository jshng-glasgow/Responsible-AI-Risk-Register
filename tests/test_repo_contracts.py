from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def read_text(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8")


class TestIssueTemplateContracts:
    def test_new_risk_template_matches_issue_to_csv_parser_fields(self):
        template = read_text(".github/ISSUE_TEMPLATE/new-risk.yml")
        script = read_text(".github/scripts/issue_to_csv.py")

        for label in [
            "Description",
            "Likelihood",
            "Severity",
            "Reach",
            "Mitigations",
            "Ownership",
            "Best Practice Examples",
            "Related Risks",
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
            "Description",
            "Likelihood",
            "Severity",
            "Reach",
            "Mitigations",
            "Ownership",
            "Best Practice Examples",
            "Related Risks",
            "Tags Action",
            "Tags",
            "Other Tags",
        ]:
            assert f"label: {label}" in template
            assert f'"{label}"' in script

    def test_update_risk_impact_fields_default_to_no_changes(self):
        template = read_text(".github/ISSUE_TEMPLATE/update-risk.yml")

        options = "options: [No changes, Very Low, Low, Medium, High, Very High, Unknown]"
        assert template.count(options) == 3
        assert template.count("default: 0") >= 4
        assert "placeholder: Leave blank if you are not proposing a change to the mitigations." in template
        assert "placeholder: Leave blank if you are not proposing a change to the ownership." in template
        assert "placeholder: Leave blank if you are not proposing a change to the best practice examples." in template

    def test_new_resource_template_matches_resource_to_csv_parser_fields(self):
        template = read_text(".github/ISSUE_TEMPLATE/new-resource.yml")
        script = read_text(".github/scripts/resource_to_csv.py")

        for label in [
            "Resource Title",
            "URL",
            "Organisation / Authors",
            "Year",
            "Type",
            "Relevance",
            "Tags",
            "Other Tags",
            "Related Risks",
            "Notes",
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
            "resources/resources.csv",
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

    def test_resource_issue_workflow_uses_prs_except_in_workshop_mode(self):
        workflow = read_text(".github/workflows/resource-to-csv.yml")

        assert "github.event.label.name == 'new resource'" in workflow
        assert "WORKSHOP_AUTO_PUBLISH_NEW_RISKS == 'true'" in workflow
        assert "python .github/scripts/resource_to_csv.py" in workflow
        assert "python .github/scripts/validate_resources.py" in workflow
        assert "python .github/scripts/render_table.py" in workflow
        assert "git add resources/resources.csv docs/index.html docs/resources.json" in workflow
        assert "peaceiris/actions-gh-pages@v3" in workflow
        assert "peter-evans/create-pull-request@v6" in workflow

    def test_risk_update_workflow_includes_field_change_summary(self):
        workflow = read_text(".github/workflows/update-csv.yml")

        assert "UPDATE_SUMMARY_PATH: .github/update-summary.md" in workflow
        assert "body-path: .github/update-summary.md" in workflow
        assert "add-paths: register/risks.csv" in workflow

    def test_register_ui_prefills_risk_update_issue_number(self):
        app = read_text("docs/app.js")

        assert 'url.searchParams.set("template", "update-risk.yml")' in app
        assert 'url.searchParams.set("issue_number", record["Issue"])' in app
