---
type: context-file
parent: "[[coding-index]]"
summary: "Agent-driven browser smoke testing: workflow_dispatch of the repo's own dev CD workflow on a feature branch, dedicated smoke logins per platform in a secrets vault, and a browser verification pass whose output is screenshots plus console and network capture rather than a self-reported PASS row."
tags: [coding, smoke-testing, verification, ci-cd, browser]
---

# Agent-Driven Browser Smoke Testing

> **Part of the Coding Standards Graph.** This file covers the browser verification pass that runs against a real deployed build. For the checklist that defines what gets tested, see `scoping-phased-delivery.md` Section 8h. For the code-reading verification agents, see `coding-verification.md`. For workflow mechanics, see `github-actions-bp.md`. For credential storage, see `security-practices.md`.

## 1. Why this exists

Every other piece of verification evidence in a normal process is produced by something that has never looked at the rendered page. Unit tests assert against objects. Integration tests assert against APIs. A conformance agent reads markup. None of them can see a component that renders and silently writes nowhere, a page that throws in the console while looking correct, or a form that posts and gets a 500 back.

<!-- CUSTOMIZE: replace with your own two incidents. The pattern that makes this section work is one failure where a person was the QA function and burned days on round trips, and one failure where an agent read the source, concluded it matched the spec, and was wrong. Those two together are the argument for a pass that looks at the rendered page. -->

**[INCIDENT 1: the human-as-QA cycle.]** [How many issues, over what period, and the shape of the round trip: someone opened the app, found it broken, reported back, waited for a fix.]

**[INCIDENT 2: the false PASS.]** [A conformance or review artifact reporting PASS on items where the implementation did not match the spec, and the fact that an agent had read the source and concluded it matched.]

A browser pass driven by an agent closes that gap and moves the first round of discovery off a person.

## 2. What this is not

This does not replace the `coding-verification.md` agents. Those read source and check pattern compliance, and they catch a different class of problem. It does not replace unit or integration tests. And on the largest changes it does not replace the human browser pass, it shortens it.

## 3. Gate role by tier

Tiers are defined in `coding-verification.md` Section 14.1.

| Tier | Agent smoke pass | `needs: smoke-test` | Human browser pass |
|---|---|---|---|
| **Tier 1** | Required. Closes the smoke gate. | Not applied. | Glance at the artifact only. |
| **Tier 2** | Required. Closes the smoke gate. Runs alongside the UI conformance and analyzer requirements in 14.1. | Not applied. | Glance at the artifact only. |
| **Tier 3** | Required, looped to clean, and the artifact posts to the issue **before the PR opens**, same rule as the parallel review agents. | Applied and stays on. | Full pass on the build left running on dev, on a shorter list. |

Apply the `agent-smoked` label when the agent artifact is posted. On Tier 1 and Tier 2 the issue can close after that label lands and the reviewer has looked. On Tier 3 the issue stays open until `needs: smoke-test` comes off.

**The agent pass is a prerequisite in every tier.** It is never skipped for schedule reasons, and a clean run is never assumed from a prior session. If the artifact is not on the issue, the pass did not happen.

## 4. Preconditions

### 4.1 The build under test is actually on dev

The dispatch workflow records the deployed ref. Read it back rather than trusting that the dispatch succeeded. A smoke run against the previous build is worse than no smoke run, because it produces a passing artifact for code that was never exercised.

### 4.2 Dev schema matches the branch under test

Two shapes exist and you have to know which one your repo is.

**If the dev CD pipeline publishes database schema itself** (a schema build job plus a publish job that gates the app deploy through `needs:`), the dispatch brings the schema with it and no manual publish is required. The precondition then inverts rather than disappearing:

1. **Assert the new object exists on dev after the dispatch, not before it.** Query it and record the assertion as row zero of the smoke artifact.
2. **Restoring does not reliably undo a schema change.** Redeploying the integration branch republishes that branch's schema, but a destructive change may not round-trip and a newly added table will not necessarily be dropped. If a wave added or dropped schema objects and then got abandoned, check dev schema state rather than assuming the restore cleaned up.

