import json, os, re, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
                                 Table, TableStyle, PageBreak, KeepTogether)
from reportlab.platypus.flowables import HRFlowable

from build_pdf import (
    MARGIN, PAGE_W, PAGE_H, DARK, GRAY, LIGHT_GRAY, BORDER_GRAY,
    title_style, subtitle_style, q_section_label_style, range_style, instr_style,
    ans_header_style, ans_note_style, ans_cell_style, ans_cell_bold_style,
    ans_header_cell_style, esc, make_header_footer, build_passage_flow,
)
from build_completion_pdf import render_blocks, substitute_blanks

FAMILY_LABEL = ("Matching (Matching Headings • Matching Information • "
                "Matching Features • Matching Sentence Endings • Summary Completion with options)")

item_style = ParagraphStyle('MatchItem', fontName='Times-Roman', fontSize=12.5,
                             leading=18, textColor=colors.black, spaceAfter=9)
bank_title_style = ParagraphStyle('BankTitle', fontName='Helvetica-Bold', fontSize=11.5,
                                   leading=14, textColor=DARK, spaceAfter=4, spaceBefore=2,
                                   alignment=TA_CENTER)
bank_cell_code_style = ParagraphStyle('BankCode', fontName='Helvetica-Bold', fontSize=11,
                                       leading=14, textColor=DARK, alignment=TA_CENTER)
bank_cell_text_style = ParagraphStyle('BankText', fontName='Times-Roman', fontSize=11,
                                       leading=14.5, textColor=colors.black)
nb_note_style = ParagraphStyle('NBNote', fontName='Helvetica-Oblique', fontSize=10.5,
                                leading=13.5, textColor=GRAY, spaceAfter=8)

DEFAULT_BANK_TITLE = {
    'Matching Headings': 'List of Headings',
    'Matching Features': 'Options',
    'Matching Sentence Endings': 'List of Sentence Endings',
    'Summary Completion (options)': 'Word Bank',
}


def build_bank_flow(subtype, bank_title, bank):
    if not bank:
        return []
    flow = [Paragraph(esc(bank_title or DEFAULT_BANK_TITLE.get(subtype, 'Options')), bank_title_style)]
    rows = [[Paragraph(esc(code), bank_cell_code_style), Paragraph(esc(text), bank_cell_text_style)]
            for code, text in bank]
    avail_w = PAGE_W - 2 * MARGIN
    t = Table(rows, colWidths=[0.07 * avail_w, 0.93 * avail_w], hAlign='LEFT')
    t.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.6, BORDER_GRAY),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, LIGHT_GRAY),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F7F7F7')),
    ]))
    flow.append(t)
    flow.append(Spacer(1, 8))
    return flow


QRANGE_LEAD_RE = re.compile(r'^\s*Questions?\s*\d+\s*[–\-]\s*\d+\s*', re.I)


def build_questions_flow(passage, qnum_start):
    flow = []
    flow.append(Paragraph("QUESTIONS", q_section_label_style))
    qnum = qnum_start
    mapping_rows = []
    for g in passage['groups']:
        qnums_sorted = sorted(g['qnums'])
        renumber_map = {}
        for orig in qnums_sorted:
            renumber_map[orig] = qnum
            qnum += 1
        new_min, new_max = renumber_map[qnums_sorted[0]], renumber_map[qnums_sorted[-1]]
        range_label = f"Questions {new_min}" if new_min == new_max else f"Questions {new_min}–{new_max}"
        flow.append(Paragraph(range_label, range_style))
        instr_text = QRANGE_LEAD_RE.sub('', g['instruction'] or '').strip()
        if instr_text:
            flow.append(Paragraph(esc(instr_text), instr_style))
        flow.extend(build_bank_flow(g['subtype'], g.get('bank_title'), g.get('bank')))

        if g.get('blocks'):
            flow.extend(render_blocks(g['blocks'], renumber_map))
        else:
            for it in g['items']:
                orig = it['qnum']
                new_n = renumber_map[orig]
                txt = f"<b>({new_n})</b> {esc(it['statement'])} &nbsp;&nbsp;<b>[ ……… ]</b>"
                flow.append(KeepTogether([Paragraph(txt, item_style)]))

        for orig in qnums_sorted:
            # find this orig's answer - items carry it directly for item-based
            # groups; blocks-based groups (word-bank summary) carry it the
            # same way via the group's 'items' list regardless
            ans = None
            for it in g['items']:
                if it['qnum'] == orig:
                    ans = it.get('answer')
                    break
            mapping_rows.append({
                'new_qnum': renumber_map[orig],
                'orig_qnum': orig,
                'answer': ans,
                'passage_title': passage['title'],
            })
    return flow, qnum, mapping_rows


