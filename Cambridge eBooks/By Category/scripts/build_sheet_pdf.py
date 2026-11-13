"""Typeset every set of one question type from one or more Cambridge books: passage, its questions, then one
answer sheet with the official answer and a one-line reason for each question.

Usage: python build_sheet_pdf.py TYPE N              -> Output/Cambridge_{N}_{name}.pdf
       python build_sheet_pdf.py TYPE 10 11 12 13 14 -> Output/Cambridge_10-14_{name}.pdf (books in order, one answer sheet)
TYPE is tfng (TRUE/FALSE/NOT GIVEN and YES/NO/NOT GIVEN) or mi (Matching Information); see SHEETS.
Reads working/TYPE/questions_C{N}.json (from tfng_extract.py / mi_extract.py), working/TYPE/keys.json (official answers),
working/TYPE/answers_C{N}.json (reasons, passage text "fixes", "join": ends of wrongly split paragraphs) and working/C{N}/text/T#P#.json.
Writes Output/Cambridge_{N}_TFNG_YNNG.pdf. Same look as build_headings_pdf.py; body 16.5pt.
Passages without paragraph letters get small gray ¶ numbers, which the reasons refer to as "Para n".
"""
import json, re, sys, pathlib
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
SHEETS = {  # file name part, running header, title-page subtitle, PDF title
    "tfng": ("TFNG_YNNG", "TRUE/FALSE/NOT GIVEN and YES/NO/NOT GIVEN",
             "TRUE/FALSE/NOT GIVEN and YES/NO/NOT GIVEN only", "TFNG and YNNG"),
    "mi": ("Matching_Information", "Matching Information",
           "Matching Information only (which paragraph contains…)", "Matching Information"),
    "me": ("Sentence_Endings", "Matching Sentence Endings",
           "Matching Sentence Endings only", "Matching Sentence Endings"),
}
TYPE = sys.argv[1]
FILE_PART, HEADER, SUBTITLE, PDF_TITLE = SHEETS[TYPE]
BOOKS = [int(a) for a in sys.argv[2:]]
MULTI = len(BOOKS) > 1
N = f"{BOOKS[0]}–{BOOKS[-1]}" if MULTI else str(BOOKS[0])  # for titles
work = ROOT / "working" / TYPE
OUT = ROOT / "Output" / f"Cambridge_{N.replace('–', '-')}_{FILE_PART}.pdf"

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
doc_note = ParagraphStyle('DocNote', fontName='TNR-Italic', fontSize=14, leading=18, textColor=GRAY,
                          alignment=TA_CENTER, spaceBefore=10)
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
box_cell = ParagraphStyle('BoxCell', fontName='TNR', fontSize=16.5, leading=20, textColor=DARK)
def_cell = ParagraphStyle('DefCell', fontName='TNR-Italic', fontSize=16.5, leading=20, textColor=DARK)
box_title = ParagraphStyle('BoxTitle', fontName='TNR-Bold', fontSize=17, leading=21, alignment=TA_CENTER, textColor=DARK)
num_cell = ParagraphStyle('NumCell', fontName='TNR-Bold', fontSize=16.5, leading=20, textColor=DARK)
sheet_title = ParagraphStyle('Sheet', fontName='Helvetica-Bold', fontSize=22, leading=26, textColor=DARK,
                             alignment=TA_CENTER, spaceAfter=8)
ans_band = ParagraphStyle('AnsBand', fontName='TNR-Bold', fontSize=16.5, leading=20, textColor=ACCENT)
stm_style = ParagraphStyle('Stm', fontName='TNR-Italic', fontSize=16, leading=19.5, textColor=colors.HexColor('#555555'))
why_style = ParagraphStyle('Why', fontName='TNR', fontSize=16, leading=19.5, textColor=colors.HexColor('#222222'))

NUM_W = 1.15 * cm
WHY_W = TEXT_W - NUM_W


def curly(t):
    t = re.sub(r"(^|[\s(\[—–-])'", r"\1‘", t)
    t = t.replace("'", "’")
    t = re.sub(r'(^|[\s(\[—–-])"', r"\1“", t)
    return t.replace('"', "”")


def markup(t):
    t = escape(curly(t)).replace("CO₂", "CO<sub>2</sub>")
    return re.sub(r"\^(\d+)", r"<super>\1</super>", t)  # 10^9 -> 10 with superscript 9


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
    c.drawString(MARGIN, PAGE_H - 1.0 * cm, f"Cambridge IELTS {N}  ·  {HEADER}")
    c.drawRightString(PAGE_W - MARGIN, 0.9 * cm, str(d.page))
    c.restoreState()


