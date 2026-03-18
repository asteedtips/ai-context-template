# Coding Best Practices
**[YOUR NAME] | [YOUR TITLE] | [YOUR COMPANY]**
*Reference file for all code creation, review, and modification tasks*
*Last Updated: [DATE]*

---

> **How to use this file**: Read this file before writing, reviewing, or modifying any code. It defines the standards for your codebase. Where a specific context file has deeper guidance (e.g., `security/security-practices.md` for credential handling), this file links to it rather than duplicating.

> **Cross-references**: `security/security-practices.md` governs all credential and secrets management. `writing/best-practices-creation.md` governs documentation output formats. `writing/banned-writing-styles.md` applies to all written deliverables including code comments and README files.

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

### 2.6 Code Style

These rules apply across your codebase. Enforce via `.editorconfig` where possible.

**Explicit typing over `var`:** Use explicit types when declaring variables. Implicit typing (`var`) reduces readability when a developer returns to unfamiliar code or reviews a PR without IDE tooling. Exception: LINQ expressions where the return type is obvious from the method chain and would be verbose to spell out.

```csharp
// Preferred
[YOUR-ENTITY-TYPE] entity = await _service.GetEntityAsync(id, ct);
List<[YOUR-DTO-TYPE]> items = result.Data;

// Avoid
var entity = await _service.GetEntityAsync(id, ct);
var items = result.Data;
```

**Always use braces on control flow:** Even when the body is a single line, wrap `if`, `else`, `else if`, `for`, `foreach`, and `while` blocks in braces. No single-line conditionals.

```csharp
// Preferred
if (id == 0)
{
    return BadRequest("Invalid input.");
}

// Avoid
if (id == 0) return BadRequest("Invalid input.");
```

**`virtual` on all public service methods:** Every public method on a service class must be declared `virtual`. This is required for Moq to intercept methods when the service is mocked as a concrete class. Without `virtual`, Moq throws `NotSupportedException` on Setup/Verify calls, and with `MockBehavior.Loose` the real method executes against null dependencies causing `NullReferenceException`.

```csharp
// Required — every public service method
public virtual async Task<[YOUR-RESULT-DTO]> DoWorkAsync(int id, CancellationToken ct)

// Wrong — will break any test that mocks this service
public async Task<[YOUR-RESULT-DTO]> DoWorkAsync(int id, CancellationToken ct)
```

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

### 4.1 SSDT-First Schema Management (Optional Pattern for SQL Server Projects)

<!-- CUSTOMIZE: If your project uses SQL Server with SSDT (SQL Server Data Tools), adopt this pattern for new bounded contexts. Remove this section if you use a different database or prefer ORM-managed migrations. -->

If your project uses SQL Server, consider making the SSDT project the single source of truth for database schema. New bounded contexts define their schema in SSDT `.sql` files. An ORM reverse-engineering tool (e.g., EF Core Power Tools) generates entity classes from the published database.

**The gated workflow:**
1. Define tables, sequences, and seed scripts as `.sql` files in the SSDT project.
2. Register folder entries in the `.sqlproj` file.
3. Add seed script references to `Script.PostDeployment.sql`.
4. Publish the SSDT project to the target database.
5. **Reverse-engineer entity classes** from the published schema. This step is a gated dependency in the phase plan; call it out as its own line item so it doesn't get skipped. See `coding/project-scoping-bp.md` Section 8.
6. Delete any hand-written entities or ORM migration files. SSDT owns the schema; the reverse-engineer tool owns entity generation. No dual sources.

**Recommended conventions:**

<!-- CUSTOMIZE: Adjust these conventions to match your team's standards. The items below are a starting point. -->

- **Primary keys:** `INT` backed by sequences. Default constraint wires the PK to the sequence.
- **Uid column:** `UNIQUEIDENTIFIER` with `DEFAULT (NEWID())` and a unique index on every table.
- **Audit columns:** `ModifyUser`, `ModifyDate`, `CreateUser`, `CreateDate` on every table.
- **System versioning:** Temporal tables (`SYSTEM_VERSIONING = ON`) with `*Hist` history tables.
- **Constraint naming:** Consistent prefixes — `DF_` for defaults, `PK_` for primary keys, `FK_` for foreign keys, `CK_` for check constraints.
- **Lookup tables:** Status/type enums become SQL lookup tables seeded via `MERGE` scripts.
- **Soft delete:** `IsDeleted BIT NOT NULL DEFAULT 0` on every table.

---

## 5. Security Standards

### Secrets Management

**Non-negotiable:** All secrets live in your secret store. See `security/security-practices.md`.

