# Phased Delivery & Execution

> **Part of the Project Scoping Graph.** This file covers the phased delivery plan, implementation orchestration, execution protocol, and per-wave checklist. For the full scoping index, see `project-scoping-index.md`.

## 8.0 Spike Phase Protocol

Not every feature has a clear shape at the start. When the architecture, data model, or external API integration is uncertain, a time-boxed spike runs before any feature branch is created. The spike's deliverable is the scoping doc, not shippable code.

### When to spike

Spike when any of these are true: (1) the feature involves an external API you haven't integrated before, (2) the data model has more than 5 new entities and the relationships aren't obvious, (3) the product owner says "let's figure this out first," or (4) no approved mockups exist yet for a UI-heavy feature.

Skip the spike when the feature is a well-understood pattern (another CRUD page, another action executor following the existing template, another settings tab) and the scoping doc can be written from existing knowledge.

### Spike rules

- **Branch:** `spike/issue-XX`. This branch is throwaway. It does not merge into `dev` or `feat/issue-XX`.
- **Time box:** 2 sessions max. If the spike hasn't produced a scoping doc after 2 sessions, stop and reassess with the product owner. The spike may be too large, or the feature may need to be broken into smaller pieces.
- **Deliverable:** A scoping doc in `docs/feat-issue-XX/` with at least Sections 1-4 (problem statement, decisions table, data model, phase plan). The spike code is reference material, not a draft of the real implementation.
- **Vertical slice (mandatory):** During the spike, pick one end-to-end flow and run it against real data. For example: one record processed through one rule, one external API call with real data, one query for real data. Document the result (worked/failed/what was learned) in the scoping doc's Decisions section. This slice is the proof that the architecture holds before committing to a full build. See "Vertical Slice Gate" below.
- **Feature branch creation gate:** The `feat/issue-XX` branch cannot be created until the scoping doc exists with Sections 1-4 confirmed by the product owner. The spike branch may be deleted at this point.

### Vertical Slice Gate

After the spike produces the scoping doc and before bulk implementation begins, one complete vertical slice must run end-to-end against real (or staging) data. The slice covers: UI form submission or trigger, service layer call, external API call with real credentials, response handling, and database persistence.

**What a valid slice proves:**
- Authentication and authorization work for the external API (token format, scopes, org IDs)
- The data model can persist and retrieve the output
- The DI registration pattern resolves correctly at runtime
- The happy path works before edge cases are addressed

**Document the slice** in the plan doc: which flow was tested, what data was used, what the result was, and any surprises. This becomes the reference point for the full build.

**Lesson learned:** A feature had 5 separate runtime bugs that all would have been caught by a single vertical slice. Instead, bugs were discovered one at a time over multiple sessions. A structured vertical slice execution prevents this pattern.

---

## 8. Phased Delivery Plan

Every project is broken into ordered phases. Phases are about dependency ordering and review gates, not scheduling. No hour estimates.

### Phase structure rules

- Each phase produces something testable or reviewable. "Set up the project" is not a phase by itself unless the project setup itself needs review.
- Phases are ordered by dependency. Data model before service layer. Service layer before API layer. API layer before UI.
- Each phase lists the files to create or modify. This is the "what changes" list that makes code review possible.
- **SSDT publish and EF Core Power Tools reverse-engineer are explicit gated steps** in any phase that introduces or modifies a database schema. Call them out as their own line items in the phase plan.
- **UI mockup conformance is a three-step hard gate** for every phase that creates or modifies [YOUR-UI-PAGES]. The phase plan must include: (1) Extract component spec from mockup as the first item, (2) Verify against mockup as the second-to-last item, and (3) CI verification as the last item. See scoping-ui-mockups.md and coding-blazor-ui.md Section 8.4.

### Plan doc size and structure

Cap the plan doc at approximately 500 lines. The plan doc is the "what are we building and why" document; it is not the execution log. If a plan doc exceeds 500 lines, it has absorbed detail that belongs elsewhere.

**Plan doc contains:** Sections 1-4 (problem statement, decisions table, data model, phase plan), the Wave Execution tracker table, and the vertical slice results.

**Decision log** (`docs/feat-issue-XX/decisions.md`): Cross-cutting decisions that affect multiple waves or change the plan's direction go here, not inline in the plan doc. Each entry has: date, decision, reasoning, and which waves are affected.

