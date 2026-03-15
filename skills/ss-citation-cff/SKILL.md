---
name: ss-citation-cff
description: >-
  Generate CITATION.cff files for GitHub repositories. Creates machine-readable
  citation metadata that GitHub renders as a "Cite this repository" button with
  APA and BibTeX export. Use when the user wants to make their repo citable,
  add a citation file, create a CITATION.cff, or enable the GitHub cite button.
  Triggers on "citation", "CITATION.cff", "cite this repo", "make citable",
  "add citation", "how to cite".
allowed-tools:
  - Read
  - Glob
  - Grep
  - Edit
  - Write
  - Bash
  - WebFetch
  - WebSearch
---

# Citation File Format (CFF) Generator

Generate valid `CITATION.cff` files that activate GitHub's "Cite this repository" sidebar button with APA and BibTeX export.

## When to Use

- User wants to add citation metadata to a repository
- User asks about making a repo citable on GitHub
- User mentions CITATION.cff or the "Cite this repository" button
- User wants APA/BibTeX citations for their software or dataset
- After a release, when citation metadata needs updating

## When NOT to Use

- User wants a `CITATION.md` (plain markdown) — just write markdown directly
- User wants to cite someone else's work — point them to the repo's cite button
- User needs a full bibliography manager — suggest Zotero or BibTeX tools

## Phase 1 — Gather Metadata

**Entry:** User requests a CITATION.cff file.

### Step 1a — Extract project metadata from local files

Read these files (skip missing ones silently):
- `package.json`, `pyproject.toml`, `Cargo.toml`, `setup.cfg`, `setup.py` — title, version, description, authors, URLs
- `CITATION.cff` — if one exists, read it for update rather than overwrite
- `README.md` — project description, author info
- `LICENSE`, `LICENSE.md`, `LICENSE.txt`, `COPYING` — detect the SPDX license identifier from file contents. **Do not ask the user for a license if a LICENSE file exists in the repo root.** Map common license texts to SPDX identifiers (e.g., "MIT License" → `MIT`, "Apache License, Version 2.0" → `Apache-2.0`, "GNU General Public License" → `GPL-3.0-or-later`).
- `git remote get-url origin` — repository URL
- `git log --format='%aN <%aE>' | sort -u` — contributor list for author suggestions
- `git describe --tags --abbrev=0 2>/dev/null` — latest version tag

### Step 1b — Enrich author info from GitHub API and profile

Run these commands to populate the primary author automatically:

```bash
# Primary user profile (name, company/affiliation, blog/website, location)
gh api user --jq '{name, company, blog, location, login, email}'

# Verified emails (pick primary)
gh api user/emails --jq '.[] | select(.primary==true) | .email'

# Social accounts (may contain ORCID link)
gh api user/social_accounts --jq '.[].url'
```

**IMPORTANT — Scrape the GitHub profile page for ORCID:**
The GitHub REST/GraphQL API does NOT expose ORCID or all social links. The rendered profile page does. Use WebFetch on `https://github.com/{login}` and look for `orcid.org` links. This is the most reliable way to find ORCID on GitHub.

Extract from all sources:
- **name** → split into `given-names` and `family-names` (last token = family name, rest = given names)
- **company** → `affiliation`
- **email** → `email` (use primary verified email from `/user/emails`)
- **blog** → `website`
- **orcid.org link from profile page** → `orcid` (full URL: `https://orcid.org/XXXX-XXXX-XXXX-XXXX`)

### Step 1c — Search for ORCID and missing info

If ORCID was not found on the GitHub profile page or social accounts:
1. Search the ORCID public API with name + affiliation for best results:
   `curl -s -H "Accept: application/json" "https://pub.orcid.org/v3.0/search/?q=family-name:{family}+AND+given-names:{given}+AND+affiliation-org-name:{affiliation}"`
2. If no affiliation available, search by name only:
   `curl -s -H "Accept: application/json" "https://pub.orcid.org/v3.0/search/?q=family-name:{family}+AND+given-names:{given}"`
3. If exactly one result (`num-found: 1`), use it automatically
4. If multiple results, present options to the user with their ORCID profile URLs
5. If zero results and email is available, try:
   `curl -s -H "Accept: application/json" "https://pub.orcid.org/v3.0/search/?q=email:{email}"`

If affiliation is still missing after gh API:
1. Search the web for `"{author name}" site:orcid.org OR site:scholar.google.com OR site:github.com` to find affiliation
2. Present findings to the user for confirmation — never auto-fill unverified affiliation

### Step 1d — Confirm with user

Determine project type: `software` (default) or `dataset`

Present all extracted metadata and ask the user to confirm or adjust:
- Title
- Authors (with auto-populated ORCID, affiliation, email)
- Version
- License (auto-detected from LICENSE file)
- DOI (if available)
- Repository URL
- Whether a `preferred-citation` to a paper is needed

