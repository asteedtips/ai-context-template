# Decisions Table & Standard Question Bank

> **Part of the Project Scoping Graph.** This file covers the decisions table format and the standard question bank. For the full scoping index, see `project-scoping-index.md`.

## The Decisions Table: Gating Artifact

The decisions table is mandatory for every project. **No code starts until the decisions table is populated and reviewed.**

The table captures every design choice, behavioral rule, and trade-off that affects implementation.

### Format

| Decision | Answer |
|----------|--------|
| [Short description of the question] | [Specific answer with enough context to implement against] |

### What belongs in the decisions table

Any question where the answer changes what code gets written:

- Behavioral rules: "Can inactive users still access this?" / "Does the system support both API key and OAuth?"
- Data model choices: "One record per user, or multiple?" / "How is multi-tenancy keyed?"
- UX decisions: "Admin sees name A or name B?" / "Pagination style: page-based or cursor-based?"
- Integration boundaries: "Polling or webhooks?" / "What auth method for external APIs?"
- Feature gates: "Hidden or locked when disabled?"
- Security and deployment: "Shared or separate deployment unit?" / "What are the trust boundaries?"

### What does NOT belong

- Implementation details that follow from the decision
- Pattern choices already standardized in your coding standards
- Testing strategy (that has its own section)

### Process for populating

1. **Start with the standard question bank below.** Mark what applies to this project.
2. **Add project-specific questions** the standard bank doesn't cover.
3. **Answer every applicable question** before moving forward. If you need research or stakeholder input, do it now using AskUserQuestion or equivalent.
4. **Review the completed table** as a unit. Look for contradictions and implications.

---

## Standard Question Bank

Not all questions apply to every project. Run through this list and answer the ones that do.

### Architecture & Hosting

- Where does this code live in the solution? New bounded context or extension of existing?
- What's the hosting model? Cloud service, function, API, frontend component?
- Does this need its own deployment pipeline, or deploy with existing code?
- Single-tenant or multi-tenant? If multi-tenant, how is tenant isolation achieved?
- Does this introduce a new external dependency (third-party API, new cloud service, new library)?
- Does a CI pipeline exist? If not, it's a prerequisite. If yes, does it need updating for new test projects?
- **What are the existing conventions for this type of component?** Before applying a generic best practice, check what the codebase already does. Use the dominant convention. If it should change, flag it separately.

### Data & Persistence

- What new entities/tables are needed? What are the relationships?
- Does this modify existing entities? Which ones and how?
- Do existing rows need migration or backfill scripts?
- What's the data retention policy? Archive, soft delete, hard delete?
- Are there default assumptions that need to change?
- **For new entities: run through the entity checklist** (primary key, audit columns, indexes, relationships, temporal table configuration). Every item a sibling entity has, the new one should too.

### Authentication & Authorization

- How is this authenticated? API key, JWT, OAuth, cloud identity, other?
- What authorization model? Role-based, resource ownership, feature flags, combination?
- Are there different permission tiers?
- Does this need rate limiting? If so, what are the limits?

### Integration & External APIs

- What external APIs does this call? What auth do they use?
- What's the retry strategy for transient failures?
- Are API credentials already stored securely, or do new secrets need adding?
- Is data pulled (polling), pushed (webhooks), or both?
- How does the external API report failures?
- **Do sandbox environments exist for each external system this feature writes to?** If any endpoint lacks a sandbox that mirrors production, the feature must include a Dry Run / test mode. This is a scoping decision, not a testing afterthought.
- **Are there shared infrastructure changes needed before this feature work starts?** (e.g., shared config structure changes, authentication refactors, shared service updates). If yes, scope and phase them separately. Don't discover these mid-build.

### UI & User Experience

- Is there a user interface? If so, where does it live (shared, pages, standalone)?
- Who are the user roles? Do they see different views?
- How do users discover this feature? Navigation changes, feature flags, new routes?
- What's the notification model? In-app, push, email, combination?
- **What's the expected data scale for list/selection controls?** If lists could exceed ~20-30 items, use a searchable component instead of a static dropdown. This is a scoping decision.

### Testing & Quality

- What's the minimum test coverage?
- What paths must be 100% covered?
- Can tests run without external dependencies?
- What's the mocking strategy?
- Will tests run in CI, or are some excluded?

### Operational

- How is this monitored in production?
- What happens when this fails? Graceful degradation, retry, alert?
- Are there compliance considerations? (data protection, security, industry standards)
- Does this affect existing features? What's the backward compatibility plan?

### Project-Specific Questions

Add questions unique to your domain that the standard bank doesn't cover. Document them in the decisions table with the same rigor as the standard questions.

---

## Corrections Log

*Tracks issues found when following this file's instructions.*

| Date | What Failed | Root Cause | Fix Applied |
|------|-------------|------------|-------------|

