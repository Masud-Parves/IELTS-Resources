# Source inventory — All_TFNG_Set01–05.pdf

Build date: 2026-10-10
Family: Identifying Information / Views (TFNG + YNNG), all sub-types, Passage level: All
Scripts: `Output/scripts/extract_tfng.py` (parse + classify), `aggregate.py` (dedupe + group), `build_pdf.py` (render)

## Scan summary

- Source folders scanned: `Passage 1/` (25 files), `Passage 2/` (22 files), `Passage 3/` (12 files) — 58 HTML files combined, `.1 file failed to parse: 0`.
- Files containing at least one TFNG/YNNG question: 41 of 58.
- Raw TFNG/YNNG questions found across all files (before dedup): 283.
- Unique passages after deduplication: 50 (32 at level 1, 3 at level 2, 15 at level 3).
- Unique TFNG/YNNG questions included across the 5 PDFs: 267.

## Duplicate passages (same passage found in more than one source file)

Only the first-seen copy of each was included; the duplicate source is listed for traceability.

1. **An important language development** — `Passage 1/Passage 1 -An important language development.html` and `Passage 2/IELTS Academic Reading Test 1.3.html` (identical test content, two different site templates/exports of the same Cambridge-style test).
2. **A New Voyage Round the World** — same two files as above (same test, Passage 3 of that test).
3. **Traditional Maori Medicine** — `Passage 1/Random Passage 1- Traditinal maori fish hooks.html` (note: filename says "fish hooks" but the file's actual passage title/content is "Traditional Maori Medicine" — the HTML content was trusted over the filename, per the workflow's instructions) and `Passage 2/Reading premium Full test 1.html`.

## Known limitations (non-blocking)

- **Katherine Mansfield** passage (source: `Passage 2/Reading premium Full test 3.html`) — this file's answer key and some question metadata are stored in heavily minified/obfuscated JavaScript that could not be reliably parsed. All 10 of its TFNG/YNNG questions (renumbered within whichever set they land in) are marked **"Answer not in source"** in the answer sheet rather than guessed. (An earlier build pass had briefly picked up a decoy numbered object from this same file — `{"1":"ONE","2":"TWO",...}`, apparently an unrelated label lookup — as if it were the answer key; this was caught by an added TFNG/YNNG-option validator and corrected before the final build.)
- **The Impact of Frozen Food** passage (source: `Passage 1/Random Passage 1A - Frozen Food.html`) — question 8 (a lone TRUE/FALSE/NOT GIVEN item embedded in an otherwise gap-fill section) has no visible rubric/instruction sentence anywhere in the source HTML near it. Its "Questions N" range heading is shown with no instruction line beneath it, rather than inventing one.
- Passage **level** (P1/P2/P3) is explicit in the source for most files (heading text, `data-part` attributes, or element ids). For a handful of single-passage files with no such signal, the level was inferred from the original question-number range (1–13 → P1, 14–26 → P2, 27–40 → P3), consistent with the standard Cambridge-style test layout — flagged here since the workflow instructions caution that this range is "a clue, not a universal rule."

## Reference style measurement

`Example/A2.pdf` and `Example/B1.pdf` were inspected with PyMuPDF. Both use a page size of ~595×842pt (A4), left/right text margins of ~51pt (~1.8cm), and an exclusively grayscale palette (near-black body text `#0C0C0C`, mid-gray headers `#8A8A8A`–`#BDBDBD`, light-gray rules `#D6D6D6`) — consistent with this workflow's Section 9 fallback style, which was used directly (A4, ~1.8cm margins, Helvetica for headings/instructions, Times-Roman for passage body and answers, grayscale only).
