"""Build Listening/IELTS_Listening_Spelling_Mastery_7_Day.pdf from the Markdown parts in Listening/Spelling Workbook/.

Usage: python build_spelling_workbook_pdf.py
Parts 00_*.md ... 99_*.md are joined in name order -> styled HTML -> PDF via headless Edge.

Markdown conventions used in the parts:
  ## [Label] Title          new chapter; Label goes in the badge (Start, Day 1, Test, Key, Log)
  [[blank]] / [[b]]        long / short writing line
  [[dictation:day1]]       numbered answer lines for that day's audio (from dictation.json)
  [[dictation-key:day1]]   the dictation script (word + sentence) for the Answer Key
  <div class="cols" markdown="1"> ... </div>   two-column exercise list
  > ⚠️ ...  /  > 💡 ...     warning / tip boxes
"""
import json, re, subprocess, pathlib, runpy, html as h

import markdown

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "Spelling Workbook"
HTML = ROOT / "scripts" / "_build_spelling_workbook.html"
PDF = ROOT / "IELTS_Listening_Spelling_Mastery_7_Day.pdf"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

# Regenerate the Real Answer Words chapter (09_answer_words.md) and its dictation sets first.
runpy.run_path(str(ROOT / "scripts" / "build_answer_words_md.py"))
DICT = json.loads((SRC / "dictation.json").read_text(encoding="utf-8"))
BLANK = "<span class='blank'></span>"
SHORT = "<span class='blank short'></span>"


def dictation_lines(key):
    d = DICT[key]
    if d.get("gapped"):
        rows = "".join(f"<li>{h.escape(gap, quote=False).replace('[[blank]]', BLANK)}</li>"
                       for _, _, gap in d["items"])
        return f"\n<ol class='gapped'>{rows}</ol>\n"
    rows = "".join(f"<li>{BLANK}</li>" for _ in d["items"])
    return f"\n<ol class='dict'>{rows}</ol>\n"


def dictation_key(key):
    d = DICT[key]
    if not any(item[1] for item in d["items"]):      # word-only sets: compact numbered list
        return "\n<ol class='wkey'>" + "".join(f"<li>{h.escape(i[0])}</li>" for i in d["items"]) + "</ol>\n"
    rows = "".join(
        f"<tr><td>{i}</td><td><b>{h.escape(item[0])}</b></td><td>{h.escape(item[1])}</td></tr>"
        for i, item in enumerate(d["items"], 1))
    return (f"\n<table class='dkey'><thead><tr><th>#</th><th>Answer</th><th>Audio script</th></tr></thead>"
            f"<tbody>{rows}</tbody></table>\n")


parts = sorted(SRC.glob("[0-9][0-9]_*.md"))
text = "\n\n".join(p.read_text(encoding="utf-8") for p in parts)
text = re.sub(r"\[\[dictation:(\w+)\]\]", lambda m: dictation_lines(m.group(1)), text)
text = re.sub(r"\[\[dictation-key:(\w+)\]\]", lambda m: dictation_key(m.group(1)), text)
text = text.replace("[[blank]]", BLANK).replace("[[b]]", SHORT)
# A tip/warning line or the line after a bold-only "rule" line starts on its own line.
text = re.sub(r"(?<=\S)\n(?=⚠️|💡)", "\n\n", text)
text = re.sub(r"(?m)^(\*\*[^\n]*\*\*)\n(?=[^\s|<>#\-])", r"\1  \n", text)

body = markdown.markdown(text, extensions=["tables", "sane_lists", "md_in_html"])

# Callout boxes.
body = body.replace("<blockquote>\n<p>⚠️", "<blockquote class='warn'>\n<p>⚠️")
body = body.replace("<blockquote>\n<p>💡", "<blockquote class='tip'>\n<p>💡")
body = body.replace("<blockquote>\n<p><strong>My score", "<blockquote class='score'>\n<p><strong>My score")