**Database access is read-only by default.** AI agents may run `SELECT` queries freely but must not execute any write, update, delete, or DDL operation without explicit approval. This applies regardless of the credential's actual permission level. See the "Database Access — Read-Only by Default" section in `security/security-practices.md` for the full policy.

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

**InMemory database key conflicts:** When using in-memory databases for testing, auto-increment counters can collide across test methods. Fix: assign explicit IDs on all seeded entities using non-overlapping ranges per test class or fixture.

**Transitive dependency awareness:** Before adding a project reference from one test project to another for shared fixtures, check the transitive package dependencies. If the referenced test project pulls in large packages, inline the shared helper instead.

**Static field contamination between test classes:** Static fields (dictionaries, lists, counters) persist across test class instantiations within a single test run. If one test class populates a static collection and another test class asserts on its count, the tests pass in isolation but fail when run together. Fix: clear static state in the test class constructor so every class starts clean.

```csharp
// Pattern: clear static state in constructor
public class YourServiceTests
{
    public YourServiceTests()
    {
        // Reset any static collections that tests depend on
        StaticClass.SharedCollection.Clear();
    }
}
```

**Background task queue mocking:** When testing code that calls `IBackgroundTaskQueue.QueueBackgroundWorkItemAsync()`, the queued lambda is never executed in tests because Moq returns a completed `ValueTask` without running the delegate. Test that the queue was called (the scheduling decision), not the side effects of the lambda.

```csharp
// Good: verify queuing happened
_mockTaskQueue.Verify(
    q => q.QueueBackgroundWorkItemAsync(It.IsAny<Func<CancellationToken, ValueTask>>()),
    Times.Once);

// Bad: asserting side effects that only happen when the lambda runs
// The lambda never executes in unit tests — Moq returns completed ValueTask
```

### 6.6 Test Impact Analysis (Before Pushing Production Changes)

When production code changes alter method signatures (return types, parameters), class constructors, or remove/rename public methods, every test file that references those classes will break. **Before pushing production changes, grep the test directory for every changed class name and fix all test files in the same commit.** One pass, not iterative CI discovery.

```bash
# After changing [YOUR-SERVICE] constructor from 5 to 4 params:
grep -rn "[YOUR-SERVICE]" Tests/
# Fix EVERY file that appears — not just the one you remember
```

**What counts as a signature change that requires this sweep:**
- Constructor parameter added, removed, or reordered
- Method return type changed
- Method removed or renamed
- Method parameter list changed
- Access modifier changed (public → private/internal)

**Phase planning implication:** When building implementation plans that modify existing code with existing tests, include a "Test Impact" line item for every wave that changes production signatures. Do not defer test fixes to a later wave — they ship with the production change that breaks them.

### 6.7 Non-Virtual Third-Party Method Testing

Some third-party or kernel library methods are non-virtual and cannot be intercepted by Moq. When a Loose mock executes the real non-virtual method, it typically throws `NullReferenceException` because the mock's internal state is null. `MockBehavior.Strict` throws `NotSupportedException` on any unsetup call.

**Test patterns for code that calls non-virtual methods:**

1. **Verify the pipeline stopped before the call:** Set up conditions so the code path returns before reaching the non-virtual method. Verify the upstream repository calls happened.

2. **Assert the expected exception:** When testing the "happy path" that reaches the non-virtual call, assert that `NullReferenceException` is thrown. This proves the pipeline executed through all mockable steps and reached the send step. Verify upstream calls in addition to the exception.

```csharp
// Pattern: assert exception proves pipeline completed
Func<Task> act = () => _service.[YOUR-METHOD]();
await act.Should().ThrowAsync<NullReferenceException>();
_mockRepository.Verify(r => r.[YOUR-UPSTREAM-CALL](), Times.Once);
```

3. **Do not attempt to Setup or Verify the non-virtual method.** Moq will throw `NotSupportedException` regardless of `MockBehavior`.

### 6.8 Grep-Before-Push Rule

Any time a commit changes a public API surface (constructor, method signature, return type, class rename), run a grep across the entire repo for the affected class/method names before pushing. This catches cascading breaks in test files, DI registrations, and other consumers in one pass rather than through iterative CI failures.

This applies to both the VM workflow (grep locally) and the CI-first workflow (grep before commit). It is faster to spend 30 seconds grepping than to wait for a CI run to surface the same error.

### 6.9 API Contract Tests (External API Wrappers)

When a service wraps an external API, unit tests must verify the shape of the outgoing HTTP request, not just that a call was made. Assert on the URL path, query parameters, HTTP method, and request body structure in the mock handler.

