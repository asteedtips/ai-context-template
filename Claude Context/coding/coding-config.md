# Configuration & Settings Standards

> **Part of the Coding Standards Graph.** This file covers configuration patterns, service injection, and environment-specific behavior. For the full standards index, see `coding-index.md`.

## 3.1 Configuration Management Pattern

All configuration follows a hierarchical, strongly-typed structure. Define a POCO tree that mirrors your configuration branches:

<!-- CUSTOMIZE: Define your configuration hierarchy. Example:

```
ApplicationConfiguration
├── App                                  ← Feature-specific operational config
│   ├── ExternalServices
│   │   ├── PaymentGateway              ← ApiKey, Endpoint, Timeout
│   │   └── NotificationService         ← ApiKey, Endpoint, MaxRetries
│   └── Features
│       ├── ReportGeneration            ← BatchSize, TimeoutMinutes, Schedule
│       └── Authentication              ← TokenExpiryMinutes, RefreshTokenDays
├── Shared                              ← Shared infrastructure config
│   ├── Database                        ← ConnectionString, CommandTimeout
│   ├── Logging                         ← Level, Retention, Endpoint
│   └── Cache                           ← Endpoint, EvictionPolicy, TtlMinutes
└── Environment                         ← "Development", "Staging", "Production"
```
-->

**Architecture pattern:**

```
Configuration Source (files, environment variables, cloud config service)
  ↓
IOptions or IConfiguration binding
  ↓
Centralized SettingsService (scoped)
  ↓
Feature services (injected via constructor)
```

## 3.2 Service Injection Pattern

Services receive a configuration/settings service via constructor injection and extract needed values into private readonly fields:

<!-- CUSTOMIZE: Show the pattern for your stack. Example with Azure App Configuration:

```csharp
public class PaymentService(
    SettingsService settingsService,
    HttpService httpService,
    ILogger<PaymentService> logger) : BaseService(logger)
{
    private readonly string _apiKey = settingsService.Settings.App.ExternalServices.PaymentGateway.ApiKey;
    private readonly string _endpoint = settingsService.Settings.App.ExternalServices.PaymentGateway.Endpoint;
    private readonly int _timeoutSeconds = settingsService.Settings.App.ExternalServices.PaymentGateway.TimeoutSeconds;
}
```
-->

**Rules:**
- Extract settings to private readonly fields during construction. This caches values and avoids repeated nested property lookups throughout the class.
- Never inject `IConfiguration` or raw `IOptions<T>` directly into feature services. Go through a centralized settings service.
- If a service needs settings from multiple branches, extract all needed fields from the settings service. That's fine.

## 3.3 Operational vs Structural Config

**Operational config varies by environment:** rate limits, timeouts, batch sizes, cron schedules, external API endpoints, feature flags, retry policies. This config belongs in a cloud config service or environment-specific configuration files that can be updated without code changes.

**Structural config rarely changes:** database connection strings (production connection string itself doesn't change, only which environment it points to), logging levels (changes only during troubleshooting), authentication authority URLs (change only if moving to a different identity provider). This config belongs in `appsettings.json` or source-controlled configuration.

**Rule:** If a value might need to change between deployments without code changes, it's operational config. Use environment-specific overrides or a cloud config service. If a value is part of how the system is structured, it's structural config.

<!-- CUSTOMIZE: Add guidance on how your team separates operational from structural config. Example:

All operational values live in Azure App Configuration with environment-specific sections. Structural config stays in appsettings.json. Database connection strings are structural but environment-specific, stored in Key Vault and injected via managed identity at deployment time.
-->

## 3.4 Environment-Specific Overrides

Configuration should support multiple environments (development, staging, production) without code changes.

<!-- CUSTOMIZE: Document your environment override strategy. Example:

**Using Azure App Configuration:**
- Keys in the **(null)** label are production defaults.
- Keys in the **Staging** label override production values for staging deployments.
- Keys in the **Development** label override for local development.
- Keys in the **Local** label are machine-specific and never committed to source control.

**Using appsettings files:**
- `appsettings.json`  -  shared defaults
- `appsettings.Development.json`  -  local development overrides
- `appsettings.Staging.json`  -  staging overrides (if needed)
- `.gitignore` includes `appsettings.Local.json` for machine-specific secrets
-->

## 3.5 Adding New Configuration

When a feature needs new configuration:

1. **Define the POCO class**  -  add a new nested class at the correct hierarchy level.
2. **Add the source keys**  -  create keys in your config source (environment variables, `appsettings.json`, cloud config service, etc.) following your naming convention.
3. **Register if needed**  -  if using `IOptions<T>` binding, add the registration in `Program.cs` or a DI extension method. If using a centralized settings service, no additional registration is needed.
4. **Inject the settings service**  -  the new service accesses its config through dependency injection.
5. **Add test coverage**  -  verify the new keys are loaded in all environments.

## 3.6 External Vendor Integration Configuration

When integrating with external services:

<!-- CUSTOMIZE: Define how vendor/external service config should be organized. Example:

**API Keys and secrets:** All API keys, OAuth tokens, and authentication credentials go in Key Vault or a secrets vault. Reference them via Key Vault URIs in your config source. Never commit credentials to source control.

**Endpoints and URLs:** External API endpoints belong in config, not hardcoded. They may change between environments (sandbox vs production endpoints) or may need to be updated without redeploying.

**Rate limits and timeouts:** Put thresholds that you'll tune based on production behavior into config. Example: external API rate limit is 1,000 requests per hour, but your code implements a batching strategy with a configurable batch size and timeout.

**Feature-specific vendor config:** If a vendor integration is used by only one feature, nest it under that feature's config branch. If multiple features use the same vendor (e.g., a shared payment processor), nest it under a Shared branch.
-->

---

## Corrections Log

*Tracks issues found when following this file's instructions.*

| Date | What Failed | Root Cause | Fix Applied |
|------|-------------|------------|-------------|

