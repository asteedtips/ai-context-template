# Database & EF Core Standards

> **Part of the Coding Standards Graph.** This file covers DbContext lifecycle, repository patterns, entity configuration, and schema management. For the full standards index, see `coding-index.md`.

## 4.1 DbContext Lifecycle and Factory Pattern

**Never inject DbContext directly into services or repositories.** Use `IDbContextFactory<T>` to create new instances per operation. This prevents context lifetime issues, entity tracking contamination across operations, and connection pool exhaustion.

```csharp
public class UserService
{
    private readonly IDbContextFactory<ApplicationDbContext> _contextFactory;

    public UserService(IDbContextFactory<ApplicationDbContext> contextFactory)
    {
        _contextFactory = contextFactory;
    }

    public async Task<UserDto> GetUserAsync(int userId, CancellationToken ct)
    {
        await using var context = await _contextFactory.CreateDbContextAsync(ct);
        var user = await context.Users.FirstOrDefaultAsync(u => u.Id == userId, ct);
        return user?.ToDto();
    }
}
```

**Rule:** Every data access operation creates a fresh DbContext, executes the query, and disposes it. This prevents context state bleeding between operations and reduces memory pressure.

## 4.2 Repository Base Class Pattern

<!-- CUSTOMIZE: Define your repository base class architecture. Example:

```csharp
public abstract class EFCoreRepository<TEntity> where TEntity : class
{
    protected readonly IDbContextFactory<ApplicationDbContext> ContextFactory;

    protected EFCoreRepository(IDbContextFactory<ApplicationDbContext> contextFactory)
    {
        ContextFactory = contextFactory;
    }

    public virtual async Task<TEntity?> GetByIdAsync(int id, CancellationToken ct)
    {
        await using var context = await ContextFactory.CreateDbContextAsync(ct);
        return await context.Set<TEntity>().FindAsync(new object[] { id }, cancellationToken: ct);
    }

    public virtual async Task<IEnumerable<TEntity>> GetAllAsync(CancellationToken ct)
    {
        await using var context = await ContextFactory.CreateDbContextAsync(ct);
        return await context.Set<TEntity>().ToListAsync(ct);
    }
}
```

Concrete repositories extend the base class and add entity-specific queries.
-->

## 4.3 Schema Organization

<!-- CUSTOMIZE: Document your schema structure. Example:

```sql
-- User management
CREATE SCHEMA [auth]
  -- Users, Roles, Permissions tables

-- Product catalog
CREATE SCHEMA [product]
  -- Products, Categories, Inventory tables

-- Transactional data
CREATE SCHEMA [transaction]
  -- Orders, Payments, Fulfillment tables
```

Use the schema to organize the logical domains of your database. This prevents table name collisions and makes the schema self-documenting.
-->

**Rules:**
- One schema per bounded context or major domain.
- Use lowercase, simple names for schemas (e.g., `auth`, `product`, `order`).
- In EF Core, map entities to schemas: `builder.ToTable("Users", schema: "auth")`.

## 4.4 Stored Procedures

Stored procedures should be used sparingly and only when there's a performance reason (e.g., bulk operations, complex multi-table updates that would be inefficient in C#).

<!-- CUSTOMIZE: Document when your team uses stored procedures. Example:

We use stored procedures only for:
1. Bulk insert/update/delete operations that process tens of thousands of rows
2. Complex financial calculations that must be atomic across multiple tables
3. Reporting queries that aggregate data from many tables with specific performance requirements

For normal CRUD and business logic, use EF Core. Stored procedures add maintenance overhead and reduce visibility.
-->

## 4.5 Entity Configuration Checklist

When creating a new entity, run through this checklist:

- [ ] Entity has a primary key property (usually `int Id`)
- [ ] All navigation properties are virtual (for EF Core lazy loading)
- [ ] All collection properties are initialized: `public List<Child> Children { get; set; } = new();`
- [ ] EF Core Fluent API configuration exists in a `{Entity}Configuration` class
- [ ] Configuration class sets up the schema, table name, and all key relationships
- [ ] Configuration applies any indexes needed for filtering or sorting
- [ ] Entity includes created/modified audit columns if needed
- [ ] Soft delete column exists if this entity is ever needed for audit/compliance
- [ ] Comments on the entity class document its purpose and relationships
- [ ] Entity is registered in DbContext's `OnModelCreating`: `modelBuilder.ApplyConfiguration(new UserConfiguration())`

## 4.6 Temporal Tables and Audit Trails

<!-- CUSTOMIZE: Document your audit/temporal table strategy. Example:

**EF Core 9+ support:** Modern EF Core can track temporal tables as shadow properties. When an entity needs automatic history:

1. Add temporal table configuration in the Fluent API: `.HasAnnotation("SqlServer:IsTemporal", true).HasAnnotation("SqlServer:TemporalHistoryTableName", "UserHistory")`
2. EF Core automatically tracks `ValidFrom` and `ValidTo` shadow properties
3. Query at a point in time: `.TemporalAsOf(someDateTime)`

**Legacy:** If using an earlier EF Core version, implement soft delete with a `DeletedAt` column and a query filter: `modelBuilder.Entity<User>().HasQueryFilter(u => u.DeletedAt == null)`
-->

## 4.7 Database-Defaulted Values

Some values (like `CreatedAt` timestamps) should be set by the database, not by the application. This prevents time skew and ensures consistency.

```csharp
// In Fluent API configuration:
builder.Property(e => e.CreatedAt)
    .HasDefaultValueSql("GETUTCDATE()");
```

**Rule:** If a column has a database default, don't set it in application code. EF Core's change tracking will ignore the database-set value on insert. Use `SQL scalar defaults` for timestamps and `SQL functions` for generated columns.

---

## Corrections Log

*Tracks issues found when following this file's instructions.*

| Date | What Failed | Root Cause | Fix Applied |
|------|-------------|------------|-------------|

