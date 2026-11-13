"""
Shared ReportLab builder for the "Cambridge IELTS Reading — By Category" PDFs.

Each book (C10-C14) gets ONE PDF containing only its Academic Reading
passages + their original questions (Writing/Listening/Speaking omitted),
reordered so passages of the same study category sit together, in the
canonical category order defined in CANON_ORDER below.

Input: a JSON file shaped like:
{
  "book_number": 10,
  "passages": [
    {
      "order": 1,
      "category": "Environment & Nature",
      "title": "The Megafires of California",
      "test": "T4",
      "passage": "P1",
      "paragraphs": ["A  Text of paragraph A...", "B  Text of paragraph B...", ...],
      "images": [{"path": "abs/or/rel/path.png", "caption": "Optional caption"}],
      "question_groups": [
        {
          "range_label": "Questions 27-32",
          "instruction": "Choose the correct heading ...",
          "type": "Matching",
          "options_box": ["i  Heading one", "ii  Heading two", ...],   // optional, for list-of-headings/options boxes
          "items": [
            {"qnum": "27", "prompt": "Paragraph A", "options": null, "answer": "iii"},
            {"qnum": "28", "prompt": "Which of the following ...", "options": ["A fish", "B bird"], "answer": "B"}
          ],
          "image": {"path": "abs/or/rel/path.png", "caption": "Diagram to label"}   // optional
        }
      ]
    },
    ...
  ]
}

Usage:
    python build_book_pdf.py plan_data_C10.json "../Output/Cambridge_10_Reading_By_Category.pdf"
"""
import json
import os
import sys
from xml.sax.saxutils import escape

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
                                 Table, TableStyle, PageBreak, KeepTogether, Image)
from reportlab.platypus.flowables import HRFlowable

MARGIN = 1.8 * cm
PAGE_W, PAGE_H = A4

DARK = colors.HexColor('#0C0C0C')
GRAY = colors.HexColor('#8A8A8A')
LIGHT_GRAY = colors.HexColor('#D6D6D6')
BORDER_GRAY = colors.HexColor('#AAAAAA')
CAT_BG = colors.HexColor('#EDF2F7')
CAT_TEXT = colors.HexColor('#1A3A5C')

# Canonical category order used for every book — the "Main Category Summary"
# order from Cambridge_IELTS_4-21_216_Gross_Main_Categories.pdf (most to
# fewest passages across the whole 4-21 index). Keeping this fixed means a
# reader who studies several books gets a consistent category sequence.
CANON_ORDER = [
    "Environment & Nature",
    "Psychology, Health & Human Behaviour",
    "Technology, Transport & Engineering",
    "Animals & Biology",
    "Arts, Culture & Media",
    "History & Archaeology",
    "Education & Language",
    "Business, Economics & Work",
    "Science & Discovery",
]

title_style = ParagraphStyle('SheetTitle', fontName='Helvetica-Bold', fontSize=22,
                              leading=26, textColor=DARK, spaceAfter=6, alignment=TA_CENTER)
subtitle_style = ParagraphStyle('SheetSubtitle', fontName='Helvetica', fontSize=12,
                                 leading=15.5, textColor=GRAY, spaceAfter=4, alignment=TA_CENTER)
toc_heading_style = ParagraphStyle('TocHeading', fontName='Helvetica-Bold', fontSize=14,
                                    leading=18, textColor=DARK, spaceBefore=10, spaceAfter=4)
toc_item_style = ParagraphStyle('TocItem', fontName='Helvetica', fontSize=11,
                                 leading=15, textColor=colors.black, leftIndent=12, spaceAfter=2)

cat_divider_style = ParagraphStyle('CatDivider', fontName='Helvetica-Bold', fontSize=17,
                                    leading=21, textColor=CAT_TEXT, spaceAfter=4,
                                    alignment=TA_CENTER)
cat_divider_sub_style = ParagraphStyle('CatDividerSub', fontName='Helvetica', fontSize=10.5,
                                        leading=13, textColor=GRAY, spaceAfter=0,
                                        alignment=TA_CENTER)

