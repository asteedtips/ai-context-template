# API Security Practices

> **When documenting any security workflow or producing deliverables from this context, read `Claude Context/writing/best-practices-creation.md`** — it governs output formats, diagram standards, naming conventions, and writing rules.

All API credentials live in a centralized secret store. No secrets, tokens, keys, or passwords are stored in plain text in any file the AI agent can read.

---

## The Rule

If it's a secret, it lives in your vault. Period. This applies to:

- OAuth client secrets
- Refresh tokens and access tokens
- API keys
- Passwords used in automation
- Webhook secrets
- Any value that would cause a security incident if exposed

Non-secret config values (org IDs, API domain URLs, app names) can remain in context files as plain text, but when in doubt, put it in the vault.

---

## Recommended Architecture

The principle is a three-layer chain: a local encrypted bootstrap that authenticates to cloud vaults, which hold all real secrets. Secrets are pulled at session start and loaded into environment variables scoped to the session.

```
Local encrypted file (bootstrap keys per organization)
        │
        ▼  (decrypts bootstrap keys)
        │
Cloud Secret Stores (all real credentials, per org)
        │
        ▼  (pulled at session start, filtered by tier and org)
        │
Session-scoped env vars (chmod 600, merged from all orgs)
```

This architecture supports multiple organizations, each with its own vault and optional Entra ID tenant. Bootstrap keys are stored locally and keyed by org (e.g., `ORG1_KV_CLIENT_ID`, `ORG2_KV_CLIENT_ID`). At session start, each org's vault is queried in sequence, secrets are filtered by access tier, merged into a single result set, and loaded into env vars. Secrets from different orgs can receive prefixes to avoid collisions (e.g., `ORG1_ZOHO_CLIENT_ID` vs. `ORG2_ZOHO_CLIENT_ID`).

