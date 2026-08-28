const CATEGORY_ORDER = {
  "Unknown": 0,
  "Very Low": 1,
  "Low": 2,
  "Medium": 3,
  "High": 4,
  "Very High": 5
};

const FIELD_LABELS = {
  "Likelihood": "Likelihood",
  "Severity": "Severity",
  "Reach": "Reach",
  "Mitigations": "Mitigations",
  "Ownership": "Ownership",
  "Best Practice Examples": "Best Practice Examples",
  "Issue": "Issue",
  "Updates": "Updates",
  "Maintainer Notes": "Maintainer Notes"
};

const searchInput = document.querySelector("#search-input");
const likelihoodFilter = document.querySelector("#likelihood-filter");
const severityFilter = document.querySelector("#severity-filter");
const reachFilter = document.querySelector("#reach-filter");
const tagFilter = document.querySelector("#tag-filter");
const sortSelect = document.querySelector("#sort-select");
const resultsSummary = document.querySelector("#results-summary");
const registerRoot = document.querySelector("#register-root");
const template = document.querySelector("#risk-card-template");

let allRecords = [];

function populateFilter(select, values) {
  const orderedValues = [...values].sort((left, right) => {
    const leftRank = CATEGORY_ORDER[left];
    const rightRank = CATEGORY_ORDER[right];

    if (leftRank !== undefined || rightRank !== undefined) {
      return (leftRank ?? -1) - (rightRank ?? -1);
    }

    return left.localeCompare(right);
  });

  for (const value of orderedValues) {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = value;
    select.append(option);
  }
}

function matchesSearch(record, query) {
  if (!query) {
    return true;
  }

  const haystack = Object.values(record).join(" ").toLowerCase();
  return haystack.includes(query);
}

function matchesFilters(record) {
  if (likelihoodFilter.value && record["Likelihood"] !== likelihoodFilter.value) {
    return false;
  }

  if (severityFilter.value && record["Severity"] !== severityFilter.value) {
    return false;
  }

  if (reachFilter.value && record["Reach"] !== reachFilter.value) {
    return false;
  }

  if (tagFilter.value) {
    const tags = (record["Tags"] || "").split(",").map((tag) => tag.trim()).filter(Boolean);
    if (!tags.includes(tagFilter.value)) {
      return false;
    }
  }

  return true;
}

function issueNumber(issueRef) {
  if (!issueRef || !issueRef.startsWith("#")) {
    return -1;
  }
  return Number.parseInt(issueRef.slice(1), 10);
}

function sortRecords(records) {
  const [field, direction] = sortSelect.value.split("-");
  const multiplier = direction === "desc" ? -1 : 1;

  return [...records].sort((left, right) => {
    if (field === "description") {
      return left["Description"].localeCompare(right["Description"]) * multiplier;
    }

    if (field === "issue") {
      return (issueNumber(left["Issue"]) - issueNumber(right["Issue"])) * multiplier;
    }

    const leftValue = CATEGORY_ORDER[left[capitalize(field)]] ?? -1;
    const rightValue = CATEGORY_ORDER[right[capitalize(field)]] ?? -1;

    if (leftValue === rightValue) {
      return left["Description"].localeCompare(right["Description"]);
    }

    return (leftValue - rightValue) * multiplier;
  });
}

function capitalize(value) {
  return value.charAt(0).toUpperCase() + value.slice(1);
}

function createBadge(text, tone) {
  const badge = document.createElement("span");
  badge.className = `badge tone-${tone.toLowerCase().replace(/\s+/g, "-")}`;
  badge.textContent = text;
  return badge;
}

function appendTextOrPlaceholder(container, value) {
  if (!value) {
    const muted = document.createElement("span");
    muted.className = "muted";
    muted.textContent = "Not provided";
    container.append(muted);
    return;
  }

  const lines = value.split("\n");
  lines.forEach((line, index) => {
    if (index > 0) {
      container.append(document.createElement("br"));
    }
    container.append(document.createTextNode(line));
  });
}

function appendIssueLinks(container, links) {
  if (!links || links.length === 0) {
    appendTextOrPlaceholder(container, "");
    return;
  }

  links.forEach((item, index) => {
    const anchor = document.createElement("a");
    anchor.href = item.url || "#";
    anchor.target = "_blank";
    anchor.rel = "noreferrer";
    anchor.textContent = item.label;
    container.append(anchor);

    if (index < links.length - 1) {
      container.append(document.createTextNode(", "));
    }
  });
}