all_keys = json.loads((work / "keys.json").read_text(encoding="utf-8"))
sets = []
for n, q in [(n, q) for n in BOOKS for q in json.loads((work / f"questions_C{n}.json").read_text(encoding="utf-8"))]:
    cfg = json.loads((ROOT / "working" / f"C{n}" / f"passages_C{n}.json").read_text(encoding="utf-8"))
    OFF = cfg.get("test_offset", 0)  # Cambridge 12 numbers its Academic tests 5-8
    answers = {(a["test"], a["passage"]): a for a in json.loads((work / f"answers_C{n}.json").read_text(encoding="utf-8"))}
    tp = (q["test"], q["passage"])
    k = next(k for k in all_keys if k["book"] == n and (k["test"], k["passage"]) == tp)
    a = answers[tp]
    p = json.loads((ROOT / "working" / f"C{n}" / "text" / f'{q["test"]}{q["passage"]}.json').read_text(encoding="utf-8"))
    for pat, rep in a.get("fixes", []):
        hits = 0
        for field in ("title", "subtitle"):
            p[field], h = re.subn(pat, rep, p[field]); hits += h
        for para in p["paras"]:
            para["text"], h = re.subn(pat, rep, para["text"]); hits += h
        if not hits:
            print("  fix not applied:", n, q["test"], q["passage"], pat)
    for end in a.get("join", []):  # a paragraph wrongly split (e.g. at a page break): join it to the next one
        i = next(i for i, para in enumerate(p["paras"]) if para["text"].endswith(end))
        p["paras"][i]["text"] += " " + p["paras"].pop(i + 1)["text"]
    whys = {str(x["q"]): x["why"] for x in a["answers"]}
    assert sorted(whys, key=int) == sorted(q["statements"], key=int) == sorted(k["answers"], key=int), tp
    if TYPE == "mi":  # every answer must be one of the passage's paragraph letters
        labels = {x["label"] for x in p["paras"]}
        assert set(k["answers"].values()) <= labels, (n, tp, sorted(labels))
    if TYPE == "me":  # every answer must be one of the endings in the box
        assert set(k["answers"].values()) <= set(q["options"]), (n, tp, sorted(q["options"]))
    sets.append({"n": n, "q": q, "k": k, "p": p, "whys": whys, "test_no": int(q["test"][1]) + OFF, "pno": q["passage"][1],
                 "numbered": not any(x["label"] for x in p["paras"])})


def nice_title(t):
    if not t:
        return "(no title in the book)"  # Cambridge 14 Test 4 Passage 3
    if not t.isupper():
        return t
    small = {"a", "an", "and", "at", "by", "for", "in", "of", "on", "or", "the", "to"}
    words = t.lower().split()  # str.title() would give "Children'S" and "Of"
    return " ".join(w if i and w in small else w[:1].upper() + w[1:] for i, w in enumerate(words))


def book(s, sep="  ·  "):
    """Book prefix, only needed when several books share one PDF."""
    return f'CAMBRIDGE {s["n"]}{sep}' if MULTI else ""


def kind_name(s):
    if s["q"]["kind"] == "MI":
        return "MATCHING INFORMATION"
    if s["q"]["kind"] == "ME":
        return "SENTENCE ENDINGS"
    sep = "/" if MULTI else " / "
    return sep.join(["TRUE", "FALSE", "NOT GIVEN"] if s["q"]["kind"] == "TFNG" else ["YES", "NO", "NOT GIVEN"])


def question_block(s):
    q = s["q"]
    out = [Paragraph(f'Questions {q["first"]}–{q["last"]}', qhead)]
    for line in q["instructions"]:  # the book sets the "write ..." and NB lines in italics
        italic = re.match(r"(Write|In boxes|NB)\b", line)
        out.append(Paragraph(markup(line).replace("NB ", "<b>NB</b>&nbsp;&nbsp;", 1), instr if italic else instr_plain))
    if "defs" not in q:
        out.append(Spacer(1, 6))
    else:
        out += definitions(q)
    rows = [[Paragraph(n, num_cell), Paragraph(markup(t), box_cell)] for n, t in q["statements"].items()]
    st = Table(rows, colWidths=[NUM_W, TEXT_W - NUM_W], hAlign='LEFT')
    st.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('TOPPADDING', (0, 0), (-1, -1), 3),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 5), ('LINEBELOW', (0, 0), (-1, -1), 0.3, LINE)]))
    out.append(st)
    if q.get("options"):
        out += [Spacer(1, 10), options_box(q)]
    return out


