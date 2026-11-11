"""Typeset every List of Headings set of Cambridge 10-14: passage, its heading question, then one answer sheet.

Usage: python build_headings_pdf.py
Reads working/headings/questions.json (from headings_extract.py), working/headings/answers.json
(official answers, one-line explanations, text fixes) and working/C{N}/text/T#P#.json (from passages_extract.py).
Writes Output/Cambridge_10-14_List_of_Headings.pdf. Same look as build_passages_pdf.py; body 16.5pt.
"""
import json, re, pathlib
from xml.sax.saxutils import escape

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table,
                                TableStyle, KeepTogether, PageBreak, Flowable)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping

ROOT = pathlib.Path(__file__).resolve().parent.parent
for name, f in [("TNR", "times.ttf"), ("TNR-Bold", "timesbd.ttf"), ("TNR-Italic", "timesi.ttf"), ("TNR-BoldItalic", "timesbi.ttf")]:
    pdfmetrics.registerFont(TTFont(name, f"C:/Windows/Fonts/{f}"))
for b, i, n in [(0, 0, "TNR"), (1, 0, "TNR-Bold"), (0, 1, "TNR-Italic"), (1, 1, "TNR-BoldItalic")]:
    addMapping("TNR", b, i, n)
work = ROOT / "working" / "headings"
OUT = ROOT / "Output" / "Cambridge_10-14_List_of_Headings.pdf"

MARGIN = 1.5 * cm
PAGE_W, PAGE_H = A4
TEXT_W = PAGE_W - 2 * MARGIN
DARK = colors.HexColor('#0C0C0C')
GRAY = colors.HexColor('#7A7A7A')
LINE = colors.HexColor('#D6D6D6')
ACCENT = colors.HexColor('#1A3A5C')
BAND = colors.HexColor('#EDF2F7')
SHADE = colors.HexColor('#F5F5F5')

doc_title = ParagraphStyle('DocTitle', fontName='Helvetica-Bold', fontSize=22, leading=26,
                           textColor=DARK, alignment=TA_CENTER, spaceAfter=4)
doc_sub = ParagraphStyle('DocSub', fontName='Helvetica', fontSize=14, leading=18,
                         textColor=GRAY, alignment=TA_CENTER, spaceAfter=10)
toc_style = ParagraphStyle('Toc', fontName='Helvetica', fontSize=14, leading=18, textColor=DARK)
band_style = ParagraphStyle('Band', fontName='Helvetica-Bold', fontSize=14, leading=17, textColor=ACCENT)
title_style = ParagraphStyle('PTitle', fontName='TNR-Bold', fontSize=22, leading=26,
                             textColor=DARK, alignment=TA_CENTER, spaceBefore=6, spaceAfter=4)
standfirst = ParagraphStyle('PSub', fontName='TNR-Italic', fontSize=16.5, leading=21,
                            textColor=colors.HexColor('#333333'), alignment=TA_CENTER, spaceAfter=10)
body = ParagraphStyle('Body', fontName='TNR', fontSize=16.5, leading=21.5,
                      textColor=colors.black, alignment=TA_LEFT, spaceAfter=8)
note_style = ParagraphStyle('Note', fontName='TNR-Italic', fontSize=16, leading=20,
                            textColor=colors.HexColor('#333333'), spaceBefore=2, spaceAfter=4)
qhead = ParagraphStyle('QHead', fontName='TNR-Bold', fontSize=18, leading=22, textColor=DARK,
                       spaceBefore=6, spaceAfter=6)
instr = ParagraphStyle('Instr', fontName='TNR-Italic', fontSize=16.5, leading=21, textColor=DARK, spaceAfter=5)
instr_plain = ParagraphStyle('InstrP', parent=instr, fontName='TNR')
box_head = ParagraphStyle('BoxHead', fontName='TNR-Bold', fontSize=17, leading=21, alignment=TA_CENTER, textColor=DARK)
box_cell = ParagraphStyle('BoxCell', fontName='TNR', fontSize=16.5, leading=20, textColor=DARK)
num_cell = ParagraphStyle('NumCell', fontName='TNR-Bold', fontSize=16.5, leading=20, textColor=DARK)
sheet_title = ParagraphStyle('Sheet', fontName='Helvetica-Bold', fontSize=22, leading=26, textColor=DARK,
                             alignment=TA_CENTER, spaceAfter=8)
