<!-- This intake works for any cloud (Azure, AWS, GCP). Resource names reference cloud platforms as illustrative examples; substitute your platform's equivalents. -->

---
type: context-file
parent: "[[coding-index]]"
summary: "Interview-driven protocol to generate a baseline master architecture doc for a repo that doesn't have one yet. Eight standing buckets (Compute, Data, Identity, Config, Observability, Integrations, Deployment, External Dependencies). Output is the repo's master arch doc that every plan doc's Architecture Context section will WikiLink back to."
tags: [coding, architecture, scoping, intake, interview]
---

# Architecture Intake ,  Generating the Master Arch Doc for a New Repo

> **When to run this:** A repo has no `docs/<project>-architecture.md` (or equivalent `docs/Architecture.md` for non-[Your Cloud Platform] projects), and a feature plan needs to be scoped or written for that repo. The plan doc's Architecture Context section (per [[scoping-phased-delivery]] Section 8) cannot be written without a master arch doc to WikiLink back to. This intake produces that master doc.
>
> **Run this once per repo, not per feature.** After the intake produces the master arch doc, every subsequent feature reuses it. The plan doc's Architecture Context section is a per-feature slice that points back to specific sections of the master doc; the master doc itself is updated incrementally as new infrastructure is added (per the wave-issue checklist gate).

> **When NOT to run this:** If the repo already has a master arch doc that's reasonably current (touched within the last 90 days, covers all eight buckets), skip the intake and go straight to writing the plan's Architecture Context section. If the existing doc is stale or has gaps in specific buckets, run a partial intake covering only the missing buckets.

---

## Output Contract

The intake produces a single file: `docs/<project>-architecture.md` ([Your Cloud Platform]-hosted projects) or `docs/Architecture.md` (non-[Your Cloud Platform]). The file has eight top-level sections matching the buckets below, each with anchor IDs that future WikiLinks can target.

**File header template:**

```markdown
---
type: architecture-master
repo: [repo-name]
last-reviewed: YYYY-MM-DD
summary: "Master architecture reference for [repo-name]. Plan docs WikiLink here for per-feature context."
---

# [Repo Name] ,  Architecture

> Master architecture reference. Per-feature plan docs include an "Architecture Context" section that WikiLinks back to specific sub-sections here.
> Update this doc whenever a feature adds, removes, or modifies any infrastructure resource (per [[scoping-phased-delivery]] Section 8d wave-issue checklist).

## Compute
...

## Data
...

## Identity
...

## Config
...

## Observability
...

## Integrations
...

## Deployment
...

## External Dependencies
...
```

Each section uses `### sub-headings` with kebab-case anchors so plan docs can link to `[[<project>-architecture#cosmos-tip-app-shared]]` rather than the whole file.

---

## How to Run the Intake

The intake is a question-driven interview, run one bucket at a time. Each bucket has a prompt set; ask 2-3 questions per round, wait for answers, then move to the next bucket. Do not dump all eight buckets' worth of questions in a single AskUserQuestion call ,  that's a wall of text, not an interview.

**For each bucket:**

1. Read the existing repo to bootstrap answers. Look at `Program.cs`, `Startup.cs`, `appsettings.json`, `host.json`, `.csproj` files, `*.bicep` / `*.tf` if present, GitHub Actions workflows, and README files. Pre-populate as much as you can.
2. Present what you found to Albert and ask the gap-filling questions for that bucket.
3. Write the bucket's section in the master arch doc immediately after Albert confirms.
4. Move to the next bucket.

**Format the output as you go.** Do not gather all eight buckets' answers and then write the doc at the end ,  that produces a doc that's never been read for accuracy. Write each section as soon as the bucket completes, present it to Albert for a quick confirm, then move on.

---

## The Eight Buckets

### Bucket 1: Compute

**What it covers:** Every runtime that hosts code in this repo. Function Apps, App Services, Web Jobs, container apps, AKS pods, console runners, MAUI shells, Blazor servers.

**Bootstrap questions (read repo first):**
- Look for `host.json` (Function Apps), `Program.cs` (App Services / Functions), `*.csproj` `OutputType` and `TargetFramework`, `Dockerfile`s.
- Identify each runtime project and its corresponding hosted resource name.

**Interview prompts:**
1. "I see [list of runtime projects from the repo]. For each one, what's the dev resource name, prd resource name, and what does it do at a one-line level?"
2. "Are there any runtimes I missed? (background workers, cron jobs, MAUI clients, scripts hosted somewhere?)"
3. "For each runtime, what region(s) does it run in, and is it active-active, active-passive, or single-region?"

**Section template:**

