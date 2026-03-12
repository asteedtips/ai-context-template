# Coding Best Practices
**[YOUR NAME] | [YOUR TITLE] | [YOUR COMPANY]**
*Reference file for all code creation, review, and modification tasks*
*Last Updated: [DATE]*

---

> **How to use this file**: Read this file before writing, reviewing, or modifying any code. It defines the standards for your codebase. Where a specific context file has deeper guidance (e.g., `security-practices.md` for credential handling), this file links to it rather than duplicating.

> **Cross-references**: `security-practices.md` governs all credential and secrets management. `best-practices-creation.md` governs documentation output formats. `banned-writing-styles.md` applies to all written deliverables including code comments and README files.

---

## 1. Architecture Standards

<!--
  CUSTOMIZE: Define your project layering, naming conventions, and solution organization.

  Example layered architecture:
  ```
  Portal / API  →  Service  →  Service.Entity  →  Database
     (UI/HTTP)     (Logic)     (DTOs/ViewModels)   (Data Access)
  ```

  Define rules like:
  - No upward references (data layer never references UI layer)
  - Shared code goes in a shared project
  - Business logic belongs in the service layer, not in API controllers
-->

### Naming Conventions

<!--
  CUSTOMIZE: Define your project, namespace, class, method, and file naming patterns.

  Examples:
  - Projects: `{Product}.{Feature}.{Layer}`
  - Classes: Entity=singular nouns, Service=`{Feature}Service`, DTO=suffix `Dto` or `Vm`
  - Methods: Async methods end with `Async` when sync overload exists
  - Files: One class per file, file name matches class name
-->

---

## 2. Code Quality Standards

### Dependency Injection

- Register services through extension methods on `IServiceCollection`
- Each feature owns its own DI registration method
- Constructor injection only — no service locator pattern
- Use `AddScoped` for services that depend on database contexts

### Error Handling

- All service methods return a result wrapper (success/fail + data + error message)
- Don't throw exceptions for expected business failures
- Catch blocks must re-throw, return a failure result, or wrap in a domain exception. **Never swallow exceptions silently.**
- Use structured logging (`ILogger<T>`), not `Console.WriteLine`
- Global exception middleware should catch unhandled exceptions and return consistent error responses

### Logging

- Use a centralized telemetry service (Application Insights, Datadog, etc.)
- Generate a correlation ID per operation and include in every log entry
- Log at `Information` for operation start/completion, `Warning` for recoverable issues, `Error` for failures
- Never log PII or secrets. Log entity IDs and correlation IDs instead.

### Async Patterns

- All I/O-bound operations must be async
- No `.Result` or `.Wait()` calls on Tasks (deadlock risk)
- Use `CancellationToken` parameters on async methods and pass through to all I/O calls

### Code Comments

- Comment *why* the code does something non-obvious, not what it does
- XML doc comments on all public methods in service and entity projects
- TODO/HACK/FIXME comments must have a corresponding tracked work item

---

## 3. Configuration & Settings Standards

<!--
  CUSTOMIZE: Define your centralized configuration pattern. The goal is ONE way to access
  configuration across your entire solution — no per-feature IOptions<T>, no IConfiguration
  injection in services, no standalone settings POCOs with services.Configure<T>().

  Key decisions to document:
  - Where config is stored (Azure App Configuration, appsettings.json, AWS Parameter Store, etc.)
  - How it's bound to code (single POCO tree, IOptions, custom service wrapper)
  - The hierarchy for organizing settings (by feature, by environment, by provider)
  - How secrets integrate (Key Vault references, environment variables, etc.)
  - How Azure Functions / background workers access the same config as the main app
  - The process for adding new configuration (what to create, where, and how to test)

  Example architecture:
  ```
  Config Store (e.g., Azure App Configuration)
    ↓ bound at startup
  Strongly-typed POCO tree (e.g., SettingsConfiguration)
    ↓ wrapped by
  SettingsService (scoped DI service)
    ↓ injected into
  Feature services (via constructor injection)
  ```

  Example hierarchy:
  ```
  SettingsConfiguration
  ├── App                    ← Feature-specific operational config (timeouts, batch sizes)
  │   ├── AppProvider        ← External vendor integrations used by one feature
  │   └── (feature classes)  ← Operational knobs per feature
  ├── Shared                 ← Shared infrastructure and cross-feature vendor config
  │   └── SharedProvider     ← Vendor integrations used by multiple features
  └── ActiveEnvironment      ← Environment discriminator
  ```

  Example service injection:
  ```csharp
  public partial class ExampleService(
      SettingsService settingsService,
      LogService logService) : BaseService(logService)
  {
      private readonly string ApiUrl = settingsService.Settings.App.AppProvider.Example.ApiUrl;
  }
  ```

  Rules to enforce:
  - Services extract settings into private readonly fields at construction time
  - Never inject IConfiguration or IOptions<T> directly into feature services
  - All Azure Functions call the same settings initialization as the main app
  - New config = new POCO property + new config store key + integration test validation