ans_band = ParagraphStyle('AnsBand', fontName='TNR-Bold', fontSize=16.5, leading=20, textColor=ACCENT)
why_style = ParagraphStyle('Why', fontName='TNR', fontSize=16, leading=19.5, textColor=colors.HexColor('#222222'))

NUM_W, ROM_W = 1.15 * cm, 1.35 * cm
WHY_W = TEXT_W - NUM_W


def curly(t):
    t = re.sub(r"(^|[\s(\[—–-])'", r"\1‘", t)
    t = t.replace("'", "’")
    t = re.sub(r'(^|[\s(\[—–-])"', r"\1“", t)
    return t.replace('"', "”")


def markup(t):
    return escape(curly(t)).replace("CO₂", "CO<sub>2</sub>")


def dashes(t):
    return t.replace("—", "–").replace("G–l", "G–I")


class Mark(Flowable):
    """Zero-height marker: records the page it lands on and adds a PDF bookmark."""
    def __init__(self, key, label):
        super().__init__()
        self.key, self.label = key, label
        self.width = self.height = 0

    def draw(self):
        c = self.canv
        PAGES[self.key] = c.getPageNumber()
        c.bookmarkPage(self.key)
        c.addOutlineEntry(self.label, self.key, 0)


def on_page(c, d):
    c.saveState()
    c.setFont('Helvetica', 9); c.setFillColor(GRAY)
    c.drawString(MARGIN, PAGE_H - 1.0 * cm, "Cambridge IELTS 10–14  ·  List of Headings")
    c.drawRightString(PAGE_W - MARGIN, 0.9 * cm, str(d.page))
    c.restoreState()


questions = json.loads((work / "questions.json").read_text(encoding="utf-8"))
answers = json.loads((work / "answers.json").read_text(encoding="utf-8"))
sets = []
for q, a in zip(questions, answers):
    assert (q["book"], q["test"], q["passage"]) == (a["book"], a["test"], a["passage"])
    n = q["book"]
    cfg = json.loads((ROOT / "working" / f"C{n}" / f"passages_C{n}.json").read_text(encoding="utf-8"))
    p = json.loads((ROOT / "working" / f"C{n}" / "text" / f'{q["test"]}{q["passage"]}.json').read_text(encoding="utf-8"))
    for pair in a.get("fixes", []):
        pat, rep = pair
        hits = 0
        for para in p["paras"]:
            para["text"], k = re.subn(pat, rep, para["text"])
            hits += k
        if not hits:
            print("  fix not applied:", n, q["test"], q["passage"], pat)
    test_no = int(q["test"][1]) + cfg.get("test_offset", 0)  # Cambridge 12 numbers its Academic tests 5-8
    ros = {h["roman"]: h["text"] for h in q["headings"]}
    qs = {x["q"]: x["label"] for x in q["questions"]}
    # checks: every question answered, every answer on the list, no heading used twice
    assert sorted(qs) == [x["q"] for x in a["answers"]], (n, q["test"], sorted(qs))
    assert all(x["roman"] in ros for x in a["answers"]), (n, q["test"])
    used = [x["roman"] for x in a["answers"]] + ([q["example"]["roman"]] if q["example"] else [])
    assert len(used) == len(set(used)), (n, q["test"], used)
    sets.append({"n": n, "test_no": test_no, "pno": q["passage"][1], "q": q, "a": a, "p": p, "ros": ros, "qs": qs})


def nice_title(t):
    return t.title() if t.isupper() else t


def qrange(s):
    nums = sorted(s["qs"])
    return f"{nums[0]}–{nums[-1]}"


