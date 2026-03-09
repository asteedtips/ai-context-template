# API Security Practices

> **When documenting any security workflow or producing deliverables from this context, read `Claude Context/best-practices-creation.md`** — it governs output formats, diagram standards, naming conventions, and writing rules.

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

## Naming Convention

Use a consistent naming pattern for secrets. When pulled into env vars, convert to uppercase with underscores.

| In Secret Store | As Env Var |
|---|---|
| `service-client-id` | `SERVICE_CLIENT_ID` |
| `service-client-secret` | `SERVICE_CLIENT_SECRET` |
| `service-refresh-token` | `SERVICE_REFRESH_TOKEN` |

<!--
  CUSTOMIZE: Add your actual secret names here once configured.
  Example:
  | `mycrm-client-id` | `MYCRM_CLIENT_ID` |
  | `email-client-id` | `EMAIL_CLIENT_ID` |
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

## What Never Goes in a File

- Actual token or secret values
- Passwords
- Private keys or certificates
- Anything prefixed with `sk_`, `pk_`, `Bearer `, or similar

If you're unsure whether something is sensitive, put it in the vault. The cost of an extra secret is zero. The cost of an exposed credential is not.

---

*Last updated: [DATE]*