**If it does not**, dev SQL stays behind the source on any branch that touched a schema project, and you must publish manually before the dispatch, then assert the object exists. A branch whose code references a column that exists only in source and not on the dev database will dead-end the smoke.

Read the dev CD workflow's job list to find out which shape you have. Do not assume.

### 4.3 Nobody else is holding dev

Read the `dev` deployment environment's history before dispatching. If the most recent deploy names a ref that is neither yours nor the integration branch, another change is holding dev and waiting on review; ask before deploying over it.

## 5. Deploy: putting the branch on dev and holding it there

### 5.1 Why not deployment slots

Slots are the obvious design and they usually do not work. Two reasons.

A **per-branch** slot gets a new hostname on every run, and a new hostname is in no identity-provider reply-URL allow-list, no third-party OAuth callback config, no CORS list, and no inbound webhook target. Making it work would mean writing a reply URL into a shared identity resource on every smoke run and removing it after, with a cleanup step that will eventually be missed.

A **single permanent** slot solves that, and then runs into hosting tier. On most managed app platforms, slots require a mid or premium tier and the entry tiers support zero. Check the tier on every dev plan before designing around slots, and price the upgrade against a benefit that deploy-and-hold already delivers.

<!-- CUSTOMIZE: record your own tier and pricing finding here once you have measured it, so the next person to reach for slots finds the measurement instead of repeating it. -->

### 5.2 The hold, and why dev stays on the feature build

**Dev keeps the feature build until the PR merges. Restoring is not a routine step.**

The point of putting a change on dev is that a person tests it there. Rolling dev back the moment the agent pass goes green would throw away the exact build the reviewer is about to open. So the lifecycle is:

1. Deploy the feature branch to dev.
2. Agent runs the smoke checklist. On any FAIL, fix, redeploy, and re-run the **whole** checklist. Loop until clean.
3. Post the evidence artifact, apply `agent-smoked`, and **leave the build on dev**.
4. The reviewer tests on dev, against a build that has already had the obvious breakage found and fixed.
5. PR to the integration branch. The merge deploys that branch, and dev returns to normal on its own.

Dev is therefore occupied for as long as the change is open, which can be hours or days. Two consequences follow.

**A second change cannot smoke while the first holds dev.** This is the real cost of the model and it is worth stating plainly rather than discovering. On a one-at-a-time cadence it costs nothing. Running two in parallel needs a conversation about sequencing before either one deploys.

**Never run a scheduled restore.** A nightly job that clears stale holds and redeploys the integration branch will eventually destroy a build waiting for human review, which is the normal state under this lifecycle. Do not build one, and remove it from any repo that has one.

### 5.2.1 Making the hold visible

**The `dev` deployment environment's history is the source of truth.** It records the ref of the most recent deploy, so "which branch is dev running" is always answerable natively, with no lock variable and no extra token.

A repository variable holding the current holder was considered as a second signal that could refuse a foreign dispatch outright. It is not recommended: deployment history answers the question it would be invented for, and the variable costs a token with `variables` write to maintain.

### 5.2.2 When a restore does happen

Restoring is an exception path, not a closing step. Three cases:

1. **The change is abandoned or deprioritized.** Redeploy the integration branch so dev stops advertising work nobody is finishing.
2. **The hold has gone stale.** A feature build nobody has tested in days is holding a shared resource. Ask before clearing it.
3. **Something else needs dev more.** A sequencing decision, and a person's to make.

Restore by dispatching the same dev CD workflow on the integration branch, the same path a merge takes.

### 5.3 Deploy: dispatch the repo's own dev CD workflow

**Do not build a separate smoke workflow. Dispatch the dev CD workflow the repo already has.**

This is the single most important rule in the file, and it is here because the opposite was tried first. An earlier version of this standard specified a `smoke-deploy.yml`, a `smoke-restore.yml`, a dedicated deployment environment, a hold variable, and a dispatch token. None of it was ever built, because the capability already existed: every dev CD workflow already carried a `workflow_dispatch` trigger and no environment protection blocking a feature-branch ref. What the specification actually produced was a series of sessions opening `.github/workflows/`, looking for a file that did not exist, and stalling.

