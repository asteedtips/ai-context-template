# Securing Claude's API Keys with Azure Key Vault

**A practical guide to keeping credentials out of chat history and off disk.**

You're using Claude (Cowork, Claude Code, or similar) and connecting it to external APIs — Zoho, Microsoft Graph, Azure DevOps, whatever. Those APIs need credentials. The question is where to put them so Claude can use them without exposing secrets in conversation logs, local files, or anywhere else they shouldn't be.

This guide walks through the system we built and battle-tested. It uses Azure Key Vault as the single source of truth for all credentials, a small Python script to bootstrap access, and a local passphrase file so you never type a secret into chat again.

---

## The Problem

Claude runs in an ephemeral environment. Every session starts fresh. That means any API keys need to be loaded at the start of each session. The naive approaches all have problems:

- **Pasting keys into chat** — they're stored in conversation history forever. Anyone with access to your chat logs sees them.
- **Hardcoding in config files** — if those files are in a synced folder (iCloud, Dropbox, OneDrive), the keys are now on multiple devices and cloud servers.
- **Environment variables on the host** — better, but still plaintext on disk and visible to any process running as your user.

What we want: keys encrypted at rest, stored in a managed vault with access controls, pulled on demand, and never visible in chat.

---

## The Architecture

```
ClaudeCowork/keys/.vault_key        ← passphrase (local file, never in chat)
        │
        ▼
ClaudeCowork/Claude Context/
  ├── claude_keys.enc               ← AES-256 encrypted bootstrap (2 keys only)
  ├── key_helper.py                 ← CLI tool that ties it all together
  └── context_sync.py               ← bidirectional GitHub sync for context files
        │
        ▼  (decrypts bootstrap keys)
        │
Azure Key Vault: your-vault-name
  └── All real credentials (including GITHUB_PAT for context sync)
        │
        ▼  (pulled at session start)
        │
~/.zshenv + JSON cache             ← session-scoped, chmod 600
        │
        ▼  (context_sync.py reads GITHUB_PAT from cache)
        │
GitHub (private repo)
  └── All .md context files, CLAUDE.md, memory/, TASKS.md
      (synced across machines, excludes .enc and .vault_key)
```

Three layers of protection:

1. **Azure Key Vault** holds every real credential. Access is controlled by Azure AD with RBAC. Audit logs track every read.
2. **Local encrypted file** (`claude_keys.enc`) holds only two bootstrap keys — the client ID and secret for the app registration that reads from Key Vault. AES-256-GCM encryption with PBKDF2 key derivation (200,000 iterations).
3. **Passphrase file** (`.vault_key`) sits on your local disk in a known location. The script reads it automatically. You never type the passphrase in chat.

A fourth layer sits alongside the vault: **GitHub context sync**. All your instruction files (CLAUDE.md, context docs, glossary, task list) are version-controlled in a private repo and pulled at session start. The sync script uses a `GITHUB_PAT` stored in Key Vault, so even the token that powers cross-machine sync goes through the same secure pipeline.

The result: Claude runs `key_helper.py unlock` at session start, everything loads, context syncs, and no secrets appear anywhere they shouldn't.

---

## Step-by-Step Setup

### Step 1: Create an Azure Key Vault

If you don't already have one, create a Key Vault in your Azure subscription.

```bash
# Log into Azure CLI
az login

# Create a resource group (skip if you already have one)
az group create --name rg-claude-secrets --location eastus

# Create the Key Vault
az keyvault create \
  --name your-vault-name \
  --resource-group rg-claude-secrets \
  --location eastus \
  --sku standard
```

Pick a vault name that makes sense for your org. It needs to be globally unique across Azure.

### Step 2: Create an App Registration (Service Principal)

This is the identity Claude will use to authenticate to Key Vault. It gets a client ID and secret — those are the only two values stored locally.

1. Go to **Azure Portal > Microsoft Entra ID > App registrations > New registration**
2. Name it something clear like `Claude-KeyVaultReader`
3. Leave redirect URI blank (this is a daemon/service app, not a user-facing one)
4. Click **Register**

