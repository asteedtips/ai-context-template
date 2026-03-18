# Source Control — Git Repository Management

<!--
  TEMPLATE: This file documents how your AI agent manages git repositories.
  Fill in your org structure, repos, PATs, and branch conventions.
  The pattern below supports multiple GitHub orgs with separate PATs per org.
-->

All code repositories clone into a defined folder, organized by company or GitHub organization:

```
Source Control/
  [Org A]/         <- repos using PAT_ORG_A
    repo-one/
    repo-two/
  [Org B]/         <- repos using PAT_ORG_B
    repo-three/
  Personal/        <- repos using your personal PAT
    private/           context files, CLAUDE.md, memory, tasks
```

<!--
  CUSTOMIZE: Replace the org names and repo examples with your own.
  If you only use one GitHub org, simplify to a single level.
-->

**Default branch rule:** Pull `dev` unless otherwise specified. Personal repos (context files, templates) typically pull `main`.

---

## PAT Selection

Each GitHub organization uses a separate Personal Access Token stored in your secret store (see `security/security-practices.md`).

<!--
  CUSTOMIZE: Fill in your actual orgs and PAT env var names.

  | GitHub org | PAT env var | Source |
  |---|---|---|
  | `github.com/[your-org]/*` | `GITHUB_PAT_ORG` | Your vault |
  | `github.com/[your-personal]/*` | `GITHUB_PAT` | Your vault |
-->

**Fine-grained PAT auth format:** Fine-grained personal access tokens (prefix `github_pat_`) require `Authorization: Bearer <token>` in API calls. The older `Authorization: token <token>` format returns 401. Classic PATs (prefix `ghp_`) accept either format. Use `Bearer` for fine-grained PATs; either format works with classic PATs.

---

## Cloning Behavior — Mounted Volume Workaround

If your AI agent runs in an environment with a mounted filesystem (Cowork, Docker, etc.), `git clone` may fail with `.git/config.lock` errors. The workaround is to clone to a temp directory first, then copy to the target path:

```bash
# Pattern for any repo clone:
git clone -b BRANCH "https://x-access-token:${PAT}@github.com/ORG/REPO.git" /tmp/sc-REPO 2>&1
cd /tmp/sc-REPO && git config user.name "[Your Name]" && git config user.email "[your@email.com]"
rsync -r /tmp/sc-REPO/ "$TARGET_DIR/REPO/" 2>&1
rm -rf /tmp/sc-REPO
```

After the initial clone, `git commit` and `git push` work directly on the mounted path. `git pull` can fail with `ORIG_HEAD.lock` errors on mounted volumes. If pull fails, use the same `/tmp/` workaround: copy to temp, pull there, rsync back.

---

## Repository Table

<!--
  CUSTOMIZE: List your repos. Group by org.

  | Repo | Local Path | Default Branch | Contents |
  |------|------------|----------------|----------|
  | `org/repo-name` | `Source Control/Org/repo-name/` | dev | Description |
-->

---

## Clone / Pull / Push Snippets

### Clone a new repo

```bash
# Adapt PAT variable, org, repo name, and branch
KEYS_FILE="path/to/your/keys.json"
PAT=$(python3 -c "import json; print(json.load(open('$KEYS_FILE'))['YOUR_PAT_NAME'])")
REPO_NAME="your-repo"
BRANCH="dev"
TARGET_DIR="path/to/Source Control/OrgName"

git clone -b "$BRANCH" "https://x-access-token:${PAT}@github.com/org/${REPO_NAME}.git" "/tmp/sc-${REPO_NAME}" 2>&1
cd "/tmp/sc-${REPO_NAME}" && git config user.name "[Your Name]" && git config user.email "[your@email.com]"
rsync -r "/tmp/sc-${REPO_NAME}/" "${TARGET_DIR}/${REPO_NAME}/" 2>&1
rm -rf "/tmp/sc-${REPO_NAME}"
```

### Pull latest

```bash
REPO_DIR="path/to/Source Control/OrgName/repo-name"
cd "$REPO_DIR" && git pull origin BRANCH 2>&1
```

### Commit and push

```bash
cd "$REPO_DIR" && git add -A && git commit -m "Description" && git push origin BRANCH 2>&1
```

---

## Docs Folder Convention — Code Repos

Every code repo uses a `docs/` folder for project plans, mockups, and reference documentation. This section defines how that folder is organized.

### Structure

```
docs/
  feat-issue-52/           <- issue-specific: plans, mockups, implementation docs, deploy scripts
  feat-issue-54/           <- issue-specific: plans, mockups, implementation docs
  draft-new-feature/       <- pre-issue: plans started locally before a GitHub issue exists
  README_Identity.md       <- reference docs that outlive any single issue
  dev-local-settings.md
```

### Rules

1. **One subfolder per GitHub issue.** Named `feat-issue-{N}/` to match the branch naming pattern (`feat/issue-{N}`). All plans, mockups, HTML wireframes, ADRs, implementation status docs, and deploy scripts for that issue go in its subfolder.

