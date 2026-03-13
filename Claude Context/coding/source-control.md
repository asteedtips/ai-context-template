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

*Last updated: [DATE]*