After registration:
1. Copy the **Application (client) ID** — this becomes `KV_CLIENT_ID`
2. Copy the **Directory (tenant) ID** — you'll hardcode this in the script
3. Go to **Certificates & secrets > New client secret**
4. Set a reasonable expiry (12-24 months), copy the secret value — this becomes `KV_CLIENT_SECRET`

**Set the expiry in your calendar now.** When it expires, Claude can't unlock anything until you rotate it.

### Step 3: Grant Key Vault Access

The app registration needs permission to read secrets from your vault.

```bash
# Grant "Key Vault Secrets User" role (read-only access to secrets)
az role assignment create \
  --role "Key Vault Secrets User" \
  --assignee <your-app-client-id> \
  --scope /subscriptions/<sub-id>/resourceGroups/rg-claude-secrets/providers/Microsoft.KeyVault/vaults/your-vault-name
```

Or in the portal: **Key Vault > Access control (IAM) > Add role assignment > Key Vault Secrets User** and assign it to your app registration.

Don't use "Key Vault Administrator" or "Key Vault Secrets Officer" — Claude only needs to read secrets, never write them.

### Step 4: Add Your Secrets to Key Vault

For each API you want Claude to access, add the credentials as secrets in Key Vault.

**Naming convention:** Use kebab-case with a service prefix. The script converts these to uppercase underscore env vars automatically.

| Key Vault Name | Becomes Env Var |
|---|---|
| `zoho-client-id` | `ZOHO_CLIENT_ID` |
| `ms-graph-client-secret` | `MS_GRAPH_CLIENT_SECRET` |
| `azure-devops-pat` | `AZURE_DEVOPS_PAT` |
| `github-pat` | `GITHUB_PAT` |
| `slack-bot-token` | `SLACK_BOT_TOKEN` |

Add secrets via CLI:

```bash
az keyvault secret set --vault-name your-vault-name --name zoho-client-id --value "your-value-here"
az keyvault secret set --vault-name your-vault-name --name zoho-client-secret --value "your-value-here"
```

Or use the Azure Portal: **Key Vault > Secrets > Generate/Import**.

### Step 5: Set Up the Local Files

Create your folder structure:

```
ClaudeCowork/
├── keys/
│   └── .vault_key              ← passphrase file
└── Claude Context/
    ├── key_helper.py           ← the script (see below)
    └── claude_keys.enc         ← created by the encrypt command
```

**Create the passphrase file:**

```bash
mkdir -p ~/path/to/ClaudeCowork/keys
echo 'your-passphrase-here' > ~/path/to/ClaudeCowork/keys/.vault_key
chmod 600 ~/path/to/ClaudeCowork/keys/.vault_key
```

Pick a strong passphrase. It protects the bootstrap keys. Special characters are fine in the `.vault_key` file because the script reads it with Python's `Path.read_text()`, not through a shell.

**A hard-won lesson about passphrases and bash:** If you ever need to pass the passphrase directly (via env var or CLI arg instead of the file), use a Python heredoc. Bash mangles special characters like `!`, `@`, `$`, and backticks even inside single quotes in some contexts. The only reliable method:

```python
python3 << 'PYEOF'
import subprocess, os
from pathlib import Path
kh = next(Path('/sessions').rglob('ClaudeCowork/Claude Context/key_helper.py'), None)
env = os.environ.copy()
env['CLAUDE_PASSPHRASE'] = 'your-passphrase-here'
subprocess.run(['python3', str(kh), 'unlock'], env=env)
PYEOF
```

The `.vault_key` file approach avoids this entirely. Use it.

### Step 6: Deploy key_helper.py

Copy the script below into `ClaudeCowork/Claude Context/key_helper.py`. Before you do, update these three values to match your environment:

```python
VAULT_NAME   = "your-vault-name"          # ← your Key Vault name
TENANT_ID    = "your-tenant-id-here"      # ← your Azure AD tenant ID
```

And in the `_derive_key` function:

```python
salt = b"change_this_to_your_own_salt_value"     # ← pick your own unique salt
```

The salt doesn't need to be secret, but it should be unique to your organization. It prevents two people with the same passphrase from generating the same encryption key. Use something like `b"yourcompany_claude_keystore_v1"`.

The full script is in the appendix at the end of this document.

