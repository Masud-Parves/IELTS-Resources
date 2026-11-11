# Cambridge IELTS Reading by Category: build notes

Purpose: one Reading-only PDF per Cambridge book, with passages regrouped by study category (from `Cambridge_IELTS_4-21_216_Gross_Main_Categories.pdf`). Done so far: books 10-14.

## Method
The source books are scanned images with no text layer. Retyping the passages was tried first and abandoned (API content filter blocked it). The PDFs are therefore built by reordering the original pages: no text is retyped.

1. `plans/plan_C{N}.json`: passages in final order (category, title, test, passage).
2. `working/C{N}/pages_C{N}.json`: 0-based PDF page indices for each passage (passage text + questions), plus `answer_key_pages` (Reading answer-key pages).
3. `scripts/assemble_pages.py N`: builds `Output/Cambridge_{N}_Reading_By_Category.pdf`. It adds an index page, a divider page per category, each original page cropped to its content and scaled up to fill A4, then the Reading answer key pages at the end.
4. `scripts/contact_sheet.py <pdf> <out_dir> <start> <end>`: thumbnail grids used to locate pages.

## Conventions
- Category order (fixed): Environment & Nature; Psychology, Health & Human Behaviour; Technology, Transport & Engineering; Animals & Biology; Arts, Culture & Media; History & Archaeology; Education & Language; Business, Economics & Work; Science & Discovery.
- Within a category, passages are ordered by test, then passage number.
- Printed page size is kept (scaled up only); a true 16-17pt font needs OCR (Tesseract is not installed). `scripts/build_book_pdf.py` (16.5pt typeset builder) is kept for that future route.

## Known issues to review
- The index PDF does not match the actual books for C11 and C14. Original plans are saved as `plan_C11_index_original.json` and `plan_C14_index_original.json`.
  - C11: index titles "The True Cost of Food", "Language, invention and human communication" and "The history of an archaeological site" are not in the book. Several test/passage numbers are also wrong. Unmatched real passages were categorised by me: Easter Island -> History & Archaeology; Neuroaesthetics -> Arts, Culture & Media; "How the other half thinks" maths preface -> Psychology, Health & Human Behaviour.
  - C14: only 3 of 12 index entries match. Real passages were categorised by me: Alexander Henderson -> Arts, Culture & Media; Back to the future of skyscraper design -> Technology; Why companies should welcome disorder -> Business; The concept of intelligence and The power of play -> Psychology; Why zoos are good -> Animals & Biology; Marine debris -> Environment & Nature. Index categories were kept where titles matched.
- Page ranges were checked on contact sheets, not page by page.
- Answer key pages sometimes include the Listening key and the "If you score" table.

## To change something
Edit the plan JSON (order or category) or the page JSON (page ranges), then rerun `python scripts/assemble_pages.py N`.

## Passages-only text PDFs (typeset, 16.5pt)
Since 2026-10-29: `Output/Cambridge_{N}_Reading_Passages_Only.pdf` holds only the 12 passages of a book, as real text (no questions, no page images). The text comes from Windows' built-in OCR engine (Windows.Media.Ocr, en-US), so Tesseract isn't needed.

1. `scripts/passages_render.py N` renders the passage pages listed in `pages_C{N}.json` at 300 dpi to `working/C{N}/ocr/`.
2. `working/C{N}/passages_C{N}.json` lists only the pages that hold passage TEXT, plus per-passage layout options: `title_lines`, `subtitle_lines`, `labelled` (A/B/C paragraph letters), `indent` (indented paragraphs instead of spaced ones), `page_opts.regions` (figure boxes to ignore), `merge`, `as_note`, `figure`, and regex `fixes` (global and per passage).
3. OCR: `powershell -File scripts/winocr.ps1 <out_dir> <pngs...>` (Windows PowerShell 5.1) writes line and word boxes as JSON.
4. Cross-check: `scripts/passages_ocr_alt.py N` makes 450 dpi binarized copies; OCR them into `ocr/bin/json`, then `scripts/passages_ocr_diff.py N` lists every word where the two OCR passes disagree. Check doubtful lines with `scripts/strips.py N out.png page:y ...`.
5. `scripts/passages_extract.py N` rebuilds title, subtitle and paragraphs into `working/C{N}/text/T#P#.json`. It also flags lines where OCR skipped ink (dropped dashes, or words with the "Th" ligature).
6. `scripts/passages_spellcheck.py N` (needs `pip install pyspellchecker`) lists unknown words and odd spacing. It catches errors that both OCR passes made the same way. British spellings and names show up too; ignore those.
7. `scripts/build_passages_pdf.py N` typesets the PDF in Times New Roman TTF (covers ş, ₂ and other characters the built-in Times lacks).

Done: C10 (32 pages), C11 (31 pages), C12 (30 pages), C13 (31 pages), C14 (32 pages).

Run winocr.ps1 with `powershell -NoProfile -ExecutionPolicy Bypass -File ...` (scripts are blocked by default).

