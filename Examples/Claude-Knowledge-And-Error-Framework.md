# Claude Knowledge and Error Framework
**A System for Persistent Memory, Error Learning, and Self-Correcting Context**

*How to build a knowledge system where Claude gets better at your workflows over time, catches its own mistakes, and tells you about them before they compound.*

---

## Why This Exists

Claude doesn't remember anything between sessions by default. Every conversation starts cold. If you're using Claude for real work (not just one-off questions), that's a problem. You repeat yourself. Claude makes the same mistakes. Patterns that took three sessions to establish get lost when the VM resets.

This framework solves that by treating Claude's context files as a living knowledge base, not static instructions. Context files get pulled from version control at session start, updated during work, and pushed back when the session ends. Errors get classified, tracked, graduated into permanent fixes, and verified. Session logs capture what happened so the next session can pick up where the last one left off.

The result: session 50 is meaningfully better than session 1, because every mistake, preference, and decision has been encoded into the system.

---

## Architecture Overview

The system has five layers, each building on the one below it.

**Layer 1: Context Files** -- Markdown files containing instructions, API references, coding standards, writing rules, and workflow definitions. These are what Claude reads at session start to understand how you work. They live in a private GitHub repo and get synced to the working environment at every session start.

**Layer 2: Memory System** -- A glossary file for decoding shorthand, acronyms, and internal language. A task file for tracking active work. Session log files that capture what happened in each conversation. All version-controlled, all synced.

**Layer 3: Session Logging** -- Every session produces a log file with an executive summary (what happened and why) and a narrative (chronological detail written for a future Claude session that has no other context). A session index file provides a searchable manifest of all sessions with dates, tags, and one-line summaries.

**Layer 4: Error Tracking** -- A central error log (`ERRORS.md`) that classifies errors by confidence tier and root cause category. Deterministic errors graduate immediately to context files. Infrastructure errors need a pattern (three occurrences) before graduating. Every graduated fix gets verified over two clean sessions.

**Layer 5: Per-File Corrections** -- Every context file has its own Corrections Log at the bottom. When something in that file's instructions causes a failure, the fix gets logged right there, next to the instructions it corrects. This is the newest layer and the one that closes the feedback loop.

---

## The Session Lifecycle

### Startup Gate

Every session runs a mandatory startup sequence before any work begins. No exceptions. The gate doesn't open until all checks pass.

1. **Unlock credentials** -- decrypt API keys from an encrypted store (Azure Key Vault in our case, but any secrets manager works).
2. **Pull latest context** -- sync all context files from GitHub so you're working with the most current instructions.
3. **Read session index and recent logs** -- scan the session manifest to understand what happened recently, then open 2-3 recent logs for detail.
4. **Knowledge health check** -- scan `ERRORS.md` for graduated errors pending verification, failed fixes that need rework, and root cause category tallies that might indicate systemic patterns. Also scan context files for stale content, overlapping information, or files that have grown too large.
5. **Environment setup** -- disk cleanup if needed, workspace redirects for heavy caches.
6. **Pull repos** -- pull the context system repos (not all repos; others get pulled on demand).
7. **Create session log file** -- every session gets a log file before work begins. A placeholder name is always better than no file.
8. **Gate check** -- verify keys are unlocked, context is pulled, index is read, and the log file exists on disk.

The gate is binary. If any step fails, fix it before proceeding. This prevents the most common class of errors: working with stale context, missing credentials, or losing session history.

### During the Session

Work happens normally, but with two background processes running:

**Session log updates** happen at milestones (decisions confirmed, files delivered, topic shifts, errors resolved, tasks completed). Not after every exchange. The log is written for a future Claude session that has zero context about what's happening now.

**Error surfacing** runs continuously. If any context file's instructions produce a failure, require a workaround, or even feel uncertain, Claude flags it inline and keeps working. The flags accumulate and get reviewed as a batch at the end of the task. More on this below.

### Session Close

Before ending: update the session log with final outcomes, append a row to the session index, and push everything to GitHub. The push includes context files (if any were modified), memory files, and the session log.

---

## The Error System

This is the part most people find interesting, because it's the mechanism that makes the whole system self-improving rather than just persistent.

### Three Confidence Tiers

Not every error teaches a lesson. The system distinguishes between errors you can learn from immediately and errors that need a pattern before drawing conclusions.

**Deterministic errors** are wrong on first occurrence. A bad API schema, a wrong endpoint, a missing required field, an incorrect auth scope. One occurrence is enough. Log it, fix it, graduate the fix into the relevant context file immediately.

**Infrastructure errors** are often transient. Timeouts, rate limits, network failures, disk full conditions. Logging these is fine, but drawing conclusions from a single occurrence is premature. The threshold is three occurrences of the same root cause across different sessions before graduating to a context file.

