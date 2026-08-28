#!/usr/bin/env python3
"""
triad_scan.py - Rule-of-three density scan for authored prose.

Companion to doc_banned_grep.py. That script catches the greppable tells from
banned-writing-styles.md Sections 1, 2, and 4 (vocabulary, phrases, dashes).
This one measures the Section 3 structural tell a word list cannot see: the
three-item construction used for cadence rather than for count.

It counts four construction types and reports density per 1,000 words:

  SYN3   syndetic tricolon      "extensions, paging zones, and bell schedules"
  ASY3   asyndetic tricolon     "on paper, in a budget cycle, against a list"
  POLY3  polysyndetic tricolon  "phones and paging and access control"
  LIST3  a bullet or numbered list with exactly three items

Series of four or more items are reported separately (LONG) and are NOT counted
as triads. That was the main over-report in the ad-hoc grep this replaces:
"A, B, C, and D" matches a naive three-item regex on its first three items.

Method
------
Not a single regex. Each sentence is split on commas into segments, the
coordinating conjunction is located, and the run of parallel items is walked
backward from it, stopping at anything that reads as a clause rather than a
list item. That is what makes the item count trustworthy enough to separate
three from four.

It does not judge decorative versus factual. That call stays human. What it
does is make the density visible so the judgment gets made at all.

Usage
-----
  python3 triad_scan.py FILE [FILE ...]
  python3 triad_scan.py --json FILE            # machine-readable
  python3 triad_scan.py --limit 6 FILE         # override the density gate

Exit codes: 0 at or under the gate, 2 over the gate, 1 read error.
"""

import json
import re
import sys

# Two tiers, mirroring doc_banned_grep.py's soft-warn / hard-fail shape.
# Both numbers are calibrated against the TIPS blog corpus and Albert's own
# LinkedIn prose, not against published research: no source publishes a usable
# per-N-words threshold for triads. See the Calibration note in the proposal.
WARN_PER_1K = 6.0    # 1 per 167 words. Corpus p25. Review the list.
FAIL_PER_1K = 10.0   # 1 per 100 words. Corpus p75+. Do not publish as-is.

# ---------------------------------------------------------------- text cleanup

_FRONTMATTER = re.compile(r"\A---\r?\n.*?\r?\n---\r?\n", re.DOTALL)
_FENCE = re.compile(r"^```.*?^```", re.DOTALL | re.MULTILINE)
_INLINE_CODE = re.compile(r"`[^`]*`")
_MD_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")   # keep link text, drop the URL
_HTML_TAG = re.compile(r"<[^>]+>")
_BOLD_ITAL = re.compile(r"(\*\*|__|\*|_)")
_HEADING = re.compile(r"^#{1,6}\s+", re.MULTILINE)
_URL = re.compile(r"https?://\S+")
_LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d{1,3}[.)])\s+(.*)$")


def strip_markdown(raw):
    """Return (prose_text, list_item_groups). Frontmatter and code are dropped."""
    body = _FRONTMATTER.sub("", raw)
    body = _FENCE.sub("", body)

    groups, current = [], []
    for line in body.splitlines():
        m = _LIST_ITEM.match(line)
        if m:
            current.append(m.group(1).strip())
        elif line.strip() == "":
            continue                      # blank lines do not break a list run
        else:
            if current:
                groups.append(current)
                current = []
    if current:
        groups.append(current)

    text = _LIST_ITEM.sub(r"\1\n", body)
    text = re.sub(r"([^.!?:;\n])\n(?=\S)", r"\1.\n", text)
    text = _HEADING.sub("", text)
    text = _MD_LINK.sub(r"\1", text)
    text = _INLINE_CODE.sub(" ", text)
    text = _HTML_TAG.sub(" ", text)
    text = _URL.sub(" ", text)
    text = _BOLD_ITAL.sub("", text)
    return text, groups


def word_count(text):
    return len(re.findall(r"[A-Za-z0-9][\w'\-]*", text))


