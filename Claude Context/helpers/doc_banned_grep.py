#!/usr/bin/env python3
"""
doc_banned_grep.py - Post-write banned-character gate for authored documents.

Purpose
-------
Catches the punctuation and vocabulary tells from
`Claude Context/writing/banned-writing-styles.md` in any authored .md / .txt / .html
deliverable BEFORE it is committed. Built after the em-dash-in-doc pattern recurred
four times (wave-7 runbook x3, the #442 plan doc), each caught only when a grep was
run from memory. This makes the check mechanical instead of memory-dependent.

It reads any UTF-8 text file, so it also scans source files (.cs / .razor) and a
commit message piped in via /dev/stdin. The dash checks are safe on C# because the
double-hyphen patterns require an alphanumeric or whitespace on both sides, so
decrement operators like `i--` and `count--` do not trip it. See the Pre-Push
Checklist in `coding/source-control.md` for the source-and-commit-message wiring
(added after em dashes leaked into a .cs comment and a commit message, ERRORS.md
2026-06-26 and 2026-06-27).

What it flags
-------------
HARD FAIL (exit 1) - unambiguous AI punctuation tells:
  - em dash      U+2014  (the "ChatGPT dash")
  - en dash      U+2013
  - double hyphen used as a pause ("word -- word" or "word--word"), excluding
    markdown horizontal rules and table separators (runs of 3+ hyphens)

SOFT WARN (exit 2 when no hard fails) - high-signal banned vocabulary:
  A curated subset of the Section 1 list, limited to words that are NOT common in
  legitimate technical prose. Deliberately excludes ambiguous words like "key"
  (key vault, primary key) and "framework" (.NET framework) to avoid false alarms.

CLEAN (exit 0).

Markdown-aware
--------------
Fenced code blocks (``` ... ```) are skipped for both checks: code legitimately
contains `--` (CLI flags) and is not prose. Inline code spans are left in scope for
the dash check but excluded from vocab matching.

Usage
-----
  python3 doc_banned_grep.py FILE [FILE ...]
  python3 doc_banned_grep.py docs/call-center/feat-issue-442/*.md
  git diff --cached --name-only --diff-filter=ACM | grep -E '\.(cs|razor)$' | xargs -r python3 doc_banned_grep.py
  printf '%s' "$MSG" | python3 doc_banned_grep.py /dev/stdin   # scan a commit message

Exit codes: 0 clean, 1 hard fail (dashes), 2 soft warn only (vocab). Use in a gate:
  python3 .../doc_banned_grep.py "$f" || { echo "clean the doc, re-run"; }
"""

import sys
import re

EM_DASH = "—"
EN_DASH = "–"

# High-signal banned vocabulary. Curated to avoid technical false positives.
# Word-boundary, case-insensitive. Multi-word phrases matched as substrings.
BANNED_WORDS = [
    "crucial", "crucially", "pivotal", "robust", "seamless", "seamlessly",
    "delve", "underscore", "underscores", "underscoring", "showcase",
    "showcases", "showcasing", "transformative", "revolutionize", "bolster",
    "garner", "spearhead", "tapestry", "beacon", "cutting-edge",
    "furthermore", "moreover",
    # 2026-07-24 no-ai-slop sync (Scott team update). Azure/security-ambiguous
    # words (hub, portal, drive, elevate, facilitate) deliberately excluded.
    "multifaceted", "meticulous", "meticulously", "paramount", "supercharge",
    "supercharges", "empower", "empowers", "empowering", "game-changer",
    "ever-evolving",
]
BANNED_PHRASES = [
    "it's worth noting", "it is worth noting", "it's important to note",
    "it is important to note", "plays a crucial role", "plays a pivotal role",
    "at its core", "in essence", "unlock the potential", "harness the power",
    "navigate the complexities", "it's not just", "it is not just",
    # 2026-07-24 no-ai-slop sync: weasel attribution, audience flattery,
    # lone-expert setups, filler openers, bait openers, therapy-speak.
    "deep dive", "built different", "experts agree", "studies show",
    "research shows", "research suggests", "widely regarded as",
    "whether you're a", "for beginners and experts alike",
    "no matter your background", "what most people get wrong",
    "here's what nobody tells you", "the part everyone misses",
    "when it comes to", "in today's world", "going forward",
    "let's dive in", "what if i told you", "plot twist", "think about it",
    "you're not alone", "are you ready to go deeper",
    # 2026-08-04 Section 3 enforcement pass. Participial padding: a sentence-final
    # -ing clause that tacks on a vague benefit instead of a fact. Measured at
    # ~80% precision across 37 TIPS documents. "allowing" is deliberately absent:
    # it usually carries real information ("allowing agents to send and receive
    # text messages from a call queue"), so flagging it would be noise.
    ", ensuring ", ", making it ", ", cementing ", ", solidifying ",
    ", reinforcing ", ", reflecting the ",
    # Copula dodges. These almost always want to be "is" or "has". "represents"
    # and "constitutes" are excluded: both are legitimate in contract and
    # compliance prose, which TIPS writes a lot of.
    "serves as", "serving as", "functions as", "acts as", "act as", "boasts",
    "stands as",
]