-->

---

## 4. Database Standards

<!--
  CUSTOMIZE: Define your database access patterns.

  Common topics:
  - ORM lifecycle (DbContext per operation via factory, not per request)
  - Read-only queries use `.AsNoTracking()` or projections
  - Stored procedures for batch operations
  - Migration naming and ordering
  - Schema organization
-->

---

## 5. Security Standards

### Secrets Management

**Non-negotiable:** All secrets live in your secret store. See `security-practices.md`.

**Database access is read-only by default.** AI agents may run `SELECT` queries freely but must not execute any write, update, delete, or DDL operation without explicit approval. This applies regardless of the credential's actual permission level. See the "Database Access — Read-Only by Default" section in `security-practices.md` for the full policy.

- Config files may contain non-secret values (URLs, feature flags, timeouts). Never client secrets, API keys, tokens, or passwords.
- Connection strings in production should use Managed Identity where possible.

### Authentication & Authorization

<!--
  CUSTOMIZE: Define your auth patterns.

  Common rules:
  - Every controller action must have [Authorize] or explicitly [AllowAnonymous]
  - Resource ownership checks: verify the requesting user has access to the specific resource
  - Rate limiting on auth endpoints and public APIs
  - Cookies: SecurePolicy=Always, HttpOnly=true, SameSite attributes
-->

---

## 6. Testing Standards

### Coverage Target

**Minimum 70% code coverage** across all projects.

**Must-test paths (100% coverage required):**
- Authentication and authorization logic
- Any code that handles money or financial calculations
- Data mutation operations (create, update, delete)
- Input validation logic

### Test Structure

- Unit tests: Mock external dependencies. One test class per source class.
- Integration tests: Test against a real database. Use `WebApplicationFactory<T>` for API tests.
- Test isolation: No dependency on external services, execution order, or shared mutable state.
- Test naming: `{MethodName}_{Scenario}_{ExpectedResult}`

---

## 7. API Design Standards

<!--
  CUSTOMIZE: Define your REST API conventions if applicable.

  Common rules:
  - Routes: noun-based, kebab-case (`/api/users/{id}/gym-access`)
  - HTTP methods for verbs (GET=read, POST=create, PUT=update, DELETE=remove)
  - Validate all incoming DTOs (FluentValidation or DataAnnotations)
  - Consistent response wrappers with correlation IDs
  - Version APIs from the start (`/api/v1/...`)
-->

---

## 8. CI/CD Standards

<!--
  CUSTOMIZE: Define your build/deploy pipeline requirements.

  Common requirements:
  1. Build with warnings-as-errors
  2. Run tests with coverage collection; fail if below threshold
  3. Security scan for vulnerable dependencies
  4. Deploy to staging on merge to main; production requires manual approval

  Branch strategy:
  - `main` = production; no direct pushes
  - Feature branches: `feature/{description}`
  - PRs require approval and passing checks
-->

---

## 9. Performance & Reliability

- Batch database calls — no N+1 query patterns (loops with `await` calls)
- Use HTTP client retry policies (Polly or built-in) for external API calls
- Background services must handle their own exceptions
- Use caching for frequently-read, rarely-changed data with explicit expiration

---

## 10. Known Gaps — Tracked Issues

<!--
  CUSTOMIZE: Track known issues in your codebase here.
  Review this section during code reviews and sprint planning.

  Example:
  | # | Issue | Severity | File Reference |
  |---|---|---|---|
  | 1 | Silent exception swallowing in [service] | High | `path/to/file.cs` |
  | 2 | No unit tests for [feature] | Medium | `path/to/tests/` |
  | 3 | Hardcoded secrets in config | Critical | `appsettings.json` |
-->

---

## 11. Patterns to Preserve

<!--
  CUSTOMIZE: Document patterns that are already working well.
  Reference these during code reviews to maintain consistency.

  Example:
  - BaseService abstract class with centralized logging
  - DI registration via extension methods
  - Result wrapper pattern for service returns
  - Fluent API entity configurations in dedicated files
-->

---

*Read this file before writing, reviewing, or modifying any code. For security guidance, see `security-practices.md`. For documentation formatting, see `best-practices-creation.md`.*
*Last updated: [DATE]*
