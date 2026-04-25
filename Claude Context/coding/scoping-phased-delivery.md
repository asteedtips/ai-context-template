---
type: context-file
parent: "[[project-scoping-index]]"
summary: "Phased delivery plan rules (dependency ordering, SSDT gates, mockup conformance), implementation orchestration (wave parallelization, progress tracker), phased execution protocol (per-phase gate sequence), and per-wave execution checklist (the 7-step loop)."
tags: [coding, scoping, phased-delivery, orchestration, execution, waves]
---

# Phased Delivery & Execution

> **Part of the [[project-scoping-index|Project Scoping Graph]].** This file covers the phased delivery plan, implementation orchestration, execution protocol, and per-wave checklist. For the full scoping index, see [[project-scoping-index]].

## 8.0 Spike Phase Protocol

Not every feature has a clear shape at the start. When the architecture, data model, or external API integration is uncertain, a time-boxed spike runs before any feature branch is created. The spike's deliverable is the scoping doc, not shippable code.

### When to spike

Spike when any of these are true: (1) the feature involves an external API you haven't integrated before (e.g., new Zoho endpoint, new Graph scope, new Cosmos pattern), (2) the data model has more than 5 new entities and the relationships aren't obvious, (3) Albert says "let's figure this out first," or (4) no approved mockups exist yet for a UI-heavy feature.

Skip the spike when the feature is a well-understood pattern (another CRUD page, another action executor following the existing template, another settings tab) and the scoping doc can be written from existing knowledge.

### Spike rules

- **Branch:** `spike/issue-XX`. This branch is throwaway. It does not merge into `dev` or `feat/issue-XX`.
- **Time box:** 2 sessions max. If the spike hasn't produced a scoping doc after 2 sessions, stop and reassess with Albert. The spike may be too large, or the feature may need to be broken into smaller pieces.
- **Deliverable:** A scoping doc in `docs/feat-issue-XX/` with at least Sections 1-4 (problem statement, decisions table, data model, phase plan). The spike code is reference material, not a draft of the real implementation.
- **Vertical slice (mandatory):** During the spike, pick one end-to-end flow and run it against real data. For example: one email processed through one rule, one Zoho API call with a real invoice number, one Graph calendar fetch for a real user. Document the result (worked/failed/what was learned) in the scoping doc's Decisions section. This slice is the proof that the architecture holds before committing to a full build. See "Vertical Slice Gate" below.
- **Feature branch creation gate:** The `feat/issue-XX` branch cannot be created until the scoping doc exists with Sections 1-4 confirmed by Albert. The spike branch may be deleted at this point.

### Vertical Slice Gate

After the spike produces the scoping doc and before bulk implementation begins, one complete vertical slice must run end-to-end against real (or staging) data. The slice covers: UI form submission or trigger, service layer call, external API call with real credentials, response handling, and database persistence.

**What a valid slice proves:**
- Authentication and authorization work for the external API (token format, scopes, org IDs)
- The data model can persist and retrieve the output
- The DI registration pattern resolves correctly at runtime
- The happy path works before edge cases are addressed

**Document the slice** in the plan doc: which flow was tested, what data was used, what the result was, and any surprises (e.g., "the Zoho API returns `INV-36187` with a dash even though the vendor's remittance says `INV36187` without one"). This becomes the reference point for the full build.

**Lesson learned (Issue-54, April 2026):** The Zoho Books integration had 5 separate runtime bugs (keyed DI invisible to IEnumerable, empty org ID, invoice regex mismatch, missing OAuth token, paid invoice filter). All 5 would have been caught by a single vertical slice: process one real payment email through the Zoho Books executor. Instead, all executors were built horizontally and the bugs were discovered one at a time over 10+ sessions.

---

## 8. Phased Delivery Plan

Every project is broken into ordered phases. Phases are about dependency ordering and review gates, not scheduling. No hour estimates.

### Phase structure rules

- Each phase produces something testable or reviewable. "Set up the project" is not a phase by itself unless the project setup itself needs review (e.g., new solution structure, new Function App).
- Phases are ordered by dependency. Data model before service layer. Service layer before API layer. API layer before UI. Testing can be a separate phase or embedded in each phase; the scope doc should specify which.
- Each phase lists the files to create or modify. This is the "what changes" list that makes code review possible.
- **SSDT publish and EF Core Power Tools reverse-engineer are explicit gated steps** in any phase that introduces or modifies a database schema. Call them out as their own line items in the phase plan. Don't bury them as an assumption inside "Data Model & Database." See [[coding-database]] Section 4.4.
- **UI mockup conformance is a three-step hard gate** for every phase that creates or modifies Razor pages. The phase plan must include: (1) `X.1 Extract component spec from mockup` as the first item, (2) `X.N-1 Verify against mockup` as the second-to-last item, and (3) `X.N CI verification` as the last item. The Extract step produces a Component Spec Checklist written in the implementation framework's language (e.g., MudBlazor components). The Verify step walks the checklist and produces a ✅/❌ artifact. The component cannot be marked DONE until the verification artifact shows all items passing. This applies to both planned phases and reactive mid-PR phases. See [[scoping-ui-mockups]] and [[coding-blazor-ui]] Section 8.4.

### Plan doc size and structure

Cap the plan doc at approximately 500 lines. The plan doc is the "what are we building and why" document; it is not the execution log. If a plan doc exceeds 500 lines, it has absorbed detail that belongs elsewhere.

**Plan doc contains:** Sections 1-4 (problem statement, decisions table, data model, phase plan), the Wave Execution tracker table, and the vertical slice results.

**Decision log** (`docs/feat-issue-XX/decisions.md`): Cross-cutting decisions that affect multiple waves or change the plan's direction go here, not inline in the plan doc. Each entry has: date, decision, reasoning, and which waves are affected. Examples: "Switched from keyed DI to unkeyed DI because IEnumerable doesn't see keyed registrations," "Added ZohoTokenService singleton because per-request token refresh caused 80%+ CPU."

**Wave-level deviations live in the GitHub issue body.** Each wave issue (Section 8d template) includes a "Deviations from Plan" section. When the wave's implementation differs from what the plan doc says, it gets logged right there: what changed, why, and what downstream impact it has. This ties the drift to the specific wave that caused it and makes it visible in the PR conversation.