**Environmental errors** are specific to the runtime. SDK version mismatches, VM constraints, stale session paths. Log these with their session context. If the error recurs after a workaround was already documented, that's a signal to escalate the workaround into a permanent fix.

### Five Root Cause Categories

Every error gets tagged with one category. This is what lets you spot systemic patterns rather than treating every error as a one-off.

**API Contract** -- wrong endpoint, missing scope, bad schema, auth misconfiguration, token refresh failure. These usually mean a context file has incorrect or incomplete API documentation.

**VM Constraint** -- mounted volume limitations, disk space, session path changes, missing tools. These are environment-specific and the fixes tend to be workarounds rather than root-cause fixes.

**Stale Reference** -- hardcoded paths, retired repos, deprecated patterns, outdated config values. These accumulate over time as the system evolves and old instructions don't get updated.

**Missing Gate** -- no validation step existed to catch this before it caused a failure. These are the most interesting category because they represent holes in the process, not mistakes in the instructions. Fixing them means adding a check that didn't exist before.

**Config Drift** -- environment-specific configuration that wasn't documented or diverged between environments. Common when you're working across multiple machines, accounts, or deployment targets.

### The Graduation Pipeline

Errors move through a lifecycle: Active, Graduated, Verified (or Failed Fix).

**Active** -- the error is logged in `ERRORS.md` with its date, tier, category, root cause, and a pointer to the session log where it happened.

**Graduated** -- the fix has been written into the relevant context file. The error row moves to the archive section with a "Verified" status set to Pending (0/2).

**Verified** -- two clean sessions that touch the same area have passed without the error recurring. At this point, the fix is confirmed. The entry stays in the archive for audit trail.

**Failed Fix** -- the error recurred before verification completed. The context file edit gets reworked with a different approach, and a new active error row is created referencing the failed attempt. Failed fixes get top priority at the next session's health check, because a fix that doesn't hold is worse than no fix. It creates false confidence.

### Per-File Corrections Logs

The newest addition. Every context file now has a standardized footer:

```markdown
---

## Corrections Log

*Tracks issues found when following this file's instructions.*

| Date | What Failed | Root Cause | Fix Applied | ERRORS.md Ref |
|------|-------------|------------|-------------|---------------|

**Notes:**
<!-- Per-entry context. Format: "YYYY-MM-DD: [explanation]" -->
```

This serves a different purpose than `ERRORS.md`. The central log tracks the error lifecycle (active, graduated, verified). The per-file log puts the fix next to the instructions it corrects, so anyone reading that file sees the gotchas inline. The `ERRORS.md Ref` column cross-links the two systems.

When an entry is resolved and verified, it moves to a "Resolved" sub-table rather than getting deleted. The audit trail stays visible in the file where the problem lived.

---

## Error Surfacing Protocol

This is the behavioral rule that makes the error system proactive rather than passive. Without it, Claude might hit a problem, work around it silently, and you'd never know.

The protocol has four steps:

**1. Log it.** When any context file's instructions produce a failure, unexpected result, or require a workaround, log it to that file's Corrections Log immediately. Include the date, what failed, root cause, and the fix applied or proposed.

**2. Cross-reference.** If the error meets the logging threshold (not a one-off typo), add it to `ERRORS.md` with its confidence tier and root cause category.

**3. Flag it.** Tell the user in the current response, but keep working on the task. Use a brief inline callout:

> **Context correction flagged:** `zoho-api.md` -- API endpoint for bulk read returns 404, switched to single-record GET. Will review at task end.

**4. End-of-task review.** Before closing out any task, surface all flagged corrections in a single block. For each one: the file affected, what went wrong, what was done about it, and whether it needs approval to commit. If nothing was flagged, skip this step silently.

### What Triggers the Protocol

The trigger list is intentionally broad. It covers not just failures, but uncertainty:

- An API call fails when following a context file's documented pattern
- A file path, repo name, or config value in a context file is wrong
- Instructions produce an error or unexpected behavior
- A workaround is needed that isn't documented
- A documented "known issue" has been resolved but the file still warns about it
- Something feels uncertain or ambiguous in a context file's instructions, even if it hasn't caused a failure yet

That last trigger is the one that catches the most drift. Claude doesn't have to wait for something to break. If a set of instructions feels like it might be outdated or incomplete, flagging it is the right call.

### What Does NOT Trigger the Protocol

- One-off typos or copy-paste mistakes (fix and move on)
- Transient infrastructure failures (network, rate limits) unless they recur
- Build/test failures unrelated to context file instructions

---

## Session Logging in Practice

### The Session Log File

Each session produces a markdown file in `memory/Tasks/` with the naming pattern `YYYY-MM-DD-short-topic.md`. The file has two sections:

**Executive Summary** (top): 2-4 sentences covering the purpose and outcome. Lists of files generated (with paths), projects touched, decisions made, and open items. This is what a future session reads first to decide whether the full log is relevant.

