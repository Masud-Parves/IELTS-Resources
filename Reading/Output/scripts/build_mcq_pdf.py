import json, os, re, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
                                 Table, TableStyle, PageBreak, KeepTogether)
from reportlab.platypus.flowables import HRFlowable

from build_pdf import (
    MARGIN, PAGE_W, PAGE_H, DARK, GRAY, LIGHT_GRAY, BORDER_GRAY,
    title_style, subtitle_style, q_section_label_style, range_style, instr_style,
    ans_header_style, ans_note_style, ans_cell_style, ans_cell_bold_style,
    ans_header_cell_style, esc, make_header_footer, build_passage_flow,
)

FAMILY_LABEL = "Multiple Choice (single answer • choose TWO/THREE answers)"

prompt_style = ParagraphStyle('McqPrompt', fontName='Times-Roman', fontSize=12.5,
                               leading=17.5, textColor=colors.black, spaceAfter=5,
                               spaceBefore=8)
option_style = ParagraphStyle('McqOption', fontName='Times-Roman', fontSize=12.5,
                               leading=17, textColor=colors.black, spaceAfter=2,
                               leftIndent=16)
required_note_style = ParagraphStyle('ReqNote', fontName='Helvetica-Oblique', fontSize=10.5,
                                      leading=13.5, textColor=GRAY, spaceAfter=4)

QRANGE_LEAD_RE = re.compile(r'^\s*Questions?\s*\d+\s*(?:and|[–\-])\s*\d+\s*', re.I)


def render_item(qlabel, prompt, options, required):
    flow = []
    flow.append(Paragraph(f"<b>{esc(qlabel)}</b>&nbsp;&nbsp;{esc(prompt)}", prompt_style))
    if required and required > 1:
        flow.append(Paragraph(f"(Choose {required} letters.)", required_note_style))
    for o in options:
        flow.append(Paragraph(f"<b>{esc(o['code'])}</b>&nbsp;&nbsp;{esc(o['text'])}", option_style))
    flow.append(Spacer(1, 6))
    return flow


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

        for it in g['items']:
            qn = it['qnum']
            if isinstance(qn, list):
                new_nums = [renumber_map[q] for q in sorted(qn)]
                qlabel = f"({new_nums[0]}–{new_nums[-1]})" if len(new_nums) > 1 else f"({new_nums[0]})"
                item_block = render_item(qlabel, it['prompt'], it['options'], it.get('required'))
                flow.append(KeepTogether(item_block))
                ans = it.get('answer')
                for q in sorted(qn):
                    # JSON round-tripping turns dict keys into strings, so a
                    # per-qnum answer dict must be probed with both forms
                    a = (ans.get(q, ans.get(str(q))) if isinstance(ans, dict) else ans)
                    mapping_rows.append({
                        'new_qnum': renumber_map[q], 'orig_qnum': q,
                        'answer': a, 'passage_title': passage['title'],
                    })
            else:
                new_n = renumber_map[qn]
                item_block = render_item(f"({new_n})", it['prompt'], it['options'], it.get('required'))
                flow.append(KeepTogether(item_block))
                mapping_rows.append({
                    'new_qnum': new_n, 'orig_qnum': qn,
                    'answer': it.get('answer'), 'passage_title': passage['title'],
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
        a = row['answer']
        if a is None:
            ans_text = 'Answer not in source'
        elif isinstance(a, list):
            ans_text = ', '.join(a)
        else:
            ans_text = str(a)
        src = sources_by_passage.get(row['passage_title'], '')
        local_num = passage_local_by_title.get(row['passage_title'], '?')
        data.append([
            Paragraph(str(row['new_qnum']), ans_cell_bold_style),
            Paragraph(esc(ans_text), ans_cell_style),
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
        fname = f"All_MCQ_Set{set_num:02d}.pdf"
        out_path = os.path.join(out_dir, fname)
        sheet_name = f"IELTS Reading — MCQ — All — Set {set_num:02d}"
        set_label = f"Set {set_num:02d}"
        total_q, mapping = build_pdf(out_path, sheet_name, set_label, chunk, set_num, n_sets)
        results.append({'file': fname, 'passages': len(chunk), 'questions': total_q})
        print(f"Built {fname}: {len(chunk)} passages, {total_q} questions")
    json.dump(results, open(os.path.join(out_dir, '_build_manifest_mcq.json'), 'w', encoding='utf-8'), indent=2)


if __name__ == '__main__':
    main()
