---
type: context-file
summary: "Issue investigation protocol — 7-phase process covering architecture load, App Insights KQL, Cosmos/database state queries, SQL config queries (Desktop Commander), code tracing, hypothesis formation, and reproduction."
tags: [coding, investigation, debugging, app-insights, cosmos, sql]
---

# Issue Investigation Protocol

> **When to use this file:** Any time an issue is brought to investigate. Run every phase in order before forming a theory. Do not skip to a hypothesis from a surface error message — the root cause is almost always visible in one of the data layers once queried.

> **Cross-references:** Your logging standards file for LogUid/correlation ID architecture. `coding-index.md` for the MOC.

---

## Prerequisites

<!-- CUSTOMIZE: Replace key names below with your project's actual Azure Key Vault secret names. -->

```python
import json
from pathlib import Path

keys = json.load(open(next(Path('/sessions').rglob('.claude_keys.json'), None)))

required = [
    '[YOUR_PROJECT]_DEV_APP_APPINSIGHTS_APP_ID',   # App Insights Application ID (GUID) — dev
    '[YOUR_PROJECT]_PRD_APP_APPINSIGHTS_APP_ID',   # App Insights Application ID (GUID) — prd
    '[YOUR_PROJECT]_DEV_COSMOS_READONLY_CONNSTR',  # Cosmos read-only connection string — dev
    '[YOUR_PROJECT]_PRD_COSMOS_READONLY_CONNSTR',  # Cosmos read-only connection string — prd
    '[YOUR_PROJECT]_KV_CLIENT_ID',                  # Service principal client ID
    '[YOUR_PROJECT]_KV_CLIENT_SECRET',              # Service principal secret
]
missing = [k for k in required if not keys.get(k)]
print("Missing secrets:", missing if missing else "None — all present")
```

**Access requirements (one-time setup per environment):**
- Service principal has **Monitoring Reader** role on the App Insights resource
- Service principal is in the **`{env}-sqldb-user` Entra group** (or equivalent SQL role)
- Cosmos read-only connection strings are in Key Vault

**Important — App Insights Application ID format:** The `Application ID` is a GUID (`xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`), found in Azure Portal: App Insights → Configure → API Access. It is NOT the instrumentation key and NOT an API key. Storing an API key in this secret will cause 403 errors; storing the wrong GUID will cause 404 errors.

---

## Phase 1 — Load Architecture Context

Before querying anything, establish which resources the affected bounded context uses.

1. Read the repo's master architecture doc (e.g., `docs/Azure-Environment-Architecture.md`).
2. Read the bounded context's architecture doc (e.g., `docs/my-feature/Architecture.md`).
3. From those two docs, confirm:
   - Which function app or web app is the entry point (`cloud_RoleName` in App Insights)
   - Which Cosmos database and container hold the relevant state
   - Which SQL schema and tables hold the config
   - Whether the issue is dev or prod (determines `ENV` in all snippets below)

<!-- CUSTOMIZE: Adapt this naming pattern to match your Azure resource conventions. -->
```
App Insights:  {product}-{env}-{scope}-appinsights
Cosmos:        {product}-{env}-shared-cosmos  →  {DatabaseName}  →  {ContainerName}
SQL Server:    {product}-{env}-{scope}-sqlsrv.database.windows.net
SQL Database:  {product}-{env}-{scope}-sqldb
```

---

## Phase 2 — App Insights

**What you're looking for:** The full exception with stack trace and all context. A correlation ID (LogUid) in a user-visible error message is a direct pointer to the log entry.

### Setup (run once per session)

<!-- CUSTOMIZE: Replace TENANT_ID, key names, and key name format with your project's values. -->

```python
import json, requests
from pathlib import Path

keys = json.load(open(next(Path('/sessions').rglob('.claude_keys.json'), None)))
TENANT_ID = "[YOUR-AZURE-TENANT-ID]"

ai_token = requests.post(
    f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token",
    data={
        'grant_type': 'client_credentials',
        'client_id': keys['[YOUR_PROJECT]_KV_CLIENT_ID'],
        'client_secret': keys['[YOUR_PROJECT]_KV_CLIENT_SECRET'],
        'scope': 'https://api.applicationinsights.io/.default'
    }
).json()['access_token']

ENV = 'dev'  # or 'prd'
APP_ID = keys[f'[YOUR_PROJECT]_{ENV.upper()}_APP_APPINSIGHTS_APP_ID']
AI_URL = f"https://api.applicationinsights.io/v1/apps/{APP_ID}/query"

def kql(query, timespan='P1D'):
    resp = requests.post(AI_URL,
        headers={'Authorization': f'Bearer {ai_token}', 'Content-Type': 'application/json'},
        json={'query': query, 'timespan': timespan}
    )
    resp.raise_for_status()
    cols = [c['name'] for c in resp.json()['tables'][0]['columns']]
    rows = resp.json()['tables'][0]['rows']
    return [dict(zip(cols, r)) for r in rows]
```

