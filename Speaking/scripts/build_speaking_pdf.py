"""Build Speaking/IELTS_Speaking_Band6.5_Guide.pdf from the Markdown guide.

Usage: python build_speaking_pdf.py
Markdown -> styled HTML (cover, contents, one section per page, printable error log) -> PDF via headless Edge.
Same look as Listening/scripts/build_listening_pdf.py.
"""
import re, subprocess, pathlib, html as h

import markdown

ROOT = pathlib.Path(__file__).resolve().parent.parent
MD = ROOT / "IELTS_Speaking_Band6.5_Guide.md"
HTML = ROOT / "scripts" / "_build.html"
PDF = ROOT / "IELTS_Speaking_Band6.5_Guide.pdf"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

text = MD.read_text(encoding="utf-8")

# Title + intro block go on the cover; horizontal rules are replaced by page breaks.
text = text[text.index("## 0."):]
text = re.sub(r"^---\s*$", "", text, flags=re.M)
text = text.replace("- [ ] ", "- ☐ ")
# Python-Markdown needs a blank line before a list that follows a bold line.
text = re.sub(r"(?m)^(\*\*[^\n]+\*\*|[A-Z][^\n|]*:)\n(- |\d+\. )", r"\1\n\n\2", text)

# Lists inside blockquotes also need a blank quote line before them.
text = re.sub(r"(?m)^(> (?!- )[^\n]*)\n(> - )", r"\1\n>\n\2", text)

body = markdown.markdown(text, extensions=["tables", "sane_lists", "fenced_code"])

body = body.replace("<li>☐ ", "<li class='check'>☐ ")
body = body.replace("<blockquote>\n<p>⚠️", "<blockquote class='warn'>\n<p>⚠️")
# Example dialogues (blockquotes starting with a bold Q:) get their own style.
body = body.replace("<blockquote>\n<p><strong>Q:</strong>", "<blockquote class='ex'>\n<p><strong>Q:</strong>")

# One page per main section, with the number in a badge.
sections = []
def h2(m):
    num, title = m.group(1), m.group(2)
    sections.append((num, title))
    return f"</section><section class='chapter'><h2><span class='num'>{num}</span>{title}</h2>"
body = re.sub(r"<h2>(\d+)\.\s*(.+?)</h2>", h2, body)
body = body.replace("</section>", "", 1) + "</section>"

# Sub-headings like "3.2 Answer extenders" get a small number tag.
body = re.sub(r"<h3>(\d+\.\d+)\s+(.+?)</h3>", r"<h3><span class='sub'>\1</span>\2</h3>", body)

# Printable error log: blank rows after the sample, and it starts on a fresh page.
blank = "<tr>" + "<td></td>" * 5 + "</tr>"
body = re.sub(r"<table>(\s*<thead>\s*<tr>\s*<th>Date</th>\s*<th>Part / Question</th>)", r"<table class='log'>\1", body)
body = re.sub(r"(<table class='log'>.*?<tbody>.*?</tr>)\s*<tr>\s*(<td></td>\s*){5}</tr>",
              lambda m: m.group(1) + blank * 16, body, count=1, flags=re.S)
body = body.replace("<h3>Log template</h3>", "<h3 class='tpl pagebreak'>Error Log</h3>")
# Weekly code-count table (printable) after the log.
codes = ["T", "SV", "A", "PL", "HS", "WF", "P", "SH"]
count = ("<h3 class='tpl pagebreak'>Weekly Code Count</h3><table class='count'><thead><tr><th>Week</th>"
         + "".join(f"<th>{c}</th>" for c in codes) + "<th>Next week's drill</th></tr></thead><tbody>"
         + "".join(f"<tr><td>Week {w}</td>" + "<td></td>" * (len(codes) + 1) + "</tr>" for w in range(1, 5))
         + "</tbody></table>")
body = body.replace("<p>At the end of each week, <strong>count the codes",
                    count + "<p>At the end of each week, <strong>count the codes", 1)
# Questions index: keep dates on one line.
body = re.sub(r"<table>(\s*<thead>\s*<tr>\s*<th>Date</th>\s*<th>My question</th>)", r"<table class='qa'>\1", body)
# Fluency tracker: tall blank rows for writing in.
body = re.sub(r"<table>(\s*<thead>\s*<tr>\s*<th>Date</th>\s*<th>Topic</th>\s*<th>Words/min</th>)", r"<table class='log fl'>\1", body)
# Week plans: keep each week's table with its heading.
body = re.sub(r"<h3>(Week \d .+?)</h3>", r"<h3 class='week'>\1</h3>", body)

