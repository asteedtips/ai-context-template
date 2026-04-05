# Project Scoping Best Practices  -  Code Projects

**[YOUR NAME] | [YOUR TITLE] | [YOUR COMPANY]**
*Reference file for scoping any project that involves writing code*
*Last Updated: [DATE]*

---

> **How to use this file**: Read this file before starting any code project  -  new feature, integration, migration, or refactor. This file defines the scoping process, mandatory artifacts, and the template for the project plan document. The goal is to identify every decision, boundary, and dependency before coding starts.

> **Graph nodes (extracted topics):**
> - `scoping-decisions-questions.md`  -  The decisions table format and the standard question bank (7 categories + project-specific questions)
> - `scoping-ui-mockups.md`  -  When to build UI mockups, what to include, the review process, and the Extract-Build-Verify hard gate for post-implementation verification
> - `scoping-phased-delivery.md`  -  Phased delivery plan rules, implementation orchestration (waves, progress tracker), execution protocol, and per-wave checklist

> **Cross-references:** `coding-best-practices.md` governs code standards. `writing/best-practices-creation.md` governs documentation output formats. `security/security-practices.md` governs credential handling.

---

## 1. Three Scoping Tracks

Not every project needs the same depth. Choose based on the nature of the work.

**Track A  -  Greenfield / New Bounded Context**

Use this when the project introduces new entities, new API surface, new UI components, or a new bounded context in the solution. Track A uses the full template with all sections.

**Track B  -  Pattern-Following Integration**

Use this when you're adding a new implementation of an existing abstraction. The architecture, interfaces, and data model already exist; you're writing a new provider, adapter, or connector. Track B uses an abbreviated template: Decisions Table, Out of Scope, Files to Create/Modify, Testing Sequence, and Changelog.

**Track C  -  Technical Debt / Coverage Improvement**

Use this when the work improves an existing codebase: adding test coverage, refactoring for testability, paying down documented gaps, or standardizing patterns. Track C uses the Track A template but the "Overview" section is a current-state audit, and the "Decisions Table" focuses on scope boundaries.

**When in doubt, default to Track A.** Scope docs with too much detail are never the problem.

---

## 2. Mandatory Scoping Process  -  13 Steps

This is the gate. Every step must complete before code starts. Do not skip steps.

### Steps 1-6: Discovery & Planning

1. **Gather requirements**  -  What does the user/stakeholder want? Write it as a one-paragraph problem statement.
2. **Run the question bank**  -  Use `scoping-decisions-questions.md` to identify every design choice that needs answering.
3. **Populate the decisions table**  -  Answer every applicable question with specific, implementation-grade answers. Use AskUserQuestion for decisions that need stakeholder input.
4. **Define out-of-scope items**  -  What won't be built in this project? Be explicit.
5. **Create UI mockups (Track A only)**  -  See `scoping-ui-mockups.md`. Mockups are validation artifacts, not design comps.
6. **Get approval on decisions and mockups**  -  Approval gates: no code starts until decisions are confirmed and mockups are approved.

### Steps 7-10: Detailed Planning

7. **Identify existing patterns**  -  What patterns already exist in the codebase for this type of work? Document them.
8. **Draft data model (Track A/C)**  -  For projects with new entities: design the schema, relationships, and validation rules. Create an ER diagram or DDL draft.
9. **Plan the phases**  -  Divide the work into ordered phases based on dependencies. Use `scoping-phased-delivery.md` for phase structure rules. Identify wave-based parallelization opportunities if the project is large enough.
10. **Scope the testing strategy**  -  Define coverage targets, must-test paths, external dependency handling, and whether tests run in CI.

### Steps 11-13: Finalization & Gate

11. **Run the quality checklist**  -  Verify the scope doc is complete and enforceable (see below).
12. **Update the scope doc template**  -  Fill in all sections (template is below).
13. **Get final approval**  -  Albert approves the scope doc. This is the gate. No code starts until the scope doc is approved.

---

## Quality Checklist for Scope Docs

Before step 13, verify every item below:

- [ ] Decisions table is complete  -  every applicable question has an answer
- [ ] Answers are implementation-grade  -  a developer can read an answer and start coding without asking clarifications
- [ ] Out-of-scope items are explicit  -  what's NOT being built is as clear as what is
- [ ] Existing patterns are documented  -  where applicable, the scope doc references the codebase's established patterns
- [ ] Data model is drafted (if applicable)  -  ER diagram or DDL showing entities, relationships, and key constraints
- [ ] Phases are defined  -  each phase is named, describes what gets built, and lists files to create/modify
- [ ] Phase ordering makes sense  -  dependencies are respected; the first phase produces something deliverable
- [ ] Testing strategy is clear  -  coverage target, must-test paths, and CI integration are documented
- [ ] Changelog template is created  -  new entries will be logged as implementation deviates from the plan
- [ ] Plan Enforcement Gates are verified  -  see `scoping-phased-delivery.md` for the five mandatory gates