A mock that only confirms "an HTTP call happened" will pass even when the wrong parameter is sent. The bug only surfaces in integration tests or production. Contract tests that assert on request shape catch these mismatches immediately.

**What to assert:**
- Correct HTTP method (GET vs POST vs PUT)
- Correct URL path and query parameters
- Correct request body structure and field names
- Correct parameter values (especially when the service maps between internal names and API-expected names)

### 6.10 Dry Run Mode for External Endpoint Integration

When a feature calls external APIs that modify data, the feature must support a **Dry Run mode** that lets the team validate the full pipeline without executing write operations against production or sandbox systems.

**Why this matters:** Most external services have no sandbox environment or limited sandbox parity. Testing against live endpoints risks creating bad records or moving real data. A dry-run capability lets the team validate rule evaluation, data extraction, and pipeline sequencing without side effects.

**Implementation pattern:**

1. **Config-level toggle.** Add a `RunMode` field (enum: `Live`, `DryRun`) to the feature's primary configuration entity. This is a persistent setting, not a one-time flag.
2. **Read/write boundary.** Every external integration already has a natural split between read operations (search, fetch, list) and write operations (create, update, move, delete). Read operations run identically in both modes. Write operations are gated by RunMode.
3. **Structured simulation logging.** In DryRun mode, each skipped write operation produces a structured log entry describing what *would* have happened, including the target system, the operation, and the payload.
4. **Results still persist.** DryRun results write to the same data store with an `IsDryRun = true` flag. This lets dashboards and activity logs display dry-run results with distinct visual treatment.
5. **One-shot test button.** The UI provides a "Test Run Now" button that triggers a single pipeline execution in DryRun mode regardless of the saved RunMode.
6. **Unit test coverage.** Tests must verify that DryRun mode (a) executes all read-only steps, (b) skips all write operations, (c) produces simulation descriptions, and (d) persists results with IsDryRun = true.

### 6.11 Reflection-Based Function Entry Point Testing

<!-- CUSTOMIZE: If your project uses Azure Functions, AWS Lambda, or similar serverless entry points, use this pattern. Remove if not applicable. -->

Serverless entry points (Azure Functions, Lambda handlers) are thin orchestration layers. The service logic is tested in service-layer unit tests. But the entry points have metadata that matters: route patterns, HTTP methods, authorization levels, trigger attributes. Bugs in these surface as 404s or auth failures in production.

**The reflection-based alternative:** Test the function's metadata through reflection instead of executing its logic. This verifies the contract without needing mocks for the full dependency tree.

**What reflection tests verify:**
- Function exists with the expected name
- Route pattern matches the expected path
- HTTP methods are correct
- Authorization level is correct
- Required parameters are present
- Return type matches expectations

**When to use:** For serverless entry points where the service layer is already tested. This is not a replacement for service-layer tests; it validates the deployment surface.

### 6.12 Untestable Production Code Protocol

When writing tests for existing production code, you'll sometimes hit methods that can't be mocked: non-virtual methods on concrete classes, sealed classes, services that create concrete dependencies internally, or static method calls.

**Don't skip the test. Don't rewrite the production code on a whim.** Follow this protocol:

1. **Try a workaround first.** Use a real instance with mocked sub-dependencies.
2. **If the workaround fails and the fix is small,** create a minimal refactor: extract an interface, make a method virtual, or inject the dependency.
3. **If the refactor is non-trivial,** stop and flag it. Document the limitation in the test plan and create a separate work item.
4. **For reflection tests,** the untestability constraint doesn't apply because they don't execute production code.

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

### UI Mockup Conformance — Hard Gate (When Mockups Exist)

<!-- CUSTOMIZE: Remove this section if your projects don't use HTML mockups for UI validation. Adjust the framework-specific examples (MudBlazor) to match your UI library. -->

When a project has approved HTML mockups (per `coding/project-scoping-bp.md` Section 5), every UI component must pass a three-step gate: Extract → Build → Verify. The component status cannot move to DONE until the verification artifact exists and shows all items passing.

**Step A — Extract Component Spec (before writing any code):**
Open the approved mockup. Produce a Component Spec Checklist — one line per visual element, written in your implementation framework's language (e.g., `MudSelect` not "a dropdown"). Write the checklist into the phase plan before coding starts. If no mockup exists for screens being built, the phase blocks until one is approved.

**Step B — Build:**
Normal implementation. The checklist from Step A is the spec.

**Step C — Verify (after code compiles, before marking DONE):**
Reopen the mockup. Walk the checklist line by line, marking each ✅ or ❌. Any ❌ means the component is not done. Fix all ❌ items, then re-run the full checklist (not just fixed items). Write the verification output into the phase plan.