**Wave-level deviations live in the GitHub issue body.** Each wave issue includes a "Deviations from Plan" section. When the wave's implementation differs from what the plan doc says, it gets logged right there: what changed, why, and what downstream impact it has. This ties the drift to the specific wave that caused it.

**Anti-drift enforcement:** At the start of each wave, before writing code, read the plan doc and the previous wave's issue body. If the current wave's approach contradicts the plan, log the deviation in the issue body before code starts. Not after.

### Plan drift rule

When implementation deviates from the scope doc (data model changes, phase reordering, new entities added), update the plan doc in the same session, not as a catch-up exercise later. Log every deviation in the changelog with the date and reasoning.

### Pattern compliance check

After each phase completes, verify that the built code follows the patterns listed in the "Existing Pattern References" section of the scope doc. This catches drift between the decisions table and the actual code.

**What to check:** DI registration pattern, error handling pattern, settings injection pattern, logging pattern, database lifecycle, naming conventions.

### Phase naming convention

Use descriptive names, not just numbers. "Phase 3: [YOUR-SERVICE] & Real-Time Messaging" is better than "Phase 3."

---

## 8b. Implementation Orchestration & Progress Tracking

Every project plan includes an orchestration section that defines how phases execute (sequentially or in parallel waves) and a progress tracker that logs every component as it's completed.

### Wave-Based Parallelization

Group phases into waves based on dependency. Phases within a wave can execute concurrently. Phases in later waves depend on earlier waves completing.

**Format:**

```
Wave 1 (parallel):
  ├── Phase 1a — [description]
  ├── Phase 1b — [description]
  └── Phase 1c — [description]

Wave 2 (after Wave 1):
  ├── Phase 2a — [description]
  └── Phase 2b — [description]

Wave 3 (after Wave 2):
  └── Phase 3 — [description]
```

**Rules:**
- A wave only starts after all phases in the preceding wave are complete.
- Within a wave, phases must not have file-level conflicts (two agents editing the same file). If they do, they can't be in the same wave.
- The wave map should explain why the grouping works; what dependency is satisfied by the prior wave that unblocks the current one.
- Not every project needs parallelization. Small projects (3-4 phases, single builder) can stay sequential.

### Per-Component Progress Tracker

A table that lists every file or logical component from the phase plan, tracked individually. This is the execution log, updated in real time as work completes.

**Format:**

| Phase | Component | Status | Commit | Notes |
|-------|-----------|--------|--------|-------|
| 1 | [YourEntity].cs entity | DONE | abc1234 | — |
| 1 | DataContext.cs DbSets | DONE | abc1234 | 3 DbSets + Fluent API |
| 3 | [YourFeature]Service.cs | IN PROGRESS | — | Blocked on API response format |
| 4 | [YourFeature]Page.razor | PENDING | — | — |

**Status values:** `PENDING`, `IN PROGRESS`, `DONE`, `BLOCKED`, `SKIPPED`

**Rules:**
- One row per file or tightly coupled file group.
- Commit hash gets filled in when the component is pushed. This creates an audit trail linking the plan to the code.
- Notes column captures blockers, decision changes, or deviations from the plan.
- Update the tracker immediately after completing a component.

### Remaining Integration Items

A separate table for cross-cutting items that span multiple phases or require manual steps outside the code ([YOUR-NUGET], DI registrations, config changes, etc.).

**Format:**

| Item | Files | Status |
|------|-------|--------|
| Add [YOUR-LIBRARY] NuGet | [YourProject].csproj | NEEDS MANUAL ADD |
| Register new service in DI | Program.cs or DI extension | DONE (commit abc1234) |
| Config section | appsettings.json | PENDING |

This prevents the "I built all the components but forgot to wire them together" failure mode.

---

## 8c. Phased Execution Protocol

This section defines the gate sequence for executing a phased delivery plan. Where Section 8 defines what the phases are and Section 8b defines how to track them, this section defines how to execute each phase to completion.

### Per-Phase Gate Sequence

After all projects within a phase pass their individual compile-run-fix gates, run the phase-level gates:

