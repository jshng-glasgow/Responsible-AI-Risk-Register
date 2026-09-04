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
const resourceSearchInput = document.querySelector("#resource-search-input");
const resourceYearFilter = document.querySelector("#resource-year-filter");
const resourceTypeFilter = document.querySelector("#resource-type-filter");
const resourceTagFilter = document.querySelector("#resource-tag-filter");
const resourceSortSelect = document.querySelector("#resource-sort-select");
const resourceResultsSummary = document.querySelector("#resource-results-summary");
const resourcesRoot = document.querySelector("#resources-root");
const resourceTemplate = document.querySelector("#resource-card-template");
const risksView = document.querySelector("#risks-view");
const resourcesView = document.querySelector("#resources-view");
const risksTab = document.querySelector("#risks-tab");
const resourcesTab = document.querySelector("#resources-tab");

let allRecords = [];
let allResources = [];

function populateFilter(select, values, compareValues) {
  const defaultComparison = (left, right) => {
    const leftRank = CATEGORY_ORDER[left];
    const rightRank = CATEGORY_ORDER[right];

    if (leftRank !== undefined || rightRank !== undefined) {
      return (leftRank ?? -1) - (rightRank ?? -1);
    }

    return left.localeCompare(right);
  };
  const orderedValues = [...values].sort(compareValues || defaultComparison);

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

function appendExternalLink(container, url, label) {
  if (!url) {
    appendTextOrPlaceholder(container, "");
    return;
  }

  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.target = "_blank";
  anchor.rel = "noreferrer";
  anchor.textContent = label;
  container.append(anchor);
}

function buildRiskUpdateUrl(record) {
  const url = new URL("https://github.com/jshng-glasgow/Responsible-AI-Risk-Register/issues/new");
  url.searchParams.set("template", "update-risk.yml");
  url.searchParams.set("issue_number", record["Issue"]);
  url.searchParams.set("title", `Update risk ${record["Issue"]}: ${record["Issue Title"]}`);
  return url.toString();
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
  const impactBadges = fragment.querySelector(".impact-badges");
  const tagBadges = fragment.querySelector(".tag-badges");
  const title = fragment.querySelector(".card-title");
  const grid = fragment.querySelector(".card-grid");
  const updateLink = fragment.querySelector(".update-button");

  title.textContent = record["Issue Title"] || record["Description"];
  updateLink.href = buildRiskUpdateUrl(record);
  impactBadges.append(
    createBadge(`${record["Likelihood"] || "Unknown"} Likelihood`, record["Likelihood"] || "Unknown"),
    createBadge(`${record["Severity"] || "Unknown"} Severity`, record["Severity"] || "Unknown"),
    createBadge(`${record["Reach"] || "Unknown"} Reach`, record["Reach"] || "Unknown")
  );
  const tags = (record["Tags"] || "").split(",").map((tag) => tag.trim()).filter(Boolean);
  tags.forEach((tag) => tagBadges.append(createBadge(tag, "tag")));

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

function matchesResourceFilters(record) {
  if (resourceYearFilter.value && record["Year"] !== resourceYearFilter.value) {
    return false;
  }
  if (resourceTypeFilter.value && record["Type"] !== resourceTypeFilter.value) {
    return false;
  }
  if (resourceTagFilter.value) {
    const tags = (record["Tags"] || "").split(",").map((tag) => tag.trim()).filter(Boolean);
    if (!tags.includes(resourceTagFilter.value)) {
      return false;
    }
  }
  return true;
}

function sortResources(records) {
  const [field, direction] = resourceSortSelect.value.split("-");
  const multiplier = direction === "desc" ? -1 : 1;

  return [...records].sort((left, right) => {
    if (field === "year") {
      const yearDifference = (Number(left["Year"]) || 0) - (Number(right["Year"]) || 0);
      if (yearDifference !== 0) {
        return yearDifference * multiplier;
      }
    }

    if (field === "type") {
      const typeDifference = (left["Type"] || "").localeCompare(right["Type"] || "") * multiplier;
      if (typeDifference !== 0) {
        return typeDifference;
      }
    }
    return (left["Resource Title"] || "").localeCompare(right["Resource Title"] || "");
  });
}

function renderResource(record) {
  const fragment = resourceTemplate.content.cloneNode(true);
  const article = fragment.querySelector(".resource-card");
  const title = fragment.querySelector(".card-title");
  const detailBadges = fragment.querySelector(".resource-detail-badges");
  const tagBadges = fragment.querySelector(".resource-tag-badges");
  const grid = fragment.querySelector(".card-grid");

  title.textContent = record["Resource Title"];
  detailBadges.append(
    createBadge(record["Type"] || "Other", "resource"),
    createBadge(record["Year"] || "Year unknown", "year")
  );

  const tags = (record["Tags"] || "").split(",").map((tag) => tag.trim()).filter(Boolean);
  if (tags.length === 0) {
    tagBadges.append(createBadge("Not tagged", "unknown"));
  } else {
    tags.forEach((tag) => tagBadges.append(createBadge(tag, "tag")));
  }

  const fields = [
    buildRow("Resource", (container) => appendExternalLink(container, record["URL"], "Open resource")),
    buildRow("Organisation / Authors", (container) => appendTextOrPlaceholder(container, record["Organisation / Authors"])),
    buildRow("Year", (container) => appendTextOrPlaceholder(container, record["Year"])),
    buildRow("Type", (container) => appendTextOrPlaceholder(container, record["Type"])),
    buildRow("Relevance", (container) => appendTextOrPlaceholder(container, record["Relevance"]))
  ];

  if (record["Tags"]) {
    fields.push(buildRow("Tags", (container) => appendTextOrPlaceholder(container, record["Tags"])));
  }
  if (record["related_risk_urls"].length > 0) {
    fields.push(buildRow("Related Risks", (container) => appendIssueLinks(container, record["related_risk_urls"])));
  }
  if (record["Notes"]) {
    fields.push(buildRow("Notes", (container) => appendTextOrPlaceholder(container, record["Notes"])));
  }
  if (record["issue_url"]) {
    fields.push(buildRow("Issue", (container) => {
      appendIssueLinks(container, [{ label: record["Issue"], url: record["issue_url"] }]);
    }));
  }
  if (record["Maintainer Notes"]) {
    fields.push(buildRow("Maintainer Notes", (container) => appendTextOrPlaceholder(container, record["Maintainer Notes"])));
  }

  for (const [term, description] of fields) {
    grid.append(term, description);
  }
  resourcesRoot.append(article);
}

function renderResources() {
  const query = resourceSearchInput.value.trim().toLowerCase();
  const filteredResources = sortResources(
    allResources.filter((record) => matchesSearch(record, query) && matchesResourceFilters(record))
  );

  resourcesRoot.replaceChildren();
  if (filteredResources.length === 0) {
    const emptyState = document.createElement("p");
    emptyState.className = "empty-state";
    emptyState.textContent = "No resources match the current filters.";
    resourcesRoot.append(emptyState);
  } else {
    filteredResources.forEach(renderResource);
  }
  resourceResultsSummary.textContent = `${filteredResources.length} of ${allResources.length} resources shown`;
}

function activateView() {
  const showingResources = window.location.hash === "#resources";
  risksView.hidden = showingResources;
  resourcesView.hidden = !showingResources;
  if (showingResources) {
    resourcesTab.setAttribute("aria-current", "page");
    risksTab.removeAttribute("aria-current");
  } else {
    risksTab.setAttribute("aria-current", "page");
    resourcesTab.removeAttribute("aria-current");
  }
}

async function init() {
  try {
    const assetVersion = window.REGISTER_ASSET_VERSION || "dev";
    const [riskResponse, resourceResponse] = await Promise.all([
      fetch(`./risks.json?v=${encodeURIComponent(assetVersion)}`, { cache: "no-store" }),
      fetch(`./resources.json?v=${encodeURIComponent(assetVersion)}`, { cache: "no-store" })
    ]);
    if (!riskResponse.ok || !resourceResponse.ok) {
      throw new Error("Unable to load register data");
    }
    allRecords = await riskResponse.json();
    allResources = await resourceResponse.json();

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
    populateFilter(
      resourceYearFilter,
      new Set(allResources.map((record) => record["Year"]).filter(Boolean)),
      (left, right) => Number(right) - Number(left)
    );
    populateFilter(resourceTypeFilter, new Set(allResources.map((record) => record["Type"]).filter(Boolean)));
    populateFilter(
      resourceTagFilter,
      new Set(
        allResources
          .flatMap((record) => (record["Tags"] || "").split(","))
          .map((tag) => tag.trim())
          .filter(Boolean)
      )
    );

    [searchInput, likelihoodFilter, severityFilter, reachFilter, tagFilter, sortSelect].forEach((element) => {
      element.addEventListener("input", render);
      element.addEventListener("change", render);
    });
    [resourceSearchInput, resourceYearFilter, resourceTypeFilter, resourceTagFilter, resourceSortSelect].forEach((element) => {
      element.addEventListener("input", renderResources);
      element.addEventListener("change", renderResources);
    });

    render();
    renderResources();
    activateView();
  } catch (error) {
    resultsSummary.textContent = "Unable to load the register data.";
    registerRoot.textContent = "Please try again later.";
    resourceResultsSummary.textContent = "Unable to load the resource data.";
    resourcesRoot.textContent = "Please try again later.";
    console.error(error);
  }
}

window.addEventListener("hashchange", activateView);
activateView();
init();
