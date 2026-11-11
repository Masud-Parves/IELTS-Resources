# Source inventory — All_MCQ_Set01–03.pdf

Build date: 2026-10-10
Family: Multiple Choice, both sub-types combined (single-answer "Choose the correct letter"; "Choose TWO/THREE" multi-select), Passage level: All
Scripts: `Output/scripts/extract_mcq.py` (parse + classify + distinguish true MCQ from look-alike question types), `js_obj.py` (JS-object parser, reused from the Matching build), `aggregate_mcq.py` (dedupe + group), `build_mcq_pdf.py` (render)

## Scan summary

- Source folders scanned: `Passage 1/`, `Passage 2/`, `Passage 3/` — 58 HTML files, 0 failed to parse.
- Files containing at least one true MCQ group: 27 of 58.
- Raw MCQ questions found across all files (before dedup): 117, in 34 question groups.
- Unique passages after deduplication: 28 (5 at level 1, 7 at level 2, 16 at level 3).
- Unique MCQ questions included across the 3 PDFs: 107, in 31 question groups.
- Questions by sub-type: single-answer 91, choose TWO/THREE 16.
- Every included question has a source-verified answer — none had to be marked "Answer not in source" for this build.

## How questions were identified

Three HTML mechanisms are used for MCQ across this corpus, all handled:

1. **Static `<input type="radio">` groups** (the majority): a radio group whose values are bare letters (A–H, not TRUE/FALSE/NOT GIVEN) is a single-answer MCQ question. The rubric ("Choose the correct letter, A, B, C or D.") and the per-question stem/options text are recovered from the surrounding HTML — several different site templates nest these differently (stem+options wrapped together, stem and options as flat sibling `<p>`/`<div>` pairs, a shared `<ul>` of `<li>` options, etc.), so the stem is located by walking outward from the option row(s) through *preceding siblings* first (matching how each template actually separates "the text above the options" from "the options"), only falling back to climbing parent elements for templates where that doesn't apply.
2. **Static `<input type="checkbox">` groups**: a checkbox group with letter values is a "Choose TWO/THREE" question. The question-number range comes from (in order of preference) a `data-q="20,21"` attribute, a shared input name like `q20_21` or `q23-24`, a nearby "Questions N–M" header, or the single checkbox's own number.
3. **Data-driven single MCQ** (`CD IELTS Reading Test 9.3.html`, `Reading Premium Full test 22.html`): built from a `mcqData`/`mcqGroups` JavaScript object rather than static HTML, parsed the same way the Matching build's `matrixDefs` groups were (recovering the real instruction sentence from the static `<p class="instruction">` that precedes the JS-filled container).

Answers were read from each file's own `correctAnswers`-style object. A dedicated MCQ-aware matcher (rather than the simple exact-match scorer used for TFNG/Matching) was needed because this family stores multi-letter answers inconsistently — as a JSON array (`["A","D"]`), as a single combined string (`"A/D"`), or keyed by the whole question range (`"1-3": ["A","D","F"]`) instead of per question number — all three forms are now recognised.

## Excluded as look-alikes, not true MCQ

Several radio-button groups use the same `<input type="radio" value="A">` markup as a real MCQ but are actually a different IELTS question type wearing MCQ's clothes. These were detected and routed out of this build rather than mis-filed:

- **Explicit "Classify the features as belonging to: A ... B ... C ..." questions** — the same small category legend (2–4 options) is reused as the "answer choices" for every statement in the group. This is a Matching-Features-style classification question, not a standalone 4-option MCQ. Found in: *Attine Ants* (Q20–24, all 3 duplicate source files) and *How Do We Find Our Way* (Q1–5).
- **"matching-grid" / table-style radio groups with no visible per-option text** (column headers A–G above blank radio cells, one table row per statement) — genuinely Matching Information / Matching Features / Matching Sentence Endings rendered as a grid, not MCQ. Found in: `CD IELTS Reading Test 3.10.html`, `3.7.html`, `3.9.html`, `Random Passage 2C - Lever Brothers' Sunlight Soap.html`, and `Reading premium Full test 3.html` (this last file turned out to use a fully minified, bundled single-page-app engine with no readable `correctAnswers`-style key at all — its MCQ-shaped content is this same blank-grid type, so nothing of value was actually lost by excluding it).

11 groups (around 60 questions) were excluded this way. **Note for your awareness:** several of these are genuine Matching-family content (Matching Features via a radio-grid, not a `<select>`) that the earlier Matching sheet build did not capture either, since that extractor only scanned `<select>` elements. If useful, a follow-up pass could extend the Matching extractor to also read these radio-grid tables — let me know if you'd like that.

## Duplicate passages (same passage found in more than one source file)

Only the first-seen copy of each was included; every source file is listed in the answer sheet's "Source" column for every question from that passage.

1. **A New Voyage Round the World** — `Passage 1/Passage 1 -An important language development.html` and `Passage 2/IELTS Academic Reading Test 1.3.html`.
2. **The History of Early Cinema** — `Passage 1/Random Passage 1G - The History of Early Cinema.html` and `Passage 1/Random Passage 1H - The History of Early Cinema.html`.
3. **The Fascinating World of Attine Ants** — `Passage 2/Random Passage 2 - Attine Ants.html` and `Passage 2/Random Passage 2I - Attine Ants.html`.

## Known limitations (non-blocking)

- For "Choose TWO" items, the answer sheet shows the full combined letter set (e.g. "C, D") against *both* renumbered question boxes, since the source stores one shared answer array for the pair/triple rather than a separate letter per box — this matches how the source itself records the answer.
- One passage (**Research in Antarctica**, Q23–24 and Q25–26) has its "Choose TWO" rubric and stem question merged into a single HTML block with no separating element, so the printed question text repeats the instruction sentence rather than showing a distinct stem line. Cosmetic only — the options, question count, and answers are all correct.
- Passage **level** (P1/P2/P3) is explicit in the source for most files; where absent, it was inferred from the fixed IELTS Academic question-number boundaries (1–13→P1, 14–26→P2, 27–40→P3).

## Reference style

Same measured style as the TFNG/Completion/Matching builds: A4, ~1.8cm margins, grayscale-only palette, Helvetica for headings/instructions, Times-Roman for passage body/question content, 13pt body / 12.5pt question text / 20pt sheet title. Each option is printed on its own line as "**A**  option text"; a "(Choose N letters.)" note is added under the stem for choose-TWO/THREE items.
