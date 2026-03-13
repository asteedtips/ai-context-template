# API Security Practices

> **When documenting any security workflow or producing deliverables from this context, read `Claude Context/writing/best-practices-creation.md`** — it governs output formats, diagram standards, naming conventions, and writing rules.

All API credentials should live in a centralized secret store. No secrets, tokens, keys, or passwords should be stored in plain text in any file the AI agent can read.

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

The principle is a three-layer chain: a local encrypted bootstrap that authenticates to a cloud vault, which holds all real secrets. The cloud vault's secrets are pulled at session start and loaded into environment variables scoped to the session.

```
Local encrypted file (2 bootstrap keys only)
        │
        ▼  (decrypts bootstrap keys)
        │
Cloud Secret Store (all real credentials)
        │
        ▼  (pulled at session start)
        │
Session-scoped env vars (chmod 600)
```

<!--
  SETUP REQUIRED: Choose and configure your secret store.

  Options (pick one):
  1. Azure Key Vault — best if you're already in the Microsoft ecosystem
  2. AWS Secrets Manager — best if you're in the AWS ecosystem
  3. 1Password CLI (op://) — good for individuals and small teams
  4. HashiCorp Vault — good for self-hosted or multi-cloud
  5. Encrypted local file + helper script — minimum viable approach

  Whichever you choose, the pattern stays the same:
  - A local bootstrap mechanism (encrypted file, env var, or CLI login)
  - A central store that holds all real secrets
  - A session-start script that pulls secrets into env vars
  - Context files reference env var NAMES only — never actual values
-->

### Component Layout

| Component | Purpose |
|---|---|
| Bootstrap credentials | Stored locally (encrypted), used only to authenticate to the vault |
| Cloud secret store | Primary credential store for all services |
| Session cache | Env vars and/or JSON file, session-scoped, restricted permissions |
| Helper script | CLI tool that ties bootstrap → vault → session cache |

---

## Access Tiers

When multiple people or agents use the same vault, tag each secret with an access tier so you can control who sees what. The unlock script filters by tier, and your vault's RBAC enforces it at the infrastructure level.

<!--
  CUSTOMIZE: Define your own tiers based on team structure.
  The example below is a starting point — adjust names and inheritance to fit your org.
-->

| Tier | Who gets it | What it includes |
|---|---|---|
| `ro` | Team members with read-only agents | Read-only API credentials + shared config |
| `rw` | Team members who need to create/update records | Read-write API credentials + shared config |
| `adm` | Admin only | PATs, org-level tokens, plus everything in rw + shared |
| `shared` | All tiers | Config values needed by everyone (org IDs, tenant IDs) |
| `app` | Application infrastructure only | DB connection strings, not pulled by agent sessions |

Tier inheritance: `ro` gets `ro + shared`. `rw` gets `rw + shared`. `adm` gets `adm + rw + shared`.

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

<!--
  CUSTOMIZE: Add your actual secret names here once configured.
  Example:
  | `mycrm-client-id-rw` | rw | `MYCRM_CLIENT_ID` |
  | `email-client-id-ro` | ro | `EMAIL_CLIENT_ID` |
-->

---

## How to Use Keys at Runtime

### Step 1 — Unlock / Load Secrets

<!--
  CUSTOMIZE: Document your specific unlock command here.

  Example for Azure Key Vault:
  ```bash
  python3 key_helper.py unlock
  ```

  Example for 1Password:
  ```bash
  eval $(op signin)
  export MY_API_KEY=$(op read "op://Vault/Item/field")
  ```

  Example for AWS Secrets Manager:
  ```bash
  aws secretsmanager get-secret-value --secret-id my-secrets | jq -r '.SecretString' > /tmp/.secrets.json
  ```
-->

### Step 2 — Load into shell variables

```bash
# Read from your session cache (adapt path to your setup)
source ~/.env_secrets
# or
export MY_KEY=$(python3 -c "import json; print(json.load(open('/tmp/.secrets.json'))['MY_KEY'])")
```

---

## Adding a New Secret

1. **Store the credential in your secret store first** — before writing any code or config
2. Use your naming convention (e.g., kebab-case with service prefix)
3. Run your unlock/load command and verify the key appears in session env vars
4. Update the relevant context file with the env var name only — never the actual value
5. Test a full unlock → load → API call cycle end-to-end
6. Document scopes granted and any expiry dates in the context file

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

When rotating a credential (expired token, compromised secret, etc.):

1. Generate the new credential in the service's dashboard
2. Update the secret value in your store (same secret name, new value)
3. Run your unlock command to pull the updated value
4. Test that the new credential works with a live API call
5. The context file does not need to change — the key name stays the same

---

## Team Onboarding — Bootstrap File Setup

Each team member receives a pre-encrypted bootstrap file containing only the service principal credentials for their assigned tier. The file is decrypted at session start using a passphrase, which authenticates to the vault and pulls that tier's secrets.

**What each person needs from the admin:**

1. A bootstrap `.enc` file for their assigned tier (ro or rw)
2. A passphrase to decrypt it

**Distribute these two pieces through separate channels** so a single compromised channel doesn't expose both. For example, send the `.enc` file via a company messaging app and the passphrase via phone call or in person.

<!--
  CUSTOMIZE: Document your specific file paths and unlock commands here.
  Example:
  1. Place the `.enc` file at `ClaudeCowork/Claude Context/keys.enc`
  2. Place the passphrase in `ClaudeCowork/keys/.vault_key`
  3. Run `python3 key_helper.py unlock --tier ro`
-->

**Revoking access:**

1. Rotate the service principal's client secret in your identity provider
2. Update the secret value in the vault
3. Regenerate the `.enc` file for that tier and redistribute to remaining authorized users
4. The revoked user's `.enc` file now contains a stale client secret that won't authenticate

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

*Last updated: [DATE] — Added access tiers, enforcement layers, tier naming convention, and team onboarding*