1. **CI gate.** Push the phase commit to GitHub. GitHub Actions runs the full build and test suite. Monitor with the equivalent of `gh run watch`. All tests must pass.
2. **Fix any CI failures.** If the CI run surfaces regressions in other test projects, fix locally, push again.
3. **Update the plan.** Record actual test counts, deviations from the original plan, CI run number (for audit trail), and any issues that inform later phases.
4. **Phase commit.** Final commit updating the plan document with phase results and CI run reference.

### Execution Order vs Phase Number

Phases don't have to execute in numerical order. When phases have no dependencies, reorder by risk: the most depended-on code with the least test coverage goes first. Document the execution order in the plan.

### Phase Results Section

Every plan should include a "Phase Results" section that gets filled in after each phase completes. Each entry records: completion date, actual test count vs estimate, commit hash, deviations from plan, and issues that affect later phases. This section is the ground truth for cross-session continuity.

---

## 8d. Per-Wave Execution Checklist — The 7-Step Loop

This section defines the gate sequence for executing each phase to completion.

### Per-Phase Gate Sequence

After all projects within a phase pass their individual compile-run-fix gates, run the phase-level gates:

1. **CI gate:** Push to GitHub. GitHub Actions runs the full build and test suite. All tests must pass.
2. **Fix any CI failures:** If regressions appear, fix locally and push again.
3. **Update the plan:** Record actual results, deviations, and CI run number for the audit trail. Do this in the same session.
4. **Phase commit:** Final commit updating the plan with phase results and CI reference.

### Phase Results Section

Every plan includes a "Phase Results" section filled in after each phase completes. Record: completion date, test count vs estimate, commit hash, deviations, and issues affecting later phases.

This section is the ground truth for cross-session continuity.

---

## 8d. Per-Wave Execution Checklist

This is the mandatory execution loop for every wave in any plan. It runs automatically after the wave's code work is complete.

### The 7-Step Loop

**Step 1: Fix the issues**
Complete all code changes for this wave per the plan's task list. Every item in the wave's scope should be addressed.

**Step 2: Verify locally with [YOUR-BUILD-TOOL]**
Run the build and relevant tests on the host machine via [YOUR-BUILD-TOOL]. Confirm: no compile errors, no test failures. Do not push until local is clean.

**Step 3: Iterate until local is green**
If Step 2 surfaces failures, fix them and re-run. Repeat until the local build and tests pass. Do not skip to Step 4 on a red local state.

**Step 4: Push to GitHub**
Commit the wave's changes with a descriptive message referencing the wave number and what changed. Push to the feature branch.

**Step 5: Watch CI**
Run the equivalent of `gh run watch` (or check via `gh run list`) and wait for the GitHub Actions run to complete. A green badge is the gate, not the push itself.

**Step 6: Fix CI failures and repeat**
If CI fails, diagnose the failure, fix locally, push again, and return to Step 5. The CI run must be green before the wave closes.

**Step 7: Update the plan doc**
Once CI is green, update the plan document in the same session:
- Mark each completed item as `DONE` in the progress tracker
- Record the commit hash for each component
- Record the CI run number
- Note any deviations, surprises, or decisions made during the wave that affect later phases

A wave with green CI but no plan update is still open.

### Why each step matters

Steps 1-3 (local gate) catch easy failures before they become CI noise. Every CI failure costs a full run cycle. Catching compile errors locally takes 30 seconds; waiting for CI takes 2-5 minutes per attempt.

Steps 4-6 (CI gate) are the authoritative check. CI runs on clean infrastructure and is the ground truth. Step 5 is explicitly "wait," not "push and move on."

Step 7 (plan update) is what makes cross-session continuity possible. Without it, the next session has to reverse-engineer what's done, what's pending, and whether the last wave actually succeeded.

### When this loop runs

Every wave. No exceptions for "small" waves, "obvious" changes, or "just a fix." The loop is designed to be fast when things are clean (Step 2 passes, CI green on first try, plan update takes 2 minutes).

---

## 8e. Wave-Level GitHub Issues

Every wave in a plan gets its own GitHub issue before coding starts. The issue serves as the interactive execution tracker for that wave. The plan document remains the architecture reference; the issues are the execution layer.

### Wave Issue Template