### Step 7: Bootstrap the Encrypted Store

Run the encrypt command once to create `claude_keys.enc` with your app registration credentials:

```bash
python3 key_helper.py encrypt '{"KV_CLIENT_ID": "your-client-id", "KV_CLIENT_SECRET": "your-client-secret"}'
```

The script reads the passphrase from `.vault_key` automatically. It creates `claude_keys.enc` in the same directory — AES-256-GCM encrypted, readable only by your user (chmod 600).

### Step 8: Test the Full Flow

```bash
python3 key_helper.py unlock
```

You should see output like:

```
✓ Unlocked 12 key(s) from Key Vault → /tmp/.claude_keys.json and ~/.zshenv
  Keys: AZURE_DEVOPS_PAT, KV_CLIENT_ID, KV_CLIENT_SECRET, ZOHO_CLIENT_ID, ...
```

No passphrase typed. No secrets in the terminal. Everything pulled from Key Vault and written to session-scoped files with restricted permissions.

### Step 9: Tell Claude How to Unlock

In your `CLAUDE.md` (or whatever instruction file Claude reads at session start), add the unlock command. Because Cowork's VM assigns a different session path each time, the script path needs to be discovered dynamically with `rglob`:

```markdown
## API Credentials

At session start, unlock keys (auto, no passphrase needed):

python3 << 'PYEOF'
from pathlib import Path
import subprocess
kh = next(Path('/sessions').rglob('ClaudeCowork/Claude Context/key_helper.py'), None)
subprocess.run(['python3', str(kh), 'unlock'])
PYEOF

Then pull latest context from GitHub:

python3 "$(find /sessions -path '*/ClaudeCowork/Claude Context/context_sync.py' 2>/dev/null | head -1)" pull

Run both before any task needing API access or up-to-date context.
```

The `rglob` call scans `/sessions` for the script regardless of what the session directory is named. The passphrase is read from the `.vault_key` file, never from chat. And the context sync pulls any updated instruction files from GitHub so every machine starts from the same state.

---

## What This Gets You

**Secrets never appear in chat.** The passphrase lives in a local file. The bootstrap keys are AES-256 encrypted. All real credentials live in Key Vault. At no point does Claude need you to type a secret.

**Single source of truth.** All credentials are in Azure Key Vault. Rotate a secret there, and the next `unlock` picks it up. No local files to hunt down and update.

**Audit trail.** Azure Key Vault logs every secret read. You know exactly when credentials were accessed and by which identity.

**Least-privilege access.** The app registration can only read secrets (Key Vault Secrets User role). It can't create, delete, or modify them. If the bootstrap credentials are compromised, the attacker can read your vault secrets but can't tamper with them.

