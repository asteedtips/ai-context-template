---
type: context-file
parent: "`coding-index.md`"
summary: "TIPS Kernel Settings pattern ([YourSettingsConfig] hierarchy, service injection, Azure App Config key naming), [YourProject] config pattern, new library adoption protocol, and NuGet version management."
tags: [coding, config, settings, kernel, azure-app-config]
---

# Configuration & Settings Standards

> **Part of the the Coding Standards Graph (`coding-index.md`).** This file covers configuration patterns for both TIPS (Kernel Settings) and [YourOrg]. For the full standards index, see `coding-index.md`.

## 3.1 The Kernel Settings Pattern (TIPS, Mandatory)

All TIPS services use `[YourApp].Kernel.Settings` for configuration. This is the only sanctioned pattern. Do not use feature-specific `IOptions<T>` binding, standalone settings POCOs with `services.Configure<T>()`, or `IConfiguration` injection in service classes.

**Architecture:**

```
Azure App Configuration (SysCfg:* keys)
  ↓ bound via AddAzureAppConfiguration()
IOptionsSnapshot<[YourSettingsConfig]>
  ↓ injected into
[YourSettingsService] (scoped)
  ↓ injected into
Feature services (via constructor injection)
```

**How it works:**

1. `DIKernelSettings.AddKernel[YourSettingsService]s()` connects to Azure App Configuration, loads all keys under the `SysCfg:` prefix, wires up Key Vault references for secrets, and binds the tree to `[YourSettingsConfig]` via `IOptionsSnapshot<T>`.
2. `[YourSettingsService]` wraps `IOptionsSnapshot<[YourSettingsConfig]>` and exposes a `.Settings` property.
3. Services inject `[YourSettingsService]` and extract needed values into private `readonly` fields at construction time.
4. Dynamic refresh works via a sentinel key (`SysCfg:AlertCfgChangeSentinel`) — update the sentinel and all settings reload.
5. Label-based overrides handle environment differences: `(null)` for production, `DevTestOverride`, `EnvironmentOverride`, `Local`.

## 3.2 [YourSettingsConfig] Hierarchy

All configuration lives in a single strongly-typed POCO tree rooted in `[YourSettingsConfig]`. The hierarchy is organized by scope:

```
[YourSettingsConfig]
├── App                              ← Feature-specific operational config
│   ├── AppProvider                  ← External carrier/vendor integrations
│   │   ├── Bandwidth                ← AccountId, ApiUrlV1, ApiUrlV2, UserId, Password
│   │   └── Inteliquent              ← ApiKey, ApiSecret, ApiUrl, ApiUrlToken
│   ├── Snout                        ← PeenScheduleCron, RekeyConcurrencyLimit, RebootBatchSize
│   ├── MeridianIvr                  ← GatherTimeoutSeconds, MaxApiRetries, DefaultTransferNumber, Cooperatives
│   └── (flat properties)            ← MassNotifyCallDelay, database strings, email addresses, domain URLs
├── Shared                           ← Shared infrastructure and cross-feature vendor config
│   ├── SharedProvider
│   │   ├── DataFactory              ← ResourceGroupName, DataFactoryName
│   │   ├── [YourPlatform]               ← ApiKey, ApiPassword, ApiClientId, ApiClientSecret, ApiUrl, etc.
│   │   ├── PostMark                 ← ServerTokenLetterOfAuthorization, ServerTokenServiceCode, etc.
│   │   ├── Sip                      ← OutboundProxy, RegistrationExpirySeconds
│   │   ├── Speech                   ← ServiceEndpoint, KeyCredential
│   │   └── Zoho                     ← ApiClientId, ApiClientSecret, ApiRefreshToken, ApiTokenUrl
│   │       ├── Books                ← ApiUrl (Books-specific endpoint)
│   │       └── Desk                 ← DefaultDepartmentId, ApiUrl (Desk-specific endpoint)
│   └── (flat properties)            ← CosmosUrl, ServiceBusFQNS, StorageAccountUrl, SubscriptionId
├── AlertCfgChangeSentinel           ← Sentinel key for dynamic config refresh
└── ActiveEnvironment                ← "Development", "Test", "Production"
```

**Placement rules, where new config goes:**

