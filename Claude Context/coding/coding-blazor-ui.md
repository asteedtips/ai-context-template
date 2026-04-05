# Blazor / UI Standards

> **Part of the Coding Standards Graph.** This file covers all Blazor and UI patterns. For the full standards index, see `coding-index.md`.

## 8.1 Component Patterns

- Keep Razor components focused. If a component exceeds ~200 lines, split it into smaller child components.
- Use code-behind files (`.razor.cs`) for components with substantial C# logic.
- Share common functionality through base classes.

### 8.1.1 CSS Class and Style Building

For dynamic CSS class assignment, use a builder pattern instead of inline string concatenation:

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

### 8.1.2 New Routable Page Checklist

When adding a new `@page` component, verify:

1. **DI verification**  -  every injected service is registered in your dependency injection setup
2. **Navigation entry**  -  the page is reachable from the UI (menu item, button, or link)
3. **Route mapping**  -  if your app uses a centralized router, confirm the route is mapped
4. **Auth/layout directives**  -  match the pattern of sibling pages in the same area
5. **Both platforms**  -  if your app spans multiple platforms (web + mobile), verify the page setup in each

### 8.1.3 Page Header Consistency

Check existing pages in the same feature area before building a page header. Use the same UI framework components and patterns for visual consistency.

**Rules:**
- When building a list/index page, use the standard app layout/chrome to avoid duplication
- When building an immersive detail page (e.g., a detail view), a custom back header is appropriate
- Check 2-3 sibling pages to see which components they use

### 8.1.4 Dialog and Form Validation Checklist

Every dialog that accepts input must include:

1. **Required field validation:** Mark required fields and show validation errors
2. **Form validity tracking:** Disable submit button while form is invalid
3. **Submit button gating:** `Disabled="@(!isValid || isLoading)"`
4. **Loading state:** Show loading indicator while the operation runs
5. **Validation functions:** Custom validators for complex formats (email, phone, etc.)

## 8.2 State Management

- Don't store state in static fields. Use scoped services, cascading parameters, or a state container pattern.
- For cross-component communication, use events or scoped services, not direct component references.

## 8.3 Error Boundaries

- Use error boundary components to catch rendering errors gracefully.
- Log component exceptions to your telemetry service.
- Display user-friendly error messages, not raw exception text.

## 8.4 Mockup Conformance: Extract, Build, Verify

When approved mockups exist, every component must pass a three-step gate before marking done:

**Step A: Extract (before writing code)**

Open the approved mockup and create a numbered checklist of every visual element:

```
ComponentName.razor  -  extracted from mockup:
☐ Layout directive: use standard app chrome
☐ Header bar with back button and title
☐ List with items
☐ Item shows: name, status, timestamp
☐ FAB for new item
☐ Empty state message
☐ MaxWidth: Large
```

Rules:
- One line per element, not prose
- Use framework-specific component names
- Include all conditional states (empty, loading, error)
- If no mockup exists, create one and get approval before starting implementation

**Step B: Build**

Write the component code to match the checklist from Step A.

**Step C: Verify (before marking done)**

Walk the checklist against the actual component. Mark each item ✅ or ❌:

```
ComponentName.razor  -  Verification:
✅ Standard app chrome
✅ Header with back button and title
✅ List items render
✅ Item displays name, status, timestamp
❌ FAB missing  -  FIXED in commit abc123
✅ Empty state shows
✅ MaxWidth.Large
Re-verified: all ✅
```

**Gate rule:** All items must be ✅ before the component is done. Fix any ❌ items and re-verify the full checklist.

## 8.5 Component Testing (bUnit or equivalent)

For component tests, use your framework's component testing tool (bUnit for Blazor, Playwright for web, etc.).

**What component tests verify:**
- Component renders without throwing given valid, empty, and error responses
- Interactive elements trigger the right service calls when clicked
- Conditional rendering works: loading states, empty states, error states display correctly
- Form validation messages appear for bad input

**What component tests do NOT verify:**
- Visual appearance (CSS, layout, spacing)  -  use manual or screenshot testing for that
- Framework library internals  -  trust the library
- API calls  -  those are mocked and tested in service-layer tests

## 8.6 UI Framework Patterns

<!-- CUSTOMIZE: Document specific patterns for your UI framework. Examples:

### MudBlazor Example: EventCallback with Lambdas

When binding a lambda to an `EventCallback<T>` parameter, explicitly create the callback:

```razor
<MudCheckbox T="bool"
             ValueChanged="@(EventCallback.Factory.Create<bool>(this, (bool v) => ToggleMember(member.Id, v)))" />
```

### MudBlazor Example: Global Imports

If your framework components are globally imported, don't re-import them in individual component files  -  this causes type ambiguity errors.

**Rule:** Add framework using statements only to `_Imports.razor`, not to individual `.razor` files.

### Three-State Filter Pattern

When UI needs three states (Active / Inactive / All) but the API takes a boolean:

```csharp
private async Task LoadItemsAsync()
{
    bool activeOnly = _statusFilter == "Active";
    var result = await ApiClient.GetItemsAsync(activeOnly: activeOnly);
    if (result?.Success == true)
    {
        _items = result.Data;
        _displayItems = _statusFilter == "Inactive"
            ? _items.Where(m => !m.IsActive).ToList()
            : _items;
    }
}
```

Store two lists: `_items` (raw API result) and `_displayItems` (filtered for display). Use the display list for selection and downstream operations.
-->

## 8.7 Component Reuse Across Platforms

If your app spans multiple platforms (web and mobile), ask: **"Will the other platform eventually need this UI?"**

If yes, build the component in a shared library so both platforms can use it. Only platform-specific routing should differ.

**Rule:** Self-contained components belong in shared, not duplicated across platforms.

---

## Corrections Log

*Tracks issues found when following this file's instructions.*

| Date | What Failed | Root Cause | Fix Applied |
|------|-------------|------------|-------------|