def build_answer_sheet_flow(all_mapping, sources_by_passage, passage_local_by_title):
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
        local_num = passage_local_by_title.get(row['passage_title'], '?')
        data.append([
            Paragraph(str(row['new_qnum']), ans_cell_bold_style),
            Paragraph(esc(str(ans)), ans_cell_style),
            Paragraph(esc(f"P{local_num}: {row['passage_title']}"), ans_cell_style),
            Paragraph(esc(f"{src} — Q{row['orig_qnum']}"), ans_cell_style),
        ])
    avail_w = PAGE_W - 2 * MARGIN
    col_widths = [0.09 * avail_w, 0.16 * avail_w, 0.33 * avail_w, 0.42 * avail_w]
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
    frame = Frame(MARGIN, MARGIN, PAGE_W - 2 * MARGIN, PAGE_H - 2 * MARGIN, id='normal')
    doc.addPageTemplates([PageTemplate(id='main', frames=[frame],
                                        onPage=make_header_footer(sheet_name))])

    total_q = sum(len(g['qnums']) for p in set_passages for g in p['groups'])
    story = []
    story.append(Paragraph("IELTS Reading Practice", title_style))
    story.append(Paragraph(
        f"{FAMILY_LABEL} &mdash; Passage Level: All &mdash; {set_label} "
        f"({set_index} of {total_sets}) &mdash; {len(set_passages)} passages, {total_q} questions",
        subtitle_style))
    story.append(HRFlowable(width='100%', color=LIGHT_GRAY, thickness=0.8, spaceAfter=10))

    qnum = 1
    all_mapping = []
    sources_by_passage = {}
    passage_local_by_title = {}
    for i, p in enumerate(set_passages, start=1):
        story.append(PageBreak())
        story.extend(build_passage_flow(i, p))
        qflow, qnum, mapping_rows = build_questions_flow(p, qnum)
        story.extend(qflow)
        all_mapping.extend(mapping_rows)
        src_files = sorted(set(os.path.basename(s['file']) for s in p['sources']))
        sources_by_passage[p['title']] = '; '.join(src_files)
        passage_local_by_title[p['title']] = i

    story.append(PageBreak())
    story.extend(build_answer_sheet_flow(all_mapping, sources_by_passage, passage_local_by_title))

    doc.build(story)
    return total_q, all_mapping


def main():
    agg_path, out_dir, set_size = sys.argv[1], sys.argv[2], int(sys.argv[3])
    passages = json.load(open(agg_path, encoding='utf-8'))
    passages_sorted = sorted(passages, key=lambda p: (p['level'], passages.index(p)))
    n_sets = math.ceil(len(passages_sorted) / set_size)
    os.makedirs(out_dir, exist_ok=True)
    results = []
    for s in range(n_sets):
        chunk = passages_sorted[s * set_size:(s + 1) * set_size]
        set_num = s + 1
        fname = f"All_Matching_Set{set_num:02d}.pdf"
        out_path = os.path.join(out_dir, fname)
        sheet_name = f"IELTS Reading — Matching — All — Set {set_num:02d}"
        set_label = f"Set {set_num:02d}"
        total_q, mapping = build_pdf(out_path, sheet_name, set_label, chunk, set_num, n_sets)
        results.append({'file': fname, 'passages': len(chunk), 'questions': total_q})
        print(f"Built {fname}: {len(chunk)} passages, {total_q} questions")
    json.dump(results, open(os.path.join(out_dir, '_build_manifest_matching.json'), 'w', encoding='utf-8'), indent=2)


if __name__ == '__main__':
    main()