- **Operational knobs for a feature** (timeouts, batch sizes, cron schedules) → `App.{FeatureName}`
- **External carrier/vendor credentials and endpoints used only by one feature** → `App.AppProvider.{VendorName}`
- **Vendor integrations used by multiple features** → `Shared.SharedProvider.{VendorName}`
- **Shared platform credentials** (like Zoho OAuth used by both Books and Desk) → parent level under `SharedProvider` with product-specific children
- **Infrastructure config** (Cosmos, Service Bus, storage) → `Shared` flat properties

## 3.3 Service Injection Pattern

Services receive `[YourSettingsService]` via constructor injection and extract settings into private `readonly` fields:

```csharp
public partial class BandwidthService(
    [YourSettingsService] settingsService,
    HttpService httpService,
    [YourLogService] logService) : BaseService(logService), ICarrierProvider
{
    private readonly [YourSettingsService] _settingsService = settingsService;
    private readonly string AccountId = settingsService.Settings.App.AppProvider.Bandwidth.AccountId;
    private readonly string UserId = settingsService.Settings.App.AppProvider.Bandwidth.UserId;
    private readonly string Password = settingsService.Settings.App.AppProvider.Bandwidth.Password;
    private readonly string ApiUrlV1 = settingsService.Settings.App.AppProvider.Bandwidth.ApiUrlV1;
    private readonly string ApiUrlV2 = settingsService.Settings.App.AppProvider.Bandwidth.ApiUrlV2;
}
```

**Rules:**
- Extract settings to private `readonly` fields during construction. This caches values and avoids repeated nested property lookups throughout the class.
- Never inject `IConfiguration`, `IOptions<T>`, or `IOptionsSnapshot<T>` directly into feature services. Always go through `[YourSettingsService]`.
- If a service needs settings from multiple branches of the hierarchy (e.g., both `App.Snout` and `Shared.SharedProvider.Zoho`), that's fine, extract both sets of fields from `[YourSettingsService]`.

## 3.4 Azure App Configuration Key Naming

Keys follow the colon-delimited hierarchy that maps directly to the `[YourSettingsConfig]` POCO tree:

```
SysCfg:{Branch}:{Class}:{Property}
```

Examples:
- `SysCfg:App:AppProvider:Bandwidth:AccountId` → `[YourSettingsConfig].App.AppProvider.Bandwidth.AccountId`
- `SysCfg:Shared:SharedProvider:Zoho:ApiClientId` → `[YourSettingsConfig].Shared.SharedProvider.Zoho.ApiClientId`
- `SysCfg:Shared:SharedProvider:Zoho:Desk:DefaultDepartmentId` → `[YourSettingsConfig].Shared.SharedProvider.Zoho.Desk.DefaultDepartmentId`
- `SysCfg:App:Snout:PeenScheduleCron` → `[YourSettingsConfig].App.Snout.PeenScheduleCron`
- `SysCfg:ActiveEnvironment` → `[YourSettingsConfig].ActiveEnvironment`

**Label organization:**
- **(null label)** — production values (default)
- **DevTestOverride** — development/test environment overrides
- **EnvironmentOverride** — enabled via `TIP_USE_ENVIRONMENT_OVERRIDE_CONFIG` env var
- **Local** — local development overrides, enabled via `TIP_IS_LOCAL_DEVELOPMENT` env var

## 3.5 Azure Functions and the Kernel Settings Stack

Azure Functions that share a service layer with the Portal (e.g., `Snout.Func`) must call `AddKernel[YourSettingsService]s()` in their `Program.cs` to get the full `[YourSettingsService]` dependency chain. This is mandatory when the Function's service layer depends on shared services (`[YourPlatform]Service`, `ZohoDeskService`, etc.) that inject `[YourSettingsService]`.

**Rule:** All Azure Functions in the TIPS solution call `AddKernel[YourSettingsService]s()`. No exceptions. Even if a Function only needs a subset of the configuration, the Kernel settings stack is the single entry point. This prevents configuration pattern drift between the Portal and Functions.

## 3.6 Adding New Configuration

When a new feature or provider needs configuration:

