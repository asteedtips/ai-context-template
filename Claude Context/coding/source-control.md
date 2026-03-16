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

After the initial clone, `git pull`, `git commit`, and `git push` all work directly on the mounted path.

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

## Commit Guidelines

- Commit after completing a logical unit of work (updated plan section, new feature, bug fix, etc.)
- Don't batch an entire session into one commit. Break it up.
- Commit messages should be short and descriptive, not generic.

---

## Architecture Documentation Convention

<!--
  OPTIONAL: Consider keeping a living architecture reference doc (Architecture.md)
  at the root of each code repo. When working on any repo, read it first to orient.
  Update it before closing the session if code was modified.
-->

---

*Last updated: 2026-03-15 -- Added Docs Folder Convention section: issue subfolders, pre-issue drafts, release notes in docs repos, deploy scripts follow their issue.*
