# Writing gate helpers

Two scripts that make the rules in `banned-writing-styles.md` mechanical instead of memory-dependent.

`doc_banned_grep.py` covers Sections 1, 2, and 4: banned vocabulary, banned phrases, participial padding, and the punctuation tells (em dash, en dash, double-hyphen-as-pause). Exit 1 on a punctuation hard fail, exit 2 on a vocabulary soft warning.

`triad_scan.py` covers the Section 3 structural tells a vocabulary grep cannot see. It measures three-item-construction density per 1,000 words and reports sentence-length and paragraph-length coefficient of variation, short-fragment runs, and anaphora runs. Only the triad density is gated. The other four are informational, because gating anaphora fights the author's own voice.

Run both before committing any authored prose file:

```bash
python3 doc_banned_grep.py path/to/file.md
python3 triad_scan.py      path/to/file.md
```

Thresholds in `triad_scan.py` are calibrated against a specific corpus. Recalibrate them against your own before treating them as settled: see the Calibration note in the Rule of Three section of `banned-writing-styles.md`.
