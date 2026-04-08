---
type: context-file
parent: "`coding-index.md`"
summary: "Coverage targets (70% floor), test project structure, unit/integration test patterns, test isolation (static fields, InMemory EF, transitive deps), API contract tests, dry run mode, reflection-based function tests, untestable code protocol, background task queue testing, grep-before-push for signature changes."
tags: [coding, testing, coverage, mocking, dry-run, reflection-tests]
---

# Testing Standards

> **Part of the the Coding Standards Graph (`coding-index.md`).** This file covers all testing patterns and requirements. For the full standards index, see `coding-index.md`.
>
> **Worked example:** For a complete example of these testing standards applied across a multi-project .NET solution (8 phases, 592 tests, 6 test projects), see `Unit-Test-Implementation.md` in `[your-app-repo]/docs/feat-issue-[N]/`. That plan shows how coverage audits, phase ordering by risk, compile-run-fix gates, and per-phase result tracking work together in practice.

## 6.1 Coverage Target

**Minimum 70% code coverage** across all projects, measured by coverlet or a similar tool integrated into the CI pipeline. This is the floor, not the ceiling.

**Must-test paths (100% coverage required regardless of overall target):**
- Authentication and authorization logic
- Any code that handles money, billing, or financial calculations
- Data mutation operations (create, update, delete)
- Input validation logic
- Stored procedure wrappers and complex queries

## 6.2 Test Project Structure

One test project per bounded context, named `[YourApp].Test.{Context}`. Each test project mirrors the source project's internal structure. This keeps test projects focused, avoids transitive dependency bloat (see Section 6.5), and makes it clear which tests cover which feature.

```
[YourApp].Test.Shared/           ← tests for Shared.Service (identity, providers, helpers)
  ├── Unit/
  │   └── Services/
  │       ├── IdentityServiceTests.cs
  │       ├── [YourPlatform]ServiceTests.cs
  │       └── BandwidthServiceTests.cs
  ├── Integration/
  └── TestHelpers/
      └── SharedTestFixture.cs

[YourApp].Test.Kernel/           ← tests for Kernel.Extensions, Kernel.Entity, Kernel.Messaging
  ├── Unit/
  │   ├── Extensions/
  │   ├── Entity/
  │   └── Messaging/
  └── TestHelpers/

[YourApp].Test.MassNotify/       ← tests for MassNotify.Service + MassNotify.Func
  ├── Unit/
  │   ├── Services/
  │   └── Functions/
  └── TestHelpers/

[YourApp].Test.LOA/              ← tests for Loa.Service + entity validation
  ├── Unit/
  │   └── Services/
  └── TestHelpers/
```