**Reusing the real deploy job is stronger than a copy of it, not weaker.** A separate smoke workflow has to duplicate the build and publish path, and a duplicated path drifts, which means a smoke that passes on a build the real pipeline would never produce. Dispatching the real workflow removes that failure mode by construction.

**Before assuming a repo can do this, check four things.** On GitHub, `GET /repos/{owner}/{repo}/environments/dev` answers the last two.

1. The dev CD workflow carries a `workflow_dispatch` trigger. Adding one is a one-line change, not a new workflow.
2. No job in it carries a branch `if:` guard that would skip on a feature branch.
3. The `dev` deployment environment has no protection rules.
4. It has no deployment branch policy, which would otherwise refuse a dispatch from a feature ref.

**Also check the blast radius.** Where the deploy targets are hardcoded dev resource names, a stray dispatch physically cannot reach a higher environment. Where an environment variable picks the target instead, a branch guard against the production refs is the only thing keeping a dispatch off prod. Prefer hardcoded targets on any new pipeline.

### 5.3.1 Deploy and merge authority

**The agent runs both the dev deploy and the PR merge without waiting on a person.** State this explicitly in your own rules, because a session that treats either as needing sign-off cannot reach the browser pass on its own, which defeats the point of the pass.

The sequence the agent owns end to end:

1. Dispatch the dev CD workflow on the feature branch.
2. Poll the run to completion and confirm every deploy job succeeded. A dispatch that was accepted is not a deploy that landed.
3. Read the deployed ref back, per 4.1.
4. Run the browser pass, and loop through 7.2.1 on any FAIL.
5. Post the artifact and apply `agent-smoked`.
6. Open the PR, confirm CI green on the merge commit, and **merge it.**

What still stops and asks: a fix that needs a scope decision, a failure in a shared component or someone else's code, a schema change that a restore would not undo cleanly, something else already holding dev, and anything the 7.2.1 stop list covers. Merge authority is authority over the mechanics, not over scope.

<!-- CUSTOMIZE: if your agent runs in a sandbox without direct network access to your git host, name the tool that does have it here and require every dispatch, poll, PR create, and merge to route through it. See source-control.md. -->

## 6. Credentials

### 6.1 Accounts

Two dedicated accounts per platform: one normal user and one super user. The smoke accounts are the default, and the only permitted login except under the documented exception in 6.5.

Give each account a name that makes the data it creates identifiable, so a smoke run's leftovers can be found and cleared. `smoke.user@` and `smoke.admin@` on the local domain, or a `[SMOKE]` display-name prefix where the identity system does not allow a custom address.

### 6.2 Vault entries

Stored in your secrets vault, tagged so a standard credential unlock surfaces them without an elevated call. Four secrets per platform, following the naming convention in `security-practices.md`:

```
{platform}-dev-smoke-user-username
{platform}-dev-smoke-user-password
{platform}-dev-smoke-admin-username
{platform}-dev-smoke-admin-password
```

If a smoke secret goes missing, query the vault's soft-delete endpoint and its purge date before concluding it was never created. A missing vault secret is three states, not one.

### 6.3 Non-negotiable rules

1. **Dev only.** No production login is stored under a smoke name in any vault, on any platform, for any reason. Browser automation plus a production credential is one bad instruction away from live customer data.
2. **The password is read from the unlocked keys file and typed into the dev login form.** It is not pasted into chat and not committed anywhere.
3. **Rotate on any use outside a smoke run.** If a person signs in with a smoke account to debug something, the password changes afterward.
4. **The vault entry describes what the credential actually authenticates against**, not what its name implies. See 6.4.

### 6.4 Check what the dev environment actually authenticates against

A "dev" login is only a dev credential if the dev environment's identity configuration points somewhere dev. Environment override settings, JWT authority values, and OAuth client configuration are all capable of repointing a dev app's login path at a production identity provider while the rest of the app still reads dev data.

**Before provisioning smoke credentials on any platform, confirm where its login path resolves.** Read the live configuration rather than the setting name. Where a dev login authenticates against production, say so in the vault entry's description, and provision the normal user only. A production-authenticating super-user credential inside an automated browser loop is a different risk class and rarely urgent enough to accept.