_word_res = [re.compile(rf"\b{re.escape(w)}\b", re.IGNORECASE) for w in BANNED_WORDS]
_phrase_res = [re.compile(re.escape(p), re.IGNORECASE) for p in BANNED_PHRASES]

# A double-hyphen used as an em-dash substitute. Two legitimate-prose forms:
#   spaced pause:  "word -- word"   (whitespace on both sides of the --)
#   word-joined:   "word--word"     (alphanumeric on both sides, no spaces)
# This deliberately does NOT match CLI long-options like "--verbose" (space before,
# letters after) which are valid to mention in prose. Runs of 3+ hyphens (markdown
# rules and table separators) are excluded separately by the is_rule_or_sep check.
_dbl_hyphen_spaced = re.compile(r"(?:^|\s)--(?:\s|$)")
_dbl_hyphen_joined = re.compile(r"[A-Za-z0-9]--[A-Za-z0-9]")


def scan(path):
    """Return (hard_fails, soft_warns) lists of (lineno, kind, snippet)."""
    hard, soft = [], []
    try:
        lines = open(path, encoding="utf-8").read().splitlines()
    except (OSError, UnicodeDecodeError) as e:
        return [(0, "read-error", str(e))], []

    in_fence = False
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        # Toggle fenced code blocks.
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        # --- HARD: em / en dash (always, anywhere in prose) ---
        if EM_DASH in line:
            hard.append((i, "em-dash (U+2014)", line.strip()[:100]))
        if EN_DASH in line:
            hard.append((i, "en-dash (U+2013)", line.strip()[:100]))

        # --- HARD: double-hyphen pause, excluding HR / table separator rows ---
        # Skip rows that are markdown rules or table separators (only -, |, :, space).
        is_rule_or_sep = bool(stripped) and set(stripped) <= set("-|: ")
        if not is_rule_or_sep and (_dbl_hyphen_spaced.search(line)
                                   or _dbl_hyphen_joined.search(line)):
            hard.append((i, "double-hyphen pause", line.strip()[:100]))

        # --- SOFT: vocab (strip inline code spans first) ---
        prose = re.sub(r"`[^`]*`", "", line)
        for rx in _word_res:
            m = rx.search(prose)
            if m:
                soft.append((i, f"banned word: {m.group(0)}", line.strip()[:100]))
        for rx in _phrase_res:
            m = rx.search(prose)
            if m:
                soft.append((i, f"banned phrase: {m.group(0)}", line.strip()[:100]))
    return hard, soft


def main(argv):
    paths = argv[1:]
    if not paths:
        print("usage: doc_banned_grep.py FILE [FILE ...]")
        return 0

    total_hard = total_soft = 0
    for path in paths:
        hard, soft = scan(path)
        if not hard and not soft:
            print(f"CLEAN  {path}")
            continue
        print(f"\n=== {path} ===")
        for ln, kind, snip in hard:
            print(f"  HARD  L{ln}: {kind}\n        {snip}")
        for ln, kind, snip in soft:
            print(f"  warn  L{ln}: {kind}\n        {snip}")
        total_hard += len(hard)
        total_soft += len(soft)

    print()
    if total_hard:
        print(f"RESULT: {total_hard} hard fail(s), {total_soft} warning(s). "
              f"Fix the hard fails (dashes) before committing.")
        return 1
    if total_soft:
        print(f"RESULT: 0 hard fails, {total_soft} warning(s). "
              f"Review vocab; commit allowed if intentional.")
        return 2
    print("RESULT: clean.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
