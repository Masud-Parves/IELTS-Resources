import os, re, json, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_tfng import (
    BeautifulSoup, find_answer_maps, extract_passages,
    find_part_number_from_ancestors, find_questions_range_header,
)
from extract_matching import nearest_block_ancestor
from js_obj import find_js_object_assignment

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # the Reading/ folder
FOLDERS = {"Passage 1": "P1", "Passage 2": "P2", "Passage 3": "P3"}

ID_QNUM_RE = re.compile(r'^q?0*(\d{1,3})$', re.I)
RANGE_NAME_RE = re.compile(r'^q0*(\d{1,3})[_\-]0*(\d{1,3})$', re.I)
LETTER_SET = re.compile(r'^[A-H]$')
TFNG_YNNG = frozenset({'TRUE', 'FALSE', 'NOT GIVEN', 'YES', 'NO'})

RUBRIC_MARKER_RE = re.compile(
    r'choose the correct letter|choose\s+(?:the\s+)?(?:two|three)\b|'
    r'choose\s+[A-D](?:\s*,\s*[A-D])*(?:\s*,?\s*or\s*[A-D])?\b', re.I)

OPTION_LABEL_RE = re.compile(r'^\s*([A-H])[\.\)]?\s*[:\-]?\s*(.*)$', re.I | re.DOTALL)
WS_RE = re.compile(r'\s+')


def collapse_ws(s):
    return WS_RE.sub(' ', s).strip() if s else s
LEADING_QNUM_RE = re.compile(
    r'^\s*(?:Questions?\s*)?\d{1,3}(?:\s*(?:[\u2013\-]|and)\s*\d{1,3})?[\.\)]?\s*', re.I)
QRANGE_RE = re.compile(r'Questions?\s*(\d+)\s*[\u2013\-]\s*(\d+)', re.I)


def find_option_row(input_tag):
    node = input_tag
    for _ in range(5):
        node = node.parent
        if node is None:
            break
        if node.name == 'label':
            return node
        cls = ' '.join(node.get('class', [])) if node.has_attr('class') else ''
        if re.search(r'\boption\b|choice-item|multi-choice-option|checkbox-option|tf-option', cls, re.I):
            return node
    return input_tag.parent


def text_excluding_nodes(container, exclude_nodes):
    parts = []
    exclude_set = set(id(n) for n in exclude_nodes)
    for desc in container.descendants:
        if not isinstance(desc, str):
            continue
        skip = False
        anc = desc.parent
        while anc is not None:
            if id(anc) in exclude_set:
                skip = True
                break
            if anc.has_attr('class') and re.search(
                    r'analysis|explain|answer-?key|review-flag|ca-display|correct-answer-display|after-check',
                    ' '.join(anc['class']), re.I):
                skip = True
                break
            if anc is container:
                break
            anc = anc.parent
        if not skip:
            t = desc.strip()
            if t:
                parts.append(t)
    return collapse_ws(' '.join(parts))


def find_rubric_block(tag):
    """Walk backward through preceding text, and for each fragment check its
    own small text first, climbing at most a couple of levels (not all the
    way to a possibly page-spanning block ancestor) - this is needed because
    inline formatting tags (e.g. "Choose <b>TWO</b> letters...") routinely
    split the rubric sentence across several separate text nodes, but must
    stay bounded or a flatly-nested template (instruction+stem+options as
    plain sibling children, no wrapping <p>) matches against a block that
    actually spans the whole question card, or further."""
    count = 0
    seen = set()
    for prev in tag.find_all_previous(string=True):
        count += 1
        if count > 6000:
            break
        node = prev.parent
        for hop in range(3):
            if node is None or id(node) in seen:
                break
            seen.add(id(node))
            txt = collapse_ws(node.get_text(' ', strip=True))
            if len(txt) < 300 and RUBRIC_MARKER_RE.search(txt):
                return node
            if len(txt) >= 15:
                break
            node = node.parent
    return None


def find_instruction_text(tag):
    block = find_rubric_block(tag)
    if block is None:
        return None
    txt = collapse_ws(block.get_text(' ', strip=True))
    if len(txt) < 15 and block.parent is not None:
        ptxt = collapse_ws(block.parent.get_text(' ', strip=True))
        if len(ptxt) < 500:
            txt = ptxt
    return txt or None


RANGED_KEY_RE = re.compile(r'''['"](\d{1,3})\s*-\s*(\d{1,3})['"]\s*:\s*(\[[^\]]*\])''')
QUOTED_STR_RE = re.compile(r''''((?:[^'\\]|\\.)*)'|"((?:[^"\\]|\\.)*)"''')