passage_title_style = ParagraphStyle('PassageTitle', fontName='Helvetica-Bold', fontSize=19,
                                      leading=23, textColor=DARK, spaceAfter=3,
                                      alignment=TA_CENTER)
passage_label_style = ParagraphStyle('PassageLabel', fontName='Helvetica-Bold', fontSize=10,
                                      leading=12, textColor=GRAY, spaceAfter=2,
                                      alignment=TA_CENTER)
passage_origin_style = ParagraphStyle('PassageOrigin', fontName='Helvetica-Oblique', fontSize=9.5,
                                       leading=12, textColor=GRAY, spaceAfter=10,
                                       alignment=TA_CENTER)

# Passage body — the user explicitly asked for 16-17pt for easy reading.
body_style = ParagraphStyle('Body', fontName='Times-Roman', fontSize=16.5, leading=23,
                             textColor=colors.black, alignment=TA_JUSTIFY, spaceAfter=11)

q_heading_style = ParagraphStyle('QHeading', fontName='Helvetica-Bold', fontSize=13.5,
                                  leading=17, textColor=DARK, spaceAfter=3, spaceBefore=8)
q_section_label_style = ParagraphStyle('QSectionLabel', fontName='Helvetica-Bold', fontSize=10,
                                        leading=12, textColor=GRAY, spaceAfter=4, spaceBefore=14)
instr_style = ParagraphStyle('Instr', fontName='Helvetica-Oblique', fontSize=12.5,
                              leading=16.5, textColor=colors.black, spaceAfter=9)
range_style = ParagraphStyle('Range', fontName='Helvetica-Bold', fontSize=13,
                              leading=16, textColor=DARK, spaceBefore=12, spaceAfter=4)
question_style = ParagraphStyle('Question', fontName='Times-Roman', fontSize=12.5,
                                 leading=17, textColor=colors.black, spaceAfter=9)
option_style = ParagraphStyle('Option', fontName='Times-Roman', fontSize=12.5,
                               leading=16.5, textColor=colors.black, leftIndent=16, spaceAfter=3)
box_style = ParagraphStyle('Box', fontName='Times-Roman', fontSize=12, leading=16,
                            textColor=colors.black, spaceAfter=2)
caption_style = ParagraphStyle('Caption', fontName='Helvetica-Oblique', fontSize=10,
                                leading=13, textColor=GRAY, spaceAfter=8, alignment=TA_CENTER)

ans_section_header_style = ParagraphStyle('AnsSectionHeader', fontName='Helvetica-Bold', fontSize=20,
                                           leading=24, textColor=DARK, spaceAfter=4, alignment=TA_CENTER)
ans_note_style = ParagraphStyle('AnsNote', fontName='Helvetica-Oblique', fontSize=10,
                                 leading=13, textColor=GRAY, spaceAfter=14, alignment=TA_CENTER)
ans_cat_style = ParagraphStyle('AnsCat', fontName='Helvetica-Bold', fontSize=13,
                                leading=16, textColor=CAT_TEXT, spaceBefore=12, spaceAfter=4)
ans_passage_style = ParagraphStyle('AnsPassage', fontName='Helvetica-Bold', fontSize=11,
                                    leading=14, textColor=DARK, spaceBefore=6, spaceAfter=2)
ans_cell_style = ParagraphStyle('AnsCell', fontName='Helvetica', fontSize=10,
                                 leading=12.5, textColor=colors.black)
ans_cell_bold_style = ParagraphStyle('AnsCellBold', fontName='Helvetica-Bold', fontSize=10.5,
                                      leading=12.5, textColor=colors.black)
ans_header_cell_style = ParagraphStyle('AnsHeaderCell', fontName='Helvetica-Bold', fontSize=10,
                                        leading=12.5, textColor=colors.white)


def esc(t):
    if t is None:
        return ''
    return escape(str(t))


