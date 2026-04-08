---
type: context-file
parent: "`coding-index.md`"
summary: "DbContext lifecycle (IDbContextFactory), [YourProject] base class pattern, schema organization, stored procedures, SSDT-first workflow, temporal table config, entity configuration checklist, and database-defaulted value rules."
tags: [coding, database, ef-core, ssdt, entity-config]
---

# Database & EF Core Standards

> **Part of the the Coding Standards Graph (`coding-index.md`).** This file covers all database and Entity Framework Core patterns. For the full standards index, see `coding-index.md`.

## 4.1 DbContext Lifecycle

**Correct pattern (TIPS does this):** Use `IDbContextFactory<T>` and create contexts per operation:

```csharp
services.AddDbContextFactory<[YourDbContext]>(options =>
    options.UseSqlServer(connectionString, sqlOptions =>
        sqlOptions.EnableRetryOnTransientFailure()));
```

**Incorrect pattern (HAF has this bug):** Creating a DbContext in the repository constructor without disposal. This leads to stale entity tracking, resource leaks, and concurrency issues.

**Rules:**
- Use `IDbContextFactory<T>` for all service and repository classes. Create contexts with `using` blocks scoped to the operation.
- Configure retry logic on transient failures (`EnableRetryOnTransientFailure()` for SQL Server).
- Use `AsNoTracking()` on all read-only queries. This matters for performance and prevents accidental mutations.
- **One `SaveChangesAsync` per DbContext instance.** Each context handles one logical unit of work. Don't call `SaveChangesAsync` multiple times on the same context instance. For multi-step writes that need separate transactional boundaries, create a new context instance from `IDbContextFactory<T>` for each step.
- **Query projections, dual-path rule:**
  - **CRUD repositories** (those that support both reads and writes) must return entity objects, not projected DTOs. This preserves change tracking so the calling service can decide whether to track, modify, or detach the entity.
  - **Read-only query methods** (explicitly marked with `AsNoTracking()` and documented as read-only) may use `.Select()` projections for performance when loading full entities would pull unnecessary columns. These methods should be clearly named (e.g., `GetThreadSummariesAsync`) so developers know they return non-tracked results.

### 4.1.1 [YourProject] Base Class Pattern (Mandatory for HAF)

All new [YourProject] repositories must inherit from `[YourBaseRepository]<TIdType, TEntity, TFilter, TDbContext>` in `[YourSharedLib]/Services/Repositories/`. All new [YourProject] services must inherit from `[YourBaseCrudService]<TIdType, TEntity, TListModel, TSingleModel, TFilter>` in `[YourSharedLib]/Services/Services/`.

**What the base classes provide:**
- `[YourBaseRepository]` — `GetById` (with tracked/untracked toggle), `Search` (paginated), `Add`, `SaveChanges`, `ExportSearch` (raw IQueryable). Subclasses implement `ApplyIdFilter` and `ApplyFilter`, and optionally override `AddIncludesForSearch` / `AddIncludesForGetById` for eager loading.
- `[YourBaseCrudService]` — `GetList` (paginated), `GetSingle`, `Create`, `Update` with permission checks. Subclasses implement four abstract conversion methods: `ConvertEntityToListModel`, `ConvertEntityToSingleModel`, `ConvertSingleModelToEntityForCreate`, `UpdateEntityFromSingleModel`. This is where entity↔DTO mapping lives.

**Rules:**
- Don't bypass the base class to create standalone repository or service implementations unless the feature's access pattern genuinely doesn't fit CRUD (e.g., a pure event processor or a background job coordinator). Document the reason if you diverge.
- Domain-specific query methods (e.g., `GetAllThreadsForUserAsync`) are added as extra methods on the concrete repository subclass, not crammed into the base class filter mechanism.
- Use the existing `PaginatedResult<T>` return type from the base repository for all list endpoints. Don't create custom pagination wrappers.

## 4.2 Schema Organization

Both projects organize entities into database schemas ([scYourBoundedContext], [scYourBoundedContext], [scYourBoundedContext], [scYourBoundedContext], etc.). Continue this pattern:
- Each bounded context gets its own schema.
- Entity configurations use Fluent API in dedicated `{Entity}Configuration.cs` files inside a `Context/Configurations/` folder (HAF pattern) or via `OnModelCreating` partials.

