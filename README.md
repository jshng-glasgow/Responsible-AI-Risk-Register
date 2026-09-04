# Responsible AI Risk Register

![Institute for Research Software logo](assets/Primary%20logo%20-%20Dark%20Navy.png)

A community-maintained register of risks associated with the use of AI in 
Research Software Engineering, maintained by the Institute for Research Software's Responsible AI Study Group.

## What is this?

This register has been developed by the Institute for Research Software's Responsible AI in RSE study group. The Institute was previously known as the Software Sustainability Institute (SSI). The register is designed to encourage continual contribution from the research software engineering (RSE) community, allow them to identify the AI risks that are most pertinent to them, and curate resources that can help the community understand or manage those risks. As the AI landscape continues to evolve, it is crucial that we develop guidelines which are relevant, adaptable, and actionable. This risk register will allow us to achieve that.

## Scope

This register is intended to capture risks in the use of generative AI in the development of research software. While there are valid concerns around the use of AI more generally as an analytic tool, or of generative AI in other areas of science, these are best addressed through discussion with the wider academic community.

Risks need not be applicable to all RSEs in all fields. If there are risks that are specific to your work then please include them — you may be surprised how relevant they are to others!

## How to Contribute

Details of how to contribute are in [CONTRIBUTING.md](CONTRIBUTING.md). Contributions can be made with or without a GitHub account.

To propose a new risk, go to the "Issues" tab and select "New issue" and "Propose new risk". See below for detailed information about each field. If you don't have a GitHub account, then a risk can be added manually using this [Microsoft form](https://forms.office.com/e/NAYjcGiF7i).

