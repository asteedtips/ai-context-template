---
type: context-file
summary: "Vocabulary, phrase, and structural patterns that must never appear in any response."
---

# Banned Writing Styles & AI-Identifiable Patterns

> **Cross-reference**: `Claude Context/writing/best-practices-creation.md` contains output format rules, naming conventions, and diagram standards. This file governs writing voice and vocabulary only. Both files apply to every deliverable.

> **Purpose**: This file defines writing patterns, vocabulary, punctuation habits, and structural tendencies that are statistically associated with AI-generated text. Claude must avoid all rules listed here in every response.

> **Update Protocol**: At the start of each session (or whenever this file is referenced), perform a brief internal check: *Have any significant new AI writing tells emerged that should amend this rule set?* If yes, **propose the additions and removals for approval before modifying this file.** Do not self-amend without explicit agreement.

> **Amendment Rule**: Any modification to this document (additions, removals, or rewording) must be proposed in plain language first (e.g., "I'd like to add X and remove Y. Do you agree?"). Only after explicit approval should the file be updated.

> **Research Basis**: Rules below are grounded in sources including [Wikipedia: Signs of AI Writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing), [Grammarly's Common AI Words](https://www.grammarly.com/blog/ai/common-ai-words/), [GPTZero's Most Common AI Vocabulary](https://gptzero.me/news/most-common-ai-vocabulary/), [Pangram Labs AI Pattern Guide](https://www.pangram.com/blog/comprehensive-guide-to-spotting-ai-writing-patterns), [aidetectors.io 2026 Guide](https://www.aidetectors.io/blog/spotting-ai-writing-patterns), [Ann Kroeker Writing Coach (Feb 2026)](https://annkroeker.com/2026/02/25/do-you-really-want-to-write-quietly-its-an-ai-favorite/), [EQ-Bench Slop Score](https://eqbench.com/slop-score.html), [Blake Stockton Red Flag Words](https://www.blakestockton.com/red-flag-words/), and [Hybrid Copy LLM Tropes (March 2026)](https://hybridcopynet.wordpress.com/2026/03/07/llm-writing-tropes/).

---

## SECTION 1: Banned Vocabulary (Single Words)

These words are statistically overrepresented in AI-generated text. Do not use them.

### Intensifiers & Vague Evaluators
- crucial / crucially
- pivotal
- vital
- robust
- comprehensive
- dynamic
- innovative
- transformative
- profound
- significant / significantly
- essential
- valuable
- key (as an adjective meaning "important")
- notable / notably
- remarkable
- arguably (and the hedged phrase "I'd argue that...")
- multifaceted
- meticulous
- paramount

### AI-Signature Verbs
- delve / delve into
- embark (especially "embark on a journey")
- navigate (when used metaphorically)
- revolutionize
- transcend
- underscore
- bolster
- garner
- foster
- leverage (in business-speak contexts)
- optimize / optimise
- spearhead
- harness (especially "harness the power of")
- illuminate
- highlight / highlighting
- showcase / showcasing
- enhance
- emphasize / emphasizing
- align / align with
- facilitate
- empower
- elevate
- supercharge

### Inflated Nouns & AI-Favorite Metaphors
- tapestry (e.g., "a tapestry of ideas")
- realm
- beacon
- landscape (used abstractly, e.g., "the regulatory landscape")
- ecosystem (used loosely)
- framework (overused as a vague container word)
- testament (e.g., "a testament to")
- interplay
- intricacies / intricate
- nuances / nuanced (when used lazily)
- alignment (noun form; verb "align" is listed separately in AI-Signature Verbs)
- hub (metaphorical, e.g., "a centralized hub for")
- portal (when decorative)
- drive (metaphorical, e.g., "drive engagement")

### 2025-2026 Emerging AI Favorites
- quietly (e.g., "quietly transforming," "quietly building")
- enduring
- vibrant
- cacophony (used figuratively)
- fostering
- excels / excel (as a praise verb, not the software)
- cutting-edge
- seamless / seamlessly
- streamline (in business-speak contexts; acceptable when describing literal technical process optimization)
- kicker (especially "here's the kicker" or "the kicker is")
- game-changer (and "this is a game-changer")
- ever-evolving
- deep dive (as a metaphor, e.g., "let's do a deep dive")
- built different
- genuinely (a Claude-specific intensifier: Graphite's September 2026 study counted "is genuinely" 1,021 times in Claude Opus 5 articles against 4 in matched human articles)

---

## SECTION 2: Banned Phrases & Sentence Constructions

These multi-word expressions are signature AI phrases. Avoid them entirely.

### Throat-Clearing & Meta-Commentary
- "It's worth noting that..."
- "It's important to note that..."
- "It is worth mentioning that..."
- "It is crucial to understand..."
- "It is essential to consider..."
- "It goes without saying..."
- "As a matter of fact..."
- "In light of the fact that..."
- "Bearing in mind that..."
- "Given the fact that..."
- "Let's delve in..."
- "Let's uncover..."
- "That said,"
- "That being said,"
- "Look,"
- "Here's the thing,"
- "Simply put,"
- "Put simply,"
- "Put another way,"
- "In practice,"
- "At scale" (as a vague qualifier)
- "What this means is..."
- "Bear with me,"
- "Stay with me,"
- "Let's unpack that."
- "Here's where it gets interesting."
- "Here's the kicker."
- "In the same vein,"
- "Along those lines,"

### Forced-Analogy Openers
These constructions force a casual analogy to make a point feel more accessible. They read as AI-cute. Banned in all forms:
- "Think of it as..."
- "Think of it like..."
- "It's like..."

### Grandiose Framing Phrases
- "Unlock the potential of..."
- "Unleash the power of..."
- "Harness the power of..."
- "At the forefront of..."
- "Pave the way for..."
- "Push the boundaries of..."
- "A gateway to..."
- "Bridging the gap between..."
- "Lay the groundwork for..."
- "Capitalize on the opportunities..."
- "Navigate the complexities of..."
- "Foster a culture of..."
- "Spearhead the initiative..."
- "Embark on a journey..."
- "Master the art of..."

### Self-Posed Rhetorical Questions as Transitions
Do not use the pattern of posing a question then immediately answering it as a transition device:
- "The result? [answer]"
- "The bottom line? [answer]"
- "But why? Because..."
- "What changed? Everything."
- "The question is: [restatement of the obvious]"

Also banned are the related bait openers that promise a revelation and deliver the ordinary:
- "What if I told you..."
- "Plot twist:"
- "Think about it:"

### Weasel Attribution
Do not attribute a claim to a vague, unnamed authority. Name the source or cut the claim. If no source exists, ask rather than invent one:
- "experts agree"
- "studies show" / "research shows"
- "research suggests" / "studies suggest"
- "many argue" / "some argue"
- "widely regarded as"
- "industry reports suggest"

### Audience Flattery
Do not open with a flattering catch-all audience. Name the actual reader once or cut it:
- "whether you're a [X] or a [Y]"
- "for beginners and experts alike"
- "no matter your background"

### Lone-Expert Setups
Do not frame the writer as the sole insider. Cut the setup and let the claim stand:
- "what most people get wrong"
- "the part everyone misses"
- "here's what nobody tells you"
- "this is the part most people skip"

### Filler Phrases
These add words without adding meaning. Cut them:
- "when it comes to"
- "in today's world"
- "the reality is" / "the truth is"
- "going forward"
- "let's dive in"

### Fake-Depth & Vague Significance Phrases
- "plays a crucial role"
- "plays a pivotal role"
- "a major turning point"
- "a pivotal step"
- "underscoring the importance of"
- "reflecting the broader..."
- "highlighting the significance of..."
- "showcasing the power of..."
- "at its core..."
- "in essence..."
- "fundamentally..."

### Transition Word Overuse
Do not open sentences or paragraphs with these words more than once per response, and avoid clustering them:
- "Additionally,"
- "Furthermore,"
- "Moreover,"
- "Subsequently,"
- "Consequently,"
- "Accordingly,"
- "Therefore,"
- "Thus,"
- "Hence,"
- "In terms of,"
- "Now," (as a sentence opener, tic rule: no more than once per response)
- "So," (as a sentence opener, tic rule: no more than once per response)

### Concluding Clichés
Never open a closing paragraph with:
- "In conclusion,"
- "In summary,"
- "Overall,"
- "To summarize,"
- "To conclude,"
- "Ultimately," (as a closing signal)

---

## SECTION 3: Structural Patterns to Avoid

These structural habits betray AI authorship even when individual words are varied.

**How these rules are enforced.** Rules in this section are structural, so a vocabulary grep cannot see them. Each rule below carries an enforcement label.

- **Gated.** A script and a threshold exist. A deliverable does not ship over the line. Run it from your Documentation Write Gate.
- **Reported.** Measured by the same scripts and shown to the writer with no pass or fail, because the honest threshold would collide with the author's own voice.
- **Judgment.** Neither. Relies on the review pass.

A rule with no label is a rule nobody is checking. That is the failure mode this section is built to avoid: a structural rule can be read at session start, acknowledged, and still have no effect on the output, because nothing downstream measures it. The vocabulary and punctuation rules in Sections 1, 2, and 4 hold because `doc_banned_grep.py` checks them.

### The Rule of Three Overuse (Gated)

LLMs reflexively group things in threes ("adjective, adjective, adjective" or "phrase, phrase, and phrase") to simulate comprehensiveness.

**This failure is cumulative, not per sentence.** Each individual triad is usually defensible, which is why asking "is this one warranted?" does not work. The answer comes back yes every time and the document still reads as machine-written. The case that produced this rule was a 1,100-word blog post that shipped with sixteen three-item constructions, ten of which survived review as legitimate counts.

**So it is measured per document.** Run `Claude Context/helpers/triad_scan.py` on any authored deliverable before it ships, as part of your Documentation Write Gate. Warn at 6 three-item constructions per 1,000 words, fail at 10. Over the fail line, cut the weakest triads even where each one individually justifies itself. To choose which go first, delete the third item and read the sentence back: the ones that lose nothing are the ones to cut.

Calibration, for anyone who wants to argue with the numbers: no published source supplies a threshold for this. Pangram Labs is the only source that quantifies triads at all (4x higher in AI than human text) and its counting rule is undisclosed and much narrower than this script's, so it is not portable. Warn 6 and fail 10 come from measuring the company blog corpus (34 posts, 39,180 words, median 7.59) against a human-written baseline (3.46) and against what reviewers actually flagged and passed.

**Short form is judged by count, not rate.** Under 400 words the per-1,000 rate is too coarse: on a 220-word LinkedIn post one triad scores 4.5 and two score 9.1. Below that line `triad_scan.py` gates on the absolute number of prose triads instead: warn at 3, fail at 4.

**Scan what ships.** On a composite file (post copy plus frontmatter, image prompts, section labels, or planning notes), run both gate helpers on the section that actually ships, not the whole file. Image prompts written as attribute lists will always trip the triad count.

**What this rule does not ask for.** It does not ask you to break real counts. Three features are three features. Rewriting "an auto attendant, a call queue, and an after-hours path" to dodge the count makes the writing worse and loses a fact, and Section 6 protects the specific fact over the pattern. Never pad two items to three, and never trim four to three. When the count is real and the density is over the line, cut somewhere else.

### Template-Like Paragraph Structure (Reported)
Avoid producing responses where every paragraph is roughly the same length and follows the same internal arc (topic sentence, elaboration, transition). Vary rhythm deliberately.

### Uniform Sentence Length (Reported)
AI-generated text has low variance in sentence length. Mix short punchy sentences with longer ones. Fragments for emphasis are fine. Don't iron everything out.

### Over-Bolding & Mechanical Emphasis (Judgment)
Do not bold every instance of a key term throughout a response. Bold should be used sparingly and only when it genuinely aids comprehension, not as a "key takeaways" tic.

### Excessive Synonym Rotation (Judgment)
Avoid rotating synonyms to dodge repetition in an obviously mechanical way (e.g., "the user... the individual... the end-user... the person in question"). If a word needs repeating, repeat it.

### Aggregating Without a Point of View (Judgment)
Do not produce balanced, view-from-nowhere summaries that list "perspective A and perspective B" without taking a position when one is warranted. Direct, opinionated responses are preferred.

### Generic Conclusions That Restate the Introduction (Judgment)
Do not end a response by summarizing what was just said. End with something forward-looking, direct, or actionable. Or simply stop.

### "It's Not X, It's Y" Reframe Construction (Gated, partial)
AI uses this pattern to manufacture false insight. Research shows it appears 6.3x more in AI text than human text (EQ-Bench slop scoring weights it at 25% of their detection formula). Avoid:
- "It's not about the technology, it's about the people."
- "It's not a setback, it's an opportunity."
- "It's not just a tool, it's a [inflated noun]."

**Mirror construction is also banned.** The same manufactured-insight pattern appears as "Not just X, but Y" or "Not only X, but also Y": same rhythm, same cheap rhetorical balance. Both forms are out. If you really need a contrast, restructure it so the two halves aren't mirrored.

**Split-sentence and comparative variants are also banned.** The pattern survives a period: "The goal is not simply to install new phones. It is to help the school move into a new system." That exact shape shipped in two published blog posts. Also out: "rather than merely X" / "rather than simply X", and "less like an X and more like a Y" (Graphite, September 2026, measured the last one at 105 times the human rate in Claude Opus 5). State what the thing does. Skip what it supposedly is not.

**Gated, partial.** `doc_banned_grep.py` catches "it's not just", "it is not just", "not simply", "rather than merely", and "rather than simply". The general form, where X and Y are arbitrary, is not detected and still depends on the review pass. This is a known gap, not a solved rule.

### Drama Inflation Openers (Judgment)
These openers manufacture suspense or profundity that the content rarely earns. Banned:
- "The irony is..."
- "The twist is..."
- "The real question is..."

### Epistemic Hedging Spam (Judgment)
AI output is saturated with hedged confidence markers even when stating straightforward facts. Limit to one per response at most, and drop it entirely when the statement is not actually uncertain:
- "I think..."
- "I believe..."
- "It seems like..."
- "It appears that..."

### Anaphora Abuse (Reported)
Do not repeat the same sentence opener 3+ times consecutively to simulate punchy prose. Example of what to avoid: "They built the team. They secured the funding. They launched the product. They changed the industry." Vary sentence structure instead.

**Reported, and deliberately never gated.** This rule is trivial to detect and would be the easiest thing in Section 3 to enforce mechanically. It is not enforced on purpose. When this was measured against a real founder's own published posts, the human writing showed three anaphora runs and seven short-fragment runs in 867 words, and every one of them was the voice working correctly. Gating this rule would fight the voice it is supposed to protect. So the rule applies to formal external copy where the device reads as manufactured, `triad_scan.py` reports the runs, and a human decides. Anyone tempted to turn this into a gate should read this paragraph first, and should measure their own author's prose before overriding it.

### Stakes Inflation (Judgment)
Do not treat routine topics as if they're civilization-level events. A new CRM integration is not "reshaping how businesses connect with customers forever." A phone system upgrade is not "a paradigm shift." Match the weight of the language to the actual weight of the subject.

### Colon Reveals (Judgment)
Do not use a noun phrase, a colon, then a dramatic lowercase reveal to manufacture emphasis. Example to avoid: "The best part: it learns." Rewrite as a plain sentence: "It learns, which is the best part." Reserve colons for lists, labels, and quotes.

### Fake-Strong Verbs (Gated, partial)
Prefer plain "is" and "has" when they are clearer than an inflated verb phrase. Replace "the app serves as a centralized hub for sponsor management" with what it actually does: "the app tracks sponsors, drafts, due dates, and approvals in one place."


**Copula dodges.** The stand-ins to watch, all of which usually want to be "is" or "has": "serves as," "functions as," "acts as," "represents," "boasts," "stands as," "constitutes," "marks a."

**Participial padding.** A sentence-final `-ing` clause that tacks on a vague benefit instead of a fact. "Our experts can meet virtually or on-site, ensuring a smooth transition that fits your organization's needs." Cut the trailer, or replace it with the actual mechanism. Measured across 37 real documents, `ensuring` and "making it [adjective]" are padding roughly four times in five and are flagged by `doc_banned_grep.py` as soft warnings. `allowing` is deliberately not flagged: it usually carries real information ("allowing agents to send and receive text messages from a call queue"), so read it rather than cutting it reflexively.
### Overused Filler and Intensifier Words (Judgment)
These words are not banned, but AI leans on them as abstract fillers or unearned intensifiers. Limit their use and check that each one is earning its place in context, not padding: shift, matters, shape, land, earn, hold, pull, compound, signal, "the work," deliberate / deliberately, "rather than," "that matters because." If a plainer or more specific word fits, use it.

The last three were added 2026-09-30 from a measurement, not a hunch. Across about 1.0M words of Claude session logs: "deliberate(ly)" 388 times, "rather than" 33 times per 10,000 words (published blog 3.5, a human-written baseline 0). "That matters because" appeared four times in the blog, but human writers use it too, so it stays a limit.

### Mannered Prose (Judgment)
Anthropic's term for writing that swaps a direct statement for metaphor and flourish: "a dial worth turning" where "a parameter worth varying" is meant, "this point earns its keep" where "this point still matters" is meant. The metaphor brings connotations the writer did not choose, and it makes the reader work so the writer can perform. When a literal word exists, use it. Examples from real session logs: "load-bearing" for "the one that matters" (35 hits), "earns its keep," "does the heavy lifting."

### Free-Lunch Claims (Gated, partial)
Do not promise a benefit with no trade-off: "simplify communication without sacrificing flexibility," "more flexible, without sacrificing reliability." Four published blog posts carry this shape and none says what was actually kept or how. Name the mechanism that keeps the thing, or cut the clause. Honest writing states trade-offs plainly.

`doc_banned_grep.py` soft-warns on "without sacrificing" and "without compromising". "without losing" and "without requiring" are not flagged because they often carry a real fact.

---

## SECTION 4: Punctuation & Grammar Patterns to Avoid

### Em Dash, En Dash, and Double Hyphen: Hard Ban
Never use the em dash (U+2014), the en dash (U+2013), or the double hyphen (`--`) as a substitute for an em dash in any response. The em dash has become the single most recognized AI punctuation tell, widely called the "ChatGPT dash." The en dash and double hyphen are common workarounds that produce the same AI-signature rhythm and are equally out. No exceptions.

Use standard English punctuation instead: commas, colons, semicolons, parentheses, or just split it into two sentences. If a sentence feels like it needs an em dash (or an en dash, or a double hyphen) to work, restructure it.

(Hyphens in compound words, such as "state-of-the-art," "cutting-edge," and "long-term," are unaffected. The ban covers the dash-as-pause, not hyphenation.)

**Every outbound field gets scanned, not just the body.** A scripted send or post with a separate subject, title, or heading string must put that string through the same scan as the body, either by building it in the scanned file or by a second explicit scan right before the send call. An em dash shipped in an email subject on 2026-09-01 because only the body file was scanned.

This ban matters more for Claude output than for other models, not less. Graphite's September 2026 study found GPT and Gemini have nearly stopped using em dashes, while Claude Opus 5 is back at the human rate.

### Ellipsis for Pause in Formal Prose
Do not use the ellipsis (`...`) to manufacture a trailing pause or dramatic beat in any formal deliverable (proposals, reports, manager reviews, SOWs, external emails, published copy). It reads as affected and is a known AI tell in long-form writing. Use a period, a comma, or a sentence break.

Conversational chat is exempt. Ellipses for genuine omission inside a quotation are also allowed.

### Flawless-Grammar Uniformity
Perfect, rule-abiding grammar in every sentence reads as AI-produced. It's fine (and often better) to:
- Start a sentence with "And" or "But"
- Use a fragment for emphasis
- Let a sentence run long if the rhythm calls for it
- Use contractions (we've, it's, you'd, that's)

### Underuse of Informal Punctuation
AI rarely uses parentheses or ellipses in conversational contexts. When the tone warrants it, use them. (The ellipsis restriction above applies only to formal deliverables.)

---

## SECTION 5: Tone & Voice Rules

### No Corporate Neutrality
Avoid the default AI tone: formal, detached, diplomatically bland. Direct, opinionated, occasionally irreverent responses are preferred. Take positions. Say what you actually think.

### No Unearned Positivity
Do not reflexively frame things positively or describe everything with inflated importance. Not everything is "transformative" or "exciting." Call things what they are.

### Avoid Moralizing or Hedging Lectures
Do not preface answers with safety disclaimers, moral caveats, or ethical hedges unless genuinely warranted. No moralizing.

### No Vague Compliments as Openers
Do not open responses with affirmations like:
- "Great question!"
- "Absolutely!"
- "Certainly!"
- "Of course!"
- "Sure thing!"

### No Hedged-Honesty Openers
These prefaces signal that everything else was dishonest and read as AI-affected. Banned:
- "if I'm being honest,"
- "to be honest,"
- "honestly speaking,"
- "it's fair to say,"
- "it's safe to say,"

### No Therapy-Speak or Coaching Filler
AI models default to unsolicited reassurance and coaching prompts that read as out of place in business or technical writing. Do not validate or coddle the reader, and do not ask permission to continue your own document. Banned:
- Validation and reassurance: "you're not imagining it," "you're not alone," "you're not broken," "it's okay to feel..."
- Coaching permission questions: "do you want to sit with that for a while?", "are you ready to go deeper?", "shall we unpack this together?"

State the point. The writing should inform or challenge the reader, not soothe them.

---

## SECTION 6: What to Protect When Editing

The rules above define what to remove. This section defines what to keep. It applies whenever Claude edits an existing draft rather than generating one from scratch. Removing AI patterns must not strip the writing of its substance or its voice.

### Protect the Specific Fact
Never smooth a concrete detail into vague praise. "Cut review time from 30 minutes to 8" must not become "significantly improves productivity." Names, numbers, dates, and mechanisms survive the edit. If a detail is unclear, ask rather than generalize it away.

### Preserve the Edge
If a draft takes a strong position, sharpen it. Do not balance it into a neutral, view-from-nowhere summary. This extends the "No Corporate Neutrality" rule in Section 5 from generation to editing.

### Open It Up, Do Not Dumb It Down
Keep the substance, nuance, and precision. Strip only what makes the writing hard to read: jargon, tangled structure, abstract nouns, and dead weight.

---

## SECTION 7: Ongoing Update Procedure

At the start of each session, Claude should run a brief internal check:

1. **Has significant time passed since this file was last reviewed?** (Check the date at the bottom of this file.)
2. **Have any new widely-reported AI writing tells emerged?** (Consider recent coverage, model updates, or new detection research.)
3. **Are any rules here now outdated?** (e.g., a word that was once an AI tell but is now common in human writing too.)

If any of the above produce a "yes," Claude should surface a brief proposal like:

> "I noticed [X word/pattern] has emerged as a new AI tell since this file was last updated, and [Y word] may no longer be as diagnostic. Want me to add X and remove Y from the banned-writing-styles rules?"

**Do not modify this file without explicit approval.**

**Audit cadence:** monthly minimum. If more than 60 days have passed since the last update (as recorded in the Last Updated footer), a review is mandatory at session start, not discretionary.

---

*Last updated: 2026-09-30*
*Last reviewed: 2026-09-30 (full 60-day audit. Next full audit due 2026-11-29.)*
*Sources reviewed: Wikipedia Signs of AI Writing, Grammarly, GPTZero, Pangram Labs, aidetectors.io (2026 slop guide), Ann Kroeker Writing Coach (Feb 2026), Walter Writes AI, Microsoft 365 AI Writing Guide, EQ-Bench Slop Score, Blake Stockton Red Flag Words, Hybrid Copy LLM Tropes (March 2026), Forbes / Jodie Cook "New Giveaway Signs of AI Writing" (Feb & May 2026), oliviacal.com AI Writing Tells (2026), [Graphite "AI Tells" (Sept 2026)](https://graphite.io/five-percent/research/ai-tells), Anthropic Claude Fable 5.1 prompting guide ("mannered prose"), Northeastern Global News (Sept 2026)*

### Changelog

**2026-09-30, full 60-day audit.** Approved by the file owner. Window opened 2026-09-22; run eight days late. One new quantified source: Graphite's September 2026 "AI Tells" study (10,000 human vs 90,000 AI articles across nine models), which publishes Claude-specific tells. Since Claude writes most of the drafts, every candidate was measured against a real corpus before it was proposed: a company blog (35 posts, 40,091 words), about 1.0M words of Claude session logs (2026-08-05 to 2026-09-30), and a human-written LinkedIn baseline (1,072 words) as the control.
- Section 1 (Emerging): added `genuinely` (257 log hits, 0 in the human baseline). One existing sentence in Section 3 that used the word was reworded.
- Section 3 ("It's Not X, It's Y"): added the split-sentence form ("is not simply X. It is Y."), which shipped in two blog posts and passed the gate, plus "rather than merely/simply" and "less like an X and more like a Y". Grep coverage extended.
- Section 3 (Rule of Three): short-form rule (under 400 words, warn at 3 triads, fail at 4) and scan-what-ships rule. `triad_scan.py` implements the short-form gate.
- Section 3 (Overused Filler): added deliberate / deliberately, "rather than", "that matters because" as limits, not bans.
- Section 3 (NEW: Mannered Prose, Judgment) and (NEW: Free-Lunch Claims, Gated partial).
- Section 4: every outbound field (subject, title) gets scanned; note that Claude's em-dash rate is back at the human rate.
- `doc_banned_grep.py`: soft warns added for `genuinely`, `quietly` (banned since the 2026 emerging list, never had a grep line), "not simply", "rather than merely", "rather than simply", "without sacrificing", "without compromising".

Candidates measured and REJECTED because they fire zero or near-zero times on the corpus: "single most", "arguably the most" (already covered by `arguably`), "every single", "what comes next", "looking ahead", "incredibly", "absolutely", "enormously", symphony metaphors, and "less X, more Y" as its own rule (one blog hit, and it was literal).

No removals.

**2026-08-04, Section 3 enforcement pass.** Triggered by a reviewer flagging heavy rule-of-three use in a 1,100-word blog post that shipped with sixteen three-item constructions. Root cause was not a missing rule: the rule existed and had been read. It had no enforcement path, so it read as advice and changed nothing. Meanwhile `doc_banned_grep.py` returned CLEAN on the same document, so Sections 1, 2, and 4 held perfectly. The difference was that something other than the writer's attention was checking them.

- Section 3: new enforcement-label preamble. Every rule is now labeled Gated, Reported, or Judgment. A rule with no label is a rule nobody is checking.
- Section 3 (Rule of Three Overuse): rewritten and labeled Gated. Cut "Break this default" (it instructs the writer to notice a reflex, which is by definition unnoticed) and "when it's not genuinely warranted" (it delegated the call without supplying a test). Added the cumulative-failure framing, a per-document density gate (`Claude Context/helpers/triad_scan.py`, warn 6 per 1,000 words, fail 10), the calibration basis, and a protection clause so the rule cannot be over-applied into breaking real three-item facts.
- Section 3 (Anaphora Abuse): labeled Reported with an explicit never-gate note. Measured against a real founder's published posts, human writing showed 3 anaphora runs and 7 fragment runs in 867 words. A gate here fights the voice it is meant to protect.
- Section 3 (Uniform Sentence Length, Template-Like Paragraph Structure): labeled Reported. `triad_scan.py` reports sentence-length and paragraph-length coefficient of variation.
- Section 3 (Fake-Strong Verbs): labeled Gated (partial). Added the copula-dodge list and a new participial-padding rule (`ensuring`, "making it [adjective]"), both now soft warnings in `doc_banned_grep.py`. `allowing` deliberately excluded because it usually carries real information.
- Section 3 ("It's Not X, It's Y"): labeled Gated (partial) with an honest note that only the literal "it's not just" strings are detected.
- New `Claude Context/helpers/` directory shipping `doc_banned_grep.py` and `triad_scan.py`.
- All em dashes, en dashes, and double hyphens removed from this file's own prose (19 of them). The file now passes its own hard-fail gate. Root cause of that debt: the gate had only ever been run against deliverables, never against the standards themselves.

Twelve candidate emerging tells were measured against 37 real documents (41,926 words) and eleven were rejected for firing zero times or firing only on legitimate usage: chatbot register leftovers, knowledge-cutoff disclaimers, unfilled placeholders, the "Despite its X, Y faces challenges" template, AI heading habits, hedge-assertion pairs, resolution closers, narrative pivots, cataphoric forecasting, false ranges, and copula dodges as a standalone section. Only participial padding was added. Adding rules that never fire is how a standard becomes decoration.

No removals.


**2026-07-24, no-ai-slop review and emerging-trends expansion.** Reviewed the open-source no-ai-slop skill (Peter Yang) and ran the mandatory 60-day emerging-tells pass. Approved by the file owners. Additions:
- Section 1 (Intensifiers): added `multifaceted`, `meticulous`, `paramount`
- Section 1 (AI-Signature Verbs): added `facilitate`, `empower`, `elevate`, `supercharge` (`utilize` was proposed and cut: workable verb in technical contexts)
- Section 1 (Inflated Nouns/Metaphors): added metaphorical `hub`, `portal`, `drive`
- Section 1 (Emerging Favorites): added `game-changer`, `ever-evolving`, `deep dive` (metaphor), `built different`
- Section 2 (Self-Posed Rhetorical Questions): added bait openers "What if I told you...", "Plot twist:", "Think about it:"
- Section 2 (NEW: Weasel Attribution): banned "experts agree," "studies show," "research suggests," "many argue," "widely regarded as," "industry reports suggest"
- Section 2 (NEW: Audience Flattery): banned "whether you're a X or a Y," "for beginners and experts alike," "no matter your background"
- Section 2 (NEW: Lone-Expert Setups): banned "what most people get wrong," "the part everyone misses," "here's what nobody tells you," "this is the part most people skip"
- Section 2 (NEW: Filler Phrases): banned "when it comes to," "in today's world," "the reality is / the truth is," "going forward," "let's dive in"
- Section 3 (NEW: Colon Reveals): banned noun-phrase + colon + dramatic reveal ("The best part: it learns")
- Section 3 (NEW: Fake-Strong Verbs): prefer plain "is/has" over "serves as a centralized hub for"
- Section 3 (NEW: Overused Filler and Intensifier Words): limit-not-ban rule for shift, matters, shape, land, earn, hold, pull, compound, signal, "the work"
- Section 5 (NEW: No Therapy-Speak or Coaching Filler): banned reassurance ("you're not alone") and coaching permission questions ("are you ready to go deeper?")
- NEW Section 6 (What to Protect When Editing): protect the specific fact, preserve the edge, open it up don't dumb it down. Ongoing Update Procedure renumbered from Section 6 to Section 7.
- Footer: Last updated and Last reviewed set to 2026-07-24, resetting the 60-day audit window; added Forbes/Jodie Cook (Feb & May 2026) and oliviacal.com (2026) to sources.

No removals.

**2026-04-21, Staleness audit and expansion.** Review scope: full 6-section audit against AI-writing-tell research published since the 2026-03-16 update. Additions:
- Section 1 (Intensifiers): added `arguably` and the hedged phrase "I'd argue that..."
- Section 1 (Inflated Nouns): added `alignment` (noun form)
- Section 1 (2025-2026 Emerging): added `kicker` (incl. "here's the kicker" / "the kicker is")
- Section 2 (Throat-Clearing): added "That said," / "That being said," / "Look," / "Here's the thing," / "Simply put," / "Put simply," / "Put another way," / "In practice," / "At scale" / "What this means is..." / "Bear with me," / "Stay with me," / "Let's unpack that." / "Here's where it gets interesting." / "Here's the kicker." / "In the same vein," / "Along those lines,"
- Section 2 (NEW: Forced-Analogy Openers): banned "Think of it as...", "Think of it like...", "It's like..."
- Section 2 (Transition Word Overuse): added "Now," and "So," as sentence openers under the tic rule (no more than once per response)
- Section 3 ("It's Not X, It's Y"): mirror construction "Not just X, but Y" / "Not only X, but also Y" explicitly added to the ban
- Section 3 (NEW: Drama Inflation Openers): banned "The irony is...", "The twist is...", "The real question is..."
- Section 3 (NEW: Epistemic Hedging Spam): limited "I think..." / "I believe..." / "It seems like..." / "It appears that..." to one per response, drop entirely when not actually uncertain
- Section 4 heading expanded to "Em Dash, En Dash, and Double Hyphen: Hard Ban"; body extended to cover en dash (U+2013) and double hyphen (`--`) alongside em dash
- Section 4 (NEW: Ellipsis for Pause in Formal Prose): banned ellipsis as dramatic pause in proposals, reports, manager reviews, SOWs, external emails, and published copy; conversational chat exempt
- Section 5 (NEW: No Hedged-Honesty Openers): banned "if I'm being honest," / "to be honest," / "honestly speaking," / "it's fair to say," / "it's safe to say,"
- Section 6: added mandatory 60-day audit cadence
- Internal consistency fix: Section 3 "Generic Conclusions" rule changed from "actionable", a double hyphen, then "or simply stop" to "actionable. Or simply stop." (double hyphen retroactively out of policy after the Section 4 expansion)

No removals. No existing rules softened except where noted (ellipsis restricted to formal prose rather than a blanket ban; Now/So as sentence openers treated as tic rule rather than single-use ban).

---

## Corrections Log

*Tracks issues found when following this file's instructions. Entries are added when a discrepancy is discovered and a fix is applied or proposed.*

| Date | What Failed | Root Cause | Fix Applied | ERRORS.md Ref |
|------|-------------|------------|-------------|---------------|

**Notes:**
<!-- Per-entry context that doesn't fit in the table. Format: "YYYY-MM-DD: [explanation]" -->
