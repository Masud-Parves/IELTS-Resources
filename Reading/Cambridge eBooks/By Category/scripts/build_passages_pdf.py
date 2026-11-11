"""Typeset the 12 Reading passages of a Cambridge book (text only, no questions) into one PDF.

Usage: python build_passages_pdf.py N
Reads working/C{N}/text/T#P#.json (from passages_extract.py) and optional figures listed in
working/C{N}/passages_C{N}.json ("figure": {"image": path, "after_para": i, "width_cm": w}).
Writes Output/Cambridge_{N}_Reading_Passages_Only.pdf. Body 16.5pt Times, as in build_book_pdf.py.
"""
import json, re, sys, pathlib
from xml.sax.saxutils import escape

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table,
                                TableStyle, KeepTogether, Image, CondPageBreak)

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping

ROOT = pathlib.Path(__file__).resolve().parent.parent
# Times New Roman TTF: looks like Times but covers characters the built-in Times lacks (e.g. ş, ₂)
for name, f in [("TNR", "times.ttf"), ("TNR-Bold", "timesbd.ttf"), ("TNR-Italic", "timesi.ttf"), ("TNR-BoldItalic", "timesbi.ttf")]:
    pdfmetrics.registerFont(TTFont(name, f"C:/Windows/Fonts/{f}"))
for b, i, n in [(0, 0, "TNR"), (1, 0, "TNR-Bold"), (0, 1, "TNR-Italic"), (1, 1, "TNR-BoldItalic")]:
    addMapping("TNR", b, i, n)
N = sys.argv[1]
work = ROOT / "working" / f"C{N}"
cfg = json.loads((work / f"passages_C{N}.json").read_text(encoding="utf-8"))
OUT = ROOT / "Output" / f"Cambridge_{N}_Reading_Passages_Only.pdf"
OFF = cfg.get("test_offset", 0)  # Cambridge 12 numbers its Academic tests 5-8

MARGIN = 1.5 * cm
PAGE_W, PAGE_H = A4
DARK = colors.HexColor('#0C0C0C')
GRAY = colors.HexColor('#7A7A7A')
ACCENT = colors.HexColor('#1A3A5C')
BAND = colors.HexColor('#EDF2F7')

doc_title = ParagraphStyle('DocTitle', fontName='Helvetica-Bold', fontSize=22, leading=26,
                           textColor=DARK, alignment=TA_CENTER, spaceAfter=4)
doc_sub = ParagraphStyle('DocSub', fontName='Helvetica', fontSize=12, leading=15,
                         textColor=GRAY, alignment=TA_CENTER, spaceAfter=10)
toc_style = ParagraphStyle('Toc', fontName='Helvetica', fontSize=11.5, leading=15, textColor=DARK)
band_style = ParagraphStyle('Band', fontName='Helvetica-Bold', fontSize=11, leading=13,
                            textColor=ACCENT)
title_style = ParagraphStyle('PTitle', fontName='TNR-Bold', fontSize=22, leading=26,
                             textColor=DARK, alignment=TA_CENTER, spaceBefore=6, spaceAfter=4)
standfirst = ParagraphStyle('PSub', fontName='TNR-Italic', fontSize=16.5, leading=21,
                            textColor=colors.HexColor('#333333'), alignment=TA_CENTER, spaceAfter=10)
body = ParagraphStyle('Body', fontName='TNR', fontSize=16.5, leading=21.5,
                      textColor=colors.black, alignment=TA_LEFT, spaceAfter=8)
note_style = ParagraphStyle('Note', fontName='TNR-Italic', fontSize=12.5, leading=16,
                            textColor=colors.HexColor('#333333'), spaceBefore=2, spaceAfter=4)


def curly(t):
    t = re.sub(r"(^|[\s(\[—–-])'", r"\1‘", t)
    t = t.replace("'", "’")
    t = re.sub(r'(^|[\s(\[—–-])"', r"\1“", t)
    return t.replace('"', "”")


