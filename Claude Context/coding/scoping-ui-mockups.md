# UI Validation Mockups

> **Part of the Project Scoping Graph.** This file covers UI mockup creation, review, and the reactive phase startup sequence. For the post-implementation verification gate (Extract-Build-Verify), see `coding-blazor-ui.md` Section 8.4.

For any project with a user-facing interface, build lightweight mockups after the decisions table is populated and out-of-scope items are defined. The purpose is to validate UI-related decisions visually while the cost of changes is still low.

## When to use this step

Any project where the decisions table contains answers about screens, user flows, roles with different views, navigation, or notifications. If the project is purely backend (APIs, pipelines, integrations with no UI), create sequence diagrams or data flow diagrams instead.

## What to build

Single-file HTML mockups. No frameworks, no build step. The goal is reviewability and speed. Each mockup should show:

1. **Screen states per role.** If decisions say "admin sees X, member sees Y," build both views.
2. **State transitions.** Empty state, loading, populated, error. Focus on states where the decision could change based on visual inspection.
3. **Navigation flow.** How the user discovers and moves between screens.
4. **Notification presentation.** If the decisions include notification choices, show how they appear in context.

## What NOT to build

- Pixel-perfect designs. These are wireframes for validation, not design comps.
- Responsive breakpoints. Build for the primary platform first.
- Interactive prototypes with real data binding. Static HTML with sample data is enough.

## Review process

1. Walk through each mockup screen against the decisions table. For every UI-related decision, confirm: "Does this match what you meant?"
2. Flag any new questions the mockup surfaces. (New decisions discovered during visual validation.)
3. Update the decisions table with any changed decisions. Log changes in the changelog.
4. Define new out-of-scope items the mockup reveals.

## Post-Implementation Verification: Hard Gate (Mandatory)

Mockups are not just validation tools during scoping. They are the spec that implementation is measured against. Every UI component goes through a three-step gate: **Extract → Build → Verify.**

**The three-step gate (summary; see `coding-blazor-ui.md` Section 8.4 for full detail):**

1. **Step A, Extract:** Before writing code, open the mockup and produce a Component Spec Checklist: one line per visual element, written in your framework's language (e.g., component names). Write this into the phase plan.
2. **Step B, Build:** Implement the component using the checklist as the spec.
3. **Step C, Verify:** After code compiles, walk the checklist against the implementation, marking each ✅ or ❌. Fix any ❌, then re-verify the full list. Write the output into the phase plan.

**Gate enforcement:** A component's status cannot move to DONE until the verification artifact exists and shows all items passing.

**Reactive phases:** When a phase is created mid-implementation, the same gate applies. The first step is still "open the mockup and extract the spec."

### Reactive Phase Startup Sequence

When a new phase is created mid-implementation, run this sequence in order before planning waves:

1. **Create mockup:** Single-file HTML covering all screens affected by the feedback.
2. **Save and commit to the feature branch.** The mockup is a project artifact, not a working document. It must be in the repo before approval, not after implementation.
3. **Get approval.** Walk through each screen. Record any changes. Update the file if it changes.
4. **Plan implementation waves.** Only after the committed mockup is approved. Reference the committed file path.
5. **Extract component spec (Step A),** per wave.

The commit at step 2 is the gate. If the mockup isn't in the repo, the phase hasn't started, regardless of approval.

## Component Mapping Table

When your framework is known at scoping time, the mockup or an adjacent document should map visual elements to framework components:

```
Visual Element    → Framework Component
Button list       → [Your framework's list component]
Search field      → [Your framework's search input]
Modal dialog      → [Your framework's dialog component]
Back navigation   → [Your framework's nav element]
```

The mapping prevents "build from the API up" where the mockup's intent gets lost in translation.

---

## Corrections Log

*Tracks issues found when following this file's instructions.*

| Date | What Failed | Root Cause | Fix Applied |
|------|-------------|------------|-------------|

