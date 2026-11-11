import json, os, re, sys, math
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
                                 Table, TableStyle, PageBreak, KeepTogether, NextPageTemplate)
from reportlab.platypus.flowables import HRFlowable
from xml.sax.saxutils import escape

MARGIN = 1.8 * cm
PAGE_W, PAGE_H = A4

DARK = colors.HexColor('#0C0C0C')
GRAY = colors.HexColor('#8A8A8A')
LIGHT_GRAY = colors.HexColor('#D6D6D6')
MID_GRAY = colors.HexColor('#BDBDBD')
BORDER_GRAY = colors.HexColor('#AAAAAA')

FAMILY_LABEL = "Identifying Information / Views (True/False/Not Given • Yes/No/Not Given)"

styles = getSampleStyleSheet()

title_style = ParagraphStyle('SheetTitle', fontName='Helvetica-Bold', fontSize=20,
                              leading=24, textColor=DARK, spaceAfter=5)
subtitle_style = ParagraphStyle('SheetSubtitle', fontName='Helvetica', fontSize=12,
                                 leading=15.5, textColor=GRAY, spaceAfter=14)
passage_title_style = ParagraphStyle('PassageTitle', fontName='Helvetica-Bold', fontSize=16,
                                      leading=20, textColor=DARK, spaceAfter=11,
                                      alignment=TA_CENTER)
passage_label_style = ParagraphStyle('PassageLabel', fontName='Helvetica-Bold', fontSize=10,
                                      leading=12, textColor=GRAY, spaceAfter=3,
                                      alignment=TA_CENTER)
body_style = ParagraphStyle('Body', fontName='Times-Roman', fontSize=13, leading=18.2,
                             textColor=colors.black, alignment=TA_JUSTIFY, spaceAfter=10)
q_heading_style = ParagraphStyle('QHeading', fontName='Helvetica-Bold', fontSize=14.5,
                                  leading=18, textColor=DARK, spaceAfter=3, spaceBefore=6)
q_section_label_style = ParagraphStyle('QSectionLabel', fontName='Helvetica-Bold', fontSize=10,
                                        leading=12, textColor=GRAY, spaceAfter=4, spaceBefore=12)
instr_style = ParagraphStyle('Instr', fontName='Helvetica-Oblique', fontSize=12.5,
                              leading=16.5, textColor=colors.black, spaceAfter=9)
range_style = ParagraphStyle('Range', fontName='Helvetica-Bold', fontSize=12.5,
                              leading=15, textColor=DARK, spaceBefore=11, spaceAfter=3)
question_style = ParagraphStyle('Question', fontName='Times-Roman', fontSize=12.5,
                                 leading=17, textColor=colors.black, spaceAfter=10)
footer_style = ParagraphStyle('Footer', fontName='Helvetica', fontSize=9, textColor=GRAY)
header_style = ParagraphStyle('Header', fontName='Helvetica-Bold', fontSize=9, textColor=GRAY)
ans_header_style = ParagraphStyle('AnsHeader', fontName='Helvetica-Bold', fontSize=18,
                                   leading=22, textColor=DARK, spaceAfter=5, alignment=TA_CENTER)
ans_note_style = ParagraphStyle('AnsNote', fontName='Helvetica-Oblique', fontSize=10.5,
                                 leading=14, textColor=GRAY, spaceAfter=14, alignment=TA_CENTER)


def esc(t):
    if t is None:
        return ''
    return escape(t)


class NumberedCanvas:
    pass


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


def option_row(labels, selected=None):
    """A row of bordered option boxes, e.g. TRUE / FALSE / NOT GIVEN."""
    cells = [Paragraph(l, ParagraphStyle('opt', fontName='Helvetica', fontSize=11,
                                          textColor=colors.black, alignment=TA_CENTER))
             for l in labels]
    t = Table([cells], colWidths=[None]*len(labels))
    t.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.6, BORDER_GRAY),
        ('INNERGRID', (0, 0), (-1, -1), 0.6, BORDER_GRAY),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    return t


def build_passage_flow(local_num, passage):
    flow = []
    flow.append(Paragraph(f"PASSAGE {local_num}", passage_label_style))
    flow.append(Paragraph(esc(passage['title']), passage_title_style))
    for para in passage['paragraphs']:
        flow.append(Paragraph(esc(para), body_style))
    return flow


def build_questions_flow(local_num, passage, qnum_start):
    flow = []
    flow.append(Paragraph("QUESTIONS", q_section_label_style))
    qnum = qnum_start
    mapping_rows = []
    qrange_lead_re = re.compile(r'^\s*Questions?\s*\d+\s*[–\-]\s*\d+\s*', re.I)
    for g in passage['groups']:
        flow.append(Paragraph(f"Questions {qnum}–{qnum + len(g['items']) - 1}", range_style))
        instr_text = qrange_lead_re.sub('', g['instruction'] or '').strip()
        if instr_text:
            flow.append(Paragraph(esc(instr_text), instr_style))
        opt_labels = ['TRUE', 'FALSE', 'NOT GIVEN'] if g['subtype'] == 'TFNG' else ['YES', 'NO', 'NOT GIVEN']
        for it in g['items']:
            block = [Paragraph(f"<b>{qnum}.</b> {esc(it['prompt'])}", question_style),
                     option_row(opt_labels)]
            flow.append(KeepTogether(block))
            flow.append(Spacer(1, 6))
            mapping_rows.append({
                'new_qnum': qnum,
                'answer': it['answer'],
                'orig_qnum': it['orig_qnum'],
                'passage_local': local_num,
                'passage_title': passage['title'],
            })
            qnum += 1
    return flow, qnum, mapping_rows


