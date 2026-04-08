---
type: context-file
parent: "`coding-index.md`"
summary: "Project layering rules, naming conventions (projects, classes, methods, enums), entity/DTO mapping patterns, and solution organization for TIPS and [YourOrg]."
tags: [coding, architecture, naming, layering]
---

# Architecture Standards

> **Part of the the Coding Standards Graph (`coding-index.md`).** This file covers project layering, naming conventions, and solution organization. For the full standards index, see `coding-index.md`.

## 1.1 Project Layering

Both TIPS and HybridAF follow a layered architecture. The expected layer order (top to bottom):

```
Portal / API  →  Service  →  Service.Entity  →  Database.Sql
   (UI/HTTP)     (Logic)     (DTOs/ViewModels)   (EF Core / Data Access)
```

**Rules:**
- UI projects reference Service projects. Service projects reference Service.Entity and Database.Sql. Database.Sql references nothing except EF Core and its own entity models.
- No upward references. A Database project must never reference a Service or UI project.
- Azure Functions (`.Func` projects) are thin HTTP/timer triggers that delegate to Service-layer classes. Business logic does not belong in Function triggers.
- Shared code goes in a `.Shared.Service` or `.Shared.Service.Entity` project. Don't duplicate utility methods across features.

**Layer knowledge boundaries (enforced):**
- **Controllers** know about DTOs only. They receive DTOs from HTTP requests and return DTOs in responses. Controllers never reference entity classes directly.
- **Services** know about both DTOs and Entities. The service layer is where entity↔DTO mapping happens.
- **Repositories** know about Entities only. Repositories never reference DTO types, never return DTOs, and never accept DTOs as parameters. All query results from repositories are entity objects. This preserves EF Core change tracking and gives the calling service full control over whether to track, detach, or project.

This separation matters most when entity tracking is needed for update workflows. The moment a repository projects to a DTO, the calling service loses the ability to track and save changes on that entity.

## 1.2 Naming Conventions

**Projects:** `{Product}.{Feature}.{Layer}` — e.g., `[YourApp].MassNotify.Service`, `[YourOrg].Integrate.Database.Sql`

**Namespaces:** Match the project name exactly. No creative namespace aliases.

**Classes:**
- Entity/model classes: singular nouns (`MassNotifyJob`, `Provider`, `FacilityConfig`)
- Service classes: `{Feature}Service` (`LoaService`, `TokenService`)
- Repository classes: `{Entity}Repository` or `EFCoreBaseRepository<T>`
- View models / DTOs: suffix with `Vm` (`SystemSubscriberVm`, `HAFIdentityPrincipalVm`)
- Configuration classes (EF Fluent API): `{Entity}Configuration`

**Methods:**
- Async methods end with `Async` only when a synchronous overload also exists. If the method is always async, the `Async` suffix is optional but be consistent within a project.
- Boolean-returning methods start with `Is`, `Has`, `Can`, or `Should`.

**Files:**
- One class per file (with the exception of small related enums or records that can share a file).
- File name matches class name.

### 1.2.1 Entity/DTO Mapping Pattern

When converting between entities and DTOs, use factory methods rather than inline property-by-property assignment:

- **Preferred:** `ChatMessageDto.CreateFrom(entity)` or `entity.ToDto()` — encapsulates mapping logic in one place, easy to find and update.
- **Avoid:** Inline `new ChatMessageDto { Sender = evt.SenderName, Body = evt.Body, ... }` scattered across Razor components or controllers.

In HAF, `[YourBaseCrudService]<T>` handles this through its abstract `Convert*` methods (`ConvertEntityToListModel`, `ConvertEntityToSingleModel`, `ConvertSingleModelToEntityForCreate`, `UpdateEntityFromSingleModel`). Use these for standard CRUD flows. For event-driven mapping (e.g., SignalR `ChatMessageEvent` → `ChatMessageDto`), add a static factory method on the DTO class.

**Exception:** If project references prevent the entity from knowing about the DTO type (e.g., the entity lives in `Database.Sql` which can't reference `Dtos`), keep the mapping in the service layer. Don't introduce a circular reference just for a factory method.

### 1.2.2 Enum Placement Convention

**Domain enums that cross layer boundaries live in `Dtos/Enums/`.** This is the single location for all shared enums (e.g., `AppRoute.cs`, `SenderType.cs`). The Dtos project functions as the shared contract layer and is referenced by API, SharedComponents, and Blazor.

**Accepted layering exception:** `[YourOrg].SharedRazor` (Database.Sql layer) may hold a project reference to `Dtos` for enum type access on entity properties. This is the only sanctioned upward reference. It exists because domain enums need type safety on both the entity and the DTO, and duplicating enum definitions across layers creates drift. Document any new SharedRazor → Dtos references in a code comment at the `using` statement.

**Rules:**
- Enum names are singular nouns without an `Enum` suffix: `SenderType`, not `SenderTypeEnum`.
- Back all enums with `int` explicitly: `public enum SenderType : int { ... }`.
- Start values at 1, not 0. Reserve 0 for `Unknown` or omit it entirely. A zero default on an uninitialized int silently becoming a valid enum value is a bug source.
- If an enum is only used within a single project and never crosses a layer boundary, it can live in that project. The `Dtos/Enums/` rule applies to enums shared across two or more projects.
- Include a comment on reserved/future values: `System = 3  // Reserved for future automated messages`.

## 1.3 Solution Organization

- Group related projects by feature domain using solution folders in the `.sln` file.
- Keep the `.editorconfig` at the solution root. Both projects already have this in place (TIPS enforces naming rules through it). [YourProject] should adopt TIPS's `.editorconfig` as the baseline.
- Store ARM/Bicep templates, deployment scripts, and infrastructure-as-code in a top-level `/infra` or `/deploy` folder, not scattered across `Properties/ServiceDependencies`.

---

## Corrections Log

*Tracks issues found when following this file's instructions. Entries are added when a discrepancy is discovered and a fix is applied or proposed.*

| Date | What Failed | Root Cause | Fix Applied | ERRORS.md Ref |
|------|-------------|------------|-------------|---------------|

**Notes:**
<!-- Per-entry context that doesn't fit in the table. Format: "YYYY-MM-DD: [explanation]" -->