def find_ranged_answer_entries(html):
    """Some files key a choose-TWO/THREE answer by its whole question range,
    e.g. correctAnswers = {'1-3': ['A','D','F'], ...} - the shared
    parse_object_entries() parser (built for single-qnum keys) drops these
    silently, so recover them here with a dedicated regex and fan the same
    array out to every question number in the range."""
    out = {}
    for m in RANGED_KEY_RE.finditer(html):
        lo, hi, arr_text = int(m.group(1)), int(m.group(2)), m.group(3)
        vals = [a or b for a, b in QUOTED_STR_RE.findall(arr_text)]
        if not vals:
            continue
        for q in range(lo, hi + 1):
            out[q] = vals
    return out


def pick_best_mcq_answer_map(maps, needed):
    """MCQ-aware alternative to the shared pick_best_answer_map(): scores a
    candidate object using normalize_mcq_answer() (so an "A/D"-style combined
    string counts as a hit), since the generic scorer checks for a value that
    is literally equal to one option code and otherwise rejects it."""
    best = None
    best_score = -1
    for varname, entries in maps:
        score = 0
        for q, valid in needed.items():
            v = entries.get(q)
            if v is None:
                v = entries.get(str(q))
            if normalize_mcq_answer(v, valid) is not None:
                score += 1
        if score > best_score:
            best_score = score
            best = (varname, entries)
    return best if best_score > 0 else None


def normalize_mcq_answer(v, valid_codes):
    """Accepts a list (['A','D']), a single letter ('A'), or a slash/comma
    joined multi-letter string ('A/D', 'A, D') and returns a sorted list of
    letters if every one of them is a valid option code for this question,
    else None."""
    if v is None:
        return None
    if isinstance(v, list):
        parts = [str(x) for x in v]
    else:
        parts = re.split(r'[\/,]', str(v))
    letters = [p.strip().upper() for p in parts if p.strip()]
    if letters and all(l in valid_codes for l in letters):
        return sorted(set(letters))
    return None


def extract_passage_number_from_instruction(instr_text):
    if not instr_text:
        return None
    m = re.search(r'Reading Passage\s*(\d+)', instr_text, re.I)
    return int(m.group(1)) if m else None


def strip_leading_qnum_repeated(text):
    # a q-badge/section-head span showing the question number(s) is often
    # duplicated right before the stem text itself (e.g. a "Questions 20-21"
    # header *and* a "20-21" badge inline before the stem) - strip every such
    # leading repeat, not just the first
    prev = None
    while prev != text:
        prev = text
        text = LEADING_QNUM_RE.sub('', text, count=1).strip()
    return text


MAX_PROMPT_LEN = 400


def strip_instruction_overlap(prompt, instr):
    """Some templates bundle the rubric and the actual stem question into one
    shared text block with no element boundary between them (so neither the
    node-exclusion in find_item_prompt() nor the rubric-block lookup can
    separate them structurally) - fall back to a plain text-prefix strip
    once both pieces are already known."""
    if not instr or not prompt:
        return prompt
    if prompt == instr:
        return prompt
    if prompt.startswith(instr):
        rest = prompt[len(instr):].strip(' .')
        return rest if len(rest) > 8 else prompt
    return prompt


def find_item_prompt(input_tag, exclude_nodes):
    # the stem is reached as a *preceding sibling*, not an ancestor - two
    # template shapes are both common: (a) "<p>stem</p><ul><li>opt</li>...
    # </ul>" - the stem is a previous sibling of the whole <ul> - and
    # (b) "<div class=question-text>stem</div><div class=choice-item>opt
    # </div>..." - the stem is a previous sibling of the *first option row
    # itself* (there is no separate options-wrapper). Try the narrower (row)
    # scope first, then climb outward one level at a time; climbing
    # ancestors directly (rather than via their previous siblings) would
    # cross into the *next* question once it passes whatever shared parent
    # this one sits in.
    if exclude_nodes:
        node = exclude_nodes[0]
        for hop in range(4):
            if node is None:
                break
            prev_sib = node.find_previous_sibling()
            if prev_sib is not None:
                txt = strip_leading_qnum_repeated(
                    collapse_ws(text_excluding_nodes(prev_sib, exclude_nodes)))
                if 8 < len(txt) < MAX_PROMPT_LEN:
                    return txt
            node = node.parent

    node = input_tag
    for _ in range(8):
        node = node.parent
        if node is None:
            break
        text = strip_leading_qnum_repeated(collapse_ws(text_excluding_nodes(node, exclude_nodes)))
        if 8 < len(text) < MAX_PROMPT_LEN:
            return text
    return None


