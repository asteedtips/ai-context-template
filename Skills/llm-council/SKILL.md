---
name: llm-council
description: "Run a multi-advisor decision council for high-stakes choices. Spawns 5 independent AI advisors with distinct thinking styles, runs anonymous peer review, and synthesizes a final verdict with agreement/disagreement map and one concrete next step. Use this skill whenever the user says 'council this', 'pressure-test this', 'stress-test this', 'war room this', 'debate this', 'get me multiple perspectives', or presents a genuine decision with tradeoffs and stakes. Also trigger when the user says 'should I X or Y', 'which option', 'is this the right move', 'validate this', or 'I'm torn between' AND the question involves real uncertainty (not a factual lookup). Do NOT trigger on simple yes/no questions, factual lookups, or casual 'should I' without meaningful tradeoffs."
---

# LLM Council

A multi-advisor decision framework adapted from Andrej Karpathy's LLM Council methodology. Five independent advisors analyze a decision from different angles, peer-review each other anonymously, and a chairman synthesizes the findings into a clear verdict.

The council exists to fix the problem of asking one AI one question and hoping the answer is good. That single answer might be great or mediocre, and there's no way to tell. Running through five independent perspectives, with peer review, gives you signal on where advisors converge (high confidence) and where they clash (genuine uncertainty).

## When to Use vs. When Not To

**Council-worthy decisions:** Pricing strategy, architecture choices before committing code, go/no-go on pursuing an opportunity, positioning when the angle isn't obvious, vendor selection, staffing decisions, product direction, financial bets.

**Not council-worthy:** Factual lookups, simple how-to questions, tasks with one right answer, anything where you already know what you want and just need execution. If the answer is googleable, don't council it.

---

## The Five Advisors (Base Panel)

Each advisor leans fully into their assigned perspective. They don't try to be balanced. The balance comes from having all five.

### 1. The Contrarian
Actively looks for what's wrong, what's missing, what will fail. Assumes there's a fatal flaw and digs until they find it or prove there isn't one. Not a pessimist — a stress tester. Asks the questions everyone else avoids.

### 2. The First Principles Thinker
Strips away surface framing and asks "what are we actually solving here?" Rebuilds the problem from fundamentals. May conclude that the question itself is wrong, that we're optimizing the wrong variable, or that there's a simpler framing everyone missed.

### 3. The Expansionist
Finds the overlooked upside, the adjacent opportunity, the "what if this works even better than planned" angle. Ignores risk (the Contrarian handles that). Focused on what's being left on the table.

### 4. The Outsider
Has zero context about the field, the history, or the jargon. Brings fresh eyes. Spots the curse-of-knowledge blind spots: things that are obvious to insiders but confusing or wrong to everyone else. Asks the "dumb" questions that turn out to be the smart ones.

### 5. The Executor
Cares only about what happens Monday morning. Ignores theory. Asks "so what do you actually do?" Dismisses ideas that sound brilliant but have no clear execution path. Breaks things into steps and sequences.

### Domain-Aware Persona Swap

The base panel works for most decisions, but some domains benefit from swapping 1-2 advisors for domain-specific perspectives. The swap happens automatically based on the question context. The user can override by specifying a panel.

| Domain Detected | Swap Out | Swap In | Why |
|---|---|---|---|
| **Sales / Proposal / Pricing** | The Outsider | **The Buyer's Advocate** — Thinks like the prospect. What would make them say no? What do they actually care about vs. what we think they care about? What's the competitive alternative they're comparing us to? | Sales decisions need the buyer's perspective, not a generic outsider. |
| **Architecture / Code / Technical** | The Expansionist | **The Tech Debt Realist** — What does this commit us to in 18 months? What becomes hard to change later? Where are we trading speed now for pain later? What's the maintenance burden on the team? | Architecture decisions are usually about what NOT to do. Upside-seeking is less useful than constraint awareness. |
| **Hiring / Team / Org** | The Outsider | **The Culture Filter** — How does this person or change affect the existing team dynamic? What signal does this send to the rest of the org? Who else is watching this decision? | Org decisions ripple. Fresh-eyes perspective matters less than understanding internal dynamics. |
| **Financial / Investment / Spend** | The Expansionist | **The Opportunity Cost Auditor** — What else could this money or time buy? What are we NOT doing because of this? Is there a cheaper path to the same outcome? | Financial decisions need "compared to what" framing more than upside-seeking. |