<!-- CUSTOMIZE: Choose and configure your secret store.

  Options (pick one):
  1. Azure Key Vault — best if you're already in the Microsoft ecosystem
  2. AWS Secrets Manager — best if you're in the AWS ecosystem
  3. 1Password CLI (op://) — good for individuals and small teams
  4. HashiCorp Vault — good for self-hosted or multi-cloud
  5. Encrypted local file + helper script — minimum viable approach

  Whichever you choose, the pattern stays the same:
  - A local bootstrap mechanism (encrypted file, env var, or CLI login)
  - A central store (or stores per org) that holds all real secrets
  - A session-start script that pulls secrets into env vars, filtering by tier and org
  - Context files reference env var NAMES only — never actual values
-->

### Component Layout

| Component | Purpose |
|---|---|
| Bootstrap credentials | Stored locally (encrypted), one per org, used only to authenticate to that org's vault |
| Cloud secret stores | Per-org credential store for all services. Each org has one primary vault and optional secondary vaults. |
| Session cache | Env vars and/or JSON file, session-scoped, restricted permissions (chmod 600), merged from all orgs |
| Helper script | CLI tool that ties bootstrap → all vaults → session cache, filtered by access tier and org |

---

## Access Tiers

Every secret in the vault is tagged with a tier value. The unlock script filters by tier, and your vault's RBAC enforces it at the infrastructure level. This enables fine-grained access control: a read-only team member's SP can only read secrets tagged `ro` and `shared`, even if they somehow bypass the script's filter.

| Tier | Who gets it | What it includes | Vault RBAC |
|---|---|---|---|
| `ro` | Team members with read-only agents | Read-only API credentials + shared config | Per-secret reader role on ro + shared secrets |
| `rw` | Team members who need to create/update records | Read-write API credentials + shared config | Per-secret reader role on rw + shared secrets |
| `adm` | Admin only | PATs, org-level tokens, plus everything in rw + shared | Per-secret reader role on adm + rw + shared secrets |
| `shared` | All tiers | Config values needed by everyone (org IDs, tenant IDs) | Included in all tier scopes |
| `app` | Application infrastructure only | DB connection strings, not pulled by agent sessions | Not accessed by agent unlock script |

Tier inheritance: `ro` gets `ro + shared`. `rw` gets `rw + shared`. `adm` gets `adm + rw + shared`. The `all` default (when no tier is specified) includes everything except deprecated secrets.

<!-- CUSTOMIZE: Define your own tiers based on team structure.
  The example above is a starting point — adjust names and inheritance to fit your org.
  For each tier, also set up corresponding service principals in your vault's RBAC: one SP per tier, with role assignments restricted to that tier's secret names.
-->

---

## Enforcement Layers

Each tier should be enforced at multiple independent levels. Even if one layer is misconfigured, the others still block unauthorized access.

| Layer | What it does |
|---|---|
| Vault RBAC | Per-secret role assignments on each service principal — the agent's identity can only read its assigned secrets |
| API scopes/permissions | Service-level OAuth scopes — a read-only credential physically cannot write, even if the agent tries |
| Software (`--tier` flag) | The unlock script filters secrets before loading — skips anything outside the agent's tier |

The combination of all three means a read-only agent can't accidentally (or intentionally) write data through any path.

---

## Naming Convention

Use a consistent naming pattern for secrets. Add a **tier suffix** so the same service can have different credentials for different access levels. The unlock script strips the tier suffix when creating env var names, so downstream code works without changes.

**Pattern:** `{service}-{descriptor}-{tier}`

| In Secret Store | Tier | As Env Var |
|---|---|---|
| `service-client-id-rw` | rw | `SERVICE_CLIENT_ID` |
| `service-client-secret-rw` | rw | `SERVICE_CLIENT_SECRET` |
| `service-client-id-ro` | ro | `SERVICE_CLIENT_ID` |
| `service-org-id` | shared | `SERVICE_ORG_ID` |

An `ro` agent and an `rw` agent both see `SERVICE_CLIENT_ID` as their env var, but the underlying credential has different permissions at the API provider level. Code doesn't change; only the permissions do.

**Multi-org naming:** When supporting multiple organizations, optionally prefix the env var name with the org identifier to avoid collisions:

| In Secret Store | Org | Tier | As Env Var |
|---|---|---|---|
| `service-client-id-rw` | [ORG1] | rw | `SERVICE_CLIENT_ID` |
| `service-client-id-rw` | [ORG2] | rw | `[ORG2]_SERVICE_CLIENT_ID` |

The unlock script applies the org prefix only if secrets from multiple orgs could collide. Otherwise it uses the base env var name.

<!-- CUSTOMIZE: Add your actual secret names here once configured.
  Example:
  | `mycrm-client-id-rw` | rw | `MYCRM_CLIENT_ID` |
  | `email-client-id-ro` | ro | `EMAIL_CLIENT_ID` |
  | `mycrm-client-id-rw` | [OtherOrg] | rw | `OTHERORG_MYCRM_CLIENT_ID` |
-->

---

## How to Use Keys at Runtime

### Step 1 — Unlock / Load Secrets

Each team member receives a passphrase and a bootstrap file (`.enc`) containing credentials for their assigned organization and tier. The unlock script uses these to authenticate to the vault, pull secrets filtered by tier, and load them into session env vars.

<!-- CUSTOMIZE: Document your specific unlock command here.

  Example for Azure Key Vault with Python helper:
  ```python
  python3 << 'PYEOF'
  from pathlib import Path
  import subprocess
  kh = next(Path('/sessions').rglob('ClaudeCowork/Claude Context/helpers/key_helper.py'), None)
  subprocess.run(['python3', str(kh), 'unlock', '--org', '[ORG_NAME]', '--tier', 'rw'])
  PYEOF
  ```

  Example for 1Password:
  ```bash
  eval $(op signin)
  export MY_API_KEY=$(op read "op://[VAULT]/[ITEM]/[field]")
  ```

  Example for AWS Secrets Manager:
  ```bash
  aws secretsmanager get-secret-value --secret-id [secret-name] | jq -r '.SecretString' > /tmp/.secrets.json
  ```

  The unlock script should:
  - Read the passphrase from a local file (never typed in chat)
  - Decrypt bootstrap keys using the passphrase
  - Authenticate to the vault using bootstrap keys
  - Filter secrets by tier and optionally by org
  - Write results to a session cache (env vars and/or JSON, chmod 600)
  - Return the env var names so the calling code can use them

  Valid tier values: `ro`, `rw`, `adm`, `all` (default, excludes deprecated).
  Valid org values: `[ORG1]`, `[ORG2]`, etc., or `all` (default, pulls from all configured orgs).
-->

### Step 2 — Load into shell variables

```bash
# Read from your session cache (adapt path to your setup)
source ~/.zshenv
# or from JSON
export MY_KEY=$(python3 -c "import json; print(json.load(open('/tmp/.claude_keys.json'))['MY_KEY'])")
```

---

## Adding a New Secret

1. **Store the credential in your secret store first** — before writing any code or config
2. Use your naming convention (e.g., kebab-case with service prefix and tier suffix)
3. Tag the secret with the appropriate tier and org in the vault
4. Set up vault RBAC to allow the intended tier's service principal to read it
5. Run your unlock/load command and verify the key appears in session env vars
6. Update the relevant context file with the env var name only — never the actual value
7. Test a full unlock → load → API call cycle end-to-end
8. Document scopes granted and any expiry dates in the context file

---

## Adding a New API Connection — Checklist

When setting up any new API integration:

1. Store the credentials in your secret store first
2. Use the naming convention (kebab-case with service prefix)
3. Run unlock and verify keys appear in session env vars
4. Create a new context file for the service (use `api-template.md` as a starting point)
5. Test a full unlock → load → API call cycle end-to-end
6. Document scopes granted and any expiry dates
7. Add the new file to the workflow dependency chains in `CLAUDE.md`

---

## Credential Rotation

When rotating a credential (expired token, compromised secret, scope change, etc.):

1. Generate the new credential in the service's dashboard (e.g., Zoho Developer Console, Microsoft Entra ID, GitHub)
2. Update the secret value in your vault (same secret name, new value)
3. Run your unlock command to pull the updated value into the session
4. Test that the new credential works with a live API call
5. The context file does not need to change — the key name stays the same

<!-- CUSTOMIZE: If your vault supports API-driven rotation (like Azure Key Vault), document the programmatic flow here.
  Example for Azure Key Vault:
  ```python
  import json, urllib.request, urllib.parse
  keys = json.load(open('/tmp/.claude_keys.json'))
  data = urllib.parse.urlencode({
      'client_id': keys['KV_CLIENT_ID'],
      'client_secret': keys['KV_CLIENT_SECRET'],
      'grant_type': 'client_credentials',
      'scope': 'https://vault.azure.net/.default'
  }).encode()
  req = urllib.request.Request("https://login.microsoftonline.com/[TENANT_ID]/oauth2/v2.0/token", data=data)
  token = json.loads(urllib.request.urlopen(req).read())['access_token']
  update = json.dumps({"value": "<NEW_VALUE>"}).encode()
  kv_req = urllib.request.Request(
      "https://[VAULT].vault.azure.net/secrets/[SECRET_NAME]?api-version=7.4",
      data=update, method='PUT',
      headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
  )
  json.loads(urllib.request.urlopen(kv_req).read())
  ```
-->

---

## Team Onboarding — Bootstrap File Setup

Each team member receives a bootstrap file (`.enc` file) containing only the service principal credentials for their assigned organization and tier. The file is decrypted at session start using a passphrase, which authenticates to the vault and pulls that org and tier's secrets.

**What each person needs from the admin:**

1. A bootstrap `.enc` file for their assigned org and tier (e.g., `claude_keys_org1_ro.enc`)
2. A passphrase to decrypt it (the same passphrase works for all bootstrap files)
3. Documentation on which orgs and tiers they have access to

**Distribute these pieces through separate channels** so a single compromised channel doesn't expose both. For example, send the `.enc` file via a company messaging app and the passphrase via phone call or in person.

**Multi-org support:** If team members need access to multiple organizations, distribute one `.enc` file per org, or use a single `.enc` file that contains all orgs they're authorized for (with tier restrictions enforced by vault RBAC and the unlock script's `--org` flag).

