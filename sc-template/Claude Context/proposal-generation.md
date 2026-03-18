# Proposal Generation Framework
**[YOUR NAME] | [YOUR TITLE] | [YOUR COMPANY]**
*Last Updated: [DATE]*

<!--
  TEMPLATE: This file provides the structure for a customer-centric proposal process.
  Customize the sections, intake questions, and QC checklist to match your business.

  Key principle: proposals are NOT a discovery tool. Your qualification framework
  (see sales-framework.md) must be satisfied before any proposal is drafted.
-->

> **Before drafting any proposal, read `Claude Context/best-practices-creation.md`** — it governs output formats (`.docx` default), Mermaid diagram standards, file naming conventions, writing rules, and the document quality checklist.

---

## Why This Document Exists

Proposals compete for attention. A decision maker gives you 60 seconds of scanning before deciding whether to read further. Every proposal must be customer-centric (their words, their problems, their outcomes) and tight enough to hold attention.

<!--
  CUSTOMIZE: Add your own win-rate data if you track it.
  Example: "Customer-centric proposals achieved X% win rate vs. Y% with generic format."
-->

---

## Output Format

Every proposal is a Word document (`.docx`) by default.

<!--
  CUSTOMIZE: Define your file naming and save location.
  Example:
  - File name: `[Company] - [Client Name] - Proposal - [YYYY-MM] - v[N].docx`
  - Save to: `Customers/[ClientName]/Proposals/`
-->

---

## Step 1 — Intake Questions

Ask these questions before doing anything else. They scope the proposal and ensure you have what you need.

<!--
  CUSTOMIZE: Define your intake questions. Typical ones:

  1. Who is the client? (Search CRM to pull context automatically)
  2. What type of client? (Determines which sections are mandatory)
  3. Which products/services are in scope?
  4. Who are the competitors in this evaluation?
  5. What's the decision timeline?
-->

---

## Step 2 — Data Collection

<!--
  CUSTOMIZE: Define where proposal data comes from.

  - CRM: Pull deal, account, contact, and activity records
  - Pricing: Define where live pricing lives (CRM, spreadsheet, API)
  - Research: Any external data sources (industry databases, etc.)

  Key rule: ALWAYS pull pricing live. Never rely on hardcoded or cached values.
-->

---

## Step 3 — Qualification Gate Check

Before writing a single word, verify that your qualification framework (see `sales-framework.md`) is fully satisfied. If any pillars are missing, flag them and ask. Do not generate the proposal with unconfirmed pillars.

Gate fails → do not generate → flag what's missing → recommend the next discovery action.

---

## Step 4 — Proposal Structure

<!--
  CUSTOMIZE: Define your section structure. The template below is a starting point.
  Adjust the number of sections, page targets, and content requirements to your business.

  Principle: Lead with THEM, close with US. They should see themselves in every section.
-->

### Recommended Sections

1. **Cover Page** (1 page) — Hero image of THEIR organization, personalized title, your branding
2. **Cover Letter** (1 page) — Open with their situation, not your company history
3. **Executive Summary** (1 page) — Problem, proposed solution, investment, expected outcome
4. **Understanding of Their Needs** (2 pages) — Mirror their language back; competitive comparison if applicable
5. **Recommended Solution** (2-3 pages) — Every component tied to a specific pain point
6. **Implementation Plan** (1 page) — Visual timeline, 4-6 milestones
7. **Investment Summary** (1-2 pages) — Multiple pricing options; savings framing
8. **Why [Your Company]** (1 page) — Proof points tied to what they care about
9. **Personal Note** (1 page) — Post-sale commitment, named contact pledge
10. **Customer References** (1 page) — Real quotes from vertical-matched customers
11. **Terms & Next Steps** (1 page) — Clear CTA, two-path close

### Section Guidelines

**Cover Letter rules:**
- Never open with "[Company] was founded in..."
- Reference the lead source if known
- One specific callback to something they actually said
- Under 250 words

**Executive Summary rules:**
- A decision maker should be able to read ONLY this page and brief a board
- Must answer: What problem? What are we proposing? What does it cost?

**Understanding of Needs rules:**
- Pull directly from CRM notes and qualification data
- Use their exact words, not paraphrases
- Include a competitive displacement table when the current vendor is known

**Investment Summary rules:**
- Show multiple term/pricing options side by side
- Make the recommended option visually distinct
- Show full-term totals AND vs. current vendor savings
- Never show monthly delta alone

**References rules:**
- Always include real customer quotes, vertical-matched
- Include direct contact info for call references
- Never fabricate quotes

---

## Step 5 — QC Checklist

Run this before finalizing any proposal. Do not deliver without completing it.

```
PROPOSAL QC CHECKLIST
---------------------
[ ] Client name correct on EVERY page — no wrong-client placeholders
[ ] Cover letter uses their exact words from CRM or discovery notes
[ ] Pain points match what was actually said — not generic assumptions
[ ] Hero image is THEIRS — not stock photos
[ ] Executive Summary includes solution at a glance + investment snapshot
[ ] Personal Note is present, not generic
[ ] Pricing math correct — manual double-check all totals
[ ] Savings framed as full-term total AND vs. current vendor
[ ] Multiple pricing options shown; recommended option marked
[ ] At least one verbatim testimonial quote from a real customer
[ ] No placeholder text remains ([TBD], [Quantity], XXXX)
[ ] Proposal is within target page count
[ ] Current vendor named specifically (if known)
[ ] File saved with correct naming convention in correct folder
```

<!--
  CUSTOMIZE: Add your own checklist items.
  Examples:
  [ ] Compliance sections present if required for client type
  [ ] Industry-specific sections included (E-Rate, HIPAA, SOC2, etc.)
  [ ] Competitive displacement table included when current vendor is known
  [ ] Your e-signature platform referenced in CTA — not a competitor's
-->

---

## Step 6 — Post-Proposal Actions

1. **Log in CRM:** Update deal stage, record date sent and expected response date
2. **Generate send email:** A proposal sent without a cover email is incomplete
3. **Set follow-up task:** 3 business days after sending
4. **Follow-up cadence:** Day 3 (check-in), Day 7 (add value), Day 14 (last outreach before stage review)

---

*Last updated: [DATE]*


---

## Corrections Log

*Tracks issues found when following this file's instructions. Entries are added when a discrepancy is discovered and a fix is applied or proposed.*

| Date | What Failed | Root Cause | Fix Applied | ERRORS.md Ref |
|------|-------------|------------|-------------|---------------|

**Notes:**
<!-- Per-entry context that doesn't fit in the table. Format: "YYYY-MM-DD: [explanation]" -->