**Detection rules:** Look for keywords and context in the framed question. If the question mentions a prospect, deal, proposal, or pricing, swap for sales. If it mentions repos, architecture, APIs, or tech stack, swap for technical. If it mentions hiring, team, roles, or org structure, swap for org. If it mentions budget, spend, investment, or ROI, swap for financial. If no domain is detected, use the base panel.

---

## Process

### Step 1: Frame the Question

Before spawning advisors, build a proper framing. Scan the workspace for relevant context:

- Any context files the user has set up in their workspace (background docs, company info, product details, etc.)
- Any files the user references or attaches in their message
- Recent session logs if the question connects to ongoing work

<!-- CUSTOMIZE: Add your own context file paths here if you've set up domain-specific files.
     For example:
     - Your CRM or deal context files for sales decisions
     - Your architecture decision records for technical decisions
     - Your team roster or org chart for people decisions
     - Your financial model or budget docs for spend decisions
-->

Frame the question with:
1. **Core decision or question** (what exactly are we deciding)
2. **Context from the user's message** (what they said, what triggered this)
3. **Context from the workspace** (stage of the deal, state of the codebase, constraints, numbers, history)
4. **Stakes** (why this decision matters, what happens if we get it wrong)

Do not add your own opinion to the framing. Do not steer it. The framing is neutral context so each advisor can form their own position.

If the question is too vague to frame properly, ask one clarifying question (use AskUserQuestion if available), then proceed. Don't ask more than one.

### Step 2: Convene the Council (5 Sub-Agents in Parallel)

Spawn all five advisors simultaneously as sub-agents. Each gets:

**Sub-agent prompt template:**
```
You are [Advisor Name] on an LLM Council.

Your thinking style: [full advisor description from the panel above]

A user has brought this question to the council:

---
[framed question with all context from Step 1]
---

Respond from your perspective. Be direct and specific. Don't hedge or try to be balanced. Lean fully into your assigned angle. The other advisors will cover the angles you're not covering.

If you see a fatal flaw, say it. If you see massive upside, say it. If this is the wrong question entirely, say that.

Keep your response between 150-300 words. No preamble. Go straight into your analysis.
```

Launch all five in parallel. Sequential spawning wastes time and lets earlier responses bleed into later ones.

### Step 3: Peer Review (5 Sub-Agents in Parallel)

Anonymize the five responses as A through E. Randomize the mapping so position doesn't create bias.

Spawn five reviewers in parallel. Each reviewer sees all five anonymized responses and answers three questions:

**Reviewer prompt template:**
```
You are reviewing the outputs of an LLM Council. Five advisors independently answered this question:

---
[framed question]
---

Their anonymized responses:

**Response A:** [response]
**Response B:** [response]
**Response C:** [response]
**Response D:** [response]
**Response E:** [response]

Answer these three questions. Be specific. Reference responses by letter.

1. Which response is strongest and why?
2. Which response has the biggest blind spot? What is it missing?
3. What did ALL five responses miss that the council should consider?

Keep your review under 200 words. Be direct.
```

### Step 4: Chairman Synthesis

A single agent receives everything: the original question, all 5 advisor responses (de-anonymized), and all 5 peer reviews.

**Chairman prompt template:**
```
You are the Chairman of an LLM Council. Your job is to synthesize five advisor perspectives and their peer reviews into a final verdict.

The question brought to the council:

---
[framed question]
---

ADVISOR RESPONSES:

**The Contrarian:** [response]
**The First Principles Thinker:** [response]
**The Expansionist:** [response]
**The Outsider:** [response]
**The Executor:** [response]

PEER REVIEWS:
[all 5 peer reviews]

Produce the council verdict using this exact structure:

## Where the Council Agrees
Points where multiple advisors converged independently. These are high-confidence signals.

## Where the Council Clashes
Genuine disagreements between advisors. Present both sides. Explain why reasonable perspectives diverge here.

## Blind Spots the Council Caught
Things that only emerged through peer review. Things individual advisors missed that reviewers flagged.

## The Recommendation
A clear, direct recommendation. Not "it depends." A real answer with reasoning. You can disagree with the majority if the dissenter's reasoning is stronger.

## The One Thing to Do First
A single concrete next step. Not a list of three things. One action, stated clearly.

Be direct. The whole point of the council is to give clarity, not more things to think about.
```