# --------------------------------------------------------------- sentence split

_ABBREV = r"(?<!\bMr)(?<!\bMrs)(?<!\bDr)(?<!\bSt)(?<!\bvs)(?<!\bU\.S)(?<!\be\.g)(?<!\bi\.e)"
_SENT_END = re.compile(_ABBREV + r"(?<=[.!?])[\"')\]]*\s+(?=[A-Z0-9\"'(])")


def sentences(text):
    for chunk in re.split(r"\n{2,}", text):
        chunk = re.sub(r"\s+", " ", chunk).strip()
        if not chunk:
            continue
        for s in _SENT_END.split(chunk):
            s = s.strip()
            if s:
                yield s


# ------------------------------------------------------------ series detection

# Finite verbs. Used only to trim framing off the first and last segments of a
# series, never to reject an item: a tricolon of parallel clauses ("what to
# check, why it matters, and how to run it") is exactly the pattern under audit.
_FINITE = re.compile(
    r"\b(?:is|are|was|were|am|be|been|being|has|have|had|will|would|shall|"
    r"should|can|could|may|might|must|do|does|did|build|builds|pull|pulls|"
    r"place|places|write|writes|run|runs|open|opens|confirm|confirms|"
    r"needs?|gets?|keeps?|makes?|takes?|comes?|goes|knows?|means?|matters?|"
    r"shows?|sends?|reaches|carries|presents|costs?)\b",
    re.IGNORECASE,
)

# A segment opening with one of these starts a new clause, so the item run ends
# there and the segment itself is not an item. Deliberately excludes the
# interrogative words (what / why / how / who / when) because those head the
# parallel clauses in a clause-level tricolon.
_CLAUSE_BREAK = re.compile(
    r"^(?:and\s+)?(?:so|but|yet|because|since|although|though|unless|until|"
    r"whereas|while|therefore|however|meanwhile|instead|it|they|he|she|we|"
    r"you|i|that|this|these|those|which|there|then)\b",
    re.IGNORECASE,
)

# Marks where a list actually begins inside a segment. Everything before it is
# framing, not item one. This is what stops "calendar, including early-release
# days, assembly schedules, and any staggered start" reading as four items.
_LIST_INTRO = re.compile(
    r"\b(?:including|includes?|included|such as|like|namely|for example|"
    r"e\.g\.|specifically|from|between|whether)\s+", re.IGNORECASE,
)

_CONJ_TAIL = re.compile(r",?\s+\b(and|or)\s+(?!so\b|then\b|that\b|if\b|when\b)",
                        re.IGNORECASE)

# A segment opening with a subordinator is a frame clause, not item one, and
# nothing item-like can be recovered from it. "When the system is not updated,
# bells ring late and announcements cut in" is two clauses, not a tricolon.
_SUBORD = re.compile(
    r"^(?:when|while|if|because|since|although|though|unless|until|after|"
    r"before|whereas|whenever|once|as)\b", re.IGNORECASE,
)

_OPEN_CLASSES = (
    ("DET", r"(?:the|a|an|this|that|these|those|every|each|any|another|one|"
            r"two|three|four|no|its|his|her|their|our|your|my|\d+)\b"),
    ("PREP", r"(?:by|in|on|at|for|with|from|to|of|during|without|within|"
             r"across|through|after|before|between|about|into|under|over|"
             r"against|as)\b"),
    ("WH", r"(?:what|why|how|who|whom|whose|when|where|whether|which)\b"),
    ("TO", r"to\b"),
)


def open_class(seg):
    """Coarse opening-word class, used only as a parallelism check."""
    w = seg.strip().lower()
    for name, pat in _OPEN_CLASSES:
        if re.match(pat, w):
            return name
    if re.match(r"\w+(?:ing|ed)\b", w):
        return "PART"
    return "OTHER"