def markup(t):
    return escape(curly(t)).replace("CO₂", "CO<sub>2</sub>")


def on_page(c, d):
    c.saveState()
    c.setFont('Helvetica', 9); c.setFillColor(GRAY)
    c.drawString(MARGIN, PAGE_H - 1.0 * cm, f"Cambridge IELTS {N}  ·  Academic Reading Passages")
    c.drawRightString(PAGE_W - MARGIN, 0.9 * cm, str(d.page))
    c.restoreState()


passages = [json.loads((work / "text" / f'{p["test"]}{p["passage"]}.json').read_text(encoding="utf-8"))
            for p in cfg["passages"]]
story = [Paragraph(f"Cambridge IELTS {N}", doc_title),
         Paragraph(f"Academic Reading: the 12 passages only (Tests {1 + OFF}–{4 + OFF})", doc_sub)]
def toc_title(p):
    if not p["title"]:
        return "<i>(no title in the book)</i>"
    return markup(p["title"].title() if p["title"].isupper() else p["title"])


rows = [[Paragraph(f'<b>Test {int(p["test"][1]) + OFF} · Passage {p["passage"][1]}</b>', toc_style),
         Paragraph(toc_title(p), toc_style)]
        for p in passages]
toc = Table(rows, colWidths=[4.6 * cm, PAGE_W - 2 * MARGIN - 4.6 * cm])
toc.setStyle(TableStyle([('LINEBELOW', (0, 0), (-1, -2), 0.4, colors.HexColor('#D6D6D6')),
                         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                         ('TOPPADDING', (0, 0), (-1, -1), 3), ('BOTTOMPADDING', (0, 0), (-1, -1), 3)]))
story += [toc, Spacer(1, 14)]

for conf, p in zip(cfg["passages"], passages):
    band = Table([[Paragraph(f'TEST {int(p["test"][1]) + OFF}  ·  READING PASSAGE {p["passage"][1]}', band_style)]],
                 colWidths=[PAGE_W - 2 * MARGIN])
    band.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), BAND),
                              ('LINEBEFORE', (0, 0), (0, -1), 3, ACCENT),
                              ('TOPPADDING', (0, 0), (-1, -1), 5), ('BOTTOMPADDING', (0, 0), (-1, -1), 5)]))
    head = [band, Paragraph(markup(p["title"]), title_style) if p["title"] else Spacer(1, 10)]
    if p["subtitle"]:
        head.append(Paragraph(markup(p["subtitle"]), standfirst))
    paras = []
    for q in p["paras"]:
        lab = f'<font name="Helvetica-Bold" color="#1A3A5C">{q["label"]}</font>&nbsp;&nbsp;' if q["label"] else ""
        paras.append(Paragraph(lab + markup(q["text"]), body))
    fig = conf.get("figure")
    if fig:
        img = Image(str(work / fig["image"]))
        w = fig["width_cm"] * cm
        img.drawWidth, img.drawHeight = w, w * img.imageHeight / img.imageWidth
        paras.insert(fig["after_para"], KeepTogether([img, Spacer(1, 8)]))
    story += [CondPageBreak(5 * cm), KeepTogether(head + paras[:1])] + paras[1:]
    story += [Paragraph(markup(n), note_style) for n in p["notes"]]
    story.append(Spacer(1, 16))

doc = BaseDocTemplate(str(OUT), pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN,
                      topMargin=MARGIN, bottomMargin=MARGIN,
                      title=f"Cambridge IELTS {N} - Reading Passages", author="Cambridge IELTS (study copy)")
doc.addPageTemplates([PageTemplate('p', [Frame(MARGIN, MARGIN, PAGE_W - 2 * MARGIN, PAGE_H - 2 * MARGIN, id='f')],
                                   onPage=on_page)])
doc.build(story)
print(OUT, doc.page, "pages")