# ---------------------------------------------------------------------------
# single-answer MCQ: <input type="radio"> grouped by name, values A-H only
# ---------------------------------------------------------------------------

def extract_radio_mcq_groups(soup):
    radios = {}
    for r in soup.find_all('input', attrs={'type': 'radio'}):
        name = r.get('name')
        val = (r.get('value') or '').strip().upper()
        if not name or not LETTER_SET.match(val):
            continue
        radios.setdefault(name, []).append((val, r))

    items = []
    for name, pairs in radios.items():
        values = set(v for v, _ in pairs)
        if len(values) < 2:
            continue
        m = ID_QNUM_RE.match(name.strip())
        if not m:
            continue
        qnum = int(m.group(1))
        option_rows = [(v, find_option_row(tag)) for v, tag in pairs]
        exclude_nodes = [row for _, row in option_rows]
        options = []
        for v, row in option_rows:
            txt = collapse_ws(row.get_text(' ', strip=True))
            om = OPTION_LABEL_RE.match(txt)
            otext = collapse_ws(om.group(2)) if om else txt
            options.append({'code': v, 'text': otext})
        options.sort(key=lambda o: o['code'])
        first_tag = pairs[0][1]
        instr = find_instruction_text(first_tag)
        prompt = strip_instruction_overlap(
            find_item_prompt(first_tag, exclude_nodes) or f'Q{qnum}', instr)
        qrange = find_questions_range_header(first_tag)
        pnum = extract_passage_number_from_instruction(instr)
        if pnum is None:
            pnum = find_part_number_from_ancestors(first_tag)
        items.append({
            'qnum': qnum, 'prompt': prompt, 'options': options,
            'codes': [o['code'] for o in options],
            'instruction': instr, 'qrange': qrange, 'passage_num': pnum,
            'tag': first_tag,
        })
    items.sort(key=lambda it: it['qnum'])

    groups = []
    cur = None
    for it in items:
        if cur and cur['instr'] == it['instruction'] and it['qnum'] == cur['max'] + 1:
            cur['items'].append(it)
            cur['max'] = it['qnum']
        else:
            if cur:
                groups.append(cur)
            cur = {'instr': it['instruction'], 'min': it['qnum'], 'max': it['qnum'], 'items': [it]}
    if cur:
        groups.append(cur)

    out = []
    excluded = []
    for g in groups:
        first_item = g['items'][0]
        # a "Classify the features as belonging to: A ... B ... C ..." group
        # (same small category legend reused as the answer choices for every
        # statement in the group) is a Matching-Features-style classification
        # question, not a true multiple-choice question with its own unique
        # options per item - keep it out of the MCQ sheet rather than
        # mis-filing it, and report it separately instead
        same_options = len(g['items']) >= 2 and all(
            it['codes'] == first_item['codes'] and
            [o['text'] for o in it['options']] == [o['text'] for o in first_item['options']]
            for it in g['items'])
        is_classify = bool(g['instr']) and 'classify' in g['instr'].lower()
        # a "matching-grid" table (one row per statement, blank radio cells
        # under shared A/B/C... column headers, no visible option text) is a
        # Matching-type question rendered without any per-option wording to
        # show - unusable as an MCQ item regardless of the shared-options size
        blank_options = any(all(not o['text'] for o in it['options']) for it in g['items'])
        if is_classify or blank_options or (same_options and len(first_item['codes']) <= 4):
            if is_classify:
                reason = 'classification'
            elif blank_options:
                reason = 'blank-option-text-looks-like-matching-grid'
            else:
                reason = 'shared-options-looks-like-classification'
            excluded.append({
                'qnums': [it['qnum'] for it in g['items']],
                'instruction': g['instr'],
                'reason': reason,
            })
            continue
        out.append({
            'subtype': 'MCQ (single answer)',
            'instruction': g['instr'],
            'items': [{'qnum': it['qnum'], 'prompt': it['prompt'], 'options': it['options'],
                       'required': 1, 'codes': it['codes']} for it in g['items']],
            'qnums': [it['qnum'] for it in g['items']],
            'min': g['min'], 'max': g['max'],
            'passage_num': first_item['passage_num'],
            'qrange': first_item['qrange'],
            'template': 'radio',
        })
    return out, excluded


# ---------------------------------------------------------------------------
# choose TWO/THREE: <input type="checkbox"> grouped by shared name
# ---------------------------------------------------------------------------

