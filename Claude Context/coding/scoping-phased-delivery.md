# Phased Delivery & Execution

> **Part of the Project Scoping Graph.** This file covers the phased delivery plan, implementation orchestration, execution protocol, and per-wave checklist. For the full scoping index, see `project-scoping-index.md`.

## Phased Delivery Plan

Every project is broken into ordered phases based on dependencies, not estimated time.

### Phase structure rules

- Each phase produces something testable or reviewable
- Phases are ordered by dependency: data model before service, service before API, API before UI
- Each phase lists files to create or modify
- Database schema changes have explicit gated steps (design, migration, reverse-engineer)
- UI mockup conformance is a three-step hard gate for every phase that creates Razor pages

### Plan drift rule

When implementation deviates from the scope doc (data models change, entities added/removed, phase reordering), **update the plan in the same session, not later.** Log every deviation in the changelog with the date and reasoning.

If the plan is always current, any session can pick up where the last one left off without reverse-engineering what was built.

### Pattern compliance check

After each phase completes, verify that the built code follows the patterns listed in the scope doc's "Existing Pattern References" section. This catches drift between decisions and actual code.

---

## Implementation Orchestration & Progress Tracking

Every project plan includes an orchestration section defining how phases execute (sequential or parallel waves) and a progress tracker logging each component as it completes.

### Wave-Based Parallelization

Group phases into waves based on dependencies. Phases within a wave execute concurrently. Phases in later waves depend on earlier waves completing.

```
Wave 1 (parallel):
  ├── Phase 1a  -  [description]
  ├── Phase 1b  -  [description]
  └── Phase 1c  -  [description]

Wave 2 (after Wave 1):
  └── Phase 2  -  [description]
```

**Rules:**
- A wave only starts after all phases in the preceding wave are complete
- Within a wave, phases must not edit the same files
- The wave map should explain why the grouping works

### Per-Component Progress Tracker

A table listing every file or logical component from the phase plan, tracked individually.

| Phase | Component | Status | Commit | Notes |
|-------|-----------|--------|--------|-------|
| 1 | Entity.cs | DONE | abc1234 |  -  |
| 2 | Service.cs | IN PROGRESS |  -  |  -  |
| 3 | Controller.cs | PENDING |  -  |  -  |

**Status values:** `PENDING`, `IN PROGRESS`, `DONE`, `BLOCKED`, `SKIPPED`

**Rules:**
- One row per file or tightly coupled file group
- Fill in commit hash when the component is pushed (audit trail)
- Update immediately after completing a component; don't batch updates

### Remaining Integration Items

A table for cross-cutting items spanning multiple phases (NuGet packages, DI registrations, config changes).

| Item | Files | Status |
|------|-------|--------|
| Add library NuGet | Project.csproj | NEEDS MANUAL ADD |
| Register in DI | Program.cs | DONE (commit abc1234) |
| Config section | appsettings.json | PENDING |

---

## Phased Execution Protocol

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

## Per-Wave Execution Checklist

This is the mandatory execution loop for every wave. If any step is skipped, the wave is not done.

### The 7-Step Loop

**Step 1: Fix the issues**
Complete all code changes for this wave per the plan.

**Step 2: Verify locally**
Run the build and tests on your host machine. Confirm no compile errors or test failures.

**Step 3: Iterate until local is green**
If Step 2 fails, fix and re-run. Repeat until clean.

**Step 4: Push to GitHub**
Commit with a descriptive message referencing the wave number.

**Step 5: Watch CI**
Run the equivalent of `gh run watch` and wait for completion. Do not move on while CI runs.

**Step 6: Fix CI failures and repeat**
If CI fails, diagnose, fix locally, push again, return to Step 5. CI must be green.

**Step 7: Update the plan doc**
Once CI is green, update the plan in the same session:
- Mark completed items as `DONE`
- Record commit hashes and CI run number
- Note deviations and decisions affecting later phases

A wave with green CI but no plan update is still open.

### Why each step matters

Steps 1-3 catch easy failures before they become CI noise. Local verification takes 30 seconds; CI takes 2-5 minutes per failed run.

Steps 4-6 are the authoritative gate. Your host machine is the ground truth for development.

Step 7 enables cross-session continuity. Without it, the next session has to reverse-engineer what's done.

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

## Corrections Log

*Tracks issues found when following this file's instructions.*

| Date | What Failed | Root Cause | Fix Applied |
|------|-------------|------------|-------------|

