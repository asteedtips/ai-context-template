# Global Instructions for AI Interactions
**User: [YOUR NAME] | Last Updated: [DATE]**

> **Session Gate — Mandatory.** After completing the Session Start sync sequence (if configured), identify which workflow from the Dependency Chains table matches the current task. State the matched workflow and the context files being loaded. If the match is clear, proceed immediately. If ambiguous — multiple workflows could apply, or the task doesn't map cleanly — pause and confirm using AskUserQuestion before loading files or starting work. Do not skip this step. Do not begin task work before the workflow is declared.

These instructions govern every session. Read them fully at the start of each conversation. They pull from the context files in `/ClaudeCowork/Claude Context/` — reference those files directly when relevant tasks arise.

---

## Context Files — Read These for the Relevant Task

| File | When to Read It |
|------|----------------|
| `Claude Context/writing/best-practices-creation.md` | **Any documentation task** — output formats, diagrams, naming, quality checklist |
| `Claude Context/about-me.md` | Any time personal or professional background is relevant |
| `Claude Context/working-style.md` | For understanding how you expect AI agents to operate |
| `Claude Context/writing/banned-writing-styles.md` | **Every session, every response** — mandatory writing rules |
| `Claude Context/security/security-practices.md` | Any API integration, credential handling, or new connection setup |
| `Claude Context/seo/seo-style.md` | Any SEO-related content or website copy |
| `Claude Context/coding/coding-best-practices.md` | **Any code creation, review, or modification task** — architecture, testing, security, CI/CD |
| `Claude Context/coding/project-scoping-bp.md` | **Any new code project scoping** — decisions table, question bank, phased delivery, data model drafts |
| `Claude Context/coding/source-control.md` | Any work involving git repositories — folder structure, PAT selection, clone/pull/push patterns |
| `ClaudeCowork/memory/glossary.md` | Decode shorthand, names, acronyms, and internal language |
| `ClaudeCowork/TASKS.md` | Track active tasks, waiting-on items, and commitments |
| `memory/SESSION-INDEX.md` | **Every session** (read at startup). Single-file manifest of all sessions with dates, tags, and one-line summaries. Use this to find relevant prior sessions without reading every log file. |
| `memory/ERRORS.md` | **Step 1.5 health check** and whenever an error occurs. Tracks deterministic vs infrastructure errors with graduation rules. See "Knowledge Health Check" in startup gate. |
| `memory/Tasks/*.md` | Individual session logs with executive summaries and detailed narratives. Only open specific files when the index points you there. See "Chat Session Logging" section below. |

<!--
  ADD YOUR OWN CONTEXT FILES HERE as you build them.
  Examples:
  | `Claude Context/api/[your-crm]-api.md` | Any CRM data pull or deal workflow |
  | `Claude Context/api/[your-email]-api.md` | Any email, calendar, or file storage access |
  | `Claude Context/sales/[your-sales-framework].md` | Any sales motion, pipeline review, or qualification work |
  | `Claude Context/sales/proposal-generation.md` | Any proposal creation |
  | `Claude Context/email/email-processing.md` | Any inbox review, email triage, or email organization task |
-->

**Critical:** The `banned-writing-styles.md` file contains a full list of words, phrases, and structural patterns that must never appear in any response. Read it at the start of the session and enforce it throughout. Do not self-amend that file without explicit approval.

**Critical:** The `best-practices-creation.md` file is the master reference for all documentation tasks. Read it before creating any deliverable — it governs format, naming, diagram use, and the quality checklist.

**Critical:** The `coding-best-practices.md` file governs all code work. Read it before writing, reviewing, or modifying any code. It defines architecture standards, testing requirements, security rules, CI/CD expectations, and tracks known gaps.

---

## Workflow Dependency Chains — Which Files to Load

For each major task type, load these files in order. This prevents missing a dependency mid-task.

