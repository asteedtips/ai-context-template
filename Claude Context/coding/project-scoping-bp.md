# Project Scoping Best Practices — Code Projects
**[YOUR NAME] | [YOUR TITLE] | [YOUR COMPANY]**
*Reference file for scoping any project that involves writing code*
*Last Updated: [DATE]*

---

> **How to use this file**: Read this file before starting any code project — new feature, integration, migration, or refactor. It defines the scoping process, the mandatory artifacts, and the section template for the project plan doc. The goal is to identify every decision, boundary, and dependency before the first line of code is written.

> **Cross-references**: `coding-best-practices.md` governs code standards. `writing/best-practices-creation.md` governs documentation output format. `writing/banned-writing-styles.md` applies to all written content. `security/security-practices.md` governs credential handling. This file governs the scoping process that happens before any of those come into play.

---

## 1. Two Scoping Tracks

Not every project needs the same depth. This doc defines two tracks based on whether you're building something new or plugging into something that already exists.

**Track A — Greenfield / New Bounded Context**
Use this when the project introduces new entities, new API surface, new UI components, or a new bounded context in the solution.

Track A uses the full template (all sections below).

**Track B — Pattern-Following Integration**
Use this when you're adding a new implementation of an existing abstraction. The architecture, interfaces, and data model already exist — you're writing a new provider, adapter, or connector.

Track B uses an abbreviated template: Decisions Table, Out of Scope, Files to Create/Modify, Testing Sequence, and Changelog. Skip sections that are already governed by the pattern doc (architecture, data model, phasing).

**When it's not obvious which track applies**, default to Track A. A scope doc with too much detail is never the problem. A scope doc with too little always is.

---

## 2. The Decisions Table — Gating Artifact

The decisions table is the single most effective scoping artifact. It is mandatory for every project, both tracks. **No code starts until the decisions table is populated and reviewed.**

The table captures every design choice, behavioral rule, and trade-off that affects implementation. Each row is a question that was asked, answered, and documented.

### Format

| Decision | Answer |
|----------|--------|
| [Short description of the question] | [Specific answer with enough context to implement against] |

### What belongs in the decisions table

Any question where the answer changes what code gets written. Specifically:

- Behavioral rules: "Can deactivated users still send messages?" / "Does the flow support both payment methods, or just one?"
- Data model choices: "One thread per user pair, or multiple?" / "Multi-tenant dictionary keyed by org ID?"
- UX decisions: "Admin sees display name or real name?" / "Cursor-based or page-number pagination?"
- Integration boundaries: "Polling or webhooks?" / "API key auth or OAuth?"
- Feature gates and notification strategy: "Hidden entirely when disabled, or visible but locked?" / "Push only, email only, or both?"
- Security and deployment choices: "Function-level auth with IP whitelist, or JWT?" / "Same App Service or separate?"

### What does NOT belong in the decisions table