<!-- CUSTOMIZE: Replace with your framework's component names -->
**Example checklist (MudBlazor):**
```
☐ @layout AppBaseLayout (not standalone container)
☐ Back-header: MudPaper with MudIconButton(Icon.ArrowBack)
☐ MudList with MudListItem per record
☐ FAB: MudFab Color.Primary for create action
☐ Empty state: MudAlert with call to action
```

**Mandatory phase plan structure for UI phases:**
```
X.1    Extract component spec from mockup — PENDING
...    (implementation items)
X.N-1  Verify against mockup — PENDING
X.N    CI verification — PENDING
```

This applies to both planned phases and reactive mid-PR phases.

### bUnit Component Testing

<!-- CUSTOMIZE: If your project uses Blazor with MudBlazor or similar component libraries, use this pattern. Adjust the fixture setup for your specific library. -->

For Blazor component tests, use bUnit. A single shared UI test project is preferred over one per bounded context.

**Fixture requirements:**
- `bUnit.TestContext` with your UI library's providers registered
- Mock service layer per context
- Loose JS interop mode for components that call JavaScript

**What bUnit tests verify:**
- Component renders without throwing given valid, empty, and error service responses
- Interactive elements trigger the right service calls
- Conditional rendering works (loading, empty, error states)
- Form validation messages appear for bad input
- Navigation redirects correctly after operations

**What bUnit tests do NOT verify:**
- Visual appearance (CSS, layout). That's manual or screenshot-based testing.
- Component library internals. Trust the library; test your usage of it.

<!-- CUSTOMIZE: Add a subsection here for any framework-version-specific migration gotchas
     your team has encountered. Example: .NET 10 changed JsonContent.Create() to default
     to camelCase serialization (JsonSerializerOptions.Web), breaking external API calls
     that expect PascalCase. Document the fix pattern and when to audit for it. -->

---

## 9. Performance & Reliability

- Batch database calls — no N+1 query patterns (loops with `await` calls)
- Use HTTP client retry policies (Polly or built-in) for external API calls
- Background services must handle their own exceptions
- Use caching for frequently-read, rarely-changed data with explicit expiration

### 9.4 Build Verification: CI-First, Not Local-First

**The primary verification gate is your CI/CD system, not local builds.** If your build system is resource-constrained or requires specific SDK versions, use CI as the primary gate. Rather than fighting those constraints, the standard workflow is:

1. Write or modify code locally.
2. Commit and push to a `feat/*` branch.
3. CI/CD pipeline builds and tests automatically.
4. Check results from the CI system.
5. If tests fail, fix locally, push again.

**When local builds still apply:** If your environment has the correct toolchain installed and the project is small enough to build locally (e.g., a Node.js project, a Python script, a small web app), a local build before commit is still valuable. For large compiled projects with many dependencies, CI is the gate.

**Pre-push checklist:**
- Code compiles conceptually (no obvious syntax issues, imports are correct, interfaces match)
- New test files follow the naming and structure conventions in Section 6
- **Grep-before-push completed** (Section 6.8) — if any public signatures changed, all test files referencing those classes are fixed in this commit
- Commit message describes the change clearly
- If the push includes workflow file changes (`.github/workflows/`, CI YAML, etc.), confirm credentials and permissions are correct

**CI-first means CI-only.** Do not fall back to local builds to diagnose failures when CI is available. Push to CI, read the results from the CI system, fix, push again. The CI log is the source of truth.

#### 9.4.1 Compile-Run-Fix Loop (Multi-Project Phases)

When a phase involves multiple test projects or multiple classes within a test project, the simple pre-push sequence above expands into an iterative gate loop. This is the per-project mechanics; for orchestration across a phased delivery plan, see `coding/project-scoping-bp.md` Section 8c.

**Per-project gate loop:**

1. **Write all test classes** for the project before compiling.
2. **Compile gate:** Build the test project. Fix every compiler error and warning.
3. **Run gate:** Run the full test project. Every test must pass.
4. **Fix loop:** If a test fails, read the failure output, diagnose, fix, and re-run.
5. **Commit** once the full project compiles and all tests pass.

**Gate failure protocol:**

If fixing a test failure requires changing production code (not just test code):
- **Bug the test exposed:** Fix the production code, commit separately with a clear message, note the bug in the plan.
- **Interface changed since the plan was written:** Update the test to match the current interface, note the deviation in the plan.
- **Code is untestable as-is:** See Section 6.12 for the untestable production code protocol.

