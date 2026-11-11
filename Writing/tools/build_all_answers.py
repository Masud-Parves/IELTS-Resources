"""Merge all 10 Model Answer Sheets into one phone-sized PDF: each IELTS Liz question and its sample answer only.

Usage (from the Writing folder, after the sheets have been built):
  python tools/build_all_answers.py Output/T2_All_Model_Answers_Mobile.pdf

Questions come from source/NN_Topic_Model_Answers.md (already typo-fixed), answers from
source/model_answers/NN_Topic/essays_*.txt. Labels, [[ ]] marks and bold are removed, so the
text reads as a plain essay. A question answered in two sheets shows both answers.
"""
import glob, html, os, re, subprocess, sys, tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from model_count import parse, clean
from build_pdf import find_browser

W = Path(__file__).resolve().parent.parent
CSS = '''
@page { size: 90mm 160mm; margin: 6mm 5mm 7mm; }
html { font-size: 12.5pt; }
body { font-family: Georgia, "Times New Roman", serif; line-height: 1.5; color: #1a1a1a; margin: 0; }
h1 { font-size: 17pt; white-space: nowrap; line-height: 1.25; margin: 2mm 0 6mm; color: #1f3a5f; }
.sub { font-size: 12pt; color: #555; }
body > .sub:first-child { margin-top: 30mm; }
h2 { font-size: 13.5pt; white-space: nowrap; color: #fff; background: #1f3a5f; padding: 3mm; margin: 0 0 4mm; break-before: page; }
.q { break-inside: avoid; margin: 0 0 3mm; }
.code { font-family: "Segoe UI", Arial, sans-serif; font-size: 10pt; font-weight: 700; color: #1f3a5f; margin: 6mm 0 1.5mm; break-after: avoid; }
.question { font-style: italic; background: #eef2f7; border-left: 3px solid #1f3a5f; padding: 2mm 2.5mm; margin: 0 0 3mm; break-after: avoid; }
p { margin: 0 0 2.5mm; text-align: left; }
.alt { font-family: "Segoe UI", Arial, sans-serif; font-size: 9.5pt; color: #777; margin: 3mm 0 1.5mm; }
hr { border: none; border-top: 1px solid #ccd; margin: 5mm 0 0; }
'''

def plain(s):
    return html.escape(re.sub(r'\s+', ' ', clean(s)).strip())

def main():
    out = Path(sys.argv[1]).resolve()
    sheets = sorted(glob.glob(str(W / 'source' / '[01]*_Model_Answers.md')))
    chapters, seen = [], {}
    for sheet in sheets:
        md = open(sheet, encoding='utf-8').read()
        chapter = re.search(r'Chapter \d+ · (.*?) · \d+ IELTS Liz Questions', md).group(1)
        questions = dict(re.findall(r'### \d+\. ([A-Z]{3}-\d+) — .*?\n\n<div class="question">(.*?)</div>', md, re.S))
        folder = W / 'source' / 'model_answers' / Path(sheet).name.replace('_Model_Answers.md', '')
        items = []
        for d in parse(sorted(glob.glob(str(folder / 'essays_*.txt')))):
            paras = [plain(d[k]) for k in ('I', 'B1', 'B2', 'C')]
            if d['code'] in seen:          # second answer to a question from an earlier sheet
                seen[d['code']].append(paras)
                continue
            seen[d['code']] = [paras]
            items.append((d['code'], questions[d['code']], seen[d['code']]))
        chapters.append((chapter, items))

    total = sum(len(i) for _, i in chapters)
    body = [f'<p class="sub">IELTS Writing</p><h1>Task 2 Model Answers</h1><p class="sub">All {total} IELTS Liz questions · 10 topics</p>']
    n = 0
    for chapter, items in chapters:
        body.append(f'<h2>{html.escape(chapter)}</h2>')
        for code, question, answers in items:
            n += 1
            body.append(f'<div class="code">{n} · {code}</div><div class="question">{question}</div>')
            for k, paras in enumerate(answers):
                if len(answers) > 1:
                    body.append(f'<div class="alt">Sample answer {k + 1}</div>')
                body.append(''.join(f'<p>{p}</p>' for p in paras))
            body.append('<hr>')
    page = f"<!doctype html><html lang='en'><head><meta charset='utf-8'><title>All Model Answers</title><style>{CSS}</style></head><body>{''.join(body)}</body></html>"
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / 'page.html'
        p.write_text(page, encoding='utf-8')
        subprocess.run([find_browser(), '--headless=new', '--disable-gpu', '--no-pdf-header-footer',
                        '--generate-pdf-document-outline', f'--user-data-dir={Path(tmp) / "profile"}',
                        f'--print-to-pdf={out}', p.as_uri()], check=True, capture_output=True, timeout=300)
    print(f'Built {out} ({out.stat().st_size // 1024} KB), {total} questions, {sum(len(a) for _, i in chapters for _, _, a in i)} answers')

if __name__ == '__main__':
    main()
