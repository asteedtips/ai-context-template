# Claude Inbox Monitor - Project Plan

**Created:** 2026-03-14
**Updated:** 2026-03-14
**Status:** Scoping
**Track:** A (Greenfield / New Bounded Context)
**Branch:** `feat/issue-52`
**Location:** `Source Control/Local` (never synced to GitHub)

---

## 1. Overview

The Claude Inbox Monitor is a new bounded context in the TIPS Portal that gives users a UI for configuring, scheduling, and monitoring automated email processing rules against Outlook mailboxes. Today, inbox processing runs through standalone Claude scheduled tasks with rules hardcoded in `Email-Processing.md`. This project moves that logic into the .NET platform with persistent configuration in SQL Server, a MudBlazor UI for rule management, and an Azure Function for background execution.

The feature sits under a new top-level "Claude" menu in the portal, designed to host multiple AI-powered tools over time. Inbox Monitor is the first.

---

## 2. Decisions Table

| # | Decision | Answer |
|---|----------|--------|
| 1 | Which portal hosts this feature? | TIPS Portal (Entra ID authentication). Not the NetSapiens portal. |
| 2 | Auth model? | Two new Entra ID app roles: `ClaudeInboxUser` (own mailbox only) and `ClaudeInboxAdmin` (all inboxes, rule management, system config). **Admin implies user** — `ClaudeInboxAdmin` grants all user-level access automatically. A user only needs one role. Both registered as new app roles in the existing TIPS Portal App Registration. |
| 3 | Can a user hold multiple roles? | Yes. The existing `GraphAppRoleHandler` + `GraphAppRoleRequirement` architecture validates each policy independently. A user can hold `TIPSPortalUser + ClaudeInboxAdmin + SnoutAdmins` simultaneously. No rearchitecting needed. |
| 4 | How does the system map users to mailboxes? | UPN = mailbox. The logged-in user's UPN (e.g., `asteed@trueipsolutions.com`) is their mailbox address. Admins can configure additional shared mailboxes (like `accounting@`) through the UI. **No whitelist** — any admin can add any mailbox address. Graph permissions enforce what's actually accessible at runtime. |
| 5 | Where does email data come from? | Microsoft Graph SDK (.NET) via the `Microsoft.Graph` NuGet package. Same credential chain as `GraphIdentityService` (ClientSecretCredential in dev, ManagedIdentityCredential in prod). |
| 6 | Graph API permissions? | **Mail.ReadWrite** application permission required. The existing App Registration has Mail.Read — needs upgrade to Mail.ReadWrite to support move, flag, and category actions. Admin consent required in Entra ID. |
| 7 | Where are rules stored? | SQL Server tables in `TipAppDataContext` under a new `scClaude` database schema. Full CRUD through the UI. Rules are EF Core entities. |
| 8 | Does the portal execute rules? | No. The portal is config and monitoring only. A separate Azure Function reads rules from SQL and executes them against Graph/Zoho APIs on a schedule. |
| 9 | Background process hosting model? | New `TIP.App.Claude.Func` Azure Function app. Follows the existing `.Func` bounded context pattern (same as Snout.Func, MeridianIvr.Func). |
| 10 | How often does the function run? | Per-inbox configurable cron schedule stored in SQL. Each inbox config row has a cron expression. The function checks which inboxes are due and processes them. |
| 11 | How do rules evaluate? | Pipeline model: (1) Fetch unread emails via Graph, (2) AI classification via Claude API — categorize and extract metadata, (3) Rule evaluation in priority order — each matched rule adds actions to a queue, (4) Action execution in sequence, (5) Write results to Cosmos DB, (6) Generate run summary. Matches the current `Email-Processing.md` pattern (detect, extract, validate, record, move) but adds AI classification as a first-class pipeline step. |
| 12 | Rule condition types? | **Full filter engine with condition groups.** Rules have condition groups connected by AND. Within each group, conditions connect via the group's LogicalOperator (AND or OR). Supports nested logic like `(Sender contains "bill.com" OR Sender contains "repay.com") AND (Subject contains "payment")`. Filterable fields cover all Graph message properties: Sender, SenderName, Subject, Body, HasAttachment, Importance, To/CC/BCC recipients, ReceivedDate range, Categories, ConversationTopic, IsRead, IsDraft, HasFlag. Match operators include Contains, NotContains, StartsWith, EndsWith, Equals, NotEquals, Regex, GreaterThan, LessThan, Between, IsTrue, IsFalse. |
| 13 | Rule action types? | Four categories: (a) Outlook operations (move to folder, flag, apply category, mark read), (b) Zoho Books (log payment against invoice), (c) Zoho CRM (update deal stage/field), (d) Zoho Desk (create ticket with attachments). |
| 14 | Zoho API approach? | Extend existing patterns. `ZohoDeskService` already exists in `Shared.Service`. Add `ZohoBooksService` and `ZohoCrmService` following the same pattern (SettingsService for config, HttpService for HTTP, BaseService for logging). Zoho credentials stored in Azure App Configuration alongside existing Desk settings. |
| 15 | What does monitoring look like? | Dashboard at top (stats: emails processed, payments logged, tickets created, errors) + chronological activity log below. Filterable by date range. No live inbox view. |
| 16 | Menu structure? | Collapsible parent menu item "Claude" with "Inbox Monitor" as the first child. Built to support additional Claude-powered tools in the future. |
| 17 | Project structure? | Full bounded context following the SNOUT pattern: `TIP.App.Claude.Service`, `TIP.App.Claude.Service.Entity`, `TIP.App.Claude.UI`, `TIP.App.Claude.Func`, `TIP.App.Test.Claude`. Own DI registration. Own test project. |
| 18 | Settings injection? | `SettingsService` (not `IOptions`). Per `coding-best-practices.md`. |
| 19 | Database lifecycle? | `IDbContextFactory<TipAppDataContext>`. Per `coding-best-practices.md`. |
| 20 | Logging? | `BaseService` + `LogService`. Application Insights telemetry with `logUid` correlation. Per existing patterns. |
| 21 | AI categorization and summarization? | **Anthropic Claude API** via HTTP (`HttpService` pattern). Used in the Azure Function pipeline to classify emails into categories (Needs Response, Follow-Up, Informational, Payment, etc.) and generate per-run natural language summaries. API key stored in Azure Key Vault. New `ClaudeAiService` in `Claude.Service` handles prompt construction, API calls, and response parsing. |
| 22 | Activity log and run history storage? | **Cosmos DB** for all activity/run data. SQL Server keeps config tables only (InboxConfig, InboxRule, ConditionGroup, Condition, Action). Cosmos stores per-email processing results, run summaries, AI classifications, action execution details, and dashboard aggregation data. Partitioned by `inboxConfigId-YYYY-MM`. TTL-based retention policy (configurable, default 90 days). Solves PII retention concern and fits the append-heavy, time-range query pattern. |
| 23 | How do we test without production sandboxes? | **Dry Run mode at the pipeline level.** `InboxConfig` gets a `RunMode` field (`Live` = 1, `DryRun` = 2). In DryRun mode, the pipeline runs identically through fetch (Graph read), AI classification, and rule evaluation — all read-only operations execute normally. Only write operations are gated: Outlook move/flag/category/mark-read, Zoho Books payment recording, Zoho CRM deal updates, and Zoho Desk ticket creation are replaced with structured log entries describing what *would* happen (e.g., "Would move email 'Invoice #4521' to folder 'Processed'"). Results still write to Cosmos with `IsDryRun = true` so the dashboard shows them with a visual indicator (amber badge). The UI provides: (1) a Live/DryRun toggle on the inbox config page, (2) a "Test Run Now" button that fires a single dry-run regardless of saved mode, and (3) distinct styling in activity log entries for dry-run results. This covers all four external systems (Outlook, Zoho Books, Zoho CRM, Zoho Desk) without requiring sandbox environments for any of them. |
| 24 | What happens when multiple rules match one email? | **All matching rules fire in priority order.** `StopProcessing` is an opt-in brake — when set to `true` on a rule, no further rules evaluate after it matches. Default behavior (`StopProcessing = false`): rules are additive, every matching rule's actions execute. This matches Outlook rules behavior and supports layered rules (e.g., Rule 1 categorizes, Rule 2 moves, Rule 3 records payment). |
| 25 | Concurrent run protection? | **Skip with log entry.** Before starting a run, the Function checks Cosmos for an in-progress `RunSummaryDocument` for that inbox. If one exists and started within the `MaxRunDurationMinutes` window (configurable, default 30), the current cycle is skipped and a `SkippedRun` entry is written to Cosmos. The dashboard shows these as warning entries. If the previous run exceeds `MaxRunDurationMinutes`, it's considered stale and the new run proceeds. |
| 26 | Email reprocessing in DryRun mode? | **Track processed message IDs in Cosmos.** Before processing an email, check Cosmos for an existing `EmailProcessingResultDocument` with that Graph `messageId` for this inbox within the same `RunMode`. If found, skip. In Live mode this is a safety net (emails are typically moved/marked read). In DryRun mode this is the primary dedup mechanism. Switching from DryRun to Live intentionally reprocesses all emails so actions actually execute. |
| 27 | Dashboard aggregation strategy? | **Query Cosmos live.** At current TIPS scale (5-10 inboxes, ~50-200 emails/day), cross-partition fan-out is manageable. RunSummary documents are lightweight. No materialized aggregates in V1. Revisit if inbox count exceeds 20 or email volume exceeds 1,000/day. |
| 28 | Function app identity for Graph API? | **Same App Registration as Portal, Managed Identity.** `TIP.App.Claude.Func` shares the existing TIPS Portal App Registration (same client ID). In production, the Function's system-assigned Managed Identity is added as a credential on the App Registration. In dev, same `ClientSecretCredential`. Mail.ReadWrite permission granted once, works for both Portal and Function. Follows the `Snout.Func` pattern. |
| 29 | Real-time UI updates? | **Azure SignalR Service (serverless mode).** The Function sends progress messages via the SignalR REST API as it processes emails. The Portal's Blazor pages connect as SignalR clients and receive live updates — processing progress, run completion, error alerts. Covers both the "Test Run Now" feedback loop and dashboard auto-refresh for scheduled runs. Azure SignalR Service sits between Function and Portal as a shared hub. |
| 30 | ZohoCRM V1 scope? | **Find deal and attach email as note.** V1 CRM executor searches for a matching deal (`GET /crm/v6/Deals/search`), then adds the email content as a note on the deal with an AI-generated summary. No field updates in V1 — the mockup's field update UI validates the design for V2. Single match = proceed, multiple matches = skip with warning, no match = skip with warning. |
| 31 | AI-powered rule suggestions? | **Light version in V1.** A "Suggest Rules" button on the inbox detail page sends the last 50 processed emails (from Cosmos) to the Claude API. The API returns 2-3 rule templates based on detected patterns (recurring senders, common subjects, classification clusters). Templates open in a pre-filled rule editor dialog where the user can customize conditions, actions, and naming before saving. No auto-creation — the user reviews and approves each suggestion. |

