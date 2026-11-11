# IELTS Reading Practice Sheet Builder — AI Operating Instructions

## Mission

Create accurate, topic-wise **question-family practice sheets** for IELTS Reading as PDFs, using only the user's local HTML source files and the reference PDFs. Here, “topic-wise” means **question-type-wise**: one sheet focuses on one question family or selected sub-type (for example, Matching Headings only). **Do not add a passage-subject filter** such as Environment, History, or Technology.

Read this entire file before acting. Follow the workflow in order. The interaction rules below apply to every sheet, including the second and all later sheets in the same conversation.

---

## 1. Main objectives

For each requested sheet:

1. Ask the user for fresh setup choices before processing any files.
2. Confirm that the required source folders and files are accessible.
3. Find all eligible passages and question groups matching the selected family, passage level, and sub-types.
4. Use only original passage text, questions, instructions, diagrams, and answers from the user's files. Never invent or silently rewrite them.
5. Keep each passage together with its own question group(s): passage text, immediately followed by that passage's selected questions, then the next passage, and so on. Put the answer sheet at the very end of the PDF, after every passage+question pair. **Do not** group all passages first and all questions afterward — that layout forces back-and-forth page flipping during practice and must be avoided. See Section 6, Step 6 for the exact required structure.
6. Match the reference PDFs as closely as can be measured.
7. Verify the finished PDF, report limitations honestly, and update the progress log.
8. Ask the complete setup questions again before beginning the next sheet.

## 2. Expected folder layout

All folders are expected to be under the same root folder as this file:

```text
(root)
├── IELTS_Reading_Sheet_Builder.md
├── Example/                         # Reference PDFs, such as A2.pdf and B1.pdf
├── Passage 1/                       # HTML source files
├── Passage 2/                       # HTML source files
├── Passage 3/                       # HTML source files
└── Output/                          # Create if missing; PDFs, logs, and scripts go here
```

Important source-file facts:

- An HTML file may contain only one passage or a complete test with Passages 1, 2, and 3.
- A file stored in `Passage 1/` may still contain all three passages. Always identify the passage's actual heading and level inside the HTML; do not trust the folder name alone.
- The folders or reference PDFs may be unavailable in a particular session. **Check access before processing.** If a required folder or file cannot be accessed, tell the user exactly what is missing and ask them to attach or make the files accessible. Never claim to have scanned files that were not accessible.
- Create `Output/` if the source root is accessible and the folder is missing. Do not create substitute source content.

---

## 3. Question families and classification

A sheet must focus on exactly **one family**. The user may choose all sub-types in that family or only selected sub-types.

| # | Family code | Family | Included question types |
|---|---|---|---|
| 1 | `TFNG` | **Identifying Information / Views** | True / False / Not Given; Yes / No / Not Given |
| 2 | `Matching` | **Matching** | Matching Headings (List of Headings); Matching Information (which paragraph contains…); Matching Features (people, dates, places, etc.); Matching Sentence Endings; Summary Completion with a box/list of options (A–J, etc.) |
| 3 | `Completion` | **Completion** | Gap fill without a clue/word bank; Gap fill with a clue/word bank; Sentence Completion; Summary Completion using words from the passage; Note, Table, Flow-chart, and Diagram Label Completion |
| 4 | `MCQ` | **Multiple Choice** | Multiple choice with one answer; choose TWO or THREE answers |
| 5 | `ShortAnswer` | **Short Answer** | Direct short-answer questions, usually with a word limit such as “NO MORE THAN … WORDS” |

### Classification rules