blurbs = {
    "0": "The four marks and what band 6 vs band 7 sounds like",
    "1": "Parts 1, 2 and 3 and what wins marks in each",
    "2": "Recorder, voice typing, and how to get feedback",
    "3": "Never stop: extenders, fillers, linking words, daily drills",
    "4": "Answer in the question's tense; tense traps; past habits (used to / would)",
    "5": "He/she/it + s, -s/-es spelling, people are, everyone has",
    "6": "a / an / the, fixed phrases, and the HE/SHE fix",
    "7": "Learning chunks, band 7 words, 12 topic groups",
    "8": "Clear sounds for Bangla speakers, stress, intonation",
    "9": "Error codes, printable log and weekly count",
    "10": "A+R+E, the Part 2 notes plan, O+R+E+C",
    "11": "Your 45-minute routine and the week-by-week plan",
    "12": "What to check before and during the test",
    "13": "What we build next",
    "14": "Every doubt I asked, and where the answer is",
    "15": "My own stories, which cue cards they fit, and model answers",
}
toc = "".join(
    f"<li><span class='tnum'>{n}</span><span class='ttl'>{h.escape(t, quote=False)}"
    f"<small>{blurbs.get(n, '')}</small></span></li>" for n, t in sections)

cover = """
<section class='cover'>
  <div class='kicker'>IELTS Speaking</div>
  <h1>My Band 6.5 Guide</h1>
  <div class='sub'>Fluency, accurate grammar and topic vocabulary, A to Z</div>
  <table class='profile'>
    <tr><th>Target</th><td>band <b>6.5</b> minimum (7 if possible)</td></tr>
    <tr><th>Biggest weak point</th><td><b>Fluency</b>: long pauses</td></tr>
    <tr><th>Grammar to fix</th><td>tenses · subject–verb agreement · articles · -s/-es · he/she</td></tr>
    <tr><th>Daily time</th><td>about 45 minutes</td></tr>
  </table>
  <div class='timeline'>
    <div><b>Week 1</b><span>6–12 Nov</span><em>Fix the base + Part 1</em></div>
    <div><b>Week 2</b><span>13–19 Nov</span><em>Part 2 + story tenses</em></div>
    <div><b>Week 3</b><span>20–26 Nov</span><em>Part 3 + longer answers</em></div>
    <div class='mock'><b>Week 4</b><span>27 Nov →</span><em>Mocks + polish</em></div>
    <div class='exam'><b>Exam</b><span>December</span><em>Band 6.5+</em></div>
  </div>
</section>
<section class='contents'>
  <h2 class='plain'>Contents</h2>
  <ol class='toc'>""" + toc + """</ol>
  <div class='howto'><b>How to use this guide:</b> read Sections 0–8 once in the first two days.
  After that, use Section 11 (today's task), Section 10 (answer frameworks) and Section 9 (error log) every day.
  Print the Error Log pages, or copy them into your notebook.
  Section 14 lists every question you have asked; Section 15 is your Story Bank.</div>
</section>
"""