ans_cell_style = ParagraphStyle('AnsCell', fontName='Helvetica', fontSize=10,
                                 leading=12.5, textColor=colors.black)
ans_cell_bold_style = ParagraphStyle('AnsCellBold', fontName='Helvetica-Bold', fontSize=10.5,
                                      leading=12.5, textColor=colors.black)
ans_header_cell_style = ParagraphStyle('AnsHeaderCell', fontName='Helvetica-Bold', fontSize=10,
                                        leading=12.5, textColor=colors.white)


def build_answer_sheet_flow(sheet_name, all_mapping, sources_by_passage):
    flow = []
    flow.append(Paragraph("ANSWER SHEET", ans_header_style))
    flow.append(Paragraph("Question numbers below match the renumbered questions in this PDF, "
                           "not the original source numbering.", ans_note_style))
    header = [Paragraph(h, ans_header_cell_style)
              for h in ["No.", "Answer", "Passage", "Source (file — original Q)"]]
    data = [header]
    for row in all_mapping:
        ans = row['answer'] if row['answer'] is not None else 'Answer not in source'
        src = sources_by_passage.get(row['passage_title'], '')
        data.append([
            Paragraph(str(row['new_qnum']), ans_cell_bold_style),
            Paragraph(esc(ans), ans_cell_style),
            Paragraph(esc(f"P{row['passage_local']}: {row['passage_title']}"), ans_cell_style),
            Paragraph(esc(f"{src} — Q{row['orig_qnum']}"), ans_cell_style),
        ])
    avail_w = PAGE_W - 2*MARGIN
    col_widths = [0.09*avail_w, 0.16*avail_w, 0.33*avail_w, 0.42*avail_w]
    t = Table(data, colWidths=col_widths, repeatRows=1, hAlign='LEFT')
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
    return flow


def build_pdf(output_path, sheet_name, set_label, set_passages, set_index, total_sets):
    doc = BaseDocTemplate(output_path, pagesize=A4,
                           leftMargin=MARGIN, rightMargin=MARGIN,
                           topMargin=MARGIN, bottomMargin=MARGIN,
                           title=sheet_name)
    frame = Frame(MARGIN, MARGIN, PAGE_W - 2*MARGIN, PAGE_H - 2*MARGIN, id='normal')
    doc.addPageTemplates([PageTemplate(id='main', frames=[frame],
                                        onPage=make_header_footer(sheet_name))])

    total_q = sum(len(g['items']) for p in set_passages for g in p['groups'])
    story = []
    story.append(Paragraph("IELTS Reading Practice", title_style))
    story.append(Paragraph(
        f"{FAMILY_LABEL} &mdash; Passage Level: All &mdash; {set_label} "
        f"({set_index} of {total_sets}) &mdash; {len(set_passages)} passages, {total_q} questions",
        subtitle_style))
    story.append(HRFlowable(width='100%', color=LIGHT_GRAY, thickness=0.8, spaceAfter=10))

    # Each passage is immediately followed by its own questions (not grouped
    # separately) so the sheet can be practiced passage-by-passage.
    qnum = 1
    all_mapping = []
    sources_by_passage = {}
    for i, p in enumerate(set_passages, start=1):
        story.append(PageBreak())
        story.extend(build_passage_flow(i, p))
        qflow, qnum, mapping_rows = build_questions_flow(i, p, qnum)
        story.extend(qflow)
        all_mapping.extend(mapping_rows)
        src_files = sorted(set(os.path.basename(s['file']) for s in p['sources']))
        sources_by_passage[p['title']] = '; '.join(src_files)

    # Answer sheet - always at the very end
    story.append(PageBreak())
    story.extend(build_answer_sheet_flow(sheet_name, all_mapping, sources_by_passage))

    doc.build(story)
    return total_q, all_mapping


def main():
    agg_path, out_dir, set_size = sys.argv[1], sys.argv[2], int(sys.argv[3])
    passages = json.load(open(agg_path, encoding='utf-8'))
    # order: by level 1,2,3, preserving first-seen order within level
    passages_sorted = sorted(passages, key=lambda p: (p['level'], passages.index(p)))
    n_sets = math.ceil(len(passages_sorted) / set_size)
    os.makedirs(out_dir, exist_ok=True)
    results = []
    for s in range(n_sets):
        chunk = passages_sorted[s*set_size:(s+1)*set_size]
        set_num = s + 1
        fname = f"All_TFNG_Set{set_num:02d}.pdf"
        out_path = os.path.join(out_dir, fname)
        sheet_name = f"IELTS Reading — TFNG/YNNG — All — Set {set_num:02d}"
        set_label = f"Set {set_num:02d}"
        total_q, mapping = build_pdf(out_path, sheet_name, set_label, chunk, set_num, n_sets)
        results.append({'file': fname, 'passages': len(chunk), 'questions': total_q})
        print(f"Built {fname}: {len(chunk)} passages, {total_q} questions")
    json.dump(results, open(os.path.join(out_dir, '_build_manifest.json'), 'w', encoding='utf-8'), indent=2)


if __name__ == '__main__':
    main()