def make_header_footer(sheet_name):
    def _draw(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica-Bold', 9)
        canvas.setFillColor(GRAY)
        canvas.drawString(MARGIN, PAGE_H - MARGIN + 14, sheet_name)
        canvas.setStrokeColor(LIGHT_GRAY)
        canvas.setLineWidth(0.6)
        canvas.line(MARGIN, PAGE_H - MARGIN + 6, PAGE_W - MARGIN, PAGE_H - MARGIN + 6)
        canvas.setFont('Helvetica', 9)
        canvas.drawRightString(PAGE_W - MARGIN, MARGIN - 20, f"Page {doc.page}")
        canvas.line(MARGIN, MARGIN - 10, PAGE_W - MARGIN, MARGIN - 10)
        canvas.restoreState()
    return _draw


def category_divider_flow(category, passages_in_cat):
    flow = [Spacer(1, 6),
            Paragraph(esc(category), cat_divider_style),
            Paragraph(f"{len(passages_in_cat)} passage(s) in this book",
                      cat_divider_sub_style),
            HRFlowable(width='60%', color=LIGHT_GRAY, thickness=1, spaceBefore=6, spaceAfter=4,
                       hAlign='CENTER')]
    return flow


def build_passage_flow(passage):
    flow = []
    flow.append(Paragraph(esc(passage['category']), passage_label_style))
    flow.append(Paragraph(esc(passage['title']), passage_title_style))
    flow.append(Paragraph(
        f"Originally Cambridge Book — {passage['test']}, {passage['passage']}",
        passage_origin_style))
    para_letter_re = __import__('re').compile(r'^([A-Z])(\s{2,})(.*)$', __import__('re').S)
    for para in passage['paragraphs']:
        m = para_letter_re.match(para)
        if m:
            text = f"<b>{esc(m.group(1))}</b>&nbsp;&nbsp;{esc(m.group(3))}"
        else:
            text = esc(para)
        flow.append(Paragraph(text, body_style))
    for img in passage.get('images') or []:
        if os.path.exists(img['path']):
            flow.append(Spacer(1, 6))
            flow.append(Image(img['path'], width=(PAGE_W - 2 * MARGIN) * 0.85,
                               height=None, kind='proportional'))
            if img.get('caption'):
                flow.append(Paragraph(esc(img['caption']), caption_style))
    return flow


def build_questions_flow(passage):
    flow = []
    flow.append(Paragraph("QUESTIONS FOR THIS PASSAGE", q_section_label_style))
    for g in passage['question_groups']:
        flow.append(Paragraph(esc(g['range_label']), range_style))
        if g.get('instruction'):
            flow.append(Paragraph(esc(g['instruction']), instr_style))
        if g.get('options_box'):
            rows = [[Paragraph(esc(o), box_style)] for o in g['options_box']]
            t = Table(rows, colWidths=[(PAGE_W - 2 * MARGIN) * 0.9])
            t.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 0.6, BORDER_GRAY),
                ('INNERGRID', (0, 0), (-1, -1), 0.3, LIGHT_GRAY),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ]))
            flow.append(t)
            flow.append(Spacer(1, 8))
        img = g.get('image')
        if img and os.path.exists(img['path']):
            flow.append(Image(img['path'], width=(PAGE_W - 2 * MARGIN) * 0.8,
                               height=None, kind='proportional'))
            if img.get('caption'):
                flow.append(Paragraph(esc(img['caption']), caption_style))
            flow.append(Spacer(1, 6))
        for it in g['items']:
            block = [Paragraph(f"<b>{esc(it['qnum'])}.</b> {esc(it['prompt'])}", question_style)]
            if it.get('options'):
                for opt in it['options']:
                    block.append(Paragraph(esc(opt), option_style))
            flow.append(KeepTogether(block))
    return flow