To suggest a supporting resource, use the "Propose a new resource" issue form. Resource submissions are stored in [resources/resources.csv](resources/resources.csv) and displayed in the [Resources section of the live register](https://jshng-glasgow.github.io/SSI-Responsible-AI-Risk-Register/#resources).

If you would like to be recognised as a contributor to the register, please add your name to [CONTRIBUTORS.md](CONTRIBUTORS.md) via a pull request.

## The Register

The live register brings together two connected collections:

* **Risks** document potential harms associated with using generative AI in Research Software Engineering, along with their impact, mitigations, ownership, and related information.
* **Resources** collect policies, guidance, position papers, case studies, and reports that can help the community understand or manage those risks.

Both collections can be browsed, searched, sorted, and filtered in the [live register](https://jshng-glasgow.github.io/SSI-Responsible-AI-Risk-Register/). Risk data is stored in [register/risks.csv](register/risks.csv), and resource data is stored in [resources/resources.csv](resources/resources.csv).

### Risk fields

The register contains:

* Ten contributor-editable fields, including the GitHub issue title and nine fields submitted through the issue form.
* One maintainer-only field, **Maintainer Notes**, which is used to document editorial decisions and is not submitted through the public issue templates.

Please be as descriptive as possible when filling in the contributor-editable fields. An explanation of each field is given below.

**Issue Title**: A short title used to identify the entry in the register and reduce ambiguity during submission and review.

**Description**: A description of the nature of the risk — who does it affect? What are the potential outcomes?

**Likelihood**: Choice of *Very Low*, *Low*, *Medium*, *High*, *Very High*, or *Unknown*.

* *Very Low* -- Highly unlikely to occur in normal RSE practice, even in the long term.
* *Low* -- Unlikely to occur in normal RSE practice, even in the long term.
* *Medium* -- Plausible and has been observed in similar contexts, or likely to be an issue in the near future.
* *High* -- Commonly encountered or well-documented. A current and existing issue.
* *Very High* -- Extremely likely, pervasive, or already difficult to avoid in current practice.
* *Unknown* -- Evidence is lacking or highly contested.

**Severity**: Choice of *Very Low*, *Low*, *Medium*, *High*, *Very High*, or *Unknown*.

* *Very Low* -- Minimal impact and easily remedied. Little or no lasting effect on outputs or individuals.
* *Low* -- Minor inconvenience or easily remedied. Limited impact on research outputs or individuals.
* *Medium* -- Meaningful impact on research quality, professional practice, or individuals. Recoverable but non-trivial.
* *High* -- Significant harm to research integrity, individuals, or communities. Potentially irreversible.
* *Very High* -- Severe or systemic harm with major consequences for research integrity, people, or communities.
* *Unknown* -- Severity is highly context-dependent or insufficient evidence exists to assess.

**Reach**: Choice of *Very Low*, *Low*, *Medium*, *High*, *Very High*, or *Unknown*.

* *Very Low* -- The impact is very narrow, affecting only an individual task, person, or isolated activity.
* *Low* -- The impact affects a small number of people or a single project/team.
* *Medium* -- The impact affects several people, projects, or teams in a contained but meaningful way.
* *High* -- The impact is broad, affecting a department, institution, or substantial part of the RSE community.
* *Very High* -- The impact is systemic or widely felt across multiple institutions, communities, or the wider research ecosystem.
* *Unknown* -- The available evidence is insufficient to assess how widely the impact would spread.

**Mitigations**: (Optional) Any potential ways in which the risk might be mitigated, either through changing RSE practice, institutional policy, or other means.

**Ownership**: (Optional) Who is responsible for addressing this risk? This might be practitioners, institutions, funders, government, or tool developers. It might be multiple people or groups.

**Best Practice Examples**: (Optional) Are there examples of institutions or organisations handling this risk well? Please provide relevant links or evidence where available; this field is not for examples of the risk occurring.

**Related Risks**: (Optional) Issue numbers for risks that overlap with, duplicate, or closely relate to this entry. This helps contributors and maintainers spot potential overlap without immediately merging submissions.

**Tags**: (Optional) Short category labels used to group similar risks in the public register. Contributors can select as many tags as are useful and may also suggest additional tags using the free-text `Other Tags` field in the issue form.

The current standard tags are:

* **Economic**: Risks relating to cost, resourcing, procurement, funding, or wider economic impacts of AI-led development.
* **Environmental**: Risks relating to energy use, emissions, water consumption, resource extraction, or other environmental harms.
* **Equity and Fiarness**: Risks that create or worsen exclusion, unequal access, unfair burden, or biased outcomes across individuals or groups.
* **Governance**: Risks relating to oversight, accountability, policy, regulation, institutional processes, or decision-making responsibilities.
* **People and Professional Practice**: Risks affecting the role, identity, autonomy, recognition, or working conditions of RSEs and related professionals.
* **Privacy and Security**: Risks involving confidential data, sensitive code, insecure generated software, access control, or other privacy and security harms.
* **Research Integrity**: Risks to the correctness, reproducibility, provenance, transparency, or reliability of research software and outputs.
* **Software Sustainability**: Risks to the long-term maintainability, supportability, portability, documentation, or resilience of research software.
* **Training and Development**: Risks relating to skills erosion, learning pathways, mentoring, onboarding, or the development of future capability.
* **Wider Societal Impacts**: Risks with broader consequences for communities, public trust, public institutions, or society beyond a single team or project.

**Issue**: (Not editable) A unique identifier for the risk, which can be used to reference it when submitting updates.

**Maintainer Notes**: (Maintainer only) Editorial notes used to record synthesis decisions, conflicting assessments, and links back to related issues when multiple submissions are combined.

This field is intended to help maintainers preserve provenance when risks are merged or revised. For example, it may be used to note that an entry was synthesised from multiple issues, that contributors disagreed on severity or likelihood, or that a conservative editorial judgement was applied when combining overlapping submissions.

### Resources

The Resources section contains supporting policies, guidance, position papers, case studies, reports, and other material relevant to responsible use of AI in Research Software Engineering.

To propose a resource, open a GitHub issue and select **Propose a new resource**. Submissions should include a stable link to the original resource and a short explanation of its relevance to the register. Contributors can also assign topic tags and identify specific risks that the resource helps address.

Resource submissions are reviewed through the same contribution workflow as risks. Accepted submissions are stored in [resources/resources.csv](resources/resources.csv) and appear in the searchable [Resources view](https://jshng-glasgow.github.io/SSI-Responsible-AI-Risk-Register/#resources).

The repository normally links to third-party resources rather than storing local copies. Files should only be included directly when preservation is necessary, stable linking is unavailable, and redistribution is permitted.

## Governance

The register is maintained by the Institute for Research Software's Responsible AI in RSE study group. All edits to the register (e.g., new risks, updates to existing risks) are reviewed by the study group. The register is periodically reviewed to merge similar risks and remove redundancy.

For workshop facilitation, maintainers can temporarily set the GitHub Actions repository variable `WORKSHOP_AUTO_PUBLISH_NEW_RISKS=true`. When enabled, issues labelled `new risk` or `new resource` are written directly to the default branch instead of opening a pull request. Issues labelled `risk update` continue to create pull requests for manual review.

## Data Usage and Confidentiality

Contributions to this register are made publicly under CC BY 4.0 and may be used in future research. No personally identifying information should be included in contributions.

## AI Assistance Disclosure

This repository was developed with assistance from OpenAI Codex. AI-assisted contributions, including code, tests, and documentation, have been reviewed, tested, and approved by an experienced human software engineer for correctness, security, and fitness for purpose.

## Funding

This work was supported through the UKRI Metascience Unit "Metascience AI" fellowship programme.

![UKRI and Metascience Unit logos](assets/metascience_UKRI.webp)

## Citation

Please cite as:

```text
@misc{ssi_ai_risk_register_2026,
  author       = {Shingleton, Joseph and {Institute for Research Software Responsible AI Study Group}},
  title        = {{Responsible AI Risk Register}},
  year         = {2026},
  publisher    = {Institute for Research Software},
  howpublished = {\url{https://github.com/jshng-glasgow/SSI-Responsbile-AI-Risk-Register/}}
}
```
