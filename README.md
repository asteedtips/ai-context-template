# AI Context System — Template

A context file system that makes AI agents compound value across sessions instead of starting from zero every time.

Built on the **C-I-M philosophy** (Context-Interaction-Memory): persistent context files teach the AI your preferences, tools, workflows, and language so each session builds on the last.

---

## What This Is

A set of `.md` files that sit alongside your AI agent (Claude, GPT, or any LLM with file access). They act as persistent memory and operating instructions. Instead of re-explaining your preferences, tools, and workflows every session, the agent reads these files and operates accordingly.

**What you get:**
- Writing rules that eliminate AI-sounding output
- Documentation standards with Mermaid diagram support
- A sales qualification and pipeline management framework
- Proposal generation workflow with a QC checklist
- Credential management architecture (secrets never in plain text)
- Email processing and triage workflow
- SEO content workflow
- Coding standards for .NET/C# projects
- Task tracking and a glossary for your internal language

---

## Quick Start

### 1. Copy the template

```bash
git clone https://github.com/[your-username]/ai-context-template.git
```

Or download the ZIP and extract it into your AI agent's working directory (e.g., `ClaudeCowork/`).

### 2. Fill in your details

Every file uses `<!-- CUSTOMIZE -->` comment blocks to mark sections you need to fill in. Start with these three:

1. **`CLAUDE.md`** — Your name, company, workflow chains, and credential setup
2. **`Claude Context/about-me.md`** — Your professional and personal context
3. **`memory/glossary.md`** — Your team members, acronyms, and internal language

### 3. Set up credentials (optional but recommended)

If you use APIs (CRM, email, file storage), follow the architecture in `Claude Context/security-practices.md` and create API-specific files using `Claude Context/api-template.md` as a starting point.

### 4. Point your AI agent at CLAUDE.md

In Claude Desktop / Cowork: place `CLAUDE.md` at the root of your working folder or in `.claude/CLAUDE.md`.

In other tools: reference the file path in your system prompt or session initialization.

---

## File Structure

```
ai-context-template/
├── CLAUDE.md                          ← Master instructions (read every session)
├── TASKS.md                           ← Active task tracking
├── CHANGELOG.md                       ← Track context file changes
├── PRIVATE-FILES.md                   ← Guide for splitting public/private
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

### File Status

| Status | Files |
|--------|-------|
| **Ready to use** (no customization needed) | `banned-writing-styles.md`, `working-style.md`, `seo-style.md` |
| **Light customization** (fill in a few sections) | `CLAUDE.md`, `best-practices-creation.md`, `CHANGELOG.md`, `TASKS.md` |
| **Full customization** (build your own content) | `about-me.md`, `glossary.md`, `security-practices.md`, `sales-framework.md`, `proposal-generation.md`, `email-processing.md`, `coding-best-practices.md` |
| **Copy per integration** | `api-template.md` → one copy per API service |

---

## The C-I-M Philosophy

**Context** compounds. Prompts depreciate.

A well-maintained context file system means your AI agent gets smarter every session. A bare prompt starts from zero every time.

- **Context**: Persistent files that teach the agent your world (these files)
- **Interaction**: The agent asks before acting, integrates what you share, and builds on what worked
- **Memory**: Glossary, task tracking, lessons learned, and changelog keep knowledge across sessions

### Core Agent Behaviors (defined in working-style.md)

1. **Ask before acting** — Clarify with selectable questions, not text dumps
2. **Build on what worked** — Reuse confirmed formats and approaches
3. **Integrate provided information** — Everything shared becomes foundational
4. **Research before responding** — Web search for current info, live API data for business context
5. **Maintain statefulness** — Reference prior agreements and decisions naturally
6. **Use tools judiciously** — Only when they add value over what's already in context

---

## Public vs. Private Split

This template is designed to be shareable. Your private data lives in a separate repo (or folder) that the agent also reads.

**Public repo** (this template): frameworks, standards, writing rules, process templates
**Private repo** (your own): filled-in API configs, credential scripts, people/glossary, proprietary sales methodology, company-specific data

See `PRIVATE-FILES.md` for a detailed guide on what stays private and what has a public counterpart.

---

## Extending the System

### Adding a new API integration
1. Copy `Claude Context/api-template.md` to `Claude Context/[service]-api.md`
2. Fill in the auth, endpoints, and behavior rules
3. Add the file to the workflow dependency chains in `CLAUDE.md`
4. Store credentials in your secret store per `security-practices.md`

### Adding a new workflow
1. Create a new `.md` file in `Claude Context/`
2. Add it to the context file table in `CLAUDE.md`
3. Add a workflow dependency chain if it requires multiple files
4. Log the addition in `CHANGELOG.md`

### Updating writing rules
1. Propose changes (additions or removals) before modifying `banned-writing-styles.md`
2. Include the source or reasoning for new bans
3. Review quarterly — some AI tells fade as models evolve

---

## Credits

Built by Albert Steed ([@AlbertSteed3](https://x.com/AlbertSteed3)) at [True IP Solutions](https://trueipsolutions.com).

Developed through daily use with Claude (Anthropic) across sales, proposals, email management, code review, and documentation workflows.

---

## License

MIT — use it, modify it, share it. If it helps you work better with AI, that's the point.
