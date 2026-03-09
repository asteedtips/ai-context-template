# Private Files — What Stays Out of the Public Template

This file documents which context files are private (specific to your setup) and should NOT be shared in the public template repo. Keep these in a separate private repo.

---

## Files That Are Private-Only (No Public Counterpart)

These files contain account-specific data, credentials, or proprietary business logic that cannot be templated.

| File | Why It's Private |
|------|-----------------|
| `Claude Context/zoho-api.md` | Your specific Zoho CRM/Books/Desk API config, org IDs, price book IDs, custom fields |
| `Claude Context/microsoft-graph-api.md` | Your specific Graph API config, SharePoint drive IDs, site IDs, auto-download rules |
| `Claude Context/Email-Processing.md` | Your email routing rules, folder structure, and people-specific routing |
| `Claude Context/collab-repo.md` | Your specific GitHub repo paths and project file structure |
| `Claude Context/about-me.md` | Your filled-in personal and professional bio |
| `Claude Context/key_helper.py` | Your credential management script |
| `Claude Context/claude_keys.enc` | Your encrypted bootstrap credentials |
| `Claude Context/context_sync.py` | Your GitHub sync script |
| `memory/glossary.md` | Your people, acronyms, and internal language |
| `keys/.vault_key` | Your vault passphrase |

## Files That Have a Public Template Counterpart

These files exist in both the public template (with placeholders) and your private set (filled in). When you update the private version, check if the structural change should also go into the public template.

| Private File | Public Template |
|-------------|----------------|
| `CLAUDE.md` | `CLAUDE.md` (template with `<!-- CUSTOMIZE -->` blocks) |
| `Claude Context/banned-writing-styles.md` | Same file, shared as-is |
| `Claude Context/working-style.md` | Same file, shared as-is |
| `Claude Context/best-practices-creation.md` | Template with placeholder folders/naming |
| `Claude Context/security-practices.md` | Concept-only version (no code, no vault names) |
| `Claude Context/proposal-generation.md` | Structure-only version (no SPICE details, no pricing rules) |
| `Claude Context/sales-enablement.md` | `sales-framework.md` (structure only, no framework specifics) |
| `Claude Context/seo-style.md` | Same file, shared as-is |
| `Claude Context/coding-best-practices.md` | Template without project-specific gaps |
| `Claude Context/Email-Processing.md` | `email-processing.md` (process template, no routing rules) |
| `zoho-api.md` + `microsoft-graph-api.md` | `api-template.md` (generic OAuth template) |
| `TASKS.md` | Empty structure |
| `CHANGELOG.md` | Empty structure |
| `memory/glossary.md` | Empty structure with prompts |

## Scheduled Tasks

Your scheduled task definitions (e.g., `Scheduled/daily-summary.md`, `Scheduled/inbox-review.md`) are private. The public template doesn't include them, but the README explains how to create your own.

---

*When sharing the public template, double-check that no private data (names, IDs, credentials, folder paths) has leaked into the public files.*