### 6.5 Exception: a maintainer's own dev session, when they confirm it

On a platform where the maintainer approves it, the browser pass may run through that person's own signed-in dev session rather than a smoke account, when they confirm it in the session. Smoke accounts stay the preferred path and the standing default; this is an exception with a reason, not a relaxation.

Why it exists. A browser with a persistent profile frequently already holds a maintainer's dev login. It also covers checklist rows a smoke account cannot close: a row needing a real provisioned resource that only a real account owns, for instance.

The rules that hold anyway:

1. **They confirm in the session, every session.** A profile that happens to be logged in is not consent. Ask, and record the answer in the artifact's Account row rather than naming a vault secret that was not used.
2. **Dev only, and it stays dev only.** The exception never extends to a production hostname, for any reason, under any framing.
3. **Only where the maintainer has approved it.** Where smoke accounts are provisioned and working, there is no reason to reach for a person's login.
4. **Never sign them out and never change their credentials.**
5. **Say in the artifact which rows used which login.** Two rows closed under different identities are different evidence and the artifact should not blur them.

## 7. The browser pass

### 7.1 Tools

Browser automation tooling changes faster than this standard does, so treat the specific tool names as the customizable part and the requirements as the fixed part.

**What the pass requires from whatever browser tooling you use:**

- Navigate to a URL and read the rendered page as text or as an accessibility tree, not only as pixels.
- Locate elements by a stable handle and click, type into, and set form values on them.
- Take screenshots of a region.
- **Read console messages and network requests per action.** This is not optional. Section 7.3 explains why, and a tool that cannot do it cannot run this pass.