**Exception: UI component tests.** bUnit tests go in a single shared `[YourApp].Test.UI` project (or alongside the bounded context's existing test project) rather than one UI test project per context. See `coding-blazor-ui.md` Section 8.5 for the rationale.

**General test project for cross-cutting integration tests.** `[YourApp].Test` can still hold integration tests that span multiple bounded contexts or test cross-cutting infrastructure (e.g., `SettingsTests.cs`, `LoaSubmissionTests` that exercise the full stack). But isolated unit tests belong in the context-specific test project.

## 6.3 Unit Tests

- Mock external dependencies (DbContext, HTTP clients, Azure services, third-party APIs). Use Moq or NSubstitute.
- One test class per source class. Test class name: `{SourceClass}Tests`.
- Test method naming: `{MethodName}_{Scenario}_{ExpectedResult}` — e.g., `SubmitLoa_WhenFilePersistenceFails_ThrowsAndDoesNotSaveRecord`.
- Each test should assert one thing. Multiple asserts are acceptable only when they verify different aspects of a single logical outcome.

## 6.4 Integration Tests

- Use `WebApplicationFactory<T>` for API integration tests.
- Test against a real database (SQL Server LocalDB or a test container) for data access integration tests. Don't mock the database in integration tests; that defeats the purpose.
- Clean up test data after each test run. Use transactions that roll back, or use a fresh database per test class.

**Current gap:** TIPS integration tests require real Azure services and credentials. Tests should be runnable without cloud dependencies using test doubles or containers.

## 6.5 Test Isolation

- Tests must not depend on external services (Azure, third-party APIs) by default. Use `IServiceCollection` replacement to swap real implementations for test doubles.
- Tests must not depend on execution order. Each test sets up its own state.
- Tests must not share mutable state. Static fields in test classes are a red flag.

**Static field contamination fix:** When production code uses static fields (like `ConcurrentDictionary` caches or rate limiters), those values persist across test class instantiations within a single test run. Clear them in the test class constructor:

```csharp
public class [FeatureService]Tests
{
    public [FeatureService]Tests()
    {
        // Static state from other test classes persists — clear it
        [StatefulService].RateLimits.Clear();
    }
}
```

If the static field has no public `Clear()` method, use reflection or refactor the production code to expose a test-only reset method behind an `internal` accessor with `[InternalsVisibleTo]`.

**InMemory EF Core key conflicts:** When using `UseInMemoryDatabase`, auto-increment counters can collide across test methods that seed different entity sets into separate in-memory databases. Fix: assign explicit IDs on all seeded entities using non-overlapping ranges (e.g., 100+, 200+, 300+ per test class or fixture). This avoids flaky test failures from PK collisions.

**Transitive dependency awareness:** Before adding a project reference from one test project to another (e.g., `Test.MassNotify` referencing `Test.Shared` for a shared fixture), check the transitive NuGet dependencies that come along for the ride. If the referenced test project pulls in large packages (the `CognitiveServices.Speech` SDK is 252MB), inline the shared helper instead. The MassNotify test project inlined `TestDbContextFactory` for this reason. A 5-line helper copy is cheaper than a 252MB transitive dependency.

## 6.6 API Contract Tests (External API Wrappers)

When a service wraps an external API ([YourPlatform], Bandwidth, Zoho, etc.), unit tests must verify the shape of the outgoing HTTP request, not just that a call was made. This means asserting on the URL path, query parameters, HTTP method, and request body structure in the mock handler.

**Why this matters:** A mock that only confirms "an HTTP call happened" will pass even when the wrong parameter is sent to the API. The bug only surfaces in integration tests or production.

**What to assert:**
- Correct HTTP method (GET vs POST vs PUT)
- Correct URL path and query parameters
- Correct request body structure and field names
- Correct parameter values (especially when the service maps between internal names and API-expected names)

**Lesson learned (SNOUT, March 2026):** `[YourApiWrapperService]` passed `MacAddress` to the NS reboot API endpoint where the `User` parameter was expected. Unit tests that only checked "reboot was called" passed. The bug was caught during a method analysis audit, not by the test suite. A contract test asserting the `user` parameter value would have caught it immediately.

## 6.7 Dry Run Mode for External Endpoint Integration

When a feature calls external APIs that modify data (Zoho CRM deal updates, Zoho Books payment recording, Zoho Desk ticket creation, Outlook mail moves, third-party webhooks, etc.), the feature must support a **Dry Run mode** that lets the team validate the full pipeline without executing write operations against production or sandbox systems.

**Why this matters:** Most external services (Outlook, Zoho CRM, Zoho Desk) have no sandbox environment. Zoho Books has one but it doesn't mirror production data. Testing against live endpoints risks creating bad records, moving real emails, or firing real webhooks. A dry-run capability lets the team validate rule evaluation, data extraction, and pipeline sequencing without side effects.

**Scoping gate (mandatory question):** During project scoping, when external API integrations are identified, explicitly ask: *"Do we have sandbox environments for each external system, or do we need a Dry Run mode?"* If any endpoint lacks a sandbox, the feature must include a run mode toggle. This question belongs in the decisions table, not buried in testing strategy.

**Implementation pattern:**

1. **Config-level toggle.** Add a `RunMode` field (enum: `Live`, `DryRun`) to the feature's primary configuration entity. This is a persistent setting, not a one-time flag.
2. **Read/write boundary.** Every external integration already has a natural split between read operations (search, fetch, list) and write operations (create, update, move, delete). Read operations run identically in both modes. Write operations are gated by RunMode.
3. **Structured simulation logging.** In DryRun mode, each skipped write operation produces a structured log entry describing what *would* have happened, including the target system, the operation, and the payload. Use a `SimulatedAction` field (human-readable description) and a `Status = "Simulated"` value distinct from Success/Failed/Skipped.
4. **Results still persist.** DryRun results write to the same data store (Cosmos, SQL, wherever results go) with an `IsDryRun = true` flag. This lets dashboards and activity logs display dry-run results with distinct visual treatment (amber badge, italic text, or similar).
5. **One-shot test button.** The UI provides a "Test Run Now" button that triggers a single pipeline execution in DryRun mode regardless of the saved RunMode. This lets a user test without changing the config back and forth.
6. **Unit test coverage.** Tests must verify that DryRun mode (a) executes all read-only steps, (b) skips all write operations, (c) produces SimulatedAction descriptions, and (d) persists results with IsDryRun = true.

**Lesson learned (Claude Inbox Monitor, March 2026):** The Inbox Monitor feature integrates with four external systems (Outlook, Zoho Books, Zoho CRM, Zoho Desk). Three have no sandbox. This pattern was designed during scoping to let the team validate the full email → classify → evaluate → act pipeline in development without creating real Desk tickets, recording real Books payments, or moving real Outlook emails.

## 6.8 Reflection-Based Function Entry Point Testing

Azure Function entry points are thin orchestration layers: they receive HTTP triggers, parse input, call the service layer, and return responses. The service logic is tested in service-layer unit tests (Sections 6.3, 6.6). But the function entry points themselves have metadata that matters: route patterns, HTTP methods, authorization levels, trigger attributes, and parameter types. Bugs in these surface as 404s, auth failures, or malformed responses in production.

**The problem with traditional mocking:** Function classes inject service-layer dependencies through constructors. Many of those services have non-virtual methods or concrete dependencies that Moq can't mock (see Section 6.9). Attempting to mock the full dependency tree for a thin entry point test creates a lot of fixture code for minimal value.

**The reflection-based alternative:** Test the function's metadata through reflection instead of executing its logic. This verifies the contract without needing any mocks.

**What reflection tests verify:**
- Function exists with the expected name
- Route pattern matches the expected path (`[Function("HandleGreeting")]`)
- HTTP methods are correct (GET+POST vs GET-only)
- Authorization level is correct (Function vs Anonymous)
- Required parameters are present (e.g., `CancellationToken`, `cooperativeId`)
- Return type matches expectations
- Timer trigger schedule is correct (for timer functions)

**When to use this pattern:** For `.Func` project entry points where the service layer is already tested. This is not a replacement for service-layer unit tests. It's an addition that validates the deployment surface.

**Lesson learned (Issue-[N], March 2026):** Phase [N] used this pattern across MeridianIvr.Func (14 tests for 17 functions), MassNotify.Func (10 tests), and Snout.Func (5 tests for timer trigger). The reflection approach caught metadata issues without requiring the 252MB+ dependency tree that full mocking would have demanded.

## 6.9 Untestable Production Code Protocol

When writing tests for existing production code, you'll sometimes hit methods that can't be mocked: non-virtual methods on concrete classes, sealed classes, services that create concrete dependencies internally (e.g., `new [YourEmailClient]()` inside a constructor), or static method calls.

**Don't skip the test. Don't rewrite the production code on a whim.** Follow this protocol:

1. **Try a workaround first.** Use a real instance of the class with mocked sub-dependencies (e.g., real `[YourLogService]` with mocked `ILogger<T>` and `TelemetryClient`). This often works when the unmockable method isn't the one you're testing.

2. **If the workaround fails and the fix is small,** create a minimal refactor to make the code testable: extract an interface, make a method virtual, or inject the dependency instead of newing it up. Commit the refactor separately from the tests, with a clear commit message explaining why.

3. **If the refactor is non-trivial,** stop and flag it. Document the limitation in the test plan, note which methods remain untested and why, and create a separate work item for the refactor. Don't let a testability refactor balloon into a mid-phase rewrite.

4. **For reflection tests** (see Section 6.8), the untestability constraint doesn't apply because reflection tests don't execute the production code.

**Known instances in TIPS (March 2026):**
- `[YourExternalService].ValidateUserRoleAssignments`: non-virtual on concrete class, can't mock with Moq. Tested structurally only.
- `[YourLogService].ProcessExceptionLog`: non-virtual. Workaround: real `[YourLogService]` instance with mocked logger dependencies.
- `[YourEmailService]`: creates concrete `[YourEmailClient]` internally. Deferred to a future refactor to introduce an injectable interface.

## 6.10 Background Task Queue Testing

When production code queues work via `IBackgroundTaskQueue.QueueBackgroundWorkItemAsync` (or similar fire-and-forget patterns), Moq's default loose behavior returns a completed `ValueTask` without executing the passed lambda. The lambda's side effects (repository calls, state changes) never run.

**Don't assert on the lambda's side effects.** Instead, verify that:
1. `QueueBackgroundWorkItemAsync` was called (proves the work was queued)
2. The initial state was set correctly before queuing (e.g., `Status = "Processing"`, `TotalRecipients = N`)
3. If the service returns a result, the result reflects the pre-queue state

```csharp
// Good: verify queuing happened
_mockTaskQueue.Verify(
    q => q.QueueBackgroundWorkItemAsync(It.IsAny<Func<CancellationToken, ValueTask>>()),
    Times.Once);

// Bad: asserting that a repository method inside the lambda was called
// This will always fail because the lambda never executes
_mockRepo.Verify(r => r.UpdateStatusAsync(...), Times.Once); // FAILS
```

**If you need to test the lambda's logic,** extract it into a separate testable method and test that method directly. Don't try to make Moq execute the queued work.

## 6.11 Grep-Before-Push for Signature Changes

When a method signature changes in production code (constructor params added/removed, return type changed, method renamed or deleted), test files referencing that method will break. CI will catch this, but you can save a round-trip by grepping first.

**Before pushing any signature change:**

```bash
# Find all test references to the changed class/method
grep -r "ClassName" Tests/ --include="*.cs" -l
# Or for constructor changes specifically
grep -r "new ClassName(" Tests/ --include="*.cs" -l
```

Update every file that appears in the results before committing. This is especially true for constructor changes, which can affect 4-5 test files that each create the service with `new`.

**Lesson learned (HAF chat, March 2026):** `[YourNotificationService]` constructor changed from 5 to 4 params. First push fixed one test file. CI showed 3 more failures in different test classes. Each failure required a separate commit/push/wait cycle. A single grep would have caught all four.

---

## Corrections Log

*Tracks issues found when following this file's instructions. Entries are added when a discrepancy is discovered and a fix is applied or proposed.*

| Date | What Failed | Root Cause | Fix Applied | ERRORS.md Ref |
|------|-------------|------------|-------------|---------------|

**Notes:**
<!-- Per-entry context that doesn't fit in the table. Format: "YYYY-MM-DD: [explanation]" -->
