# AI Context System — Template

Most people use AI like a search engine with better grammar. They type a prompt, get an answer, and start over next time. Every session begins at zero.

This repo exists because there's a better way.

## The Problem

AI agents are stateless by default. They don't remember your preferences, your tools, your team, your writing voice, or the decisions you made last Tuesday. So you end up repeating yourself constantly, getting generic output, and spending more time correcting the AI than you would have spent doing the work yourself.

The people getting real value from AI aren't writing better prompts. They're building persistent context that compounds across sessions.

## What This Is

A set of `.md` files that sit alongside your AI agent (Claude, GPT, or any LLM with file access). They act as operating instructions and persistent memory. Instead of re-explaining your preferences, tools, and workflows every session, the agent reads these files at startup and operates with full context from the first message.

This template was extracted from a production system used daily for sales proposals, pipeline management, email triage, code review, SEO content, and document creation at a real company. It's not theoretical — every file exists because a real workflow needed it.

**What's included:**

- **Writing rules** — a researched list of AI-identifiable words, phrases, and patterns that make output sound robotic. Ready to use immediately.
- **Agent operating instructions** — how the AI should behave: ask before acting, build on what worked, research before responding, maintain statefulness.
- **Documentation standards** — output formats, Mermaid diagram types, quality checklists, file naming conventions.
- **Sales framework** — qualification methodology structure, pipeline hygiene rules, health scoring, and deal removal criteria.
- **Proposal workflow** — customer-centric proposal structure, intake questions, CRM data collection, QC checklist.
- **Credential management** — architecture pattern for keeping API secrets out of plain text files (encrypted bootstrap → cloud vault → session-scoped env vars).
- **Email processing** — inbox triage categories, routing rules, and a confirm-before-moving protocol.
- **SEO workflow** — keyword strategy, intent-first planning, and verification checklist.
- **Coding standards** — layered architecture, DI patterns, error handling, testing targets, CI/CD pipeline requirements.
- **Task tracking and glossary** — persistent task board and a decoder ring for your internal shorthand.

---

## The C-I-M Framework

The system is built on three principles: **Context**, **Interaction**, and **Memory**.

**Context** is the knowledge base. These files teach the agent who you are, how you work, what tools you use, and what standards you expect. Context compounds — every file you add makes the agent more useful. Context is the only part of an AI workflow that appreciates over time. Prompts depreciate the moment you send them.

**Interaction** is the operating model. The agent asks targeted questions before starting (using selectable options, not text walls), integrates everything you share as foundational context, builds on outputs you've confirmed as good, and researches before responding when current information matters. The goal is zero context-switching for you — the agent handles the legwork and presents results.

**Memory** is the persistence layer. A glossary that decodes your shorthand and tracks lessons learned. A task board that carries over between sessions. A changelog that lets the agent scan what's new since its last session. Memory is what turns isolated conversations into a compounding knowledge graph.

Most people focus on prompts (the Interaction layer) and ignore Context and Memory entirely. That's why their output plateaus. This template gives you all three from day one.

---

## Best Practices for Building Your Context System

These patterns come from months of daily production use. Follow them and you'll avoid the mistakes that cost the most time.

### 1. Start with three files, not thirteen

Don't try to fill in everything at once. Start with:

1. **`CLAUDE.md`** — Your name, company, and the "How I Expect You to Work" section
2. **`banned-writing-styles.md`** — Use it as-is on day one. It works immediately.
3. **`memory/glossary.md`** — Add your team members and the acronyms you use daily

Everything else can wait until you actually need it. The sales framework matters when you're doing sales work. The coding standards matter when you're writing code. Don't front-load setup for workflows you won't touch this week.

### 2. Separate public frameworks from private data

This repo is the public half — frameworks, standards, and process templates. Your private data (API credentials, customer names, CRM configs, proprietary methodology, pricing, team details) lives in a separate private repo or folder.

The `PRIVATE-FILES.md` file documents exactly which files should stay private and which ones have a public template counterpart. The split matters because you want to update frameworks without exposing business data, and share useful patterns without leaking credentials.

### 3. Use dependency chains, not a flat file list

Not every task needs every context file. Loading thirteen files when you only need two wastes token budget and dilutes the agent's focus. The `CLAUDE.md` template includes a workflow dependency chain table:

| Workflow | Files to Load (in order) |
|----------|--------------------------|
| Casual conversation | `banned-writing-styles.md` only |
| Proposal creation | `security-practices.md` → `[crm]-api.md` → `proposal-generation.md` → `best-practices-creation.md` → `banned-writing-styles.md` |
| Code work | `coding-best-practices.md` → `security-practices.md` |

This tells the agent exactly what to read and in what order. Lightweight tasks stay fast. Complex tasks get full context.

### 4. Never duplicate content across files

When the same information appears in multiple files, it drifts. One file gets updated, the others don't, and the agent gets contradictory instructions. Instead, use cross-references: "See `security-practices.md` for the full credential architecture." One source of truth per topic.

### 5. Make the agent ask before acting

The single biggest quality improvement isn't a better prompt — it's a rule that says "ask 1-3 clarifying questions before starting any non-trivial task." This is baked into `working-style.md` and `CLAUDE.md`. It catches wrong assumptions before they become wrong outputs.