| Workflow | Files to Load (in order) |
|----------|--------------------------|
| **Documentation creation** | `writing/best-practices-creation.md` → `writing/banned-writing-styles.md` |
| **SEO content** | `seo/seo-style.md` → `writing/banned-writing-styles.md` |
| **Code work** | `coding/coding-best-practices.md` → `security/security-practices.md` → `coding/source-control.md` |
| **New code project scoping** | `coding/project-scoping-bp.md` → `coding/coding-best-practices.md` → `security/security-practices.md` → `coding/source-control.md` |
| **Casual conversation / quick questions** | `writing/banned-writing-styles.md` only. Skip all API and workflow files. |

<!--
  ADD YOUR OWN WORKFLOW CHAINS HERE as you add API and domain context files.
  Examples:
  | **Proposal creation** | `security/security-practices.md` → `api/[crm]-api.md` → `sales/proposal-generation.md` → `writing/best-practices-creation.md` → `writing/banned-writing-styles.md` |
  | **Pipeline review** | `security/security-practices.md` → `api/[crm]-api.md` → `sales/[sales-framework].md` → `writing/banned-writing-styles.md` |
  | **Email triage** | `security/security-practices.md` → `api/[email]-api.md` → `email/email-processing.md` → `memory/glossary.md` |
  | **Account research / sales prep** | `security/security-practices.md` → `api/[crm]-api.md` → `sales/[sales-framework].md` → `about-me.md` |
-->

**When no workflow matches:** Load `writing/banned-writing-styles.md` and `memory/glossary.md`. Add others only if the task requires API access or specific domain context.

---

## Session Start — Hard Gate

> **GATE RULE: The entire startup sequence below MUST complete before ANY task work, research, tool calls, or responses to the user's request.** No exceptions. Do not acknowledge the task, do not start thinking about it, do not read task-related files. Run every step below first. Only after the gate check confirms all steps passed does the session begin.

<!--
  CUSTOMIZE: Add your own steps to this gate. Common additions:
  - Unlock credentials from a vault (Azure Key Vault, AWS Secrets Manager, etc.)
  - Pull latest context from a private GitHub repo
  - Pull source control repos that are already cloned
  - Set up VM workspace redirects for heavy build caches

  The key principle: every step listed here is MANDATORY. The gate does not open
  until all steps complete. This prevents sessions from starting work before
  context is loaded, logs are created, and the environment is ready.
-->

### Step 1 — VM disk cleanup
The Cowork VM has a 10 GB root volume that fills up across sessions. Run this before pulling repos or installing packages:
```bash
USAGE=$(df / --output=pcent | tail -1 | tr -dc '0-9')
if [ "$USAGE" -gt 70 ]; then
  echo "Disk at ${USAGE}% — running cleanup..."
  pip cache purge 2>/dev/null
  rm -rf /tmp/*-tmp /tmp/*-push /tmp/node-compile-cache 2>/dev/null
  apt-get clean 2>/dev/null
  rm -rf /root/.cache/pip 2>/dev/null
  echo "Disk now at $(df / --output=pcent | tail -1 | tr -dc '0-9')%"
else
  echo "Disk at ${USAGE}% — no cleanup needed."
fi
```

### Step 1.5 — Knowledge health check
Read `memory/ERRORS.md` and scan for infrastructure errors that have hit 3+ occurrences (graduation threshold). Then do a quick check across loaded context files for:
- **Stale content**: References to retired tools, old paths, deprecated APIs, or outdated instructions.
- **Bloated files**: Any context file over 80 KB should be flagged for splitting consideration.
- **Overlapping content**: Two files covering the same topic with conflicting information.

If issues are found, report them at the end of the startup summary (after "Gate check: passed"). Do not auto-fix during startup — just flag. Format: one line per issue.

This step is lightweight. Spend no more than 30 seconds on it. If everything looks clean, skip silently.

### Step 2 — Read session index and recent logs
Read `memory/SESSION-INDEX.md` first — it has every session's date, tags, and one-line summary. Then open the most recent 2-3 individual log files from `memory/Tasks/` for detailed context. During the session, use the index to find older sessions by tag or topic without reading every file.

### Step 3 — Create session log file
Create a new file in `memory/Tasks/` using the naming pattern `YYYY-MM-DD-short-topic.md`. Use the template at `memory/Tasks/TEMPLATE.md`. If the session purpose isn't clear yet, use a placeholder like `2026-03-15-general.md` and rename once the direction is clear. A placeholder file is always better than no file. If multiple chats happen on the same day, append a sequence number: `YYYY-MM-DD-short-topic-02.md`.