- **Summary Completion with a list/box of options belongs to Matching.** Summary Completion where answers must be taken from the passage belongs to Completion.
- Classify a question group using its original instruction text, answer format, and structure together. Do not rely on one keyword alone.
- Common signals include:
  - TFNG: “TRUE if the statement agrees with the information…”
  - Yes/No/Not Given: “YES if the statement agrees with the views/claims of the writer…”
  - Matching Headings: “List of Headings” or “Choose the correct heading for each paragraph.”
  - Matching Information: “Which paragraph contains the following information?”
  - Matching Features: match statements to a person, date, place, or other feature.
  - Matching Sentence Endings: complete each sentence with the correct ending from a list.
  - Summary with options: complete the summary using a list/box of words or options.
  - Completion: complete notes, tables, flow charts, diagrams, sentences, or a summary using words from the passage or a word bank.
  - MCQ: “Choose the correct letter…” or “Choose TWO/THREE letters…”
  - Short Answer: answer direct questions with a stated word limit, rather than filling blanks in a text/table.
- If the question type cannot be determined confidently, mark it **Unclear — user decision required**. Report the source file, passage level, question numbers, original instructions, and reason for uncertainty. Do not include the unclear group until the user resolves it if the decision affects inclusion.
- Do not classify a passage as a match merely because it contains a relevant subject. Eligibility depends on its **question family/sub-type**, not the passage's subject.

---

## 4. Mandatory interaction rules — apply to every sheet

These rules override any temptation to reuse previous choices or start work immediately.

1. **Ask before every new sheet.** Even if a sheet was just completed, ask the full setup questions again before starting another.
2. Ask all four setup questions together in one concise message. Use the numbered family list from Section 3.
3. Let the user answer in shorthand, for example: `2; Passage 3; Matching Headings only; sets of 10`.
4. If one or more required choices are missing or ambiguous, ask only about those missing/ambiguous choices. Wait for the answer before proceeding.
5. Do not assume “next topic,” “continue,” or “make another one” means the user wants the same settings. Reuse a setting only if the user explicitly says to reuse that specific setting. Ask about any remaining required choices.
6. Do not add a passage-subject filter. This workflow is question-family-wise only.
7. Do not create a sample PDF, select a family on the user's behalf, or silently apply an unstated preference.
8. Before building, inspect `Output/sheets_log.md` if it exists. If a sheet with the same family, level, and sub-types may already exist, show the relevant file and ask whether to rebuild it or include only new eligible passages. If the log is missing, report that fact and create it after a successful build; do not pretend that previous work has been checked.
9. Never overwrite an existing PDF, script, or log entry without following the relevant rules in Sections 8 and 10.
10. After delivery, ask the complete four setup questions again for the next sheet. Do not ask only which family comes next.

### Required setup message

When the user asks to start a sheet or create the next sheet, ask the following and wait:

1. **Which question family?**
   1. Identifying Information / Views (True / False / Not Given; Yes / No / Not Given)
   2. Matching
   3. Completion
   4. Multiple Choice
   5. Short Answer
2. **Which passage level?** Passage 1 / Passage 2 / Passage 3 / All.
3. **Which sub-types?** All sub-types in the selected family, or only specified sub-types (for example, Matching Headings only).
4. **How should the sheet be split?** One PDF containing all eligible passages, or multiple PDFs with how many passages per set? If the user chooses multiple sets but gives no number, use 10 passages per set. If the user chooses one PDF, do not split it.

Do not scan files or generate a PDF until the required choices are clear.

---

## 5. Workflow — follow in order

### Step 1 — Confirm choices and inspect existing work

After the user has answered all required setup questions:

1. Record the selected family, level, sub-types, and split preference for this build only.
2. Check `Output/sheets_log.md`, if accessible.
3. If a potentially matching sheet already exists, explain which file matches and ask whether to **rebuild** or **include only new eligible passages**. Wait for the answer.
4. If the log is missing or inaccessible, state that limitation. Do not claim that existing outputs have been fully checked.

### Step 2 — Confirm source access and study the reference PDFs

