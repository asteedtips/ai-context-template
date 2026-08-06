---
type: context-file
parent: "`coding-index.md`"
summary: "DI registration patterns, error handling (BaseServiceResult), logging standards, async patterns, code comments, and code style rules (.editorconfig, explicit typing, braces)."
tags: [coding, quality, DI, error-handling, logging, style]
---

# Code Quality Standards

> **Part of the the Coding Standards Graph (`coding-index.md`).** This file covers dependency injection, error handling, logging, async patterns, and code style. For the full standards index, see `coding-index.md`.

## 2.1 Dependency Injection

**Pattern (already in use, enforce it):** Register services through extension methods on `IServiceCollection`:

```csharp
public static class DI[Feature]Services
{
    public static IServiceCollection Add[FeatureService]s(
        this IServiceCollection services, IConfiguration config)
    {
        services.AddDbContextFactory<[YourDbContext]>(options => ...);
        services.AddScoped<[FeatureService]>();
        return services;
    }
}
```

**Rules:**
- Every feature owns a `DI{Feature}Services.cs` extension method. No service registration happens in `Program.cs` directly (beyond calling the extension methods and framework-level middleware).
- Use `AddScoped` for services that depend on DbContext. Use `AddSingleton` only for stateless helpers. Use `AddTransient` sparingly and only when a new instance per injection point is genuinely needed.
- Constructor injection only. No `IServiceProvider.GetService<T>()` calls inside business logic (service locator anti-pattern).

## 2.2 Error Handling

**The pattern TIPS gets right:**
```csharp
public abstract class BaseService
{
    protected void LogException(Exception ex, string message) { ... }
    protected void LogInfo(string message) { ... }
}
```

**The pattern [YourProject] gets right:**
```csharp
public class BaseServiceResult<T>
{
    public bool IsSuccess { get; set; }
    public T? Data { get; set; }
    public string? ErrorMessage { get; set; }
}
```

**Combined standard going forward:**
- All service methods return a result wrapper (success/fail + data + error message). Don't throw exceptions for expected business failures. Throw only for truly unexpected conditions.
- Catch blocks must either (a) re-throw, (b) return a failure result, or (c) wrap and throw a domain-specific exception. **Never swallow exceptions silently.** This is a known bug in TIPS's `LoaService.cs` (file persistence failure is logged but not propagated, allowing data to be saved without its attached files).
- Never use `Console.WriteLine` for error output. This is a known issue in HAF's `FacilityConfigController.cs`. Use `ILogger<T>` exclusively.
- Global exception-handling middleware should catch unhandled exceptions, log them, and return a consistent error response (500 with a correlation ID, no stack traces in production).

## 2.3 Logging

**Standard (TIPS sets a good example here):**
- Use Application Insights for all telemetry, logs, and exceptions.
- Generate a `LogUid` (GUID) per operation and include it in every log entry for correlation.
- Three log channels: exceptions (`TrackException`), structured logs (`TrackTrace`), and custom events (`TrackEvent`).
- Include KQL query examples in README files so developers can actually find their logs. TIPS's Portal README does this well.

**Rules:**
- Log at `Information` level for operation start/completion. Log at `Warning` for recoverable issues. Log at `Error` for failures that need investigation.
- Never log PII (names, emails, phone numbers) or secrets. Log entity IDs and correlation IDs instead.
- Every Azure Function trigger should log its invocation with the trigger payload summary (not the full payload if it contains PII).

## 2.4 Async Patterns

- All I/O-bound operations must be async. No `.Result` or `.Wait()` calls on Tasks (deadlock risk in ASP.NET).
- Use `ConfigureAwait(false)` in library/service code that doesn't need the synchronization context.
- Use `CancellationToken` parameters on all async methods and pass them through to EF Core queries, HTTP calls, and Azure SDK calls.
- For real-time features, polling is acceptable only as a transport fallback (e.g., when SignalR WebSocket negotiation fails). If a feature uses polling alongside a real-time connection, monitor production to confirm polling stays a fallback and doesn't become the primary data path.

## 2.5 Code Comments

- Don't comment what the code does. Comment *why* the code does something non-obvious.
- XML doc comments (`///`) on all public methods in Service and Service.Entity projects. Controllers should have XML docs that feed Swagger/OpenAPI generation.
- TODO/HACK/FIXME comments are acceptable as markers but must have a corresponding tracked item (GitHub Issue or Azure DevOps work item). [YourProject] currently has 15+ untracked TODO/HACK comments.
- Regex patterns must include a comment describing what the pattern matches in plain English. Example: `// Matches URLs starting with http:// or https:// followed by domain and path`.

## 2.6 Code Style

These rules apply to both TIPS and [YourProject] codebases. Enforce via `.editorconfig` where possible.

**Required `.editorconfig` analyzer rules:** The following Roslyn analyzers should be set to `warning` (or `error` in CI) in the solution-level `.editorconfig`. These catch common code quality issues that slip through PR review:

- `dotnet_diagnostic.IDE0005.severity = warning` (Remove unnecessary using directives)
- `dotnet_diagnostic.IDE0055.severity = warning` (Fix formatting)
- `dotnet_diagnostic.CS8600.severity = warning` (Converting null literal or possible null value to non-nullable type)

**Lesson learned (HAF Chat, March 2026):** Three chat service files shipped with unused `using Microsoft.Extensions.Logging`, `using Microsoft.Extensions.DependencyInjection`, and `using Microsoft.Graph.Models` imports. Tyler's team cleaned them up in PR #[N]. If IDE0005 had been a build warning, the CI pipeline would have caught them before merge.

**Explicit typing over `var`:** Use explicit types when declaring variables. Implicit typing (`var`) reduces readability when a developer returns to unfamiliar code or reviews a PR without IDE tooling. Exception: LINQ expressions where the return type is obvious from the method chain and would be verbose to spell out.

```csharp
// Preferred
[YourEntity] thread = await _chatService.GetThreadAsync(threadId, ct);
List<ChatMessageDto> messages = result.Data;

// Avoid
var thread = await _chatService.GetThreadAsync(threadId, ct);
var messages = result.Data;
```

**Always use braces on control flow:** Even when the body is a single line, wrap `if`, `else`, `else if`, `for`, `foreach`, and `while` blocks in braces. No single-line conditionals.

```csharp
// Preferred
if (userId == 0)
{
    return BadRequest("Invalid user.");
}

// Avoid
if (userId == 0) return BadRequest("Invalid user.");
```

---

## Corrections Log

*Tracks issues found when following this file's instructions. Entries are added when a discrepancy is discovered and a fix is applied or proposed.*

| Date | What Failed | Root Cause | Fix Applied | ERRORS.md Ref |
|------|-------------|------------|-------------|---------------|

**Notes:**
<!-- Per-entry context that doesn't fit in the table. Format: "YYYY-MM-DD: [explanation]" -->