```markdown
## Compute

### [Project Name] (e.g., TIP.App.Inbox.Func)
- **Type:** Function App / App Service / Web Job / Container / Console
- **Dev resource:** tip-dev-app-func-inbox (East US 2)
- **Prd resource:** tip-prd-app-func-inbox (East US 2)
- **Purpose:** [one-line description of what this runtime does]
- **Trigger:** Timer (`0 0 */15 * * *`) / HTTP / Service Bus / Cosmos change feed / Manual
- **SDK:** .NET 8 isolated worker / .NET 8 in-proc / Node 20 / etc.
```

---

### Bucket 2: Data

**What it covers:** Every data plane this repo reads from or writes to. Cosmos DB containers, SQL databases and tables, blob containers, Service Bus queues/topics, Event Grid, Redis caches, file shares.

**Bootstrap questions (read repo first):**
- Look for `DbContext` classes, `CosmosClient` initialization, `BlobServiceClient`, connection string keys in `appsettings.json` and Key Vault.
- Identify each data plane and its corresponding resource.

**Interview prompts:**
1. "I see [list of data planes from the repo]. For each Cosmos container or SQL table, what's the partition key (Cosmos) or primary key strategy (SQL), and roughly what does it store?"
2. "Are there shared data planes used by multiple repos? (Cosmos accounts named `*-shared-cosmos`, etc.)"
3. "Any data planes I missed ,  caches, blob storage for attachments, Service Bus queues, Event Grid topics?"

**Section template:**

```markdown
## Data

### Cosmos DB

#### tip-app-shared-cosmos (account)
- **Dev resource:** tip-dev-app-shared-cosmos
- **Prd resource:** tip-prd-app-shared-cosmos
- **Containers:**
  - `inbox-rules` (PK: `/userId`) ,  stores per-user inbox rules
  - `inbox-runs` (PK: `/runId`) ,  stores run history
  - [...]

### SQL Databases

#### tip-app-shared-sql
- **Dev resource:** tip-dev-app-shared-sql / tip-app-database
- **Prd resource:** tip-prd-app-shared-sql / tip-app-database
- **Schema source:** TIP.App.Database.Schema (SSDT project, Windows-only build)
- **Key tables:** [list with one-line purpose each]

### Blob Storage

#### [account name]
- [containers + purpose]

### Service Bus / Event Grid / Redis

[as applicable]
```

---

### Bucket 3: Identity

**What it covers:** How code in this repo authenticates to [Your Cloud Platform] resources, external APIs, and other services. System-managed identities, user-assigned identities, app registrations, service principals, OAuth refresh tokens.

**Bootstrap questions (read repo first):**
- Look for `Default[Your Cloud Platform]Credential`, `ManagedIdentityCredential`, `ClientSecretCredential` usage. Look for app registration IDs in config.
- Identify which runtime uses which identity.

**Interview prompts:**
1. "For each runtime in Bucket 1, what identity does it use to access [Your Cloud Platform] resources (Cosmos, Key Vault, etc.)? System-assigned MI? User-assigned MI? Service principal?"
2. "What app registrations exist for this repo? (Names, IDs, what they're used for ,  e.g., delegated Graph access, Zoho OAuth client)"
3. "Are there OAuth refresh tokens stored somewhere for delegated access? Where, and what's the refresh strategy?"

**Section template:**

```markdown
## Identity

### System-Managed Identities

#### tip-dev-app-func-inbox / tip-prd-app-func-inbox
- **Type:** System-assigned
- **Role assignments:**
  - Cosmos DB Data Contributor on `tip-*-app-shared-cosmos`
  - Key Vault Secrets User on `tip-*-app-shared-kv`
  - App Configuration Data Reader on `tip-*-app-shared-appconfig`

### App Registrations

#### TIP App ,  Microsoft Graph (Delegated)
- **Tenant:** [tenant ID]
- **Client ID:** [stored in App Config: `SysCfg:Shared:Graph:ClientId`]
- **Scopes:** Mail.Read, Calendars.Read, [...]
- **Refresh token storage:** Cosmos `user-graph-tokens` container

#### TIP App ,  Zoho OAuth
- **Client ID/Secret:** Key Vault `zoho-app-client-id` / `zoho-app-client-secret`
- **Refresh token:** Key Vault `zoho-app-refresh-token`
- **Used by:** ZohoOAuthService (singleton, refreshes once per hour)
```

---

### Bucket 4: Config

**What it covers:** Where configuration values live. App Configuration prefixes, Key Vault secrets, appsettings.json, environment variables, feature flags.

**Bootstrap questions (read repo first):**
- Look at every `appsettings.json`, `appsettings.Development.json`, `host.json`, `local.settings.json`. Look for `ConfigurationBuilder.Add[Your Cloud Platform]AppConfiguration` and `Add[Your Cloud Platform]KeyVault`.
- List every config key the code reads.