def question_block(s):
    q = s["q"]
    out = [Paragraph(f"Questions {qrange(s)}", qhead)]
    for i, line in enumerate(q["instructions"]):
        out.append(Paragraph(markup(dashes(line)), instr_plain if i == 0 else instr))
    out.append(Spacer(1, 4))
    rows = [[Paragraph("List of Headings", box_head), ""]]
    rows += [[Paragraph(f'<b>{h["roman"]}</b>', box_cell), Paragraph(markup(h["text"]), box_cell)] for h in q["headings"]]
    box = Table(rows, colWidths=[1.5 * cm, TEXT_W - 1.5 * cm])
    box.setStyle(TableStyle([('SPAN', (0, 0), (1, 0)), ('BOX', (0, 0), (-1, -1), 0.8, GRAY),
                             ('BACKGROUND', (0, 0), (-1, -1), SHADE), ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                             ('TOPPADDING', (0, 0), (-1, -1), 2.5), ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5)]))
    out += [box, Spacer(1, 10)]
    if q["example"]:
        ex = Table([[Paragraph("<b>Example</b>", box_cell), Paragraph("<b>Answer</b>", box_cell)],
                    [Paragraph(q["example"]["label"], box_cell), Paragraph(q["example"]["roman"], box_cell)]],
                   colWidths=[7 * cm, 4 * cm], hAlign='LEFT')
        ex.setStyle(TableStyle([('BOX', (0, 0), (-1, -1), 0.6, LINE), ('BACKGROUND', (0, 0), (-1, -1), SHADE),
                                ('TOPPADDING', (0, 0), (-1, -1), 2), ('BOTTOMPADDING', (0, 0), (-1, -1), 3)]))
        out += [ex, Spacer(1, 8)]
    # two columns, read down: number box + "Paragraph A"
    items = q["questions"]
    half = (len(items) + 1) // 2
    left, right = items[:half], items[half:]
    def cells(it):
        return [Paragraph(str(it["q"]), num_cell), Paragraph(it["label"], box_cell)] if it else ["", ""]
    grid = [cells(l) + cells(right[i] if i < len(right) else None) for i, l in enumerate(left)]
    qt = Table(grid, colWidths=[NUM_W, TEXT_W / 2 - NUM_W] * 2, hAlign='LEFT')
    qt.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('TOPPADDING', (0, 0), (-1, -1), 3),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 4), ('LINEBELOW', (0, 0), (-1, -1), 0.3, LINE)]))
    out.append(qt)
    return out


def passage_block(s, i):
    p = s["p"]
    band = Table([[Paragraph(f'CAMBRIDGE {s["n"]}  ·  TEST {s["test_no"]}  ·  READING PASSAGE {s["pno"]}', band_style)]],
                 colWidths=[TEXT_W])
    band.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), BAND), ('LINEBEFORE', (0, 0), (0, -1), 3, ACCENT),
                              ('TOPPADDING', (0, 0), (-1, -1), 5), ('BOTTOMPADDING', (0, 0), (-1, -1), 5)]))
    label = f'C{s["n"]} Test {s["test_no"]} P{s["pno"]}: {nice_title(p["title"])}'
    head = [Mark(f"p{i}", label), band, Paragraph(markup(p["title"]), title_style)]
    if p["subtitle"]:
        head.append(Paragraph(markup(p["subtitle"]), standfirst))
    paras = []
    for q in p["paras"]:
        lab = f'<font name="Helvetica-Bold" color="#1A3A5C">{q["label"]}</font>&nbsp;&nbsp;' if q["label"] else ""
        paras.append(Paragraph(lab + markup(q["text"]), body))
    out = [PageBreak(), KeepTogether(head + paras[:1])] + paras[1:]
    out += [Paragraph(markup(n), note_style) for n in p["notes"]]
    out += [Spacer(1, 10), KeepTogether(question_block(s))]
    return out