**Anti-drift enforcement:** At the start of each wave, before writing code, read the plan doc and the previous wave's issue body. If the current wave's approach contradicts the plan, log the deviation in the issue body before code starts. Not after.

**Lesson learned (Issue-54, April 2026):** The plan doc grew to 2,918 lines before being pruned to 416. It had become an execution log rather than an architecture reference. Sessions were skipping it entirely because it was too long to scan. Splitting into plan (architecture) + decision log (cross-cutting changes) + wave issues (execution details) keeps each artifact at a useful size.

### Architecture Context section (mandatory)

Every plan doc includes an "Architecture Context" section between the Decisions table and the Data Model. This is the per-feature slice of infrastructure context. The full topology lives in the project's master architecture doc (e.g., `docs/Azure-Environment-Architecture.md`). The plan doc carries only what this feature touches, with WikiLinks back to the relevant master arch sections.

**Why a per-feature slice instead of the full master doc.** Reading the full 60+ KB master arch doc at the start of every wave burns context on infrastructure that isn't relevant to the feature. The per-feature slice is small (typically 30-60 lines), can be loaded fast, and points back to the master doc via WikiLinks for any deeper read needed mid-wave. The slice is the resume artifact; the master doc is the authoritative source.

**Required sub-headings (omit any that don't apply, but keep the heading order):**

- **Compute** ,  which Function App, App Service, Web Job, or container runtime hosts this code
- **Data** ,  Cosmos containers, SQL tables, blob containers, Service Bus queues, etc. that this feature reads from or writes to
- **Identity** ,  system-managed identities, app registrations, role assignments, scope grants
- **Config** ,  App Configuration prefixes, Key Vault secrets, appsettings keys
- **Observability** ,  App Insights resource(s), log conventions, structured log scope keys, custom metrics
- **Integrations** ,  external APIs called (Microsoft Graph, Zoho, NetSapiens, etc.) with auth pattern
- **Deployment** ,  CI/CD workflows that ship this code, promotion path (dev verify, prd tag, etc.)
- **External Dependencies** ,  third-party rate limits, SLAs, fallback behavior
- **Out-of-Scope Infrastructure** ,  explicitly list what this feature does NOT touch

**Format example:**

```markdown
## Architecture Context

This feature touches the following existing infrastructure. For full topology see [[Azure-Environment-Architecture]].

### Compute
- TIP.App.Inbox.Func (Function App, dev: tip-dev-app-func-inbox / prd: tip-prd-app-func-inbox): runs the rule-suggestion timer ([[Azure-Environment-Architecture#function-apps]])

### Data
- Cosmos container `inbox-rules` (db: tip-app-shared-cosmos): stores suggested rules ([[Azure-Environment-Architecture#cosmos-tip-app-shared]])
- Cosmos container `inbox-runs` (db: tip-app-shared-cosmos): stores run history

### Identity
- System-assigned MI on tip-dev-app-func-inbox / tip-prd-app-func-inbox (Cosmos data contributor role) ([[README_Identity#system-managed-identities]])

### Config
- App Config prefix `SysCfg:App:Inbox:` (Inbox-specific)
- App Config prefix `SysCfg:Shared:Graph:` (delegated Graph credentials)

### Observability
- App Insights: tip-dev-app-shared-ai (dev), tip-prd-app-shared-ai (prd)
- Log conventions: `BaseService` + `LogService`; structured log scope keys `RuleId`, `RunId`

### Integrations
- Microsoft Graph (delegated tenant via refresh token)
- Zoho Books (admin-tier API client; via shared `ZohoOAuthService`)

### Deployment
- CI/CD: cd-dev.yml deploys on merge to dev; cd-prd.yml deploys on tag
- Promotion: dev verified clean for 24 hours before prd tag

### External Dependencies
- Microsoft Graph (rate limit 10000 req/10min per app)
- Zoho Books (rate limit 100 req/min per org)

### Out-of-Scope Infrastructure
- Does not touch SQL DB, NetSapiens API, SignalR, or any AppService
```

**WikiLink discipline.** Every sub-heading entry that has a corresponding section in the master arch doc must include a WikiLink to that section: e.g., `[[Azure-Environment-Architecture#cosmos-tip-app-shared]]`. This makes the resume path one click instead of a re-read.

**If no master arch doc exists for this repo:** Run the intake interview defined in [[architecture-intake]] to generate the master doc first, then write the per-feature Architecture Context section. The intake produces `docs/Azure-Environment-Architecture.md` (or `docs/Architecture.md` for non-Azure repos) and is a one-time cost per repo, not per feature.

**When to update.** When a wave adds, removes, or modifies any item in the Architecture Context section, update both the per-feature slice in the plan doc AND the corresponding section of the master arch doc in the same commit. The existing wave-issue checklist already requires updating the master arch doc when Azure resources change; this expands the rule to keep the plan doc's slice in sync as well.

### Plan drift rule

When implementation deviates from the scope doc (data model changes, phase reordering, new entities added, entities merged or removed), **update the plan doc in the same session, not as a catch-up exercise later.** Log every deviation in the changelog with the date and reasoning.

The SNOUT build changed from 7 separate per-tool job entities to a unified `SnoutJob` with a `ToolName` discriminator during scaffolding. That was a good design decision, but the plan wasn't updated until a separate audit session days later. By then, the plan and the code were out of sync, making cross-session handoffs harder. If the plan is always current, any session can pick up where the last one left off without reverse-engineering what actually got built.

### Pattern compliance check

After each phase completes, verify that the built code follows the patterns listed in the "Existing Pattern References" section of the scope doc. This catches drift between the decisions table (which says "use SettingsService") and the actual code (which might use `IOptions<T>` out of habit).

**What to check:** DI registration pattern, error handling pattern (`BaseServiceResult<T>`), settings injection pattern (`SettingsService` not `IOptions`), logging pattern (`BaseService` + `LogService`), database lifecycle (`IDbContextFactory`), naming conventions.

**Lesson learned (SNOUT, March 2026):** The SNOUT scaffolding used `IOptions<T>` with standalone settings POCOs in several places despite Decision #6 and Decision #15 in the decisions table both specifying `SettingsService`. The violations weren't caught until a build failure review. A pattern compliance check after Phase 1 would have caught them immediately.

### Phase naming convention

Use descriptive names, not just numbers. "Phase 3: SignalR Hub & Real-Time Messaging" is better than "Phase 3."

### Example from past projects

**Chat Feature (Track A):**
- Phase 1: Data Model & Migrations
- Phase 2: Repository & Service Layer
- Phase 3: REST API Controllers
- Phase 4: SignalR Hub & Real-Time Messaging
- Phase 5: Blazor UI Components
- Phase 6: Notification Pipeline (Push + Email)
- Phase 7: Testing
- Phase 8: Admin Bulk Messaging

**Meridian IVR (Track A, migration):**
- Phase 1: Scaffolding (projects, DI, solution structure)
- Phase 2: Entity Layer (VMs, enums, helpers)
- Phase 3: Service Layer (API clients, business logic)
- Phase 4: Function Layer (HTTP triggers)
- Phase 5: Testing
- Phase 6: Deployment

**Wix Integration (Track B):**
- Phase 1: Drop provider files, merge enum/DI changes
- Phase 2: Kernel settings model update
- Phase 3: App Configuration / Key Vault setup
- Phase 4: Testing sequence

---

## 8b. Implementation Orchestration & Progress Tracking

Every project plan includes an orchestration section that defines how phases execute (sequentially or in parallel waves) and a progress tracker that logs every component as it's completed. This section is added after the phase plan is defined and becomes the living execution dashboard during implementation.

### Why this matters

The HAF Chat Feature plan ran 8 phases across 5 parallel waves, with multiple agents working concurrently on independent work streams. Without an explicit wave map showing which phases could overlap and which had hard dependencies, the build would have been sequential by default. The orchestration section turned an 8-phase waterfall into a 5-wave concurrent build. The progress tracker caught a stale notification flag issue that would have been missed without per-component status tracking.

### Wave-Based Parallelization

Group phases into waves based on dependency. Phases within a wave can execute concurrently. Phases in later waves depend on earlier waves completing.

**Format:**

```
Wave 1 (parallel):
  ├── Phase 1a ,  [description]
  ├── Phase 1b ,  [description]
  └── Phase 1c ,  [description]

Wave 2 (after Wave 1):
  ├── Phase 2a ,  [description]
  └── Phase 2b ,  [description]

Wave 3 (after Wave 2):
  └── Phase 3 ,  [description]
```

**Rules:**
- A wave only starts after all phases in the preceding wave are complete.
- Within a wave, phases must not have file-level conflicts (two agents editing the same file). If they do, they can't be in the same wave.
- The wave map should explain *why* the grouping works; what dependency is satisfied by the prior wave that unblocks the current one.
- Not every project needs parallelization. Small projects (3-4 phases, single builder) can stay sequential. The wave map adds value when there are 5+ phases or when multiple agents/sessions can work concurrently.

### Per-Component Progress Tracker

A table that lists every file or logical component from the phase plan, tracked individually. This is the execution log, updated in real time as work completes.

**Format:**

| Phase | Component | Status | Commit | Notes |
|-------|-----------|--------|--------|-------|
| 1 | EntityName.cs entity | DONE | abc1234 | ,  |
| 1 | DataContext.cs DbSets | DONE | abc1234 | 3 DbSets + Fluent API |
| 3 | FeatureService.cs | IN PROGRESS | ,  | Blocked on API response format |
| 4 | FeaturePage.razor | PENDING | ,  | ,  |

**Status values:** `PENDING`, `IN PROGRESS`, `DONE`, `BLOCKED`, `SKIPPED`

**Rules:**
- One row per file or tightly coupled file group (e.g., entity + its Fluent API configuration can be one row).
- Commit hash gets filled in when the component is pushed. This creates an audit trail linking the plan to the code.
- Notes column captures blockers, decision changes, or anything that deviated from the plan.
- Update the tracker immediately after completing a component; don't batch updates at the end of a session.

### Remaining Integration Items

A separate table for cross-cutting items that span multiple phases or require manual steps outside the code (NuGet packages to add, DI registrations, config changes, etc.).

**Format:**

| Item | Files | Status |
|------|-------|--------|
| Add FluentValidation NuGet | API.csproj | NEEDS MANUAL ADD |
| Register new service in DI | Program.cs or DI extension | DONE (commit abc1234) |
| Config section in appsettings | appsettings.json | PENDING |

This table prevents the "I built all the components but forgot to wire them together" failure mode. It's populated during the phase plan and updated during execution.

### Lessons from past projects

The Chat Feature plan tracked 50+ individual components across 7 phases. Every component had a status and commit hash. When a notification default bug was discovered mid-build (three files hardcoding `false` instead of `true`), the tracker made it visible immediately and the fix was logged as a separate row. Without the tracker, that fix would have been buried in a bulk commit with no record of why it was needed.

---

## 8c. Phased Execution Protocol

This section defines the gate sequence for executing a phased delivery plan. Where Section 8 defines *what* the phases are and Section 8b defines *how to track* them, this section defines *how to execute* each phase to completion. The per-project compile-run-fix gate mechanics live in [[coding-best-practices]] Section 9.4.1; this section covers the orchestration layer on top of that.

### Per-Phase Gate Sequence

After all projects within a phase pass their individual compile-run-fix gates (see [[coding-best-practices]] Section 9.4.1), run the phase-level gates:

1. **CI gate.** Push the phase commit to GitHub. GitHub Actions runs the full build and test suite. Monitor with `gh run watch`. All tests must pass, not just the current phase's tests. This replaces the previous "solution gate" step because CI runs on infrastructure with the correct SDK and full disk space, which the Cowork VM often can't provide. See `github-actions-bp.md` Section 6 for the monitoring workflow.
2. **Fix any CI failures.** If the CI run surfaces regressions in other test projects (NuGet conflicts, namespace collisions, shared fixture changes), fix locally, push again. The concurrency group cancels the stale run automatically.
3. **Update the plan.** Record actual test counts, deviations from the original plan, CI run number (for audit trail), and any issues encountered that inform later phases. This happens in the same session, not as a catch-up task later (per Section 8's plan drift rule).
4. **Phase commit.** Final commit updating the plan document with phase results and CI run reference. This creates a clean audit trail linking the plan to the code and the CI run.

### Execution Order vs Phase Number

Phases don't have to execute in numerical order. When phases have no dependencies between them, reorder by risk: the most depended-on code with the least test coverage goes first. The Issue-52 unit test plan ran phases in order 1 → 6 → 2 → 3 → 4 → 5 → 7 → 8 because Phase 6 (Kernel) had no dependencies and covered foundational code that every other phase relied on.

Document the execution order in the plan. A reader should never have to guess which phase runs next.

### Phase Results Section

Every plan should include a "Phase Results" section (or equivalent) that gets filled in after each phase completes. Each entry records: completion date, actual test count vs estimate, commit hash, deviations from plan, and any issues that affect later phases. This section is the ground truth for cross-session continuity. A future session picking up the plan reads the results to understand what's done, what diverged, and what to expect next.

**Lesson learned (Issue-52, March 2026):** The Unit Test Implementation plan's Phase Results section captured 6 deviations in Phase 1 alone (test count exceeded 2x estimate, GraphAppRoleHandler reduced to structural tests due to non-virtual methods, InMemory EF key conflicts, extension method mocking nuances, JsonElement type sensitivity). Without that record, the next session would have hit the same issues again.

---

## 8d. Per-Wave Execution Checklist

This is the mandatory execution loop for every wave in any plan. It runs automatically after the wave's code work is complete; Claude does not wait to be asked. If any step is skipped, the wave is not done.

**Background:** Across multiple projects (Issue-52, Issue-54, HAF PR #59), the same pattern repeated: code was written, local state was assumed good, and the push/CI/plan-update steps were either skipped or only ran when Albert re-prompted them. This checklist exists to close that gap permanently.

### The 7-Step Loop

**Step 1: Write the code**
Complete all code changes for this wave per the plan's task list. Use the VM's Write/Edit tools to create and modify files. Desktop Commander is for build, test, and git operations ,  not file editing. Every item in the wave's scope should be addressed before moving forward.

**Step 2: Verify locally with Desktop Commander**

> ⚠️ **NEVER use the VM's dotnet install for this step ,  not even as a quick check.**
> The VM has disk constraints, an SDK version that may not match production, and cannot write to OneDrive-mounted `obj/` directories (virtiofs permission error). Any build attempt from VM bash will either silently use wrong artifacts or outright fail.
> **This rule applies equally when resuming a session after compaction.** If the open issue has a Context Sync block, load those files first ,  the Desktop Commander requirement is documented there and in [[coding-best-practices]] Section 9.4. Resuming a session does not exempt this step.

Run the build and relevant tests on Albert's Mac via Desktop Commander (`mcp__desktop-commander__start_process`).

- **Tool:** `mcp__desktop-commander__start_process` with the command below
- **dotnet path:** `/opt/homebrew/bin/dotnet` (always use full path; Desktop Commander runs under `/bin/sh` and does not inherit `.zshrc` PATH)
- **Repo root:** `~/CloudStorage/OneDrive-TrueIPSolutions,LLC/ClaudeCowork/Source Control/TIPS/[YOUR-PROJECT]/`
- **Build command:** `/opt/homebrew/bin/dotnet build {Project}.csproj`
- **Test command:** `/opt/homebrew/bin/dotnet test {TestProject}.csproj`
- **SSDT exception:** Skip `TIP.App.Database.Schema/` and `TIP.App.Database.Sql.*` projects on Mac. These are SSDT-managed and Mac can't build them. CI handles them via the Windows runner.

Confirm: no compile errors, no test failures in the affected area. Do not push until local is clean.

**Step 3: Iterate until local is green**
If Step 2 surfaces failures, fix them and re-run. Repeat until the local build and tests pass. Do not skip to Step 3.5 on a red local state.

**Step 3.5: Verify staging is clean**
Run `git status` and confirm no unstaged modifications (`M`), unstaged deletions (`D`), or unexpected untracked files (`??`). If any exist, stage them and re-run the local build to confirm. This step prevents the "local passes but CI fails" pattern where modified files are tested locally but not included in the commit. See [[coding-verification]] Section 14.5 for full details. Do not push until staging is clean.

**Step 4: Commit and push via Desktop Commander**
Run `git commit` and `git push` via Desktop Commander on Albert's Mac ,  not via VM bash. The OneDrive-mounted `.git/` folder can't handle lock file operations from the virtiofs VM mount, causing failures. The commands:

```
# Commit
mcp__desktop-commander__start_process
cmd: git -C "~/CloudStorage/OneDrive-TrueIPSolutions,LLC/ClaudeCowork/Source Control/TIPS/[YOUR-PROJECT]" commit -m "feat(wave-N): description of what this wave delivered"

# Push
mcp__desktop-commander__start_process
cmd: git -C "~/CloudStorage/OneDrive-TrueIPSolutions,LLC/ClaudeCowork/Source Control/TIPS/[YOUR-PROJECT]" push origin feat/issue-NN
```

Commit message format: `feat(wave-N): [what changed]`. Specific enough that a reader can understand what the wave delivered without opening the diff.

**Step 5: Watch CI**
Run `gh run watch` (or check via `gh run list`) and wait for the GitHub Actions run to complete. Do not move on while CI is running. A green badge is the gate, not the push itself.

**Step 6: Fix CI failures and repeat**
If CI fails, diagnose the failure (build error, test regression, NuGet conflict), fix locally, push again, and return to Step 5. The CI run must be green before the wave closes. Do not mark anything done on a red CI run.

**Step 7: Update the plan doc**
Once CI is green, update the plan document in the same session:
- Mark each completed item as `DONE` in the progress tracker
- Record the commit hash for each component
- Record the CI run number (from `gh run list` output)
- Note any deviations, surprises, or decisions made during the wave that affect later phases

This step is not optional and not a catch-up task. A wave with green CI but no plan update is still open.

### Why each step matters

Steps 1-3 (local gate) catch the easy failures before they become CI noise. Every CI failure costs a full run cycle. Catching compile errors and obvious test failures locally takes 30 seconds; waiting for CI takes 2-5 minutes per attempt.

Steps 4-6 (CI gate) are the authoritative check. The Cowork VM often can't run the full .NET build or test suite due to SDK and disk constraints. CI runs on clean infrastructure and is the ground truth. Step 5 is explicitly "wait," not "push and move on." A push that triggers a failing run that you don't watch means the next wave starts on a broken codebase.

Step 7 (plan update) is what makes cross-session continuity possible. Without it, the next session has to reverse-engineer what's done, what's pending, and whether the last wave actually succeeded.

### When this loop runs

Every wave. No exceptions for "small" waves, "obvious" changes, or "just a fix." The loop is designed to be fast when things are clean (Step 2 passes, CI green on first try, plan update takes 2 minutes). It only takes substantial time when something is wrong, which is exactly when you want it running.

---

## 8e. Wave-Level Git Issues

Every wave in a plan gets its own GitHub issue before coding starts. The issue serves as the interactive execution tracker for that wave, replacing the monolithic plan document as the "what am I working on right now" artifact. The plan document remains the architecture reference and long-lived decisions record; the issues are the execution layer.

### Why issues instead of plan doc rows

The issue-54 retrospective exposed a pattern: a 1,907-line plan document was too long to scan during a coding session. Steps were skipped because the checklist was buried inside a large file. GitHub issues solve three problems: (1) each coding session opens one issue, not a 1,900-line file; (2) checklists are interactive with visible progress bars; (3) issue close is the enforcement mechanism because you cannot close without checking every box.

### Issue hierarchy and tagging

Every feature gets a parent tracking issue. Each wave gets a child issue linked to the parent. The chain is:

```
Feature Issue (#54: Claude Inbox Monitor)
  ├── Wave 1 Issue (#54-W1: Database Schema & Entity Layer)
  ├── Wave 2 Issue (#54-W2: Service Layer)
  ├── Wave 3 Issue (#54-W3: Blazor UI Components)
  └── Wave 4 Issue (#54-W4: Azure Function & Testing)
```

**Naming convention:** `[Feature Short Name] Wave [N]: [Description]`

**Labels (apply to every wave issue):**
- `feat/issue-NN` (links to the parent feature issue)
- `wave` (identifies this as a wave execution issue, not a bug or feature request)
- `plan:[plan-doc-section]` (e.g., `plan:phase-5` maps the issue back to the plan document section it implements)

**Parent issue body** includes a task list of all wave issues so progress rolls up:

```markdown
## Waves
- [ ] #101 Wave 1: Database Schema & Entity Layer
- [ ] #102 Wave 2: Service Layer
- [ ] #103 Wave 3: Blazor UI Components
- [ ] #104 Wave 4: Azure Function & Testing
```

When a wave issue is closed, check the corresponding box in the parent. The parent closes when all wave boxes are checked.

### Wave issue template

Every wave issue body follows this template. The checklist is the enforcement mechanism; all boxes must be checked before the issue can be closed.

**The Context Sync block is mandatory.** Fill it in when creating the issue. It is the recovery mechanism if a session compacts or resets mid-wave ,  a resuming Claude reads this block and loads the files before touching any code or running any commands.

```markdown
## Wave [N]: [Description]

**Parent:** #[parent-issue-number]
**Plan section:** [Section reference, e.g., "Phase 5: Blazor UI Components"]
**Depends on:** #[prior-wave-issue] (or "None" for Wave 1)

## Context Sync ,  Load These Before Resuming
> If continuing this issue after a context reset or compaction, load these files before doing anything else.
> The rules that gate this checklist (Desktop Commander build, Tier 2 agents, staging check) live in these files.
> Do not run commands, write code, or check any box until these are loaded.

- `Claude Context/coding/coding-best-practices.md` ,  Desktop Commander build rule (Section 9.4), never VM dotnet
- `Claude Context/coding/coding-verification.md` ,  Tier 2 agent requirements (Section 14)
- `Claude Context/coding/scoping-phased-delivery.md` ,  7-step loop (Section 8d), this checklist
- `Claude Context/writing/banned-writing-styles.md`
- `docs/feat-issue-XX/Issue-XX-Plan.md` ,  **Architecture Context section** (the per-feature infrastructure slice; load this entire section, not the whole plan)
- `docs/Azure-Environment-Architecture.md` ,  full topology master doc; follow the WikiLinks from the plan's Architecture Context section to the specific master sections this wave touches (`#function-apps`, `#cosmos-tip-app-shared`, `#app-insights`, etc.)
- [Add wave-specific files: e.g., `coding-database.md` for DB waves, `coding-blazor-ui.md` for UI waves]

### Scope
[Copy the component list from the plan's phase definition. Each file or logical unit gets its own line.]

- EntityName.cs
- EntityConfig.cs (Fluent API)
- DataContext.cs (DbSet additions)

### Applicable Rules
[5-8 specific rules extracted from the coding standards graph that apply to THIS wave's scope. See Section 8f.]

### Execution Checklist
- [ ] **Context sync** ,  load all files in the Context Sync block above before proceeding (mandatory if resuming after compaction)
- [ ] **Architecture context gate (must be checked before writing any code)** ,  Read the plan doc's "Architecture Context" section AND every WikiLinked master arch doc section listed there. Confirm I can answer the following five questions in chat without re-reading: (1) which compute resource(s) does this wave run in? (2) which data plane(s) does it read from / write to? (3) which App Insights resource receives telemetry? (4) what auth pattern do external integrations use? (5) what is explicitly out of scope? If any answer requires re-reading, the gate has not passed; finish loading and re-verify before checking this box.
- [ ] **Review plan section** before writing any code
- [ ] **Confirm `docs/Azure-Environment-Architecture.md` is current** ,  if this wave adds or modifies any Azure resource (Cosmos container, App Config key, Key Vault entry, Function App, SignalR, etc.), update the arch doc AND the plan doc's Architecture Context section, and commit both before writing any application code. Adding resources after the fact is the gap this gate closes.
- [ ] **[UI waves only] Extract component spec from mockup** (Section 8.4 gate)
- [ ] **Write the code** for all items in Scope
- [ ] **[UI waves only] Verify against mockup** (produce pass/fail checklist)
- [ ] **Run Tier 2 verification agents** ,  Code Review Agent for any multi-file or service change; also UI Conformance Agent if Blazor components were modified. Both must return PASS before proceeding. (Per [[coding-verification]] Section 14.2–14.3. Fix any failures before the next step.)
- [ ] **Verify staging is clean** (`git status` shows no unstaged modifications)
- [ ] **Build locally via Desktop Commander** ,  `mcp__desktop-commander__start_process`, cmd: `/opt/homebrew/bin/dotnet build {Project}.csproj` from repo root. Skip SSDT projects (`TIP.App.Database.*`). Zero errors. **⚠️ Never use VM dotnet ,  see Section 8d Step 2.**
- [ ] **Run tests locally via Desktop Commander** ,  `/opt/homebrew/bin/dotnet test {TestProject}.csproj`. Zero failures.
- [ ] **Commit and push via Desktop Commander** ,  `git commit` and `git push` run on Albert's Mac, not VM bash (OneDrive virtiofs lock file constraint). Format: `feat(wave-N): description`
- [ ] **CI green** (`gh run watch` completes successfully)
- [ ] **Fix CI failures** if any (repeat push/watch cycle until green)
- [ ] **Update plan doc** (mark items DONE, record commit hash + CI run number)
- [ ] **Push plan doc update** (separate commit for audit trail)

### Deviations from Plan
[When this wave's implementation differs from the plan doc, log it here: what changed, why, and what downstream impact it has. If no deviations, write "None." This section is filled in during execution, not after.]

### Notes
[Filled in during execution: blockers, lessons learned, anything that doesn't fit in Deviations]
```

### Rules for wave issues

1. **Create before coding.** The wave issue must exist and be linked to the parent before the first line of code is written. Creating issues mid-wave defeats the purpose.
2. **One wave per session (recommended).** A session should not span more than one wave without a gate break. See "Session Length and Gate Breaks" in [[coding-best-practices]] Section 9.4.2.
3. **Close only when complete.** Every checkbox must be checked. A wave with green CI but an unchecked "Update plan doc" box is not closeable.
4. **Chain dependencies.** Each wave issue's "Depends on" field links to the prior wave. This creates a visible dependency chain. Do not start a wave whose dependency is still open.
5. **Update parent on close.** When closing a wave issue, check the corresponding line in the parent issue's wave task list. This keeps the parent's progress bar accurate.
6. **Deferred items become new issues.** If a wave discovers work that should be deferred (not in scope for this wave), create a new issue, label it with the feature tag, and reference it in the wave's Notes section. Do not silently add scope to the current wave.

### Creating wave issues from the plan

After the plan document is approved (scoping Step 13 in [[project-scoping-bp]]), create the wave issues as a batch:

1. Create the parent feature issue (if it doesn't exist already).
2. For each wave in the plan's orchestration section (Section 8b), create a child issue using the template above.
3. Populate the "Scope" section by copying the component list from the corresponding plan phase.
4. Populate "Applicable Rules" using the targeted rule extraction process (Section 8f).
5. Link all wave issues to the parent and to each other (dependency chain).
6. Apply labels: `feat/issue-NN`, `wave`, `plan:phase-N`.

### Completed waves and audit trail

Closed wave issues become the audit trail. The issue body (scope, checklist, notes) plus the linked commits tell the complete story of what happened during that wave. This is more discoverable than rows in a plan document because GitHub's issue search, labels, and timeline are purpose-built for this.

For retroactive documentation of completed work (e.g., applying this to issue-54's already-completed phases), create the wave issues with all checkboxes pre-checked and a note in the body: "Retroactive issue created [date] per retrospective recommendation. Work was completed in sessions [list session dates]."

---

## 8f. Targeted Rule Extraction Per Wave

Instead of loading the full 12-file coding standards graph before each wave, extract the 5-8 specific rules that apply to the wave's scope and put them in the wave's GitHub issue description (Section 8e, "Applicable Rules" field).

### Why this matters

The issue-54 retrospective found that loading 12 context files of standards before coding creates a false sense of compliance. The rules are read at session start, but they fade as the session progresses and cognitive load increases. Reading 5 targeted rules in the issue body creates actual awareness because each rule is directly relevant to the code being written.

### How to extract rules

When populating the "Applicable Rules" section of a wave issue:

1. **Identify the wave's concerns.** What kind of code is being written? Database entities? Service methods? Blazor components? API integrations?
2. **Pull from the coding index.** Use [[coding-index]] to find which graph nodes cover those concerns.
3. **Extract specific sections, not entire files.** Instead of "See [[coding-quality]]," write "DI registration: use `DI{Feature}Services.cs`, not `Program.cs` ([[coding-quality]] Section 2.1)."
4. **Include the lesson, not just the rule.** "Kernel Settings pattern, not `IOptions<T>` (see SNOUT Phase 1 deviation)" is more memorable than "Follow Section 3."
5. **Cap at 8 rules.** If more than 8 rules apply, the wave is probably too large. Split it.

### Rule extraction by wave type

| Wave type | Typical rules to extract |
|-----------|--------------------------|
| Database/Entity | IDbContextFactory lifecycle, Fluent API config, SSDT gated step, naming conventions |
| Service Layer | DI registration pattern, BaseServiceResult returns, async/CancellationToken, settings injection, error handling |
| Blazor UI | Mockup conformance gate (8.4), new page checklist (8.1.2), component size limit (~200 lines), dialog validation (8.1.4), SharedComponents layer check (8.8) |
| API Integration | Dry Run mode, Polly retry, credential handling, error surfacing via BaseServiceResult |
| Testing | 70% coverage target, test isolation (InMemory per-test), mock patterns, test naming |
| CI/CD | Desktop Commander local gate, `gh run watch`, concurrency group, fix-before-next-wave |

---

## 8g. Fix Issue Template

Fix issues (bugs, patches, regressions) get their own GitHub issue just like wave issues. They follow the same checklist discipline. "It's just a fix" is not an exemption ,  a fix that touches multiple files, modifies a UI component, or changes a service method is Tier 2 by definition and runs the same gates.

**What's different from a wave issue:**
- No "Review plan section" step (fixes are reactive, not planned-phase work)
- No mockup conformance gate unless the fix changes visual structure
- The parent link is to the feature issue or parent bug, not a wave hierarchy

**What's the same:**
- Labels applied at issue creation (not retroactively)
- Context Sync block populated before leaving the issue creation step
- PATCH the issue body as each step completes ,  do not rely on comments to communicate progress
- CI watched to green before any item is marked done
- `needs: smoke-test` label applied if Albert must pull and verify in browser

### Fix issue template

```markdown
## Problem
[1-2 sentence description of the bug. Include the screenshot or error message that triggered the issue.]

## Root Cause
[What in the code is wrong and why. Include file name and line if known.]

## Expected Behavior
[What it should do instead.]

---

## Context Sync ,  Load These Before Resuming
> If continuing this issue after a context reset or compaction, load these files before doing anything else.

- `Claude Context/coding/coding-best-practices.md`
- `Claude Context/coding/coding-verification.md`
- `Claude Context/coding/scoping-phased-delivery.md`
- `Claude Context/writing/banned-writing-styles.md`
- `Claude Context/coding/source-control.md`
- [Add any file specific to this fix, e.g. `coding-database.md` for schema fixes]

This issue: #NN | Branch: `feat/issue-NN`

---

## Execution Checklist

- [ ] Context sync (read files above if resuming after compaction)
- [ ] Apply label `feat/issue-NN` to this issue ← do this at issue creation, not retroactively
- [ ] Read affected file(s) to understand current state before changing anything
- [ ] Write the fix
- [ ] Build affected .csproj + test project(s) via Desktop Commander ,  0 errors. Never build solution-level (.sln/.slnx includes SSDT projects, which fail on macOS). See coding-best-practices.md Section 9.3.1 for SSDT exclusion list and targeted build pattern.
- [ ] Verify staging is clean (`git status` ,  no unstaged M or D files before pushing)
- [ ] Run tests via Desktop Commander ,  all pass
- [ ] Run Tier 2 verification agents if change touches multiple files, a service method, or any UI (Code Review Agent + UI Conformance Agent if Blazor involved)
- [ ] Commit and push via Desktop Commander (not VM bash ,  virtiofs lock file constraint)
- [ ] CI green ,  watch run via `curl` on the Actions API or Desktop Commander `gh run watch`. Do not mark done on a red CI run.
- [ ] PATCH this issue body to check off all completed items above ← posting a comment does NOT check boxes
- [ ] Apply `needs: smoke-test` label if any remaining verification requires Albert to pull and test in browser
- [ ] Post verification results as a comment on this issue
- [ ] Browser smoke test: [describe what Albert needs to verify] (remove this line if no human verification needed)
- [ ] Remove `needs: smoke-test` label and close issue after smoke test passes
```

### Fix issue rules

1. **Create before coding.** Same rule as wave issues ,  the issue must exist before the first line of code changes.
2. **Labels at creation.** `feat/issue-NN` goes on at creation. If you forget and add it later, that's a process gap ,  add it to the Corrections Log.
3. **PATCH the body, not just the comment.** After running each checklist step, PATCH the issue body to flip `- [ ]` to `- [x]`. Posting a verification comment records what was done but does not update the visible progress bar. Both are required.
4. **`needs: smoke-test` as a handoff signal.** Whenever remaining verification requires Albert to pull and confirm in a browser, apply this label before ending the session. This makes the handoff explicit at the GitHub project level rather than buried in chat history. Albert removes it (or closes the issue) after confirming.
5. **CI watch is not optional.** Every push triggers a CI run. `gh run watch` (or equivalent curl check) must confirm green before the wave closes. Pushing and moving on without watching is a process gap regardless of whether local tests passed.
6. **Architecture.md.** If any component changed that appears in Architecture.md, update that file before closing the session. See `source-control.md` Architecture.md Convention.
7. **Template at creation, not after the fact.** The fix issue body must use the Section 8g template at the moment the issue is created ,  not filled in retroactively once the code is done. If an issue is created mid-session under time pressure (e.g., during a reload after context overflow), stop and populate the full template before writing any code. A bare-description issue with no Execution Checklist is a process gap the same as a missing label. If you created an issue without the template, reopen it, PATCH the body with the full template (marking already-completed steps `[x]`), and add `needs: smoke-test` before ending the session.

---

## Plan Enforcement Gates ,  Quick Reference

This section is a single-pass checklist for verifying that a plan contains all mandatory execution gates. Use it during plan review (scoping Step 11) and before approving the plan (Step 13). Every item below must be verifiable by reading the plan; if an item can't be confirmed from the plan text, the plan has a gap.

### Gate 1: UI Mockups Approved Before Implementation

- [ ] Plan includes a mockup step before any UI phase starts (not after, not during)
- [ ] Mockup files are committed to the repo, not floating in ClaudeCowork or chat
- [ ] Albert has approved each mockup screen before the corresponding phase begins
- [ ] For reactive phases created mid-PR: the plan includes the 6-step Reactive Phase Startup Sequence from [[scoping-ui-mockups]] (create, save, commit, approve, plan waves, extract spec)

**What goes wrong without this gate:** HAF Chat Phase 5 built two thread list pages without ever opening the approved mockup. Tyler's review flagged 8 issues, all of which the mockup already addressed. The entire Phase 6 was avoidable rework.

### Gate 2: UI Conformance Baked Into Every UI Phase

- [ ] Every phase that creates or modifies a Razor page includes these three line items:
  - `X.1 Extract component spec from mockup` (first item in the phase)
  - `X.N-1 Verify against mockup` (second-to-last item)
  - `X.N CI verification` (last item)
- [ ] The Extract step produces a Component Spec Checklist written in the implementation framework's language (e.g., MudBlazor component names)
- [ ] The Verify step produces a pass/fail artifact (the checklist with each item marked). The component cannot be marked DONE without this artifact.
- [ ] This applies equally to planned phases and reactive mid-PR phases

**What goes wrong without this gate:** All six SNOUT pages diverged from their approved mockups. An unplanned Phase 6b correction pass was needed. Root cause: pages were built from the service layer up, not from the mockup down.

### Gate 3: Local Build and Test via Desktop Commander

- [ ] The plan references the per-wave execution checklist (Section 8d) or includes its own local verification steps
- [ ] Every wave runs a local build and test pass on the host machine via Desktop Commander before pushing
- [ ] Local failures are fixed and re-verified before any push to GitHub
- [ ] "Local is green" is a prerequisite for Step 4 (push), not an optional nice-to-have

**What goes wrong without this gate:** Every CI failure that could have been caught locally costs a full run cycle (2-5 minutes). Across Issue-52, multiple waves pushed with local failures still present, burning CI runs on predictable compile errors.

### Gate 4: CI Build Green Before Wave Closes

- [ ] The plan includes `gh run watch` (or equivalent) as an explicit step after every push
- [ ] CI must be green before any item is marked DONE in the progress tracker
- [ ] CI failures are diagnosed, fixed locally, pushed again, and re-watched. The loop repeats until green.
- [ ] A wave with green local but red CI is not done. CI is the ground truth, not the local build.

**What goes wrong without this gate:** A push that triggers a failing run that goes unwatched means the next wave starts on a broken codebase. Across HAF PR #59, multiple pushes were made without watching the CI result, and regressions accumulated silently.

### Gate 5: Plan Updated at End of Every Wave

- [ ] The plan doc is updated in the same session the wave completes, not as a catch-up task later
- [ ] Each completed item is marked DONE with commit hash and CI run number
- [ ] Deviations from the original plan are logged in the changelog with date and reasoning
- [ ] Phase Results section records: completion date, actual test count vs estimate, deviations, issues affecting later phases

**What goes wrong without this gate:** The SNOUT build had a design change (7 entities to 1 unified entity) that wasn't recorded in the plan until days later. By then, the plan and code were out of sync, making cross-session handoffs unreliable. Any session picking up the work had to reverse-engineer what actually got built.

---

## 8h. Smoke Test Checklist

Every feature's plan doc includes a Smoke Test Checklist: the 5-10 specific user-facing behaviors that prove the feature works when Albert tests it in the browser. This checklist replaces ad-hoc exploration with structured verification.

### When to write the checklist

Write it during scoping, after the vertical slice is confirmed and the phase plan is approved. The checklist goes in the plan doc as its own section. It is not a late addition; the act of writing it forces you to think about what "done" actually looks like from a user's perspective.

### Checklist format

Each item has three parts: what to do, what should happen, and where to check it.

```markdown
## Smoke Test Checklist

| # | Action | Expected Result | Page/Route |
|---|--------|----------------|------------|
| 1 | Click "Run Now" on Albert's inbox | Processing starts, SignalR progress updates appear in real time | /ai-dashboard/inbox/{id} |
| 2 | Wait for run to complete | Toast notification, bell icon shows unread count | Any page (top bar) |
| 3 | Open Run Detail for the completed run | All processed emails shown with action results, no "CompletedWithErrors" | /ai-dashboard/inbox/run/{runId} |
| 4 | Open a Zoho Books payment email result | Invoice number extracted, Zoho lookup shows matched invoice with amount | Run detail > expand email row |
| 5 | Check Today's Brief page | Shows most recent run summary + calendar section with meetings | /ai-briefing |
```

### Linking to issues

When `needs: smoke-test` is applied to an issue, the issue body must include the specific checklist items from the plan doc that apply to that issue. Not just the label; the actual test steps. Copy the relevant rows from the checklist table and paste them into the issue body under a `## Smoke Test` heading. Albert can then check them off directly in the issue after testing.

**Lesson learned (Issue-54, April 2026):** The `needs: smoke-test` label was used on dozens of issues, but there was no documented definition of what a smoke test covers or what "passing" looks like. Albert was effectively the QA team, discovering bugs through ad-hoc exploration. 83 of 95 issues were found and fixed same-day, meaning each one was a round-trip of "Albert finds it broken, reports back, Claude fixes it." A defined checklist would have caught clusters of related issues in a single pass instead of one at a time.

---

## Corrections Log

*Tracks issues found when following this file's instructions. Entries are added when a discrepancy is discovered and a fix is applied or proposed.*

| Date | What Failed | Root Cause | Fix Applied | ERRORS.md Ref |
|------|-------------|------------|-------------|---------------|
| 2026-04-05 | Issues #69, #70, #71 closed with dotnet test unrun, Tier 2 agents not invoked, missing unit tests unchecked | Wave/fix issue template had no Tier 2 agent checkbox; no Context Sync block to guide a resuming session back to the rules | Added Context Sync block and `[ ] Context sync` as first checklist item; added `[ ] Run Tier 2 verification agents` item; added VM hard-stop callout to Step 2 | ,  |
| 2026-04-05 | Fix issues #72/#73/#75 had labels applied retroactively, checkboxes never PATCHed, no CI watch after push, no staging check, no `needs: smoke-test` handoff signal | Fix issues were using an ad-hoc checklist derived from the wave template but missing four explicit gates: label-at-creation, issue body PATCH, CI watch, and staging check. No dedicated fix issue template existed. | Added Section 8g: Fix Issue Template with complete checklist including all four missing gates plus `needs: smoke-test` label rule. Created `needs: smoke-test` label in [YOUR-PROJECT] repo. | ,  |
| 2026-04-05 | Fix issues #80 and #81 created mid-session (context reload) without Section 8g template ,  plain description only, no Execution Checklist, no `needs: smoke-test` label, closed before smoke test. | Session was under pressure after context overflow reload. Issue creation happened as a "quick reference" step before coding rather than following the full template. Section 8g existed but had no rule explicitly requiring template population before coding when an issue is created mid-session. | Added Rule 7 to Section 8g Fix Issue Rules: template must be applied at creation, not retroactively. If created bare, reopen and PATCH before ending the session. Retroactively PATCHed #80 and #81 with full template and `needs: smoke-test` label. | ,  |

**Notes:**
<!-- Per-entry context that doesn't fit in the table. Format: "YYYY-MM-DD: [explanation]" -->
2026-04-05: The two failures were structurally independent. (1) The issue template was missing the Tier 2 agent checkbox entirely ,  it was only in coding-verification.md, not in the checklist Claude actually executes against. (2) The VM dotnet rule existed in coding-best-practices.md but was invisible to a session resuming after compaction because that file wasn't reloaded. The Context Sync block fixes both by making the issue itself the recovery artifact.
2026-04-05 (second entry): The comment vs. PATCH distinction was never made explicit anywhere in the process docs. Posting a verification comment to an issue and PATCHing its body to tick checkboxes are two different API calls ,  the session was only making one of them. Added the PATCH step as an explicit checklist item in both the fix issue template (8g) and as a note in coding-verification.md Section 14.3. The `needs: smoke-test` label formalized the handoff signal so Albert has a GitHub-level view of what's waiting for him without relying on chat history.
2026-04-05 (third entry): Issues #80/#81 created bare mid-reload-session. Fix: Rule 7 added to 8g ,  template is non-negotiable at creation, regardless of session pressure. The template is the recovery artifact; creating a bare issue then filling it in later defeats the purpose of the Context Sync block.
