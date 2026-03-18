# Email Inbox Processing — Standard Operating Procedure

> **Purpose**: This file defines how the AI agent reviews, categorizes, and organizes your inbox. Follow this procedure whenever an inbox review is requested.

---

## Process Overview

1. **Load credentials** — Authenticate to your email API
2. **Pull ALL inbox messages** — Paginate until no more results. Never assume a single page is the full inbox.
3. **Pull full bodies** — For any message where the preview is insufficient for categorization, fetch the full body
4. **List mail folders** — Get the current folder structure so routing is accurate
5. **Categorize** — Sort each message into one of three buckets (see below)
6. **Present plan** — Show the categorized list and proposed routing before executing any moves
7. **Execute** — Only after confirmation: move informational emails, apply flags and categories to action items

---

## Categorization Buckets

### 1. Needs Response
You personally need to reply or take direct action. Apply:
- Category/label: **"Needs Response"**
- Flag: **flagged**
- Due date: Set if a deadline exists or can be inferred

### 2. Needs Follow-Up
You are monitoring but the ball is in someone else's court, or the team needs to handle it. Apply:
- Category/label: **"Follow Up"**
- Flag: Only flag if there's a hard deadline
- Due date: Set if deadline exists

### 3. Informational
Read-only, FYI, newsletters, completed notifications, receipts. These get **moved** out of inbox to the appropriate folder. No flag or category needed.

---

## Routing Rules for Informational Emails

<!--
  CUSTOMIZE: Define your routing rules. These determine where informational
  emails get moved. Rules are evaluated top-down, first match wins.

  Example:
  | Priority | Rule | Destination Folder |
  |----------|------|--------------------|
  | 1 | From: [specific person] | `People > [Name]` |
  | 2 | Subject mentions "[project name]" | `Projects > [Project]` |
  | 3 | From: [domain].com | `[Category]` |
  | 4 | Subject mentions conference/event | `Marketing > Events` |
  | 5 | **Default** — anything not matched above | `Archive` or `Support` |
-->

### Rules for Adding New Routing Rules
- New rules may be added during a session. When they are, update this file immediately.
- Rules are evaluated top-down, first match wins.
- Always confirm new rules before adding to this file.

---

## Folder Structure Reference

<!--
  CUSTOMIZE: Document your email folder structure here.
  This helps the AI agent route emails correctly.

  Example:
  ```
  Inbox/
  ├── Clients/
  │   ├── [Client A]
  │   └── [Client B]
  ├── People/
  │   ├── [Person A]
  │   └── [Person B]
  ├── Projects/
  │   ├── [Project A]
  │   └── [Project B]
  └── [Company]/
      ├── Billing
      ├── Legal
      ├── Marketing
      └── Sales
  ```
-->

---

## Important Notes

- **Never send emails** without explicit permission (see your email API context file for the full rule).
- **Always paginate.** Your inbox likely has 50+ messages at any time.
- **Confirm before moving.** Present the full routing plan and get sign-off before executing moves.
- **Flagged messages stay.** Any message that already has a flag should not be moved unless explicitly requested.
- **Unread messages stay.** Only move messages that have been read.

---

*Last updated: [DATE]*


---

## Corrections Log

*Tracks issues found when following this file's instructions. Entries are added when a discrepancy is discovered and a fix is applied or proposed.*

| Date | What Failed | Root Cause | Fix Applied | ERRORS.md Ref |
|------|-------------|------------|-------------|---------------|

**Notes:**
<!-- Per-entry context that doesn't fit in the table. Format: "YYYY-MM-DD: [explanation]" -->
