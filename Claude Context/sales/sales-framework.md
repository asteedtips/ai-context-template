# Sales Framework — Qualification & Pipeline Management

<!--
  TEMPLATE: This file provides the structure for a sales qualification framework
  and pipeline management process. Fill in your own framework (MEDDIC, BANT,
  SPICE, or your own) and customize the pipeline rules to match your CRM and
  sales motion.
-->

**[YOUR NAME] | [YOUR TITLE] | [YOUR COMPANY]**

> **Before preparing any sales documentation, read `Claude Context/writing/best-practices-creation.md`** — it governs output formats, diagram standards, naming conventions, and writing rules for all deliverables.

---

## Your Qualification Framework

<!--
  SETUP REQUIRED: Define your sales qualification framework.

  A qualification framework answers: "Is this deal real, and should we spend time on it?"

  Common frameworks:
  - MEDDIC: Metrics, Economic Buyer, Decision Criteria, Decision Process, Identify Pain, Champion
  - BANT: Budget, Authority, Need, Timeline
  - SPICE: Situation, Problem, Impact, Critical Event, Expected Outcome
  - Custom: Build your own based on what predicts wins in your business

  For each pillar, define:
  1. What it means
  2. The core question it answers
  3. Discovery questions to surface it
  4. What "confirmed" looks like
  5. What to do if it's missing

  Example structure (replace with your own):

  | Pillar | Core Question |
  |--------|---------------|
  | [Pillar 1] | [What does this answer?] |
  | [Pillar 2] | [What does this answer?] |
  | [Pillar 3] | [What does this answer?] |
  | [Pillar 4] | [What does this answer?] |
  | [Pillar 5] | [What does this answer?] |
-->

---

## Pre-Sales Workflow

- Run **account-research** BEFORE any outreach or call — no cold conversations
- Document a qualification hypothesis before booking a meeting
- Confirm qualification signals after discovery; stop if none surfaced

### Minimum Research Before First Contact

```
1. Company overview: what they do, size, vertical, org structure
2. Recent news: leadership changes, funding, budget cycles, incidents
3. Hiring signals: open roles that indicate active evaluation
4. Key contacts: decision-maker + technical evaluator + champion
5. Current tech stack: what they're running now in your category
```

---

## Pipeline Review Best Practices

Run a pipeline review every week — ideally Monday morning. The goal is to catch problems before they become losses.

### The Five Hygiene Non-Negotiables

Every deal in the pipeline must have all five of these, or it's not a real deal:

1. **Amount populated** — If there's no dollar figure, there's no business case. A deal with no amount is a conversation, not an opportunity.
2. **Close date in the future** — Past close dates are the single biggest sign of a stalled pipeline. Every past close date must be either pushed to a real future date or marked closed-lost.
3. **Stage matches reality** — A deal closing in 10 days cannot be in early qualification. Either the stage is wrong or the date is wrong.
4. **Last activity within 14 days** — If nobody has touched a deal in two weeks, it's at risk. Flag it.
5. **Next step defined** — Every deal needs a concrete next action, owner, and date. "Will follow up" is not a next step.

### Pipeline Health Score

```
HEALTH SCORE = 100
  − (% with no amount) × 25
  − (% past close date) × 30
  − (% stale 14+ days) × 25
  − (% with no next step) × 20
```

| Score | Meaning | Action |
|-------|---------|--------|
| 80–100 | Healthy | Maintain cadence |
| 60–79 | Needs attention | Fix hygiene in 48 hours |
| 40–59 | At risk | Emergency review with each rep |
| Below 40 | Broken | Rebuild from scratch; run qualification on every deal |

### Deal Removal Rule

Remove a deal from the active pipeline if:
- No activity in 60+ days AND no response to re-engagement attempt
- Close date has been pushed 3+ times with no commitment
- No qualification pillar confirmed after 2 discovery attempts
- Prospect has gone dark at both champion and economic buyer level

A clean pipeline of 15 real deals is worth more than 40 deals with 20 zombies.

### Red Flags to Watch in Every Review

- Close date passed + still open → push or close-lost
- No amount + late stage → no business case; block it
- 30+ days in same stage → stuck; needs diagnosis
- Silent 14+ days → re-engage or deprioritize

<!--
  CUSTOMIZE: Add your own stage gates.

  Example:
  | Stage | Required Before Advancing |
  |-------|--------------------------|
  | Qualification → Proposal | [Your pillars] confirmed; amount estimated |
  | Proposal → Negotiation | All pillars confirmed; proposal delivered |
  | Negotiation → Closed Won | Verbal commitment; contract path confirmed |
-->

---

## Self-Improvement Loop

- After every discovery call: log what qualification pillars were confirmed vs. missing
- After a lost deal: document the root cause
- Write lessons that prevent the same miss from repeating
- Review lessons at the start of each sales week

---

## Core Principles

- **No Unqualified Proposals**: Proposals aren't a discovery tool. Qualify first, propose second.
- **Quantify the Pain**: If you can't put a number on the problem, you don't have a deal — you have a conversation.
- **Their Words, Not Yours**: Use the exact language the prospect used to describe their problem and outcome.
- **Relationships Over Transactions**: Win on trust and reliability.
- **Always Leave a Next Step**: Every interaction ends with a confirmed next action, owner, and date.

---

## Skill Reference Map

| Sales Motion | Skill to Use |
|-------------|-------------|
| Research a new prospect | `account-research` |
| Prep for a discovery or demo call | `call-prep` |
| Draft cold outreach or re-engagement | `draft-outreach` |
| Build a leave-behind or exec summary | `create-an-asset` |
| Research a competitor before a deal | `competitive-intelligence` |
| Summarize a call + next steps | `call-summary` |
| Review pipeline health weekly | `pipeline-review` |
| Forecast a deal or period | `forecast` |
| Start the day with priorities | `daily-briefing` |

---

*Last updated: [DATE]*
