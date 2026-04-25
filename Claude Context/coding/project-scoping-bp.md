# Project Scoping Best Practices — Code Projects
**[YOUR NAME] | [YOUR TITLE] | [YOUR COMPANY]**
*Reference file for scoping any project that involves writing code*
*Last Updated: [DATE]*

---

> **How to use this file**: Read this file before starting any code project — new feature, integration, migration, or refactor. It defines the scoping process, the mandatory artifacts, and the section template for the project plan doc. The goal is to identify every decision, boundary, and dependency before the first line of code is written.

> **Cross-references**: `coding-best-practices.md` governs code standards. `writing/best-practices-creation.md` governs documentation output format. `writing/banned-writing-styles.md` applies to all written content. `security/security-practices.md` governs credential handling. This file governs the scoping process that happens before any of those come into play.

---

## 1. Two Scoping Tracks

Not every project needs the same depth. This doc defines two tracks based on whether you're building something new or plugging into something that already exists.

**Track A — Greenfield / New Bounded Context**
Use this when the project introduces new entities, new API surface, new UI components, or a new bounded context in the solution.

Track A uses the full template (all sections below).

**Track B — Pattern-Following Integration**
Use this when you're adding a new implementation of an existing abstraction. The architecture, interfaces, and data model already exist — you're writing a new provider, adapter, or connector.

Track B uses an abbreviated template: Decisions Table, Out of Scope, Files to Create/Modify, Testing Sequence, and Changelog. Skip sections that are already governed by the pattern doc (architecture, data model, phasing).

**Track C: Technical Debt / Coverage Improvement**
Use this when the work is neither greenfield nor a new integration, but rather improving an existing codebase: adding test coverage, refactoring for testability, paying down documented gaps, or standardizing patterns across bounded contexts.

