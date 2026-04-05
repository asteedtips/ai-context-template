# Testing Standards

> **Part of the Coding Standards Graph.** This file covers all testing patterns and requirements. For the full standards index, see `coding-index.md`.

## 6.1 Coverage Target

**Minimum 70% code coverage** across all projects, measured by coverlet or your chosen tool. This is the floor, not the ceiling.

**Must-test paths (100% coverage required regardless of overall target):**
- Authentication and authorization logic
- Code that handles money, billing, or financial calculations
- Data mutation operations (create, update, delete)
- Input validation logic
- Complex queries and stored procedure wrappers

## 6.2 Test Project Structure

One test project per bounded context or feature area. Each test project mirrors the source project's structure.

```
Project.Test/
  ├── Unit/
  │   ├── Services/
  │   │   └── ServiceNameTests.cs
  │   └── Repositories/
  │       └── RepositoryNameTests.cs
  ├── Integration/
  │   └── [Integration tests]
  └── TestHelpers/
      └── SharedFixture.cs
```

**Rules:**
- Unit tests go in `Unit/`; integration tests go in `Integration/`.
- One test class per source class. Test class name: `{SourceClass}Tests`.
- Keep test projects focused. If a test project becomes too large, split by feature or bounded context.

## 6.3 Unit Tests

- Mock external dependencies (DbContext, HTTP clients, cloud services, third-party APIs). Use Moq or NSubstitute.
- Test method naming: `{MethodName}_{Scenario}_{ExpectedResult}`  -  e.g., `ValidateInput_WhenEmailMissing_ReturnsFalse`.
- Each test should assert one thing. Multiple asserts are acceptable only when they verify different aspects of a single outcome.

```csharp
[Fact]
public async Task CreateUser_WhenEmailExists_ReturnsConflictError()
{
    // Arrange
    var mockRepo = new Mock<IUserRepository>();
    mockRepo.Setup(r => r.FindByEmailAsync("test@example.com", It.IsAny<CancellationToken>()))
        .ReturnsAsync(new User { Id = 1, Email = "test@example.com" });

    var service = new UserService(mockRepo.Object);

    // Act
    var result = await service.CreateUserAsync(
        new CreateUserRequest { Email = "test@example.com" }, CancellationToken.None);

    // Assert
    Assert.False(result.IsSuccess);
    Assert.Equal("Email already exists.", result.ErrorMessage);
}
```

## 6.4 Integration Tests

- Use `WebApplicationFactory<T>` or `TestServer` for API integration tests.
- Test against a real database (LocalDB, test container) for data access tests. Don't mock the database; that defeats the purpose.
- Clean up test data after each test using transactions, isolated test databases, or fixtures.

## 6.5 Test Isolation

- Tests must not depend on external services (cloud, APIs) by default. Use dependency injection to swap real implementations for test doubles.
- Tests must not depend on execution order. Each test sets up its own state.
- Tests must not share mutable state. Static fields are a red flag.

**Static field contamination fix:** When production code uses static fields (caches, rate limiters, global state), clear them in the test class constructor:

```csharp
public class RateLimitServiceTests
{
    public RateLimitServiceTests()
    {
        // Clear static state from other tests
        RateLimitRegistry.Clear();
    }
}
```

**InMemory DbContext key conflicts:** When using in-memory databases, auto-increment counters can collide across tests. Fix: assign explicit IDs to seeded entities using non-overlapping ranges (100+, 200+, 300+ per test class).

**Transitive dependency awareness:** Before adding a test project reference from one test project to another (for a shared fixture), check what transitive dependencies come with it. If the referenced test project pulls in large packages, inline the helper instead.

## 6.6 API Contract Tests

When a service wraps an external API, unit tests must verify the shape of the outgoing HTTP request, not just that a call was made. Assert on the URL path, query parameters, HTTP method, and request body structure.

**What to assert:**
- Correct HTTP method (GET, POST, PUT, DELETE, PATCH)
- Correct URL path and query parameters
- Correct request body structure and field names
- Correct parameter values (especially when mapping between internal and API-expected names)

```csharp
[Fact]
public async Task SendNotification_MakesCorrectApiCall()
{
    // Arrange
    var mockHandler = new Mock<HttpMessageHandler>();
    mockHandler.Protected()
        .Setup<Task<HttpResponseMessage>>(
            "SendAsync",
            ItExpr.Is<HttpRequestMessage>(r =>
                r.Method == HttpMethod.Post &&
                r.RequestUri.Path.Contains("/notifications/send") &&
                r.RequestUri.Query.Contains("userId=123")),
            ItExpr.IsAny<CancellationToken>())
        .ReturnsAsync(new HttpResponseMessage { StatusCode = HttpStatusCode.OK });

    // Act
    var result = await service.SendNotificationAsync(123, ct);

    // Assert
    Assert.True(result.IsSuccess);
}
```

## 6.7 Dry Run Mode for External Endpoint Integration

When features call external APIs that modify data (CRM updates, email moves, record creation), support a **Dry Run mode** that validates the pipeline without side effects.

**Why:** Most external services lack sandbox environments. Testing against live endpoints risks creating bad records or moving real data. Dry Run lets teams validate without side effects.

**Implementation pattern:**
1. Add a `RunMode` config (enum: `Live`, `DryRun`)
2. Read operations run identically in both modes. Write operations are gated by RunMode.
3. In DryRun mode, log what *would* have happened instead of executing writes
4. Results persist with an `IsDryRun = true` flag for audit trails
5. UI provides a "Test Run" button for one-shot testing

**Unit test coverage:** Verify that DryRun mode (a) runs read steps, (b) skips writes, (c) logs simulated actions, and (d) persists results with correct flags.

## 6.8 Background Task Queue Testing

When code queues background work via `IBackgroundTaskQueue.QueueWorkAsync()` (or similar), don't assert on the lambda's internal side effects. The lambda may never execute in tests.

**Instead, verify:**
1. `QueueWorkAsync` was called (proves work was queued)
2. The service set up correct initial state before queuing
3. The returned result reflects the pre-queue state

```csharp
[Fact]
public async Task ProcessBatch_QueuesBackgroundWork()
{
    // Arrange
    var mockQueue = new Mock<IBackgroundTaskQueue>();

    // Act
    var result = await service.ProcessBatchAsync(data, mockQueue.Object, ct);

    // Assert: verify queuing happened
    mockQueue.Verify(
        q => q.QueueWorkAsync(It.IsAny<Func<CancellationToken, ValueTask>>()),
        Times.Once);

    // Don't assert on the queued lambda's internal behavior
}
```

## 6.9 Grep-Before-Push for Signature Changes

When a method signature changes (params added/removed, return type changed, method renamed), test files break. Save a round-trip by grepping before push.

```bash
# Find all test references to the changed class
grep -r "ClassName" Tests/ --include="*.cs" -l
# Update every matching file before committing
```

This is especially critical for constructor changes, which can affect multiple test files.

---

## Corrections Log

*Tracks issues found when following this file's instructions.*

| Date | What Failed | Root Cause | Fix Applied |
|------|-------------|------------|-------------|