def _is_item(seg, allow_subord=False):
    """A coordinate item: short, no clause-break opener, no internal stop."""
    if not seg or len(seg) > 80:
        return False
    if not allow_subord and _SUBORD.match(seg):
        return False
    if _CLAUSE_BREAK.match(seg):
        return False
    if re.search(r"[;:]", seg):
        return False
    return bool(re.search(r"[A-Za-z]", seg))


def _trim_tail(seg):
    """Cut a final item at a trailing finite verb, so 'an after-hours path are
    what keep volume down' yields the item 'an after-hours path'."""
    seg = seg.strip()
    m = _FINITE.search(seg)
    if m and m.start() > 0:
        head = seg[:m.start()].strip().rstrip(",")
        if head:
            return head
    return seg


def _trim_head(seg, want_class=None, peers=None):
    """Recover item one from the segment that also carries the sentence frame.
    'Can more than one person trigger an all-call' -> 'trigger an all-call'.
    'We build phones' -> 'phones'. Returns None if nothing item-like remains.

    A subordinate frame clause yields nothing: the series has not started yet.
    When want_class is given, the recovered item must open in the same coarse
    class as the items already collected, which is what stops 'actually respond'
    from joining 'by text, by email, as a notification'."""
    seg = seg.strip()
    if _SUBORD.match(seg) and all(_FINITE.search(i) for i in (peers or [])) \
            and len(peers or []) >= 2:
        # The coordinated elements are finite clauses, so this is clause
        # coordination and the subordinate frame holds no item one.
        return None

    intro = None
    for m in _LIST_INTRO.finditer(seg):
        intro = m
    if intro:
        rest = seg[intro.end():].strip()
        if _is_item(rest) and (want_class is None or open_class(rest) == want_class):
            return rest
        return None

    last = None
    for m in _FINITE.finditer(seg):
        last = m
    if not last:
        return None
    rest = seg[last.end():].strip()
    if not _is_item(rest):
        return None
    if want_class is None or open_class(rest) == want_class:
        return rest
    # The frame ran past the verb. Try progressively shorter trailing phrases.
    words = rest.split()
    for start in range(1, len(words)):
        cand = " ".join(words[start:])
        if open_class(cand) == want_class and _is_item(cand):
            return cand
    return None


def _majority_class(items):
    if not items:
        return None
    counts = {}
    for it in items:
        c = open_class(it)
        counts[c] = counts.get(c, 0) + 1
    top = max(counts.items(), key=lambda kv: kv[1])
    return top[0] if top[1] >= 2 or len(items) == 1 else None


def _split_clauses(sentence):
    """Split on semicolons and colons; a series never spans them."""
    return [c for c in re.split(r"[;:]", sentence) if c.strip()]