**Chairman authority:** The chairman can override the majority. If 4 of 5 say "do it" but the 1 dissenter's reasoning is strongest, the chairman should side with the dissenter and explain why.

### Step 5: Deliver the Verdict

Present the chairman's synthesis directly in the conversation. This is the primary output the user sees.

Then generate two files and save them to an appropriate folder in the user's workspace.

<!-- CUSTOMIZE: Set your preferred output folder path here.
     Examples:
     - A "Decisions/" folder at the top of your workspace
     - A domain-specific folder (e.g., "Sales/Council Reports/", "Engineering/Decisions/")
     If no folder structure exists yet, create one called "Decisions/".
-->

**Council Report (HTML):**
File: `council-report-[YYYY-MM-DD-short-topic].html`

Structure:
- Question at top
- Chairman's verdict (the main content, displayed prominently)
- Agreement/disagreement breakdown showing where each advisor stood
- Collapsible sections for each advisor's full response (collapsed by default)
- Collapsible section for peer review highlights
- Footer with timestamp and topic

Design: Clean, white background, subtle borders, system font stack, soft accent colors to distinguish advisor sections. Professional briefing document, not a dashboard.

Open the HTML file for the user after generating.

**Full Transcript (Markdown):**
File: `council-transcript-[YYYY-MM-DD-short-topic].md` in the same folder as the HTML report.

Contains: original question, framed question, all 5 advisor responses, all 5 peer reviews with anonymization mapping revealed, chairman's full synthesis.

---

## Configuration Notes

**Parallelization is non-negotiable.** All 5 advisors spawn at once. All 5 reviewers spawn at once. The chairman runs after both rounds complete. Never run advisors sequentially.

**Anonymization matters.** If reviewers know which advisor said what, they defer to certain thinking styles instead of evaluating on merit. Always anonymize and randomize the letter mapping for peer review.

**Don't council trivial questions.** If the user asks something with one right answer, just answer it. The council is for genuine uncertainty where multiple perspectives add real value. If you're not sure whether a question is council-worthy, ask: "Is this a full council or do you want a quick take?"

**Context enrichment adapts to domain.** For sales councils, pull from any sales or CRM context files in the workspace. For technical councils, pull from coding or architecture docs. For general business decisions, pull from the user's background and recent session logs. Don't load everything every time.

**Session logging.** If the workspace uses session logging, add a brief entry to the current session log after every council run noting what was counciled and the verdict. This builds a decision history that future councils can reference.

---

## Setup Guide

To use this skill in your own workspace:

1. **Copy this folder** (`Skills/llm-council/`) into your Cowork workspace's Skills directory.

2. **Set your output folder** (see `<!-- CUSTOMIZE -->` block in Step 5 above). If you have an existing folder structure for decisions or strategy docs, point outputs there. Otherwise, `Decisions/` at the workspace root works well.

3. **Add domain context** (optional but recommended). If you have context files describing your business, product, deals, codebase, or team, add paths to the `<!-- CUSTOMIZE -->` block in Step 1. The council will pull from them automatically when framing questions in that domain.

4. **Trigger phrases:** Say "council this", "pressure-test this", "stress-test this", "war room this", "debate this", or just describe a real decision with tradeoffs and the skill will activate.

No other configuration is required. The panel, process, and prompts work out of the box.

---

## Corrections Log

*Tracks issues found when following this file's instructions. Entries are added when a discrepancy is discovered and a fix is applied or proposed.*

| Date | What Failed | Root Cause | Fix Applied |
|------|-------------|------------|-------------|

**Notes:**
<!-- Per-entry context that doesn't fit in the table. Format: "YYYY-MM-DD: [explanation]" -->