**Session Narrative** (bottom): A chronological walkthrough broken into milestone headings. Written for a future Claude session that has no other context. Includes what was asked for, what approach was taken, what problems came up and how they were solved, file paths, API calls, and the reasoning behind decisions.

### The Session Index

`SESSION-INDEX.md` is a flat table with one row per session:

```markdown
| Date | File | Tags | Summary |
|------|------|------|---------|
| 2026-03-17 | `error-handling-architecture.md` | context-framework, knowledge-mgmt | Added Error Surfacing Protocol and Per-File Corrections Log to all context files. |
```

A tag vocabulary table at the top defines all valid tags. Tags are lowercase and hyphenated. New tags get added to the vocabulary when no existing tag fits.

This index is the first thing read at session start. It provides the full picture without opening individual log files. During a session, you can grep the index to find older sessions by tag or topic rather than reading every log sequentially.

### Update Frequency

Session logs update at milestones, not after every exchange. Milestones include: decisions confirmed, files created or delivered, topic shifts, errors encountered and resolved, tasks completed.

---

## The Knowledge Health Check

At session start (after reading the session index and recent logs), a quick health check scans for accumulating problems:

**Error patterns** -- Are any root cause categories accumulating 3+ entries? That might mean a systemic issue that needs an architectural fix rather than one-off workarounds.

**Failed fixes** -- Are there graduated errors that failed verification? These are top priority.

**Stale content** -- Do any context files reference retired repos, old paths, deprecated APIs, or tools that have been replaced?

**File bloat** -- Is any context file over 80 KB? Large files should be considered for splitting.

**Overlapping content** -- Are two files covering the same topic with conflicting information?

This check is lightweight. If everything is clean, move on silently. If issues are found, flag them at the end of the startup summary. Don't auto-fix during startup; just surface the problems for review.

---

## Multi-Repo Propagation

If you're distributing context to a team or maintaining a public template, changes need to flow downstream deliberately.

The architecture uses three tiers:

**Private** -- your full working context. Everything lives here. Personal preferences, API credentials, proprietary data, all context files.

**Team** -- a sanitized copy for your organization. Stripped of personal preferences, credential paths, and point-in-time audit findings. Contains coding standards, API references (with behavior gates, not credentials), security practices, and writing rules.

**Public** -- a templatized copy for anyone to adopt. Stripped of all organization-specific data. Uses `<!-- CUSTOMIZE -->` blocks and `[PLACEHOLDER]` values where private data would go.

A single checklist runs whenever a context file is modified. It checks which downstream repos contain copies of that file, determines if the change should propagate, and presents all targets for approval in one prompt. Changes always propagate in order: Private first, then Team, then Public. The team copy should always be equal to or ahead of the public template.

---

## What This Looks Like After 80+ Sessions

Some real numbers from our implementation:

- 22 context files, each with a Corrections Log footer
- 80+ session logs in the index, tagged and searchable
- 7 graduated errors in the archive (5 verified, 2 pending verification)
- 1 active error (persistent workaround for a VM constraint)
- 5 root cause categories tracked, with "Missing Gate" as the largest (indicating process gaps rather than instruction errors)
- 3 repos kept in sync (private, team of 6, public template)

The error that taught us the most: "Missing Gate" errors accounted for 5 of 7 graduated entries. These weren't cases where instructions were wrong. They were cases where no instruction existed at all. The system didn't have a check for PAT auth format, static field contamination between tests, or method signature verification before pushing. Each one now has a gate that prevents the error from recurring.

---

## Getting Started

If you want to implement this in your own Claude workflow, the minimum viable version needs four things:

1. **A CLAUDE.md file** with a startup gate that pulls context, reads recent history, and creates a session log before work begins.

2. **A memory folder** with `SESSION-INDEX.md` (searchable manifest), `ERRORS.md` (error tracking with confidence tiers), `glossary.md` (shorthand decoder), and a `Tasks/` subfolder for session logs.

3. **A sync mechanism** to persist changes across sessions. We use a GitHub repo with a Python sync script. The tool doesn't matter; the persistence does.

4. **A Corrections Log footer** on every context file, so errors get tracked where they happen.

The Error Surfacing Protocol (flag-and-continue with end-of-task review) is optional but recommended. Without it, you're relying on yourself to notice when Claude hits a problem and works around it quietly. The protocol makes the system self-reporting.

A public template with the full structure (minus any proprietary content) is available at [github.com/asteedtips/ai-context-template](https://github.com/asteedtips/ai-context-template).

---

*Built by Albert Steed (True IP Solutions, Wilmington NC) across 80+ Claude sessions, March 2026.*
*This document was written in a session that used the system it describes: logged, indexed, error-checked, and pushed to version control for future sessions to reference.*