### Query by correlation ID / LogUid (most direct path from a user error)

When a user-visible error message contains a GUID prefix, that GUID maps directly to a log entry:

```python
LOG_UID = 'f3f19b09-45d8-4c27-b099-edaca51c21a5'  # replace with actual UID

results = kql(f"""
union traces, exceptions
| where customDimensions["logUid"] == '{LOG_UID}'
| project timestamp, itemType, message, outerMessage, details, customDimensions
| order by timestamp asc
""")
for r in results:
    print(r['timestamp'], r['itemType'])
    print(r.get('message') or r.get('outerMessage'))
    if r.get('details'):
        print(r['details'][:2000])
    print()
```

### Query recent exceptions for a specific service

```python
# cloud_RoleName is the Azure resource name (function app or web app)
ROLE = '[your-resource-name]'  # from Architecture.md

results = kql(f"""
exceptions
| where cloud_RoleName == '{ROLE}'
| where timestamp > ago(4h)
| order by timestamp desc
| project timestamp, problemId, outerMessage,
          customDimensions["logUid"], customDimensions["Category"]
""")
```

### Query by category (service class name)

```python
results = kql("""
exceptions
| where customDimensions["Category"] has "MyServiceClass"
| where timestamp > ago(24h)
| order by timestamp desc
| project timestamp, outerMessage, customDimensions["Category"],
          customDimensions["logUid"]
""")
```

### Breadcrumb trace around a known exception timestamp

```python
AROUND_TS = '2026-01-15T14:23:00Z'  # replace

results = kql(f"""
union traces, exceptions
| where cloud_RoleName == '{ROLE}'
| where timestamp between(
    datetime('{AROUND_TS}') - 2m .. datetime('{AROUND_TS}') + 2m
  )
| order by timestamp asc
| project timestamp, itemType, message, outerMessage, customDimensions["Category"]
""")
```

---

## Phase 3 — Cosmos DB (or your document database)

**What you're looking for:** The actual document state at the time of the issue. Stale locks, missing summaries, or malformed results show up here directly.

<!-- CUSTOMIZE: Replace database/container names and partition key field with your project's values. -->

```python
from azure.cosmos import CosmosClient

CONN_STR = keys[f'[YOUR_PROJECT]_{ENV.upper()}_COSMOS_READONLY_CONNSTR']
cosmos = CosmosClient.from_connection_string(CONN_STR)
db = cosmos.get_database_client('[YourDatabaseName]')
container = db.get_container_client('[YourContainerName]')
```

### Query recent documents (partition-scoped)

Always supply the partition key to avoid cross-partition fan-out:

```python
PARTITION_VALUE = 'your-partition-key-value'

items = list(container.query_items(
    query="SELECT * FROM c WHERE c.[partitionField] = @id ORDER BY c._ts DESC OFFSET 0 LIMIT 20",
    parameters=[{"name": "@id", "value": PARTITION_VALUE}],
    partition_key=PARTITION_VALUE
))
for item in items:
    import datetime
    ts = datetime.datetime.utcfromtimestamp(item['_ts']).strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{ts}] type={item.get('type','N/A')}  id={item['id']}")
```

### Check for stale locks

```python
locks = list(container.query_items(
    query="SELECT * FROM c WHERE c.type = 'LockDocument' AND c.[partitionField] = @id",
    parameters=[{"name": "@id", "value": PARTITION_VALUE}],
    partition_key=PARTITION_VALUE
))
print(f"Active locks: {len(locks)}")
for lock in locks:
    print(lock)
```

### Find the last run summary

```python
summaries = list(container.query_items(
    query="""SELECT TOP 1 * FROM c
             WHERE c.type = 'RunSummaryDocument'
             AND c.[partitionField] = @id
             ORDER BY c._ts DESC""",
    parameters=[{"name": "@id", "value": PARTITION_VALUE}],
    partition_key=PARTITION_VALUE
))
if summaries:
    s = summaries[0]
    print(f"Status: {s.get('status')}  Suspended: {s.get('isSuspended')}")
    print(f"Failures: {s.get('consecutiveFailureCount')}")
```

---

## Phase 4 — SQL Config

**What you're looking for:** Misconfigured rules, suspended records, or missing config that explains the observed behavior.

SQL queries run via Desktop Commander on the Mac because the VM sandbox lacks ODBC drivers.

