---
type: moc
summary: "Map of Content for project scoping standards. Start here; follow WikiLinks to the specific topic needed for the current scoping task."
tags: [coding, scoping, moc, index]
---

# Project Scoping Index

> **How to use this file:** Read the section descriptions below. Follow the WikiLink to whichever topic applies to your current task. Most scoping tasks only need 2-3 nodes, not the entire graph. The descriptions contain enough context to decide whether you need the full file.

> **Cross-references:** `coding-index.md` governs the coding standards that apply after scoping completes. `security-practices.md` governs credential handling during scoping (Key Vault secrets, sandbox environments). `best-practices-creation.md` governs documentation output formats for the scope doc. [[banned-writing-styles]] applies to all written deliverables including scope docs.

---

## Scoping Tracks & Core Process

**[[project-scoping-bp]]** — Two scoping tracks (A: greenfield, B: pattern-following, C: tech debt), out-of-scope rules, existing pattern references, draft data models, testing strategy, changelog rules, scope doc template (section order and file naming), the 13-step scoping process, and the quality checklist. This is the retained core of the original monolithic file. **Read when:** starting any new code project scoping, checking which track to use, writing the scope doc, running the quality checklist before approval.

## Decisions Table & Question Bank

**[[scoping-decisions-questions]]** — The decisions table format (gating artifact, what belongs vs. what doesn't, population process) and the standard question bank covering 7 categories: Architecture & Hosting, Data & Persistence, Authentication & Authorization, Integration & External APIs, UI & User Experience, Testing & Quality, Operational, plus project-specific questions with examples from Chat, Meridian IVR, and Wix. **Read when:** populating the decisions table for any project, running through the question bank, checking whether a specific question category applies.

## UI Validation Mockups

**`project-scoping-bp.md`** — When and what to build for UI mockups (Track A only), the review process against the decisions table, the post-implementation verification hard gate (Extract, Build, Verify), the reactive phase startup sequence (6-step commit-first flow), component mapping tables, and lessons learned from SNOUT and [YourProject] Chat Phase [N]. **Read when:** scoping any project with a user-facing interface, creating reactive phases mid-PR, verifying implementation against mockups, building component mapping tables.

## Phased Delivery & Execution

**`project-scoping-bp.md`** — Phased delivery plan rules (dependency ordering, SSDT gates, mockup conformance gates), implementation orchestration (wave-based parallelization, per-component progress tracker, remaining integration items), the phased execution protocol (per-phase gate sequence with CI as authority), the per-wave execution checklist (the mandatory 7-step loop with Step 3.5 staging verification), wave-level GitHub issues (Section 8e: issue hierarchy, tagging, linking, checklist template, wave-to-parent rollup), targeted rule extraction per wave (Section 8f: extracting 5-8 applicable rules into each wave issue), and Plan Enforcement Gates quick reference. **Read when:** building or executing a phase plan, creating wave issues from a plan, setting up wave parallelization, running the per-wave checklist, tracking component progress, understanding CI gate requirements, populating applicable rules for a wave.

---

*This index was created 2026-04-05 as part of the project scoping graph split. The original monolithic [[project-scoping-bp]] (722 lines) was decomposed into topic-specific nodes for on-demand loading. Sections that are tightly coupled to the overall scoping process (tracks, out-of-scope, pattern references, data models, testing strategy, changelog, template, process steps, quality checklist) remain in the original file.*
