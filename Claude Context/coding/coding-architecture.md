# Architecture Standards

> **Part of the Coding Standards Graph.** This file covers project layering, naming conventions, and solution organization. For the full standards index, see `coding-index.md`.

## 1.1 Project Layering

Layered architecture separates concerns into discrete tiers. The standard layer order (top to bottom):

```
UI / API  →  Service  →  Entity / DTO  →  Database
(HTTP)       (Logic)      (Models)         (Data Access)
```

**Rules:**
- UI projects reference Service projects. Service projects reference Entity and Database projects. Database projects reference nothing except data access libraries.
- No upward references. A Database project must never reference a Service or UI project.
- Functions and background jobs are thin HTTP/timer triggers that delegate to Service-layer classes. Business logic does not belong in Function triggers.
- Shared code goes in a `.Shared.Service` or `.Shared.Entity` project. Don't duplicate utility methods across features.

**Layer knowledge boundaries (enforced):**
- **Controllers** know about DTOs only. They receive DTOs from HTTP requests and return DTOs in responses. Controllers never reference entity classes directly.
- **Services** know about both DTOs and Entities. The service layer is where entity↔DTO mapping happens.
- **Repositories** know about Entities only. Repositories never reference DTO types, never return DTOs, and never accept DTOs as parameters. All query results from repositories are entity objects. This preserves change tracking and gives the calling service full control over whether to track, detach, or project results.

This separation is especially important when entity tracking is needed for update workflows. The moment a repository projects to a DTO, the calling service loses the ability to track and save changes on that entity.

## 1.2 Naming Conventions

**Projects:** `{Product}.{Feature}.{Layer}`  -  e.g., `App.Authentication.Service`, `Integrate.Database.Sql`

**Namespaces:** Match the project name exactly. No creative namespace aliases.

**Classes:**
- Entity/model classes: singular nouns (`User`, `Department`, `Configuration`)
- Service classes: `{Feature}Service` (`UserService`, `PaymentService`)
- Repository classes: `{Entity}Repository` or `GenericRepository<T>` (depends on your pattern)
- View models / DTOs: suffix with `Vm` or `Dto` (pick one and be consistent)
- Configuration classes: `{Entity}Configuration`

**Methods:**
- Async methods end with `Async` only when a synchronous overload also exists. If the method is always async, the suffix is optional but be consistent within a project.
- Boolean-returning methods start with `Is`, `Has`, `Can`, or `Should`.

**Files:**
- One class per file (with rare exceptions for small related enums or records).
- File name matches class name.

### 1.2.1 Entity/DTO Mapping Pattern

When converting between entities and DTOs, use factory methods rather than inline property-by-property assignment:

- **Preferred:** `UserDto.CreateFrom(entity)` or `entity.ToDto()`  -  encapsulates mapping logic in one place.
- **Avoid:** Inline `new UserDto { Name = entity.Name, Email = entity.Email, ... }` scattered across controllers.

In base service patterns, this happens through abstract conversion methods that each concrete service must implement. For event-driven mapping (e.g., receiving an external API response and converting to a DTO), add a static factory method on the DTO class.

**Exception:** If project boundaries prevent the entity from knowing about the DTO type (entity in Data layer, DTO in API layer), keep the mapping in the service layer. Don't introduce a circular reference just to use a factory method.

### 1.2.2 Enum Placement Convention

**Domain enums that cross layer boundaries live in a shared Dtos or Contracts project.** This is the single location for all shared enums (e.g., `UserRole`, `MessageType`, `Status`). The shared layer functions as the contract between layers and is referenced by API, UI, and services.

**Rules:**
- Enum names are singular nouns without an `Enum` suffix: `UserRole`, not `UserRoleEnum`.
- Back all enums with `int` explicitly: `public enum UserRole : int { ... }`.
- Start values at 1, not 0. Reserve 0 for `Unknown` or omit it. A zero default on an uninitialized int silently becoming a valid enum value is a bug source.
- If an enum is only used within a single project and never crosses a layer boundary, it can live in that project.
- Include a comment on reserved or future values: `SystemMessage = 5  // Reserved for automated notifications`.

## 1.3 Solution Organization

- Group related projects by feature domain using solution folders in the `.sln` file.
- Keep the `.editorconfig` at the solution root. This file enforces naming and style rules across the entire codebase.
- Store ARM/Bicep templates, deployment scripts, and infrastructure-as-code in a top-level `/infra` or `/deploy` folder, not scattered across Properties or other locations.

---

## Corrections Log

*Tracks issues found when following this file's instructions.*

| Date | What Failed | Root Cause | Fix Applied |
|------|-------------|------------|-------------|

