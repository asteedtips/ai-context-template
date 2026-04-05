# Project Scoping Index

> **How to use this file:** Read the section descriptions below. Follow the link to whichever topic applies to your current scoping task. Most scoping tasks need 2-3 nodes. The descriptions contain enough context to decide whether you need the full file.

> **Cross-references:** `coding-index.md` governs the coding standards that apply after scoping completes. `security/security-practices.md` governs credential and credential handling during scoping. `writing/best-practices-creation.md` governs documentation output formats for the scope doc.

---

## Scoping Tracks & Core Process

**`project-scoping-bp.md`**  -  Three scoping tracks (greenfield, pattern-following, tech debt), out-of-scope rules, existing pattern references, draft data models, testing strategy, changelog rules, scope doc template (section order), the 13-step scoping process, and the quality checklist. This is the core scoping reference. **Read when:** starting any new code project scoping, checking which track to use, writing the scope doc, running the quality checklist before approval.

## Decisions Table & Question Bank

**`scoping-decisions-questions.md`**  -  The decisions table format (what gets decided, population process, blocking decisions) and the standard question bank covering 7 categories: Architecture & Hosting, Data & Persistence, Authentication & Authorization, Integration & External APIs, UI & User Experience, Testing & Quality, and Operational topics. **Read when:** populating the decisions table for any project, running through the question bank, checking whether a specific question applies.

## UI Validation Mockups

**`scoping-ui-mockups.md`**  -  When and what to build for UI mockups (which tracks need them), the mockup review process, the post-implementation verification hard gate (Extract-Build-Verify), component mapping tables, and the reactive phase startup sequence for mid-PR additions. **Read when:** scoping any project with a user-facing interface, creating reactive phases mid-project, verifying implementation against mockups.

## Phased Delivery & Execution

**`scoping-phased-delivery.md`**  -  Phased delivery plan rules (dependency ordering, database gates, mockup gates), implementation orchestration (wave-based parallelization, per-phase gate sequence), the per-wave execution checklist (the mandatory 7-step loop: code → verify locally → iterate → push → watch CI → fix issues → update plan). **Read when:** building or executing a phase plan, setting up waves, running the per-wave checklist, understanding CI integration.

---

*This index was created in [DATE] as part of the project scoping graph split. The original monolithic file was decomposed into topic-specific nodes for on-demand loading.*
