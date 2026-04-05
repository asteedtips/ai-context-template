# Verification Agent Protocol

> **Part of the Coding Standards Graph.** This file covers the verification agent system for automated code review. For the full standards index, see `coding-index.md`.

When implementing code features, you can spin up independent sub-agents to review the work before marking it complete. This catches categories of issues that would otherwise surface in code review: architecture violations, missing documentation, pattern noncompliance, and UI conformance gaps.

## 14.1 Complexity Tiers

| Tier | Scope | Verification Needed |
|------|-------|---------------------|
| **Tier 1: Small** | Single file, <50 lines changed, no UI | No agent review. Review is built into the primary implementation pass. |
| **Tier 2: Medium** | Multiple files, new services, or any UI work | One code review agent after implementation is complete. |
| **Tier 3: Large** | New feature, multi-phase, external APIs, database schema changes | Two agents in parallel after each phase. |

**How to determine tier:** Use the phase plan or estimate scope by file count and change size. When in doubt, round up. A Tier 2 review on a borderline-Tier-1 change takes minimal time; missing a real issue is expensive.

## 14.2 What Each Agent Checks

**Code Review Agent (Tier 2 and Tier 3):**

Reviews the implementation against the coding standards. Checks:

- Layer reference direction: no upward references
- Dependency injection pattern: centralized registration, constructor injection
- Configuration pattern: consistency with your config standards
- DbContext lifecycle: proper factory usage, not direct injection
- Service return types: consistent result wrapper pattern
- Async/await patterns: CancellationToken usage, no `.Result` or `.Wait()`
- Explicit typing and code style: vars vs explicit, braces on control flow
- Documentation: XML docs on public methods, comments on complex logic
- TODO/HACK comments have tracked work items
- No PII in logging
- Read-only queries use appropriate flags
- Exception handling: no silent swallowing

The agent produces a pass/fail list. Failures block the task from being marked done.

**UI Conformance Agent (Tier 2 with UI, Tier 3 with UI):**

Only runs when changes involve UI components and approved mockups exist. Executes the Extract-Build-Verify gate from `coding-blazor-ui.md`:

- Walks the component spec checklist against the implemented markup
- Marks each item ✅ or ❌
- Checks any new routable pages against the checklist requirements

Any ❌ item blocks the task from being marked done.

**External API Agent (Tier 3 only, when applicable):**

Only runs when changes touch external APIs or integrations. Checks:

- Dry Run / test mode support if production sandbox doesn't exist
- Retry policies and resilience patterns
- No hardcoded credentials in code
- Error handling: failures surface via result pattern, not silently swallowed
- Request payload verification: correct parameters sent to external APIs

## 14.3 When Agents Run

Agents run **after implementation is complete but before marking the phase or task done.** They complement CI; they don't replace it.

**Sequence:**
1. Implement the code
2. Run verification agent(s) based on tier
3. Fix any failures surfaced by agents
4. Push to your feature branch (triggers CI)
5. CI validates compilation and tests
6. Mark phase/task done only after both agent review and CI pass

## 14.4 Agent Output and Fixes

Agents produce a structured report of pass/fail items. For any failures:

1. Read the agent's reasoning for why something failed
2. Fix the issue in the code
3. Re-run the agent to confirm the fix
4. If failures remain, create a separate work item to address them and document why in the phase plan

---

## Corrections Log

*Tracks issues found when following this file's instructions.*

| Date | What Failed | Root Cause | Fix Applied |
|------|-------------|------------|-------------|