Track C uses the same template as Track A, but the "Overview" section is a current-state audit (what exists today, what's missing, measured by coverage or gap count), the "Decisions Table" focuses on scope boundaries (which contexts to cover, which to defer, what coverage target per phase), and the "Phased Delivery Plan" orders phases by risk (most-depended-on and least-tested code goes first).

**When it's not obvious which track applies**, default to Track A. A scope doc with too much detail is never the problem. A scope doc with too little always is.

---

## 2. The Decisions Table — Gating Artifact

The decisions table is the single most effective scoping artifact. It is mandatory for every project, both tracks. **No code starts until the decisions table is populated and reviewed.**

The table captures every design choice, behavioral rule, and trade-off that affects implementation. Each row is a question that was asked, answered, and documented.

### Format

| Decision | Answer |
|----------|--------|
| [Short description of the question] | [Specific answer with enough context to implement against] |

### What belongs in the decisions table

Any question where the answer changes what code gets written. Specifically:

- Behavioral rules: "Can deactivated users still send messages?" / "Does the flow support both payment methods, or just one?"
- Data model choices: "One thread per user pair, or multiple?" / "Multi-tenant dictionary keyed by org ID?"
- UX decisions: "Admin sees display name or real name?" / "Cursor-based or page-number pagination?"
- Integration boundaries: "Polling or webhooks?" / "API key auth or OAuth?"
- Feature gates and notification strategy: "Hidden entirely when disabled, or visible but locked?" / "Push only, email only, or both?"
- Security and deployment choices: "Function-level auth with IP whitelist, or JWT?" / "Same App Service or separate?"

### What does NOT belong in the decisions table

- Implementation details that follow directly from the decision (an implementation choice, not a scoping decision)
- Pattern choices that are already standardized (things in coding-best-practices.md — don't repeat them)
- Testing strategy (that has its own section)

### Process for populating

1. **Start with the standard question bank** (Section 3 below). Run through every question. Mark the ones that apply to this project.
2. **Add project-specific questions** that the standard bank doesn't cover. Every domain has its own edge cases.
3. **Answer every applicable question** before moving to the next section. If an answer requires research, research it. If it requires user input, present selectable options — don't leave it as an open question.
4. **Review the completed table** as a unit. Look for contradictions, gaps, and implications. One decision often forces another.

---

## 3. Standard Question Bank

These questions apply to most code projects. Not all will be relevant to every project. The scoping process starts by running through this list, marking what applies, and answering what does.

### Architecture & Hosting

- Where does this code live in the solution? New bounded context or extension of an existing one?
- What's the hosting model? App Service, Functions, standalone API, frontend framework?
- Does this need its own deployment pipeline, or does it deploy with an existing app?
- Single-tenant or multi-tenant? If multi-tenant, how is tenant isolation achieved?
- Does this introduce a new external dependency (third-party API, new cloud service, new package)?

### Data & Persistence

- What new entities/tables are needed? What are the relationships?
- Does this modify existing entities? If so, which ones and how?
- Do existing rows need backfilling or migration scripts?
- What's the data retention policy? Archive, soft delete, hard delete, temporal tables?
- Are there default value assumptions that need to change?

### Authentication & Authorization

- How is this authenticated? JWT, function key, identity platform, API key, other?
- What authorization model applies? Role-based, resource-ownership, feature flags, or a combination?
- Are there different permission tiers?
- Does this need rate limiting? If so, what are the limits and the window?

### Integration & External APIs

- What external APIs does this call? What auth model do they use?
- What's the retry strategy for transient failures?
- Are API credentials already in your secret store, or do new secrets need to be added?
- Is data pulled (polling), pushed (webhooks), or both?
- What's the error contract? How does the external API report failures?
- **Does this feature require changes to shared services, config structures, or infrastructure that other features depend on?** If yes, those prerequisite changes must be scoped and completed before the feature work begins. Don't discover shared infrastructure changes mid-build.

### UI & User Experience

- Is there a UI component? If so, where does it live?
- Who are the user roles that interact with this? Do they see different views?
- How does the user discover this feature? Navigation changes, feature flags, new routes?
- What's the notification model? In-app, push, email, some combination?

### Testing & Quality

- What's the minimum test coverage for this feature?
- What are the must-test paths (100% coverage required)?
- Can tests run without external dependencies?
- What's the mocking strategy?

### Operational

- How is this monitored in production?
- What happens when this fails? Graceful degradation, retry, alert?
- Are there compliance considerations (PCI, HIPAA, SOC2, etc.)?
- Does this affect existing features? If so, what's the backward compatibility plan?

### Project-Specific Questions

After running through the standard bank, add questions unique to this project's domain. These are the ones no template can predict.

---

## 4. Out of Scope — Mandatory

Every project scope doc includes an out-of-scope section. This is not optional, regardless of project size or track. The purpose is to draw the line early so it doesn't get drawn mid-implementation when the cost is higher.

### Format

| Item | Rationale |
|------|-----------|
| [Feature or capability being excluded] | [Why it's excluded and when it might be revisited] |

### How to populate

1. For every decision in the decisions table, ask: "What related thing are we NOT doing?"
2. For every user-facing feature, ask: "What would a user expect that we're not building?"
3. For every integration, ask: "What API capabilities exist that we're not using?"

---

## 5. UI Validation Mockups (Track A Only)

For any project with a user-facing interface, build lightweight mockups after the decisions table is populated and out-of-scope items are defined. The purpose is to validate UI-related decisions visually before moving into data models and phasing.

### When to use this step

Any Track A project where the decisions table contains answers about screens, user flows, roles with different views, navigation changes, or notification presentation. If the project is purely backend, skip this section. For backend projects, the equivalent validation tool is a sequence diagram or data flow diagram (use Mermaid per `writing/best-practices-creation.md`).

### What to build

Single-file HTML mockups. No frameworks, no build step. Each mockup should show:

1. **Screen states per role.** If the decisions table says "admin sees X, member sees Y," build both views.
2. **State transitions.** Empty state, loading, populated, error.
3. **Navigation flow.** How the user gets to the feature.
4. **Notification presentation.** If applicable, show how notifications appear in context.

### Post-Implementation Verification — Hard Gate (Mandatory)

Every UI component goes through a three-step gate: **Extract → Build → Verify.** See `coding-best-practices.md` for the full process.

1. **Step A — Extract:** Before writing code, open the mockup and produce a Component Spec Checklist: one line per visual element, written in the implementation framework's language. Write this into the phase plan.
2. **Step B — Build:** Implement using the checklist as the spec.
3. **Step C — Verify:** After code compiles, walk the checklist marking each ✅ or ❌. Fix any ❌, re-verify the full list. Write verification output into the plan.

The component cannot be marked DONE until the verification artifact shows all items passing. This applies to both planned and reactive phases.

### Component Mapping Table

<!-- CUSTOMIZE: Replace framework examples with your stack -->

When the implementation framework is known, include a mapping from visual mockup elements to framework components. This prevents UI being built from the API layer up rather than from the mockup down.

```
Visual Element     → Framework Component
Record list        → [YOUR_LIST_COMPONENT]
Filter dropdown    → [YOUR_SELECT_COMPONENT]
Create button      → [YOUR_FAB_COMPONENT]
Page layout        → [YOUR_LAYOUT_DIRECTIVE]
```

---

## 6. Existing Pattern References

The scope doc does not duplicate code patterns that are already documented elsewhere. Instead, it lists which existing pattern docs apply and calls out any deviations.

### Format

| Pattern Doc | Applies To | Deviations |
|-------------|-----------|------------|
| `coding-best-practices.md` Section X | DI registration | None — follow standard pattern |
| `security-practices.md` Section Y | Secrets | Two new secrets to add |

---

## 7. Draft Data Models (Track A Only)

For greenfield projects, the scope doc includes draft entity definitions. These are not final but drafting them during scoping forces decisions about relationships, nullability, default values, and data types.

### What to include

- New entity classes with properties, types, and relationships
- New enums with values and backing types
- Modifications to existing entities
- Migration scripts for backfilling existing data

### What to skip

- ORM configuration details (follow established patterns)
- Full DTO/ViewModel definitions (derive from entities during implementation)
- Stored procedures (define the need, not the SQL)

---

## 8. Phased Delivery Plan

Every project is broken into ordered phases. Phases are about dependency ordering and review gates, not scheduling. No hour estimates.

### Phase structure rules

- Each phase produces something testable or reviewable.
- Phases are ordered by dependency. Data model before service layer. Service layer before API. API before UI.
- Each phase lists the files to create or modify.

### Plan drift rule

When implementation deviates from the scope doc (data model changes, phase reordering, new entities added), **update the plan doc in the same session, not as a catch-up exercise later.** Log every deviation in the changelog with the date and reasoning.

### Pattern compliance check

After each phase completes, verify that the built code follows the patterns listed in the "Existing Pattern References" section of the scope doc. This catches drift between decisions and actual implementation.

### Phase naming convention

Use descriptive names, not just numbers. "Phase 3: SignalR Hub & Real-Time Messaging" is better than "Phase 3."

---

## 8b. Implementation Orchestration & Progress Tracking

Every project plan includes an orchestration section that defines how phases execute and a progress tracker that logs every component as it's completed.

### Wave-Based Parallelization

Group phases into waves based on dependency. Phases within a wave can execute concurrently.

```
Wave 1 (parallel):
  ├── Phase 1a — [description]
  └── Phase 1b — [description]

Wave 2 (after Wave 1):
  └── Phase 2 — [description]
```

**Rules:**
- A wave only starts after all phases in the preceding wave are complete.
- Within a wave, phases must not have file-level conflicts.
- Not every project needs parallelization. Small projects (3-4 phases) can stay sequential.

### Per-Component Progress Tracker

| Phase | Component | Status | Commit | Notes |
|-------|-----------|--------|--------|-------|
| 1 | Entity.cs | DONE | abc1234 | — |
| 3 | FeatureService.cs | IN PROGRESS | — | Blocked on API format |
| 4 | FeaturePage.razor | PENDING | — | — |

**Status values:** `PENDING`, `IN PROGRESS`, `DONE`, `BLOCKED`, `SKIPPED`

---

## 8c. Phased Execution Protocol

This section defines the gate sequence for executing a phased delivery plan. Where Section 8 defines *what* the phases are and Section 8b defines *how to track* them, this section defines *how to execute* each phase to completion. The per-project compile-run-fix gate mechanics live in `coding-best-practices.md` Section 9.4.1; this section covers the orchestration layer.

### Per-Phase Gate Sequence

After all projects within a phase pass their individual compile-run-fix gates (see `coding-best-practices.md` Section 9.4.1), run the phase-level gates:

1. **Solution gate.** Run the full test suite, not just the phase's tests. This catches regressions where new mocks, helpers, or dependency changes conflict with existing tests.
2. **Fix any solution-level regressions** from step 1.
3. **Update the plan.** Record actual test counts, deviations, and issues that inform later phases. Same session, not later.
4. **Phase commit.** Final commit updating the plan document with phase results.

### Execution Order vs Phase Number

Phases don't have to execute in numerical order. When phases have no dependencies between them, reorder by risk: the most depended-on code with the least test coverage goes first.

Document the execution order in the plan.

### Phase Results Section

Every plan should include a "Phase Results" section that gets filled in after each phase completes. Each entry records: completion date, actual test count vs estimate, commit hash, deviations from plan, and issues that affect later phases. This section is the ground truth for cross-session continuity.

---

## 8d. Per-Wave Execution Checklist

This is the mandatory execution loop for every wave in any plan. It runs automatically after the wave's code work is complete — do not wait to be prompted. If any step is skipped, the wave is not done.

### The 7-Step Loop

**Step 1 — Fix the issues**
Complete all code changes for this wave per the plan's task list. Every item in the wave's scope should be addressed before moving forward.

**Step 2 — Verify locally**
Run the build and relevant tests locally. Confirm: no compile errors, no test failures in the affected area. Do not push until local is clean.

**Step 3 — Iterate until local is green**
If Step 2 surfaces failures, fix them and re-run. Repeat until the local build and tests pass.

**Step 4 — Push to GitHub**
Commit the wave's changes with a descriptive message referencing the wave number and what changed.

**Step 5 — Watch CI**
Wait for the GitHub Actions run to complete. A green badge is the gate, not the push itself.

**Step 6 — Fix CI failures and repeat**
If CI fails, diagnose, fix locally, push again, and return to Step 5. The CI run must be green before the wave closes.

**Step 7 — Update the plan doc**
Once CI is green, update the plan document in the same session:
- Mark each completed item as `DONE` in the progress tracker
- Record the commit hash for each component
- Record the CI run number
- Note any deviations or decisions made during the wave that affect later phases

A wave with green CI but no plan update is still open.

### When this loop runs

Every wave. No exceptions for "small" waves, "obvious" changes, or "just a fix."

---

## 9. Testing Strategy

The scope doc defines how this project will be tested.

### Minimum content

- **Coverage target**: Default is 70% per `coding-best-practices.md`. If higher is needed for specific paths, state which.
- **Must-test paths**: List areas that need 100% coverage (auth, money handling, data mutations).
- **Mocking strategy**: What gets mocked and what uses real implementations.
- **Test isolation**: Can tests run without external services?

### Test count estimation

When scoping a test phase, initial estimates consistently undershoot the actual count by 1.5x to 2x. This is the natural result of edge cases, parameterized test expansions, and validation tests that only become visible once you're writing the tests. Use a 1.75x multiplier when estimating test counts for phase scoping. This doesn't change effort (there are no hour estimates), but it prevents later phases from being scoped too aggressively based on unrealistic baselines.

---

## 10. Changelog — Mandatory

Every scope doc has a changelog section. Any change made after the initial scope is approved gets logged.

### Format

| Date | Change | Reason |
|------|--------|--------|
| [DATE] | [What changed] | [Why it changed] |

### Rules

- Log every change that affects the decisions table, data model, phase plan, or out-of-scope list.
- If a change contradicts a previous decision, note the original and why it changed.

---

## 11. Scope Doc Template

Every project plan doc follows this section order. Sections marked as Track A only can be skipped for Track B.

```markdown
# [Project Name] — Project Plan

**Created:** [Date]
**Updated:** [Date]
**Status:** [Scoping / In Progress / Code Complete / Deployed]

---

## 1. Overview
[One paragraph: what is being built and why.]

## 2. Decisions Table
[Mandatory — see Section 2 above]

## 3. Out of Scope
[Mandatory — see Section 4 above]

## 4. Architecture & Where Code Lives (Track A only)
[Solution structure, new projects, layering, hosting model]

## 5. UI Validation Mockups (Track A only, if UI exists)
[HTML mockups validating UI decisions]

## 6. Existing Pattern References
[Links to pattern docs with deviation notes]

## 7. Data Model (Track A only)
[Draft entities, enums, migration scripts]

## 8. Phased Delivery Plan
[Ordered phases with files to create/modify]

## 8b. Implementation Orchestration & Progress
[Wave map, progress tracker, integration items]

## 8c. Phased Execution Protocol
[Per-phase gate sequence, execution order documented, phase results section present]

## 8d. Per-Wave Execution Checklist
[7-step loop: fix → verify locally → iterate → push → watch CI → fix CI → update plan — see Section 8d above]

## 9. Testing Strategy
[Coverage, must-test paths, mocking, isolation]

## 10. Changelog
[Mandatory]
```

### File naming

`[Project]-Plan.md` — descriptive name matching the project.

### File location

Plan files live in the code repo's `docs/` folder, organized by issue. See `source-control.md` "Docs Folder Convention" for the full structure.

- **When a GitHub issue exists:** `docs/feat-issue-{N}/{Project}-Plan.md`
- **Before a GitHub issue exists:** `docs/draft-{project-name}/{Project}-Plan.md`. Rename the folder to `feat-issue-{N}/` when the issue is created.

Supporting files (mockups, ADRs, deploy scripts, status trackers) go in the same issue subfolder alongside the plan.

---

## 12. Scoping Process — Step by Step

**Step 1 — Identify the track.** Greenfield (Track A) or pattern-following (Track B)? If unsure, default to Track A.

**Step 2 — Run the standard question bank.** Go through every question in Section 3. Mark what applies. Present one question at a time so each answer can inform the next.

**Step 3 — Add project-specific questions.** Based on the domain, add questions the standard bank doesn't cover.

**Step 4 — Populate the decisions table.** Every answered question becomes a row.

**Step 5 — Define what's out of scope.** For every decision, ask what related thing is NOT being built.

**Step 6 — Build UI validation mockups (Track A, if UI exists).** Walk through each screen against the decisions table. Update decisions and out-of-scope as needed.

**Step 7 — Reference existing patterns.** List which pattern docs apply and note deviations.

**Step 8 — Draft data models (Track A only).** Write the entity definitions.

**Step 9 — Build the phase plan.** Break work into ordered phases. List files per phase.

**Step 10 — Define testing strategy.** Coverage target, must-test paths, mocking approach.

**Step 11 — Review the complete scope doc.** Read as a unit. Look for contradictions and gaps.

**Step 12 — Get approval and start building.** The scope doc is the contract.

---

## 13. Quality Checklist

Before marking a scope doc complete, verify:

- [ ] Decisions table is populated with specific, implementable answers (not "TBD")
- [ ] Out of scope section exists with at least one entry
- [ ] Every applicable question from the standard bank has been answered
- [ ] UI mockups built and reviewed (Track A with UI), or sequence diagram built (backend-only)
- [ ] Existing pattern references listed with deviation notes
- [ ] Data model drafts included (Track A) with relationships and defaults
- [ ] Phases ordered by dependency, each producing something testable
- [ ] Testing strategy specifies coverage target, must-test paths, and mocking approach
- [ ] Execution protocol defined: per-phase gate sequence, execution order documented, phase results section present (see Section 8c)
- [ ] Wave execution checklist understood: after each wave, run the 7-step loop from Section 8d automatically
- [ ] Changelog section exists
- [ ] No banned vocabulary from `writing/banned-writing-styles.md`
- [ ] File saved to the correct location with the correct naming convention

---

*Read this file before starting any code project. As new projects are scoped and built, update the standard question bank with questions that keep recurring.*
*Last updated: 2026-03-24 — Added Section 8d Per-Wave Execution Checklist (7-step mandatory loop). Updated template and quality checklist.*


---

## Corrections Log

*Tracks issues found when following this file's instructions. Entries are added when a discrepancy is discovered and a fix is applied or proposed.*

| Date | What Failed | Root Cause | Fix Applied | ERRORS.md Ref |
|------|-------------|------------|-------------|---------------|

**Notes:**
<!-- Per-entry context that doesn't fit in the table. Format: "YYYY-MM-DD: [explanation]" -->