2. **Pre-issue drafts.** When scoping starts locally before a GitHub issue is created, use `draft-{project-name}/` (e.g., `docs/draft-new-feature/`). Rename to `feat-issue-{N}/` as soon as the GitHub issue is created. Git tracks the rename cleanly.

3. **Reference docs stay at root.** Documentation that applies to the whole repo and outlives any single issue (README_*, Architecture references, developer setup guides) stays at `docs/` root level. If a doc starts as issue-specific but becomes a long-lived reference, promote it to root when the issue closes.

4. **Plan file naming inside the subfolder.** The primary plan file uses the pattern from `project-scoping-bp.md` Section 11: `{Project}-Plan.md`. Supporting files (mockups, ADRs, status trackers) use descriptive names.

5. **Release notes go in docs repos, not code repos.** If your org uses a separate docs repository for release notes, write them there. Never commit release notes to the code repo.

<!--
  CUSTOMIZE: If your org has a separate docs repo for release notes, specify it here:

  | Org | Docs Repo | Release Notes Path |
  |-----|-----------|-------------------|
  | [YOUR_ORG] | `[org]/docs` | `product-development/release-notes/` |

  Release notes naming: `release-{seq}-{short-description}.md`
-->

6. **Deploy scripts follow their issue.** If deploy scripts (PowerShell, Bicep, ARM) are created as part of an issue, they go in that issue's subfolder. Cross-cutting deploy scripts get promoted to `docs/deploy/` or the repo's `/infra` folder.

### Workflow — Issue Lifecycle in Docs

1. **Scoping (pre-issue):** Create `docs/draft-{project-name}/` with the plan file and mockups.
2. **Issue created:** Rename folder to `docs/feat-issue-{N}/`. Update any internal references.
3. **Implementation:** All issue-specific documentation stays in the subfolder. Update the plan as work progresses per `project-scoping-bp.md` plan drift rule.
4. **Release:** Write the release notes file in the docs repo (not the code repo). Reference the issue number and PR.
5. **Post-merge cleanup:** After the feature branch merges, evaluate whether any docs should be promoted to root `docs/` as lasting references.

---

## Pre-Push Checklist (All Repos)

Before pushing any commit, verify these items:

1. **Signature change grep.** If any method signature changed (renamed, parameters added/removed, return type changed), grep all test files and consuming code for references to the old signature. This prevents multi-file breakage that CI catches but takes a full round-trip to diagnose. See `coding-best-practices.md` Section 6.8.

2. **CI-first verification.** If your environment uses CI as the primary build gate (see `coding-best-practices.md` Section 9.4), do not build locally for verification. Push to the feature branch and let CI verify.

3. **PAT scope for workflow files.** If the commit includes changes to `.github/workflows/` files, confirm the PAT has the `workflow` scope. Standard `repo` scope is not sufficient.

---

## Commit Guidelines

- Commit after completing a logical unit of work (updated plan section, new feature, bug fix, etc.)
- Don't batch an entire session into one commit. Break it up.
- Commit messages should be short and descriptive, not generic.

---

## PR Workflow — Comments on Every Push

When a push is related to an open PR, post a summary comment on the PR describing what changed in that push. If a linked issue exists, post the same summary there. This keeps reviewers informed without them needing to diff commits.

**On every push to a PR branch:**
1. Post a comment on the PR with a structured summary: which files changed, what the changes do, and current CI status.
2. If the PR references a GitHub issue, post the same summary as a comment on the issue.
3. Keep summaries factual — list commits, describe changes, note CI status. No filler.

**After CI goes green (final push):**
1. Post a follow-up comment confirming CI passed with the test count.
2. Update the PR description/body if the feature summary or test plan changed.
3. Review and update release notes (see next section).

---

## Phase Close — Release Notes Review

At the end of every phase that touches production code, review the release notes in your docs repo for accuracy. Do not wait to be asked.

**What to check:**
- Do the release notes still accurately describe the feature's behavior after this phase's changes?
- Were any dependencies added or removed?
- Did the test coverage description change?
- Did infrastructure requirements change?

**When to update:** After CI is green on the final push for a phase, before closing out the session. If the phase only changed internal implementation (no behavior, API, or infrastructure changes), verify that's the case by reading the release notes file — don't assume.

---

## Architecture Documentation Convention

<!--
  OPTIONAL: Consider keeping a living architecture reference doc (Architecture.md)
  at the root of each code repo. When working on any repo, read it first to orient.
  Update it before closing the session if code was modified.
-->

---

*Last updated: 2026-03-16 -- Added Pre-Push Checklist, corrected git pull guidance for mounted volumes, added fine-grained PAT Bearer auth note, PR Workflow, Phase Close sections.*


---

## Corrections Log

*Tracks issues found when following this file's instructions. Entries are added when a discrepancy is discovered and a fix is applied or proposed.*

| Date | What Failed | Root Cause | Fix Applied | ERRORS.md Ref |
|------|-------------|------------|-------------|---------------|

**Notes:**
<!-- Per-entry context that doesn't fit in the table. Format: "YYYY-MM-DD: [explanation]" -->