def find_series_in_clause(clause):
    """Return list of (kind, item_count, items) for one clause."""
    out = []
    segs = [s.strip() for s in clause.split(",")]
    if len(segs) < 2:
        # No commas. Only polysyndeton is possible here.
        parts = re.split(r"\s+and\s+", clause, flags=re.IGNORECASE)
        if len(parts) == 3 and all(_is_item(p.strip()) for p in parts[:2]):
            tail = _trim_tail(parts[2])
            if tail:
                out.append(("POLY3", 3, [p.strip() for p in parts[:2]] + [tail]))
        return out

    # Locate the segment carrying the coordinating conjunction.
    conj_idx = None
    for i in range(len(segs) - 1, 0, -1):
        if re.match(r"^(and|or)\s+", segs[i], re.IGNORECASE) or \
           _CONJ_TAIL.search(segs[i]):
            conj_idx = i
            break

    if conj_idx is None:
        # Asyndetic run: walk back from the last segment.
        items = []
        for i in range(len(segs) - 1, -1, -1):
            cand = _trim_tail(segs[i]) if i == len(segs) - 1 else segs[i]
            if _is_item(cand):
                items.insert(0, cand)
                continue
            head = _trim_head(segs[i], _majority_class(items), items)
            if head:
                items.insert(0, head)
            break
        if len(items) == 3:
            out.append(("ASY3", 3, items))
        elif len(items) >= 4:
            out.append(("LONG", len(items), items))
        return out

    # Syndetic: last item is whatever follows the conjunction.
    seg = segs[conj_idx]
    m = re.match(r"^(and|or)\s+(.*)$", seg, re.IGNORECASE)
    last = m.group(2) if m else _CONJ_TAIL.split(seg)[-1]
    head_in_seg = None
    if not m:
        pieces = _CONJ_TAIL.split(seg)
        if len(pieces) >= 3:
            head_in_seg = pieces[0].strip()   # non-Oxford "a, b and c"
    last = _trim_tail(last)
    if not last or _CLAUSE_BREAK.match(last):
        return out

    items = [last]
    if head_in_seg:
        cand = head_in_seg if _is_item(head_in_seg) else _trim_head(
            head_in_seg, _majority_class(items), items)
        if not cand:
            return out
        items.insert(0, cand)

    for i in range(conj_idx - 1, -1, -1):
        seg_i = segs[i]
        intro_at_start = re.match(_LIST_INTRO, seg_i)
        if intro_at_start:
            # The list begins here. Take what follows and stop walking back.
            rest = seg_i[intro_at_start.end():].strip()
            if _is_item(rest):
                items.insert(0, rest)
            break
        if _is_item(seg_i):
            items.insert(0, seg_i)
            continue
        head = _trim_head(seg_i, _majority_class(items), items)
        if head:
            items.insert(0, head)
        break

    if len(items) == 3:
        out.append(("SYN3", 3, items))
    elif len(items) >= 4:
        out.append(("LONG", len(items), items))
    return out


def find_series(text):
    triads, longs = [], []
    for sent in sentences(text):
        for clause in _split_clauses(sent):
            for kind, n, items in find_series_in_clause(clause):
                rec = (kind, n, " / ".join(items))
                (longs if kind == "LONG" else triads).append(rec)
    return triads, longs


def _sent_words(text):
    return [len(re.findall(r"[A-Za-z0-9][\w'\-]*", s)) for s in sentences(text)]


def _cv(vals):
    """Coefficient of variation. Low CV is the mechanical signature of uniform
    sentence or paragraph length (the 'burstiness' measure, sigma over mu)."""
    vals = [v for v in vals if v > 0]
    if len(vals) < 4:
        return None
    mu = sum(vals) / len(vals)
    var = sum((v - mu) ** 2 for v in vals) / len(vals)
    return round((var ** 0.5) / mu, 3) if mu else None


def find_fragment_runs(text, max_words=6, run=3):
    """Runs of three or more consecutive very short sentences. Same rhetorical
    move as an in-sentence triad, delivered as fragments: 'Lightning. Power
    surge. Water damage.' Reported separately because Albert's own voice uses
    it deliberately in Register A."""
    sents = list(sentences(text))
    lens = [len(re.findall(r"[A-Za-z0-9][\w'\-]*", s)) for s in sents]
    hits, i = [], 0
    while i < len(sents):
        j = i
        while j < len(sents) and 0 < lens[j] <= max_words:
            j += 1
        if j - i >= run:
            hits.append((j - i, " / ".join(s.rstrip(".") for s in sents[i:j])))
            i = j
        else:
            i = max(i + 1, j)
    return hits


_FIRST_WORD = re.compile(r"^[\"\'(]*([A-Za-z][\w'\-]*)")


def find_anaphora(text, run=3):
    """Three or more consecutive sentences opening on the same word. This is the
    Anaphora Abuse rule in Section 3, and it is fully mechanical."""
    sents = list(sentences(text))
    firsts = []
    for s in sents:
        m = _FIRST_WORD.match(s)
        firsts.append(m.group(1).lower() if m else None)
    hits, i = [], 0
    while i < len(sents):
        j = i + 1
        while j < len(sents) and firsts[j] and firsts[j] == firsts[i]:
            j += 1
        if j - i >= run and firsts[i]:
            hits.append((j - i, firsts[i], sents[i][:60]))
            i = j
        else:
            i += 1
    return hits