---

## 3. Out of Scope

| Item | Rationale |
|------|-----------|
| Live inbox email viewer | Not building an "Outlook in the portal." The monitoring view shows processing activity, not raw email content. Can revisit in V2. |
| Multi-tenant (cross-organization) | This is TIPS-only. No multi-org mailbox support. |
| Email sending/replying | The function reads and processes inboxes. It does not compose or send emails. Per Email-Processing.md: "Never send emails." |
| Mobile-responsive layout | Desktop-first. No responsive breakpoints for mobile. Matches SNOUT approach. |
| Auto-record partial payments | Payment validation requires exact amount match for auto-recording. Partial payments are detected and surfaced as warnings with both amounts in the activity log (Decision #30 pending update), but not auto-recorded in Zoho Books. Full partial payment support deferred to V2. |
| ZohoCRM field updates | V1 CRM executor finds the deal and attaches email as a note with AI summary (Decision #30). Field-level updates (Stage, custom fields, etc.) are V2. The mockup's field update UI validates the design for V2 implementation. |
| AI auto-rule creation | V1 provides AI-generated rule templates that the user reviews and customizes (Decision #31). Fully automatic rule creation without user review is deferred. |
| Materialized dashboard aggregates | V1 queries Cosmos live on page load (Decision #27). Pre-computed daily aggregates deferred until scale demands it. |

---

## 4. Architecture and Where Code Lives

### Solution Structure

```
TIP.App.Claude.Service/              <- Business logic, Graph/Zoho API clients
  DI/DIAppClaudeServices.cs
  Inbox/InboxProcessingService.cs    <- Core pipeline engine
  Inbox/InboxConfigService.cs        <- CRUD for inbox configs
  Inbox/InboxRuleService.cs          <- CRUD for rules and actions
  Ai/ClaudeAiService.cs              <- Anthropic Claude API: email classification + summarization + rule suggestions
  Ai/IEmailClassificationService.cs  <- Interface for AI classification (swappable provider)
  Ai/RuleSuggestionService.cs        <- Generates rule templates from recent processing results via Claude API
  Monitoring/ActivityLogService.cs   <- Read/query from Cosmos DB for dashboard + activity log
  Monitoring/CosmosClientService.cs  <- Cosmos DB connection management
  Monitoring/SignalRNotificationService.cs  <- Sends processing progress/completion events to Azure SignalR Service
  Provider/
    ZohoBooksService.cs              <- Payment recording (new, in Shared.Service)
    ZohoCrmService.cs                <- Deal search + note attachment (new, in Shared.Service)

TIP.App.Claude.Service.Entity/       <- DTOs, ViewModels, Enums
  InboxConfigVm.cs
  InboxRuleVm.cs
  InboxRuleConditionGroupVm.cs
  InboxRuleConditionVm.cs
  InboxRuleActionVm.cs
  InboxActivityLogVm.cs
  EmailClassificationResult.cs       <- AI classification response: category, confidence, summary, extracted metadata
  RunSummaryDocument.cs              <- Cosmos RunSummary document model
  EmailProcessingResultDocument.cs   <- Cosmos per-email result document model
  Enums/
    ConditionField.cs                <- Sender, SenderName, Subject, Body, HasAttachment, Importance, To/CC/BCC, ReceivedDate, Categories, etc.
    MatchOperator.cs                 <- Contains, NotContains, StartsWith, EndsWith, Equals, NotEquals, Regex, GreaterThan, LessThan, Between, IsTrue, IsFalse
    LogicalOperator.cs               <- And, Or
    RuleActionType.cs                <- OutlookMove, OutlookFlag, OutlookCategory, OutlookMarkRead, ZohoBooksPayment, ZohoCrmDealUpdate, ZohoDeskTicket
    InboxProcessingStatus.cs         <- Pending, Processing, Completed, Failed, Skipped
    RunMode.cs                       <- Live, DryRun

TIP.App.Claude.UI/                   <- Blazor UI components
  Components/
    Pages/
      ClaudeDashboard.razor          <- Landing page for /claude
      InboxMonitorList.razor         <- List of configured inboxes (/claude/inbox)
      InboxMonitorDetail.razor       <- Single inbox config + rules table (/claude/inbox/{id})
      InboxActivityLog.razor         <- Activity log for an inbox (/claude/inbox/{id}/activity)
    Shared/
      RuleEditor.razor               <- Rule creation/edit dialog (wraps condition + action editors)
      ConditionGroupEditor.razor     <- Condition group builder with AND/OR toggle, field/operator/value pickers
      ActionEditor.razor             <- Action configuration per rule
      RuleSuggestionDialog.razor     <- AI-generated rule templates shown for user review/customization
      InboxStatCard.razor            <- Dashboard stat cards
  DIAppClaudeUIServices.cs

TIP.App.Claude.Func/                 <- Azure Function app
  Functions/
    InboxProcessorFunction.cs        <- Timer trigger, reads inbox configs, executes pipeline
  Program.cs
  host.json

TIP.App.Test.Claude/                 <- Unit and integration tests
  Unit/
    Services/InboxProcessingServiceTests.cs
    Services/InboxRuleServiceTests.cs
    Services/ZohoBooksServiceTests.cs
  TestHelpers/ClaudeTestFixture.cs
```

### Database Schema (`scClaude`)

New tables in `TIP.App.Database.Schema` under `scClaude/`:

```
scClaude.InboxConfig              <- Configured mailboxes
scClaude.InboxRule                <- Processing rules per inbox
scClaude.InboxRuleConditionGroup  <- Groups of conditions with AND/OR logic per rule
scClaude.InboxRuleCondition       <- Individual filter conditions within a group
scClaude.InboxRuleAction          <- Actions per rule (pipeline steps)
```

### Cosmos DB Container (`claude-activity`)

Run history and activity logs stored in Cosmos DB (not SQL). See Section 7 for document schemas.

```
Container: claude-activity
Partition key: /partitionKey (format: "{inboxConfigId}-{YYYY-MM}")
TTL: Configurable per document, default 90 days (7,776,000 seconds)
Document types: EmailProcessingResult, RunSummary
```

### Hosting Model

- **UI:** Blazor Server, rendered in TIP.App.Portal (same as SNOUT, LOA, Rating)
- **Background:** TIP.App.Claude.Func, deployed as a separate Azure Function App (same App Registration as Portal, Managed Identity auth)
- **Config Database:** Existing TIP App SQL Server, new `scClaude` schema (rules, conditions, actions, inbox configs)
- **Activity Database:** Azure Cosmos DB, `claude-activity` container (run history, email results, AI classifications, dashboard data)
- **AI:** Anthropic Claude API via HTTP for email classification, summarization, and rule suggestion generation
- **Real-time:** Azure SignalR Service (serverless mode) — Function sends progress/completion events, Portal Blazor pages receive live updates
- **Auth:** Entra ID app roles through existing GraphAppRoleHandler

---

## 5. UI Validation Mockups

To be built after decisions table review. Will include:

1. **Claude Landing Page** (`/claude`): Menu entry point showing available Claude tools
2. **Inbox Monitor List** (`/claude/inbox`): Card grid of configured inboxes with status indicators
3. **Inbox Config Detail** (`/claude/inbox/{id}`): Inbox settings (mailbox address, schedule, enabled/disabled) + rules table
4. **Rule Editor Dialog**: Modal for creating/editing a rule. Includes condition group builder (add groups, set AND/OR per group, add conditions with field/operator/value pickers) and action pipeline builder.
5. **Activity Log** (`/claude/inbox/{id}/activity`): Chronological log with filters

Mockups will show both ClaudeInboxUser view (own inbox only, read-only rules) and ClaudeInboxAdmin view (all inboxes, full CRUD).

---

## 6. Existing Pattern References

| Pattern Doc | Applies To | Deviations |
|-------------|-----------|------------|
| `coding-best-practices.md` Section 1.1 | Project layering | None. Full stack: Database.Sql -> Service.Entity -> Service -> UI -> Portal |
| `coding-best-practices.md` Section 1.2 | Naming conventions | None. Follow `TIP.App.Claude.*` naming. |
| `coding-best-practices.md` Section 2.1 | DI registration | None. `DIAppClaudeServices.cs` + `DIAppClaudeUIServices.cs` pattern. |
| `coding-best-practices.md` Section 3 | SettingsService | None. Zoho config through SettingsService, not IOptions. |
| `coding-best-practices.md` Section 4 | IDbContextFactory | None. Standard factory pattern for TipAppDataContext. |
| SNOUT bounded context | Full project structure | Baseline pattern. Claude follows SNOUT's DI chain, page structure, auth policy setup, and test fixture approach. |
| `ZohoDeskService` in Shared.Service | Zoho API client pattern | Extending. Adding `ZohoBooksService` and `ZohoCrmService` in Shared.Service following the same HttpService + SettingsService + BaseService pattern. |
| `GraphIdentityService` in Shared.Service | Graph SDK usage | Extending. Adding mail read/write operations using the same credential chain. |
| `security-practices.md` | Credential handling | All Zoho and Graph credentials in Azure App Configuration (with Key Vault references where appropriate). No secrets in code or config files. |

---

## 7. Data Model

### New Entities (scClaude schema)

```csharp
// scClaude.InboxConfig - A configured mailbox to monitor
public class InboxConfig
{
    public int InboxConfigId { get; set; }
    public string MailboxAddress { get; set; }          // e.g., "accounting@trueipsolutions.com"
    public string DisplayName { get; set; }             // e.g., "Accounting Inbox"
    public string CronExpression { get; set; }          // e.g., "0 */4 * * *"
    public bool IsEnabled { get; set; }
    public bool IsSharedMailbox { get; set; }           // true = app credentials, false = delegated
    public string? OwnerUpn { get; set; }               // null for shared, UPN for personal
    public string CreatedBy { get; set; }
    public DateTime CreatedDate { get; set; }
    public string? ModifiedBy { get; set; }
    public DateTime? ModifiedDate { get; set; }
    public DateTime? LastProcessedDate { get; set; }
    public int? LastProcessedCount { get; set; }
    public int RunMode { get; set; }                     // Enum: Live=1, DryRun=2 (default: Live)
    public int MaxRunDurationMinutes { get; set; }       // Stale run timeout (default: 30). If previous run exceeds this, next cycle proceeds.

    // Navigation
    public ICollection<InboxRule> Rules { get; set; }
    public ICollection<InboxActivityLog> ActivityLogs { get; set; }
}

// scClaude.InboxRule - A processing rule for an inbox
public class InboxRule
{
    public int InboxRuleId { get; set; }
    public int InboxConfigId { get; set; }              // FK to InboxConfig
    public string RuleName { get; set; }                // e.g., "Bill.com Payment"
    public string? Description { get; set; }
    public int Priority { get; set; }                   // Lower = higher priority, evaluated in order
    public bool IsEnabled { get; set; }
    public bool StopProcessing { get; set; }            // If true, no further rules evaluate after this one matches
    public string CreatedBy { get; set; }
    public DateTime CreatedDate { get; set; }
    public string? ModifiedBy { get; set; }
    public DateTime? ModifiedDate { get; set; }

    // Navigation
    public InboxConfig InboxConfig { get; set; }
    public ICollection<InboxRuleConditionGroup> ConditionGroups { get; set; }
    public ICollection<InboxRuleAction> Actions { get; set; }
}

// scClaude.InboxRuleConditionGroup - A group of conditions with a logical operator
// Groups connect with AND (all groups must pass for the rule to match).
// Within a group, conditions connect via the group's LogicalOperator.
// Example: (Sender contains "bill.com" OR Sender contains "repay.com") AND (Subject contains "payment")
//          = Group 1 (OR): two sender conditions + Group 2 (AND): one subject condition
public class InboxRuleConditionGroup
{
    public int InboxRuleConditionGroupId { get; set; }
    public int InboxRuleId { get; set; }                // FK to InboxRule
    public int LogicalOperator { get; set; }            // Enum: And=1, Or=2 — how conditions WITHIN this group relate
    public int SortOrder { get; set; }                  // Display/evaluation order among groups

    // Navigation
    public InboxRule InboxRule { get; set; }
    public ICollection<InboxRuleCondition> Conditions { get; set; }
}

// scClaude.InboxRuleCondition - A single filter condition within a group
public class InboxRuleCondition
{
    public int InboxRuleConditionId { get; set; }
    public int InboxRuleConditionGroupId { get; set; }  // FK to ConditionGroup (NOT directly to Rule)
    public int ConditionField { get; set; }             // Enum: Sender=1, SenderName=2, Subject=3, Body=4, etc.
    public int MatchOperator { get; set; }              // Enum: Contains=1, NotContains=2, StartsWith=3, etc.
    public string MatchValue { get; set; }              // The pattern to match against
    public string? MatchValueEnd { get; set; }          // Second value for Between operator (date ranges)
    public bool IsCaseSensitive { get; set; }           // Default: false
    public int SortOrder { get; set; }                  // Display order within the group

    // Navigation
    public InboxRuleConditionGroup ConditionGroup { get; set; }
}

// scClaude.InboxRuleAction - A pipeline action within a rule
public class InboxRuleAction
{
    public int InboxRuleActionId { get; set; }
    public int InboxRuleId { get; set; }                // FK to InboxRule
    public int ActionType { get; set; }                 // Enum: OutlookMove=1, OutlookFlag=2, OutlookCategory=3,
                                                        //        OutlookMarkRead=4, ZohoBooksPayment=10,
                                                        //        ZohoCrmDealUpdate=20, ZohoDeskTicket=30
    public int ExecutionOrder { get; set; }             // Order within the pipeline
    public string ActionConfigJson { get; set; }        // JSON blob with action-specific parameters
                                                        // e.g., {"folderId": "AAMk...", "folderName": "TIPS/AR"}
                                                        // e.g., {"departmentId": "45096...", "teamId": "45096...", "priority": "Medium"}
    public bool IsEnabled { get; set; }

    // Navigation
    public InboxRule InboxRule { get; set; }
}

// NOTE: InboxActivityLog has moved to Cosmos DB — see Cosmos Document Models below
```

### Enums

```csharp
public enum ConditionField
{
    // Core message fields
    Sender = 1,              // From email address
    SenderName = 2,          // From display name
    Subject = 3,
    Body = 4,

    // Boolean properties
    HasAttachment = 5,
    IsRead = 6,
    IsDraft = 7,
    HasFlag = 8,

    // Metadata
    Importance = 10,         // Low, Normal, High
    ToRecipients = 11,       // To line (email addresses)
    CcRecipients = 12,       // CC line
    BccRecipients = 13,      // BCC line
    ReceivedDate = 14,       // DateTime — supports range/comparison operators
    Categories = 15,         // Outlook categories (comma-separated)
    ConversationTopic = 16   // Thread topic
}

public enum MatchOperator
{
    // String operators
    Contains = 1,
    NotContains = 2,
    StartsWith = 3,
    EndsWith = 4,
    Equals = 5,
    NotEquals = 6,
    Regex = 7,

    // Comparison operators (for dates, importance)
    GreaterThan = 10,
    LessThan = 11,
    Between = 12,            // Uses MatchValue + MatchValueEnd

    // Boolean operators (for HasAttachment, IsRead, IsDraft, HasFlag)
    IsTrue = 20,
    IsFalse = 21
}

public enum LogicalOperator
{
    And = 1,
    Or = 2
}

public enum RuleActionType
{
    // Outlook operations (1-9)
    OutlookMove = 1,
    OutlookFlag = 2,
    OutlookCategory = 3,
    OutlookMarkRead = 4,

    // Zoho Books (10-19)
    ZohoBooksPayment = 10,

    // Zoho CRM (20-29)
    ZohoCrmDealUpdate = 20,

    // Zoho Desk (30-39)
    ZohoDeskTicket = 30
}

public enum InboxProcessingStatus
{
    Pending = 0,
    Processing = 1,
    Completed = 2,
    Failed = 3,
    Skipped = 4
}

public enum RunMode
{
    Live = 1,
    DryRun = 2
}
```

### ActionConfigJson Examples

Each action type has its own JSON schema for the `ActionConfigJson` field:

**OutlookMove:**
```json
{"folderId": "AAMk...", "folderName": "TIPS/AR"}
```

**OutlookFlag:**
```json
{"flagStatus": "flagged", "dueDate": null}
```

**OutlookCategory:**
```json
{"categories": ["Auto Processed", "Needs Response"]}
```

**OutlookMarkRead:**
```json
{"markAsRead": true}
```

**ZohoBooksPayment:**
```json
{
  "accountId": "2061049000050352430",
  "paymentMode": "Bank Remittance",
  "invoiceNumberField": "Subject",
  "invoiceNumberRegex": "INV-\\d+",
  "amountField": "Body",
  "amountRegex": "\\$[\\d,]+\\.\\d{2}",
  "paymentDateRule": "ReceivedDatePlusDays",
  "paymentDateDaysOffset": 2,
  "referenceFormat": "{date} {provider}"
}
```

**ZohoDeskTicket:**
```json
{
  "departmentId": "450966000000006907",
  "teamId": "450966000000355001",
  "accountId": "450966000004737035",
  "priority": "Medium",
  "channel": "Email",
  "identifierRegex": "-PO(\\d+)-",
  "skipReplies": true
}
```

**ZohoCrmDealUpdate (stub for V1):**
```json
{
  "dealField": "Stage",
  "dealValue": "Closed Won",
  "matchField": "Deal_Name",
  "matchPattern": "contains"
}
```

### Cosmos DB Document Models (claude-activity container)

Two document types share the same container, distinguished by `documentType`:

```csharp
// Per-email processing result — one document per email processed
public class EmailProcessingResultDocument
{
    [JsonPropertyName("id")]
    public string Id { get; set; }                      // GUID
    [JsonPropertyName("partitionKey")]
    public string PartitionKey { get; set; }            // "{inboxConfigId}-{yyyy-MM}"
    public string DocumentType { get; set; } = "EmailProcessingResult";
    public int InboxConfigId { get; set; }
    public string RunId { get; set; }                   // Groups all emails in one processing run
    public string EmailMessageId { get; set; }          // Graph message ID
    public string EmailSubject { get; set; }
    public string EmailSender { get; set; }
    public DateTime EmailReceivedDate { get; set; }
    public int? MatchedRuleId { get; set; }             // SQL InboxRuleId (null if no match)
    public string? MatchedRuleName { get; set; }
    public string ProcessingStatus { get; set; }        // Completed, Failed, Skipped
    public AiClassification? AiClassification { get; set; }
    public List<ActionExecutionResult> ActionsExecuted { get; set; }
    public string? ErrorMessage { get; set; }
    public DateTime ProcessedDate { get; set; }
    public bool IsDryRun { get; set; }                  // true = simulated run, actions were logged but not executed
    public Guid LogUid { get; set; }                    // Correlation ID for Application Insights
    public int Ttl { get; set; }                        // Cosmos TTL in seconds (default: 7776000 = 90 days)
}

// AI classification result embedded in each email result
public class AiClassification
{
    public string Category { get; set; }                // NeedsResponse, FollowUp, Informational, Payment, Spam, etc.
    public double Confidence { get; set; }              // 0.0 - 1.0
    public string Summary { get; set; }                 // One-line AI summary of the email
    public Dictionary<string, string>? ExtractedMetadata { get; set; }  // e.g., {"invoiceNumber": "INV-1234", "amount": "5250.00"}
}

// Result of a single action execution within the pipeline
public class ActionExecutionResult
{
    public string ActionType { get; set; }              // OutlookMove, ZohoBooksPayment, etc.
    public string Status { get; set; }                  // Success, Failed, Skipped, Simulated
    public string? Details { get; set; }                // JSON string with action-specific result data
    public string? SimulatedAction { get; set; }        // Dry run only: human-readable description of what would happen
    public string? ErrorMessage { get; set; }
}

// Per-run summary — one document per inbox processing run
public class RunSummaryDocument
{
    [JsonPropertyName("id")]
    public string Id { get; set; }                      // "run-{GUID}"
    [JsonPropertyName("partitionKey")]
    public string PartitionKey { get; set; }            // "{inboxConfigId}-{yyyy-MM}"
    public string DocumentType { get; set; } = "RunSummary";
    public int InboxConfigId { get; set; }
    public string RunId { get; set; }                   // Same GUID used in EmailProcessingResultDocuments
    public DateTime RunStarted { get; set; }
    public DateTime RunCompleted { get; set; }
    public int TotalEmails { get; set; }
    public int Processed { get; set; }
    public int Skipped { get; set; }
    public int Failed { get; set; }
    public Dictionary<string, int> CategorySummary { get; set; }    // e.g., {"NeedsResponse": 3, "Payment": 2}
    public Dictionary<string, int> ActionsSummary { get; set; }     // e.g., {"OutlookMove": 10, "ZohoBooksPayment": 2}
    public string AiSummary { get; set; }               // Natural language run summary from Claude API
    public bool IsDryRun { get; set; }                  // true = simulated run
    public Guid LogUid { get; set; }
    public int Ttl { get; set; }
}
```

**Cosmos DB queries the dashboard and activity log will use:**
- **Dashboard stats:** Query `RunSummaryDocument` by partition key (inbox + month) for totals
- **Activity log:** Query `EmailProcessingResultDocument` by partition key, filter by date range, page with continuation tokens
- **Cross-inbox dashboard:** Fan-out query across partitions (admin view) or single-partition query (user view)

### Modifications to Existing Entities

**TipAppDataContext.cs** (add DbSets):
```csharp
// scClaude — config tables only (activity data lives in Cosmos DB)
public DbSet<InboxConfig> InboxConfigs { get; set; }
public DbSet<InboxRule> InboxRules { get; set; }
public DbSet<InboxRuleConditionGroup> InboxRuleConditionGroups { get; set; }
public DbSet<InboxRuleCondition> InboxRuleConditions { get; set; }
public DbSet<InboxRuleAction> InboxRuleActions { get; set; }
```

**TipAppDataContext.Partial.cs** (Fluent API):
- Table names mapped to `scClaude` schema
- Relationships configured: InboxConfig → InboxRule (1:N), InboxRule → InboxRuleConditionGroup (1:N), InboxRuleConditionGroup → InboxRuleCondition (1:N), InboxRule → InboxRuleAction (1:N)
- Cascade deletes: Rule delete cascades to ConditionGroups → Conditions and Actions. InboxConfig delete cascades to Rules.
- No activity log indexes needed (moved to Cosmos)

**Constants.cs** (add new auth constants):
```csharp
// AuthorizeRole
public const string ClaudeInboxUser = "ClaudeInboxUser";
public const string ClaudeInboxAdmin = "ClaudeInboxAdmin";

// AuthorizePolicy
public const string ClaudeInboxUser = "ClaudeInboxUser";
public const string ClaudeInboxAdmin = "ClaudeInboxAdmin";
```

---

## 8. Phased Delivery Plan

### Phase 1: Database Schema and Entity Layer
Create the `scClaude` schema, SSDT table definitions, EF Core entities, and reverse-engineer into the data context.

**Files to create/modify:**
- `TIP.App.Database.Schema/scClaude/InboxConfig.sql`
- `TIP.App.Database.Schema/scClaude/InboxRule.sql`
- `TIP.App.Database.Schema/scClaude/InboxRuleConditionGroup.sql`
- `TIP.App.Database.Schema/scClaude/InboxRuleCondition.sql`
- `TIP.App.Database.Schema/scClaude/InboxRuleAction.sql`
- `TIP.App.Database.Sql/scClaude/InboxConfig.cs` (entity)
- `TIP.App.Database.Sql/scClaude/InboxRule.cs` (entity)
- `TIP.App.Database.Sql/scClaude/InboxRuleConditionGroup.cs` (entity)
- `TIP.App.Database.Sql/scClaude/InboxRuleCondition.cs` (entity)
- `TIP.App.Database.Sql/scClaude/InboxRuleAction.cs` (entity)
- `TIP.App.Database.Sql/TipAppDataContext.cs` (add DbSets — config tables only, no activity log)
- `TIP.App.Database.Sql/TipAppDataContext.Partial.cs` (Fluent API config)

**Gated steps:**
- [ ] SSDT publish to dev database
- [ ] EF Core Power Tools reverse-engineer

### Phase 2: Service Entity Layer (DTOs, Enums, ViewModels)
Create the DTOs and enums that the service and UI layers consume.

**Files to create:**
- `TIP.App.Claude.Service.Entity/TIP.App.Claude.Service.Entity.csproj`
- `TIP.App.Claude.Service.Entity/Enums/ConditionField.cs`
- `TIP.App.Claude.Service.Entity/Enums/MatchOperator.cs`
- `TIP.App.Claude.Service.Entity/Enums/LogicalOperator.cs`
- `TIP.App.Claude.Service.Entity/Enums/RuleActionType.cs`
- `TIP.App.Claude.Service.Entity/Enums/InboxProcessingStatus.cs`
- `TIP.App.Claude.Service.Entity/Enums/RunMode.cs`
- `TIP.App.Claude.Service.Entity/InboxConfigVm.cs`
- `TIP.App.Claude.Service.Entity/InboxRuleVm.cs`
- `TIP.App.Claude.Service.Entity/InboxRuleConditionGroupVm.cs`
- `TIP.App.Claude.Service.Entity/InboxRuleConditionVm.cs`
- `TIP.App.Claude.Service.Entity/InboxRuleActionVm.cs`
- `TIP.App.Claude.Service.Entity/InboxDashboardVm.cs`
- `TIP.App.Claude.Service.Entity/EmailClassificationResult.cs`
- `TIP.App.Claude.Service.Entity/EmailProcessingResultDocument.cs`
- `TIP.App.Claude.Service.Entity/RunSummaryDocument.cs`
- `TIP.App.Claude.Service.Entity/AiClassification.cs`
- `TIP.App.Claude.Service.Entity/ActionExecutionResult.cs`

**Modify:**
- `TIP.App.Shared.Service.Entity/Constants/Constants.cs` (add ClaudeInboxUser/ClaudeInboxAdmin roles and policies)

### Phase 3: Shared Zoho Service Extensions
Extend the existing Zoho integration in Shared.Service. Add Books and CRM service classes alongside the existing Desk service.

**Files to create:**
- `TIP.App.Shared.Service/Provider/ZohoBooks/ZohoBooksService.cs`
- `TIP.App.Shared.Service/Provider/ZohoCrm/ZohoCrmService.cs` (real — search deals, add note)
- `TIP.App.Shared.Service.Entity/Provider/ZohoBooks/ZohoBooksPaymentRequest.cs`
- `TIP.App.Shared.Service.Entity/Provider/ZohoBooks/ZohoBooksPaymentResponse.cs`
- `TIP.App.Shared.Service.Entity/Provider/ZohoBooks/ZohoBooksInvoiceLookupResponse.cs`
- `TIP.App.Shared.Service.Entity/Provider/ZohoCrm/ZohoCrmDealSearchRequest.cs`
- `TIP.App.Shared.Service.Entity/Provider/ZohoCrm/ZohoCrmDealSearchResponse.cs`
- `TIP.App.Shared.Service.Entity/Provider/ZohoCrm/ZohoCrmNoteRequest.cs`

**Modify:**
- `TIP.App.Shared.Service/DIAppSharedServices.cs` (register new Zoho services)
- `TIP.Kernel.Settings/SettingsConfiguration.cs` (verify ZohoBooks config class has all needed fields: ApiUrl, OrgId)

### Phase 4: Claude Service Layer (Core Logic)
Build the inbox processing pipeline, rule evaluation engine, and CRUD services.

**Files to create:**
- `TIP.App.Claude.Service/TIP.App.Claude.Service.csproj`
- `TIP.App.Claude.Service/DIAppClaudeServices.cs`
- `TIP.App.Claude.Service/Inbox/InboxConfigService.cs` (CRUD for inbox configs)
- `TIP.App.Claude.Service/Inbox/InboxRuleService.cs` (CRUD for rules, conditions, actions)
- `TIP.App.Claude.Service/Inbox/InboxProcessingService.cs` (core pipeline: fetch emails, evaluate rules, queue actions, execute)
- `TIP.App.Claude.Service/Inbox/ActionExecutors/OutlookActionExecutor.cs`
- `TIP.App.Claude.Service/Inbox/ActionExecutors/ZohoBooksActionExecutor.cs`
- `TIP.App.Claude.Service/Inbox/ActionExecutors/ZohoDeskActionExecutor.cs`
- `TIP.App.Claude.Service/Inbox/ActionExecutors/ZohoCrmActionExecutor.cs` (find deal + attach note with AI summary)
- `TIP.App.Claude.Service/Inbox/ActionExecutors/IActionExecutor.cs`
- `TIP.App.Claude.Service/Ai/IEmailClassificationService.cs`
- `TIP.App.Claude.Service/Ai/ClaudeAiService.cs`
- `TIP.App.Claude.Service/Ai/RuleSuggestionService.cs` (query Cosmos for recent results, build prompt, parse AI-generated rule templates)
- `TIP.App.Claude.Service/Monitoring/CosmosClientService.cs`
- `TIP.App.Claude.Service/Monitoring/ActivityLogService.cs` (reads/writes Cosmos DB)
- `TIP.App.Claude.Service/Monitoring/SignalRNotificationService.cs` (sends events to Azure SignalR Service)

### Phase 5: UI Layer
Build the Blazor pages and components for the Claude menu, inbox list, detail/rules editor, and activity log.

**Files to create:**
- `TIP.App.Claude.UI/TIP.App.Claude.UI.csproj`
- `TIP.App.Claude.UI/DIAppClaudeUIServices.cs`
- `TIP.App.Claude.UI/_Imports.razor`
- `TIP.App.Claude.UI/Components/Pages/ClaudeDashboard.razor` (`/claude`)
- `TIP.App.Claude.UI/Components/Pages/InboxMonitorList.razor` (`/claude/inbox`)
- `TIP.App.Claude.UI/Components/Pages/InboxMonitorDetail.razor` (`/claude/inbox/{id}`)
- `TIP.App.Claude.UI/Components/Pages/InboxActivityLog.razor` (`/claude/inbox/{id}/activity`)
- `TIP.App.Claude.UI/Components/Shared/RuleEditor.razor`
- `TIP.App.Claude.UI/Components/Shared/ConditionGroupEditor.razor`
- `TIP.App.Claude.UI/Components/Shared/ActionEditor.razor`
- `TIP.App.Claude.UI/Components/Shared/RuleSuggestionDialog.razor` (AI rule template review/customize dialog)
- `TIP.App.Claude.UI/Components/Shared/InboxStatCard.razor`

**Modify:**
- `TIP.App.Shared.UI/Components/Layout/NavMenu.razor` (add Claude menu with AuthorizeView)
- `TIP.App.Shared.UI/DIAppSharedUIServices.cs` (add ClaudeInboxUser and ClaudeInboxAdmin policies)
- `TIP.App.Portal/Program.cs` (register Claude UI services, add assembly reference, add SignalR client services)

**Gated steps:**
- [ ] UI mockup verification per component (see Section 5)

### Phase 6: Azure Function (Background Processor)
Build the timer-triggered function that reads inbox configs from SQL, executes the processing pipeline, and sends real-time progress events via Azure SignalR Service.

**Files to create:**
- `TIP.App.Claude.Func/TIP.App.Claude.Func.csproj`
- `TIP.App.Claude.Func/Program.cs` (registers SignalR output binding, Kernel settings, Claude services)
- `TIP.App.Claude.Func/host.json`
- `TIP.App.Claude.Func/Functions/InboxProcessorFunction.cs` (timer trigger with concurrent run guard + SignalR progress events)

### Phase 7: Testing
Unit tests for service layer, rule evaluation, action executors, and Zoho service extensions.

**Files to create:**
- `TIP.App.Test.Claude/TIP.App.Test.Claude.csproj`
- `TIP.App.Test.Claude/TestHelpers/ClaudeTestFixture.cs`
- `TIP.App.Test.Claude/Unit/Services/InboxConfigServiceTests.cs`
- `TIP.App.Test.Claude/Unit/Services/InboxRuleServiceTests.cs`
- `TIP.App.Test.Claude/Unit/Services/InboxProcessingServiceTests.cs`
- `TIP.App.Test.Claude/Unit/Services/ActionExecutors/OutlookActionExecutorTests.cs`
- `TIP.App.Test.Claude/Unit/Services/ActionExecutors/ZohoBooksActionExecutorTests.cs`
- `TIP.App.Test.Claude/Unit/Services/ActionExecutors/ZohoDeskActionExecutorTests.cs`
- `TIP.App.Test.Claude/Unit/Services/Ai/ClaudeAiServiceTests.cs`
- `TIP.App.Test.Claude/Unit/Services/Ai/RuleSuggestionServiceTests.cs`
- `TIP.App.Test.Claude/Unit/Services/Monitoring/ActivityLogServiceTests.cs`
- `TIP.App.Test.Claude/Unit/Services/ActionExecutors/ZohoCrmActionExecutorTests.cs`
- `TIP.App.Test.Shared/Unit/Services/Provider/ZohoBooksServiceTests.cs`
- `TIP.App.Test.Shared/Unit/Services/Provider/ZohoCrmServiceTests.cs`

### Phase 8: Seed Data and Migration
Create seed data scripts to populate initial inbox configs and rules based on current Email-Processing.md.

**Files to create:**
- `TIP.App.Database.Schema/scClaude/SeedData/SeedInboxConfigs.sql`
- `TIP.App.Database.Schema/scClaude/SeedData/SeedInboxRules.sql`

This translates the existing `Email-Processing.md` rules into database rows so the system starts with the same behavior as the current Claude scheduled tasks.

---

## 8b. Implementation Orchestration and Progress

### Wave Map

```
Wave 1 (sequential):
  Phase 1 - Database Schema & Entity Layer
  (Must complete before any service layer can query data)

Wave 2 (parallel):
  Phase 2 - Service Entity Layer (DTOs/Enums)
  Phase 3 - Shared Zoho Service Extensions
  (Both independent of each other, both depend on Phase 1 entities)

Wave 3 (sequential):
  Phase 4 - Claude Service Layer
  (Depends on Phase 2 DTOs and Phase 3 Zoho services)

Wave 4 (parallel):
  Phase 5 - UI Layer
  Phase 6 - Azure Function
  (Both consume the service layer. Independent of each other.)

Wave 5 (sequential):
  Phase 7 - Testing
  Phase 8 - Seed Data & Migration
  (Testing depends on all code being written. Seed data depends on schema being final.)
```

### Per-Component Progress Tracker

| Phase | Component | Status | Commit | Notes |
|-------|-----------|--------|--------|-------|
| 1 | scClaude schema (SSDT) — 5 tables (no activity log, that's Cosmos) | PENDING | | |
| 1 | InboxConfig.cs entity | PENDING | | |
| 1 | InboxRule.cs entity | PENDING | | |
| 1 | InboxRuleConditionGroup.cs entity | PENDING | | |
| 1 | InboxRuleCondition.cs entity | PENDING | | |
| 1 | InboxRuleAction.cs entity | PENDING | | |
| 1 | TipAppDataContext.cs DbSets (5) | PENDING | | |
| 1 | TipAppDataContext.Partial.cs Fluent API | PENDING | | |
| 1 | SSDT publish gate | PENDING | | |
| 1 | EF Core reverse-engineer gate | PENDING | | |
| 2 | Claude.Service.Entity.csproj | PENDING | | |
| 2 | Enums (6 files: ConditionField, MatchOperator, LogicalOperator, RuleActionType, InboxProcessingStatus, RunMode) | PENDING | | |
| 2 | ViewModels (6 files: Config, Rule, ConditionGroup, Condition, Action, Dashboard) | PENDING | | |
| 2 | Cosmos document models (5 files: EmailProcessingResultDocument, RunSummaryDocument, AiClassification, ActionExecutionResult, EmailClassificationResult) | PENDING | | |
| 2 | Constants.cs auth updates | PENDING | | |
| 3 | ZohoBooksService.cs | PENDING | | |
| 3 | ZohoCrmService.cs (search deals + add note) | PENDING | | |
| 3 | ZohoCrm entity classes (3 files) | PENDING | | |
| 3 | ZohoBooks entities | PENDING | | |
| 3 | DIAppSharedServices.cs update | PENDING | | |
| 4 | Claude.Service.csproj | PENDING | | |
| 4 | DIAppClaudeServices.cs | PENDING | | |
| 4 | InboxConfigService.cs | PENDING | | |
| 4 | InboxRuleService.cs | PENDING | | |
| 4 | InboxProcessingService.cs | PENDING | | |
| 4 | IActionExecutor + implementations | PENDING | | |
| 4 | IEmailClassificationService + ClaudeAiService | PENDING | | |
| 4 | RuleSuggestionService.cs | PENDING | | |
| 4 | CosmosClientService.cs | PENDING | | |
| 4 | ActivityLogService.cs (Cosmos read/write) | PENDING | | |
| 4 | SignalRNotificationService.cs | PENDING | | |
| 5 | Claude.UI.csproj | PENDING | | |
| 5 | DIAppClaudeUIServices.cs | PENDING | | |
| 5 | ClaudeDashboard.razor | PENDING | | |
| 5 | InboxMonitorList.razor | PENDING | | |
| 5 | InboxMonitorDetail.razor | PENDING | | |
| 5 | InboxActivityLog.razor | PENDING | | |
| 5 | RuleEditor.razor | PENDING | | |
| 5 | ActionEditor.razor | PENDING | | |
| 5 | RuleSuggestionDialog.razor | PENDING | | |
| 5 | Drag-to-reorder on rules table (InboxMonitorDetail) | PENDING | | |
| 5 | SignalR client integration (live progress on dashboard + detail pages) | PENDING | | |
| 5 | NavMenu.razor update | PENDING | | |
| 5 | Program.cs Portal update | PENDING | | |
| 5 | Auth policy registration | PENDING | | |
| 5 | Mockup verification (per page) | PENDING | | |
| 6 | Claude.Func.csproj | PENDING | | |
| 6 | InboxProcessorFunction.cs | PENDING | | |
| 7 | Test project setup | PENDING | | |
| 7 | InboxConfigService tests | PENDING | | |
| 7 | InboxRuleService tests | PENDING | | |
| 7 | InboxProcessingService tests | PENDING | | |
| 7 | ActionExecutor tests | PENDING | | |
| 7 | ZohoBooksService tests | PENDING | | |
| 7 | ZohoCrmService tests | PENDING | | |
| 7 | RuleSuggestionService tests | PENDING | | |
| 7 | ZohoCrmActionExecutor tests | PENDING | | |
| 8 | Seed data scripts | PENDING | | |

### Remaining Integration Items

| Item | Files | Status |
|------|-------|--------|
| Add Microsoft.Graph NuGet to Claude.Service | Claude.Service.csproj | PENDING |
| Add Microsoft.Azure.Cosmos NuGet to Claude.Service | Claude.Service.csproj | PENDING |
| Upgrade Mail.Read to Mail.ReadWrite in Entra ID App Registration | Azure Portal | PENDING |
| Register Entra ID app roles (ClaudeInboxUser, ClaudeInboxAdmin) | Azure Portal | PENDING |
| Add Claude auth policies to DIAppSharedUIServices | DIAppSharedUIServices.cs | PENDING |
| Add Claude.UI assembly to Portal MapRazorComponents | Program.cs | PENDING |
| Azure App Config: verify Zoho Books settings | Azure Portal | PENDING |
| Provision Cosmos DB account + `claude-activity` container | Azure Portal / IaC | PENDING |
| Add Cosmos DB connection string to Azure Key Vault | Azure Key Vault | PENDING |
| Add Anthropic API key to Azure Key Vault | Azure Key Vault | PENDING |
| Add Cosmos + Anthropic settings to SettingsConfiguration.cs | SettingsConfiguration.cs | PENDING |
| Provision Claude.Func Azure Function App | Azure Portal / IaC | PENDING |
| Add Claude.Func to deployment pipeline | docs/deploy | PENDING |
| Provision Azure SignalR Service instance | Azure Portal / IaC | PENDING |
| Add SignalR connection string to Azure Key Vault | Azure Key Vault | PENDING |
| Add SignalR settings to SettingsConfiguration.cs | SettingsConfiguration.cs | PENDING |
| Add Microsoft.Azure.SignalR NuGet to Claude.Func | Claude.Func.csproj | PENDING |
| Add Microsoft.AspNetCore.SignalR.Client NuGet to Claude.UI | Claude.UI.csproj | PENDING |
| Add Claude.Func Managed Identity to Portal App Registration | Azure Portal | PENDING |

---

## 9. Testing Strategy

**Coverage target:** 70% minimum per `coding-best-practices.md`.

**Must-test paths (100% coverage):**
- Rule condition evaluation (all operator types: Contains, StartsWith, Equals, Regex)
- Multi-rule matching (all matches fire in priority order, StopProcessing short-circuits)
- Pipeline execution order (actions execute in correct sequence)
- Payment validation (amount match, invoice found, open balance, exact match only, partial payment warning with amounts)
- CRM deal search (single match proceeds, multiple matches skip with warning, no match skip with warning)
- Auth policy enforcement (user sees only own inbox, admin sees all)
- Concurrent run protection (skip when in-progress, proceed when stale)
- Email dedup via Cosmos messageId check (same RunMode = skip, different RunMode = reprocess)
- Error handling (Graph API failures, Zoho API failures, partial pipeline execution)

**Mocking strategy:**
- Graph SDK: Mock `GraphServiceClient` calls using Moq
- Zoho APIs: Mock `HttpService` responses using `Moq.Contrib.HttpClient`
- Anthropic API: Mock `HttpService` responses for Claude API calls
- Cosmos DB: Mock `CosmosClient`/`Container` using Moq (no emulator in unit tests)
- Database: In-memory SQLite via `IDbContextFactory` mock
- SettingsService: Mock with test configuration values

**Test isolation:** All tests run without external services. No live Graph, Zoho, Anthropic, Cosmos, or database calls in unit tests.

**Dry Run mode testing:**
- Test that DryRun mode executes the full pipeline through fetch, classification, and rule evaluation (all read-only steps)
- Test that DryRun mode skips all write operations and generates SimulatedAction descriptions instead
- Test that Cosmos documents written in DryRun mode have `IsDryRun = true`
- Test that ActionExecutionResult.Status = "Simulated" for all actions in DryRun mode
- Test that the "Test Run Now" button triggers a single run with DryRun regardless of saved InboxConfig.RunMode
- Test that dashboard correctly filters and badges dry-run vs live results

**Naming convention:** `{MethodName}_{Scenario}_{ExpectedResult}` with Arrange-Act-Assert structure.

---

## 10. Changelog

| Date | Change | Reason |
|------|--------|--------|
| 2026-03-14 | Initial scope doc created | Scoping session with Albert |
| 2026-03-14 | Plan review updates | Admin-implies-user auth model. No shared mailbox whitelist. Mail.ReadWrite permission upgrade. Full filter engine with condition groups (AND/OR), expanded ConditionField enum (16 fields covering all Graph message properties), expanded MatchOperator enum (12 operators including Between, IsTrue/IsFalse). New InboxRuleConditionGroup entity added. LogicalOperator enum added. |
| 2026-03-14 | AI + Cosmos DB architecture | Added Anthropic Claude API for email classification and summarization (Decision #21). Moved activity logs and run history from SQL Server to Cosmos DB (Decision #22). New document models: EmailProcessingResultDocument, RunSummaryDocument with AiClassification embedded. Partition key: `{inboxConfigId}-{YYYY-MM}` with 90-day TTL default. Added ClaudeAiService, IEmailClassificationService, CosmosClientService to architecture. Removed InboxActivityLog from SQL schema (5 tables now, not 6). Updated integration items: Cosmos DB provisioning, Anthropic API key, Cosmos connection string. |
| 2026-03-14 | Dry Run test mode (Decision #23) | Added `RunMode` field to InboxConfig (Live/DryRun enum). Pipeline gates all write operations in DryRun mode — read operations (fetch, classify, evaluate) run normally. Added `IsDryRun` flag to both Cosmos document models. Added `SimulatedAction` field and "Simulated" status to ActionExecutionResult. Added RunMode enum to entity layer. Updated testing strategy with dry-run-specific test cases. UI additions: Live/DryRun toggle, "Test Run Now" button, amber badge for dry-run activity entries. |
| 2026-03-14 | Final plan review (Decisions #24-31) | Eight new decisions from scoping review: (24) All matching rules fire in priority order, StopProcessing is opt-in brake. (25) Concurrent run protection — skip with log entry + MaxRunDurationMinutes stale timeout. (26) DryRun email dedup via Cosmos messageId check, cross-RunMode reprocessing is intentional. (27) Dashboard queries Cosmos live, no materialization in V1. (28) Function uses same App Registration as Portal, Managed Identity. (29) Azure SignalR Service for real-time UI updates — Function sends progress events, Portal receives live. (30) CRM V1 = find deal + attach email as note with AI summary, field updates deferred V2. (31) AI rule suggestions — light template generation from recent Cosmos results, user reviews/customizes before saving. |
| 2026-03-14 | Scope changes from review | Moved INTO scope: drag-to-reorder on rules table, Azure SignalR real-time push, CRM deal executor (find + note), AI rule template suggestions, partial payment warnings with amounts. Moved OUT of scope: CRM field updates (V2), AI auto-rule creation without review, materialized dashboard aggregates. Updated architecture tree, phase file lists, progress tracker, integration items, and testing strategy. |

---

*This plan lives in `Source Control/Local` and is never synced to GitHub. It is the working reference for building the Claude Inbox Monitor feature in `tip-app-services` on the `feat/issue-52` branch.*
