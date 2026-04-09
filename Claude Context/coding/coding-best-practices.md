# Coding Best Practices

**[YOUR NAME] | [YOUR TITLE] | [YOUR COMPANY]**
*Reference file for all code creation, review, and modification tasks*
*Last Updated: [DATE]*

---

> **How to use this file**: This file contains the thinner sections of the coding standards. Larger topic areas have been extracted into standalone files for on-demand loading. Start at `coding-index.md` to find the right file for your task, or use the quick reference below.

> **Graph nodes (extracted topics):**
> - `coding-architecture.md`  -  Project layering, naming conventions, entity/DTO mapping, enums, solution organization
> - `coding-quality.md`  -  DI registration, error handling, logging, async patterns, code comments, code style
> - `coding-config.md`  -  Configuration patterns, service injection, operational vs structural config
> - `coding-database.md`  -  DbContext lifecycle, repository patterns, schema, entity checklist
> - `coding-testing.md`  -  Coverage targets, test structure, unit/integration tests, isolation, dry run mode
> - `coding-blazor-ui.md`  -  Component patterns, CSS builders, page checklist, header consistency, dialog validation, mockup conformance gate
> - `coding-verification.md`  -  Verification agent protocol (complexity tiers, what agents check)

> **Cross-references:** `security/security-practices.md` governs all credential and secrets management. `writing/best-practices-creation.md` governs documentation output formats. `writing/banned-writing-styles.md` applies to all written deliverables including code comments and README files. `github-actions-bp.md` covers GitHub Actions CI/CD implementation details.

---

## 5. Security Standards

### 5.1 Secrets Management

**Non-negotiable:** All secrets live in a secrets vault (Azure Key Vault or equivalent). Never commit credentials to source control.

**Database access is read-only by default.** Agents may run read-only queries freely but must not execute write, update, delete, or DDL operations without explicit approval. This applies regardless of the credential's actual permission level.

**Rules for all projects:**
- Application configuration may contain non-secret values (URLs, feature flags, timeouts). It must never contain client secrets, API keys, tokens, or passwords.
- Development configuration can use local secrets storage for development only. Never commit secret values.
- Connection strings in production must use managed identity or secure credential storage, falling back to vault references.

### 5.2 Authentication & Authorization

**Pattern:**
- All endpoints should have clear authentication and authorization requirements
- Cookies should be configured with `SecurePolicy=Always`, `HttpOnly=true`, `SameSite` attributes where applicable
- CSRF protection should be enabled where appropriate
- Implement resource ownership checks: when a user requests data, verify they have access to that specific resource

**Rules for API projects:**
- Every controller action must have an `[Authorize]` attribute or the controller itself must. Anonymous endpoints must be explicitly marked as such with a code comment explaining why.
- Rate limiting should be applied on authentication endpoints and public-facing APIs
- Resource ownership checks should verify that the requesting user has access to the requested resource

### 5.3 CORS

- Development environments can be permissive, but production must specify exact allowed origins
- Never combine open origin allowance with credential allowance

---

## 7. API Design Standards

### 7.1 Route Design

**Standard:**
- Routes should be resource-oriented and use consistent naming (usually plural for collections)
- Use HTTP methods for verbs: GET (read), POST (create), PUT (full update), PATCH (partial update), DELETE (remove)
- Collection endpoints: `/api/resources`
- Single-resource endpoints: `/api/resources/{id}`
- Sub-resource endpoints: `/api/resources/{id}/sub-resources`

### 7.2 Request Validation

- Validate all incoming request models
- Return proper HTTP status codes for validation failures (400 Bad Request, not 200 with error in body)
- Validate at the API boundary; services should assume valid input

### 7.3 Response Patterns

- Use consistent response wrappers across your API
- Return proper HTTP status codes: 200 (success), 201 (created), 204 (no content), 400 (bad request), 401 (unauthorized), 403 (forbidden), 404 (not found), 500 (server error)
- Include a correlation ID in error responses for debugging
- Never return stack traces in production responses

### 7.4 API Documentation

- Use XML doc comments on all controller actions to feed documentation generation
- Include example request/response payloads for complex endpoints
- Version APIs from the start (`/api/v1/...`) to prevent breaking changes later

### 7.5 Controller Routing: Match Existing Convention First

Before applying a new routing convention, check what the existing codebase does. If the codebase uses one pattern consistently, use that pattern. Do not introduce inconsistency just to follow a generic best practice.

**Process:** Check existing controllers to find the dominant pattern. Use that pattern. If you believe the project should adopt a different convention, flag it as a separate refactor decision in the scope doc; don't mix convention changes into feature branches.

---

## 9. CI/CD Standards

For GitHub Actions implementation details, see `github-actions-bp.md`. This section covers the high-level standards.

### 9.1 Pipeline Requirements

Every push and PR should trigger:

1. **Build:** Compile each project
2. **Test:** Run test suite with results uploaded as artifacts
3. **Optional future additions:** Code coverage collection, security scanning

### 9.2 Branch Strategy

- Primary development branch contains the latest work-in-progress
- Main/master branch is production-ready
- Feature branches: `feat/{short-description}`
- Bugfix branches: `fix/{short-description}`
- CI triggers on pushes and PRs to primary branches

### 9.3 Environment Configuration

- Use environment-specific configuration (dev, staging, production) for secrets and endpoints
- Use OIDC or managed identity for cloud authentication from CI when possible
- Deployment to cloud services via appropriate actions

### 9.4 Build Verification: CI-First

The primary verification gate is your CI system, not local builds. CI runs on clean infrastructure with all dependencies correctly installed.

