"""Build Speaking/IELTS_Speaking_Person_Topics.pdf from the Markdown file (simple layout).

Usage: python build_person_pdf.py
Sections: 1 Vocabulary, 2 Reusable Sentences, 3 Cue Cards. No cover, no contents.
"""
import re, subprocess, pathlib, time

import markdown

ROOT = pathlib.Path(__file__).resolve().parent.parent
MD = ROOT / "IELTS_Speaking_Person_Topics.md"
HTML = ROOT / "scripts" / "_build_person.html"
PDF = ROOT / "IELTS_Speaking_Person_Topics.pdf"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

text = MD.read_text(encoding="utf-8")
text = re.sub(r"^---\s*$", "", text, flags=re.M)
text = re.sub(r"(?m)^(\*\*[^\n]+\*\*|[A-Z][^\n|]*:)\n(- |\d+\. )", r"\1\n\n\2", text)

body = markdown.markdown(text, extensions=["tables", "sane_lists"])

# Each main section starts on a new page.
body = re.sub(r"<h2>(\d+)\.\s*(.+?)</h2>", r"<h2 class='sec'><span class='num'>\1</span>\2</h2>", body)
first = body.find("<h2 class='sec'>")
body = body[:first] + body[first:].replace("<h2 class='sec'>", "<h2 class='sec first'>", 1)
# Cue cards: a box that doesn't split across pages.
body = re.sub(r"<h4>Card (\d+) · (.+?)</h4>", r"<h4 class='card'><span class='cn'>\1</span>\2</h4>", body)
body = re.sub(r"(<h4 class='card'>.*?)(?=<h4 class='card'>|<h2|$)", r"<div class='cardbox'>\1</div>", body, flags=re.S)

css = """
/* Same look as the Writing Idea Bank (Writing/tools/style.css): Georgia 15.5pt body, Segoe UI headings, 14pt tables. */
@page { size: A4; margin: 18mm 16mm 20mm 16mm;
  @bottom-center { content: "Page " counter(page) " / " counter(pages); font-family: "Segoe UI", Arial, sans-serif;
                   font-size: 10pt; color: #777; } }
:root { --ink: #1d1d1f; --accent: #1f4e79; --accent-soft: #e8f0f8; }
* { box-sizing: border-box; }
html { font-size: 15.5pt; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family: "Georgia", "Cambria", "Nirmala UI", serif; color: var(--ink); line-height: 1.6; margin: 0; background: #fff; }
em { font-style: normal; }
h1, h2, h3, h4 { font-family: "Segoe UI", "Nirmala UI", Arial, sans-serif; color: var(--accent); line-height: 1.3; break-after: avoid; }
h1 { font-size: 26pt; margin: 0 0 8pt; border-bottom: 3px solid var(--accent); padding-bottom: 6pt; }
h2.sec { font-size: 21pt; margin: 0 0 8pt; border-bottom: 2px solid var(--accent-soft); padding-bottom: 4pt;
         display: flex; align-items: center; gap: 10pt; break-before: auto; margin-top: 22pt; }
h2.sec.first { break-before: auto; margin-top: 14pt; }
h2 .num { background: var(--accent); color: #fff; border-radius: 6px; min-width: 30pt; height: 30pt;
          display: inline-flex; align-items: center; justify-content: center; font-size: 17pt; }
h3 { font-size: 18pt; margin: 18pt 0 6pt; }
p { margin: 0 0 10pt; }
ul { margin: 4pt 0 10pt; padding-left: 22pt; } li { margin-bottom: 4pt; }
strong { color: #0b2f52; }
table { width: 100%; border-collapse: collapse; margin: 8pt 0 14pt; font-size: 14pt; }
th, td { border: 1px solid #c9d3de; padding: 5pt 7pt; vertical-align: top; text-align: left; }
th { background: var(--accent); color: #fff; font-family: "Segoe UI", Arial, sans-serif; }
tr:nth-child(even) td { background: #f6f8fb; }
tr { break-inside: avoid; }
td:nth-child(2) { font-family: "Nirmala UI", "Kalpurush", sans-serif; }
td:first-child { font-weight: 700; width: 30%; }
.cardbox { border: 1px solid #c9d3de; border-left: 5px solid var(--accent); border-radius: 8px;
           padding: 8pt 14pt 6pt; margin: 0 0 14pt; break-inside: auto; background: #fbfcfe;
           -webkit-box-decoration-break: clone; box-decoration-break: clone; }
/* cards and sections flow one after another with no empty space; a card title never sits alone at a page bottom */
.cardbox > p:first-of-type { break-after: avoid; }
.cardbox li { break-inside: avoid; }
blockquote > p:first-child { break-after: avoid; }
p { orphans: 2; widows: 2; }
h4.card { font-size: 16pt; margin: 2pt 0 6pt; display: flex; gap: 8pt; align-items: baseline; }
h4.card .cn { background: var(--accent); color: #fff; border-radius: 5px; min-width: 32pt; text-align: center;
              padding: 0 6pt; font-size: 14pt; flex-shrink: 0; }
.cardbox p { margin: 2pt 0 4pt; } .cardbox ul { margin: 2pt 0 6pt; } .cardbox li { margin-bottom: 2pt; }
blockquote { margin: 8pt 0 4pt; padding: 6pt 12pt; background: var(--accent-soft); border-left: 5px solid var(--accent); border-radius: 4px; }
blockquote p { margin: 0; }
"""

page = f"""<!doctype html><html lang='en'><head><meta charset='utf-8'>
<title>IELTS Speaking Person Topics</title><style>{css}</style></head><body>{body}</body></html>"""
HTML.write_text(page, encoding="utf-8")

before = PDF.stat().st_mtime if PDF.exists() else 0
subprocess.run([EDGE, "--headless", "--disable-gpu", "--no-pdf-header-footer", "--print-to-pdf-no-header",
                f"--print-to-pdf={PDF}", HTML.as_uri()], check=True, capture_output=True, timeout=120)
# Edge can return before the file is written; wait for it.
for _ in range(60):
    if PDF.exists() and PDF.stat().st_mtime > before:
        time.sleep(1); break
    time.sleep(0.5)
print("wrote", PDF)
