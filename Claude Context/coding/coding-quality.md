# Code Quality Standards

> **Part of the Coding Standards Graph.** This file covers dependency injection, error handling, logging, async patterns, and code style. For the full standards index, see `coding-index.md`.

## 2.1 Dependency Injection

**Pattern:** Register services through extension methods on `IServiceCollection`:

```csharp
public static class DI[YourFeature]Services
{
    public static IServiceCollection Add[YourFeature]Services(
        this IServiceCollection services, IConfiguration config)
    {
        services.AddScoped<[YourService]>();
        services.AddScoped<[YourRepository]>();
        return services;
    }
}
```

**Rules:**
- Every feature owns a `DI{Feature}Services.cs` extension method. No service registration happens in `Program.cs` directly beyond calling the extension methods.
- Use `AddScoped` for services that depend on DbContext. Use `AddSingleton` only for stateless helpers. Use `AddTransient` sparingly and only when a new instance per injection point is genuinely needed.
- Constructor injection only. No `IServiceProvider.GetService<T>()` calls inside business logic (service locator anti-pattern).

## 2.2 Error Handling

**The pattern:** All service methods return a result wrapper that includes success status, data, and error messages.

```csharp
public class ServiceResult<T>
{
    public bool IsSuccess { get; set; }
    public T? Data { get; set; }
    public string? ErrorMessage { get; set; }
}
```

**Rules:**
- Don't throw exceptions for expected business failures. Return a failure result instead.
- Catch blocks must either (a) re-throw, (b) return a failure result, or (c) wrap and throw a domain-specific exception. Never swallow exceptions silently.
- Never use `Console.WriteLine` for error output. Use `ILogger<T>` exclusively.
- Global exception-handling middleware should catch unhandled exceptions, log them, and return a consistent error response (500 with correlation ID, no stack traces in production).

## 2.3 Logging

**Standard:**
- Use a centralized telemetry service for all logs and exceptions (Application Insights, Datadog, or similar).
- Generate a correlation ID per operation and include it in every log entry for tracking.
- Use three log levels: `Information` for operation start/completion, `Warning` for recoverable issues, `Error` for failures that need investigation.
- Never log personally identifiable information (names, emails, phone numbers) or secrets. Log entity IDs and correlation IDs instead.
- Include KQL (Kusto Query Language) or equivalent query examples in README files so developers can find their logs in production.

## 2.4 Async Patterns

- All I/O-bound operations must be async. No `.Result` or `.Wait()` calls on Tasks (deadlock risk).
- Use `ConfigureAwait(false)` in library/service code that doesn't need the synchronization context.
- Use `CancellationToken` parameters on all async methods and pass them through to database calls, HTTP requests, and external API calls.
- For real-time features, polling is acceptable only as a transport fallback. If a feature uses polling alongside a real-time transport, monitor production to confirm polling stays a fallback.

## 2.5 Code Comments

- Comment *why* the code does something non-obvious, not what it does.
- XML doc comments (`///`) on all public methods in Service and Entity projects. API controllers should have XML docs that feed Swagger/OpenAPI generation.
- TODO/HACK/FIXME comments are acceptable as markers but must have a corresponding tracked work item. Don't leave untracked TODO comments.
- Regex patterns must include a comment describing what they match in plain English. Example: `// Matches URLs starting with http:// or https:// followed by domain and optional port`.

## 2.6 Code Style

These rules apply across your codebase. Enforce via `.editorconfig` where possible.

**Required `.editorconfig` analyzer rules:** The following Roslyn analyzers should be set to `warning` (or `error` in CI):

- `dotnet_diagnostic.IDE0005.severity = warning` (Remove unnecessary using directives)
- `dotnet_diagnostic.IDE0055.severity = warning` (Fix formatting)
- `dotnet_diagnostic.CS8600.severity = warning` (Converting null literal or possible null value to non-nullable type)

**Explicit typing over `var`:** Use explicit types when declaring variables. Implicit typing (`var`) reduces readability when a developer returns to unfamiliar code or reviews code without IDE tooling. Exception: LINQ expressions where the return type is obvious from the method chain and would be verbose to spell out.

```csharp
// Preferred
UserDto user = await _userService.GetUserAsync(userId, ct);
List<DepartmentDto> departments = result.Data;

// Avoid
var user = await _userService.GetUserAsync(userId, ct);
var departments = result.Data;
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

*Tracks issues found when following this file's instructions.*

| Date | What Failed | Root Cause | Fix Applied |
|------|-------------|------------|-------------|