<!-- CUSTOMIZE: name your default browser tool and your fallback, and say which one wins when both are available. Where more than one exists (for example, an in-application browser pane with its own persistent profile, and an extension driving the user's real browser), state the default explicitly rather than leaving each session to choose. A pane with its own profile is usually the better default: it is isolated from the person's own browsing, and its persistence means a prior session's dev login is often still live. -->

**Whatever the tooling, it runs where the browser runs, not where your shell runs.** It generally cannot open a `localhost` server your agent's sandbox started, or a `file://` path on that sandbox. That is a second reason the pass has to go through a real dev deploy rather than a local run.

### 7.1.1 Driving a server-rendered interactive page without producing false evidence

These traps are specific to frameworks that keep UI state on the server over a persistent connection (Blazor Server, LiveView, Livewire, and similar). Each one manufactures a plausible-looking wrong answer, which is precisely what the artifact format exists to prevent.

1. **Element handles go stale the moment the DOM re-renders.** An autocomplete popup, a component menu, or a live server push invalidates every handle from the previous query. A stale handle does not error; it clicks whatever now occupies that position. **Re-query handles after any interaction that could re-render, and prefer keyboard navigation to the next field over clicking when a popup is likely open.**
2. **Setting `.value` in JavaScript and dispatching a synthetic `input` event does not reach server-side bound fields.** For a text field without an immediate-binding flag, the binding fires on blur. The DOM looks correct and the submit button stays disabled, which reads as an application bug and is not one. **Type with real keyboard input and blur explicitly. JavaScript value-setting is diagnostic only, never a substitute for a real interaction.**
3. **After a deploy swaps the app, an open tab is on a dying connection.** The first click after a redeploy runs against a circuit that is already gone and produces arbitrary results. **Hard-reload the page after every deploy, before the first smoke action.**
4. **Confirm an action by its observable side effect, not by the click returning.** Where a cancel control sits close to a submit control, a stale handle can hit the wrong one; the panel closes, which looks like success. **Every row's Observed column should name a side effect that was actually checked.**
5. **Browser tooling can report a zero-size viewport,** which makes screenshot capture and coordinate-based clicking unreliable and can look like an application defect. **Prefer handle-based clicking over coordinates, and if a screenshot comes back empty or a coordinate click lands nowhere, check the viewport before diagnosing the app.**
6. **A drawer or overlay left open from earlier in the session can sit over the element under test.** Close anything you opened before starting a row.

### 7.2 Sequence

1. Confirm the preconditions in Section 4. Stop if any fails.
2. Navigate to the dev URL and sign in with the account the checklist calls for.
3. For each checklist row: perform the action, read the page, screenshot the relevant region, then read console messages and network requests **for that row**.
4. Record observed behavior per row, not a verdict alone.
5. On any FAIL or BLOCKED row, enter the fix loop in 7.2.1.
6. When the checklist is clean, post the artifact, apply `agent-smoked`, and **leave the build on dev** for the human pass. Do not restore.

### 7.2.1 The fix loop

A FAIL is not a handoff. Fix it, redeploy, and run the checklist again.

1. Diagnose from the evidence already captured. The console message and the failing request usually name the cause, which is the reason they are captured on every row rather than reconstructed after the fact.
2. Write the fix on the same branch, with a test where the failure was testable.
3. Build and run tests locally before redeploying. A redeploy is minutes; a local build is seconds.
4. Redeploy the branch to dev.
5. **Re-run the entire checklist, not the failed row.** A fix can break a row that previously passed, and finding that out from the human pass rather than the agent pass wastes the whole point.
6. Record each iteration in the artifact.

**Stop the loop and ask when:** the fix needs a scope decision, the failure is in someone else's code or a shared component, the same row fails twice for different reasons (which usually means the row or the requirement is wrong rather than the code), or the failure implies the mockup and the spec disagree.

**Do not loop silently.** Report iterations as they happen. Four rounds on one row is a signal worth surfacing early, not a detail for the closing summary.

### 7.2.2 Handoff

When the checklist is clean, say plainly: what is deployed on dev, the URL, which account to sign in with, what the agent pass already covered, and which rows are marked HUMAN and still need eyes. The reviewer is not re-running the checklist. They are looking at what an agent cannot judge.

### 7.3 Console and network are read on every row

Not only on rows that look wrong. A row that renders correctly and throws a `TypeError` in the console is a FAIL. A row that renders correctly while a background POST returns 500 is a FAIL. These are precisely the quirks that unit and integration tests cannot reach, and they are the reason this pass exists at all.

### 7.4 Writing checklist rows an agent can actually run

Section 8h rows are usually written for a human, who can tell whether something "looks right." An agent cannot, and a row it cannot evaluate turns into a guess, which is how false-PASS rows get written.

A row an agent can run states an observable condition: text that must be present, an element that must exist, a count, a value, a route the browser must end on. "The dashboard loads correctly" is not a row. "The dashboard shows a [WIDGET NAME] card whose value is a non-negative integer, and the page ends on `/[EXPECTED ROUTE]`" is.

Rows that genuinely need human judgment (visual polish, spacing, whether a layout feels right) are marked `HUMAN` in the checklist and excluded from the agent pass. They belong to the mockup conformance gate in `coding-blazor-ui.md` Section 8.4 or to the human pass.

## 8. The evidence artifact

Posted as a comment on the wave or fix issue. This format is the deliverable of the agent pass, and a run without it did not happen.

```markdown
## Agent Smoke Pass

**Environment:** dev, `[DEV APP SERVICE NAME]`
**Ref deployed:** `feat/issue-[NN]` @ `[SHA]`
**Deploy run:** <link to the dev CD workflow run>
**Account:** `[PLATFORM]_DEV_SMOKE_USER` (normal user)
**Schema assertion:** PASS, `[SCHEMA.OBJECT]` present on dev with [N] rows
**Result: 6 PASS, 1 FAIL, 1 BLOCKED, 2 HUMAN (deferred)**

| # | Action | Expected | Observed | Console | Network | Result |
|---|---|---|---|---|---|---|
| 1 | Open /[list route] | List renders with at least one row | 12 rows, first is "[value]" | clean | clean | PASS |
| 2 | Click a row | Detail opens, items in order | Detail opened, 8 items ascending | clean | clean | PASS |
| 3 | Submit the form | Item appends, status Sent | Item appended, status stuck on Sending | `TypeError: Cannot read properties of undefined (reading 'status')` at `[file]:214` | `POST /api/[route]` returned 500 | **FAIL** |
| 4 | Filter by unread | Only unread shown | not run, blocked by row 3 | | | BLOCKED |

### Console errors, full text
```
[paste the full stack, not a summary]
```

### Failed requests, full
```
POST /api/[route]  ->  500
{"error":"[full response body]"}
```

### Screenshots
(attached, one per row)

### Rows deferred to human review
- 7: [visual item] against the mockup (HUMAN)
- 8: [visual item] (HUMAN)
```

**Every row carries an Observed column.** A row reading PASS with no observed behavior is not evidence, it is the false-PASS failure in a new format. This rule is the whole point of the artifact.

## 9. Rules

1. **Never edit the checklist to match what was found.** A row that cannot be run is BLOCKED with a reason, never quietly rewritten or dropped.
2. **Never run against a production hostname.** Not when the dev deploy fails, not to confirm something works "somewhere," not for any reason.
3. **Dispatch the dev deploy and merge the PR without asking.** Both are the agent's to run, per 5.3.1.
4. **There is no smoke-test workflow file.** Dispatch the repo's existing dev CD workflow. Do not search `.github/workflows/` for one, do not write one, and do not treat its absence as a blocker. See 5.3.
5. **Leave the build on dev when the pass is clean.** Restoring is an exception path (5.2.2), never a closing step, and no scheduled job may restore automatically.
6. **A FAIL enters the fix loop, and the fix re-runs the full checklist**, since a fix can break a row that previously passed.
7. **The artifact posts before the PR opens on Tier 3**, same rule and same severity as the parallel verification agents in `coding-verification.md` Section 14.3.
8. **A resumed session does not assume the pass already ran.** Check the issue for the artifact and the `agent-smoked` label. Absence means it did not happen.
9. **Say what is on dev before ending any session that deployed there.** A shared environment holding an unannounced build is how someone else's afternoon gets lost.

## 10. Setup checklist for a new repo

Check the first four before building anything. In practice most repos already pass them.

- [ ] Confirm the repo's dev CD workflow carries a `workflow_dispatch` trigger. Add one if it does not; that is a one-line change, not a new workflow.
- [ ] Confirm no job in that workflow carries a branch `if:` guard that would skip on a feature branch.
- [ ] Confirm the `dev` deployment environment has no protection rules and no deployment branch policy.
- [ ] Confirm the deploy targets are hardcoded to dev resource names rather than selected by an environment variable.
- [ ] Check whether the dev CD workflow publishes database schema (4.2). If not, the manual publish rule applies on that repo.
- [ ] Create the `agent-smoked` label.
- [ ] Confirm where the dev login path actually resolves (6.4) before creating any account.
- [ ] Provision the two smoke accounts, and **verify the roles or permission flags actually landed** rather than trusting a plan doc.
- [ ] Add the four vault secrets with honest descriptions, and verify a standard unlock surfaces them.
- [ ] Run one smoke end to end on a throwaway branch before relying on it for real work.

**Do not add to this list:** a smoke-specific deploy or restore workflow, a dedicated smoke environment, a hold variable, or a dispatch token. See 5.3 for why.

---

## Corrections Log

*Tracks issues found when following this file's instructions. Entries are added when a discrepancy is discovered and a fix is applied or proposed.*

| Date | What Failed | Root Cause | Fix Applied | ERRORS.md Ref |
|------|-------------|------------|-------------|---------------|

**Notes:**
<!-- Per-entry context that doesn't fit in the table. Format: "YYYY-MM-DD: [explanation]" -->
<!-- The two largest corrections already folded into this file, kept here because they are the
     kind of mistake worth not repeating: (1) a smoke-specific deploy and restore workflow pair
     was specified in Section 5.3 and never built, because every repo dev CD workflow already
     supported a feature-branch dispatch. Sessions searched for the nonexistent file and stalled.
     (2) A nightly scheduled restore was specified alongside it, which would have destroyed a
     feature build sitting on dev waiting for human review, the normal state under 5.2. Look at
     what the pipeline already does before specifying new pipeline. -->