The key detail: the agent should present questions as selectable options, not plain text. Clicking a choice takes two seconds. Typing a correction after a wrong first draft takes ten minutes.

### 6. Track what works, ban what doesn't

The `banned-writing-styles.md` file is a living document. When the agent produces a phrase that sounds robotic, add it to the ban list. When a format works well, note it in the relevant context file. Over time, your context system converges on output that sounds like you wrote it — because the ban list is shaped by your taste, not a generic style guide.

### 7. Log lessons in the glossary

The glossary isn't just a decoder ring. It has a Lessons Learned section where you record patterns: "LESSON: Deals stall when Impact is unquantified. RULE: Never leave a discovery call without at least one number attached to the problem." The agent reads this at session start. Mistakes made once don't repeat.

### 8. Push context to version control

These files should be in a Git repo (private for your actual data, public for the template). Version control gives you history, rollback, and the ability to sync across machines. The `CLAUDE.md` template includes a session-start sync sequence that pulls latest context from GitHub before the agent does anything else.

### 9. Internal deliverables stay lightweight

Plans, analysis, audit findings, and anything between you and the AI should be inline chat or `.md` files. Don't generate a formatted `.docx` for something only you will read. Reserve polished documents for external audiences — clients, staff, board members. This saves time and keeps the feedback loop tight.

### 10. End with a next step, not a summary

Every context file and every agent interaction should point forward. "Here's what we could do next" beats "Here's what we just discussed." This is built into the writing rules and the working-style instructions. Summaries are for reports. Conversations should move.

---

## Quick Start

### 1. Clone the template

```bash
git clone https://github.com/asteedtips/ai-context-template.git
```

Or download the ZIP and drop it into your AI agent's working directory.

### 2. Fill in the first three files

Every file uses `<!-- CUSTOMIZE -->` HTML comment blocks to mark sections you need to fill in. Start with `CLAUDE.md`, `about-me.md`, and `memory/glossary.md`.

### 3. Set up credentials (when you need API access)

Follow the architecture in `security-practices.md`. Copy `api-template.md` for each service. Store secrets in a vault, never in plain text.

### 4. Point your agent at CLAUDE.md

**Claude Desktop / Cowork:** Place `CLAUDE.md` at the root of your selected folder or in `.claude/CLAUDE.md`.

**Other LLMs with file access:** Reference the file path in your system prompt or session initialization.

---

## File Structure

```
ai-context-template/
├── CLAUDE.md                          ← Master instructions (read every session)
├── TASKS.md                           ← Active task tracking
├── CHANGELOG.md                       ← Track context file changes
├── PRIVATE-FILES.md                   ← Guide for splitting public/private
├── LICENSE                            ← MIT
├── README.md                          ← This file
│
├── Claude Context/
│   ├── about-me.md                    ← Your bio and background
│   ├── banned-writing-styles.md       ← AI writing pattern bans (ready to use)
│   ├── working-style.md              ← How the agent should operate (ready to use)
│   ├── best-practices-creation.md     ← Doc output formats, diagrams, quality checklist
│   ├── security-practices.md          ← Credential management architecture
│   ├── api-template.md               ← Copy this for each API integration
│   ├── sales-framework.md            ← Qualification + pipeline management
│   ├── proposal-generation.md         ← Customer-centric proposal workflow
│   ├── email-processing.md           ← Inbox triage and routing process
│   ├── seo-style.md                  ← SEO content workflow (ready to use)
│   └── coding-best-practices.md       ← .NET/C# coding standards
│
└── memory/
    └── glossary.md                    ← People, acronyms, lessons learned
```

### Readiness Levels

| Ready to use (zero changes needed) | `banned-writing-styles.md`, `working-style.md`, `seo-style.md` |
|---|---|
| **Light customization** | `CLAUDE.md`, `best-practices-creation.md`, `CHANGELOG.md`, `TASKS.md` |
| **Build your own content** | `about-me.md`, `glossary.md`, `security-practices.md`, `sales-framework.md`, `proposal-generation.md`, `email-processing.md`, `coding-best-practices.md` |
| **Copy per API integration** | `api-template.md` → duplicate and rename for each service |

---

## Extending the System

**New API integration:** Copy `api-template.md` → fill in auth, endpoints, and behavior rules → add to `CLAUDE.md` dependency chains → store secrets per `security-practices.md`.

**New workflow:** Create a `.md` in `Claude Context/` → add to the context file table in `CLAUDE.md` → add a dependency chain if it needs multiple files → log in `CHANGELOG.md`.

**New writing rules:** Propose additions or removals before editing `banned-writing-styles.md`. Include the reasoning. Review quarterly — AI tells evolve as models change.

---

## Credits

Built by [Albert Steed](https://www.linkedin.com/in/albertsteed/) at [True IP Solutions](https://trueipsolutions.com). Developed through daily production use with Claude (Anthropic) across sales, proposals, email management, code review, and documentation.

The system started as a handful of notes and grew into 17 interconnected context files that run a real business. This template is the distilled, shareable version.

## License

MIT — use it, fork it, modify it, share it. If it helps you get more out of AI, that's the point.