def extract_checkbox_groups(soup):
    boxes = {}
    for c in soup.find_all('input', attrs={'type': 'checkbox'}):
        name = c.get('name') or c.get('id')
        val = (c.get('value') or '').strip().upper()
        if not name or not LETTER_SET.match(val):
            continue
        boxes.setdefault(name, []).append((val, c))

    out = []
    for name, pairs in boxes.items():
        values = set(v for v, _ in pairs)
        if len(values) < 2:
            continue
        first_tag = pairs[0][1]

        qnums = None
        container = first_tag.find_parent(attrs={'data-q': True})
        if container is not None:
            dq = container.get('data-q')
            nums = re.findall(r'\d+', dq)
            if nums:
                qnums = [int(n) for n in nums]
        if qnums is None:
            rm = RANGE_NAME_RE.match(name.strip())
            if rm:
                lo, hi = int(rm.group(1)), int(rm.group(2))
                qnums = list(range(lo, hi + 1))
        if qnums is None:
            qrange = find_questions_range_header(first_tag)
            if qrange:
                qnums = list(range(qrange[0], qrange[1] + 1))
        if qnums is None:
            m = ID_QNUM_RE.match(name.strip())
            if not m:
                continue
            qnums = [int(m.group(1))]

        option_rows = [(v, find_option_row(tag)) for v, tag in pairs]
        exclude_nodes = [row for _, row in option_rows]
        options = []
        for v, row in option_rows:
            txt = collapse_ws(row.get_text(' ', strip=True))
            om = OPTION_LABEL_RE.match(txt)
            otext = collapse_ws(om.group(2)) if om else txt
            options.append({'code': v, 'text': otext})
        options.sort(key=lambda o: o['code'])

        instr = find_instruction_text(first_tag)
        default_prompt = f"Questions {qnums[0]}-{qnums[-1]}"
        prompt = strip_instruction_overlap(
            find_item_prompt(first_tag, exclude_nodes) or default_prompt, instr)
        qrange = find_questions_range_header(first_tag) or (qnums[0], qnums[-1])
        pnum = extract_passage_number_from_instruction(instr)
        if pnum is None:
            pnum = find_part_number_from_ancestors(first_tag)

        out.append({
            'subtype': 'MCQ (choose multiple)',
            'instruction': instr,
            'items': [{'qnum': qnums, 'prompt': prompt, 'options': options,
                       'required': len(qnums), 'codes': [o['code'] for o in options]}],
            'qnums': qnums,
            'min': min(qnums), 'max': max(qnums),
            'passage_num': pnum,
            'qrange': qrange,
            'template': 'checkbox',
        })
    return out


# ---------------------------------------------------------------------------
# CD-IELTS data-driven single MCQ: mcqData (qnum -> {q, opts}) + mcqGroups
# (container id -> [qnums]); container's static instruction is recovered the
# same way as the Matching extractor does for matrixDefs/matrixGrid.
# ---------------------------------------------------------------------------

def extract_js_mcq_groups(soup, html):
    mcq_data = find_js_object_assignment(html, 'mcqData')
    mcq_groups = find_js_object_assignment(html, 'mcqGroups')
    if not mcq_data or not mcq_groups:
        return []
    out = []
    for container_id, qnum_list in mcq_groups.items():
        qnums = sorted(int(q) for q in qnum_list if str(q) in mcq_data)
        if not qnums:
            continue
        instr = None
        qrange = None
        cont = soup.find(id=container_id)
        if cont is not None:
            count = 0
            for prev in cont.find_all_previous(string=True):
                count += 1
                if count > 400:
                    break
                s = str(prev).strip()
                if re.search(r'choose|correct letter', s, re.I) and len(s) > 10:
                    block = nearest_block_ancestor(prev.parent)
                    instr = collapse_ws(block.get_text(' ', strip=True)) if block is not None else s
                    break
            for prev in cont.find_all_previous(string=QRANGE_RE):
                m = QRANGE_RE.search(str(prev))
                if m:
                    qrange = (int(m.group(1)), int(m.group(2)))
                break
        items = []
        for q in qnums:
            entry = mcq_data[str(q)]
            opts = entry.get('opts', {})
            options = [{'code': k, 'text': v} for k, v in opts.items()]
            options.sort(key=lambda o: o['code'])
            items.append({'qnum': q, 'prompt': entry.get('q', f'Q{q}'), 'options': options,
                          'required': 1, 'codes': [o['code'] for o in options]})
        pnum = extract_passage_number_from_instruction(instr)
        out.append({
            'subtype': 'MCQ (single answer)',
            'instruction': instr,
            'items': items,
            'qnums': qnums,
            'min': qnums[0], 'max': qnums[-1],
            'passage_num': pnum,
            'qrange': qrange,
            'template': 'mcqData:' + container_id,
        })
    return out


