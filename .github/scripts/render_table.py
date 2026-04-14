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
    <link rel="stylesheet" href="./styles.css">
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
                <input id="search-input" type="search" placeholder="Search risks, mitigations, ownership, examples..." />
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
                    <option value="risk-asc">Risk (A-Z)</option>
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
            <div class="card-header">
                <div class="card-meta"></div>
                <h2 class="card-title"></h2>
            </div>
            <dl class="card-grid"></dl>
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
    if not issue_ref or not isinstance(issue_ref, str) or not issue_ref.startswith("#"):
        return None
    return f"https://github.com/jshng-glasgow/SSI-Responsbile-AI-Risk-Register/issues/{issue_ref[1:]}"


def normalise_text(value):
    if pd.isna(value):
        return ""
    return str(value)


def serialise_records(dataframe):
    records = []
    for row in dataframe.to_dict(orient="records"):
        clean_row = {key: normalise_text(value) for key, value in row.items()}
        clean_row["issue_url"] = build_issue_url(clean_row.get("Issue", ""))
        clean_row["update_refs"] = [ref.strip() for ref in clean_row.get("Updates", "").split(",") if ref.strip()]
        clean_row["update_urls"] = [
            {"label": ref, "url": build_issue_url(ref)}
            for ref in clean_row["update_refs"]
        ]
        records.append(clean_row)
    return records


def build_asset_version(records):
    payload = json.dumps(records, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:12]


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