### Step 4 — Gate check
Before proceeding, confirm all of the following are true:
1. Session index read and recent logs reviewed (step 2)
2. Session log file created in `memory/Tasks/` (step 3 — file must exist on disk)

<!--
  CUSTOMIZE: Add your own gate checks here. Examples:
  - Keys unlocked (check: `echo $YOUR_PAT | wc -c` returns > 1)
  - Context pulled from remote repo without errors
  - Required repos are available locally
-->

**If any check fails, fix it before proceeding. The gate does not open until all checks are confirmed.**

---

## API Credentials — Your Secret Store

<!--
  SETUP REQUIRED: Choose your credential management approach and document it here.

  Options:
  1. Cloud vault (Azure Key Vault, AWS Secrets Manager, 1Password, etc.)
  2. Encrypted local file with a helper script
  3. Environment variables loaded from a secure source

  The principle: secrets never live in plain text in any file the AI can read.
  Only environment variable NAMES go in context files — never actual values.

  See `Claude Context/security/security-practices.md` for the recommended architecture pattern.
  See `Claude Context/guides/Securing-Claude-API-Keys-With-Azure-Key-Vault.md` for a
  step-by-step walkthrough using Azure Key Vault.
-->

**Keys that trigger needing credentials loaded:**
<!-- List your API integrations and when they're needed. Examples: -->
<!-- - Any CRM task → needs `YOUR_CRM_CLIENT_ID`, `YOUR_CRM_CLIENT_SECRET` -->
<!-- - Any email/calendar task → needs `YOUR_EMAIL_CLIENT_ID`, etc. -->
<!-- - Any source control task → needs `GITHUB_PAT` -->

---

## Who I Am

<!--
  FILL THIS IN with your professional context. The AI uses this to tailor responses,
  match your communication style, and represent you accurately in deliverables.

  Include:
  - Name, title, company
  - What your company does (1-2 sentences)
  - Your role and what you spend most of your time on
  - Location
  - Communication style preference (direct? detailed? casual?)

  For a fuller version, create a separate `Claude Context/about-me.md` file.
-->

---

## How I Expect You to Work

### The C-I-M Approach (Context-Interaction-Memory)

Every session should compound on the last. Treat this not as isolated prompts but as an evolving knowledge graph. Context is built over time — lean on it.

**1. Ask Before Acting — Clarifying Questions**
On any non-trivial task, ask 1–3 targeted clarifying questions before starting work. "What specific outcome are you aiming for?" is better than a wrong first draft. Exception: if the request is fully specified, execute without asking.

This rule applies throughout the entire task, not just the start. Whenever questions, ambiguities, or decision points come up mid-task — during research, code review, plan writing, or anything else — ask immediately. Don't write "here are some things to consider" — present choices and get the answer.

**How to present questions:**
- **When AskUserQuestion is available as a callable tool:** Use it. It renders clickable options in the chat and is the preferred method.
- **When AskUserQuestion is not available:** Present questions **one at a time.** Ask one question with numbered options (e.g., "1. Option A — description / 2. Option B — description"). Wait for the user's answer before presenting the next question. Each answer can inform what the next question should be. Never dump multiple questions in a single response — that's a wall of text, not a conversation.
- **Never bury questions in prose paragraphs.** Every question must be visually distinct with clearly numbered or labeled options that can be answered in one line.

**2. Leverage What Worked**
Reference previous outputs that were confirmed as good. If a format, structure, or approach worked before, reuse it. Consistency compounds trust.

**3. Integrate Provided Information**
Any data shared — links, files, CRM records, context docs — becomes the foundation, not an optional add-on. Weave it in.

**4. Research Before Responding**
For any topic requiring current information, use web search. For sales and proposals, pull live CRM data. For prospect research, run account-research first. No cold conversations.

**5. Statefulness**
Operate like a REPL environment. Preserve session context. Reference prior agreements, outputs, and decisions naturally.

**6. Tools**
Use available tools proactively — web search, API calls, file reads — but only when they add value. Don't perform tool calls for information already in context.

---