Only ask about fields that could not be auto-detected.

**Exit:** User confirms the metadata.

## Phase 2 — Generate CITATION.cff

**Entry:** Confirmed metadata from Phase 1.

1. Build the CITATION.cff following CFF schema v1.2.0
2. Use this field order (required fields first, then recommended, then optional):

```yaml
cff-version: 1.2.0
message: "If you use this software, please cite it as below."
type: software                    # or "dataset"
title: "Project Title"
version: "1.0.0"
date-released: "YYYY-MM-DD"      # ISO 8601
license: MIT                      # SPDX identifier
doi: "10.5281/zenodo.XXXXXXX"    # if available
repository-code: "https://github.com/owner/repo"
url: "https://project-website.com"  # if different from repo
abstract: >-
  One-paragraph description.
authors:
  - family-names: "Last"
    given-names: "First"
    orcid: "https://orcid.org/0000-0000-0000-0000"  # optional
    affiliation: "University"                         # optional
    email: "user@example.com"                         # optional
  - name: "Organization Name"     # entity author (no family/given names)
keywords:
  - keyword1
  - keyword2
```

3. If user has a paper to cite, add `preferred-citation`:

```yaml
preferred-citation:
  type: article                   # article, book, conference-paper, etc.
  title: "Paper Title"
  authors:
    - family-names: "Last"
      given-names: "First"
  doi: "10.1234/example"
  journal: "Journal Name"
  year: 2025
  volume: "1"
  issue: "1"
  start: "1"
  end: "10"
```

4. Valid `preferred-citation` types: `article`, `book`, `conference-paper`, `manual`, `misc`, `pamphlet`, `report`, `thesis`, `unpublished`

**Rules:**
- `cff-version` is always `1.2.0`
- `date-released` must be ISO 8601 format (YYYY-MM-DD)
- `license` must be a valid SPDX identifier
- `doi` must not include the URL prefix — just `10.xxxx/yyyy`
- `orcid` must be the full URL: `https://orcid.org/XXXX-XXXX-XXXX-XXXX`
- Authors: use `family-names` + `given-names` for people, `name` for organizations
- Omit optional fields that have no value — do not leave empty strings

**Exit:** CITATION.cff content generated.

## Phase 3 — Write and Validate

**Entry:** Generated CITATION.cff content.

1. Write `CITATION.cff` to the repository root
2. Validate the file:
   - Check YAML syntax is valid
   - Verify required fields present: `cff-version`, `message`, `title`, `authors`
   - Verify `authors` has at least one entry with either `family-names` + `given-names` or `name`
   - Verify `date-released` is ISO 8601 if present
   - Verify `license` is a known SPDX identifier if present
3. If a `CITATION.cff` already existed, show a diff of changes

**Exit:** Valid CITATION.cff written to repo root.

## Phase 4 — Inform the User

**Entry:** CITATION.cff written successfully.

1. Confirm the file was created
2. Explain what happens next:
   - GitHub will show a "Cite this repository" button in the sidebar once pushed to the default branch
   - Users can copy APA or BibTeX citations from that button
   - Zenodo integration will use this metadata if GitHub-Zenodo linking is enabled
3. If no DOI exists, suggest:
   - Zenodo GitHub integration for automatic DOI minting on releases
   - Adding the DOI back to CITATION.cff after it's assigned
4. Offer to commit the file

**Exit:** User informed and file ready.

## Schema Quick Reference

### Top-Level Fields

| Field | Required | Description |
|-------|----------|-------------|
| `cff-version` | Yes | Always `1.2.0` |
| `message` | Yes | Tells users how/why to cite |
| `title` | Yes | Software or dataset name |
| `authors` | Yes | List of person or entity objects |
| `type` | No | `software` (default) or `dataset` |
| `version` | No | Current version string |
| `date-released` | No | ISO 8601 date |
| `doi` | No | DOI without URL prefix |
| `license` | No | SPDX identifier |
| `license-url` | No | URL to license if non-standard |
| `repository-code` | No | Source code URL |
| `repository-artifact` | No | Built artifact URL |
| `url` | No | Project homepage |
| `abstract` | No | Description paragraph |
| `keywords` | No | List of keywords |
| `contact` | No | List of person/entity objects |
| `preferred-citation` | No | Reference object for a paper |
| `references` | No | List of reference objects |
| `identifiers` | No | List of `{type, value}` objects |
| `commit` | No | Commit hash of the version |

### Person Fields

`family-names`, `given-names` (required for persons), `name-particle`, `name-suffix`, `orcid`, `affiliation`, `email`, `alias`, `address`, `city`, `country`, `fax`, `post-code`, `region`, `tel`, `website`

### Entity Fields

`name` (required for entities), `address`, `city`, `country`, `date-end`, `date-start`, `email`, `fax`, `location`, `orcid`, `post-code`, `region`, `tel`, `website`