Extra extractor options (added for C12-C14), all in `passages_C{N}.json`:
- `single` (top level or per passage): one-column pages, read top to bottom.
- `test_offset` (top level): C12 numbers its Academic tests 5-8, so it is 4 there; the PDF shows Test 5-8.
- `relabel`: any tiny line left of the text counts as a paragraph letter, and letters are renumbered A, B, C... (faint letters get misread).
- `labels`: one letter per paragraph, `·` for none, when OCR missed letters entirely (the extractor flags a count mismatch).
- `split`: text where a new paragraph starts that the layout hides (usually at a page break). A split piece that matches `as_note` becomes a footnote.
- A "Questions n" heading under the passage cuts the page there automatically.
- `title_lines: 0` for a passage with no title (C14 Test 4 P3). The PDF then shows "(no title in the book)" in the contents.

Hard pages (C13 is a tilted photocopy):
- `scripts/ocr_quality.py N` scores each page (% of unknown lowercase words) for both OCR passes. Use it to find bad pages. A 0% score with 0 words means that pass found nothing.
- `scripts/dewarp.py N page` straightens curved or tilted lines (keeps p###_orig.png). Re-run winocr.ps1 on the page afterwards.
- `scripts/ocr_hybrid.py N page` (needs `pip install rapidocr-onnxruntime`): re-reads each Windows OCR word box with RapidOCR. The Windows word is kept when the dictionary knows it, otherwise RapidOCR's reading is used. Use it on pages above about 2% unknown. It can drop a doubled letter, but the spell check flags those.
- `scripts/use_alt_ocr.py N page`: use the binarized pass as the main OCR when it is clearly better.
- C13 p88 needed all three plus fixes: one whole line was missing from OCR.

Proofreading checks that caught real errors in C12-C14: the spell check's `caps:` list (unknown capitalised words mid-sentence, e.g. "Inotto"); a full stop before a lowercase word (C13 reads commas as full stops: a global fix); a comma before a sentence-starting word ("true, In the"); and short odd tokens ("I.JK", "0K", "'l").

## List of Headings sheet (typeset, 16.5pt)
Since 2026-10-31: `Output/Cambridge_10-14_List_of_Headings.pdf` (46 pages) holds every List of Headings set in books 10-14: 11 passages, 73 questions. Each passage is followed by its question set, and one Answer Sheet at the end gives the official answer and a one-line reason for each question. Question numbers stay as in the book.

1. `working/headings/sets.json`: book, test, passage and question page of each set, plus overrides for noisy pages (`drop`, `instructions`, `questions`, `fixes`).
2. `scripts/headings_extract.py` reads the Windows OCR JSON into `working/headings/questions.json`. Roman numerals are assigned by position, because OCR drops some of them; it prints a note wherever OCR read something different.
3. `working/headings/answers.json`: official answers, the reasons, and text `fixes` applied only to this PDF.
4. `scripts/build_headings_pdf.py` builds the PDF. It stops if a question has no answer, an answer isn't on the list, or a heading is used twice. It prints a warning if a reason won't fit on one line.

Finding the sets: read the answer keys by eye and look for Roman-numeral answers. OCR can't read the numerals in the keys (`scripts/headings_render_keys.py` renders the pages), and searching the OCR text for "List of Headings" gave the same 11 sets.

The C11 scan has a student's handwritten answers on the question pages (they match the key), and these OCR as noise.

OCR errors found in the shared text JSON and fixed only for this PDF (still in the Passages-Only PDFs): C11 T2P2 "Daniken" (Däniken); C11 T4P3 "Other inventions the wheel" (dash dropped); C12 T2P2 "white a magnificent" (while); C13 T1P2 missing closing quote after "social situations,", "to wander In fact", "to fester' For"; C14 T2P3 "used elsewhere," (full stop).

## TRUE/FALSE/NOT GIVEN and YES/NO/NOT GIVEN sheets (typeset, 16.5pt)
Since 2026-11-03: `Output/Cambridge_{N}_TFNG_YNNG.pdf`, one per book (C10: 10 passages, 51 questions; C11: 9, 44; C12: 8, 36; C13: 6, 32; C14: 9, 45; 208 in all). The layout matches the List of Headings sheet. Passages without paragraph letters get small gray ¶ numbers, and the reasons refer to those ("Para 3"). The title page says these numbers are not in the book.

1. `scripts/tfng_keys.py` reads the OCR'd answer keys into `working/tfng/keys.json`. OCR missed many C12 answers, so C12 was corrected by eye (marked "note" in the file). Check every book against the key pages.
2. `scripts/tfng_extract.py [N]` finds each set's "Questions a–b" heading. Faint C13 scans read it as "Cuestions", and C14 dropped the numbers; the fallback is the "Do the following statements agree" line. It writes `working/tfng/questions_C{N}.json`. Instructions and the TRUE/FALSE box are rebuilt from the book's own first line ("information given in" / "claims of the writer" / "views of the writer").
3. `working/tfng/overrides.json`: global statement fixes plus typed statements where OCR failed. C11 needs these because a student's handwritten answers merge into the words; C13 needs them for missed question numbers. The file also holds `defs` for C11 Test 2 P3, whose YES/NO set prints "if there is no information on this" for NOT GIVEN.
4. `working/tfng/answers_C{N}.json`: one reason per question, passage `fixes` and `join` (ends of paragraphs that were wrongly split). Everything is checked against crops of the scans.
5. `scripts/build_sheet_pdf.py tfng N` builds one book (the builder was `build_tfng_pdf.py` until it was generalised for Matching Information). `scripts/build_sheet_pdf.py tfng 10 11 12 13 14` builds the merged `Output/Cambridge_10-14_TFNG_YNNG.pdf` (173 pages): one contents page, continuous page numbers, book labels on each passage, and one answer sheet at the end grouped by book. After changing reasons or fixes, rebuild both the single-book files and the merged one. The builder stops if questions, reasons and key don't match. It warns when a reason won't fit on one line.

Write each reason with the official answer showing: one reason written from memory (C10 T3 Q7) had argued the wrong answer.

More OCR errors fixed only in these PDFs (they are still in the Passages-Only PDFs): C10 "1 6th", "El Nifio", "I-degree", "controversial, For", missing quotes in T3P3/T4P1; C11 "109" (10⁹), "1800" (180°), "tying" (lying), "gain md", "Imown", "silk Cowers" (growers), "silk yam" (yarn), "admirable." / "evolution." (colons); C12 dropped dashes (cork, stamps), "1 8th", "sika deer." (colon); C13 "1 840s", "1 872", "Vyas" (was), and in T1P3 a lost quote plus a split last paragraph; C14 "1 1 January", plus commas for full stops in T2P1, T3P1, T3P3 and T4P1.

## Matching Information sheets ("Which paragraph contains…")
Since 2026-11-03: `Output/Cambridge_{N}_Matching_Information.pdf` per book (C10: 3 passages, 13 questions; C11: 2, 11; C12: 3, 13; C13: 4, 17; C14: 5, 24) and the merged `Cambridge_10-14_Matching_Information.pdf` (17 passages, 78 questions, 66 pages). Same layout and builder: `python scripts/build_sheet_pdf.py mi N...`.

1. Sets found by searching the OCR for "contains the following information". Then every test's questions 1-40 were checked to belong to a recognised group. That check found C12 Test 6 P3 (Q37-40), whose instruction line OCR garbled.
2. `working/mi/keys.json`: OCR can't read single letters in the keys, so all answers were read by eye from the key pages. The 13 letters the OCR did read all agree.
3. `scripts/mi_extract.py` writes `working/mi/questions_C{N}.json`. The instructions are kept as printed, including the book's own inconsistencies: C12 Test 7 says "eight sections" then "Which paragraph", and C13 Test 4 says "seven paragraphs" then "Which section". `working/mi/overrides.json` holds the typed C12 Test 6 sets plus global fixes.
4. `working/mi/answers_C{N}.json`: reasons and passage fixes (C11 "let done", "0.5 oc", missing quotes, "(in mathematics]"; C14 "back,' After", "Cambridge,"). The builder checks that every answer is one of the passage's paragraph letters.

## Matching Sentence Endings sheets
Since 2026-11-03: `Output/Cambridge_{N}_Sentence_Endings.pdf` for C10-C13 (C14 has no such sets) and the merged `Cambridge_10-14_Sentence_Endings.pdf` (8 passages, 34 questions, 35 pages). Build with `python scripts/build_sheet_pdf.py me N...`; C14 needs an empty `working/me/answers_C14.json` (`[]`) so the merged build runs.

- Sets: C10 T1P3, T4P3; C11 T3P2, T4P2; C12 T3P3 (Test 7); C13 T1P3, T2P3 (heading OCR'd as "Questions 3E40"), T4P2. Answers were read by eye from the key pages; the 3 letters the OCR read agree.
- `scripts/me_extract.py` writes `working/me/questions_C{N}.json` with `statements` (sentence beginnings), `options` (the lettered endings) and `options_title` (C13 T1P3's box is titled "List of Ideas"). `working/me/overrides.json` supplies endings C11 T4P2 A-B and C13 T1P3 Q34-36, which OCR missed or merged.
- The builder draws the endings box and shows the completed sentence on the answer sheet. Reasons always say "Para D" / "Para 4", because the answer letter here is an ending, not a paragraph.

When generating code through a bash heredoc, `\b` and `\1` can turn into control characters (this happened twice). Edit Python files with the Edit tool, or check them for characters below 0x20 afterwards.

Known OCR traps: the "Th" ligature is read as "Ih" (sometimes with a quote mark that isn't there, or the word is dropped); dashes get dropped; OCR can merge a left-column line with the right-column line beside it (the extractor splits these). Italics are not kept.
- C11 scan only: an irLanguage.com watermark (filtered by the top-level `drop` regex; keep it narrow, because a plain `Languag` match deletes real lines containing "language"), and worse ligature misreads (fo→fb, ti→å/ö, tr→ü•, fi/fl dropped). Global fixes run AFTER per-passage fixes, in list order.
- Write config JSON from Python, not a bash heredoc: the shell collapses `\` so regex escapes break.