## 4.3 Stored Procedures & Raw SQL

- Stored procedures are acceptable for complex batch operations or performance-critical queries. Both projects use them.
- All stored procedure parameters must be created via `SqlParameter` objects (already done correctly in both projects). Never concatenate user input into SQL strings.
- Wrap stored procedure calls in auto-generated interfaces (`I[YourDbContext]Procedures`, `IIntegrateContextProcedures`) so they can be mocked in tests.

## 4.4 Schema Management: SSDT-First (TIPS Standard)

TIPS uses SQL Server Data Tools (SSDT) as the single source of truth for database schema. EF Core does not own the schema. This pattern was formalized during the SNOUT migration after an initial attempt with hand-written EF migrations proved error-prone and created drift between the SQL schema and the C# entities.

**The workflow:**

1. **Define schema in SSDT.** All tables, sequences, constraints, indexes, temporal tables, and seed data live as `.sql` files in the `[YourApp].Database.Schema` project. Follow existing conventions: sequence-based INT PKs (start at 1000000), `Uid` (UNIQUEIDENTIFIER) columns, audit columns (`ModifyUser`/`ModifyDate`/`CreateUser`/`CreateDate`), system versioning with `*Hist` temporal tables, named constraints (`DF_`/`PK_`/`FK_` prefixes), and extended properties.
2. **Publish the SSDT project** to the target database (SSDT Publish profile, not `dotnet ef database update`).
3. **Reverse-engineer entities with EF Core Power Tools.** After the schema is published, run EF Core Power Tools to generate the C# entity classes and `DbContext` configuration from the live database. This is the bridge between SSDT and EF Core. The generated entities go in `Database.Sql.{Feature}/Entities/`.
4. **Delete any hand-written entities or migrations.** If scaffolding produced hand-written entity classes or a `/Migrations/` folder, delete them after the reverse-engineer completes. SSDT owns the schema; EF Core Power Tools owns the entity generation. No dual sources.

**Rules:**
- No EF migrations in SSDT-managed projects. No `/Migrations/` folder, no `dotnet ef migrations add`, no snapshot files.
- Schema changes go through SSDT `.sql` files, not through C# entity modifications. Change the SQL first, publish, then re-run the reverse-engineer to update the C# classes.
- New bounded contexts (new `scXxx` schemas) always use SSDT-first. This is not optional.
- The reverse-engineer step is a gated dependency in the phase plan. It must be called out explicitly as its own line item so it doesn't get skipped or forgotten. See `project-scoping-bp.md` Section 8.

**SSDT conventions (reference):**

| Convention | Example |
|------------|---------|
| Schema per bounded context | [scYourBoundedContext], [scYourBoundedContext], [scYourBoundedContext] |
| Sequence naming | [scYourBoundedContext] (start 1000000) |
| Temporal table naming | [scYourBoundedContext] |
| Lookup/status tables | [scYourBoundedContext] with seed data in `Initialize/InitTypes.sql` |
| Post-deployment script | `Script.PostDeployment.sql` includes all `InitTypes.sql` files |

**Lesson learned (SNOUT, March 2026):** The initial SNOUT scaffolding hand-wrote 8 entity classes and a migration. When the schema was later defined properly in SSDT, the hand-written entities had drifted (wrong PK types, missing audit columns, missing temporal tables). The reverse-engineer step caught all of it, but only after rework. Starting with SSDT from day one would have avoided the entire detour.

## 4.5 EF Core Temporal Table Configuration (EF Core 9+)

In EF Core 9, temporal table period columns (`SysStart`, `SysEnd`) are **shadow properties** by default. Do not add them as CLR properties on the entity class. The entity owns the business columns; the temporal tracking columns are owned by EF Core and SQL Server.

**Correct configuration (Fluent API):**

```csharp
entity.ToTable("[YourEntity]", "dbo")
    .ToTable(tb => tb.IsTemporal(ttb =>
    {
        ttb.UseHistoryTable("[YourEntity]History", "dbo");
        ttb.HasPeriodStart("SysStart").HasColumnName("SysStart");
        ttb.HasPeriodEnd("SysEnd").HasColumnName("SysEnd");
    }));
```

