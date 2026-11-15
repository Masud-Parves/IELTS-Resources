"""Build the 7 one-day spelling sheets: Listening/Spelling Sheets/Day_N_*.pdf

Usage: python build_spelling_day_sheets.py [1 2 ...]      (default: all 7 days)

Each sheet = that day's lesson (Listening/Spelling Workbook/0N_dayN.md, cleaned)
           + "Words from real Cambridge tests" that follow the day's rule
           + exercises, dictation, assessment
           + the day's answers (from 10_answer_key.md) on the last pages.
Style follows the Writing Idea Bank PDFs (Writing/tools/style.css): Georgia 15.5pt body,
Segoe UI blue headings, 14pt tables, "Page x / y" footer.
"""
import json, re, sys, subprocess, pathlib, tempfile, html as h

import markdown

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "Spelling Workbook"
OUT = ROOT / "Spelling Sheets"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
DICT = json.loads((SRC / "dictation.json").read_text(encoding="utf-8"))
CAM = json.loads((SRC / "cambridge_answer_words.json").read_text(encoding="utf-8"))
BLANK = "<span class='blank'></span>"
SHORT = "<span class='blank short'></span>"

NAMES = {1: "Day_1_ANT_vs_ENT", 2: "Day_2_ANCE_vs_ENCE", 3: "Day_3_ABLE_vs_IBLE",
         4: "Day_4_ARY_ERY_and_Other_Endings", 5: "Day_5_Double_Silent_Letters_and_Vowels",
         6: "Day_6_Vocabulary_Bank", 7: "Day_7_Singular_and_Plural"}


# ---------- Cambridge 10-19 answer words that follow each day's rule ----------
def forms(r):
    return [r["word"]] + r["forms"]

def any_form(r, pat):
    return any(re.search(pat, f) for f in forms(r))

SKIP = {"plants", "percent", "style", "floor"}     # match a pattern by accident, not a spelling trap
D4 = (r"(ary|ery|ory|tion|sion|cian|al|el|le|ic|ical|cial|tial|ous|ful|our|or|ar|re|ise|yse)s?$")
RULES = {
    1: lambda r: len(r["word"]) > 5 and r["word"] not in SKIP and any_form(r, r"(ant|ent)s?$"),
    2: lambda r: len(r["word"]) > 6 and any_form(r, r"(ance|ence|ancy|ency|ancies|encies)s?$"),
    3: lambda r: any_form(r, r"(able|ible)s?$"),
    4: lambda r: len(r["word"]) > 4 and r["word"] not in SKIP and not r["word"].endswith("ure")
                 and any_form(r, D4) and r["count"] >= 2,
    5: lambda r: re.search(r"([bcdfgklmnprstz])\1", r["word"]) is not None,
    6: lambda r: r["count"] >= 3,
    7: lambda r: r["count"] >= 2 and any(f != r["word"] and f.endswith("s") for f in r["forms"]),
}
CAM_NOTE = {
    1: "These real answers end in <b>-ant</b> or <b>-ent</b>. Note: <b>-ment</b> is always -ent.",
    2: "These real answers end in <b>-ance / -ence / -ancy / -ency</b>.",
    3: "These real answers end in <b>-able / -ible</b>.",
    4: "Real answers with today's endings that came up <b>two or more times</b>.",
    5: "These real answers have a <b>double letter</b>. Say the double letter when you spell them.",
    6: "The most frequent answers in all 40 tests (used <b>3 or more times</b>).",
    7: "Real answers that appeared in the plural, used 2+ times. <b>Check the -s every time.</b>",
}

def cambridge_box(day):
    rows = [r for r in CAM if RULES[day](r)]
    if day == 7:
        def show(r):
            pl = next(f for f in r["forms"] if f != r["word"] and f.endswith("s"))
            return f"{h.escape(r['word'])} → <b>{h.escape(pl)}</b>"
    else:
        show = lambda r: h.escape(r["word"])
    items = "".join(f"<li>{show(r)}" + (f" <sup>×{r['count']}</sup>" if r["count"] >= 2 else "") + "</li>"
                    for r in rows)
    cls = "camlist wide" if day == 7 else "camlist"
    return (f"<div class='cam'><h2>Words from real Cambridge tests</h2>"
            f"<p>{CAM_NOTE[day]} (Cambridge IELTS 10–19 Listening keys; ×2 = the answer appeared twice.)</p>"
            f"<ul class='{cls}'>{items}</ul></div>")


