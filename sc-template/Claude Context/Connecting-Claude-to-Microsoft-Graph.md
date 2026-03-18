# Connecting Claude to Microsoft Graph API

**A practical guide to giving Claude controlled access to Outlook, Calendar, SharePoint, and OneDrive.**

This is a companion to [Securing Claude's API Keys with Azure Key Vault](./Securing-Claude-API-Keys-With-Azure-Key-Vault.md). That guide covers how to store and manage credentials securely. This one covers how to set up the Microsoft Graph connection itself, including the decisions you need to make about what Claude should and shouldn't be allowed to do.

---

## What Microsoft Graph Gets You

Microsoft Graph is a single API that covers most of Microsoft 365. Once connected, Claude can:

- Read and draft emails in Outlook
- Check your calendar and upcoming meetings
- Browse SharePoint sites and document libraries
- Download files from SharePoint or OneDrive
- Search across your Microsoft 365 content

The catch: Graph uses OAuth 2.0 with granular scopes, so you control exactly what Claude can access. Getting the scopes right matters. Too narrow and Claude can't do the work. Too broad and you've handed over more access than you intended.

---

## Before You Start: Decisions to Make

Don't skip this section. These choices shape your entire setup. Work through each one before touching Azure Portal.

### Decision 1: Email Access Level

| Level | What Claude Can Do | Scopes Needed |
|-------|-------------------|---------------|
| **Read-only** | Read inbox, search messages, view full email bodies | `Mail.Read` |
| **Read + Draft** | Everything above, plus create and edit draft emails (never sends) | `Mail.Read`, `Mail.ReadWrite` |
| **Read + Draft + Send** | Everything above, plus send email as you | `Mail.Read`, `Mail.ReadWrite`, `Mail.Send` |

**Our recommendation:** Start with Read + Draft. Claude creates drafts for your review. You click Send yourself. This gives you a human checkpoint on every outgoing message without limiting Claude's ability to compose.

If you go with Read + Draft + Send, add a behavior rule in your Claude instruction file that blocks sending unless you explicitly approve each message. The scope grants the *capability*; your instruction file controls the *policy*.

### Decision 2: Calendar Access Level

| Level | What Claude Can Do | Scopes Needed |
|-------|-------------------|---------------|
| **Read-only** | View events, check availability, pull meeting details | `Calendars.Read` |
| **Read + Write** | Everything above, plus create/update/cancel events | `Calendars.Read`, `Calendars.ReadWrite` |

**Our recommendation:** Read-only unless you have a specific use case for Claude creating meetings. Calendar mistakes (double-booking, wrong attendees, wrong time zones) are harder to undo than email drafts.

### Decision 3: SharePoint / OneDrive Access Level

| Level | What Claude Can Do | Scopes Needed |
|-------|-------------------|---------------|
| **Read-only** | Browse sites, list files, download documents | `Sites.Read.All`, `Files.Read.All` |
| **Read + Write** | Everything above, plus upload, modify, and organize files | `Sites.Read.All`, `Files.Read.All`, `Files.ReadWrite.All` |

**Our recommendation:** Start read-only. If you need Claude to upload files to specific folders (processed reports, generated documents), grant write access but restrict it with behavior rules that limit *where* Claude can write. More on that below.

### Decision 4: Behavior Rules (The Part Most People Skip)

Scopes are binary: on or off. Behavior rules give you finer control. They live in your Claude instruction file (CLAUDE.md or equivalent) and tell Claude what it's allowed to do *within* the permissions you've granted.

Think through these:

**Email behavior rules to consider:**

- Can Claude send email, or only draft? (We recommend draft-only even if you grant `Mail.Send`)
- Should Claude confirm recipient and subject before saving a draft?
- Are there addresses Claude should never email (competitors, legal, press)?
- Can Claude delete or move messages, or only read them?

**Calendar behavior rules to consider:**

- Can Claude create events, or only read them?
- Should Claude confirm details before creating/modifying any event?
- Can Claude accept or decline meeting invitations on your behalf?

**SharePoint behavior rules to consider:**

- Can Claude upload files, or only download?
- If uploads are allowed, which folders? Restrict to specific paths.
- Can Claude modify existing files, or only add new ones?
- Can Claude delete anything? (We recommend never.)
- Are there specific files Claude should auto-download without asking? (Pricing sheets, templates, logos — things used repeatedly in workflows.)

**General rules to consider:**

- Should Claude ask for confirmation before any write operation?
- Are there specific folders or mailboxes that are off-limits entirely?
- Should Claude log or report what it accessed during a session?

Write these rules down. Put them in your instruction file. Claude follows what you write, but it can't follow rules that don't exist.

---

## Step-by-Step Setup

### Step 1: Register an App in Azure AD

1. Go to **Azure Portal → Microsoft Entra ID → App registrations → New registration**
2. Name it something descriptive (e.g., `Claude-GraphReader` or `Claude-M365Access`)
3. Under **Supported account types**, select "Accounts in this organizational directory only" (single tenant)
4. Set the **Redirect URI**:
   - Platform: **Mobile and desktop applications**
   - URI: `https://login.microsoftonline.com/common/oauth2/nativeclient`
5. Click **Register**

After registration, copy these three values — you'll need them:

| Value | Where to Find It |
|-------|-----------------|
| **Application (client) ID** | App registration overview page |
| **Directory (tenant) ID** | App registration overview page |
| **Client Secret** | Certificates & secrets → New client secret |

**Set a calendar reminder for the client secret expiry.** 12-24 months is typical. When it expires, Claude loses access until you rotate it.

### Step 2: Configure API Permissions

1. In your app registration, go to **API permissions → Add a permission → Microsoft Graph → Delegated permissions**
2. Add the scopes you decided on in the planning section above
3. Click **Grant admin consent** (requires admin role in your tenant)

**Minimum recommended scopes:**

```
offline_access          — Required for refresh tokens
User.Read               — Read your own profile
Mail.Read               — Read email
Mail.ReadWrite          — Create/manage drafts
Calendars.Read          — Read calendar
Sites.Read.All          — Read SharePoint sites
Files.Read.All          — Read files
```

**Add these only if you decided you need them:**

```
Mail.Send               — Send email as you
Calendars.ReadWrite     — Create/modify calendar events
Files.ReadWrite.All     — Upload/modify files in SharePoint/OneDrive
```

The `offline_access` scope is required. Without it, you won't get a refresh token, which means you'd need to re-authenticate every 60 minutes.

### Step 3: Get Your Initial Refresh Token

This is the one manual step. You need to complete an OAuth consent flow in a browser to get the first refresh token. After that, Claude uses the refresh token to get new access tokens automatically.

**Option A: Browser-based flow (simplest)**

1. Open this URL in your browser (replace the placeholders):

```
https://login.microsoftonline.com/<your-tenant-id>/oauth2/v2.0/authorize?client_id=<your-client-id>&response_type=code&redirect_uri=https://login.microsoftonline.com/common/oauth2/nativeclient&scope=offline_access Mail.Read Mail.ReadWrite Mail.Send Calendars.Read Calendars.ReadWrite User.Read Sites.Read.All Files.Read.All Files.ReadWrite.All&response_mode=query
```

2. Sign in and consent to the permissions
3. You'll be redirected to a URL like:
   ```
   https://login.microsoftonline.com/common/oauth2/nativeclient?code=0.AAAA...
   ```
4. Copy the `code` parameter value from the URL

5. Exchange the code for tokens:

```bash
curl -s -X POST "https://login.microsoftonline.com/<your-tenant-id>/oauth2/v2.0/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=<your-client-id>" \
  -d "client_secret=<your-client-secret>" \
  -d "code=<the-code-you-copied>" \
  -d "grant_type=authorization_code" \
  -d "redirect_uri=https://login.microsoftonline.com/common/oauth2/nativeclient" \
  -d "scope=offline_access Mail.Read Mail.ReadWrite Mail.Send Calendars.Read Calendars.ReadWrite User.Read Sites.Read.All Files.Read.All Files.ReadWrite.All"
```

6. The response includes both an `access_token` and a `refresh_token`. Copy the **refresh token** — that's what you'll store.

**The authorization code expires in about 10 minutes.** Don't wait. Exchange it immediately.

### Step 4: Store the Credentials

If you're using the Azure Key Vault system from the companion guide, add these secrets:

```bash
az keyvault secret set --vault-name your-vault-name --name ms-graph-client-id --value "<your-client-id>"
az keyvault secret set --vault-name your-vault-name --name ms-graph-client-secret --value "<your-client-secret>"
az keyvault secret set --vault-name your-vault-name --name ms-graph-tenant-id --value "<your-tenant-id>"
az keyvault secret set --vault-name your-vault-name --name ms-graph-refresh-token --value "<your-refresh-token>"
```

After running `key_helper.py unlock`, these become available as environment variables:

| Key Vault Secret | Env Var |
|-----------------|---------|
| `ms-graph-client-id` | `MS_GRAPH_CLIENT_ID` |
| `ms-graph-client-secret` | `MS_GRAPH_CLIENT_SECRET` |
| `ms-graph-tenant-id` | `MS_GRAPH_TENANT_ID` |
| `ms-graph-refresh-token` | `MS_GRAPH_REFRESH_TOKEN` |

If you're not using Key Vault, store these however your credential system works — but don't put the actual values in any file that Claude can read or that syncs to the cloud.

### Step 5: Tell Claude How to Authenticate

Add this to your Claude instruction file. Claude runs this at the start of any session that needs Graph access.

**Load credentials from your key store:**

```bash
MS_CLIENT_ID=$(python3 -c "import json; print(json.load(open('/tmp/.claude_keys.json'))['MS_GRAPH_CLIENT_ID'])")
MS_CLIENT_SECRET=$(python3 -c "import json; print(json.load(open('/tmp/.claude_keys.json'))['MS_GRAPH_CLIENT_SECRET'])")
MS_TENANT_ID=$(python3 -c "import json; print(json.load(open('/tmp/.claude_keys.json'))['MS_GRAPH_TENANT_ID'])")
MS_REFRESH_TOKEN=$(python3 -c "import json; print(json.load(open('/tmp/.claude_keys.json'))['MS_GRAPH_REFRESH_TOKEN'])")
```

**Get a fresh access token:**

```bash
curl -s -X POST "https://login.microsoftonline.com/${MS_TENANT_ID}/oauth2/v2.0/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=${MS_CLIENT_ID}" \
  -d "client_secret=${MS_CLIENT_SECRET}" \
  -d "refresh_token=${MS_REFRESH_TOKEN}" \
  -d "grant_type=refresh_token" \
  -d "scope=offline_access Mail.Read Mail.ReadWrite Calendars.Read User.Read Sites.Read.All Files.Read.All"
```

Extract the `access_token` from the JSON response and use it in all subsequent API calls:

```
Authorization: Bearer <access_token>
```

Access tokens expire after 60 minutes. If a call fails with a 401, get a fresh token and retry.

---

## Common API Patterns

Once authenticated, here are the calls you'll use most often. All examples use `<access_token>` as a placeholder.

### User Profile

```bash
curl -s "https://graph.microsoft.com/v1.0/me" \
  -H "Authorization: Bearer <access_token>"
```

### Email — Read Inbox

```bash
curl -s "https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messages?\$top=25&\$orderby=receivedDateTime desc&\$select=subject,from,receivedDateTime,isRead,bodyPreview" \
  -H "Authorization: Bearer <access_token>"
```

### Email — Get Unread Messages

```bash
curl -s "https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messages?\$filter=isRead eq false&\$top=25&\$orderby=receivedDateTime desc&\$select=subject,from,receivedDateTime,bodyPreview" \
  -H "Authorization: Bearer <access_token>"
```

### Email — Read Full Message

```bash
curl -s "https://graph.microsoft.com/v1.0/me/messages/<message_id>?\$select=subject,from,toRecipients,body,receivedDateTime" \
  -H "Authorization: Bearer <access_token>"
```

### Email — Search

```bash
curl -s "https://graph.microsoft.com/v1.0/me/messages?\$search=\"<search_term>\"&\$top=20" \
  -H "Authorization: Bearer <access_token>"
```

### Email — Create Draft

```bash
curl -s -X POST "https://graph.microsoft.com/v1.0/me/messages" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Subject here",
    "body": { "contentType": "Text", "content": "Body here" },
    "toRecipients": [{ "emailAddress": { "address": "recipient@example.com" } }]
  }'
```

This saves to Drafts without sending. Claude can compose; you review and send.

### Email — Send

```bash
curl -s -X POST "https://graph.microsoft.com/v1.0/me/sendMail" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "subject": "Subject here",
      "body": { "contentType": "Text", "content": "Body here" },
      "toRecipients": [{ "emailAddress": { "address": "recipient@example.com" } }]
    }
  }'
```

### Calendar — Today's Events

```bash
TODAY=$(date -u +"%Y-%m-%dT00:00:00Z")
TOMORROW=$(date -u -d "+1 day" +"%Y-%m-%dT00:00:00Z")

curl -s "https://graph.microsoft.com/v1.0/me/calendarView?startDateTime=${TODAY}&endDateTime=${TOMORROW}&\$orderby=start/dateTime&\$select=subject,start,end,organizer,location" \
  -H "Authorization: Bearer <access_token>"
```

### Calendar — Next 7 Days

```bash
START=$(date -u +"%Y-%m-%dT00:00:00Z")
END=$(date -u -d "+7 days" +"%Y-%m-%dT23:59:59Z")

curl -s "https://graph.microsoft.com/v1.0/me/calendarView?startDateTime=${START}&endDateTime=${END}&\$orderby=start/dateTime&\$select=subject,start,end,organizer,location,bodyPreview" \
  -H "Authorization: Bearer <access_token>"
```

### SharePoint — List Sites

```bash
curl -s "https://graph.microsoft.com/v1.0/sites?\$search=*&\$select=id,displayName,webUrl" \
  -H "Authorization: Bearer <access_token>"
```

### SharePoint — Get a Specific Site

```bash
# Format: sites/{hostname}:/{server-relative-path}
curl -s "https://graph.microsoft.com/v1.0/sites/yourdomain.sharepoint.com:/sites/YourSiteName?\$select=id,displayName,webUrl" \
  -H "Authorization: Bearer <access_token>"
```

### SharePoint — List Document Libraries

```bash
curl -s "https://graph.microsoft.com/v1.0/sites/<site_id>/drives?\$select=id,name,webUrl" \
  -H "Authorization: Bearer <access_token>"
```

### SharePoint — Browse Files

```bash
# Root of a library
curl -s "https://graph.microsoft.com/v1.0/drives/<drive_id>/root/children?\$select=id,name,size,lastModifiedDateTime,webUrl,file,folder" \
  -H "Authorization: Bearer <access_token>"

# Subfolder
curl -s "https://graph.microsoft.com/v1.0/drives/<drive_id>/root:/<folder-path>:/children?\$select=id,name,size,lastModifiedDateTime,webUrl,file,folder" \
  -H "Authorization: Bearer <access_token>"
```

### SharePoint — Download a File

```bash
# By path
curl -sL "https://graph.microsoft.com/v1.0/drives/<drive_id>/root:/<url-encoded-path>:/content" \
  -H "Authorization: Bearer <access_token>" \
  -o "<local_filename>"

# By item ID
curl -sL "https://graph.microsoft.com/v1.0/drives/<drive_id>/items/<item_id>/content" \
  -H "Authorization: Bearer <access_token>" \
  -o "<local_filename>"
```

### Search Across All SharePoint

```bash
curl -s "https://graph.microsoft.com/v1.0/search/query" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "requests": [{
      "entityTypes": ["driveItem"],
      "query": { "queryString": "<search_term>" },
      "from": 0,
      "size": 25
    }]
  }'
```

---

## Pagination

Most Graph endpoints return a maximum of 25-999 records per page. Control page size with `$top` and follow `@odata.nextLink` in the response to get the next page:

```
GET <value of @odata.nextLink>
```

---

## Writing Your Behavior Rules

Here's a template you can adapt for your Claude instruction file. Copy it, edit the rules to match the decisions you made above, and add it to your CLAUDE.md or equivalent.

```markdown
## Claude Behavior Rules — Microsoft Graph

### Email
- Drafting emails is permitted. Claude may compose and save emails to the Drafts folder.
- Sending emails is [PERMITTED / NOT PERMITTED] unless explicitly approved per-message.
- When a draft is created, confirm the subject, recipient, and body preview before saving.
- [Add any address restrictions, folder restrictions, or other email rules here.]

### Calendar
- Reading calendar events is permitted.
- Creating or modifying events is [PERMITTED / NOT PERMITTED].
- [Add any rules about accepting/declining invitations, specific calendar restrictions, etc.]

### SharePoint / OneDrive
- Reading files and browsing sites/libraries is permitted.
- Uploading or modifying content is [PERMITTED / NOT PERMITTED].
- [If uploads are permitted, specify which folders.]
- Deleting SharePoint content is NOT permitted under any circumstances.
- [List any files Claude should auto-download without asking — pricing sheets, templates, etc.]

### General
- Before any write operation (draft, upload, calendar change), confirm the action with me.
- [Add any folder or site restrictions — areas Claude should never access.]
```

Adapt this to your workflow. The goal: Claude knows what it can touch and what it can't, without you having to think about it every session.

---

## Troubleshooting

**401 Unauthorized on API calls:** Access token expired. Get a fresh one using the refresh token flow. If that also fails, the refresh token may have expired (90 days of inactivity or client secret rotation). Re-run the initial consent flow from Step 3.

**403 Forbidden:** The app registration doesn't have the required scope, or admin consent hasn't been granted. Check API permissions in Azure Portal.

**Token refresh returns "invalid_grant":** The refresh token is dead. Common causes: client secret was rotated, user changed their password, or the token went unused for 90+ days. Re-run the consent flow.

**Can't find SharePoint site:** Use the search endpoint first to discover site IDs. Site URLs and IDs aren't always intuitive. Once you find the right site ID and drive ID, add them to your instruction file so Claude doesn't have to search every time.

**Rate limiting (429 Too Many Requests):** Graph allows 10,000 requests per 10 minutes per app per tenant. If you hit this, something is looping. Check your automation.

---

## Things to Remember

- **Refresh tokens don't have a fixed expiry** but will die if unused for 90 days or if the app's client secret rotates. Use the connection regularly or set a reminder to refresh it.
- **Client secrets expire.** Set a calendar reminder for the expiry date you chose during setup.
- **Scopes are granted at consent time.** If you add new scopes to the app registration later, you need to re-run the consent flow (Step 3) to get a new refresh token that includes the new scopes.
- **API version:** Use `v1.0` (stable, production). The `beta` endpoint has more features but breaking changes happen without notice.
- **Admin consent:** Some scopes require tenant admin consent. If you're not an admin, coordinate with whoever is before starting.

---

*Companion to: Securing Claude's API Keys with Azure Key Vault*
*Last updated: March 8, 2026*


---

## Corrections Log

*Tracks issues found when following this file's instructions. Entries are added when a discrepancy is discovered and a fix is applied or proposed.*

| Date | What Failed | Root Cause | Fix Applied | ERRORS.md Ref |
|------|-------------|------------|-------------|---------------|

**Notes:**
<!-- Per-entry context that doesn't fit in the table. Format: "YYYY-MM-DD: [explanation]" -->