1. Confirm that the source root, chosen `Passage` folder(s), and `Example` folder are accessible.
2. Inspect `Example/A2.pdf` and `Example/B1.pdf` when present. If one is missing, use the available reference and report the missing one. If neither is available, use the fallback style in Section 9 and state that the reference style could not be measured.
3. Measure, rather than guess:
   - Page size and margins
   - Font family and font size for title, passage title, body, instructions, questions, and answer sheet
   - Line spacing and paragraph spacing
   - Paragraph-letter style and placement
   - Answer-sheet layout
   - Section order, headers, footers, and page numbering
4. Use PyMuPDF (`fitz`) to inspect PDF text spans and render pages when possible. Measurements inferred from a PDF may not reveal every original design setting; label uncertain measurements as estimates.
5. Record measured values and any limitations for the final report.

### Step 3 — Inventory and parse the HTML files

For each HTML file in the selected level folder(s):

1. Record its path and filename in an inventory.
2. Parse with BeautifulSoup and a suitable HTML parser such as `lxml`.
3. Identify each passage using its actual heading (for example, “READING PASSAGE 1/2/3”), passage title, page structure, and question ranges. Typical ranges such as 1–13, 14–26, and 27–40 are clues only, not universal rules.
4. Extract and record:
   - Source filename/path
   - Actual passage level
   - Original passage title
   - Complete passage text, including paragraph labels (A, B, C, etc.)
   - Any images, diagrams, tables, captions, or labels needed to understand the passage/questions
   - Each question group, original instructions, original question numbers, options, and question type
   - Answer key and its source location, when available
5. Search for answers in visible text, hidden HTML blocks, data attributes, scripts or embedded structures, and separate answer sections/files where available. Do not assume an answer is present just because a question is present.
6. Preserve the relationship between a passage, its question groups, and its answer key. Do not accidentally attach answers from another passage or test.
7. If parsing fails or a file is unreadable, record the filename and the problem. Do not silently skip it.

### Step 4 — Classify, filter, and deduplicate

1. Keep only passages at the selected level (or all levels, if the user chose All) that contain at least one question group matching the chosen family and selected sub-types.
2. If only a sub-type is selected, include only the matching question groups from eligible passages. Do not include unrelated groups just because they belong to the same passage.
3. A passage can qualify even if only one of its question groups matches. Include the passage once, and include only the eligible question group(s) in the question section.
4. Detect likely duplicates using title plus the first 200 characters of normalized passage text, then compare further text when needed. Do not remove passages solely because their titles are similar. Keep one confirmed duplicate and list all duplicate source paths in the report.
5. If the same passage exists in different levels or has materially different questions/answers, inspect carefully before deciding whether it is a duplicate.
6. Before building, provide a concise **pre-build inventory**:
   - Number of files scanned and any files unavailable/failed
   - Number of eligible unique passages
   - Number of matching question groups and questions
   - Duplicates detected
   - Missing answer keys, diagrams, or ambiguous question groups
   - Planned output file(s) and split count
7. If an unresolved ambiguity could change what gets included or how an answer is matched, stop and ask the user. Otherwise, proceed and document non-blocking issues.
8. If no eligible passages are found, do not create an empty or fabricated sheet. Report the search result and ask whether the user wants to change the family, level, or sub-types.

### Step 5 — Plan the output and file names

1. If the user requested one PDF, make one PDF containing all eligible unique passages. If the user requested sets, divide the eligible passages into sets of the selected size; use 10 only when the user chose sets but did not specify a number.
2. Keep a passage and all its selected question groups together in the same set. Do not split a single passage's selected question group across different sets unless technically unavoidable; if unavoidable, explain it and keep question-answer mapping clear.
3. Use filenames such as:

```text
Output/P1_TFNG_Set01.pdf
Output/P1_TFNG_Set02.pdf
Output/P2_Matching_Set01.pdf
Output/All_Completion_Set01.pdf
```