```markdown
## Context Sync — Load These Before Resuming
> If continuing this issue after a context reset, load these files before doing anything else.

- `standards/coding-best-practices.md` — [YOUR-BUILD-TOOL] rule, required build platform
- `standards/coding-verification.md` — Verification agent requirements
- `standards/scoping-phased-delivery.md` — 7-step loop, this checklist
- `standards/banned-writing-styles.md`
- [Add wave-specific files: e.g., `coding-database.md` for DB waves, `coding-blazor-ui.md` for UI waves]

### Scope
[Copy the component list from the plan's phase definition. Each file or logical unit gets its own line.]

### Applicable Rules
[5-8 specific rules from the coding standards that apply to THIS wave's scope.]

### Execution Checklist
- [ ] Context sync — load all files above before proceeding
- [ ] Review plan section before writing any code
- [ ] Confirm [YOUR-INFRASTRUCTURE-ARCHITECTURE] is current if this wave adds/modifies any cloud resources
- [ ] [UI waves only] Extract component spec from mockup
- [ ] Write the code for all items in Scope
- [ ] [UI waves only] Verify against mockup (produce pass/fail checklist)
- [ ] Run Tier 2 verification agents (Code Review Agent for multi-file changes; UI Conformance Agent if [YOUR-UI-FRAMEWORK] modified)
- [ ] Verify staging is clean (`git status` shows no unstaged modifications)
- [ ] Build locally via [YOUR-BUILD-TOOL] — zero errors
- [ ] Run tests locally via [YOUR-BUILD-TOOL] — zero failures
- [ ] Commit and push via [YOUR-BUILD-TOOL] (`git commit` and `git push` on host machine)
- [ ] Watch CI (run `gh run watch` or check dashboard)
- [ ] Fix any CI failures and push again (return to CI watch step)
- [ ] Update plan doc: mark items DONE, record commit hashes, note CI run number
- [ ] Apply `needs: smoke-test` label if browser verification needed
- [ ] Post verification comment with results
```

---

## Plan Enforcement Gates  -  Quick Reference

### Gate 1: UI Mockups Approved Before Implementation

- Plan includes mockup step before UI phase starts
- Mockups are committed to the repo (not floating)
- Mockups are approved before the corresponding phase begins

### Gate 2: UI Conformance Baked Into Every UI Phase

- Every UI phase includes: Extract, Build, Verify steps
- Extract produces a Component Spec Checklist
- Verify produces a pass/fail artifact
- Component cannot be marked DONE without passing verification

### Gate 3: Local Build and Test Before Push

- Plan references the per-wave execution checklist
- Every wave runs local build and tests before pushing
- Local failures are fixed and re-verified before push

### Gate 4: CI Build Green Before Wave Closes

- CI run is watched after every push
- CI must be green before marking items DONE
- CI failures are diagnosed, fixed, and re-tested

### Gate 5: Plan Updated at End of Every Wave

- Plan doc is updated in the same session the wave completes
- Each item is marked DONE with commit hash and CI run
- Deviations are logged in the changelog
- Phase Results record date, test count, deviations, issues

---

## 8h. Smoke Test Checklist

When a wave is marked complete and ready for user-facing verification, apply the `needs: smoke-test` label to the wave issue. The smoke test is a manual run-through of the completed features in a staging or local environment before the wave closes.

**Smoke test is mandatory when:**
- UI components are changed or added
- External API integrations are modified
- Data flow paths are altered
- New configuration is introduced

**Smoke test can be skipped when:**
- Only service-layer code is changed with test coverage
- Only refactoring occurs with no behavioral changes
- Only documentation or comments are updated

**Format:**

```markdown
### Smoke Test Checklist
- [ ] [YOUR-FEATURE] renders without errors
- [ ] [YOUR-FEATURE] accepts valid input and submits
- [ ] [YOUR-FEATURE] rejects invalid input with appropriate error messages
- [ ] External API calls return expected data
- [ ] Database persistence works end-to-end
- [ ] Error handling catches and displays exceptions gracefully
- [ ] Logging captures relevant trace data
- [ ] Performance is acceptable (no hangs or slowdowns)
```

**After smoke test passes:** Remove `needs: smoke-test` label and close the wave issue.

---

## Corrections Log

*Tracks issues found when following this file's instructions.*

| Date | What Failed | Root Cause | Fix Applied |
|------|-------------|------------|-------------|