def options_box(q):
    """The box of lettered endings, with its title when the book gives one."""
    rows = [[Paragraph(f"<b>{c}</b>", box_cell), Paragraph(markup(t), box_cell)] for c, t in q["options"].items()]
    if q.get("options_title"):
        rows.insert(0, [Paragraph(markup(q["options_title"]), box_title), ""])
    box = Table(rows, colWidths=[1.2 * cm, TEXT_W - 2.2 * cm], hAlign='CENTER')
    style = [('VALIGN', (0, 0), (-1, -1), 'TOP'), ('BOX', (0, 0), (-1, -1), 0.8, GRAY),
             ('BACKGROUND', (0, 0), (-1, -1), SHADE),
             ('TOPPADDING', (0, 0), (-1, -1), 2.5), ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5)]
    if q.get("options_title"):
        style += [('SPAN', (0, 0), (1, 0))]
    box.setStyle(TableStyle(style))
    return box


def definitions(q):
    """The TRUE/FALSE/NOT GIVEN (or YES/NO/NOT GIVEN) box."""
    defs = Table([[Paragraph(f"<b>{d[0]}</b>", def_cell), Paragraph(markup(d[1]), def_cell)] for d in q["defs"]],
                 colWidths=[3.3 * cm, TEXT_W - 4.3 * cm], hAlign='CENTER')
    defs.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('BACKGROUND', (0, 0), (-1, -1), SHADE),
                              ('BOX', (0, 0), (-1, -1), 0.6, LINE),
                              ('TOPPADDING', (0, 0), (-1, -1), 2), ('BOTTOMPADDING', (0, 0), (-1, -1), 3)]))
    return [Spacer(1, 2), defs, Spacer(1, 8)]


def passage_block(s, i):
    p = s["p"]
    where = f'PASSAGE {s["pno"]}' if MULTI else f'READING PASSAGE {s["pno"]}'  # keeps the merged band on one line
    band = Table([[Paragraph(f'{book(s)}TEST {s["test_no"]}  ·  {where}  ·  {kind_name(s)}', band_style)]],
                 colWidths=[TEXT_W])
    band.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), BAND), ('LINEBEFORE', (0, 0), (0, -1), 3, ACCENT),
                              ('TOPPADDING', (0, 0), (-1, -1), 5), ('BOTTOMPADDING', (0, 0), (-1, -1), 5)]))
    label = f'{"C" + str(s["n"]) + " " if MULTI else ""}Test {s["test_no"]} P{s["pno"]}: {nice_title(p["title"])}'
    head = [Mark(f"p{i}", label), band, Paragraph(markup(p["title"]), title_style) if p["title"] else Spacer(1, 10)]
    if p["subtitle"]:
        head.append(Paragraph(markup(p["subtitle"]), standfirst))
    paras = []
    for j, q in enumerate(p["paras"], 1):
        if q["label"]:
            lab = f'<font name="Helvetica-Bold" color="#1A3A5C">{q["label"]}</font>&nbsp;&nbsp;'
        elif s["numbered"]:
            lab = f'<font name="Helvetica" size="11" color="#9A9A9A">¶{j}</font>&nbsp;&nbsp;'
        else:
            lab = ""
        paras.append(Paragraph(lab + markup(q["text"]), body))
    out = [PageBreak(), KeepTogether(head + paras[:1])] + paras[1:]
    out += [Paragraph(markup(n), note_style) for n in p["notes"]]
    out += [Spacer(1, 10), KeepTogether(question_block(s))]
    return out


