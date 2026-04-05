# Source Control  -  Git Repository Management
<!-- CUSTOMIZE: Update org names, PAT variable names, and repo names for your organization -->

All code repositories clone into the `Source Control/` folder, organized by organization:

```
Source Control/
  Personal/          ← your personal GitHub org repos
  [ORG-1]/           ← primary org repos (e.g., your company)
  [ORG-2]/           ← secondary org repos (e.g., a client or partner)
```

**Default branch rule:** Pull `dev` unless otherwise specified.

**PAT selection rule:**

| GitHub org | PAT env var |
|---|---|
| `github.com/[personal org]/*` | `GITHUB_PAT` |
| `github.com/[org-1]/*` | `GITHUB_PAT_ORG1` |
| `github.com/[org-2]/*` | `GITHUB_PAT_ORG2` |

<!-- CUSTOMIZE: Replace the org names and PAT variable names above with your actual values -->

**PAT auth formats:** Both formats work for fine-grained PATs:

- **Git URL auth** (for clone/pull/push): `https://x-access-token:${PAT}@github.com/ORG/REPO.git`
- **GitHub API auth** (for `curl`, REST calls): `Authorization: Bearer ${PAT}` header

Don't mix them. Git operations use the URL format. API operations use the header format.

---

## Cloning Behavior  -  Mounted Volume Workaround

The Cowork VM's mounted filesystem does not support `.git/config.lock` operations during `git clone`. The workaround is to clone to `/tmp/` first, then `rsync` to the target path:

```bash
# Pattern for any repo clone:
git clone -b BRANCH "https://x-access-token:${PAT}@github.com/ORG/REPO.git" /tmp/sc-REPO 2>&1
cd /tmp/sc-REPO && git config user.name "[YOUR NAME]" && git config user.email "[YOUR EMAIL]"
rsync -r /tmp/sc-REPO/ "$COWORK/Source Control/COMPANY/REPO/" 2>&1
rm -rf /tmp/sc-REPO
```

**Write operations on the mounted volume are unreliable.** `git pull`, `git commit`, and `git push` can all fail with "Operation not permitted" when git tries to write temp objects or lock files. The macOS APFS filesystem owns the mount and blocks writes from the Linux VM process.

**Rule: always use the `/tmp/` clone workaround for any commit operation on a mounted repo.** Clone fresh to `/tmp/`, make the change, commit, push, then discard the clone. The mounted copy stays as a read reference.

If a lock file is left behind by a failed git operation, the VM cannot delete it. Remove it from the Mac side:

```bash
# Mac-side cleanup
BASE="[YOUR COWORK PATH]"
rm -f "$BASE/Source Control/[ORG]/[REPO]/.git"/*.lock
echo "All git locks cleared"
```

---

## Pre-Push Checklist (All Repos)

Before every `git push` that includes code changes:

1. **Signature change grep:** If any method or constructor signature changed, grep all test files for references before pushing. See `coding-best-practices.md` Section 6.11.
2. **CI-first for compiled languages:** Let CI verify the build rather than compiling locally. Push to a feature branch and watch the pipeline.
3. **PAT scope:** If the push includes workflow files (`.github/workflows/`), confirm the PAT has `workflow` scope.

---

## Clone Pattern (Any Repo)

```bash
# Replace PAT, ORG, REPO_NAME, BRANCH with your values
git clone -b "$BRANCH" "https://x-access-token:${PAT}@github.com/${ORG}/${REPO_NAME}.git" "/tmp/sc-${REPO_NAME}" 2>&1
cd "/tmp/sc-${REPO_NAME}" && git config user.name "[YOUR NAME]" && git config user.email "[YOUR EMAIL]"
rsync -r "/tmp/sc-${REPO_NAME}/" "${SC_DIR}/${REPO_NAME}/" 2>&1
rm -rf "/tmp/sc-${REPO_NAME}"
```

## Pull / Push Pattern

```bash
REPO_DIR="[path to repo on mounted volume]"
rm -f "$REPO_DIR/.git"/*.lock 2>/dev/null  # pre-op: clear stale locks
git -C "$REPO_DIR" pull origin BRANCH 2>&1
rm -f "$REPO_DIR/.git"/*.lock 2>/dev/null  # post-op: clean up
```

```bash
rm -f "$REPO_DIR/.git"/*.lock 2>/dev/null
git -C "$REPO_DIR" add -A && git -C "$REPO_DIR" commit -m "Description" && git -C "$REPO_DIR" push origin BRANCH 2>&1
rm -f "$REPO_DIR/.git"/*.lock 2>/dev/null
```

---

## Docs Folder Convention  -  Code Repos

Every code repo uses a `docs/` folder for project plans, mockups, and reference documentation.

### Structure

```
docs/
  feat-issue-52/           ← issue-specific: plans, mockups, implementation docs
  draft-inbox-monitor/     ← pre-issue: plans started before a GitHub issue exists
  README_Architecture.md   ← reference docs that outlive any single issue
```

### Rules

1. **One subfolder per GitHub issue.** Named `feat-issue-{N}/`. All plans, mockups, ADRs, and deploy scripts for that issue go in its subfolder.
2. **Pre-issue drafts.** Use `draft-{project-name}/`. Rename to `feat-issue-{N}/` when the GitHub issue is created.
3. **Reference docs stay at root.** Documentation that applies to the whole repo and outlives any single issue stays at `docs/` root level.
4. **Release notes go in docs repos, not code repos.**

### Workflow  -  Issue Lifecycle in Docs

1. **Scoping:** Create `docs/draft-{project-name}/` with plan and mockups.
2. **Issue created:** Rename folder to `docs/feat-issue-{N}/`.
3. **Implementation:** All issue-specific docs stay in the subfolder. Update the plan as work progresses.
4. **Release:** Write release notes in the docs repo.
5. **Post-merge:** Evaluate whether any docs should be promoted to root `docs/` as lasting references.

---

## Commit Guidelines

- Commit after completing a logical unit of work.
- Don't batch an entire session into one commit. Break it up.
- Commit messages should be short and descriptive, not generic.

---

## Corrections Log

*Tracks issues found when following this file's instructions.*

| Date | What Failed | Root Cause | Fix Applied | ERRORS.md Ref |
|------|-------------|------------|-------------|---------------|
| 2026-03-20 | `git commit` on a mounted volume path failed with "Operation not permitted"  -  prior note said commit/push worked directly | macOS APFS owns the mount; Linux VM cannot write git temp objects or lock files during commit | Corrected the guidance: write ops are unreliable on mounted volumes. Added `/tmp/` clone pattern as the standard for all commit operations. |  -  |

**Notes:**
<!-- Per-entry context that doesn't fit in the table. Format: "YYYY-MM-DD: [explanation]" -->
