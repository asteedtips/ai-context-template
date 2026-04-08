---
type: moc
summary: "Map of Content for all coding standards. Start here; follow WikiLinks to the specific topic needed for the current task."
tags: [coding, moc, index]
---

# Coding Standards Index

> **How to use this file:** Read the section descriptions below. Follow the WikiLink to whichever topic applies to your current task. Most tasks only need 1-2 nodes, not the entire graph. The descriptions contain enough context to decide whether you need the full file.

> **Cross-references:** `project-scoping-index.md` governs the scoping process that happens before coding starts. `security-practices.md` governs credential handling. `best-practices-creation.md` governs documentation output formats. [[banned-writing-styles]] applies to all written deliverables including code comments and README files. `github-actions-bp.md` covers CI/CD implementation details.

---

## Architecture & Structure

**`coding-architecture.md`** — Project layering rules (UI → Service → Entity → Database), naming conventions for projects, namespaces, classes, methods, and files. Entity/DTO mapping patterns (factory methods vs inline assignment). Enum placement convention (Dtos/Enums/ for cross-layer). Solution organization (.editorconfig, infra folder). **Read when:** creating new projects, reviewing layer references, naming anything, adding enums.

## Code Quality

**`coding-quality.md`** — DI registration (`DI{Feature}Services.cs` pattern), error handling (`BaseServiceResult<T>` wrapper), logging standards (Application Insights, LogUid correlation), async patterns (no `.Result`/`.Wait()`, CancellationToken), code comments (XML docs, TODO tracking), and code style (.editorconfig analyzers, explicit typing over `var`, braces on control flow). **Read when:** writing any service class, setting up DI, handling errors, adding logging, reviewing code style.

## Configuration & Settings

**`coding-config.md`** — TIPS Kernel Settings pattern (mandatory: `[YourSettingsService]`, `[YourSettingsConfig]` hierarchy, Azure App Config key naming, sentinel refresh). [YourProject] config pattern (`IOptions<T>` per feature). Service injection pattern (extract to `readonly` fields). New library adoption protocol. Internal NuGet version management. Known migration: MeridianIVR → Kernel Settings. **Read when:** adding config values, creating new features that need settings, working with Azure App Configuration, introducing new libraries.

## Database & EF Core

**`coding-database.md`** — `IDbContextFactory<T>` lifecycle (not injected DbContext), [YourProject] base class pattern (`[YourBaseRepository]`, `[YourBaseCrudService]`), schema organization, stored procedures, SSDT-first workflow (TIPS standard: define in SQL, publish, reverse-engineer), temporal table config (shadow properties in EF Core 9+), new entity configuration checklist, database-defaulted values. **Read when:** creating entities, writing repositories, modifying schema, working with temporal tables, configuring EF Core.

## Security

**Sections 5.1-5.3 remain in [[coding-best-practices]]** — Secrets management (Azure Key Vault, non-negotiable), authentication/authorization patterns (TIPS dual identity, [YourProject] JWT), CORS rules. Thin section; links to `security-practices.md` for full detail. **Read when:** handling secrets, setting up auth, configuring CORS.

## Testing

**`coding-testing.md`** — Coverage targets (70% floor, 100% on must-test paths), test project structure (one per bounded context), unit test patterns (Moq, naming conventions), integration tests, test isolation (static field contamination, InMemory EF key conflicts, transitive dependency awareness), API contract tests, dry run mode for external endpoints, reflection-based function entry point tests, untestable production code protocol, background task queue testing, grep-before-push for signature changes. **Read when:** writing any tests, setting up test projects, testing external API wrappers, dealing with unmockable code.

## API Design

**Sections 7.1-7.5 remain in [[coding-best-practices]]** — Route design (noun-based, kebab-case), request validation (FluentValidation/DataAnnotations), response patterns (`BaseServiceResult`, HTTP status codes), API documentation (XML docs, Swagger), controller routing convention (match existing pattern first). **Read when:** building REST APIs, adding controller routes.

## Blazor / UI

**`coding-blazor-ui.md`** — Component patterns (200-line limit, code-behind), CSS class builders, new routable page checklist (DI, nav entry, SharedNavigator, auth/layout, both platforms), page header consistency, dialog/form validation checklist, state management, error boundaries, mockup conformance hard gate (Extract → Build → Verify), MudBlazor gotchas (CS1660, `@using` collision), three-state filter pattern, SharedComponents layer check (MAUI reuse), bUnit testing. **Read when:** building any Blazor page or component, working with MudBlazor, verifying against mockups.

## CI/CD

**Sections 9.1-9.4.3 remain in [[coding-best-practices]]** — Pipeline requirements (build/test/upload per push), branch strategy (dev/main/feat), environment configuration, CI-first verification (not VM-first), Desktop Commander local builds (Section 9.3.1: required tool for all TIPS .NET builds, full macOS path `/opt/homebrew/bin/dotnet`, SSDT exception, repo root path), pre-push checklist, compile-run-fix loop, CI monitor gate and wave close rules, and session length caps with gate breaks (Section 9.4.3: one wave per session for Tier 3 features, mandatory gate break between waves). **Read when:** working with GitHub Actions, pushing code, closing waves, running local builds via Desktop Commander. See also `github-actions-bp.md` for full workflow templates.

## Performance & Reliability

**Sections 10.1-10.3 remain in [[coding-best-practices]]** — N+1 query prevention, Polly resilience, caching (`IMemoryCache`/`IDistributedCache`). Thin section. **Read when:** optimizing queries, adding retry logic, implementing caching.

## Documentation

**Sections 11.1-11.4 remain in [[coding-best-practices]]** — Architecture.md (repo-level living doc), README standards, ADR format, inline documentation rules. **Read when:** writing repo documentation, creating ADRs.

## Tracked Gaps

**Section 12 remains in [[coding-best-practices]]** — Known issues for TIPS (8 items) and [YourProject] (12 items) from the March 2026 code review, with resolution status. **Read when:** planning work items, checking what's already tracked.

## Good Patterns to Preserve

**Section 13 remains in [[coding-best-practices]]** — Patterns already working well in TIPS and [YourProject] that should be maintained, not refactored. **Read when:** reviewing code to understand what "good" looks like in these codebases.

## Verification Agent Protocol

**`coding-verification.md`** — Complexity-tiered sub-agent review system. Tier 1 (small): no agent. Tier 2 (medium): one code review agent. Tier 3 (large): two parallel agents. Agents check pattern compliance, mockup conformance, and external API rules. Also includes the pre-push staging verification gate (Section 14.5): `git status` check for unstaged modifications before every push. Runs after coding, before marking done. **Read when:** completing any code task to determine if verification agents should run, or before any git push.

---

*This index was created 2026-04-05 as part of the coding standards graph split. The original monolithic [[coding-best-practices]] (1,478 lines) was decomposed into topic-specific nodes for on-demand loading. Sections that remained thin (security, API design, CI/CD, performance, docs, gaps, good patterns) stay in the original file.*