# One chapter per "## [Label] Title".
chapters = []
def h2(m):
    label, title = m.group(1), m.group(2)
    chapters.append((label, title))
    cls = "chapter key" if label == "Key" else "chapter"
    return f"</section><section class='{cls}'><h2><span class='num'>{h.escape(label)}</span>{title}</h2>"
body = re.sub(r"<h2>\[([^\]]+)\]\s*(.+?)</h2>", h2, body)
body = body.replace("</section>", "", 1) + "</section>"

# Exercise / dictation / assessment headings get their own colour.
body = re.sub(r"<h3>((?:Exercise|Dictation|Day \d Assessment|Test Section)[^<]*)</h3>", r"<h3 class='ex'>\1</h3>", body)
body = body.replace("<h3>Error Log</h3>", "<h3 class='newpage'>Error Log</h3>")
# Keep each dictation heading, its "Play ..." line and its answer lines on one page.
body = re.sub(r"(<h4>Block \d</h4>\s*<ol class='dict'>.*?</ol>)", lambda m: "<div class='keep'>" + m.group(1) + "</div>",
              body, flags=re.S)
body = re.sub(r"(<h3 class='ex'>(?:Dictation|Test Section 1)[^<]*</h3>\s*<p>.*?</p>\s*<ol class='(?:dict|gapped)'>.*?</ol>)",
              lambda m: "<div class='keep'>" + m.group(1) + "</div>", body, flags=re.S)
# Answer-key day headings start a new page.
body = re.sub(r"<h3>(Answers?: [^<]*)</h3>", r"<h3 class='keyday'>\1</h3>", body)

blurbs = {
    "Start": "Why you misspell, the 12 problems, IELTS spelling rules, the daily routine",
    "Day 1": "Important, different, convenient: 5 rules and 43 words",
    "Day 2": "Importance, difference, patience or patients?",
    "Day 3": "Available, possible: the whole-word rule, -e and -y changes",
    "Day 4": "Library, stationery, and -al/-el, -ic/-ical, -cial/-tial, -ous, -tion/-sion, -ful, -or/-our, -er/-re, -ise",
    "Day 5": "Accommodation, receipt, Wednesday, ie/ei, ea/ee, ai/ay, ou/ow, British spelling",
    "Day 6": "120 words in 10 IELTS Listening topics",
    "Day 7": "Sheep, species, information, a ten-minute walk: noun-number traps",
    "Test": "60 marks covering all seven days",
    "Bank": "623 real gap-fill answer words from Cambridge 10–19, most frequent first, with 7 dictations",
    "Key": "Answers to every exercise, assessment and dictation",
    "Log": "Score tracker, error log, spaced review",
}
toc = "".join(
    f"<li><span class='tnum'>{h.escape(l)}</span><span class='ttl'>{t}"
    f"<small>{blurbs.get(l, '')}</small></span></li>" for l, t in chapters)

cover = """
<section class='cover'>
  <div class='kicker'>IELTS Listening · Spelling</div>
  <h1>7-Day IELTS Listening Spelling Mastery</h1>
  <div class='sub'>A Comprehensive Workbook to Eliminate Common Spelling Mistakes</div>
  <div class='days'>
    <div><b>1</b><span>-ant / -ent</span></div>
    <div><b>2</b><span>-ance / -ence</span></div>
    <div><b>3</b><span>-able / -ible</span></div>
    <div><b>4</b><span>-ary / -ery &amp; more</span></div>
    <div><b>5</b><span>Double, silent, vowels</span></div>
    <div><b>6</b><span>120-word bank</span></div>
    <div class='plural'><b>7</b><span>Singular &amp; plural</span></div>
  </div>
  <table class='profile'>
    <tr><th>Words covered</th><td><b>450+</b> words with IPA, meaning, example and common mistake</td></tr>
    <tr><th>Practice</th><td>40+ exercises · 8 audio dictations · 7 daily assessments · Final Mastery Test</td></tr>
    <tr><th>Spelling</th><td>British English (IELTS accepts British or American, so be consistent)</td></tr>
    <tr><th>Personal</th><td>★ marks words <b>you</b> have misspelled before</td></tr>
  </table>
</section>
<section class='contents'>
  <h2 class='plain'>Contents</h2>
  <ol class='toc'>""" + toc + """</ol>
</section>
"""