**Workflow:**
1. Write or modify code
2. Commit and push to a feature branch
3. CI builds and tests automatically
4. Check results with your CI command-line tool
5. If tests fail, fix locally, push again

**When local builds apply:** Only with explicit permission, and only for projects small enough to build locally. For large multi-project builds, CI is always the gate.

---

## 10. Performance & Reliability

### 10.1 Query Optimization

- Avoid N+1 query patterns (looping and making individual queries instead of batching)
- Use eager loading when you know you'll need related data
- Use projections when you only need specific columns
- Watch for loops containing async I/O calls; each iteration is a round-trip

### 10.2 Resilience

- HTTP calls to external APIs should include retry policies for transient failures
- Database connections should enable retry-on-transient-failure
- Background services should handle their own exceptions gracefully

### 10.3 Caching

- Use caching for data that's read frequently and changes rarely (configurations, lookup tables, provider settings)
- Set explicit cache expiration; never cache indefinitely
- Monitor cache hit rates in production

### 10.4 DateTimeOffset Required for External API Date Parameters

When passing date/time values to external APIs, always use `DateTimeOffset`, not `DateTime`. `DateTime.UtcNow.Date` returns a `DateTime` with `Kind = Unspecified` after `.Date` strips the time component. When serialized with `ToString("o")`, this produces a string with no UTC offset — some API servers silently interpret this as local time, shifting the query window by the server's timezone offset.

```csharp
// Bad — strips timezone Kind, produces no UTC offset
string startDate = DateTime.UtcNow.Date.ToString("o");

// Good — preserves UTC offset
string startDate = DateTimeOffset.UtcNow.Date.ToString("o");
```

**Rule:** Use `DateTimeOffset.UtcNow` (not `DateTime.UtcNow`) for any date value passed as a query parameter to an external API. This applies to calendar queries, date range filters, and any external service that interprets date strings.

**Lesson learned (a project, April 2026):** A calendar API returned zero events because the query window was shifted by the server's timezone offset. The fix was one character — `DateTimeOffset` instead of `DateTime`. Two separate issues traced to the same root cause before it was identified.

### 10.5 DI Registration: Keyed Services Are Invisible to IEnumerable<T> Injection

`AddKeyedScoped`, `AddKeyedTransient`, and `AddKeyedSingleton` register a service under a specific key. When another service injects `IEnumerable<T>` to get all implementations of an interface, .NET's DI container does **not** include keyed registrations in that enumeration. The result is an empty collection with no error — the service silently never dispatches.

**Rule:** Services that need to be resolved via `IEnumerable<T>` (the strategy/executor pattern) must be registered with `AddScoped`, `AddTransient`, or `AddSingleton` — not their keyed variants.

```csharp
// Bad — keyed registration is invisible to IEnumerable<IHandler> injection
services.AddKeyedScoped<IHandler, ConcreteHandlerA>("typeA");

// Good — standard registration is visible to IEnumerable<IHandler>
services.AddScoped<IHandler, ConcreteHandlerA>();
```

Use `AddKeyedScoped` only when you retrieve the service explicitly by key via `[FromKeyedServices("key")]` or `IServiceProvider.GetKeyedService<T>("key")`. If you need both patterns, register twice: once keyed, once standard.

**Lesson learned (a project, April 2026):** Action executors were registered with `AddKeyedScoped` but injected as `IEnumerable<IActionExecutor>`. The executor loop received zero executors and silently processed no actions. No exception was thrown — the failure was invisible until manual testing.

---

## 11. Documentation Standards

### 11.1 Repository-Level Documentation

Every code repository should have an `Architecture.md` file at the repo root covering:
- Repository layout and organization
- Tech stack
- Application architecture and request flow
- Authentication and authorization (if applicable)
- Data access patterns (if applicable)
- Configuration and environment variables
- Error handling approach
- Known considerations and constraints

This is a living document. Update it when the codebase changes.

### 11.2 README Files

Every project (compilation unit) should have a `README.md` covering:
- What the project does (one paragraph)
- How to configure it for local development
- Environment-specific settings
- How to run its tests
- Key architectural decisions

### 11.3 Architecture Decision Records (ADRs)

When a non-obvious technical choice is made, document it:

```markdown
# ADR-001: [Title]

## Status: Accepted
## Date: YYYY-MM-DD

## Context
[Why the decision was needed]

## Decision
[What was decided]

## Consequences
[What trade-offs this creates]
```

Store ADRs in a `/docs/adr/` folder at the repo root.

### 11.4 Inline Documentation

- Comment *why*, not *what*. The code shows what; comments explain why.
- XML doc comments on all public methods in business logic projects
- TODO/HACK/FIXME comments must have a corresponding tracked work item
- Magic numbers must be replaced with named constants or explained in comments

---

## 12. Current Gaps

Document known gaps or areas for improvement discovered during code review. Include:
- Issue number or description
- Severity level
- File reference
- Status (open, in progress, resolved)

---

## 13. What Good Looks Like

Not everything needs fixing. Document patterns that are working well and should be maintained:

- Effective DI registration patterns
- Well-structured service layers
- Good error handling approaches
- Clean repository patterns
- Well-documented API contracts

---

*Read `coding-index.md` to find the right standards file for your task. For security-specific guidance, see `security/security-practices.md`. For documentation formatting, see `writing/best-practices-creation.md`.*

*Last Updated: [DATE]  -  Graph split: extracted sections on architecture, quality, config, database, testing, Blazor UI, and verification into standalone files. This file retains sections on security, API design, CI/CD, performance, documentation, gaps, and good patterns.*

---

## Corrections Log

*Tracks issues found when following this file's instructions.*

| Date | What Failed | Root Cause | Fix Applied |
|------|-------------|------------|-------------|