<!-- CUSTOMIZE: Document your specific file paths and unlock commands here.
  Example:
  1. Place bootstrap files at `ClaudeCowork/Claude Context/helpers/claude_keys_[ORG].enc`
  2. Place the passphrase in `ClaudeCowork/keys/.vault_key` (shared for all orgs)
  3. Run:
     ```python
     subprocess.run(['python3', 'key_helper.py', 'unlock', '--org', '[ORG]', '--tier', 'ro'])
     ```
     or
     ```python
     subprocess.run(['python3', 'key_helper.py', 'unlock'])  # pulls all orgs, all tiers
     ```
  4. Secrets appear in `~/.zshenv` and `/tmp/.claude_keys.json`
-->

**Revoking access:**

1. Rotate the service principal's client secret in your identity provider (e.g., Entra ID for Azure vaults)
2. Update the secret value in the vault
3. Regenerate the `.enc` file for that org and tier, and redistribute to remaining authorized users
4. The revoked user's `.enc` file now contains a stale client secret that won't authenticate to the vault

---

## Database Access — Read-Only by Default

All database connections used by AI agents operate under a **read-only policy**. This applies to any database accessed during a session — SQL Server, PostgreSQL, MySQL, Cosmos DB, or any other data store.

<!--
  This section is NOT optional. It protects production data from accidental writes.
  Customize the approver name/role but keep the policy intact.
