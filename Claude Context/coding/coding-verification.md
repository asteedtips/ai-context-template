---
type: context-file
parent: "`coding-index.md`"
summary: "Verification Agent Protocol: complexity-tiered sub-agent review (code review, UI conformance, external API) with isolation rules and mandatory sequencing before marking tasks done."
tags: [coding, verification, code-review, agents]
---

# Verification Agent Protocol

> **Part of the the Coding Standards Graph (`coding-index.md`).** This file covers the verification agent system for automated code review. For the full standards index, see `coding-index.md`.

When Claude is writing or modifying code, it can spin up independent sub-agents to review the work before marking it done. This catches the same categories of issues that have historically surfaced in Tyler's reviews or required unplanned correction phases (SNOUT Phase [N]b, [YourProject] Chat Phase [N]). The protocol is complexity-gated: small changes don't need it, large changes require it.

## 14.1 Complexity Tiers

| Tier | Scope | Agent Strategy |
|------|-------|----------------|
| **Tier 1: Small** | Single file, <50 lines changed, no UI | No verification agent. Review is built into the primary coding pass. |
| **Tier 2: Medium** | Multiple files, new service methods, or any UI work | One verification agent after coding is complete. |
| **Tier 3: Large** | New feature, multi-phase, touches external APIs or database schema | Two verification agents in parallel after each phase milestone. |

**How to determine the tier:** The scope is known from the phase plan before any code is written. If there's no phase plan (ad-hoc fix, quick patch), use the file count and change size to classify. When in doubt, round up: a Tier 2 review on a borderline-Tier-1 change costs seconds; missing a real issue costs a correction phase.