def find_list_triads(groups):
    return [("LIST3", 3, " / ".join(g)[:120]) for g in groups if len(g) == 3]


# ----------------------------------------------------------------------- report

def scan(path):
    try:
        raw = open(path, encoding="utf-8").read()
    except (OSError, UnicodeDecodeError) as e:
        return {"path": path, "error": str(e)}

    text, groups = strip_markdown(raw)
    words = word_count(text)
    triads, longs = find_series(text)
    list3 = find_list_triads(groups)

    n = len(triads)
    per_1k = (n / words * 1000) if words else 0.0
    paras = [p for p in re.split(r"\n{2,}", text) if p.strip()]
    return {
        "path": path,
        "sentence_len_cv": _cv(_sent_words(text)),
        "paragraph_len_cv": _cv([word_count(p) for p in paras]),
        "fragment_runs": find_fragment_runs(text),
        "anaphora_runs": find_anaphora(text),
        "words": words,
        "prose_triads": n,
        "per_1k": round(per_1k, 2),
        "one_per_words": round(words / n) if n else None,
        "list_triads": len(list3),
        "longer_series": len(longs),
        "hits": triads + list3,
        "longs": longs,
    }


def main(argv):
    as_json = "--json" in argv
    verbose = "--verbose" in argv
    warn, fail = WARN_PER_1K, FAIL_PER_1K
    args = []
    skip = False
    for a in argv[1:]:
        if skip:
            skip = False
            continue
        if a == "--limit":
            skip = True
            warn = float(argv[argv.index(a) + 1])
        elif a.startswith("--limit="):
            warn = float(a.split("=", 1)[1])
        elif a.startswith("--"):
            continue
        else:
            args.append(a)

    if not args:
        print("usage: triad_scan.py [--json] [--verbose] [--limit N] FILE ...")
        return 0

    results = [scan(p) for p in args]
    if as_json:
        print(json.dumps(results, indent=2))
        return 0

    n_fail = n_warn = 0
    for r in results:
        if "error" in r:
            print(f"ERROR  {r['path']}: {r['error']}")
            continue
        d = r["per_1k"]
        if d >= fail:
            flag, n_fail = "FAIL", n_fail + 1
        elif d >= warn:
            flag, n_warn = "warn", n_warn + 1
        else:
            flag = "ok  "
        print(f"\n=== {r['path']} ===")
        print(f"  {flag}  {r['prose_triads']} prose triads / {r['words']} words "
              f"= {d} per 1,000 (1 per {r['one_per_words']} words); "
              f"warn {warn}, fail {fail}")
        print(f"        {r['list_triads']} three-item list(s), "
              f"{r['longer_series']} series of four or more (not counted)")
        for kind, k, snip in r["hits"]:
            print(f"    {kind}  {snip[:110]}")
        if verbose:
            for kind, k, snip in r["longs"]:
                print(f"    LONG({k}) {snip[:110]}")
        print("  other Section 3 structure (reported, not gated):")
        print(f"     sentence-length CV {r['sentence_len_cv']} "
              f"(under ~0.45 reads uniform), "
              f"paragraph-length CV {r['paragraph_len_cv']}")
        for k, snip in r["fragment_runs"]:
            print(f"     FRAG{k}  {snip[:100]}")
        for k, w, snip in r["anaphora_runs"]:
            print(f"     ANAPH{k} on '{w}'  {snip}")
    print()
    if n_fail:
        print(f"RESULT: {n_fail} file(s) at or over the {fail}/1k fail gate, "
              f"{n_warn} at warn. Cut the decorative triads, keep the real counts.")
        return 2
    if n_warn:
        print(f"RESULT: 0 fails, {n_warn} file(s) at warn "
              f"({warn}/1k). Review the triad list before publishing.")
        return 2
    print("RESULT: clean.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