1. **Define the POCO class** — add a new nested class in `[YourSettingsConfig]` at the correct hierarchy level (see 3.2 placement rules).
2. **Add the App Config keys** — create keys in Azure App Configuration following the `SysCfg:` naming convention (see 3.4). Secrets go in Key Vault with App Config key vault references.
3. **No DI registration needed** — the Kernel settings binding automatically maps new POCO properties from the `SysCfg:` section. No `services.Configure<T>()` call required.
4. **Inject `[YourSettingsService]`** — the new service accesses its config through `settingsService.Settings.{Path}`.
5. **Add integration test coverage** — extend `SettingsTests.cs` to validate the new keys are populated in all environments.

## 3.7 Known Migration: MeridianIVR Settings Standardization

`MeridianIvr` currently uses a standalone `IOptions<MeridianIvrOptions>` pattern with `services.Configure<T>()` binding. This predates the Kernel settings standardization decision and must be migrated:

- Move `MeridianIvrOptions` properties into `[YourSettingsConfig].App.MeridianIvr`
- Switch `MeridianCisService` and `MeridianPaymentGatewayService` from `IOptions<MeridianIvrOptions>` to `[YourSettingsService]` injection
- Update `MeridianIvr.Func/Program.cs` to call `AddKernel[YourSettingsService]s()`
- Migrate App Config keys from `MeridianIvr:*` to `SysCfg:App:MeridianIvr:*`
- Delete `MeridianIvrOptions.cs` after migration

**Backlog:** The MeridianIVR multi-tenant `Cooperatives` dictionary config will eventually move to a SQL database table with a SNOUT management page for onboarding/managing cooperatives. Secrets per cooperative will use convention-based Key Vault naming (`meridianivr-{cooperativeId}-cis-username`) with startup caching. Until then, the dictionary structure remains in `[YourSettingsConfig]`.

## 3.8 [YourProject] Configuration Pattern

HAF does not use the TIPS Kernel settings stack. [YourProject] uses Azure App Configuration with `IOptions<T>` binding per feature.

**Rules for HAF:**
- Operational settings that may vary by environment (rate limits, timeouts, max message lengths, bulk send caps, polling intervals) belong in Azure App Configuration, not in `appsettings.json`. The `appsettings.json` file is for structural config (connection strings, logging levels, authentication authority URLs) that rarely changes between deployments.
- When adding a new feature with configurable values, create a settings POCO class (e.g., `ChatSettings`), bind it through `services.Configure<ChatSettings>(config.GetSection("Chat"))`, and inject via `IOptions<ChatSettings>`.
- Register the corresponding keys in Azure App Configuration for each environment (dev, test, prod). Don't rely on `appsettings.json` defaults in deployed environments.

## 3.9 New Library Adoption Protocol

When introducing a new library or framework into a codebase that already uses a different approach for the same concern (e.g., adding FluentValidation where DataAnnotations are used), include a developer orientation step:
- Add a brief section in the PR description or docs explaining why the library was chosen and where it applies.
- Include at least one example validator/implementation in the PR as a reference pattern.
- If the plan is to migrate the existing approach over time, document the migration scope and timeline. Don't leave it ambiguous whether old code should be converted.

## 3.10 Internal NuGet Package Version Management

When working on a feature branch that spans multiple weeks, internal NuGet packages (e.g., `[YourOrg].Kernel`, `[YourOrg].Kernel.Entity`, `[YourOrg].Kernel.Messaging`) may receive updates on `main` during the feature work. Before handing off or merging a long-lived feature branch:

1. Check the current version of internal packages on `main` or the latest published version.
2. Update all `.csproj` references in the feature branch to the latest stable version.
3. Build and test to confirm compatibility.

**Why:** If the kernel or shared packages get bug fixes or new features while the feature branch is open, merging the branch will revert those packages to the old version unless the branch is updated first. This creates silent regressions.

**Lesson learned (HAF Chat, March 2026):** The facility-chat branch pinned `[YourOrg].Kernel` at `1.1.17` for the duration of the project. By handoff, `1.1.20` was the current version. Tyler's team had to bump all 6 `.csproj` files (commit `611befa`). A pre-handoff version check would have caught it.

---

## Corrections Log

*Tracks issues found when following this file's instructions. Entries are added when a discrepancy is discovered and a fix is applied or proposed.*

| Date | What Failed | Root Cause | Fix Applied | ERRORS.md Ref |
|------|-------------|------------|-------------|---------------|

**Notes:**
<!-- Per-entry context that doesn't fit in the table. Format: "YYYY-MM-DD: [explanation]" -->