css = """
@page { size: A4; margin: 15mm 14mm 17mm 14mm;
  @bottom-center { content: counter(page); font: 9pt 'Segoe UI', sans-serif; color: #8A94A3; }
  @bottom-right { content: '7-Day Listening Spelling Mastery'; font: 8pt 'Segoe UI', sans-serif; color: #B0B8C4; } }
@page :first { @bottom-center { content: none; } @bottom-right { content: none; } }
:root { --ink:#16202C; --muted:#5B6675; --accent:#14465F; --accent2:#2A7F9E; --band:#EAF3F6;
        --line:#D3DDE3; --warn:#FFF5DD; --warnline:#E0A526; --good:#E7F5EC; --goodline:#2E8B57;
        --ex:#6A3FA0; --exband:#F3EEFA; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; font: 10.2pt/1.48 'Segoe UI', Calibri, 'Lucida Sans Unicode', sans-serif; color: var(--ink); background: #fff; }
section.chapter, section.contents { break-before: page; }
h2 { font-size: 19pt; color: var(--accent); margin: 0 0 12px; padding-bottom: 8px;
     border-bottom: 3px solid var(--accent); display: flex; align-items: center; gap: 12px; break-after: avoid; }
h2 .num { background: var(--accent); color: #fff; border-radius: 8px; padding: 0 10px; height: 36px; white-space: nowrap;
          display: inline-flex; align-items: center; justify-content: center; font-size: 13pt; }
h3 { font-size: 12.5pt; color: var(--accent); margin: 16px 0 6px; break-after: avoid;
     border-left: 4px solid var(--accent2); padding-left: 8px; }
h3.ex { color: var(--ex); border-left-color: var(--ex); background: var(--exband); padding: 4px 8px; border-radius: 3px; }
h3.keyday { margin-top: 22px; }
h4 { font-size: 11pt; margin: 12px 0 4px; color: var(--accent2); break-after: avoid; }
p { margin: 5px 0; }
ul, ol { margin: 5px 0; padding-left: 22px; } li { margin: 2px 0; }
table { width: 100%; border-collapse: collapse; margin: 7px 0 11px; font-size: 9.2pt; break-inside: auto; }
tr { break-inside: avoid; }
thead { display: table-header-group; }
th { background: var(--accent); color: #fff; text-align: left; padding: 4px 7px; font-weight: 600; }
td { padding: 4px 7px; border-bottom: 1px solid var(--line); vertical-align: top; }
tbody tr:nth-child(even) td { background: #F6F9FA; }
blockquote { margin: 9px 0; padding: 7px 11px; background: var(--band); border-left: 4px solid var(--accent2); border-radius: 4px;
             break-inside: avoid; }
blockquote.warn { background: var(--warn); border-left-color: var(--warnline); }
blockquote.tip { background: var(--good); border-left-color: var(--goodline); }
blockquote.score { background: #fff; border: 1.5px dashed var(--ex); }
blockquote p { margin: 3px 0; }
code { font-family: Consolas, monospace; background: #EEF1F4; padding: 0 4px; border-radius: 3px; font-size: 9pt; }
strong { color: #0B1824; }
.blank { display: inline-block; min-width: 42mm; border-bottom: 1px solid #7C8794; height: 1.05em; vertical-align: -2px; }
.blank.short { min-width: 11mm; }
.cols { columns: 2; column-gap: 9mm; }
.cols ol { margin-top: 0; }
.cols li { break-inside: avoid; padding: 2px 0; }
ol.dict { columns: 2; column-gap: 9mm; padding-left: 26px; }
ol.dict li { padding: 5px 0; break-inside: avoid; }
ol.dict .blank { min-width: 62mm; }
ol.gapped li { padding: 5px 0; }
ol.dict, ol.gapped { break-inside: avoid; }
h3.newpage { break-before: page; }
.keep { break-inside: avoid; }
.az { columns: 5; column-gap: 6mm; font-size: 9.3pt; list-style: none; padding: 0; margin: 6px 0; }
.az li { margin: 0; line-height: 1.38; break-inside: avoid; }
.az li.azletter { font-weight: 700; color: #fff; background: var(--accent); display: table; padding: 0 7px;
                  border-radius: 3px; margin: 6px 0 2px; break-after: avoid; }
.az sup { color: var(--ex); font-weight: 700; font-size: 7pt; }
ol.wkey { columns: 4; column-gap: 6mm; font-size: 9pt; }
table.dkey td:first-child { width: 6%; } table.dkey td:nth-child(2) { width: 24%; }

/* Cover */
section.cover { height: 258mm; display: flex; flex-direction: column; justify-content: center; padding: 0 6mm; }
.kicker { font-size: 13pt; letter-spacing: 3px; text-transform: uppercase; color: var(--accent2); font-weight: 600; }
.cover h1 { font-size: 40pt; line-height: 1.08; margin: 8px 0 8px; color: var(--accent); }
.cover .sub { font-size: 15pt; color: var(--muted); margin-bottom: 30px; }
.days { display: grid; grid-template-columns: repeat(7, 1fr); gap: 5px; margin-bottom: 30px; }
.days div { background: var(--band); border-top: 5px solid var(--accent2); border-radius: 4px; padding: 9px 6px;
            display: flex; flex-direction: column; gap: 3px; min-height: 26mm; }
.days b { font-size: 20pt; color: var(--accent); line-height: 1; }
.days span { font-size: 8.8pt; }
.days .plural { background: var(--exband); border-top-color: var(--ex); }
table.profile { font-size: 11pt; }
table.profile th { width: 26%; background: var(--band); color: var(--accent); border-bottom: 2px solid #fff; padding: 8px 12px; }
table.profile td { padding: 8px 12px; background: #fff !important; }

/* Contents */
h2.plain { display: block; }
ol.toc { list-style: none; padding: 0; margin: 10px 0 20px; }
ol.toc li { display: flex; gap: 14px; align-items: center; padding: 8px 4px; border-bottom: 1px solid var(--line); }
.tnum { background: var(--accent); color: #fff; border-radius: 6px; min-width: 58px; height: 30px; display: inline-flex;
        align-items: center; justify-content: center; font-weight: 700; font-size: 10pt; }
.ttl { font-size: 12pt; font-weight: 600; display: flex; flex-direction: column; }
.ttl small { font-size: 9.3pt; font-weight: 400; color: var(--muted); }

/* Answer key: denser */
section.key { font-size: 9.6pt; }
section.key ol { columns: 2; column-gap: 8mm; }
section.key ol li { break-inside: avoid; }
section.key table.dkey { font-size: 8.8pt; }

/* Trackers */
table.tracker td { height: 11mm; vertical-align: middle; }
table.errlog td { height: 9mm; }
"""

page = f"""<!doctype html><html lang='en'><head><meta charset='utf-8'>
<title>7-Day IELTS Listening Spelling Mastery</title><style>{css}</style></head>
<body>{cover}{body}</body></html>"""

# Trackers: mark tables by their first header so CSS can give them tall rows.
page = re.sub(r"<table>(\s*<thead>\s*<tr>\s*<th>Day</th>\s*<th>Date</th>)", r"<table class='tracker'>\1", page)
page = re.sub(r"<table>(\s*<thead>\s*<tr>\s*<th>Date</th>\s*<th>❌)", r"<table class='errlog'>\1", page)

HTML.write_text(page, encoding="utf-8")
subprocess.run([EDGE, "--headless", "--disable-gpu", "--no-pdf-header-footer", "--print-to-pdf-no-header",
                f"--print-to-pdf={PDF}", HTML.as_uri()], check=True, capture_output=True, timeout=180)
print("wrote", PDF)
