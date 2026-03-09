# Private Files — What Stays Out of the Public Template

This template is designed to be shared publicly. But your actual working system will contain private data that should never go in a public repo. This file explains how to split the two.

---

## The Principle

**Public repo (this template):** Frameworks, standards, writing rules, process templates, and structural patterns. Nothing here identifies you, your company, your customers, or your credentials.

**Private repo (yours):** Filled-in API configs, credential management scripts, encrypted key files, customer names, team rosters, proprietary methodology details, pricing data, and anything with real account IDs or org-specific values.

---

## What Should Stay Private

Any file that contains one or more of these belongs in your private repo, not the public template:

- **Credential files** — encrypted key stores, vault passphrases, helper scripts that reference your specific vault or secret store
- **API configuration with real values** — org IDs, drive IDs, site IDs, price book IDs, custom field mappings specific to your CRM/email/file storage instance
- **People and routing rules** — team member names, emails, external contacts, email folder structures, and message routing logic
- **Filled-in about-me** — your actual bio, company details, and personal information
- **Filled-in glossary** — your real team shorthand, acronyms, and lessons learned
- **Proprietary methodology** — if your sales qualification framework, pricing strategy, or win-rate data is a competitive advantage, the detailed version stays private
- **Project-specific files** — repo sync configs, collab repo paths, project file structures
- **Scheduled task definitions** — your specific automated workflows and their prompts
- **Sync scripts** — any scripts that pull/push context files to your private repos

---

## How the Split Works in Practice

Most of the files in this template have a "filled-in" private counterpart. The public version has `<!-- CUSTOMIZE -->` comment blocks. Your private version has those blocks replaced with real data.

When you update a private file, ask yourself: "Did I change the structure or just the data?" If the structure changed (new section, new checklist item, new workflow step), consider updating the public template too. If only data changed (new team member, updated API endpoint, rotated credential), the public template doesn't need a touch.

### Example mapping

| Public Template | Your Private Version |
|----------------|---------------------|
| `CLAUDE.md` (with placeholder workflow chains) | `CLAUDE.md` (with your real API files, company name, credential setup) |
| `api-template.md` (generic OAuth pattern) | `[your-crm]-api.md`, `[your-email]-api.md` (filled-in per service) |
| `sales-framework.md` (structure only) | `sales-framework.md` (with your actual qualification pillars and win data) |
| `proposal-generation.md` (section structure + QC checklist) | `proposal-generation.md` (with your pricing rules, CRM fields, and customer references) |
| `email-processing.md` (process template) | `email-processing.md` (with your folder structure and routing rules) |
| `about-me.md` (empty prompts) | `about-me.md` (your filled-in bio) |
| `memory/glossary.md` (empty structure) | `memory/glossary.md` (your people, terms, and lessons) |

Files like `banned-writing-styles.md`, `working-style.md`, and `seo-style.md` are the same in both — they're generic enough to share as-is.

---

## Before You Push Anything Public

Run this mental checklist:

- [ ] No real names (yours, team, customers, contacts) in any public file
- [ ] No company names, org IDs, drive IDs, site IDs, or account numbers
- [ ] No API endpoints with real values baked in
- [ ] No file paths that reveal your directory structure
- [ ] No credential file names, vault names, or secret store identifiers
- [ ] No pricing data, win-rate numbers, or proprietary methodology details
- [ ] References to private tools use generic placeholders (`[your-crm]`, `[your-email]`)

---

*Keep this file in the public repo as a guide for anyone forking the template. It teaches the split without revealing what's on the private side.*
