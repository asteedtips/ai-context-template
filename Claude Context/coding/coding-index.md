# Coding Standards Index

> **How to use this file:** Read the section descriptions below. Follow the link to whichever topic applies to your current task. Most tasks only need 1-2 nodes, not the entire graph. The descriptions contain enough context to decide whether you need the full file.

> **Cross-references:** `project-scoping-index.md` governs the scoping process that happens before coding starts. `security/security-practices.md` governs credential handling. `writing/best-practices-creation.md` governs documentation output formats. `writing/banned-writing-styles.md` applies to all written deliverables including code comments and README files. `github-actions-bp.md` covers CI/CD implementation details.

---

## Architecture & Structure

**`coding-architecture.md`**  -  Project layering rules (UI / API → Service → Entity → Database), naming conventions for projects, namespaces, classes, methods, and files. Entity/DTO mapping patterns (factory methods vs inline assignment). Enum placement convention for shared contracts. Solution organization (.editorconfig, infra folder). **Read when:** creating new projects, reviewing layer references, naming anything, adding enums.

## Code Quality

**`coding-quality.md`**  -  Dependency injection (extension method pattern), error handling (result wrapper pattern), logging standards (centralized telemetry, correlation IDs), async patterns (no `.Result`/`.Wait()`, CancellationToken), code comments (documentation standards, TODO tracking), and code style (.editorconfig analyzers, explicit typing over `var`, braces on control flow). **Read when:** writing any service class, setting up DI, handling errors, adding logging, reviewing code style.

## Configuration & Settings

**`coding-config.md`**  -  Configuration management patterns, service injection pattern, environment-specific settings, feature flag management, external vendor config structure. Note the difference between operational config (varies by environment) vs structural config (rarely changes). **Read when:** adding config values, creating new features that need settings, working with environment-specific behavior, introducing new external integrations.

## Database & EF Core

**`coding-database.md`**  -  DbContext lifecycle and factory patterns, repository base class architecture, schema organization, stored procedures, entity configuration checklists, temporal tables and audit trails, new entity setup workflow. **Read when:** creating entities, writing repositories, modifying schema, working with temporal tables, configuring EF Core.

## Security

**Sections 5.1-5.3 remain in `coding-best-practices.md`**  -  Secrets management (best practices), authentication/authorization patterns, CORS rules. Links to `security/security-practices.md` for full detail. **Read when:** handling secrets, setting up auth, configuring CORS.

## Testing

**`coding-testing.md`**  -  Coverage targets and measurement, test project structure, unit test patterns (mocking, naming conventions), integration tests, test isolation strategies (static field contamination, context key conflicts, transitive dependency awareness), API contract tests, external endpoint handling, reflection-based tests, dealing with unmockable production code, background task testing, pre-push verification checklist. **Read when:** writing any tests, setting up test projects, testing external APIs, testing hard-to-mock code.

## API Design

**Sections 7.1-7.5 remain in `coding-best-practices.md`**  -  Route design (resource-oriented, naming patterns), request validation standards, response patterns and HTTP status codes, API documentation (XML comments, OpenAPI/Swagger), controller routing conventions. **Read when:** building REST APIs, adding controller routes, designing API contracts.

## Blazor / UI

**`coding-blazor-ui.md`**  -  Component architecture (size limits, code-behind pattern), CSS utilities, routable page checklist (DI, navigation, layout, authentication), header consistency, dialog and form validation, state management patterns, error boundaries, mockup conformance process (Extract / Build / Verify), UI framework patterns and gotchas, filter patterns, component reuse strategy. **Read when:** building any Blazor page or component, working with UI frameworks, verifying against mockups.

## CI/CD

**Sections 9.1-9.4.2 remain in `coding-best-practices.md`**  -  Pipeline requirements (build/test steps), branch strategy (dev/main/feature), environment configuration, primary verification gate, pre-push checklist, compile-run-fix loop, CI monitoring and wave close rules. **Read when:** working with GitHub Actions, pushing code, closing waves. See also `github-actions-bp.md` for full workflow templates.

## Performance & Reliability

**Sections 10.1-10.3 remain in `coding-best-practices.md`**  -  Query optimization and N+1 prevention, resilience patterns (retries, timeouts), caching strategies. **Read when:** optimizing queries, adding retry logic, implementing caching.

## Documentation

**Sections 11.1-11.4 remain in `coding-best-practices.md`**  -  Repo-level architecture documentation, README standards, Architecture Decision Records (ADRs), inline documentation rules. **Read when:** writing repo documentation, creating ADRs.

## Tracked Gaps

**Section 12 remains in `coding-best-practices.md`**  -  Known issues from recent code reviews, with resolution status and severity. **Read when:** planning work items, checking what's already tracked.

## Good Patterns to Preserve

**Section 13 remains in `coding-best-practices.md`**  -  Patterns already working well in your codebase that should be maintained, not refactored. **Read when:** reviewing code to understand what "good" looks like.

## Verification Agent Protocol

**`coding-verification.md`**  -  Complexity-tiered code review system. Tier 1 (small): no agent. Tier 2 (medium): one code review agent. Tier 3 (large): two parallel agents. Agents check pattern compliance, mockup conformance, and external API contract rules. Runs after coding, before marking done. **Read when:** completing any code task to determine if verification agents should run.

---

*This index was created in [DATE] as part of the coding standards graph split. The original monolithic file was decomposed into topic-specific nodes for on-demand loading. Sections that remained thin (security, API design, CI/CD, performance, docs, gaps, good patterns) stay in the original file.*