---

## Scope Doc Template

Use this template for all Track A projects. For Track B/C, use the abbreviated version noted below.

### Header

```
# Project Scoping: [Project Name]
**Date:** [YYYY-MM-DD]
**Track:** A / B / C
**Status:** In Progress / Approved / Closed
```

### 1. Overview

**Problem statement:** One paragraph. What is the user trying to accomplish? What's the pain point?

**Solution approach:** One paragraph. How does this project solve the problem?

**Success criteria:** Bullet list. How do we know this project succeeded?

### 2. Decisions Table

See `scoping-decisions-questions.md` for the format and question bank.

### 3. Out of Scope

**Explicitly list what is NOT being built.** This prevents scope creep. Example:

- Mobile app (web only in V1)
- Real-time sync (polling is acceptable)
- Support for custom branding per customer
- Audit trail for all data changes

### 4. Existing Pattern References

Link to or describe the patterns the codebase already uses for this type of work. Examples:

- DI registration: see `Program.cs` lines 12-45 for the established pattern
- Error handling: all services return `BaseServiceResult<T>`, see `ChatService.cs` for examples
- Database: repositories use `IDbContextFactory<T>`, no injected DbContext

### 5. Data Model (Track A/C)

If the project introduces new entities:

**Entity list:**
- Entity name, primary key, key relationships
- Example: `ChatThread` (PK: Id, FK: GymId, FK: InitiatorUserId, FK: RecipientUserId)

**ER diagram** (text or Mermaid):
```
Gym |--- many ---> ChatThread
User |--- many ---> ChatThread
```

**Key constraints and defaults:**
- Audit columns: CreatedAt, ModifiedAt, deleted/archived flags
- Concurrency: RowVersion shadow property for optimistic locking
- Temporal tables: if history tracking is needed
- Unique indexes: business-key uniqueness constraints

### 6. Phased Delivery Plan

Use `scoping-phased-delivery.md` for phase structure rules.

**Phases:**
- Phase 1: [Name]  -  [files to create/modify]
- Phase 2: [Name]  -  [files to create/modify]
- Phase 3: [Name]  -  [files to create/modify]

**Wave structure (if applicable):**
```
Wave 1 (parallel): Phase 1a, Phase 1b
Wave 2 (after Wave 1): Phase 2
Wave 3 (after Wave 2): Phase 3
```

### 7. Testing Strategy

- **Minimum coverage:** 70% (or your standard)
- **Must-test paths:** List paths that require 100% coverage (auth, payment, data mutation, validation)
- **External dependencies:** What external services/APIs does this need? Are sandboxes available?
- **CI integration:** Will tests run in CI? Are any tests excluded (integration tests requiring credentials)?
- **Dry Run mode (if applicable):** See `coding-testing.md` Section 6.7 for implementation details

### 8. Changelog

As implementation deviates from the plan, log entries here with the date and reasoning. Format:

```
**2026-04-05:** Data model changed from 3 entities to 1 unified entity with discriminator (Phase 1 scaffolding). Reason: simplifies storage, reduces foreign key complexity. Updated phase plan accordingly.

**2026-04-06:** Added Phase 7 for integration testing. Original plan assumed unit tests only; discovered during Phase 5 that integration tests are necessary for webhook validation.
```

### 9. Appendix (Optional)

Links to related docs, discussions, or decisions that informed this scope.

---

## Abbreviated Template (Track B/C)

Use this for pattern-following or technical debt projects:

1. Overview
2. Decisions Table
3. Out of Scope
4. Files to Create/Modify
5. Testing Sequence
6. Changelog

---

*For detailed guidance on specific sections, see the graph node files: `scoping-decisions-questions.md`, `scoping-ui-mockups.md`, and `scoping-phased-delivery.md`.*

*Last Updated: [DATE]  -  Graph split: extracted decisions table, UI mockups, and phased delivery into standalone files. This file retains the scoping process, three tracks, quality checklist, and scope doc template.*

---

## Corrections Log

*Tracks issues found when following this file's instructions.*

| Date | What Failed | Root Cause | Fix Applied |
|------|-------------|------------|-------------|