4. Codes: `P1`, `P2`, `P3`, or `All` for level; `TFNG`, `Matching`, `Completion`, `MCQ`, or `ShortAnswer` for family.
5. Add a short, safe sub-type suffix when needed to distinguish files, for example `P2_Matching_Headings_Set01.pdf`. Keep names consistent and readable.
6. If the target filename already exists, never overwrite it without explicit permission. Ask first or create a new sequential set number if this does not conflict with the user's request or existing log. Record the chosen behavior.

### Step 6 — Build the PDF

Each PDF must use this structure. **This ordering is mandatory — do not bunch all passages together followed by all questions; that layout makes the sheet unusable for practice (the reader has to flip back and forth between a passage and its questions).**

1. **Title block:** Clearly state IELTS Reading Practice, selected question family/sub-type, selected passage level, set number (if applicable), number of passages, and number of questions.
2. **Passage + Questions pairs, repeated for every passage in the set, in order:**
   a. The passage: start on a new page when practical, with a local sheet label such as “Passage 1” and its original title, and its paragraph letters retained exactly.
   b. Immediately after that same passage (no other passage in between): that passage's selected question group(s) — a heading such as “Questions 1–6” or “Questions for Passage 1: [original title]”, the exact original instructions, and all selected question text/options/labels/diagrams.
   c. Then move on to the next passage and repeat a–b for it, and so on, until every passage in the set has been covered.
   - Example for a 2-passage set: Passage 1 (“History of Glass”) → its questions → Passage 2 (“Globalization”) → its questions → … → Answer Sheet.
3. **Answer Sheet:** Put it at the very end of the PDF, after every passage+question pair, beginning on a new page. Use the reference PDF layout where possible.

#### Question numbering and answer mapping

- Renumber included questions continuously throughout each PDF (1, 2, 3, …) so every answer has one unambiguous number.
- Preserve original numbering information in source notes or a mapping record. In the answer sheet, identify the source passage/file and original question range, for example: `Passage 3 — Cambridge 12 Test 1.html — original Q1–7`.
- For questions with multiple required answers (such as “Choose TWO letters”), preserve the original requirement and record the required number of answer components.
- Keep option letters and paragraph labels exactly as in the source. Do not reorder options.
- The answer sheet must correspond to the **renumbered questions in the finished PDF**, not merely repeat the original HTML numbering.

#### Text and image handling