### Prerequisite

```bash
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew install msodbcsql18
```

### Script builder (run in VM)

<!-- CUSTOMIZE: Replace server/database names and the QUERY string with your project's values. -->

```python
import json, os
from pathlib import Path

keys = json.load(open(next(Path('/sessions').rglob('.claude_keys.json'), None)))
COWORK = str(next(Path('/sessions').rglob('ClaudeCowork'), None))
SCRIPT_PATH = f"{COWORK}/.vm-workspace/tmp/sql_investigate.py"
os.makedirs(f"{COWORK}/.vm-workspace/tmp", exist_ok=True)

ENV = 'dev'
QUERY = "SELECT TOP 20 * FROM [yourSchema].[YourTable] WHERE IsActive = 1"

script = f"""
import pyodbc

conn = pyodbc.connect(
    'DRIVER={{ODBC Driver 18 for SQL Server}};'
    'SERVER=[your-project]-{ENV}-sqlsrv.database.windows.net;'
    'DATABASE=[your-project]-{ENV}-sqldb;'
    'Authentication=ActiveDirectoryServicePrincipal;'
    'UID={keys["[YOUR_PROJECT]_KV_CLIENT_ID"]};'
    'PWD={keys["[YOUR_PROJECT]_KV_CLIENT_SECRET"]}'
)
cursor = conn.cursor()
cursor.execute('''{QUERY}''')
cols = [d[0] for d in cursor.description]
for row in cursor.fetchall():
    print(dict(zip(cols, row)))
conn.close()
"""

Path(SCRIPT_PATH).write_text(script)
print("Script written — run via Desktop Commander")
```

---

## Phase 5 — Code Tracing

With real data from Phases 2–4, trace the code path the failure traveled.

1. From the App Insights `Category` dimension, identify the exact class and method that threw.
2. Read that file. Follow the call chain up from the throw.
3. Cross-reference: does the Cosmos state match what the code would expect? Does SQL config explain why a rule matched or didn't?

Look for: early returns, null checks, exception swallows, or conditions that silently skip processing.

---

## Phase 6 — Form a Hypothesis

Write one sentence for each before proceeding:

1. **What failed:** The specific method and exception.
2. **Why it failed:** The state or config condition that triggered it.
3. **When it started:** Approximate timestamp; any config change before that time?
4. **Blast radius:** Is this one record or all records? One environment or both?

Do not proceed to Phase 7 until all four are answerable without re-reading.

---

## Phase 7 — Reproduce

**For HTTP endpoint failures:**

```python
import requests

# <!-- CUSTOMIZE: Replace base URL pattern with your project's naming convention -->
API_BASE = f"https://[your-project]-{ENV}-appsrv-web.azurewebsites.net"
resp = requests.get(f"{API_BASE}/api/[your-endpoint]",
    headers={'Authorization': f'Bearer {your_token}'}
)
print(resp.status_code, resp.text[:500])
```

**Watch for new exceptions after triggering:**

```python
import time

def watch_exceptions(role, seconds=60):
    for _ in range(seconds // 10):
        time.sleep(10)
        results = kql(f"""
            exceptions
            | where cloud_RoleName == '{role}'
            | where timestamp > ago(2m)
            | order by timestamp desc
            | project timestamp, outerMessage, customDimensions["logUid"]
        """)
        if results:
            print(f"New exception: {results[0]['outerMessage']}")
            return results[0]
    print("No new exceptions in window")
```

---

## Quick Reference — Vault Secrets

<!-- CUSTOMIZE: Replace with your project's actual Key Vault secret names. -->

| Secret | Used for |
|--------|----------|
| `[YOUR_PROJECT]_DEV_APP_APPINSIGHTS_APP_ID` | App Insights Application ID GUID — dev |
| `[YOUR_PROJECT]_PRD_APP_APPINSIGHTS_APP_ID` | App Insights Application ID GUID — prd |
| `[YOUR_PROJECT]_DEV_COSMOS_READONLY_CONNSTR` | Cosmos read-only connection string — dev |
| `[YOUR_PROJECT]_PRD_COSMOS_READONLY_CONNSTR` | Cosmos read-only connection string — prd |
| `[YOUR_PROJECT]_KV_CLIENT_ID` | Service principal client ID |
| `[YOUR_PROJECT]_KV_CLIENT_SECRET` | Service principal secret |

---

## Corrections Log

*Tracks issues found when following this file's instructions.*

| Date | What Failed | Root Cause | Fix Applied | ERRORS.md Ref |
|------|-------------|------------|-------------|---------------|

**Notes:**
<!-- Per-entry context. Format: "YYYY-MM-DD: [explanation]" -->
