---
type: context-file
parent: "`coding-index.md`"
summary: "Blazor component patterns, CSS builders, new page checklist, header consistency, dialog validation, state management, error boundaries, mockup conformance (Extract-Build-Verify hard gate), MudBlazor gotchas, three-state filter pattern, SharedComponents layer check, and bUnit testing."
tags: [coding, blazor, ui, mudblazor, mockup-conformance, bunit]
---

# Blazor / UI Standards

> **Part of the the Coding Standards Graph (`coding-index.md`).** This file covers all Blazor and UI patterns. For the full standards index, see `coding-index.md`.

## 8.1 Component Patterns

Both projects use Blazor Server-Side Rendering (SSR) with interactive components.

**Rules:**
- Keep Razor components focused. If a component exceeds ~200 lines, split it into smaller child components.
- Use code-behind files (`.razor.cs`) for components with substantial C# logic. Inline `@code` blocks are fine for simple components.
- HAF's `BaseUx.razor` pattern (shared base component with common functionality) is worth adopting in TIPS as well.
- HAF's provider-specific config editors (`ArboxConfigEditor.razor`, `XplorConfigEditor.razor`, etc.) demonstrate a good pattern: one component per provider variant, sharing a `BaseConfigDialog.cs` base class.

### 8.1.1 CSS Class and Style Building

For dynamic CSS class and style assignment in Blazor components, use a builder pattern instead of inline string concatenation. Inline concatenation (`$"message-bubble {(isMine ? "sent" : "received")} {(isRead ? "" : "unread")}"`) becomes unreadable as conditions grow and is error-prone (trailing spaces, missing separators).

**Pattern:**
- Create `ICssClassBuilder` and `IStyleBuilder` interfaces with fluent `.Add(className, condition)` methods.
- Provide a default implementation (e.g., `CssClassBuilder`) that developers use across components.
- The builder handles separator logic, conditional inclusion, and produces a clean output string.

```csharp
// Preferred
string classes = new CssClassBuilder("message-bubble")
    .Add("sent", isMine)
    .Add("received", !isMine)
    .Add("unread", !isRead)
    .Build();

// Avoid
string classes = $"message-bubble {(isMine ? "sent" : "received")} {(isRead ? "" : "unread")}".Trim();
```

This is a new pattern for [YourOrg]. No existing builder exists. The first implementation should live in `SharedComponents/` and be usable by both `[YourBlazorApp]` and any server-rendered Blazor components.

### 8.1.2 New Routable Page Checklist

When adding a new `@page` component, all of the following must be verified before the commit:

1. **DI verification** — every `@inject` in the new page resolves to a service registered in both `Program.cs` (Blazor WASM) and `MauiProgram.cs` (MAUI). Grep the startup files for each injected type.
2. **Navigation entry** — the page is reachable from the UI. Add a menu item, button, or link in the appropriate navigation component (e.g., [YourNavBar] hamburger menu). A routable page with no way to reach it is incomplete.
3. **SharedNavigator mapping** — if the page uses an `AppRoute` enum value, confirm the route is mapped in both SharedNavigator implementations (Blazor WASM and MAUI). Unmapped routes throw `NotImplementedException`.
4. **Auth/layout directives** — confirm `@attribute [Authorize]`, `@layout`, and `@rendermode` match the pattern of sibling pages in the same area. If existing pages in the same feature omit these, the new page should too.
5. **Both platforms** — if the page is Blazor WASM only, confirm MAUI doesn't need it. If it applies to both, verify DI and navigation in both projects.

