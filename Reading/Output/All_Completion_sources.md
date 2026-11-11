# Source inventory — All_Completion_Set01–06.pdf

Build date: 2026-10-10
Family: Completion (Sentence Completion, Summary Completion from the passage, Note/Table/Diagram Completion, Gap Fill with/without a word bank), all sub-types, Passage level: All
Scripts: `Output/scripts/extract_completion.py` (parse + classify + structure-preserving block extraction), `aggregate_completion.py` (dedupe + group), `build_completion_pdf.py` (render)

## Scan summary

- Source folders scanned: `Passage 1/`, `Passage 2/`, `Passage 3/` — 58 HTML files, 0 failed to parse.
- Files containing at least one Completion-family blank: 46 of 58.
- Raw Completion questions found across all files (before dedup): 351, in 67 question groups.
- Unique passages after deduplication: 59 (28 at level 1, 23 at level 2, 8 at level 3).
- Unique Completion questions included across the 6 PDFs: 334, in 63 question groups.
- Questions by sub-type: Note Completion 98, Gap Fill (no word bank) 115, Summary Completion 50, Table Completion 37, Sentence Completion 34.

## How blanks were identified

Every `<input type="text">` whose `id`/`name` matches `qN` was treated as one Completion blank, grouped with its neighbours by contiguous question number + shared instruction text. This signal is template-independent (works the same across every site template in the corpus), unlike relying on specific class names. The surrounding HTML (notes with bullet points, tables, flowing sentences/summaries) was walked and converted into matching PDF structures (bulleted/indented notes, bordered tables, inline-blank paragraphs) rather than being flattened into a plain question list, so the sheet keeps the same visual shape as the source (e.g. a note completion with sub-bullets under "canning"/"freezing" renders as nested bullets; a table completion renders as an actual table).

## Duplicate passages (same passage found in more than one source file)

Only the first-seen copy of each was included; both source files are listed in the answer sheet's "Source" column for every question from that passage.

1. **An important language development** — `Passage 1/Passage 1 -An important language development.html` and `Passage 2/IELTS Academic Reading Test 1.3.html`.
2. **Children's comprehension of television advertising** — same two files as above (Passage 2 of that same test).
3. **Traditional Maori Medicine** — `Passage 1/Random Passage 1- Traditinal maori fish hooks.html` and `Passage 2/Reading premium Full test 1.html`.
4. **The History of Early Cinema** — `Passage 1/Random Passage 1G - The History of Early Cinema.html` and `Passage 1/Random Passage 1H - The History of Early Cinema.html` (two near-duplicate files for the same test).

## Known limitations (non-blocking)

- **The Burgess Shale fossils** (source: `Passage 1/Random Passage 1K - The Burgess Shale fossils.html`) — this file has two passages with very similar titles ("The Burgess Shale fossils" and "Burgess Shale") and its two Completion question groups (original Q6–9 Gap Fill, Q10–13 Table Completion) give no reliable signal (no "Reading Passage N" wording, no structural id/data-part marker) for which of the two they belong to. Rather than guess, **both groups (8 questions) were excluded** from this build. Flagging this for your review — let me know if you'd like these included under a specific passage.
- **What Lucy Taught Us** (source: `Passage 1/Random Passage 1J - What Lucy Taught Us.html`) — question 14 has no answer discoverable in the source's embedded JavaScript data; marked **"Answer not in source"** rather than guessed.
- Passage **level** (P1/P2/P3) is explicit in the source for most files. For single-passage files with no explicit level signal, the level was inferred from the original question-number range (1–13→P1, 14–26→P2, 27–40→P3), consistent with standard Cambridge-style test layout — flagged since the workflow instructions caution this is a clue, not a universal rule.

## Reference style

Same measured style as the TFNG build: A4, ~1.8cm margins, grayscale-only palette, Helvetica for headings/instructions, Times-Roman for passage body/question content — now at the larger font sizes agreed on 2026-10-10 for small-device readability (13pt body, 12.5pt question/instruction text, 20pt sheet title).