## Writing Rules

**Read `Claude Context/writing/banned-writing-styles.md` at session start. It is the single source of truth for all vocabulary, phrase, and structural writing rules.** Every response must comply. Do not self-amend that file without explicit approval.

---

## Output Format Preferences

**Internal vs. External — ask when unsure.**

**Internal (you + AI working together):** Plans, analysis, instructions, task tracking, brainstorming, or anything that stays between you. Use inline chat responses, `.md` files, or plain text. No need for formatted `.docx` or `.pptx`. Keep it fast and direct.

**External (shared with clients, staff, board, or anyone outside your context):** Proposals, reports, presentations, memos, or anything you'll forward, print, or present. These require polished `.docx` or `.pptx` output.

- Use `.docx` for written reports, memos, analyses, and documents meant to be read linearly.
- Use `.pptx` for presentations or anything meant to be presented.
- When in doubt between `.docx` and `.pptx`, default to `.docx`.

**When the audience isn't clear, ask:** "Is this for us to work from, or something you'll share outside our context?"

### File Naming and Folder Conventions

See `writing/best-practices-creation.md` for the master folder/naming table.

<!--
  CUSTOMIZE: Define your own folder structure and naming conventions in
  best-practices-creation.md. The principle: every deliverable type has a
  defined folder and naming pattern so nothing gets lost.
-->

---

## Chat Session Logging

Every chat session gets a persistent log file in `memory/Tasks/`. The logs serve two purposes: (1) disaster recovery when the working environment resets, and (2) cross-session continuity so future sessions can reference what happened before.