function buildRow(label, contentBuilder) {
  const term = document.createElement("dt");
  term.textContent = label;

  const description = document.createElement("dd");
  contentBuilder(description);

  return [term, description];
}

function renderRecord(record) {
  const fragment = template.content.cloneNode(true);
  const article = fragment.querySelector(".risk-card");
  const meta = fragment.querySelector(".card-meta");
  const title = fragment.querySelector(".card-title");
  const grid = fragment.querySelector(".card-grid");

  title.textContent = record["Issue Title"] || record["Description"];
  meta.append(
    createBadge(`${record["Likelihood"] || "Unknown"} Likelihood`, record["Likelihood"] || "Unknown"),
    createBadge(`${record["Severity"] || "Unknown"} Severity`, record["Severity"] || "Unknown"),
    createBadge(`${record["Reach"] || "Unknown"} Reach`, record["Reach"] || "Unknown")
  );
  const tags = (record["Tags"] || "").split(",").map((tag) => tag.trim()).filter(Boolean);
  tags.forEach((tag) => meta.append(createBadge(tag, "tag")));

  const fields = [
    buildRow("Description", (container) => appendTextOrPlaceholder(container, record["Description"])),
    buildRow("Likelihood", (container) => appendTextOrPlaceholder(container, record["Likelihood"])),
    buildRow("Severity", (container) => appendTextOrPlaceholder(container, record["Severity"])),
    buildRow("Reach", (container) => appendTextOrPlaceholder(container, record["Reach"])),
    buildRow("Mitigations", (container) => appendTextOrPlaceholder(container, record["Mitigations"])),
    buildRow("Ownership", (container) => appendTextOrPlaceholder(container, record["Ownership"])),
    buildRow("Best Practice Examples", (container) => appendTextOrPlaceholder(container, record["Best Practice Examples"])),
    buildRow("Related Risks", (container) => appendIssueLinks(container, record["related_risk_urls"])),
    buildRow("Tags", (container) => appendTextOrPlaceholder(container, record["Tags"])),
    buildRow("Issue", (container) => {
      appendIssueLinks(container, record["issue_url"] ? [{ label: record["Issue"], url: record["issue_url"] }] : []);
    }),
    buildRow("Updates", (container) => appendIssueLinks(container, record["update_urls"])),
    buildRow("Maintainer Notes", (container) => appendTextOrPlaceholder(container, record["Maintainer Notes"]))
  ];

  for (const [term, description] of fields) {
    grid.append(term, description);
  }

  registerRoot.append(article);
}

function render() {
  const query = searchInput.value.trim().toLowerCase();
  const filteredRecords = sortRecords(
    allRecords.filter((record) => matchesSearch(record, query) && matchesFilters(record))
  );

  registerRoot.replaceChildren();

  if (filteredRecords.length === 0) {
    const emptyState = document.createElement("p");
    emptyState.className = "empty-state";
    emptyState.textContent = "No risks match the current filters.";
    registerRoot.append(emptyState);
  } else {
    filteredRecords.forEach(renderRecord);
  }

  resultsSummary.textContent = `${filteredRecords.length} of ${allRecords.length} risks shown`;
}

async function init() {
  try {
    const assetVersion = window.REGISTER_ASSET_VERSION || "dev";
    const response = await fetch(`./risks.json?v=${encodeURIComponent(assetVersion)}`, { cache: "no-store" });
    allRecords = await response.json();

    populateFilter(likelihoodFilter, new Set(allRecords.map((record) => record["Likelihood"]).filter(Boolean)));
    populateFilter(severityFilter, new Set(allRecords.map((record) => record["Severity"]).filter(Boolean)));
    populateFilter(reachFilter, new Set(allRecords.map((record) => record["Reach"]).filter(Boolean)));
    populateFilter(
      tagFilter,
      new Set(
        allRecords
          .flatMap((record) => (record["Tags"] || "").split(","))
          .map((tag) => tag.trim())
          .filter(Boolean)
      )
    );

    [searchInput, likelihoodFilter, severityFilter, reachFilter, tagFilter, sortSelect].forEach((element) => {
      element.addEventListener("input", render);
      element.addEventListener("change", render);
    });

    render();
  } catch (error) {
    resultsSummary.textContent = "Unable to load the register data.";
    registerRoot.textContent = "Please try again later.";
    console.error(error);
  }
}

init();