- Do not paraphrase, correct grammar, simplify, or modernize source content. Only remove HTML markup and normalize formatting where this does not alter visible wording.
- Decode HTML entities correctly (for example, display `&amp;` as `&` where that is the source's rendered text). Avoid accidental loss of punctuation, apostrophes, symbols, or special characters.
- Preserve useful diagrams, tables, maps, labels, captions, and image-dependent information. If an image cannot be extracted or reproduced clearly, report it and ask for guidance if the missing visual makes the question unsolvable.
- Do not add decorative images, hints, explanations, or teaching notes that are not in the source.

### Step 7 — Verify and quality-check the PDF

Do not deliver the PDF until these checks have been completed as far as the available tools allow:

#### Content accuracy

- The number of unique passages in the output equals the number planned after filtering/deduplication.
- Every included question belongs to the chosen family/sub-type and level.
- Every passage and question is present in the correct order.
- Passage text, question wording, answer options, paragraph letters, and instructions match the source's rendered text.
- Word limits and instructions (for example, “NO MORE THAN TWO WORDS”) are copied exactly.
- The answer sheet has one entry for every included question, except that a multi-part question may require multiple answer components under one question number.
- Every answer is linked to the correct question. If an answer is not found in the source, write **“Answer not in source”** and list it in the report. Never invent an answer. If the user explicitly asks for an AI-solved missing answer, mark it **“AI answer — not verified”** and keep it distinct from source-provided answers.

#### Layout and rendering

- Render at least 3–4 representative pages to images, including a passage page, a question page, and an answer-sheet page. If the PDF is shorter, inspect every page.
- Visually inspect margins, font consistency, spacing, page breaks, headers/footers, diagrams, tables, and answer alignment.
- No text, question, table, or diagram should be clipped, overlapped, unreadably small, or outside the page.
- Avoid splitting a question and its answer options across pages where possible. Keep passage titles with the first paragraph; keep question instructions with the first question in that group; repeat table headers when a table continues across pages.
- A passage may span multiple pages if needed. Do not shrink the font excessively merely to force content onto one page.
- Use only black text, white background, and gray tones as specified in Section 9.
- If visual inspection tools are unavailable, say that layout was not visually verified. Do not claim it was inspected.

#### Final consistency checks

- Count passages and questions from the final PDF or build data, not from memory.
- Compare the final output file list with the planned file list.
- Confirm that every output file exists and is not empty.
- Confirm that the progress log is updated only after the corresponding output has been successfully created and checked.

### Step 8 — Update the progress log

Maintain `Output/sheets_log.md`. After each successful build, append a row with at least:

| Date | File | Family | Sub-types | Level | Passages | Questions | Source files / notes | QA status |
|---|---|---|---|---|---:|---:|---|---|

- Record one row per PDF file.
- Include the source filenames or a reference to a source inventory, duplicate notes, missing answers, and any limitations.
- Use the actual current date available in the working environment. If the date cannot be determined, do not invent one; use `Date unavailable`.
- Do not erase old entries. Correct an old entry only when a real correction is necessary, and explain the correction in the report.
- Do not log a build as successful if the PDF was not created or verification failed. Use a clear status such as `Created — QA passed`, `Created — QA partial`, or `Failed`.

### Step 9 — Report the result and ask about the next sheet

Give a concise but informative report containing:

1. **Files created:** exact filenames and locations.
2. **Counts:** number of passages and questions in each PDF.
3. **Selection summary:** family, sub-types, level, and split size used.
4. **Source scan:** number of files scanned, files skipped/failed and reasons, duplicates removed.
5. **Answer-key status:** answers missing from source and any AI answers explicitly requested by the user.
6. **Reference design:** measured style values and which values had to use fallbacks.
7. **Quality assurance:** checks completed, whether rendered pages were visually inspected, and any remaining limitations.
8. **Progress log:** whether `Output/sheets_log.md` was updated successfully.

Then ask the four setup questions from Section 4 again, including the full numbered family list, level, sub-types, and split preference. Wait for the user's answers before doing any work on the next sheet.

---

## 6. Non-negotiable source-integrity rules

1. **Never invent questions.** Use only questions found in the user's source files.
2. **Never invent passage content.** Do not add passages from websites, books, memory, or any other external source.
3. **Never rewrite source wording.** Preserve passage text, questions, instructions, options, and word limits. Only clean markup and presentation without changing the rendered words.
4. **Never invent answers.** If an answer is absent from the source, write `Answer not in source` unless the user explicitly asks for AI-solved answers; those must be labelled `AI answer — not verified`.
5. **Never guess about ambiguity.** Ask the user when uncertainty could affect selection, passage/question pairing, or answer mapping.
6. **Never pretend to access unavailable files.** Clearly identify missing folders/files and request access.
7. **Never overwrite existing output without permission.**
8. **Preserve necessary visual material.** Keep diagrams, tables, figures, labels, and images that are required to answer a question.
9. **Keep family-only organization.** Do not add a passage-subject filter or group sheets by subject.
10. **Separate facts from estimates.** Clearly identify measurements or classifications that are uncertain rather than presenting them as verified.

---

## 7. Output naming rules

Use the following examples and conventions:

```text
Output/P1_TFNG_Set01.pdf
Output/P1_TFNG_Set02.pdf
Output/P2_Matching_Set01.pdf
Output/P2_Matching_Headings_Set01.pdf
Output/All_Completion_Set01.pdf
Output/P3_MCQ_Set01.pdf
Output/All_ShortAnswer_Set01.pdf
```

- Level codes: `P1`, `P2`, `P3`, `All`.
- Family codes: `TFNG`, `Matching`, `Completion`, `MCQ`, `ShortAnswer`.
- Use a sub-type suffix only when needed to distinguish a focused sheet from other sheets in the same family/level.
- Use zero-padded set numbers (`Set01`, `Set02`, etc.).
- Check for existing filenames and the progress log before choosing a set number.

---

## 8. Progress log format

File: `Output/sheets_log.md`

Use this table and keep it updated after successful builds:

| Date | File | Family | Sub-types | Level | Passages | Questions | Source files / notes | QA status |
|---|---|---|---|---|---:|---:|---|---|

If a more detailed source inventory is needed, save it in `Output/` using a filename linked to the relevant PDF, for example `P2_Matching_Headings_Set01_sources.md`. Do not create extra reports unless they materially help trace sources, duplicates, or unresolved issues.

---

## 9. PDF style rules

First use the style measured from `Example/A2.pdf` and `Example/B1.pdf`. Do not invent measurements. If a property cannot be measured, use these fallbacks and mention them in the report.

Fonts must stay comfortably readable on a small device (phone-sized PDF viewer), not just on a full desktop page — prefer the larger end of any reasonable range rather than the smaller end.

| Element | Fallback |
|---|---|
| Page | A4, margins 1.8–2 cm |
| Body font | Readable serif or clean sans-serif, **13 pt**, line spacing about 1.4 |
| Sheet title | 20 pt bold |
| Passage title | 16 pt bold |
| Instructions | 12.5 pt italic or bold, matching source/reference style |
| Questions | 12.5 pt |
| Answer sheet | 12 pt; clear table or numbered list with question number and answer |
| Header | Small gray sheet name on every page |
| Footer | Page number at the bottom |

Colours: black text, white background, and gray only (`#666666` to `#DDDDDD`) for lines, borders, light shading, and question-number boxes. No other colours.

Prioritize readability and source fidelity over decorative design. Use consistent styles, clear hierarchy, adequate whitespace, and stable numbering. Avoid unnecessary blank pages.

---

## 10. Tools and reusable scripts

Use Python when available. Install missing packages only if installation is supported and permitted in the environment:

```bash
pip install beautifulsoup4 lxml pymupdf reportlab
```

- `beautifulsoup4` + `lxml`: parse HTML source files.
- `pymupdf` (`fitz`): inspect PDF text spans, measure available font information, and render pages for visual checks.
- `reportlab`: generate PDFs. HTML-to-PDF via a suitable renderer may be used if it better preserves layout, provided the final PDF is verified.

Keep reusable build scripts in `Output/scripts/` when possible. Before changing or replacing an existing script, inspect it and do not overwrite user work without permission. Keep the script configurable for family, sub-types, passage level, split size, and output path so the next sheet can be built consistently.

If a required package or tool is unavailable, explain the limitation and use a reliable available alternative only if it preserves content accurately. Do not claim a tool was used if it was not.

---

## 11. Final operating checklist

Before each build:

- [ ] Asked all four setup questions and received clear choices.
- [ ] Checked the progress log and resolved any existing-sheet decision.
- [ ] Confirmed access to source and reference files.
- [ ] Scanned, classified, filtered, and deduplicated source passages.
- [ ] Reported the pre-build inventory and resolved blocking ambiguities.

Before delivery:

- [ ] Included only the selected family/sub-types and level.
- [ ] Preserved source wording, instructions, options, paragraph labels, and needed visuals.
- [ ] Renumbered questions consistently and mapped answers correctly.
- [ ] Marked answers missing from the source rather than inventing them.
- [ ] Checked passage/question/answer counts.
- [ ] Checked page rendering and layout, or clearly disclosed if visual checking was unavailable.
- [ ] Confirmed output files exist and are non-empty.
- [ ] Updated the progress log with the correct QA status.
- [ ] Reported files, counts, sources, duplicates, missing answers, style measurements, and limitations.
- [ ] Asked the complete setup questions again for the next sheet and waited.
