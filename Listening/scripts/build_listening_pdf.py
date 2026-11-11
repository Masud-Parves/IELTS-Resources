"""Build Listening/IELTS_Listening_3_Week_Plan.pdf from the Markdown guide.

Usage: python build_listening_pdf.py
Markdown -> styled HTML (cover, contents, one section per page, printable templates) -> PDF via headless Edge.
"""
import re, subprocess, pathlib, html as h

import markdown

ROOT = pathlib.Path(__file__).resolve().parent.parent
MD = ROOT / "IELTS_Listening_3_Week_Plan.md"
HTML = ROOT / "scripts" / "_build.html"
PDF = ROOT / "IELTS_Listening_3_Week_Plan.pdf"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

text = MD.read_text(encoding="utf-8")

# Drop the title + intro block (they go on the cover) and the horizontal rules (sections get their own pages).
text = text[text.index("## 0."):]
text = re.sub(r"^---\s*$", "", text, flags=re.M)
# Task-list boxes and local file links do not work on paper.
text = text.replace("- [ ] ", "- ☐ ")
# Python-Markdown needs 4-space nested lists and a blank line before a list that follows a bold line.
text = re.sub(r"(?m)^ {3}- ", "    - ", text)
text = re.sub(r"(?m)^(\*\*[^\n]+\*\*|[A-Z][^\n|]*:)\n(- )", r"\1\n\n\2", text)
text = re.sub(r"\[([^\]]+\.md)\]\([^)]+\)", r"<span class='file'>Writing/\1</span>", text)

body = markdown.markdown(text, extensions=["tables", "sane_lists"])

body = body.replace("<li>☐ ", "<li class='check'>☐ ")
# Callouts: blockquotes starting with a warning sign become warning boxes.
body = body.replace("<blockquote>\n<p>⚠️", "<blockquote class='warn'>\n<p>⚠️")

# One page per main section; keep the section number in a badge.
sections = []
def h2(m):
    num, title = m.group(1), m.group(2)
    sections.append((num, title))
    return (f"</section><section class='chapter'><h2><span class='num'>{num}</span>{title}</h2>")
body = re.sub(r"<h2>(\d+)\.\s*(.+?)</h2>", h2, body)
body = body.replace("</section>", "", 1) + "</section>"

# Tools A-F as cards.
body = re.sub(r"<h3>(Tool [A-F]):\s*(.+?)</h3>", r"<h3 class='tool'><span class='tag'>\1</span>\2</h3>", body)

# Printable templates: more blank rows, and the tracker on its own page.
blank = "<tr>" + "<td></td>" * 7 + "</tr>"
body = re.sub(r"(<th>Why / what I learned</th>\s*</tr>\s*</thead>\s*<tbody>)(.*?)(</tbody>)",
              lambda m: m.group(1) + blank * 15 + m.group(3), body, flags=re.S)
body = body.replace("<h3>Week 3: Exam simulation</h3>", "<h3 class='pagebreak'>Week 3: Exam simulation</h3>")
body = body.replace("<h3>Mistake Log</h3>", "<h3 class='tpl'>Mistake Log</h3>")
body = body.replace("<h3>21-Day Tracker</h3>", "<h3 class='tpl pagebreak'>21-Day Tracker</h3>")
# Mark the template tables so CSS can make rows tall.
body = re.sub(r"<table>(\s*<thead>\s*<tr>\s*<th>Date</th>\s*<th>Test</th>)", r"<table class='log'>\1", body)
body = re.sub(r"<table>(\s*<thead>\s*<tr>\s*<th>Week</th>\s*<th>SP</th>)", r"<table class='count'>\1", body)
body = re.sub(r"<table>(\s*<thead>\s*<tr>\s*<th>Day</th>\s*<th>Spelling</th>)", r"<table class='tracker'>\1", body)

