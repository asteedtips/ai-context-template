# Context Files — Changelog

Track what changed and when, so the agent can scan one file at session start to know what's new since the last session.

---

## 2026-09-30

**`writing/banned-writing-styles.md` brought current, gate helpers added.**

- Synced the rules file from the April 2026 version to the current one: the July emerging-tells pass, the August Section 3 enforcement labels and per-document triad gate, and the September 60-day audit (genuinely, reframe variants, mannered prose, free-lunch claims, short-form triad gate, outbound-field scan). The April copy also carried literal em dashes, which its own rules ban.
- Added `Claude Context/helpers/doc_banned_grep.py` (vocabulary, phrase, and dash gate) and `Claude Context/helpers/triad_scan.py` (rule-of-three density gate). Run both on any authored prose before it ships.

## 2026-03-13

**Major restructure: subfolder organization and new files.**

- Reorganized `Claude Context/` from flat layout into domain subfolders: `writing/`, `coding/`, `sales/`, `security/`, `api/`, `email/`, `seo/`, `guides/`
- Added `coding/project-scoping-bp.md` — full project scoping process with decisions table, question bank, phased delivery, and progress tracking
- Added `coding/source-control.md` — multi-org git repo management, PAT selection patterns, clone/pull/push snippets for mounted environments
- Updated `CLAUDE.md` — subfolder paths in context file table and dependency chains, added code work and project scoping workflows, added multi-tier repo architecture section, improved chat session logging section
- Updated all cross-references across files to use new subfolder paths
- Updated `README.md` — new file structure diagram, updated file count (20+), added best practices for subfolder organization
- Updated `PRIVATE-FILES.md` — added new file categories (source control, team files, migration playbooks, session logs), added multi-tier architecture section, expanded the pre-push checklist

## [Initial Release]

Initial setup of context file system.

---

*Update this file after every context file change. Format: date, file, what changed.*
