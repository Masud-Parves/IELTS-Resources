# Source inventory — All_Matching_Set01–04.pdf

Build date: 2026-10-10
Family: Matching, all sub-types (Matching Headings, Matching Information, Matching Features, Matching Sentence Endings, Summary Completion with a word/option bank), Passage level: All
Scripts: `Output/scripts/extract_matching.py` (parse + classify + bank/legend extraction), `js_obj.py` (small JS-object-literal parser for the data-driven CD-IELTS engine), `aggregate_matching.py` (dedupe + group), `build_matching_pdf.py` (render)

## Scan summary

- Source folders scanned: `Passage 1/`, `Passage 2/`, `Passage 3/` — 58 HTML files, 0 failed to parse.
- Files containing at least one Matching-family question group: 28 of 58.
- Raw Matching questions found across all files (before dedup): 252, in 49 question groups.
- Unique passages after deduplication: 33 (5 at level 1, 19 at level 2, 9 at level 3).
- Unique Matching questions included across the 4 PDFs: 231, in 45 question groups.
- Questions by sub-type: Matching Features 72, Matching Information 71, Matching Headings 60, Summary Completion (options) 23, Matching Sentence Endings 5.

## How questions were identified

This corpus uses several different HTML templates for Matching-type questions, all handled:

1. **Static `<select>` dropdown** (the large majority — ~230 of the raw 252 questions): a `<select>` whose non-placeholder `<option>` values are either bare roman numerals (`i`–`xii`) or single letters (`A`–`L`). The question's own number comes from the select's `id`/`name`/`data-question` attribute. The sub-type is classified from the nearest preceding rubric sentence ("Choose the correct heading…", "Which paragraph contains…", "Match each statement with the correct person…", "…correct ending…"). The heading/people/ending bank is then located by walking forward in document order from that rubric (handles banks in a named `.headings-box`/`.features-box` div, banks as a run of sibling `<p>` lines, and banks packed into a single `<p>` separated only by `<br>` tags).
2. **Data-driven "matrix" engine** (`CD IELTS Reading Test 9.3.html`, `Reading Premium Full test 22.html`): these files build the question grid from a `matrixDefs` JavaScript object (parsed with a small hand-written JS-literal parser rather than guessed at) rather than static HTML; the original instruction sentence was still recovered from the static `<p class="instruction">` that precedes the (JS-filled) empty container, so no wording was invented.
3. **Drag-and-drop Matching Headings** (`Reading Premium Full test 22.html`): a `.headings-box` of `.mh-heading-card[data-code]` elements plus `.mh-drop-slot[data-question]` markers placed against each lettered paragraph.
4. **Drag-and-drop word-bank Summary Completion** (`Random Passage 3- Science and flimmaking.html`): the same drag widget reused for a lettered word bank dropped into blanks inside a running summary paragraph — rendered like a Completion-style paragraph with inline blanks, not a per-paragraph heading list.

Answers were read from each file's own `correctAnswers` JavaScript object (same mechanism as the earlier TFNG/Completion builds), validated against each question's actual valid option set before being accepted (rejects decoy objects with the right question numbers but unrelated values).

## Duplicate passages (same passage found in more than one source file)

Only the first-seen copy of each was included; every source file is listed in the answer sheet's "Source" column for every question from that passage.

1. **Children's comprehension of television advertising** — `Passage 1/Passage 1 -An important language development.html` and `Passage 2/IELTS Academic Reading Test 1.3.html`.
2. **A New Voyage Round the World** — same two files as above (a different passage of that same test).
3. **The History of Early Cinema** — `Passage 1/Random Passage 1G - The History of Early Cinema.html` and `Passage 1/Random Passage 1H - The History of Early Cinema.html` (two near-duplicate files for the same test).
4. **The Fascinating World of Attine Ants** — `Passage 2/Random Passage 2 - Attine Ants.html` and `Passage 2/Random Passage 2I - Attine Ants.html` (identical Q14–19 Matching Information group in both).

## Known limitations (non-blocking)

- **"The fascinating world of attine ants"** (`Passage 2/Random Passage 2E - The facinating world of attine ants.html`) was kept as a *separate* passage entry rather than merged into the Attine Ants duplicate group above: its title capitalization and paragraph text differ enough from the other two files that the automatic duplicate check did not treat it as a confirmed match, and it also carries a longer Q14–24 question range (11 questions vs. 6). It may in fact be the same underlying passage in an extended form — flagging for your review rather than guessing.
- Two files have `<select>`-based question dropdowns whose options are `TRUE`/`FALSE`/`NOT GIVEN`, not Matching codes — i.e. they implement **TFNG via a dropdown instead of radio buttons** (`Passage 2/Random Passage 2J – The Conquest of Malaria in Italy.html`, and the select-driven TFNG portion is template boilerplate only in `Passage 2/Reading premium Full test 5.html`, which has no real Matching content). These were correctly excluded from this Matching build. Note for your awareness: because the earlier TFNG sheets only scanned `<input type="radio">` elements, this file's TFNG questions were likely **not** included in the earlier `All_TFNG_Set01–05.pdf` build. Let me know if you'd like those sheets revisited.
- Passage **level** (P1/P2/P3) is explicit in the source for most files. Where a group's own instruction text had no "Reading Passage N" wording and no structural data-part marker (chiefly the data-driven "matrix" engine files), the level was inferred from the fixed IELTS Academic question-number boundaries (1–13→P1, 14–26→P2, 27–40→P3), consistent with this corpus's own documented convention for that engine.
- All 231 included questions have a source-verified answer — none had to be marked "Answer not in source" for this build.

## Reference style

Same measured style as the TFNG/Completion builds: A4, ~1.8cm margins, grayscale-only palette, Helvetica for headings/instructions, Times-Roman for passage body/question content, 13pt body / 12.5pt question text / 20pt sheet title. The heading/option bank (List of Headings, List of People, List of Researchers, Word Bank, etc.) is rendered as a bordered two-column reference table directly above its question block, since these questions are unsolvable without it.