# ---------- dictation helpers (same data as the full workbook) ----------
def dictation_lines(key):
    d = DICT[key]
    if d.get("gapped"):
        rows = "".join(f"<li>{h.escape(gap, quote=False).replace('[[blank]]', BLANK)}</li>"
                       for _, _, gap in d["items"])
        return f"\n<ol class='gapped'>{rows}</ol>\n"
    return "\n<ol class='dict'>" + "".join(f"<li>{BLANK}</li>" for _ in d["items"]) + "</ol>\n"


def dictation_key(key):
    rows = "".join(f"<tr><td>{i}</td><td><b>{h.escape(a)}</b></td><td>{h.escape(s)}</td></tr>"
                   for i, (a, s, *_) in enumerate(DICT[key]["items"], 1))
    return (f"\n<table class='dkey'><thead><tr><th>#</th><th>Answer</th><th>Audio script</th></tr></thead>"
            f"<tbody>{rows}</tbody></table>\n")


# ---------- clean one day's Markdown ----------
def drop_section(text, title):
    return re.sub(rf"(?ms)^### {re.escape(title)}\n.*?(?=^### )", "", text)


def clean(text):
    text = drop_section(text, "Learning objectives")
    text = text.replace("You will use this table again tomorrow. ", "")
    text = re.sub(r"(?m)^> \*\*My score:.*$", "> **My score: ______ / 20**", text)
    text = re.sub(r" ?★", "", text)
    text = text.replace("▶ ", "")
    text = text.replace("❌ ", "").replace("✅ ", "")
    return text


def answers_for(day):
    key = (SRC / "10_answer_key.md").read_text(encoding="utf-8")
    m = re.search(rf"(?ms)^### Answers: Day {day}\n(.*?)(?=^### |\Z)", key)
    return re.sub(r"(?m)^\*\*([^*\n]+):\*\* (\d.*)$", answer_list, m.group(1))


def answer_list(m):
    items = []
    for part in m.group(2).split(" · "):
        n = re.match(r"(\d+) (.*)", part)
        if n:
            items.append(f"<li><b>{n.group(1)}</b> {md_inline(n.group(2))}</li>")
        elif items:                                   # text that belongs to the previous answer
            items[-1] = items[-1][:-5] + " · " + md_inline(part) + "</li>"
    return f"<h3 class='anshead'>{m.group(1)}</h3>\n<ul class='ans'>{''.join(items)}</ul>\n"


def md_inline(t):
    return markdown.markdown(t)[3:-4]


def md_to_html(text):
    text = re.sub(r"\[\[dictation:(\w+)\]\]", lambda m: dictation_lines(m.group(1)), text)
    text = re.sub(r"\[\[dictation-key:(\w+)\]\]", lambda m: dictation_key(m.group(1)), text)
    text = text.replace("[[blank]]", BLANK).replace("[[b]]", SHORT)
    text = re.sub(r"(?<=\S)\n(?=⚠️|💡)", "\n\n", text)
    text = re.sub(r"(?m)^(\*\*[^\n]*\*\*)\n(?=[^\s|<>#\-])", r"\1  \n", text)
    body = markdown.markdown(text, extensions=["tables", "sane_lists", "md_in_html"])
    # Callouts: keep the box colour, drop the emoji.
    body = body.replace("<blockquote>\n<p>⚠️ ", "<blockquote class='warn'>\n<p>")
    body = body.replace("<blockquote>\n<p>💡 ", "<blockquote class='tip'>\n<p>")
    body = body.replace("<blockquote>\n<p><strong>My score", "<blockquote class='score'>\n<p><strong>My score")
    body = re.sub(r"<p>⚠️ ", "<p class='warnline'>", body)
    body = re.sub(r"<p>💡 ", "<p class='tipline'>", body)
    body = body.replace("💡 ", "").replace("⚠️ ", "").replace(" ⚠️", "").replace("⚠️", "")
    # IPA in a font that has every IPA symbol.
    body = re.sub(r"(?<=[\s(>])(/[^/<>\s]{1,30}/)(?=[\s),.<])", r"<span class='ipa'>\1</span>", body)
    # Word tables: IPA and part of speech on the line under the word.
    body = re.sub(r"(<td><strong>[^<]+</strong>) (<span class='ipa'>)", r"\1<br>\2", body)
    body = body.replace("<th>Word · IPA · Part of speech</th>", "<th class='w'>Word</th>")
    # Heading levels: ### -> h2, #### -> h3.
    body = re.sub(r"<(/?)h3>", r"<\1h2>", re.sub(r"<(/?)h4>", r"<\1h3>", body))
    body = re.sub(r"<h2>((?:Exercise|Dictation|Day \d Assessment)[^<]*)</h2>", r"<h2 class='ex'>\1</h2>", body)
    # Keep a dictation heading, its instruction and its answer lines together.
    body = re.sub(r"(<h2 class='ex'>Dictation[^<]*</h2>\s*<p>.*?</p>\s*<ol class='(?:dict|gapped)'>.*?</ol>)",
                  lambda m: "<div class='keep'>" + m.group(1) + "</div>", body, flags=re.S)
    return body