**UI Tier 2 requirements.** When a Tier 2 review touches UI (`.razor`, `.razor.cs`, or your framework's equivalent component files), the verification artifact must include BOTH of the following before the work can be marked done, in addition to the code review agent:

1. **Mockup Conformance Hard Gate Step C re-run.** Walk the Component Spec Checklist (produced in Step A) against the actual rendered output, line by line. Record `[OK]` or `[FAIL]` per item in the phase plan. Any `[FAIL]` is blocking.
2. **Analyzer warning audit.** Run the build, list every distinct framework analyzer warning (for example, MudBlazor `MUD####`, ASP.NET `BL####`, Razor `RZ####`, or your UI framework's equivalent codes) in the output, and resolve each per the Analyzer Warning Discipline rule in 14.1.x. No matching analyzer warning may carry into a closed Tier 2 verification.

Both items are independent of the code review agent. The code review agent reads source; the conformance and analyzer audits read the build output and rendered DOM. All three must pass.

### 14.1.x Analyzer Warning Discipline

Framework analyzer warnings (MudBlazor `MUD####`, ASP.NET `BL####`, Razor `RZ####`, and similar codes from any UI framework you use) are blocking for any Tier 2 UI verification. Treat them as compile errors, not noise, regardless of whether the solution build reports success. The analyzer's job is to surface renamed or removed APIs across framework major versions; ignoring its output is how a working code path silently turns into a broken one.

**Required handling when these warnings appear in a build that touches UI:**

1. List every distinct analyzer code surfaced by the build output (for example, `MUD0002 Illegal Attribute 'IsVisible' on 'MudDialog' using pattern 'LowerCase'`).
2. For each code, open the framework source in the version control tag matching the project's package version. Compare the attribute name, type, and pattern against the source.
3. If the analyzer message confirms an API rename or removal, fix the call site before closing the verification step. If the analyzer is wrong (rare), document the disagreement in the verification artifact with a link to the framework source line.
4. Never dismiss an analyzer warning as "pre-existing" without running steps 1-3 first. "Pre-existing" is a hypothesis, not a verdict.

<!-- CUSTOMIZE: replace with your project's most expensive analyzer-warning miss. The pattern: a real incident, the exact warning code, the underlying API rename, and the consequence. -->
**Example incident pattern:** A UI framework's analyzer reported an attribute-name violation across multiple components. The team dismissed it as pre-existing noise because the solution build still succeeded. The warning was the real signal of a major-version API rename. Two consecutive commits shipped a regression that was only caught by manual smoke testing after CI green. The fix was a one-character rename per file. The analyzer had been reporting the answer the whole time.

### 14.1.y Shared Components Discovery Gate

Before writing any new UI component or service that resembles existing functionality, grep the codebase first. Reuse beats reinvent. The trigger words are broad: export, download, date picker, date range, filter, multi-select, modal, dialog, chart, table, drawer, snackbar, tooltip, breadcrumb, pagination, search, toolbar, header, footer, card, badge, chip, icon, loading, skeleton, empty state, error state, alert. Any UI helper, any service helper, any shared concept.

**Required handling when starting a new component or service:**

1. State the function in plain language ("I am about to build a date range picker with presets") so grep terms are obvious.
2. Grep the repo before writing:
   - `find {repo} -type f \( -name '*.razor' -o -name '*.cs' -o -name '*.tsx' -o -name '*.vue' \) -not -path '*/obj/*' -not -path '*/bin/*' -not -path '*/node_modules/*' | xargs grep -l '{ConceptName}'`
   - List the candidate shared-component folders for your stack (for example `{Shared.UI}/Components/`, `{BoundedContext}.UI/Components/`, or your framework's equivalent location).
   - List any candidate service helper projects for the concept (export, notifications, reporting, etc.).
   - For third-party libraries: `grep -rln '{LibraryName}' {repo}` against your project files.
3. Read the existing artifact. Two outcomes:
   - Reusable as-is or with a small extension: wire to the new caller, extend with new parameters in a backwards-compatible way, ship.
   - Genuinely needs a new component: document why ("existing X at Y did not fit because Z") in the commit message.
4. Never assume the concept does not exist yet without grep evidence. "Nobody has built this" is a hypothesis, not a verdict.

<!-- CUSTOMIZE: replace with your project's most expensive missed-reuse incident. The pattern: a real incident, the existing shared component that was missed, the per-page reimplementation that shipped, the retrofit cost. -->
**Example incident pattern:** A UI wave starts from an approved mockup. The mockup shows a date range picker, an export menu, and a filter chip. The author builds those inline inside the new page. Post-delivery review catches that the date range picker and the export service already existed as shared infrastructure elsewhere in the codebase. A retrofit commit replaces the per-page implementations with the shared components. The whole retrofit was avoidable with a thirty-second grep before the first line of the new page was written. UI waves that start from a mockup are the most common violation site, because the mockup shows the helpers inline and the reflex is to render them per-page.

## 14.2 What Each Agent Checks

**Code Review Agent (Tier 2 and Tier 3):**

The agent receives the diff (or full file for new files) plus the coding standards files. It checks against the concrete rules defined in `coding-architecture.md`, `coding-quality.md`, `coding-config.md`, `coding-database.md`, and `coding-testing.md`:

- Layer reference direction: no upward refs (Section 1.1)
- DI registration pattern: `DI{Feature}Services.cs`, not `Program.cs` (`coding-quality.md` Section 2.1)
- Kernel Settings pattern: not standalone `IOptions<T>` (Section 3, TIPS only)
- `IDbContextFactory<T>` lifecycle: not injected `DbContext` (Section 4)
- `BaseServiceResult<T>` return types on service methods
- No `.Result` or `.Wait()` on Tasks
- Explicit typing over `var` (Section 2.1)
- Braces on all control flow (Section 2.2)
- XML docs on public methods in Service and Service.Entity projects
- TODO/HACK/FIXME has a tracked work item
- No PII in log statements
- `AsNoTracking()` on read-only queries
- Async methods use `CancellationToken` parameters
- Exception handling follows `BaseServiceResult` pattern, no silent swallowing

The agent produces a pass/fail list. Any failure blocks the task from being marked done.

**UI Conformance Agent (Tier 2 with UI, Tier 3 with UI):**

Only runs when the change involves Blazor/Razor components and an approved mockup exists. Executes the `coding-blazor-ui.md` Section 8.4 three-step gate:

- Opens the mockup file
- Walks the component spec checklist line by line against the implemented markup
- Produces ✅/❌ output for each checklist item
- Checks the new routable page checklist (Section 8.1.2) if any `@page` components were added

Any ❌ item blocks the task from being marked done.

**External API Agent (Tier 3 only, when applicable):**

Only runs when the change touches external APIs (Zoho, Graph, webhooks). Checks:

- Dry Run mode implementation if no sandbox exists (`coding-testing.md` Section 6.7)
- Polly retry policies on HTTP clients
- No hardcoded credentials (defers to `security-practices.md`)
- Error handling on API responses: failures surface via `BaseServiceResult`, not swallowed

## 14.3 When Agents Run

Agents run **after coding is complete but before the task or phase is marked done.** They do not replace GitHub Actions CI. CI validates compilation and test execution. Verification agents validate pattern compliance and conformance to standards that CI can't check (mockup fidelity, architecture rules, naming conventions).

**Sequence:**
1. Code the change
2. Run verification agent(s) based on tier
3. Fix any failures surfaced by agents
4. Push to `feat/*` branch (triggers CI)
5. CI validates compilation and tests
6. Mark phase/task done only after both agent review and CI pass

**Fix issues follow the same rules as wave issues.** A bug fix or patch issue that touches multiple files, adds a service method, or modifies UI is Tier 2 by definition. The fix issue checklist must include the Tier 2 agent step just as a wave issue would. "It's just a fix" is not an exemption — the complexity tier is determined by the scope of the change, not the intent.

**Resuming a session after compaction does not skip this step.** If a session is picked up mid-task after a context reset, the agent steps are not assumed to have been completed in the previous session. Check the open issue's checklist: if the Tier 2 agent checkboxes are not ticked, run the agents before closing the issue. The issue's Context Sync block (Section 8e of `project-scoping-bp.md`) lists the files to load first — read those before running any agents or commands.

**Posting a verification comment and PATCHing the issue body are two separate required steps.** After running agents and posting a comment with the results, you must also PATCH the issue body via the GitHub API to flip each completed checklist item from `- [ ]` to `- [x]`. Comments record what was done; the issue body's checkboxes drive the visible progress bar and are the enforcement mechanism for closing. Do not consider a checklist item complete until the box is ticked in the body — a comment alone is not sufficient.

## 14.4 Agent Isolation

Verification agents run with `isolation: "worktree"` when possible, giving them a clean copy of the repository. This prevents the reviewing agent from being influenced by uncommitted scratch work or partial changes in the working tree. When worktree isolation isn't available (e.g., mounted volume constraints), the agent still reviews the diff independently but notes that it's operating on the working copy.

## 14.5 Pre-Push Staging Verification

Before every `git push`, run a staging verification step. This is a separate gate from the verification agents (which check code quality) and from the local build (which checks compilation). This gate checks that what you are about to push matches what you tested locally.

### The problem this solves

Two of three CI cascades in issue-[N] traced to the same root cause: files were modified locally but not staged for commit. The local build passed (using the modified files in the working directory), but CI built from the committed state (without the modifications). The result was predictable compile errors that cost multiple push/fix/repush cycles.

### The gate

After the local build and tests pass (Section 8d Steps 2-3) and before the push (Section 8d Step 4), run:

```bash
git status
```

**Check for:**
- `M` (modified but not staged) files. These were changed but won't be in the commit. Either stage them (`git add`) or explain in the commit message why they are excluded.
- `D` (deleted but not staged) files. These were removed locally but still exist in the commit. Stage the deletion (`git rm`) or restore the file.
- `??` (untracked) files. New files that won't be in the commit. Either stage them or confirm they are intentionally untracked (e.g., local config overrides).

**Pass condition:** `git status` shows only staged changes and intentionally untracked files. No unstaged modifications, no unstaged deletions.

**Failure action:** Do not push. Stage the missing changes, re-run the local build to confirm nothing broke, then proceed to push.

### Integration with the 7-step loop

This gate inserts between Step 3 (iterate until local green) and Step 4 (push). The sequence becomes:
1. Fix issues → 2. Verify locally → 3. Iterate until green → **3.5. Verify staging is clean** → 4. Push → 5. Watch CI → 6. Fix CI → 7. Update plan

The wave issue checklist template (Section 8e) already includes this as a checkbox: "Verify staging is clean (`git status` shows no unstaged modifications)."

---

## Corrections Log

*Tracks issues found when following this file's instructions. Entries are added when a discrepancy is discovered and a fix is applied or proposed.*

| Date | What Failed | Root Cause | Fix Applied | ERRORS.md Ref |
|------|-------------|------------|-------------|---------------|
| 2026-04-05 | Fix issues #69, #70, #71 closed without running Tier 2 agents | Section 14.3 scoped agents to "phases" and "waves" — fix issues were not explicitly covered; resuming sessions had no instruction to confirm prior agent steps | Added explicit paragraphs: fix issues follow the same tier rules; resuming sessions must check the issue checklist before assuming agents ran | — |
| 2026-04-05 | Fix issues #72/#73 — verification comments posted but issue body checkboxes never ticked | No instruction anywhere made the PATCH-vs-comment distinction explicit; session treated posting a comment as "issue updated" | Added explicit paragraph to Section 14.3: comment and PATCH are two separate required steps; comment alone does not tick boxes | — |

**Notes:**
<!-- Per-entry context that doesn't fit in the table. Format: "YYYY-MM-DD: [explanation]" -->
2026-04-05: The rule said "before the task or phase is marked done" but "task" was ambiguous — fix issues were being treated as below the tier threshold. Added explicit language covering fix issues and session resumption via the Context Sync block pattern.
2026-04-05 (second entry): The distinction between a GitHub issue comment (POST to /comments) and an issue body update (PATCH to /issues/N) was never documented. Both write to the issue but only the PATCH changes checkbox state. Added an explicit paragraph so this is unambiguous. Cross-referenced in scoping-phased-delivery.md Section 8g Corrections Log.