def answer_sheet():
    out = [PageBreak(), Mark("answers", "Answer Sheet"), Paragraph("Answer Sheet", sheet_title)]
    for s in sets:
        title = f'Cambridge {s["n"]}, Test {s["test_no"]}, Passage {s["pno"]}: {nice_title(s["p"]["title"])} (Q{qrange(s)})'
        band = Table([[Paragraph(markup(title), ans_band)]], colWidths=[TEXT_W])
        band.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), BAND), ('LINEBEFORE', (0, 0), (0, -1), 3, ACCENT),
                                  ('TOPPADDING', (0, 0), (-1, -1), 4), ('BOTTOMPADDING', (0, 0), (-1, -1), 5)]))
        rows = []
        for a in s["a"]["answers"]:
            letter = s["qs"][a["q"]].split()[1]
            w = stringWidth(curly(a["why"]).replace("CO₂", "CO2"), why_style.fontName, why_style.fontSize)
            if w > WHY_W - 2:
                print(f'  too long for one line ({w:.0f} > {WHY_W:.0f}): C{s["n"]} Q{a["q"]}: {a["why"]}')
            head = Paragraph(f'<b>{a["roman"]}</b>&nbsp;&nbsp;({letter})&nbsp;&nbsp;<b>{markup(s["ros"][a["roman"]])}</b>', box_cell)
            cell = [head, Paragraph(markup(a["why"]), why_style)]
            rows.append([Paragraph(str(a["q"]), num_cell), cell])
        style = TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (1, 0), (1, -1), 0),
                            ('RIGHTPADDING', (1, 0), (1, -1), 0), ('TOPPADDING', (0, 0), (-1, -1), 3),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 5), ('LINEBELOW', (0, 0), (-1, -1), 0.3, LINE)])
        # band stays with the first answer; the rest of the set may run on to the next page
        out += [Spacer(1, 8), KeepTogether([band, Spacer(1, 2), Table(rows[:1], colWidths=[NUM_W, WHY_W], style=style)]),
                Table(rows[1:], colWidths=[NUM_W, WHY_W], style=style)]
    return out


def build(pages):
    total = sum(len(s["qs"]) for s in sets)
    story = [Paragraph("Cambridge IELTS 10–14", doc_title),
             Paragraph(f"Academic Reading: List of Headings only ({len(sets)} passages, {total} questions)", doc_sub)]
    rows = [[Paragraph(f'<b>C{s["n"]} · Test {s["test_no"]} · P{s["pno"]}</b>', toc_style),
             Paragraph(markup(nice_title(s["p"]["title"])), toc_style),
             Paragraph(f'Q{qrange(s)}', toc_style),
             Paragraph(str(pages.get(f"p{i}", "")), toc_style)] for i, s in enumerate(sets)]
    rows.append([Paragraph('<b>Answer Sheet</b>', toc_style), Paragraph("Official answers, with a one-line reason for each", toc_style),
                 "", Paragraph(str(pages.get("answers", "")), toc_style)])
    toc = Table(rows, colWidths=[5.2 * cm, TEXT_W - 9.2 * cm, 2.6 * cm, 1.4 * cm])
    toc.setStyle(TableStyle([('LINEBELOW', (0, 0), (-1, -2), 0.4, LINE), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                             ('TOPPADDING', (0, 0), (-1, -1), 3), ('BOTTOMPADDING', (0, 0), (-1, -1), 3)]))
    story += [toc]
    for i, s in enumerate(sets):
        story += passage_block(s, i)
    story += answer_sheet()
    doc = BaseDocTemplate(str(OUT), pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN,
                          topMargin=MARGIN, bottomMargin=MARGIN,
                          title="Cambridge IELTS 10-14 - List of Headings", author="Cambridge IELTS (study copy)")
    doc.addPageTemplates([PageTemplate('p', [Frame(MARGIN, MARGIN, TEXT_W, PAGE_H - 2 * MARGIN, id='f')], onPage=on_page)])
    doc.build(story)
    return doc.page


# two passes: the first finds the page numbers the contents table shows
PAGES = {}
build({})
first = dict(PAGES)
pages = build(first)
assert first == PAGES, "contents page numbers moved between passes"
print(OUT, pages, "pages,", len(sets), "passages,", sum(len(s["qs"]) for s in sets), "questions")
