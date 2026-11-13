# Cambridge 10–19 Listening answer words

Collects every gap-fill answer from the Listening answer keys of Cambridge IELTS 10–19 (40 tests) and turns them into a de-duplicated word list for the spelling workbook. Run all commands from this folder.

1. `python scripts/render_keys.py`: renders the 40 key pages listed in `scripts/key_pages.json` at 300 dpi to `working/keys/`. To find the pages in a new book, use `scripts/render_tail.py` and OCR the last pages.
2. **Windows OCR:** `powershell -NoProfile -ExecutionPolicy Bypass -File "../By Category/scripts/winocr.ps1" working/keys_json working/keys/*.png`
3. **RapidOCR** (second pass; it reads the single words and letters that Windows OCR drops): `python scripts/rapid_pass.py`
4. `python scripts/extract_answers.py win` and `python scripts/extract_answers.py rapid` split each page into its two columns and read the numbered answers. C11 and C12 use the PDF text layer instead of OCR, because the C12 scan OCRs badly; C17's text layer is garbage.
5. `python scripts/merge_answers.py` merges the two readings with `scripts/overrides.json` (fixes checked by eye) into `working/answers.json`. It lists every disagreement.
6. `python scripts/build_wordlist.py` writes `working/wordlist.json` and the workbook copy `Listening/Spelling Workbook/cambridge_answer_words.json`. It keeps only word answers, splits `/` alternatives and `(s)` options, removes function words, number words and names, merges singular/plural and American/British spellings, and counts how many answers use each word.
7. Rebuild the workbook: `python Listening/scripts/build_spelling_workbook_pdf.py`. For the block audio: `pwsh -File Listening/scripts/make_spelling_workbook_audio.ps1 -Only aw1,aw2,aw3,aw4,aw5,aw6,aw7`.

Result (2026-11-13): 825 word answers → 623 unique words; 132 are used 2+ times.

`working/` holds rendered key pages and OCR output and is gitignored. The workbook copy has words and counts only, with no test or question numbers.