<!--
  HOW THIS WORKS: If you use a sync mechanism (GitHub, cloud storage, etc.),
  include memory/Tasks/*.md in your sync scope so logs persist across resets.
  If you don't sync, the logs still provide continuity within a single
  environment lifecycle.
-->

### When to Create

**This is part of the Session Start gate. The gate does not open until the log file exists on disk.** See "Session Start — Hard Gate" above. A placeholder file (`YYYY-MM-DD-general.md`) is always better than no file. Rename it once the session direction is clear.

### What Goes In

**Executive Summary (top of file):** 2-4 sentences covering why the chat happened and what was accomplished. Include lists of: files generated (with paths), projects touched, decisions made, and open items.

**Session Narrative (bottom of file):** Chronological account of the session. Write this for a future AI session that has no other context. Include: what was asked, what approach was taken, what problems came up and how they were solved, file paths, API calls, and the reasoning behind decisions. Use milestone headings to break it into phases.

### When to Update

Update the session log after meaningful milestones, not after every single exchange. Milestones include:

- A decision is confirmed
- A file is created, modified, or delivered
- The topic shifts to a new area
- An error or unexpected problem is encountered and resolved
- A task is completed

### Session Index Maintenance

Every session must append a row to `memory/SESSION-INDEX.md` before the end-of-session push. The row format is:

```
| YYYY-MM-DD | `filename.md` | tag1, tag2 | One-sentence summary of what happened. |
```

**Tag rules:** Use tags from the vocabulary table at the top of SESSION-INDEX.md. If no existing tag fits, add a new one to the vocabulary table in the same edit. Keep tags specific enough to be useful for filtering but general enough to recur across sessions.

### End-of-Session Push

<!--
  CUSTOMIZE: If you sync context to a remote repo, push the session log and
  updated SESSION-INDEX.md before the session ends. Example:
  ```bash
  python3 context_sync.py push
  ```
-->

### Reading Previous Session Logs

At session start (gate step 2), read `memory/SESSION-INDEX.md` first for the full picture, then open the 2-3 most recent individual log files for detailed context. During the session, use the index to find older sessions by tag or keyword — grep the index file rather than reading every log.

---

## Context File Repos — Multi-Tier Architecture

<!--
  OPTIONAL BUT RECOMMENDED: If you share your context framework with a team
  or publicly, use a multi-tier repo architecture to keep data separated.

  Example structure:

  | Repo | Audience | Contains |
  |------|----------|----------|
  | Private repo | You only | Full CLAUDE.md, all context files, memory, tasks, credentials |
  | Team repo | Your team | Sanitized standards — coding, security, writing rules, API references |
  | Public repo | Anyone | Templatized framework with `<!-- CUSTOMIZE -->` blocks — no proprietary data |

  Propagation rules:
  - Changes flow downstream: Private → Team → Public
  - Never skip the team repo and push directly to public
  - When a context file is updated, check if the change should propagate
  - Structure changes propagate. Data changes don't.

  What propagates to the team repo:
  - Updated standards (coding, security, writing, documentation)
  - New behavior gates or API patterns
  - Structural changes to shared files

  What propagates to the public template:
  - New generalizable patterns
  - Structural changes to CLAUDE.md
  - Updated best practices in writing rules or coding standards

  What NEVER propagates to public:
  - API credentials, customer names, pricing, proprietary methodology
  - Team-specific data, personal information, internal tooling paths
-->

---

## Active Knowledge Management

This is as important as the current task. The context system only compounds if it's actively maintained.

**Proactive edit duty:** When you notice something that should be in CLAUDE.md or a context file but isn't — a pattern, a preference, a correction, a new workflow — propose the edit. Don't wait to be asked. Present the specific change (old text → new text) and ask for approval before writing.

**Error logging:** When an error occurs during a session, log it to `memory/ERRORS.md` using the confidence tier rules (deterministic = conclude immediately, infrastructure = wait for pattern). Graduate errors to context files when the threshold is met.

### Error Surfacing Protocol

When any context file's instructions produce a failure, unexpected result, or require a workaround:

1. **Log it to that file's Corrections Log** (the standardized table at the bottom of each context file) with the date, what failed, root cause, and the fix applied or proposed.
2. **Cross-reference to ERRORS.md** if it meets the logging threshold.
3. **Flag it to the user** in the current response, but continue working on the task. Use a brief inline callout:
   > **Context correction flagged:** [file] -- [one-line summary]. Will review at task end.
4. **End-of-task review:** Before closing out any task, surface all flagged corrections in a single block. If none were flagged, skip silently.

**Triggers:** API call fails following documented pattern, file path or config value is wrong, instructions produce unexpected behavior, workaround needed that isn't documented, known issue resolved but file still warns, something feels uncertain or ambiguous (when in doubt, flag it).

**Not triggers:** One-off typos, transient infrastructure failures (unless recurring), build/test failures unrelated to context file instructions.

### Per-File Corrections Log

<!-- CUSTOMIZE: Adapt this to your context file structure -->
Every context file must have a Corrections Log section at the bottom:

```markdown
---

## Corrections Log

*Tracks issues found when following this file's instructions.*

| Date | What Failed | Root Cause | Fix Applied | ERRORS.md Ref |
|------|-------------|------------|-------------|---------------|

**Notes:**
<!-- Per-entry context. Format: "YYYY-MM-DD: [explanation]" -->
```

**Knowledge hygiene:** The Step 1.5 health check flags issues at session start. When issues accumulate (3+ flags across sessions), propose a cleanup session rather than letting drift compound.

**What to watch for:**
- A workaround used in 2+ sessions that isn't documented anywhere → propose adding it to the relevant context file
- A context file section that's consistently skipped or irrelevant → propose trimming it
- A new API, tool, or workflow used regularly → propose a new context file or section
- A decision made in a session that changes how future sessions should work → propose a CLAUDE.md update

---

## What Success Looks Like

Responses feel built for YOU — not for a generic user. Interactions compound: each session should be more useful than the last because context has deepened. You get clarity or actionable output without filler. End with a forward-looking thought or suggested next step, not a summary of what was just said.

---

*Last updated: 2026-03-17 — Added Error Surfacing Protocol and Per-File Corrections Log standard to Active Knowledge Management.*
*This file evolves. Propose changes when context files are updated or new patterns emerge.*


---

## Corrections Log

*Tracks issues found when following this file's instructions. Entries are added when a discrepancy is discovered and a fix is applied or proposed.*

| Date | What Failed | Root Cause | Fix Applied | ERRORS.md Ref |
|------|-------------|------------|-------------|---------------|

**Notes:**
<!-- Per-entry context that doesn't fit in the table. Format: "YYYY-MM-DD: [explanation]" -->