blurbs = {
    "0": "Score math and where your missing marks are",
    "1": "Books, audio, and which tests to use",
    "2": "Mistake Log, dictation, spelling, transcript method, shadowing, full test",
    "3": "How to handle each part and each question type",
    "4": "The 2-question rule, signal phrases, distractor traps",
    "5": "Answer rules, your vowel problem, word bank",
    "6": "Your 75-minute routine",
    "7": "Day-by-day plan and weekly targets",
    "8": "How to run the mocks and judge if you are ready",
    "9": "What to check before, during, and after each part",
    "10": "Mistake Log, code count, 21-day tracker",
}
toc = "".join(
    f"<li><span class='tnum'>{n}</span><span class='ttl'>{h.escape(t, quote=False)}"
    f"<small>{blurbs.get(n, '')}</small></span></li>" for n, t in sections)

cover = """
<section class='cover'>
  <div class='kicker'>IELTS Listening</div>
  <h1>My 3-Week Plan</h1>
  <div class='sub'>Listening skills + spelling, from 25 to 30+</div>
  <table class='profile'>
    <tr><th>Now</th><td>about <b>25/40</b> (band 6.0)</td></tr>
    <tr><th>Target</th><td><b>30+/40</b> (band 7.0+)</td></tr>
    <tr><th>Main problems</th><td>Part 3 feels fast · spelling mistakes</td></tr>
    <tr><th>Daily time</th><td>about 75 minutes</td></tr>
  </table>
  <div class='timeline'>
    <div><b>Week 1</b><span>4–10 Nov</span><em>Find the problems, fix the ear</em></div>
    <div><b>Week 2</b><span>11–17 Nov</span><em>Part 3 &amp; 4 power week</em></div>
    <div><b>Week 3</b><span>18–24 Nov</span><em>Exam simulation</em></div>
    <div class='mock'><b>Mocks</b><span>25–30 Nov</span><em>2–3 unseen tests</em></div>
    <div class='exam'><b>Exam</b><span>December</span><em>Band 7+</em></div>
  </div>
</section>
<section class='contents'>
  <h2 class='plain'>Contents</h2>
  <ol class='toc'>""" + toc + """</ol>
  <div class='howto'><b>How to use this guide:</b> read Sections 0–5 once in the first two days.
  After that you only need Section 6 (daily routine), Section 7 (today's task) and Section 10 (log and tracker).
  Print the pages of Section 10, or copy them into your notebook.</div>
</section>
"""