- Implementation details that follow directly from the decision (an implementation choice, not a scoping decision)
- Pattern choices that are already standardized (things in coding-best-practices.md — don't repeat them)
- Testing strategy (that has its own section)

### Process for populating

1. **Start with the standard question bank** (Section 3 below). Run through every question. Mark the ones that apply to this project.
2. **Add project-specific questions** that the standard bank doesn't cover. Every domain has its own edge cases.
3. **Answer every applicable question** before moving to the next section. If an answer requires research, research it. If it requires user input, present selectable options — don't leave it as an open question.
4. **Review the completed table** as a unit. Look for contradictions, gaps, and implications. One decision often forces another.

---

## 3. Standard Question Bank

These questions apply to most code projects. Not all will be relevant to every project. The scoping process starts by running through this list, marking what applies, and answering what does.

### Architecture & Hosting

- Where does this code live in the solution? New bounded context or extension of an existing one?
- What's the hosting model? App Service, Functions, standalone API, frontend framework?
- Does this need its own deployment pipeline, or does it deploy with an existing app?
- Single-tenant or multi-tenant? If multi-tenant, how is tenant isolation achieved?
- Does this introduce a new external dependency (third-party API, new cloud service, new package)?

### Data & Persistence

- What new entities/tables are needed? What are the relationships?
- Does this modify existing entities? If so, which ones and how?
- Do existing rows need backfilling or migration scripts?
- What's the data retention policy? Archive, soft delete, hard delete, temporal tables?
- Are there default value assumptions that need to change?

### Authentication & Authorization

- How is this authenticated? JWT, function key, identity platform, API key, other?
- What authorization model applies? Role-based, resource-ownership, feature flags, or a combination?
- Are there different permission tiers?
- Does this need rate limiting? If so, what are the limits and the window?

### Integration & External APIs

- What external APIs does this call? What auth model do they use?
- What's the retry strategy for transient failures?
- Are API credentials already in your secret store, or do new secrets need to be added?
- Is data pulled (polling), pushed (webhooks), or both?
- What's the error contract? How does the external API report failures?
- **Does this feature require changes to shared services, config structures, or infrastructure that other features depend on?** If yes, those prerequisite changes must be scoped and completed before the feature work begins. Don't discover shared infrastructure changes mid-build.

### UI & User Experience

- Is there a UI component? If so, where does it live?
- Who are the user roles that interact with this? Do they see different views?
- How does the user discover this feature? Navigation changes, feature flags, new routes?
- What's the notification model? In-app, push, email, some combination?

### Testing & Quality

- What's the minimum test coverage for this feature?
- What are the must-test paths (100% coverage required)?
- Can tests run without external dependencies?
- What's the mocking strategy?

### Operational

- How is this monitored in production?
- What happens when this fails? Graceful degradation, retry, alert?
- Are there compliance considerations (PCI, HIPAA, SOC2, etc.)?
- Does this affect existing features? If so, what's the backward compatibility plan?

### Project-Specific Questions

After running through the standard bank, add questions unique to this project's domain. These are the ones no template can predict.

---

## 4. Out of Scope — Mandatory

Every project scope doc includes an out-of-scope section. This is not optional, regardless of project size or track. The purpose is to draw the line early so it doesn't get drawn mid-implementation when the cost is higher.

### Format

| Item | Rationale |
|------|-----------|
| [Feature or capability being excluded] | [Why it's excluded and when it might be revisited] |

### How to populate

1. For every decision in the decisions table, ask: "What related thing are we NOT doing?"
2. For every user-facing feature, ask: "What would a user expect that we're not building?"
3. For every integration, ask: "What API capabilities exist that we're not using?"

---

## 5. UI Validation Mockups (Track A Only)

For any project with a user-facing interface, build lightweight mockups after the decisions table is populated and out-of-scope items are defined. The purpose is to validate UI-related decisions visually before moving into data models and phasing.

### When to use this step

Any Track A project where the decisions table contains answers about screens, user flows, roles with different views, navigation changes, or notification presentation. If the project is purely backend, skip this section. For backend projects, the equivalent validation tool is a sequence diagram or data flow diagram (use Mermaid per `writing/best-practices-creation.md`).

### What to build

Single-file HTML mockups. No frameworks, no build step. Each mockup should show:

1. **Screen states per role.** If the decisions table says "admin sees X, member sees Y," build both views.
2. **State transitions.** Empty state, loading, populated, error.
3. **Navigation flow.** How the user gets to the feature.
4. **Notification presentation.** If applicable, show how notifications appear in context.

### Post-Implementation Verification (Mandatory)

After each UI component is built, verify it against the approved mockup before marking it done. See `coding-best-practices.md` for the full per-component verification process.

---

## 6. Existing Pattern References

The scope doc does not duplicate code patterns that are already documented elsewhere. Instead, it lists which existing pattern docs apply and calls out any deviations.

### Format

| Pattern Doc | Applies To | Deviations |
|-------------|-----------|------------|
| `coding-best-practices.md` Section X | DI registration | None — follow standard pattern |
| `security-practices.md` Section Y | Secrets | Two new secrets to add |

---

## 7. Draft Data Models (Track A Only)

For greenfield projects, the scope doc includes draft entity definitions. These are not final but drafting them during scoping forces decisions about relationships, nullability, default values, and data types.

### What to include

- New entity classes with properties, types, and relationships
- New enums with values and backing types
- Modifications to existing entities
- Migration scripts for backfilling existing data

### What to skip

- ORM configuration details (follow established patterns)
- Full DTO/ViewModel definitions (derive from entities during implementation)
- Stored procedures (define the need, not the SQL)

---

## 8. Phased Delivery Plan

Every project is broken into ordered phases. Phases are about dependency ordering and review gates, not scheduling. No hour estimates.

### Phase structure rules

- Each phase produces something testable or reviewable.
- Phases are ordered by dependency. Data model before service layer. Service layer before API. API before UI.
- Each phase lists the files to create or modify.

### Plan drift rule

When implementation deviates from the scope doc (data model changes, phase reordering, new entities added), **update the plan doc in the same session, not as a catch-up exercise later.** Log every deviation in the changelog with the date and reasoning.

### Pattern compliance check

After each phase completes, verify that the built code follows the patterns listed in the "Existing Pattern References" section of the scope doc. This catches drift between decisions and actual implementation.

### Phase naming convention

Use descriptive names, not just numbers. "Phase 3: SignalR Hub & Real-Time Messaging" is better than "Phase 3."

---

## 8b. Implementation Orchestration & Progress Tracking

Every project plan includes an orchestration section that defines how phases execute and a progress tracker that logs every component as it's completed.

### Wave-Based Parallelization

Group phases into waves based on dependency. Phases within a wave can execute concurrently.

```
Wave 1 (parallel):
  ├── Phase 1a — [description]
  └── Phase 1b — [description]

Wave 2 (after Wave 1):
  └── Phase 2 — [description]
```

**Rules:**
- A wave only starts after all phases in the preceding wave are complete.
- Within a wave, phases must not have file-level conflicts.
- Not every project needs parallelization. Small projects (3-4 phases) can stay sequential.

### Per-Component Progress Tracker

| Phase | Component | Status | Commit | Notes |
|-------|-----------|--------|--------|-------|
| 1 | Entity.cs | DONE | abc1234 | — |
| 3 | FeatureService.cs | IN PROGRESS | — | Blocked on API format |
| 4 | FeaturePage.razor | PENDING | — | — |

**Status values:** `PENDING`, `IN PROGRESS`, `DONE`, `BLOCKED`, `SKIPPED`

---

## 9. Testing Strategy

The scope doc defines how this project will be tested.

### Minimum content

- **Coverage target**: Default is 70% per `coding-best-practices.md`. If higher is needed for specific paths, state which.
- **Must-test paths**: List areas that need 100% coverage (auth, money handling, data mutations).
- **Mocking strategy**: What gets mocked and what uses real implementations.
- **Test isolation**: Can tests run without external services?

---

## 10. Changelog — Mandatory

Every scope doc has a changelog section. Any change made after the initial scope is approved gets logged.

### Format

| Date | Change | Reason |
|------|--------|--------|
| [DATE] | [What changed] | [Why it changed] |

### Rules

- Log every change that affects the decisions table, data model, phase plan, or out-of-scope list.
- If a change contradicts a previous decision, note the original and why it changed.

---

## 11. Scope Doc Template

Every project plan doc follows this section order. Sections marked as Track A only can be skipped for Track B.

```markdown
# [Project Name] — Project Plan

**Created:** [Date]
**Updated:** [Date]
**Status:** [Scoping / In Progress / Code Complete / Deployed]

---

## 1. Overview
[One paragraph: what is being built and why.]

## 2. Decisions Table
[Mandatory — see Section 2 above]

## 3. Out of Scope
[Mandatory — see Section 4 above]

## 4. Architecture & Where Code Lives (Track A only)
[Solution structure, new projects, layering, hosting model]

## 5. UI Validation Mockups (Track A only, if UI exists)
[HTML mockups validating UI decisions]

## 6. Existing Pattern References
[Links to pattern docs with deviation notes]

## 7. Data Model (Track A only)
[Draft entities, enums, migration scripts]

## 8. Phased Delivery Plan
[Ordered phases with files to create/modify]

## 8b. Implementation Orchestration & Progress
[Wave map, progress tracker, integration items]

## 9. Testing Strategy
[Coverage, must-test paths, mocking, isolation]

## 10. Changelog
[Mandatory]
```

---

## 12. Scoping Process — Step by Step

**Step 1 — Identify the track.** Greenfield (Track A) or pattern-following (Track B)? If unsure, default to Track A.

**Step 2 — Run the standard question bank.** Go through every question in Section 3. Mark what applies. Present one question at a time so each answer can inform the next.

**Step 3 — Add project-specific questions.** Based on the domain, add questions the standard bank doesn't cover.

**Step 4 — Populate the decisions table.** Every answered question becomes a row.

**Step 5 — Define what's out of scope.** For every decision, ask what related thing is NOT being built.

**Step 6 — Build UI validation mockups (Track A, if UI exists).** Walk through each screen against the decisions table. Update decisions and out-of-scope as needed.

**Step 7 — Reference existing patterns.** List which pattern docs apply and note deviations.

**Step 8 — Draft data models (Track A only).** Write the entity definitions.

**Step 9 — Build the phase plan.** Break work into ordered phases. List files per phase.

**Step 10 — Define testing strategy.** Coverage target, must-test paths, mocking approach.

**Step 11 — Review the complete scope doc.** Read as a unit. Look for contradictions and gaps.

**Step 12 — Get approval and start building.** The scope doc is the contract.

---

## 13. Quality Checklist

Before marking a scope doc complete, verify:

- [ ] Decisions table is populated with specific, implementable answers (not "TBD")
- [ ] Out of scope section exists with at least one entry
- [ ] Every applicable question from the standard bank has been answered
- [ ] UI mockups built and reviewed (Track A with UI), or sequence diagram built (backend-only)
- [ ] Existing pattern references listed with deviation notes
- [ ] Data model drafts included (Track A) with relationships and defaults
- [ ] Phases ordered by dependency, each producing something testable
- [ ] Testing strategy specifies coverage target, must-test paths, and mocking approach
- [ ] Changelog section exists
- [ ] No banned vocabulary from `writing/banned-writing-styles.md`
- [ ] File saved to the correct location with the correct naming convention

---

*Read this file before starting any code project. As new projects are scoped and built, update the standard question bank with questions that keep recurring.*
*Last updated: [DATE]*