#### 9.4.2 Phase-by-Phase CI Verification

When modifying existing code that already has tests (as opposed to writing net-new code), push production changes and their corresponding test updates together, then wait for CI to pass before moving to the next phase. Do not batch all phases into a single push.

**Why:** Batching works when everything is net-new (no existing tests to break). But when existing tests depend on the production code being changed, failures compound across phases and become harder to isolate.

**The rule:**
1. Complete production changes for one phase/wave.
2. Run the grep-before-push sweep (Section 6.8) to find and fix all impacted test files.
3. Commit production changes + test fixes together.
4. Push. Wait for CI to pass.
5. Move to the next phase.

**Exception:** If the phases are independent (different files, different test classes, no shared signatures), batching is acceptable. Use judgment — if a Phase 2 change could break a Phase 1 test, they must be sequential.

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

## 12. Verification Agent Protocol

When Claude is writing or modifying code, it can spin up independent sub-agents to review the work before marking it done. This catches pattern violations, UI conformance issues, and architectural drift that would otherwise surface in human code review. The protocol is complexity-gated — small changes don't need it, large changes require it.

### 12.1 Complexity Tiers

| Tier | Scope | Agent Strategy |
|------|-------|----------------|
| **Tier 1 — Small** | Single file, <50 lines changed, no UI | No verification agent. Review is built into the primary coding pass. |
| **Tier 2 — Medium** | Multiple files, new service methods, or any UI work | One verification agent after coding is complete. |
| **Tier 3 — Large** | New feature, multi-phase, touches external APIs or database schema | Two verification agents in parallel after each phase milestone. |

**How to determine the tier:** The scope is known from the phase plan before any code is written. If there's no phase plan, use the file count and change size to classify. When in doubt, round up.

### 12.2 What Each Agent Checks

**Code Review Agent (Tier 2 and Tier 3):**

<!--
  CUSTOMIZE: List the specific rules from your coding standards that the
  code review agent should check. Reference section numbers from this file.
  Example checklist items:
  - Layer reference direction (no upward refs)
  - DI registration pattern
  - Result wrapper pattern on service methods
  - No .Result or .Wait() on Tasks
  - Braces on all control flow
  - XML docs on public methods
  - No PII in log statements
  - AsNoTracking() on read-only queries
  - CancellationToken on async methods
-->

The agent receives the diff plus this best practices file and checks against your documented rules. It produces a pass/fail list. Any failure blocks the task from being marked done.

**UI Conformance Agent (Tier 2 with UI, Tier 3 with UI):**

Only runs when the change involves UI components and an approved mockup exists. Executes the mockup conformance gate:

- Opens the mockup file
- Walks the component spec checklist line by line against the implemented markup
- Produces pass/fail output for each checklist item

<!--
  CUSTOMIZE: Reference your UI standards section and any framework-specific
  checklists (e.g., new routable page checklist, component checklist).
-->

Any failure blocks the task from being marked done.

**External API Agent (Tier 3 only, when applicable):**

Only runs when the change touches external APIs. Checks:

- Dry Run mode implementation if no sandbox exists
- Retry policies on HTTP clients
- No hardcoded credentials
- Error handling on API responses

### 12.3 When Agents Run

Agents run **after coding is complete but before the task or phase is marked done.** They do not replace CI — CI validates compilation and test execution. Verification agents validate pattern compliance and conformance to standards that CI can't check.

**Sequence:**
1. Code the change
2. Run verification agent(s) based on tier
3. Fix any failures surfaced by agents
4. Push to feature branch (triggers CI)
5. CI validates compilation and tests
6. Mark phase/task done only after both agent review and CI pass

### 12.4 Agent Isolation

Verification agents run with worktree isolation when possible, giving them a clean copy of the repository. This prevents the reviewing agent from being influenced by uncommitted scratch work or partial changes in the working tree.

---

*Read this file before writing, reviewing, or modifying any code. For security guidance, see `security/security-practices.md`. For documentation formatting, see `writing/best-practices-creation.md`.*
*Last updated: 2026-03-17 — Added Section 12 (Verification Agent Protocol): complexity-tiered sub-agent review for code, UI conformance, and external API compliance.*


---

## Corrections Log

*Tracks issues found when following this file's instructions. Entries are added when a discrepancy is discovered and a fix is applied or proposed.*

| Date | What Failed | Root Cause | Fix Applied | ERRORS.md Ref |
|------|-------------|------------|-------------|---------------|

**Notes:**
<!-- Per-entry context that doesn't fit in the table. Format: "YYYY-MM-DD: [explanation]" -->