def answer_sheet():
    out = [PageBreak(), Mark("answers", "Answer Sheet"), Paragraph("Answer Sheet", sheet_title)]
    for s in sets:
        q = s["q"]
        title = f'{"Cambridge " + str(s["n"]) + ", " if MULTI else ""}Test {s["test_no"]}, Passage {s["pno"]}: {nice_title(s["p"]["title"])} (Q{q["first"]}–{q["last"]})'
        band = Table([[Paragraph(markup(title), ans_band)]], colWidths=[TEXT_W])
        band.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), BAND), ('LINEBEFORE', (0, 0), (0, -1), 3, ACCENT),
                                  ('TOPPADDING', (0, 0), (-1, -1), 4), ('BOTTOMPADDING', (0, 0), (-1, -1), 5)]))
        rows = []
        for n, stm in q["statements"].items():
            why = s["whys"][n]
            w = stringWidth(curly(why).replace("CO₂", "CO2"), why_style.fontName, why_style.fontSize)
            if w > WHY_W - 2:
                print(f'  too long for one line ({w:.0f} > {WHY_W:.0f}): C{s["n"]} T{s["test_no"]} Q{n}: {why}')
            ans = s["k"]["answers"][n]
            if q.get("options"):  # sentence endings: show the completed sentence
                stm = f'{stm} {q["options"][ans]}'
            head = Paragraph(f'<b>{ans}</b>&nbsp;&nbsp;<font color="#666666"><i>{markup(stm)}</i></font>', box_cell)
            rows.append([Paragraph(n, num_cell), [head, Paragraph(markup(why), why_style)]])
        style = TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (1, 0), (1, -1), 0),
                            ('RIGHTPADDING', (1, 0), (1, -1), 0), ('TOPPADDING', (0, 0), (-1, -1), 3),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 5), ('LINEBELOW', (0, 0), (-1, -1), 0.3, LINE)])
        # band stays with the first answer; the rest of the set may run on to the next page
        out += [Spacer(1, 8), KeepTogether([band, Spacer(1, 2), Table(rows[:1], colWidths=[NUM_W, WHY_W], style=style)])]
        if rows[1:]:
            out.append(Table(rows[1:], colWidths=[NUM_W, WHY_W], style=style))
    return out


SHORT = {"TFNG": "T/F/NG ", "YNNG": "Y/N/NG ", "MI": "", "ME": ""}


def build(pages):
    total = sum(len(s["q"]["statements"]) for s in sets)
    story = [Paragraph(f"Cambridge IELTS {N}", doc_title),
             Paragraph(f"Academic Reading: {SUBTITLE} ({len(sets)} passages, {total} questions)", doc_sub)]
    rows = [[Paragraph(f'<b>{"C" + str(s["n"]) + " · " if MULTI else ""}Test {s["test_no"]} · P{s["pno"]}</b>', toc_style),
             Paragraph(markup(nice_title(s["p"]["title"])), toc_style),
             Paragraph(f'{SHORT[s["q"]["kind"]]}Q{s["q"]["first"]}–{s["q"]["last"]}', toc_style),
             Paragraph(str(pages.get(f"p{i}", "")), toc_style)] for i, s in enumerate(sets)]
    rows.append([Paragraph('<b>Answer Sheet</b>', toc_style), Paragraph("Official answers, with a one-line reason for each", toc_style),
                 "", Paragraph(str(pages.get("answers", "")), toc_style)])
    c0 = 5.0 * cm if MULTI else 3.6 * cm
    toc = Table(rows, colWidths=[c0, TEXT_W - c0 - 5.6 * cm, 4.2 * cm, 1.4 * cm], repeatRows=0)
    toc.setStyle(TableStyle([('LINEBELOW', (0, 0), (-1, -2), 0.4, LINE), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                             ('TOPPADDING', (0, 0), (-1, -1), 3), ('BOTTOMPADDING', (0, 0), (-1, -1), 3)]))
    story += [toc]
    if any(s["numbered"] for s in sets):
        story.append(Paragraph("Small gray ¶ numbers mark paragraphs in passages that have no paragraph letters. "
                               "They are not in the book; the answer reasons use them (“Para 3”).", doc_note))
    for i, s in enumerate(sets):
        story += passage_block(s, i)
    story += answer_sheet()
    doc = BaseDocTemplate(str(OUT), pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN,
                          topMargin=MARGIN, bottomMargin=MARGIN,
                          title=f"Cambridge IELTS {N} - {PDF_TITLE}", author="Cambridge IELTS (study copy)")
    doc.addPageTemplates([PageTemplate('p', [Frame(MARGIN, MARGIN, TEXT_W, PAGE_H - 2 * MARGIN, id='f')], onPage=on_page)])
    doc.build(story)
    return doc.page


# two passes: the first finds the page numbers the contents table shows
PAGES = {}
build({})
first = dict(PAGES)
pages = build(first)
assert first == PAGES, "contents page numbers moved between passes"
print(OUT, pages, "pages,", len(sets), "passages,", sum(len(s["q"]["statements"]) for s in sets), "questions")