css = """
@page { size: A4; margin: 16mm 15mm 18mm 15mm;
  @bottom-center { content: counter(page); font: 9pt 'Segoe UI', sans-serif; color: #8A94A3; }
  @bottom-right { content: 'IELTS Speaking · Band 6.5 Guide'; font: 8pt 'Segoe UI', sans-serif; color: #B0B8C4; } }
@page :first { @bottom-center { content: none; } @bottom-right { content: none; } }
:root { --ink:#1E1A2C; --muted:#5E6275; --accent:#3B2A6B; --accent2:#6B4FB0; --band:#F1EEF8;
        --line:#DCD8E6; --warn:#FFF6E0; --warnline:#E0A526; --good:#E8F5EC; --goodline:#2E8B57; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; font: 10.5pt/1.5 'Segoe UI', 'Nirmala UI', Calibri, sans-serif; color: var(--ink); background: #fff; }
section.chapter, section.contents { break-before: page; }
h2 { font-size: 19pt; color: var(--accent); margin: 0 0 12px; padding-bottom: 8px;
     border-bottom: 3px solid var(--accent); display: flex; align-items: center; gap: 12px; break-after: avoid; }
h2 .num { background: var(--accent); color: #fff; border-radius: 8px; min-width: 38px; height: 38px;
          display: inline-flex; align-items: center; justify-content: center; font-size: 17pt; }
h3 { font-size: 13pt; color: var(--accent); margin: 18px 0 6px; break-after: avoid; }
h3 .sub { background: var(--band); color: var(--accent2); font-size: 10pt; padding: 1px 7px; border-radius: 10px;
          margin-right: 8px; vertical-align: 2px; }
h3.week { background: var(--band); border-left: 5px solid var(--accent2); padding: 6px 10px; border-radius: 4px; }
p { margin: 6px 0; }
ul, ol { margin: 6px 0; padding-left: 22px; } li { margin: 2px 0; }
li.check { list-style: none; margin-left: -18px; font-size: 11pt; padding: 2px 0; }
table { width: 100%; border-collapse: collapse; margin: 8px 0 12px; font-size: 9.5pt; break-inside: auto; }
tr { break-inside: avoid; }
th { background: var(--accent); color: #fff; text-align: left; padding: 5px 8px; font-weight: 600; }
td { padding: 3px 8px; border-bottom: 1px solid var(--line); vertical-align: top; }
tbody tr:nth-child(even) td { background: #F8F7FB; }
blockquote { margin: 10px 0; padding: 8px 12px; background: var(--band); border-left: 4px solid var(--accent2);
             border-radius: 4px; break-inside: avoid; }
blockquote.warn { background: var(--warn); border-left-color: var(--warnline); }
blockquote.ex { background: var(--good); border-left-color: var(--goodline); }
blockquote p { margin: 3px 0; }
pre { background: #F6F4FA; border: 1.5px dashed var(--accent2); border-radius: 6px; padding: 10px 14px;
      font-size: 10.5pt; line-height: 1.7; break-inside: avoid; }
pre code { background: none; padding: 0; font-size: 10.5pt; }
code { font-family: Consolas, monospace; background: #EFECF5; padding: 0 4px; border-radius: 3px; font-size: 9.5pt; }
strong { color: #140F22; } th strong { color: inherit; }
.pagebreak { break-before: page; }
p:has(+ table), p:has(+ blockquote) { break-after: avoid; }

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
.timeline .exam { border-top-color: var(--goodline); background: var(--good); }

/* Contents */
h2.plain { display: block; }
ol.toc { list-style: none; padding: 0; margin: 6px 0 14px; }
ol.toc li { display: flex; gap: 12px; align-items: center; padding: 2px 4px; border-bottom: 1px solid var(--line); }
.tnum { background: var(--accent); color: #fff; border-radius: 6px; min-width: 27px; height: 27px; display: inline-flex;
        align-items: center; justify-content: center; font-weight: 700; }
.ttl { font-size: 11pt; font-weight: 600; display: flex; flex-direction: column; }
.ttl small { font-size: 9.5pt; font-weight: 400; color: var(--muted); }
.howto { background: var(--good); border-left: 4px solid var(--goodline); padding: 10px 12px; border-radius: 4px; }

table.qa td:first-child { white-space: nowrap; }
/* Printable templates */
h3.tpl { font-size: 15pt; }
table.log td { height: 10mm; }
table.log th:nth-child(1) { width: 10%; } table.log th:nth-child(2) { width: 18%; }
table.log:not(.fl) th:nth-child(5) { width: 8%; } table.fl th:nth-child(6) { width: 30%; }
table.log tbody tr:nth-child(even) td { background: #F8F7FB; }
table.count td { height: 12mm; text-align: center; } table.count td:first-child { text-align: left; font-weight: 600; }
table.count th:last-child { width: 26%; }
"""

page = f"""<!doctype html><html lang='en'><head><meta charset='utf-8'>
<title>IELTS Speaking Band 6.5 Guide</title><style>{css}</style></head>
<body>{cover}{body}</body></html>"""
HTML.write_text(page, encoding="utf-8")

import time
before = PDF.stat().st_mtime if PDF.exists() else 0
subprocess.run([EDGE, "--headless", "--disable-gpu", "--no-pdf-header-footer", "--print-to-pdf-no-header",
                f"--print-to-pdf={PDF}", HTML.as_uri()], check=True, capture_output=True, timeout=120)
# Edge can return before the file is written; wait for it.
for _ in range(60):
    if PDF.exists() and PDF.stat().st_mtime > before:
        time.sleep(1); break
    time.sleep(0.5)
print("wrote", PDF)
