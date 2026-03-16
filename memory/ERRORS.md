# Error Knowledge Log
*Tracks errors encountered across sessions with confidence-based learning rules.*

---

## How This File Works

Not every error is a lesson. This log distinguishes between errors that teach something immediately and errors that need a pattern before drawing conclusions.

### Confidence Tiers

| Tier | Examples | Rule |
|------|----------|------|
| **Deterministic** | Bad schema, wrong type, missing field, invalid API scope, incorrect endpoint, auth misconfiguration | Conclude immediately. One occurrence is enough — the fix is knowable from the error alone. Graduate to the relevant context file after resolution. |
| **Infrastructure** | Timeout, rate limit, network failure, VM disk full, transient 5xx | Log, but draw no conclusion until a pattern emerges. Three occurrences of the same root cause across different sessions = graduate to context file. |
| **Environmental** | VM constraint, SDK not installed, package version mismatch, session path stale | Log with the session context. If it recurs after a workaround was documented, escalate the workaround to a permanent fix in the relevant context file. |

### Graduation Rules

When an error graduates from this log into a context file:

1. Add the lesson to the appropriate context file.
2. Mark the error row below as **Graduated** with a pointer to where it went.
3. Do not delete graduated rows — they serve as an audit trail.

### What Does NOT Go Here

- One-off typos or copy-paste mistakes (fix and move on).
- Errors that are already documented in a context file's "Known Issues" or "Pitfalls" section.
- Build/test failures that belong in the session log narrative.

---

## Active Error Log

| Date | Tier | Error Summary | Root Cause | Session Log | Status |
|------|------|---------------|------------|-------------|--------|
| | | | | | |

---

## Graduated Errors (Archive)

*Errors that have been resolved and their lessons incorporated into context files.*

| Date | Error Summary | Graduated To | Resolution |
|------|---------------|-------------|------------|
| | | | |

---

*Review this file at session start. Add new errors as they occur. Graduate when patterns confirm.*