**Two output paths for different consumers.** The script writes decrypted keys to two locations: `~/.zshenv` (shell exports that MCP servers and bash scripts read via `source`) and a JSON cache file (that Python scripts read with `json.load()`). Both are chmod 600. The JSON cache goes to `/tmp/.claude_keys.json` by default, but the script includes a fallback to `~/.claude_keys.json` if `/tmp` has stale permissions from a previous session (common in Cowork's VM environment where `/tmp` files can be owned by different session users).

**Session-scoped exposure.** Both output files live inside the ephemeral VM. They don't persist between Claude sessions. `/tmp` is cleared on reboot, and `~/.zshenv` resets with each new VM instance.

**Backward compatible.** The script still accepts a `CLAUDE_PASSPHRASE` env var or `--passphrase` CLI arg if you need those for other workflows. The `.vault_key` file is just the preferred path.

**Context stays in sync across machines.** Because the GitHub PAT lives in Key Vault, unlocking keys also unlocks the ability to sync context files. One `unlock` followed by one `pull` and every machine starts from the same instruction set, the same glossary, the same task list. Edits made on one machine get pushed back and picked up by the next session on any other machine.

---

## Adding a New API

Once the system is running, adding a new API connection takes about 2 minutes:

1. Add the secret to Key Vault: `az keyvault secret set --vault-name your-vault-name --name new-service-api-key --value "the-value"`
2. Run `key_helper.py unlock` — the new key appears automatically as `NEW_SERVICE_API_KEY`
3. Update your Claude instruction files to reference the env var name

No script changes. No re-encryption. No passphrase needed.

---

## Rotating Credentials

When a credential expires or gets compromised:

1. Generate the new credential in the service's dashboard
2. Update the secret in Key Vault (same name, new value): `az keyvault secret set --vault-name your-vault-name --name the-secret-name --value "new-value"`
3. Run `key_helper.py unlock` to pull the updated value
4. Test with a live API call

The bootstrap credentials (client ID and secret for the app registration) are the one exception. If those change, you need to re-run the encrypt command to update `claude_keys.enc`.

---

## Syncing Context Across Machines

Once you have Key Vault working, you've solved the credential problem. But Claude also needs instruction files, context docs, a glossary of internal shorthand, and a task list. If you use Claude on more than one machine (laptop at the office, desktop at home, etc.), those files drift out of sync fast.

The solution: store them in a private GitHub repo and sync at session start.

### What Gets Synced

All `.md` and `.py` files in `Claude Context/`, plus `CLAUDE.md`, `memory/glossary.md`, and `TASKS.md`. The encrypted key file (`claude_keys.enc`) and passphrase file (`.vault_key`) are explicitly excluded from sync. They never leave your local machine.

### The Sync Script

A companion script, `context_sync.py`, lives alongside `key_helper.py` in `Claude Context/`. It supports four commands:

| Command | What It Does |
|---|---|
| `pull` | Download latest files from GitHub. Run at session start. |
| `push` | Upload local changes to GitHub. Run after editing context files. |
| `sync` | Pull first, then push. Full round-trip. |
| `status` | Dry run showing what would change, without touching anything. |

The script uses SHA-256 hashes to compare local and remote files, so it only transfers what's actually changed.

### How It Ties Into Key Vault

The sync script needs a GitHub Personal Access Token to authenticate. That token (`GITHUB_PAT`) is stored in Key Vault like every other credential. The session-start sequence looks like this:

1. `key_helper.py unlock` — decrypts bootstrap keys, authenticates to Key Vault, pulls all secrets (including `GITHUB_PAT`) into the session
2. `context_sync.py pull` — reads `GITHUB_PAT` from the JSON cache that `key_helper.py` just wrote, clones the repo, and copies any updated files into place
3. Claude re-reads any files that changed

After editing context files during a session:

```bash
python3 "$(find /sessions -path '*/ClaudeCowork/Claude Context/context_sync.py' 2>/dev/null | head -1)" push
```

This commits the changes and pushes them to GitHub, so the next session on any machine starts with the latest version.

### Setting Up the Repo

1. Create a private repo (e.g., `your-username/private`)
2. Push your initial context files into it with the same folder structure: `Claude Context/`, `memory/`, `CLAUDE.md`, `TASKS.md`
3. Generate a fine-grained PAT with read/write access to that repo's contents
4. Store the PAT in Key Vault: `az keyvault secret set --vault-name your-vault-name --name github-pat --value "ghp_..."`
5. Update `context_sync.py` with your repo name in the `REPO` constant

After that, every `unlock` makes the PAT available and every `pull` or `push` works without any manual token handling.

### Security Exclusions

The sync script has a hardcoded `NEVER_SYNC` set:

```python
NEVER_SYNC = {"claude_keys.enc", ".vault_key"}
```

These files are excluded from both pull and push operations. Even if they somehow end up in the repo, the script won't copy them down. And it won't push them up from your local machine. The encryption layer and passphrase stay local.

---

## Security Considerations

**What's protected and what isn't:**

- The `.vault_key` passphrase file is the weakest link. Anyone with access to that file and `claude_keys.enc` can decrypt the bootstrap keys and access your vault. Protect it with filesystem permissions (chmod 600) and don't sync it to cloud storage.
- Azure Key Vault access is controlled by Azure AD RBAC. The app registration's client secret has an expiry. Set a calendar reminder.
- The decrypted keys in `/tmp/.claude_keys.json` are accessible to any process running as your user during the session. The file has chmod 600, but that's the extent of the protection.
- If someone gets physical access to your machine while a session is running, they can read the decrypted keys from `/tmp`. This is true of any secrets management approach that loads credentials into memory or the filesystem.

**What never goes in a file — anywhere, ever:**

- Actual token or secret values
- Passwords
- Private keys or certificates
- Anything prefixed with `sk_`, `pk_`, `Bearer `, or similar

If you're unsure whether something is sensitive, put it in the vault. The cost of an extra secret is zero. The cost of an exposed credential is not.

Non-secret config values (org IDs, API domain URLs, app names) can live in context files as plain text. But when in doubt, vault it.

**Things you should not do:**

- Don't commit `.vault_key` or `claude_keys.enc` to git. Add them to `.gitignore`. The `context_sync.py` script has a hardcoded `NEVER_SYNC` set that blocks these files from being pushed even if you forget.
- Don't sync the `keys/` folder to iCloud, Dropbox, or OneDrive.
- Don't grant the app registration more than "Key Vault Secrets User" access.
- Don't store the passphrase and the encrypted file in the same cloud service.
- Don't skip setting an expiry on the app registration client secret.
- Don't store actual credential values in context files that get synced to GitHub. The context files should reference env var names (`ZOHO_CLIENT_ID`), never the values themselves.

---

## Appendix: key_helper.py

Here's the full script. Update `VAULT_NAME` and `TENANT_ID` for your environment. The `VAULT_KEY_F` path should point to wherever you placed your `.vault_key` file.

```python
#!/usr/bin/env python3
"""
key_helper.py — Bootstrap credentials and pull secrets from Azure Key Vault.

The local claude_keys.enc file holds ONLY two bootstrap keys:
  KV_CLIENT_ID     — App registration client ID
  KV_CLIENT_SECRET — App registration client secret

All other credentials live in Azure Key Vault.

Passphrase resolution (checked in order):
  1. CLAUDE_PASSPHRASE env var (if set)
  2. --passphrase CLI argument (if provided)
  3. .vault_key file (auto-read, no chat exposure)
"""

import argparse
import base64
import json
import sys
import urllib.request
import urllib.parse
from pathlib import Path

SCRIPT_DIR   = Path(__file__).resolve().parent
COWORK_ROOT  = SCRIPT_DIR.parent
VAULT_KEY_F  = COWORK_ROOT / "keys" / ".vault_key"
ENC_FILE     = SCRIPT_DIR / "claude_keys.enc"
TMP_KEYS     = Path("/tmp/.claude_keys.json")

# ── UPDATE THESE FOR YOUR ENVIRONMENT ──
VAULT_NAME   = "your-vault-name"                    # ← your Key Vault name
VAULT_URL    = f"https://{VAULT_NAME}.vault.azure.net"
TENANT_ID    = "your-tenant-id-here"                 # ← your Azure AD tenant ID


def _tmp_keys_path() -> Path:
    """Return a writable path for the decrypted keys cache."""
    try:
        if TMP_KEYS.exists():
            TMP_KEYS.write_text(TMP_KEYS.read_text())
        else:
            TMP_KEYS.touch(mode=0o600)
        return TMP_KEYS
    except (PermissionError, OSError):
        pass
    alt = Path.home() / ".claude_keys.json"
    return alt


# ── Crypto helpers ─────────────────────────────────────────────────────

def _derive_key(passphrase: str) -> bytes:
    from hashlib import pbkdf2_hmac
    salt = b"change_this_to_your_own_salt_value"     # ← pick your own salt
    return pbkdf2_hmac("sha256", passphrase.encode(), salt, iterations=200_000)


def _encrypt(data: dict, passphrase: str) -> str:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    import secrets
    key   = _derive_key(passphrase)
    nonce = secrets.token_bytes(12)
    ct    = AESGCM(key).encrypt(nonce, json.dumps(data, indent=2).encode(), None)
    return json.dumps({"nonce": base64.b64encode(nonce).decode(),
                       "ct":    base64.b64encode(ct).decode()})


def _decrypt(passphrase: str) -> dict:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    if not ENC_FILE.exists():
        print(f"ERROR: Bootstrap store not found at {ENC_FILE}", file=sys.stderr)
        print("Run 'encrypt' to initialize it with KV_CLIENT_ID and KV_CLIENT_SECRET.",
              file=sys.stderr)
        sys.exit(1)
    try:
        payload = json.loads(ENC_FILE.read_text())
        key     = _derive_key(passphrase)
        nonce   = base64.b64decode(payload["nonce"])
        ct      = base64.b64decode(payload["ct"])
        return json.loads(AESGCM(key).decrypt(nonce, ct, None).decode())
    except Exception:
        print("ERROR: Decryption failed — wrong passphrase or corrupted file.",
              file=sys.stderr)
        sys.exit(1)


# ── Azure Key Vault helpers ───────────────────────────────────────────

def _kv_token(client_id: str, client_secret: str) -> str:
    data = urllib.parse.urlencode({
        "client_id":     client_id,
        "client_secret": client_secret,
        "grant_type":    "client_credentials",
        "scope":         "https://vault.azure.net/.default",
    }).encode()
    req = urllib.request.Request(
        f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token",
        data=data, method="POST"
    )
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())["access_token"]
    except urllib.error.HTTPError as e:
        print(f"ERROR: Could not get Key Vault token: {e.read().decode()[:200]}",
              file=sys.stderr)
        sys.exit(1)


def _kv_list_secrets(token: str) -> list:
    req = urllib.request.Request(
        f"{VAULT_URL}/secrets?api-version=7.4",
        headers={"Authorization": f"Bearer {token}"}
    )
    with urllib.request.urlopen(req) as r:
        items = json.loads(r.read()).get("value", [])
    return [item["id"].split("/")[-1] for item in items]


def _kv_get_secret(name: str, token: str) -> str:
    req = urllib.request.Request(
        f"{VAULT_URL}/secrets/{name}?api-version=7.4",
        headers={"Authorization": f"Bearer {token}"}
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())["value"]


# ── Shell export helper ───────────────────────────────────────────────

def _write_zshenv(keys: dict):
    zshenv = Path.home() / ".zshenv"
    lines  = zshenv.read_text().splitlines() if zshenv.exists() else []
    start  = "# --- claude-keystore-begin ---"
    end    = "# --- claude-keystore-end ---"
    filtered, inside = [], False
    for line in lines:
        if line.strip() == start:   inside = True
        elif line.strip() == end:   inside = False
        elif not inside:            filtered.append(line)
    exports = [start] + [f'export {k}="{v}"' for k, v in keys.items()] + [end]
    zshenv.write_text("\n".join(filtered + exports) + "\n")
    zshenv.chmod(0o600)


# ── Commands ──────────────────────────────────────────────────────────

def cmd_unlock(passphrase: str):
    bootstrap     = _decrypt(passphrase)
    client_id     = bootstrap.get("KV_CLIENT_ID")
    client_secret = bootstrap.get("KV_CLIENT_SECRET")
    if not client_id or not client_secret:
        print("ERROR: KV_CLIENT_ID or KV_CLIENT_SECRET missing from bootstrap store.",
              file=sys.stderr)
        sys.exit(1)
    token = _kv_token(client_id, client_secret)
    secret_names = _kv_list_secrets(token)
    all_keys, errors = {}, []
    for name in secret_names:
        env_name = name.replace("-", "_").upper()
        try:
            all_keys[env_name] = _kv_get_secret(name, token)
        except Exception as e:
            errors.append(f"{name}: {e}")
    all_keys["KV_CLIENT_ID"]     = client_id
    all_keys["KV_CLIENT_SECRET"] = client_secret
    keys_path = _tmp_keys_path()
    keys_path.write_text(json.dumps(all_keys, indent=2))
    keys_path.chmod(0o600)
    _write_zshenv(all_keys)
    print(f"Unlocked {len(all_keys)} key(s) from Key Vault")
    print(f"  Keys: {', '.join(sorted(all_keys.keys()))}")
    if errors:
        print(f"  Warnings: {errors}", file=sys.stderr)


def cmd_encrypt(new_json: str, passphrase: str):
    new_data = json.loads(new_json)
    existing = _decrypt(passphrase) if ENC_FILE.exists() else {}
    merged   = {**existing, **new_data}
    ENC_FILE.write_text(_encrypt(merged, passphrase))
    ENC_FILE.chmod(0o600)
    added   = set(new_data.keys()) - set(existing.keys())
    updated = set(new_data.keys()) & set(existing.keys())
    print(f"Saved to {ENC_FILE}")
    if added:   print(f"  Added:   {', '.join(sorted(added))}")
    if updated: print(f"  Updated: {', '.join(sorted(updated))}")
    print(f"  Total bootstrap keys: {len(merged)}")


def cmd_list(passphrase: str):
    keys = _decrypt(passphrase)
    print(f"Bootstrap keys in local store ({len(keys)} total):")
    for k in sorted(keys.keys()):
        print(f"  {k}")


# ── Main ──────────────────────────────────────────────────────────────

def _resolve_passphrase(args_passphrase: str) -> str:
    import os
    env_pp = os.environ.get("CLAUDE_PASSPHRASE")
    if env_pp:
        return env_pp
    if args_passphrase:
        return args_passphrase
    if VAULT_KEY_F.exists():
        pp = VAULT_KEY_F.read_text().strip()
        if pp:
            return pp
    return ""


def main():
    parser = argparse.ArgumentParser(
        description="Claude Key Vault bootstrap",
        epilog="Place passphrase in keys/.vault_key for auto-unlock."
    )
    sub = parser.add_subparsers(dest="command")
    p_unlock = sub.add_parser("unlock", help="Pull all secrets from Key Vault")
    p_unlock.add_argument("--passphrase", default="")
    p_enc = sub.add_parser("encrypt", help="Add/update bootstrap keys locally")
    p_enc.add_argument("json", help='JSON string e.g. \'{"KV_CLIENT_ID": "..."}\'')
    p_enc.add_argument("--passphrase", default="")
    p_list = sub.add_parser("list", help="Show bootstrap key names")
    p_list.add_argument("--passphrase", default="")
    args = parser.parse_args()
    pp   = _resolve_passphrase(getattr(args, "passphrase", ""))
    if not pp:
        print("ERROR: No passphrase found. Checked:", file=sys.stderr)
        print("  1. CLAUDE_PASSPHRASE env var", file=sys.stderr)
        print("  2. --passphrase CLI argument", file=sys.stderr)
        print(f"  3. {VAULT_KEY_F}", file=sys.stderr)
        sys.exit(1)
    if args.command == "unlock":    cmd_unlock(pp)
    elif args.command == "encrypt": cmd_encrypt(args.json, pp)
    elif args.command == "list":    cmd_list(pp)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
```

**Dependency:** The script needs the `cryptography` package. Install it with `pip install cryptography`.

---

## Prerequisites Checklist

Before you start, make sure you have:

- [ ] An Azure subscription with permission to create resources
- [ ] Azure CLI installed (`az --version`)
- [ ] Python 3.8+ with the `cryptography` package
- [ ] Claude desktop app with Cowork mode (or Claude Code)
- [ ] A strong passphrase you won't forget
- [ ] A private GitHub repo for context sync (optional but recommended if you use multiple machines)
- [ ] A fine-grained GitHub PAT with repo contents read/write scope (for context sync)

---

## Quick Reference

| Task | Command |
|---|---|
| Unlock all keys | `python3 key_helper.py unlock` |
| Add/update bootstrap keys | `python3 key_helper.py encrypt '{"KEY": "value"}'` |
| List bootstrap key names | `python3 key_helper.py list` |
| Add a new API secret | `az keyvault secret set --vault-name X --name Y --value Z` |
| Rotate a secret | Update in Azure Portal or CLI, then run `unlock` |
| Pull latest context from GitHub | `python3 context_sync.py pull` |
| Push context changes to GitHub | `python3 context_sync.py push` |
| Check sync status (dry run) | `python3 context_sync.py status` |

---

*Built and tested with Claude Cowork + Azure Key Vault. Last updated March 8, 2026.*


---

## Corrections Log

*Tracks issues found when following this file's instructions. Entries are added when a discrepancy is discovered and a fix is applied or proposed.*

| Date | What Failed | Root Cause | Fix Applied | ERRORS.md Ref |
|------|-------------|------------|-------------|---------------|

**Notes:**
<!-- Per-entry context that doesn't fit in the table. Format: "YYYY-MM-DD: [explanation]" -->