-->

**The rule:** The agent may execute `SELECT` queries and read data freely. Any operation that would alter or delete data requires explicit approval from the designated approver before execution. There are no exceptions.

**Operations that require explicit approval:**
- `INSERT`, `UPDATE`, `DELETE`, `MERGE`
- `TRUNCATE TABLE`, `DROP TABLE`, `ALTER TABLE`
- `CREATE`, `ALTER`, or `DROP` on any database object (tables, views, stored procedures, indexes, schemas)
- `EXEC` or `EXECUTE` on any stored procedure (unless the approver has confirmed it is read-only)
- Any transaction that wraps a write operation
- Bulk copy / `bcp` / data import operations

**Operations that are always permitted:**
- `SELECT` (including JOINs, CTEs, subqueries, aggregations, window functions)
- `INFORMATION_SCHEMA` and `sys.*` catalog queries (or equivalent for your database engine)
- `EXPLAIN` / execution plan analysis
- Temporary tables created within the session for query analysis — these do not persist
- `SET` statements that affect session behavior (e.g., `SET NOCOUNT ON`)

**How to request write access:** If a task requires modifying data (data migrations, cleanup scripts, schema changes), the agent will draft the SQL, present it for review, and wait for explicit approval before executing. The approver may also pre-approve a category of writes at the start of a task (e.g., "you can insert rows into the staging table").

**This policy applies regardless of the credential's actual permissions.** Even when connecting with an admin-level account, the agent treats the connection as read-only unless told otherwise.

<!--
  CUSTOMIZE: Replace "designated approver" with the actual person or role.
  Example: "requires explicit approval from the team lead"
  Example: "requires explicit approval from Albert"
-->

---

## What Never Goes in a File

- Actual token or secret values
- Passwords
- Private keys or certificates
- Anything prefixed with `sk_`, `pk_`, `Bearer `, or similar

If you're unsure whether something is sensitive, put it in the vault. The cost of an extra secret is zero. The cost of an exposed credential is not.

---

*Last updated: [DATE] — Updated to multi-org, multi-vault architecture with delegated access tiers, per-org prefixing, and team onboarding flow for distributed bootstrap files.*


---

## Corrections Log

*Tracks issues found when following this file's instructions. Entries are added when a discrepancy is discovered and a fix is applied or proposed.*

| Date | What Failed | Root Cause | Fix Applied | ERRORS.md Ref |
|------|-------------|------------|-------------|---------------|

**Notes:**
<!-- Per-entry context that doesn't fit in the table. Format: "YYYY-MM-DD: [explanation]" -->
