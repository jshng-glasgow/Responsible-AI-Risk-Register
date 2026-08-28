"""Render the published HTML shell and JSON payload for the risk register."""

import hashlib
import json
import os

import pandas as pd


CSV_PATH = "register/risks.csv"
DOCS_DIR = "docs"
HTML_PATH = os.path.join(DOCS_DIR, "index.html")
JSON_PATH = os.path.join(DOCS_DIR, "risks.json")


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SSI Generative AI Risk Register</title>
    <link rel="stylesheet" href="./styles.css?v={asset_version}">
</head>
<body>
    <main class="page-shell">
        <section class="hero">
            <p class="eyebrow">Software Sustainability Institute</p>
            <h1>Generative AI Risk Register</h1>
            <p class="intro">
                A community-maintained register of risks associated with AI in Research Software Engineering.
                Browse, search, sort, and filter the current register below.
            </p>
            <div class="hero-actions">
                <a class="button button-primary" href="https://github.com/jshng-glasgow/SSI-Responsible-AI-Risk-Register/" target="_blank" rel="noreferrer">Contribute on GitHub</a>
                <a class="button button-secondary" href="./risks.json" target="_blank" rel="noreferrer">Download JSON</a>
            </div>
        </section>

        <section class="controls-panel" aria-label="Register controls">
            <div class="control">
                <label for="search-input">Search</label>
                <input id="search-input" type="search" placeholder="Search titles, descriptions, mitigations, ownership, best practice examples..." />
            </div>
            <div class="control">
                <label for="likelihood-filter">Likelihood</label>
                <select id="likelihood-filter">
                    <option value="">All</option>
                </select>
            </div>
            <div class="control">
                <label for="severity-filter">Severity</label>
                <select id="severity-filter">
                    <option value="">All</option>
                </select>
            </div>
            <div class="control">
                <label for="reach-filter">Reach</label>
                <select id="reach-filter">
                    <option value="">All</option>
                </select>
            </div>
            <div class="control">
                <label for="tag-filter">Tag</label>
                <select id="tag-filter">
                    <option value="">All</option>
                </select>
            </div>
            <div class="control">
                <label for="sort-select">Sort by</label>
                <select id="sort-select">
                    <option value="description-asc">Description (A-Z)</option>
                    <option value="likelihood-desc">Likelihood (highest first)</option>
                    <option value="severity-desc">Severity (highest first)</option>
                    <option value="reach-desc">Reach (highest first)</option>
                    <option value="issue-desc">Most recent issue</option>
                </select>
            </div>
        </section>

        <section class="results-bar" aria-live="polite">
            <p id="results-summary">Loading register...</p>
        </section>

        <section id="register-root" class="register-root" aria-live="polite"></section>
    </main>

    <template id="risk-card-template">
        <article class="risk-card">
            <details class="risk-details">
                <summary class="card-summary">
                    <span class="card-header">
                        <span class="card-title" role="heading" aria-level="2"></span>
                        <span class="card-meta">
                            <span class="meta-group">
                                <span class="meta-label">Impact:</span>
                                <span class="badge-list impact-badges"></span>
                            </span>
                            <span class="meta-group">
                                <span class="meta-label">Tags:</span>
                                <span class="badge-list tag-badges"></span>
                            </span>
                        </span>
                    </span>
                    <span class="toggle-label" aria-hidden="true">
                        <span class="when-collapsed">View details</span>
                        <span class="when-expanded">Hide details</span>
                    </span>
                </summary>
                <dl class="card-grid"></dl>
            </details>
        </article>
    </template>

    <script>
        window.REGISTER_ASSET_VERSION = "{asset_version}";
    </script>
    <script src="./app.js?v={asset_version}"></script>
</body>
</html>
"""


def build_issue_url(issue_ref):
    """Return the GitHub issue URL for a ``#123`` style reference."""
    if not issue_ref or not isinstance(issue_ref, str) or not issue_ref.startswith("#"):
        return None
    return f"https://github.com/jshng-glasgow/SSI-Responsbile-AI-Risk-Register/issues/{issue_ref[1:]}"


def normalise_text(value):
    """Convert DataFrame values into serialisable strings."""
    if pd.isna(value):
        return ""
    return str(value)


def serialise_issue_refs(value):
    """Convert a comma-separated issue list into label and URL objects."""
    refs = [ref.strip() for ref in value.split(",") if ref.strip()]
    return refs, [{"label": ref, "url": build_issue_url(ref)} for ref in refs]


def serialise_records(dataframe):
    """Convert the risk register DataFrame into JSON-ready records."""
    records = []
    for row in dataframe.to_dict(orient="records"):
        clean_row = {key: normalise_text(value) for key, value in row.items()}
        clean_row["related_risk_refs"], clean_row["related_risk_urls"] = serialise_issue_refs(
            clean_row.get("Related Risks", "")
        )
        clean_row["issue_url"] = build_issue_url(clean_row.get("Issue", ""))
        clean_row["update_refs"], clean_row["update_urls"] = serialise_issue_refs(clean_row.get("Updates", ""))
        records.append(clean_row)
    return records


def build_asset_version(records):
    """Create a stable short hash used to bust cached data and frontend assets."""
    digest = hashlib.sha256(json.dumps(records, sort_keys=True, ensure_ascii=False).encode("utf-8"))
    for asset_name in ("app.js", "styles.css"):
        asset_path = os.path.join(DOCS_DIR, asset_name)
        if os.path.exists(asset_path):
            with open(asset_path, "rb") as asset_file:
                digest.update(asset_file.read())
    return digest.hexdigest()[:12]


if __name__ == "__main__":
    os.makedirs(DOCS_DIR, exist_ok=True)

    dataframe = pd.read_csv(CSV_PATH).fillna("")
    records = serialise_records(dataframe)
    asset_version = build_asset_version(records)

    with open(JSON_PATH, "w", encoding="utf-8") as json_file:
        json.dump(records, json_file, indent=2, ensure_ascii=False)

    with open(HTML_PATH, "w", encoding="utf-8") as html_file:
        html_file.write(HTML_TEMPLATE.format(asset_version=asset_version))

    print(f"Generated {HTML_PATH}")
    print(f"Generated {JSON_PATH}")