def build_answer_key_flow(book_passages):
    flow = [PageBreak(),
            Paragraph("ANSWER KEY — READING", ans_section_header_style),
            Paragraph("Numbers below are each passage's ORIGINAL question numbers as printed "
                      "in the source book (not renumbered).", ans_note_style)]
    last_cat = None
    for p in book_passages:
        if p['category'] != last_cat:
            flow.append(Paragraph(esc(p['category']), ans_cat_style))
            last_cat = p['category']
        flow.append(Paragraph(
            f"{esc(p['title'])} &nbsp;&mdash;&nbsp; {esc(p['test'])}, {esc(p['passage'])}",
            ans_passage_style))
        rows = [[Paragraph(h, ans_header_cell_style) for h in ["Q#", "Answer"]]]
        for g in p['question_groups']:
            for it in g['items']:
                ans = it.get('answer')
                ans_text = ans if ans else 'Answer not in source'
                rows.append([Paragraph(esc(it['qnum']), ans_cell_bold_style),
                             Paragraph(esc(ans_text), ans_cell_style)])
        avail_w = PAGE_W - 2 * MARGIN
        t = Table(rows, colWidths=[0.15 * avail_w, 0.35 * avail_w], hAlign='LEFT')
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), GRAY),
            ('GRID', (0, 0), (-1, -1), 0.5, LIGHT_GRAY),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ]))
        flow.append(t)
        flow.append(Spacer(1, 6))
    return flow


def build_toc_flow(book_number, book_passages):
    flow = []
    by_cat = {}
    for p in book_passages:
        by_cat.setdefault(p['category'], []).append(p)
    for cat in CANON_ORDER:
        if cat not in by_cat:
            continue
        flow.append(Paragraph(esc(cat), toc_heading_style))
        for p in by_cat[cat]:
            flow.append(Paragraph(
                f"&bull; {esc(p['title'])} <font color='#8A8A8A'>({esc(p['test'])}, {esc(p['passage'])})</font>",
                toc_item_style))
    return flow


def build_book_pdf(data, output_path):
    book_number = data['book_number']
    book_passages = data['passages']
    sheet_name = f"Cambridge IELTS {book_number} — Reading by Category"

    doc = BaseDocTemplate(output_path, pagesize=A4,
                           leftMargin=MARGIN, rightMargin=MARGIN,
                           topMargin=MARGIN, bottomMargin=MARGIN,
                           title=sheet_name)
    frame = Frame(MARGIN, MARGIN, PAGE_W - 2 * MARGIN, PAGE_H - 2 * MARGIN, id='normal')
    doc.addPageTemplates([PageTemplate(id='main', frames=[frame],
                                        onPage=make_header_footer(sheet_name))])

    total_q = sum(len(g['items']) for p in book_passages for g in p['question_groups'])
    story = [Paragraph(sheet_name, title_style),
             Paragraph(f"Academic Reading only — {len(book_passages)} passages, {total_q} questions. "
                       "Writing, Listening and Speaking sections omitted. Passages are grouped by "
                       "study category, not by their original test.", subtitle_style),
             HRFlowable(width='100%', color=LIGHT_GRAY, thickness=0.8, spaceAfter=10)]

    story.extend(build_toc_flow(book_number, book_passages))

    last_cat = None
    by_cat_count = {}
    for p in book_passages:
        by_cat_count.setdefault(p['category'], 0)
        by_cat_count[p['category']] += 1
    for p in book_passages:
        if p['category'] != last_cat:
            story.append(PageBreak())
            story.extend(category_divider_flow(p['category'], range(by_cat_count[p['category']])))
            last_cat = p['category']
        else:
            story.append(PageBreak())
        story.extend(build_passage_flow(p))
        story.extend(build_questions_flow(p))

    story.extend(build_answer_key_flow(book_passages))

    doc.build(story)
    return total_q


def main():
    if len(sys.argv) != 3:
        sys.exit("Usage: python build_book_pdf.py <data.json> <output.pdf>")
    data_path, out_path = sys.argv[1], sys.argv[2]
    data = json.load(open(data_path, encoding='utf-8'))
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    total_q = build_book_pdf(data, out_path)
    print(f"Built {out_path}: {len(data['passages'])} passages, {total_q} questions")


if __name__ == '__main__':
    main()