**Lesson learned (PR #[N] Phase [N], March 2026):** Thread list pages were built with correct routes and SharedNavigator mapping, but `ChatConnectionService` was never registered in DI (pre-existing gap across all chat pages), and no hamburger menu items were added. Tyler hit both issues on first test. Root cause: no page-level completeness checklist existed.

### 8.1.3 Page Header / Navigation Bar Consistency

Before building a page header (back button bar, title bar, app bar), check what the existing pages in the same feature area use. The goal is visual and structural consistency across the app.

**How to check:** Open 2-3 sibling pages in the same area. Look for which MudBlazor component they use for the top bar: `<MudAppBar>`, `<MudPaper>` with a theme class, or `<MudToolBar>`. Use the same one.

**When building a list/index page:** Use `@layout [YourBaseLayout]` (which provides the [YourNavBar] + theme). The page gets the standard app chrome automatically. Do not build a custom `MudAppBar` for pages that are part of the normal navigation flow.

**When building an immersive/detail page** (e.g., a chat conversation): A custom back-header bar is appropriate. Use the component that sibling detail pages use.

**Lesson learned (HAF Chat, March 2026):** We used `<MudPaper>` with `theme-bg-primary` for back-header bars on new-message pages. Other pages in the same area used `<MudAppBar Color="Color.Primary" Fixed="false">`. Tyler's team had to fix the inconsistency in PR #[N]. A 30-second check of sibling pages would have prevented it.

### 8.1.4 Blazor Dialog and Form Validation Checklist

Every MudBlazor dialog that accepts user input must include:

1. **Required field validation**: `Required="true"` and `RequiredError="Field name is required!"` on every field that can't be blank.
2. **Form validity tracking**: `<MudForm @ref="form" @bind-IsValid="isValid">` on the form container.
3. **Submit button gating**: `Disabled="@(!isValid || isLoading)"` on the submit button. Never allow submitting an invalid form.
4. **Loading state**: An `isLoading` bool that shows a `MudProgressCircular` on the submit button and disables both Submit and Cancel while the operation runs.
5. **Validation functions**: Custom validators (email format, phone format, etc.) via `Validation="@(new Func<string?, string?>(Validator))"`.

```razor
<DialogActions>
    <MudButton OnClick="Cancel" Disabled="isLoading">Cancel</MudButton>
    <MudButton Color="Color.Primary" Variant="Variant.Filled"
               OnClick="OnSave" Disabled="@(!isValid || isLoading)">
        @if (isLoading)
        {
            <MudProgressCircular Class="ms-n1" Size="Size.Small" Indeterminate="true" />
            <MudText Class="ms-2">Saving...</MudText>
        }
        else
        {
            <MudText>Save</MudText>
        }
    </MudButton>
</DialogActions>
```

**Lesson learned (a prior project handoff, March 2026):** The `GeneratePassDialog` shipped without required field validation or a loading state. Tyler's team added both in PR #[N] (6 fields got `Required` + `RequiredError`, plus the full loading spinner pattern). These patterns should be standard for every dialog, not discovered during QA.

## 8.2 State Management

- Don't store state in static fields. Use scoped services, cascading parameters, or a state container pattern.
- For cross-component communication, use events or a scoped state service; not direct component references.

## 8.3 Error Boundaries

- Use `<ErrorBoundary>` components to catch rendering errors gracefully.
- Log component exceptions to Application Insights.
- Display user-friendly error messages, not raw exception text.

## 8.4 Mockup-First Development: Extract → Build → Verify Hard Gate

> **This is the single highest-impact gate in the UI development process.** The issue-[N] retrospective found that every UI conformance failure traced to the same root cause: code was built from the API layer up, not from the mockup down. The fix is structural: the mockup is the first artifact opened in any UI wave, before any code is written. No exceptions for "I'll check the mockup after the service layer compiles."

When a project has approved HTML mockups (per `project-scoping-bp.md`), every Razor component must pass a three-step gate: Extract → Build → Verify. The component status cannot move to DONE until the verification artifact exists and shows all items passing. This is a hard gate with the same enforcement weight as the startup gate in your CLAUDE.md.

**Mockup-first rule:** When starting a UI wave, the literal first action is opening the mockup file and running Step A (Extract). Do not read service interfaces, do not check what API methods exist, do not look at the database schema. Open the mockup. The component structure comes from the design, not from the data model. Service methods are shaped to serve the UI, not the other way around.

### Step A: Extract Component Spec (before writing any code)

Open the approved mockup. For each screen this phase touches, produce a **Component Spec Checklist**, a numbered list of every visual element in the mockup, written in the implementation framework's language (e.g., MudBlazor component names for Blazor projects). This checklist is written into the implementation plan as a sub-section of the phase **before any code is written.**

Example:
```
[YourEntity]List.razor — extracted from HAF-Chat-Mockups.html:
☐ @layout [YourBaseLayout] (not standalone MudContainer)
☐ Back-header: MudPaper with arrow_back MudIconButton + "Messages" title
☐ MudList with MudListItem per thread
☐ Thread item: avatar, gym name (bold if unread), last message preview, relative time
☐ FAB: MudFab Color.Primary for new message
☐ Empty state: MudAlert "No messages yet"
☐ MaxWidth: Large (not Small)
```

**Rules for the checklist:**
- One line per visual element. Not prose, not a paragraph. A checkable item.
- Use framework-specific component names (MudSelect, MudFab, MudAlert), not generic terms ("a dropdown," "a button").
- Include layout directives (@layout, MaxWidth, PageTitle).
- Include conditional states (empty, loading, error) if the mockup shows them.
- If no mockup exists for screens being built, this is the trigger to create one. The phase blocks until mockups are approved.
- **Mockup commit is part of approval.** A mockup is not considered approved until it is committed to the feature branch at `docs/{issue-folder}/`. A local working copy is a draft location only. The commit happens before the first implementation wave, not after. See `project-scoping-bp.md` "Reactive Phase Startup Sequence" for the full step order.

### Step B: Build

Normal implementation. Write the Razor code, wire up services, run CI. The checklist from Step A is the spec. Build to match it.

### Step C: Verify (after code compiles, before marking DONE)

Reopen the mockup. Walk the Component Spec Checklist from Step A line by line. For each item, mark it ✅ or ❌ with a note. The verification output is written into the implementation plan:

```
[YourEntity]List.razor — Verification:
✅ @layout [YourBaseLayout]
✅ Back-header with arrow_back + "Messages"
✅ MudList with MudListItem per thread
✅ Bold if unread (BoldIfUnread helper)
✅ FAB with MudFab
❌ Empty state — missing → FIXED in commit abc123
✅ MaxWidth.Large
Re-verified after fix: all ✅
```

**Gate rule:** Any ❌ means the component is not done. Fix all ❌ items, then re-run the full checklist (not just the fixed items, re-verify everything, because fixes can break other elements). The phase status only moves to DONE when every item is ✅ and the re-verification confirms it.

**What counts as a gap (❌):**
- Missing columns in a table that the mockup shows
- Missing UI sections (stat cards, summary panels, activity tables)
- Missing interactive elements (pagination, search, export, toggles)
- Different data shapes than what the mockup specifies
- Missing conditional states (empty state messaging, error alerts, loading indicators)
- Missing visual treatments (row highlighting, opacity on inactive rows, diff-colored values)
- Wrong layout directive (standalone MudContainer when mockup uses app chrome)
- Missing navigation elements (back button, FAB, page title)

### Mandatory Phase Plan Structure for UI Phases

Every phase that creates or modifies Razor pages must include these items in the phase plan, in this order:

```
X.1    Extract component spec from mockup — PENDING
...    (implementation items)
X.N-2  Verify against mockup — PENDING
X.N-1  CI verification — PENDING
X.N    Update implementation plan — PENDING
```

The Extract step is the first item. The Verify step comes after all implementation items but before CI. The plan update is the final mandatory step in every wave, mark the wave `DONE ✅`, add the commit SHA and CI run link to the wave's CI checklist, then push the plan update as a standalone docs commit. This ordering prevents two shortcuts: "CI is green, ship it" (skips mockup conformance) and "wave is done in my head" (skips plan synchronization).

**Plan update gate:** A wave is not closed until the implementation plan reflects it. After CI goes green: update the wave status in the plan, add the commit SHA and a link to the CI run, then push the plan change as a separate commit. The `paths-ignore: ['**/*.md', 'docs/**']` filter on the CI `push` trigger ensures this plan commit does not re-trigger the build. If the plan commit and the code commit are accidentally combined, CI runs anyway; the filter only skips CI when every file in the push falls within the ignored paths.

**Reactive phases (mid-PR additions):** When a new phase is created mid-implementation in response to reviewer feedback, the same structure applies. The first step is still "open the mockup and extract the spec for the screens being built." Reactive does not mean skip the gate.

### Lessons learned

**a prior project (March 2026):** All six SNOUT Razor pages diverged from their approved mockups during Phase [N]. Four had large gaps, two had moderate gaps. An unplanned Phase [N]b correction pass was needed. Root cause: pages were built from the service layer up rather than from the mockup down.

**a prior project (March 2026):** Phase [N] added two thread list pages without referencing the approved `HAF-Chat-Mockups.html`. Tyler's Round 3 review flagged 8 issues, all of which the mockup already addressed (layout directive, gym selector, FAB for new thread, back header, page titles, MaxWidth). Phase [N] fixed all 8 by building to the mockup spec. Root cause: Phase [N] was created reactively and skipped the Extract step entirely. The mockup was never opened. Every fix in Phase [N] was building what the mockup already showed. This is why the Extract → Build → Verify gate exists: it catches at build time what would otherwise surface as reviewer feedback.

**a prior project Phase [N] (March 2026):** Phase [N] mockup was created and approved during the planning conversation, but the file was saved to [YourWorkspace] root instead of `docs/Issue-[N]-Facility-Chat/`. Implementation proceeded and all CI was green, but the mockup wasn't a committed project artifact. Discovered post-implementation; required a separate cleanup commit (`37b19998`) and a PR comment update. Root cause: no rule required committing the mockup to the feature branch before waves started. Fix: added "Mockup commit is part of approval" rule above.

## 8.5 bUnit Component Testing

For Blazor component tests, use bUnit. A single shared UI test project (`[YourApp].Test.UI`, or bUnit tests added to the existing bounded-context test project) is preferred over one UI test project per context.

**Why one project:** bUnit test setup is identical across all bounded contexts: `AddMudServices()`, `JSInterop.Mode = JSRuntimeMode.Loose`, mocked `NavigationManager`, mocked `AuthenticationStateProvider`. Splitting by context duplicates this fixture setup for no benefit. Organize by folder instead (`Shared/`, `Snout/`, `MassNotify/`).

**Fixture requirements:**
- `bUnit.TestContext` with MudBlazor providers registered
- Mock service layer per context (`I*Service` interfaces)
- `JSInterop.Mode = JSRuntimeMode.Loose` for MudBlazor components that call JS interop

**What bUnit tests verify (that service-layer tests don't):**
- Component renders without throwing given valid, empty, and error service responses
- Interactive elements trigger the right service calls when clicked
- Conditional rendering works: loading states, empty states, error states display correctly
- Form validation messages appear for bad input
- Page navigation redirects correctly after operations complete

**What bUnit tests do NOT verify:**
- Visual appearance (CSS, layout, spacing). That's manual or screenshot-based testing.
- MudBlazor internal behavior. Trust the library; test your usage of it.
- API calls. Those are mocked; real calls are tested in service-layer tests.

**Pure HTML vs MudBlazor components:** Components that don't use MudBlazor (like `LoadingStateOverlay`, `TipTabControl`) test cleanly without JS interop mocking. MudBlazor components (like `StatCard`) require the full `AddMudServices()` + loose JS interop setup. Keep this in mind when adding new shared components; pure HTML components are simpler to test.

**Lesson learned (Issue-[N] Phase [N], March 2026):** bUnit 2.0.33-preview was required for .NET 10 compatibility. ThemeToggle tests were deferred because `ThemeService` has `InitializeAsync`/`OnChange` event patterns that add fixture complexity beyond the initial bUnit rollout.

## 8.6 MudBlazor Known Patterns

Common MudBlazor gotchas specific to the [YourProject] Blazor WASM project.

### CS1660: EventCallback ValueChanged with lambdas

When binding a lambda to a `ValueChanged` parameter that expects `EventCallback<T>`, the Razor compiler sometimes cannot infer the generic type from an implicit lambda and emits CS1660 ("Cannot convert lambda expression to type 'bool'").

**Broken:**
```razor
<MudCheckbox T="bool"
             ValueChanged="@(v => ToggleMember(member.UserId, v))" />
```

**Fix, use `EventCallback.Factory.Create<T>` explicitly:**
```razor
<MudCheckbox T="bool"
             ValueChanged="@(EventCallback.Factory.Create<bool>(this, (bool v) => ToggleMember(member.UserId, v)))" />
```

This pattern applies to any `ValueChanged`, `SelectedValuesChanged`, or similar `EventCallback<T>` parameter where the lambda captures a local variable and the compiler loses type inference.

### Never add `@using MudBlazor` in component files

`MudBlazor` is already imported globally via `[YourBlazorApp]/_Imports.razor`. Adding `@using MudBlazor` again in a `.razor` page causes CS0104 ambiguity on every MudBlazor type in that file (e.g., `'Color' is ambiguous between 'MudBlazor.Color' and 'System.Drawing.Color'`).

**Rule:** Do not add `@using MudBlazor` in any `.razor` component or page file. If a page needs `Color`, `Variant`, or any other MudBlazor type, it already has access through `_Imports.razor`.

## 8.7 Three-State Filter Pattern (non-nullable bool API)

When a UI needs three filter states (e.g., Active / Inactive / All) but the API method takes a non-nullable `bool` (e.g., `bool activeOnly`), use this pattern:

- **Active chip:** call `activeOnly: true` — server filters to active records only.
- **Inactive chip:** call `activeOnly: false` (returns all), then filter client-side: `_members.Where(m => !m.IsActive).ToList()`.
- **All chip:** call `activeOnly: false` — no client-side filter.

Store two lists: `_members` (raw API result) and `_displayMembers` (display-filtered for the current chip). Selection and downstream operations (e.g., `BulkSendRequestDto.MemberUserIds`) use IDs from the display list.

```csharp
private async Task LoadMembersAsync()
{
    bool activeOnly = _statusFilter == "Active";
    var result = await HafHttp.GetMembersForBulkSendAsync(gymId, activeOnly: activeOnly, search: _searchText);
    if (result?.ResultSuccessful == true && result.Result != null)
    {
        _members = result.Result;
        _displayMembers = _statusFilter == "Inactive"
            ? _members.Where(m => !m.IsActive).ToList()
            : _members;
    }
}
```

When chip changes: call `LoadMembersAsync()`, clear selection (`_selectedIds.Clear()`), re-render.

**IncludeDeactivated mapping** (for bulk send DTOs): `Inactive` or `All` chip → `IncludeDeactivated = true`.

## 8.8 SharedComponents Layer Check

Before committing any new Blazor page, ask: **"Will another platform (MAUI) eventually need the same UI?"**

If yes, or even if it's likely, the UI belongs in `SharedComponents/` as a self-contained component. The Blazor page becomes a thin routing shell. Building it as a page-only component forces MAUI to duplicate that work later, which is exactly what SharedComponents exists to prevent.

**Reference pattern:** `SharedComponents/Facility/FacilityList.razor` (self-contained component) + `[YourBlazorApp]/Pages/Locations.razor` (thin shell). The shell contains exactly five things: `@page`, `@attribute [Authorize]`, `@layout`, `@rendermode`, and the component tag. No logic, no service injection, no UI markup.

**Self-contained means:** The SharedComponent injects all its own services (`HafHttpClient`, `ChatConnectionService`, `ISharedNavigator`, `NavigationManager`) and owns all UI, including the back header, loading state, empty state, and action buttons. Nothing is passed via `[Parameter]` that the component could resolve itself via DI.

**RZ9985, class name collision:** When a SharedComponent is in scope via `@using SharedComponents.{Namespace}`, the page shell file must have a different filename (and therefore a different Blazor-assigned class name) than the SharedComponent. The Blazor compiler derives class names from filenames. Two files named `[YourEntity]List.razor` in different namespaces but both in scope produce RZ9985: "Multiple components use the same tag." Convention: page shells are named by route concept (`MessagesPage.razor`, `NewMessagePage.razor`); SharedComponents are named by component function (`[YourEntity]List.razor`, `ChatNewThread.razor`). Routing is determined solely by the `@page` directive, never by the class name.

**When discovered late (migration pattern):** If a page was built in `[YourBlazorApp]/Pages/` and needs to move into SharedComponents: (1) copy all logic and markup into a new `SharedComponents/{Namespace}/ComponentName.razor` file; (2) reduce the original page file to a thin shell; (3) rename the page file if needed to avoid RZ9985; (4) run CI and confirm green; (5) run the mockup conformance check against the SharedComponent.

**Applies to all page modifications, not just new pages.** If you are adding content to an existing page that exists in both WASM and MAUI (e.g., adding a Messages card to `AdminHome.razor`), check whether the page has already been extracted to a SharedComponent. If both platform copies exist with duplicated logic, extract to a SharedComponent as part of the change. Do not add the content to both platform copies independently.

**Lesson learned (a prior project Phase [N], March 2026):** Three chat screens were built as full pages in `[YourBlazorApp]/Pages/`. Tyler's Round 4 review flagged that MAUI would need the same UI. A full architectural refactor was required after all CI was green. **Second lesson (a prior project handoff, March 2026):** During the same project, we added UI to both `AdminHome.razor` copies (WASM and MAUI) instead of extracting to a SharedComponent. Tyler's team later created `AdminHomeComponent.razor` in PR #[N] to eliminate the duplication. The rule existed; we failed to apply it to our own non-chat modifications.

---

## Corrections Log

*Tracks issues found when following this file's instructions. Entries are added when a discrepancy is discovered and a fix is applied or proposed.*

| Date | What Failed | Root Cause | Fix Applied | ERRORS.md Ref |
|------|-------------|------------|-------------|---------------|

**Notes:**
<!-- Per-entry context that doesn't fit in the table. Format: "YYYY-MM-DD: [explanation]" -->