**Incorrect pattern (causes runtime exception):**
```csharp
// DO NOT add these to the entity class — they conflict with EF shadow properties
public DateTime SysStart { get; set; }
public DateTime SysEnd { get; set; }
```

**Lesson learned (HAF Chat, March 2026):** We added `SysStart` and `SysEnd` as CLR properties on `[YourEntity]`. This caused EF Core to treat them as both explicit properties and temporal shadow properties, producing a runtime conflict. We fixed it once ourselves (commit `cc59b78`) but never wrote the rule. Tyler's team had to fix it again (commit `d455236` + `948acb6`). A fix that doesn't get captured as a standard is just a fix that gets repeated.

## 4.6 New Entity Configuration Checklist

When adding a new EF Core entity to either codebase, verify every item in this checklist before marking the entity complete. These are required configurations that existing entities all have. Missing any one causes subtle runtime bugs.

| Item | What to configure | Example |
|------|-------------------|---------|
| Primary key | `entity.HasKey(e => e.Id);` | Every entity |
| Table and schema | `entity.ToTable("TableName", "schema");` | `entity.ToTable("[YourEntity]", "dbo");` |
| RowVersion / concurrency | `entity.Property(e => e.RowVer).IsRequired().IsRowVersion().IsConcurrencyToken();` | Required on every table with a `RowVer` column |
| Temporal table config | `IsTemporal()` with `HasPeriodStart`/`HasPeriodEnd` as shadow properties (see Section 4.5) | Every temporal table |
| Audit columns | `HasDefaultValueSql("GETUTCDATE()")` for `CreatedDate`, `HasDefaultValue(true)` for `IsActive`, etc. | Match existing entity patterns |
| Uid column | `HasDefaultValueSql("NEWID()")` | Every entity with a `Uid` GUID column |
| Indexes | Named indexes with `HasDatabaseName()` | `entity.HasIndex(e => e.GymId).HasDatabaseName("IX_[YourEntity]_GymId");` |
| Unique constraints | Named unique indexes | `entity.HasIndex(e => new { e.UserId, e.GymId }).IsUnique().HasDatabaseName("UQ_[YourEntity]_UserGym");` |
| Navigation properties | `HasOne`/`HasMany` with `WithMany`/`WithOne` + `HasForeignKey` + `OnDelete` behavior | Check existing entities for the pattern |
| Default values | `HasDefaultValue()` or `HasDefaultValueSql()` for columns with DB defaults | See Section 4.7 below |

## 4.7 Database-Defaulted Values: Don't Set in Code

If a column has a `HasDefaultValueSql()` or `HasDefaultValue()` configuration in the Fluent API, application code must not manually assign that value when creating a new entity instance. The database owns the default.

**Why:** (a) Setting it in code contradicts the single source of truth (the DB default). (b) `DateTime.UtcNow` uses the app server's clock, while `GETUTCDATE()` uses the DB server's clock; in distributed systems these can diverge. (c) Future changes to the default only need to happen in one place (the DB), not in every code path that creates the entity.

```csharp
// Correct — let the DB default handle it
[YourEntity] thread = new [YourEntity]
{
    UserId = userId,
    GymId = gymId,
    IsActive = true  // Only set if explicitly needed; check if HasDefaultValue covers it
};

// Wrong — manually setting a DB-defaulted column
[YourEntity] thread = new [YourEntity]
{
    UserId = userId,
    GymId = gymId,
    CreatedDate = DateTime.UtcNow,  // REMOVE — HasDefaultValueSql("GETUTCDATE()") handles this
    IsActive = true
};
```

**Lesson learned (HAF Chat, March 2026):** `[YourRepository]` set `CreatedDate = DateTime.UtcNow` on new `[YourEntity]` entities despite the column having `HasDefaultValueSql("GETUTCDATE()")`. Tyler's team removed it (commit `e24c04d`). Harmless in most cases but creates clock skew in distributed environments and obscures the real default source.

---

## Corrections Log

*Tracks issues found when following this file's instructions. Entries are added when a discrepancy is discovered and a fix is applied or proposed.*

| Date | What Failed | Root Cause | Fix Applied | ERRORS.md Ref |
|------|-------------|------------|-------------|---------------|

**Notes:**
<!-- Per-entry context that doesn't fit in the table. Format: "YYYY-MM-DD: [explanation]" -->