# ---------------------------------------------------------------------------

def extract_file(path):
    with open(path, encoding='utf-8', errors='replace') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'lxml')

    groups, excluded_classification = extract_radio_mcq_groups(soup)
    groups += extract_checkbox_groups(soup)
    groups += extract_js_mcq_groups(soup, html)

    for g in groups:
        if g['passage_num'] is None:
            lo = g['min']
            g['passage_num'] = 1 if lo <= 13 else 2 if lo <= 26 else 3

    seen_qnums = set()
    deduped = []
    for g in sorted(groups, key=lambda g: g['min']):
        qset = set(g['qnums'])
        if qset & seen_qnums:
            continue
        seen_qnums |= qset
        deduped.append(g)
    deduped.sort(key=lambda g: g['min'])

    passages = extract_passages(soup, html)
    answer_maps = find_answer_maps(html)
    needed = {}
    for g in deduped:
        for it in g['items']:
            valid = frozenset(c.upper() for c in it['codes'])
            qn = it['qnum']
            if isinstance(qn, list):
                for q in qn:
                    needed[q] = valid
            else:
                needed[qn] = valid
    best_map = pick_best_mcq_answer_map(answer_maps, needed) if answer_maps and needed else None
    ranged_entries = find_ranged_answer_entries(html)
    answers = {}
    if best_map:
        varname, entries = best_map
        for q, valid in needed.items():
            v = entries.get(q)
            if v is None:
                v = entries.get(str(q))
            norm = normalize_mcq_answer(v, valid)
            if norm is not None:
                answers[q] = norm
    # ranged-key fallback ('1-3': [...]) - independent of whether best_map
    # scored any hits, since a file's only MCQ answers can be the ones a
    # range key hides from the generic per-qnum scorer
    for q, valid in needed.items():
        if q in answers:
            continue
        norm = normalize_mcq_answer(ranged_entries.get(q), valid)
        if norm is not None:
            answers[q] = norm

    return {
        'file': path,
        'questions': deduped,
        'passages': passages,
        'answers': answers,
        'answer_map_var': best_map[0] if best_map else None,
        'excluded_classification': excluded_classification,
    }


if __name__ == '__main__':
    results = []
    for folder, code in FOLDERS.items():
        d = os.path.join(ROOT, folder)
        for fn in sorted(os.listdir(d)):
            if not fn.lower().endswith('.html'):
                continue
            path = os.path.join(d, fn)
            try:
                res = extract_file(path)
                res['folder_level'] = code
            except Exception as e:
                import traceback
                res = {'file': path, 'error': str(e), 'trace': traceback.format_exc(), 'folder_level': code}
            results.append(res)
            if 'questions' in res:
                for g in res['questions']:
                    g.pop('tag', None)
                    for it in g['items']:
                        it.pop('tag', None)

    out_path = sys.argv[1] if len(sys.argv) > 1 else "extract_mcq_out.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    def qcount(g):
        return len(g['qnums'])

    total_q = sum(qcount(g) for r in results if 'error' not in r for g in r.get('questions', []))
    total_groups = sum(len(r.get('questions', [])) for r in results if 'error' not in r)
    files_with_q = sum(1 for r in results if r.get('questions'))
    errs = [r for r in results if 'error' in r]
    print(f"Files processed: {len(results)}")
    print(f"Files with at least one MCQ group: {files_with_q}")
    print(f"Total MCQ question groups: {total_groups}")
    print(f"Total MCQ questions: {total_q}")
    print(f"Errors: {len(errs)}")
    for r in errs:
        print(' ERR', r['file'], r['error'])
    excl = [(r['file'], e) for r in results if 'error' not in r for e in r.get('excluded_classification', [])]
    print(f"Excluded as classification (not true MCQ): {len(excl)} group(s)")
    for f, e in excl:
        print('  EXCLUDED', f, e['qnums'], e['reason'], '-', (e['instruction'] or '')[:70])
    by_subtype = {}
    for r in results:
        if 'error' in r:
            continue
        for g in r.get('questions', []):
            by_subtype[g['subtype']] = by_subtype.get(g['subtype'], 0) + qcount(g)
    print('By subtype:', by_subtype)
