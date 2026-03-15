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
- **Source control repo tables** — your actual repo names, org structure, PAT names, and branch conventions (the template in `coding/source-control.md` has the pattern; your private version has the real data)
- **Project-specific files** — scoping docs, project plans, architecture references for active codebases
- **Team context files** — team project prompts, role-specific instructions, org-specific operations guides
- **Scheduled task definitions** — your specific automated workflows and their prompts
- **Sync scripts** — any scripts that pull/push context files to your private repos (helper scripts, context_sync, etc.)
- **Migration playbooks** — internal migration guides between specific tools or platforms
- **Session logs** — `memory/Tasks/*.md` files contain session-specific work details

---

## How the Split Works in Practice

Most of the files in this template have a "filled-in" private counterpart. The public version has `<!-- CUSTOMIZE -->` comment blocks. Your private version has those blocks replaced with real data.

When you update a private file, ask yourself: "Did I change the structure or just the data?" If the structure changed (new section, new checklist item, new workflow step), consider updating the public template too. If only data changed (new team member, updated API endpoint, rotated credential), the public template doesn't need a touch.

### Example mapping

| Public Template | Your Private Version |
|----------------|---------------------|
| `CLAUDE.md` (with placeholder workflow chains) | `CLAUDE.md` (with your real API files, company name, credential setup) |
| `api/api-template.md` (generic OAuth pattern) | `api/[your-crm]-api.md`, `api/[your-email]-api.md` (filled-in per service) |
| `sales/sales-framework.md` (structure only) | `sales/sales-framework.md` (with your actual qualification pillars and win data) |
| `sales/proposal-generation.md` (section structure + QC checklist) | `sales/proposal-generation.md` (with your pricing rules, CRM fields, customer references) |
| `email/email-processing.md` (process template) | `email/email-processing.md` (with your folder structure and routing rules) |
| `coding/source-control.md` (pattern + snippets) | `coding/source-control.md` (with your actual repos, orgs, PATs, and branches) |
| `coding/project-scoping-bp.md` (question bank + process) | `coding/project-scoping-bp.md` (with your project examples and lessons learned) |
| `about-me.md` (empty prompts) | `about-me.md` (your filled-in bio) |
| `memory/glossary.md` (empty structure) | `memory/glossary.md` (your people, terms, and lessons) |

Files like `writing/banned-writing-styles.md`, `working-style.md`, and `seo/seo-style.md` are the same in both — they're generic enough to share as-is.

### Files that only exist in private

These have no public template counterpart because they're too org-specific to generalize:

| Private-Only File | Why It Stays Private |
|---|---|
| `api/[crm]-api.md` | Specific CRM endpoints, field mappings, account IDs |
| `api/[email]-api.md` | Specific Graph/email API config with drive IDs, tenant IDs |
| `security/[vault]-setup-guide.md` | Step-by-step tied to your specific vault instance |
| `security/team-key-distribution.md` | Your team's credential distribution process |
| `team/team-project-*.md` | Role-specific instructions for your team members |
| `helpers/*.py` | Key helper scripts tied to your vault and sync architecture |
| `migrations/*.md` | Internal migration playbooks between your specific tools |

---

## Multi-Tier Architecture (Optional)

If you share standards with a team, consider a three-tier repo structure:

| Tier | Audience | What It Contains |
|------|----------|-----------------|
| **Private** | You only | Everything — full context, credentials, memory, personal data |
| **Team** | Your team | Sanitized standards — coding, security, writing rules, API patterns (no personal data) |
| **Public** | Anyone | This template — frameworks with `<!-- CUSTOMIZE -->` blocks (no org data at all) |

Changes flow downstream: Private → Team → Public. Structure changes propagate. Data changes don't.

See the "Context File Repos — Multi-Tier Architecture" section in `CLAUDE.md` for the full setup.

---

## Before You Push Anything Public

Run this mental checklist:

- [ ] No real names (yours, team, customers, contacts) in any public file
- [ ] No company names, org IDs, drive IDs, site IDs, or account numbers
- [ ] No API endpoints with real values baked in
- [ ] No file paths that reveal your directory structure
- [ ] No credential file names, vault names, or secret store identifiers
- [ ] No pricing data, win-rate numbers, or proprietary methodology details
- [ ] No repo names, branch names, or PAT names that reveal your org structure
- [ ] No project-specific examples that name real products or codebases
- [ ] References to private tools use generic placeholders (`[your-crm]`, `[your-email]`, `[your-org]`)

---

*Keep this file in the public repo as a guide for anyone forking the template. It teaches the split without revealing what's on the private side.*