**Interview prompts:**
1. "I found config keys grouped under [list of prefixes ,  e.g., `SysCfg:App:Inbox:`, `SysCfg:Shared:Graph:`]. Are these the canonical prefix conventions for this repo?"
2. "Which keys live in App Configuration vs Key Vault vs appsettings? Any keys that should move?"
3. "Feature flags ,  is App Configuration's feature flag service in use? Which flags exist?"

**Section template:**

```markdown
## Config

### App Configuration

**Resource:** tip-dev-app-shared-appconfig / tip-prd-app-shared-appconfig

**Prefix conventions:**
- `SysCfg:App:Inbox:*` ,  Inbox-feature-specific settings
- `SysCfg:App:Pipeline:*` ,  Pipeline-feature-specific settings
- `SysCfg:Shared:Graph:*` ,  Microsoft Graph delegated app credentials (shared by multiple features)
- `SysCfg:Shared:Zoho:*` ,  Zoho API credentials (shared)

**Loading pattern:** `ConfigurationBuilder.Add[Your Cloud Platform]AppConfiguration` with managed identity, label = environment name (`dev` / `prd`).

### Key Vault

**Resource:** tip-dev-app-shared-kv / tip-prd-app-shared-kv

**Secret naming:**
- `zoho-app-*` ,  Zoho OAuth credentials
- `graph-app-refresh-token-{userId}` ,  per-user Graph refresh tokens
- [...]

**Loading pattern:** Referenced via App Configuration Key Vault references (`{"uri":"https://..."}`), so the application reads only App Config and Key Vault is transparent.

### appsettings.json (per-runtime overrides)

[List runtime-local overrides if any]

### Feature Flags

[List active feature flags + what they gate]
```

---

### Bucket 5: Observability

**What it covers:** Where logs and metrics go, how telemetry is structured, how alerts fire.

**Bootstrap questions (read repo first):**
- Look for `AddApplicationInsightsTelemetry`, `ILogger<T>` usage patterns, `LogService` / `BaseService` references, custom metrics.

**Interview prompts:**
1. "Which App Insights resource does each runtime send telemetry to?"
2. "What's the standard log scope key convention? (e.g., always include `RunId`, `UserId`, `RuleId`)"
3. "Are there active alerts? What conditions, what notification channels?"
4. "Custom metrics ,  anything beyond default request/dependency telemetry?"

**Section template:**

```markdown
## Observability

### App Insights Resources

- **Dev:** tip-dev-app-shared-ai
- **Prd:** tip-prd-app-shared-ai
- **Connected runtimes:** All runtimes from Bucket 1, via App Configuration `SysCfg:Shared:AppInsights:ConnectionString`

### Logging Conventions

- **Base classes:** Every service inherits from `BaseService`, which holds an `ILogger<T>` and a `LogService` for structured scope writes
- **Standard scope keys:**
  - `UserId` (always when a user context exists)
  - `RuleId` (for Inbox rule operations)
  - `RunId` (for Inbox/Pipeline runs)
  - `IssueNumber` (for code generated for a specific GitHub issue)
- **Severity convention:** Information for happy path, Warning for retry-able failures, Error for unhandled exceptions

### Custom Metrics

[List custom metrics + their dimensions]

### Alerts

[List active alerts ,  name, condition, notification channel]
```

---

### Bucket 6: Integrations

**What it covers:** External APIs this repo calls, how it authenticates to them, and how it handles their failure modes.

**Bootstrap questions (read repo first):**
- Look for `HttpClient` factories, `Polly` policies, named clients, retry strategies.

**Interview prompts:**
1. "Which external APIs does this repo call? (Microsoft Graph, Zoho, NetSapiens, Stripe, etc.)"
2. "For each API, what's the auth pattern (OAuth refresh, API key, app-only, delegated)?"
3. "What retry / circuit-breaker policy is in place? (Polly retry counts, backoff strategy, fallback behavior)"
4. "Any APIs with strict rate limits or unusual error semantics worth flagging?"

**Section template:**

```markdown
## Integrations

### Microsoft Graph
- **Auth:** Delegated, per-user OAuth refresh token (stored in Key Vault, see Bucket 3)
- **Clients:** Singleton `GraphClientFactory` resolves a `GraphServiceClient` per user from cached refresh token
- **Retry:** Polly ,  3 attempts, exponential backoff 200ms / 1s / 5s, retry on 429 / 503 / network
- **Rate limit:** 10000 req/10min per app ,  code does not currently throttle, relies on Polly retry

### Zoho Books / Desk / CRM
- **Auth:** Single org-level OAuth refresh token (Key Vault), refreshed once per hour by `ZohoOAuthService` (singleton)
- **Clients:** `ZohoBooksClient`, `ZohoDeskClient`, `ZohoCrmClient` ,  each scoped per-request
- **Retry:** Polly ,  3 attempts, on 429 wait per `Retry-After` header
- **Rate limit:** 100 req/min per org ,  see [[zoho-api]]

[Repeat for each integration]
```