CSS = """
@page { size: A4; margin: 18mm 16mm 20mm 16mm;
  @bottom-center { content: "Day %DAY% · Page " counter(page) " / " counter(pages);
                   font-family: "Segoe UI", Arial, sans-serif; font-size: 10pt; color: #777; } }
:root { --ink:#1d1d1f; --accent:#1f4e79; --soft:#e8f0f8; --tip:#eef7ee; --tipline:#4c9a4c;
        --warn:#fff8ec; --warnline:#e0a64a; --line:#c9d3de; }
html { font-size: 15.5pt; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family: Georgia, Cambria, serif; color: var(--ink); line-height: 1.6; margin: 0; background: #fff; }
h1, h2, h3 { font-family: "Segoe UI", Arial, sans-serif; color: var(--accent); line-height: 1.3; break-after: avoid; }
h1 { font-size: 26pt; margin: 0 0 4pt; border-bottom: 3px solid var(--accent); padding-bottom: 6pt; }
.kicker { font-family: "Segoe UI", Arial, sans-serif; font-size: 12pt; letter-spacing: 2px; text-transform: uppercase;
          color: #4a7aa5; font-weight: 600; }
h2 { font-size: 20pt; margin: 22pt 0 8pt; border-bottom: 2px solid var(--soft); padding-bottom: 4pt; }
h2.ex { background: var(--soft); border: none; border-left: 6px solid var(--accent); padding: 4pt 10pt; border-radius: 4px; }
h3 { font-size: 17pt; margin: 16pt 0 6pt; color: #2b5d8a; }
h2.part { font-size: 24pt; border-bottom: 3px solid var(--accent); break-before: page; margin-top: 0; }
p { margin: 0 0 10pt; }
ul, ol { margin: 4pt 0 10pt; padding-left: 26pt; } li { margin-bottom: 4pt; }
strong { color: #0b2f52; }
table { width: 100%; border-collapse: collapse; margin: 8pt 0 14pt; font-size: 13.5pt; line-height: 1.45; }
th, td { border: 1px solid var(--line); padding: 5pt 7pt; vertical-align: top; text-align: left; }
th { background: var(--accent); color: #fff; font-family: "Segoe UI", Arial, sans-serif; font-weight: 600; }
tr:nth-child(even) td { background: #f6f8fb; }
tr { break-inside: avoid; } thead { display: table-header-group; }
.ipa { font-family: "Segoe UI", "Lucida Sans Unicode", sans-serif; font-size: 0.9em; color: #555; white-space: nowrap; }
blockquote { margin: 8pt 0 14pt; padding: 8pt 14pt; background: var(--soft); border-left: 5px solid var(--accent);
             break-inside: avoid; }
blockquote p:last-child { margin-bottom: 0; }
blockquote.tip, p.tipline { background: var(--tip); border-left: 5px solid var(--tipline); }
blockquote.warn, p.warnline { background: var(--warn); border-left: 5px solid var(--warnline); }
p.tipline, p.warnline { padding: 6pt 12pt; }
blockquote.score { background: #fff; border: 2px dashed var(--accent); font-size: 17pt; }
.blank { display: inline-block; min-width: 50mm; border-bottom: 1.2px solid #555; height: 1.1em; vertical-align: -3px; }
.blank.short { min-width: 16mm; }
.cols { columns: 2; column-gap: 10mm; }
.cols ol { margin-top: 0; } .cols li { break-inside: avoid; padding: 3pt 0; }
.cols .blank { min-width: 32mm; }
ol.dict { columns: 2; column-gap: 10mm; padding-left: 30pt; }
ol.dict li { padding: 6pt 0; break-inside: avoid; } ol.dict .blank { min-width: 62mm; }
ol.gapped li { padding: 6pt 0; }
.keep { break-inside: avoid; }
.howto { font-family: "Segoe UI", Arial, sans-serif; font-size: 13pt; background: var(--soft); border-radius: 8px;
         padding: 8pt 14pt; margin: 10pt 0 16pt; }
.howto ol { margin: 2pt 0 0; } .howto li { margin-bottom: 1pt; }
.cam { background: #f4f9f4; border: 1.5px solid #b9dcb9; border-radius: 8px; padding: 4pt 14pt 8pt; margin: 16pt 0;
       }
.cam h2 { color: #2e6b2e; border-bottom-color: #cfe7cf; margin-top: 8pt; }
.cam p { font-size: 13pt; }
.camlist { columns: 3; column-gap: 8mm; list-style: none; padding: 0; margin: 0; font-size: 14pt; }
.camlist.wide { columns: 2; }
.camlist li { margin: 0 0 2pt; break-inside: avoid; }
.camlist sup { color: #2e6b2e; font-family: "Segoe UI", Arial, sans-serif; font-size: 9pt; font-weight: 700; }
.answers p { margin-bottom: 9pt; line-height: 1.7; }
h3.anshead { font-size: 15pt; margin: 12pt 0 4pt; border-bottom: 1px solid var(--soft); }
ul.ans { columns: 3; column-gap: 6mm; list-style: none; padding: 0; margin: 0 0 8pt; font-size: 13.5pt; line-height: 1.45; }
ul.ans li { break-inside: avoid; margin-bottom: 3pt; }
ul.ans b { display: inline-block; min-width: 1.6em; color: #4a7aa5; font-family: "Segoe UI", Arial, sans-serif; font-size: 11pt; }
th.w { width: 27%; }
table.dkey { font-size: 12.5pt; } table.dkey td:first-child { width: 6%; } table.dkey td:nth-child(2) { width: 24%; }
"""


