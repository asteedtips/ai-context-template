# [Service Name] API Configuration

<!--
  TEMPLATE: Copy this file for each API integration you set up.
  Rename it to match the service (e.g., zoho-api.md, microsoft-graph-api.md, hubspot-api.md).

  This template covers the standard OAuth 2.0 pattern. Adapt for API key auth,
  Basic auth, or other mechanisms as needed.
-->

> **Before preparing any documentation using this data, read `Claude Context/best-practices-creation.md`** — it governs output formats, diagram standards, naming conventions, and writing rules for all deliverables.

Use this file as persistent context whenever you need to access [Service Name] data.

## Authentication

<!--
  FILL IN: Document the auth mechanism for this API.
  Common patterns: OAuth 2.0 (refresh token), API key, Basic auth, JWT
-->

> Credentials are stored in your secret store (see `security-practices.md`). Never write actual values in this file.

| Field | Env Var After Unlock |
|-------|---------------------|
| **Client ID** | `SERVICE_CLIENT_ID` |
| **Client Secret** | `SERVICE_CLIENT_SECRET` |
| **Refresh Token** | `SERVICE_REFRESH_TOKEN` |
| **Scopes** | `[list scopes granted]` |
| **API Domain** | `https://api.service.com` |
| **Auth Domain** | `https://auth.service.com` |

---

## Step 0 — Load Credentials

Keys must be unlocked first. Run the unlock sequence from `security-practices.md` if your session cache doesn't exist yet.

Then load credentials into shell variables:

```bash
SERVICE_CLIENT_ID=$(python3 -c "import json; print(json.load(open('/tmp/.secrets.json'))['SERVICE_CLIENT_ID'])")
SERVICE_CLIENT_SECRET=$(python3 -c "import json; print(json.load(open('/tmp/.secrets.json'))['SERVICE_CLIENT_SECRET'])")
SERVICE_REFRESH_TOKEN=$(python3 -c "import json; print(json.load(open('/tmp/.secrets.json'))['SERVICE_REFRESH_TOKEN'])")
```

---

## Step 1 — Get a Fresh Access Token

Before every API session, refresh the token:

```bash
curl -s -X POST "https://auth.service.com/oauth/token" \
  -d "grant_type=refresh_token" \
  -d "client_id=${SERVICE_CLIENT_ID}" \
  -d "client_secret=${SERVICE_CLIENT_SECRET}" \
  -d "refresh_token=${SERVICE_REFRESH_TOKEN}"
```

Extract `access_token` from the JSON response and use it in all subsequent requests:
```
Authorization: Bearer <access_token>
```

---

## Step 2 — Common API Calls

<!--
  FILL IN: Document the API calls you use most frequently.
  Include the full curl command with placeholders for tokens and IDs.
  Group by function (e.g., Contacts, Deals, Tickets, Files).
-->

### Example: List Records
```bash
curl -s "https://api.service.com/v1/records?per_page=200" \
  -H "Authorization: Bearer <access_token>"
```

### Example: Search
```bash
curl -s "https://api.service.com/v1/records/search?query=<search_term>" \
  -H "Authorization: Bearer <access_token>"
```

### Example: Get a Specific Record
```bash
curl -s "https://api.service.com/v1/records/<record_id>" \
  -H "Authorization: Bearer <access_token>"
```

---

## Pagination

<!--
  FILL IN: Document how this API handles pagination.
  Common patterns: page/per_page, offset/limit, cursor-based, @odata.nextLink
-->

---

## Behavior Rules

<!--
  FILL IN: Define what the AI agent is and isn't allowed to do with this API.

  Examples:
  - Reading data: permitted
  - Creating drafts: permitted
  - Sending emails: NOT permitted without explicit amendment
  - Deleting records: NOT permitted
  - Modifying permissions: NOT permitted
-->

---

## Notes

<!--
  FILL IN: Any gotchas, rate limits, expiry dates, or quirks.
  Examples:
  - Refresh token does not expire as long as the app is active
  - Rate limit: 5,000 calls/day
  - Client secret expires [DATE] — set a reminder to rotate
  - API version: v3
-->

---

*Last updated: [DATE]*