---

### Bucket 7: Deployment (CI/CD)

**What it covers:** How code in this repo gets to dev and prd. GitHub Actions workflows, branch protection, deploy gates, promotion path.

**Bootstrap questions (read repo first):**
- Look at `.github/workflows/*.yml`. List CI, CD-dev, CD-prd workflows, their triggers, and what they deploy.

**Interview prompts:**
1. "Confirm the workflows I see: [list]. Anything missing?"
2. "What's the promotion path? (Merge to dev branch deploys to dev; tag triggers prd? Manual approval gate? Smoke test wait?)"
3. "Branch protection rules ,  required reviews, required CI checks?"

**Section template:**

```markdown
## Deployment

### Workflows
- **`ci.yml`** ,  runs on every push to any branch. Build + test. Required for PR merge.
- **`cd-dev.yml`** ,  runs on push to `dev`. Builds, then deploys all runtimes (Bucket 1) to dev resources.
- **`cd-prd.yml`** ,  runs on tag matching `v*.*.*`. Builds, then deploys to prd resources after manual approval.

### Branch Protection
- `main`: requires 1 approval, CI green, no force push
- `dev`: requires CI green, no force push

### Promotion Path
1. PR merged into `dev` → cd-dev.yml runs → dev deployed
2. Manual smoke test on dev for 24h
3. Tag `v*.*.*` cut from `dev` → cd-prd.yml runs → manual approval → prd deployed

### Build Constraints
- SSDT projects (`TIP.App.Database.Schema`) build only on Windows runners
- Mac development cannot build solution-level (`.sln`); per-project builds only
```

---

### Bucket 8: External Dependencies

**What it covers:** Third-party services that this repo depends on for runtime behavior, beyond integrations covered in Bucket 6. Includes: SaaS tools (Auth0, Stripe, SendGrid, Twilio), infrastructure-as-a-service (CDN, DNS), open-source libraries with critical version dependencies.

**Bootstrap questions (read repo first):**
- Look at `*.csproj` package references for any SaaS SDK. Look at hostnames in HTTP clients beyond what Bucket 6 covers.

**Interview prompts:**
1. "Beyond the integrations in Bucket 6, what other third parties does the runtime depend on? (CDN for static assets, DNS provider, email sending service, SMS service, image processing, payments?)"
2. "Are there any libraries pinned to specific versions for compatibility reasons that future devs need to know about?"
3. "What's the SLA / fallback if any of these go down? (e.g., 'if SendGrid is down, emails queue for retry, no user-facing failure')"

**Section template:**

```markdown
## External Dependencies

### Email Delivery ,  SendGrid
- **Auth:** API key in Key Vault (`sendgrid-api-key`)
- **SLA:** 99.95% (SendGrid public commitment)
- **Fallback:** Failed sends queue in Service Bus `email-retry`, retried hourly

### SMS ,  Twilio
- [...]

### Pinned Libraries
- `Microsoft.Graph` pinned at 5.x ,  6.x has a breaking change in `IBaseRequest` we haven't migrated yet
- [...]
```

---

## Closing the Intake

After all eight buckets are written:

1. **Commit the master arch doc.** Branch: `docs/arch-baseline`. Commit message: `docs: add baseline <project>-architecture.md from intake`.
2. **Push and merge.** This is a docs-only change; no CI gate beyond markdown lint.
3. **Confirm to Albert.** Report: file path, sections written, any gaps Albert deferred ("we'll fill in Observability alerts later"), and whether the intake is considered complete or incremental.
4. **Update the relevant plan doc(s).** If a feature plan was waiting on this intake, return to that plan and write its Architecture Context section now, with WikiLinks back to the new master doc.

---

## When to Re-Run the Intake

- A repo's master arch doc has gone stale (last-reviewed > 90 days and several waves have shipped without updating it). Run a partial intake covering only the buckets that look out of date.
- A new bucket of infrastructure was added (e.g., the project picks up Service Bus for the first time). Add a new sub-section to the existing master doc rather than rerunning the full intake.
- The repo is being split or merged with another repo. Run a fresh intake on the new repo boundary.

The intake is not a quarterly ritual; it's a one-time bootstrap with incremental updates. The wave-issue checklist already enforces incremental updates as features ship.

---

## Corrections Log

*Tracks issues found when following this file's instructions. Entries are added when a discrepancy is discovered and a fix is applied or proposed.*

| Date | What Failed | Root Cause | Fix Applied | ERRORS.md Ref |
|------|-------------|------------|-------------|---------------|

**Notes:**
<!-- Per-entry context that doesn't fit in the table. Format: "YYYY-MM-DD: [explanation]" -->

---

*Last updated: 2026-04-24*