def build(day):
    src = next(SRC.glob(f"0{day}_day{day}.md"))
    text = clean(src.read_text(encoding="utf-8"))
    m = re.match(r"## \[Day \d\] (.+)\n", text)
    title = m.group(1).replace("Special Chapter: ", "")
    text = text[m.end():]
    # Split: lesson | practice (first Exercise onwards).
    i = text.index("### Exercise")
    lesson, practice = text[:i], text[i:]
    audio = f"Day{day}_Dictation.wav"
    howto = (f"<div class='howto'><b>How to use this sheet</b><ol>"
             f"<li>Read the rules, then cover the word lists and test yourself.</li>"
             f"<li>Do the exercises on the Practice pages.</li>"
             f"<li>Play <b>{audio}</b> for the dictation, then do the assessment.</li>"
             f"<li>Check your answers on the last pages. Write every wrong word 3 times.</li></ol></div>")
    body = (f"<div class='kicker'>IELTS Listening · Spelling · Day {day}</div><h1>{h.escape(title)}</h1>{howto}"
            + md_to_html(lesson) + cambridge_box(day)
            + "<h2 class='part'>Practice</h2>" + md_to_html(practice)
            + "<h2 class='part'>Answers</h2><div class='answers'>" + md_to_html(answers_for(day)) + "</div>")
    page = (f"<!doctype html><html lang='en'><head><meta charset='utf-8'><title>Day {day}: {h.escape(title)}</title>"
            f"<style>{CSS.replace('%DAY%', str(day))}</style></head><body>{body}</body></html>")
    OUT.mkdir(exist_ok=True)
    pdf = OUT / f"{NAMES[day]}.pdf"
    with tempfile.TemporaryDirectory() as tmp:
        hp = pathlib.Path(tmp) / f"day{day}.html"
        hp.write_text(page, encoding="utf-8")
        subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        f"--user-data-dir={pathlib.Path(tmp) / 'profile'}", f"--print-to-pdf={pdf}", hp.as_uri()],
                       check=True, capture_output=True, timeout=180)
    print("wrote", pdf.name)


if __name__ == "__main__":
    days = [int(a) for a in sys.argv[1:]] or list(range(1, 8))
    for d in days:
        build(d)