css = """
@page { size: A4; margin: 16mm 15mm 18mm 15mm;
  @bottom-center { content: counter(page); font: 9pt 'Segoe UI', sans-serif; color: #8A94A3; }
  @bottom-right { content: 'IELTS Listening · 3-Week Plan'; font: 8pt 'Segoe UI', sans-serif; color: #B0B8C4; } }
@page :first { @bottom-center { content: none; } @bottom-right { content: none; } }
:root { --ink:#16202C; --muted:#5B6675; --accent:#1A3A5C; --accent2:#2F6B9A; --band:#EDF2F7;
        --line:#D5DCE4; --warn:#FFF6E0; --warnline:#E0A526; --good:#E8F5EC; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; font: 10.5pt/1.5 'Segoe UI', Calibri, sans-serif; color: var(--ink); background: #fff; }
section.chapter, section.contents { break-before: page; }
h2 { font-size: 19pt; color: var(--accent); margin: 0 0 12px; padding-bottom: 8px;
     border-bottom: 3px solid var(--accent); display: flex; align-items: center; gap: 12px; break-after: avoid; }
h2 .num { background: var(--accent); color: #fff; border-radius: 8px; min-width: 38px; height: 38px;
          display: inline-flex; align-items: center; justify-content: center; font-size: 17pt; }
h3 { font-size: 13pt; color: var(--accent); margin: 18px 0 6px; break-after: avoid; }
h3.tool { background: var(--band); border-left: 5px solid var(--accent2); padding: 6px 10px; border-radius: 4px; }
h3.tool .tag { background: var(--accent2); color: #fff; font-size: 9.5pt; padding: 2px 8px; border-radius: 10px;
               margin-right: 8px; vertical-align: 2px; }
p { margin: 6px 0; }
ul, ol { margin: 6px 0; padding-left: 22px; } li { margin: 2px 0; }
li.check { list-style: none; margin-left: -18px; font-size: 11pt; padding: 2px 0; }
table { width: 100%; border-collapse: collapse; margin: 8px 0 12px; font-size: 9.8pt; break-inside: auto; }
tr { break-inside: avoid; }
th { background: var(--accent); color: #fff; text-align: left; padding: 5px 8px; font-weight: 600; }
td { padding: 5px 8px; border-bottom: 1px solid var(--line); vertical-align: top; }
tbody tr:nth-child(even) td { background: #F7F9FB; }
blockquote { margin: 10px 0; padding: 8px 12px; background: var(--band); border-left: 4px solid var(--accent2);
             border-radius: 4px; }
blockquote.warn { background: var(--warn); border-left-color: var(--warnline); }
blockquote p { margin: 3px 0; }
code { font-family: Consolas, monospace; background: #EEF1F4; padding: 0 4px; border-radius: 3px; font-size: 9.5pt; }
.file { font-family: Consolas, monospace; font-size: 9.5pt; background: #EEF1F4; padding: 0 4px; border-radius: 3px; }
strong { color: #0E1A27; }
.pagebreak { break-before: page; }

/* Cover */
section.cover { height: 255mm; display: flex; flex-direction: column; justify-content: center; padding: 0 8mm; }
.kicker { font-size: 14pt; letter-spacing: 3px; text-transform: uppercase; color: var(--accent2); font-weight: 600; }
.cover h1 { font-size: 46pt; line-height: 1.05; margin: 6px 0 4px; color: var(--accent); }
.cover .sub { font-size: 15pt; color: var(--muted); margin-bottom: 28px; }
table.profile { width: 100%; font-size: 12pt; margin-bottom: 30px; }
table.profile th { width: 34%; background: var(--band); color: var(--accent); border-bottom: 2px solid #fff; padding: 9px 12px; }
table.profile td { padding: 9px 12px; background: #fff !important; border-bottom: 1px solid var(--line); }
.timeline { display: grid; grid-template-columns: repeat(5, 1fr); gap: 6px; }
.timeline div { background: var(--band); border-top: 5px solid var(--accent2); padding: 10px 8px; border-radius: 4px;
                display: flex; flex-direction: column; gap: 2px; }
.timeline b { color: var(--accent); font-size: 12pt; } .timeline span { font-size: 9.5pt; color: var(--muted); }
.timeline em { font-style: normal; font-size: 9.5pt; }
.timeline .mock { border-top-color: var(--warnline); background: var(--warn); }
.timeline .exam { border-top-color: #2E8B57; background: var(--good); }

/* Contents */
h2.plain { display: block; }
ol.toc { list-style: none; padding: 0; margin: 10px 0 20px; }
ol.toc li { display: flex; gap: 14px; align-items: center; padding: 9px 4px; border-bottom: 1px solid var(--line); }
.tnum { background: var(--accent); color: #fff; border-radius: 6px; min-width: 32px; height: 32px; display: inline-flex;
        align-items: center; justify-content: center; font-weight: 700; }
.ttl { font-size: 12pt; font-weight: 600; display: flex; flex-direction: column; }
.ttl small { font-size: 9.5pt; font-weight: 400; color: var(--muted); }
.howto { background: var(--good); border-left: 4px solid #2E8B57; padding: 10px 12px; border-radius: 4px; }

/* Templates */
h3.tpl { font-size: 15pt; }
table.log td { height: 9.6mm; } table.log th:nth-child(3) { width: 6%; } table.log th:nth-child(6) { width: 8%; }
table.log th:nth-child(7) { width: 30%; }
table.count td { height: 12mm; text-align: center; } table.count td:first-child { text-align: left; font-weight: 600; }
table.tracker td { height: 9.8mm; vertical-align: middle; } table.tracker td:first-child { font-weight: 700; text-align: center; }
table.log tbody tr:nth-child(even) td, table.tracker tbody tr:nth-child(even) td { background: #F7F9FB; }
"""

page = f"""<!doctype html><html lang='en'><head><meta charset='utf-8'>
<title>IELTS Listening 3-Week Plan</title><style>{css}</style></head>
<body>{cover}{body}</body></html>"""
HTML.write_text(page, encoding="utf-8")

subprocess.run([EDGE, "--headless", "--disable-gpu", "--no-pdf-header-footer", "--print-to-pdf-no-header",
                f"--print-to-pdf={PDF}", HTML.as_uri()], check=True, capture_output=True, timeout=120)
print("wrote", PDF)
