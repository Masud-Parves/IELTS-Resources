import os, re, json, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_tfng import (
    BeautifulSoup, find_answer_maps, parse_object_entries, extract_passages,
    find_part_number_from_ancestors, container_text_excluding, CHROME_TITLE_RE,
)

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # the Reading/ folder
FOLDERS = {"Passage 1": "P1", "Passage 2": "P2", "Passage 3": "P3"}

ID_QNUM_RE = re.compile(r'^q0*(\d{1,3})$', re.I)

NUMBER_WORDS = {1:'ONE',2:'TWO',3:'THREE',4:'FOUR',5:'FIVE',6:'SIX',7:'SEVEN',8:'EIGHT',
                9:'NINE',10:'TEN',11:'ELEVEN',12:'TWELVE',13:'THIRTEEN',14:'FOURTEEN',
                15:'FIFTEEN',16:'SIXTEEN',17:'SEVENTEEN',18:'EIGHTEEN',19:'NINETEEN',
                20:'TWENTY',21:'TWENTY-ONE',22:'TWENTY-TWO',23:'TWENTY-THREE',
                24:'TWENTY-FOUR',25:'TWENTY-FIVE',26:'TWENTY-SIX',27:'TWENTY-SEVEN',
                28:'TWENTY-EIGHT',29:'TWENTY-NINE',30:'THIRTY',31:'THIRTY-ONE',
                32:'THIRTY-TWO',33:'THIRTY-THREE',34:'THIRTY-FOUR',35:'THIRTY-FIVE',
                36:'THIRTY-SIX',37:'THIRTY-SEVEN',38:'THIRTY-EIGHT',39:'THIRTY-NINE',
                40:'FORTY'}


def is_number_word_decoy(entries):
    keys = [k for k in entries if isinstance(entries.get(k), str)]
    if len(keys) < 5:
        return False
    matches = sum(1 for k in keys if entries[k].strip().upper() == NUMBER_WORDS.get(k))
    return matches / len(keys) > 0.6


def pick_best_completion_answer_map(maps, needed_qnums):
    best = None
    best_score = -1
    for varname, entries in maps:
        if is_number_word_decoy(entries):
            continue
        score = sum(1 for q in needed_qnums if q in entries)
        if score > best_score:
            best_score = score
            best = (varname, entries)
    return best if best_score > 0 else None


# ---- instruction / sub-type detection -------------------------------------

INSTR_MARKER_RE = re.compile(
    r'complete the (summary|notes?|table|flow[- ]?chart|diagram|sentences?)'
    r'|choose\s+(?:no more than\s+)?\w+\s+words?'
    r'|ONE WORD ONLY|NO MORE THAN', re.I)

BOILERPLATE_LINE_RE = re.compile(r'^(write|choose|use)\b', re.I)


def find_instruction_block(input_tag):
    count = 0
    for prev in input_tag.find_all_previous(string=True):
        count += 1
        if count > 5000:
            break
        s = str(prev)
        if INSTR_MARKER_RE.search(s):
            parent = prev.parent
            block_text = container_text_excluding(parent) if parent else ''
            if len(block_text) < 25 and parent is not None and parent.parent:
                block_text = container_text_excluding(parent.parent)
            if not block_text:
                block_text = s.strip()
            return block_text
    return None


def classify_subtype(instr_text, has_table, has_wordbank):
    t = (instr_text or '').lower()
    if 'summary' in t:
        base = 'Summary Completion'
    elif 'table' in t or has_table:
        base = 'Table Completion'
    elif 'flow' in t and 'chart' in t:
        base = 'Flow-chart Completion'
    elif 'diagram' in t:
        base = 'Diagram Completion'
    elif 'note' in t:
        base = 'Note Completion'
    elif 'sentence' in t:
        base = 'Sentence Completion'
    else:
        base = 'Gap Fill'
    if base == 'Gap Fill':
        base = 'Gap Fill (with word/option bank)' if has_wordbank else 'Gap Fill (no word bank)'
    return base


def extract_passage_number_from_instruction(instr_text):
    if not instr_text:
        return None
    m = re.search(r'Reading Passage\s*(\d+)', instr_text, re.I)
    return int(m.group(1)) if m else None


def find_questions_range_header(input_tag):
    for prev in input_tag.find_all_previous(string=re.compile(r'Questions?\s*\d+\s*[\u2013\-]\s*\d+', re.I)):
        m = re.search(r'Questions?\s*(\d+)\s*[\u2013\-]\s*(\d+)', str(prev), re.I)
        if m:
            return int(m.group(1)), int(m.group(2))
    return None


# ---- HTML fragment -> simple block spec for rendering ----------------------

SKIP_TAGS = {'script', 'style', 'button', 'svg', 'nav'}
SKIP_CLASS_RE = re.compile(
    r'review-flag|word-warning|word-hint|inline-answer-feedback|inline-explanation|'
    r'nav-arrow|context-menu|highlight-toolbar|size-tooltip|settings|'
    r'q-num-inline|q-num\b|q-badge|sentence-num|question-number|qnum|'
    r'inline-qno|q-no\b|qno\b', re.I)


BARE_NUM_RE = re.compile(r'^\s*\d{1,3}\.?\s*$')


def node_is_skippable(el, qnum_filter=None):
    if getattr(el, 'name', None) in SKIP_TAGS:
        return True
    if hasattr(el, 'get') and el.get('class'):
        if SKIP_CLASS_RE.search(' '.join(el['class'])):
            return True
    if hasattr(el, 'get') and el.get('id') and re.search(r'^(hint|feedback|explain)', el['id'], re.I):
        return True
    # a small inline element whose entire content is just a bare number that
    # matches one of this group's question numbers is a redundant visual
    # "question number" label (varies by template/class name) - skip it
    # structurally rather than trying to enumerate every class name used
    if qnum_filter and getattr(el, 'name', None) in ('span', 'strong', 'b', 'sup', 'small'):
        if hasattr(el, 'find') and el.find(['input', 'select']) is not None:
            return False  # wraps the real blank - not just a number label
        txt = el.get_text(strip=True) if hasattr(el, 'get_text') else ''
        m = BARE_NUM_RE.match(txt)
        if m and int(re.search(r'\d+', txt).group()) in qnum_filter:
            return True
    return False


BLANK_TOKEN_RE = re.compile(r'\[\[Q:(\d+)\]\]')


def inline_text_with_blanks(el, qnum_filter=None):
    """Render inline content of el as a string with reportlab-safe <b>/<i> tags.
    Each text-input blank becomes a [[Q:origN]] token - the PDF build step
    substitutes these with the final renumbered blank marker, so extraction
    stays agnostic of final question numbering."""
    from xml.sax.saxutils import escape
    parts = []
    for child in el.children:
        if node_is_skippable(child, qnum_filter):
            continue
        if isinstance(child, str):
            # collapse runs of whitespace (incl. literal newlines from
            # pretty-printed source HTML) to a single space, but keep it so
            # words on either side of a stripped tag stay separated
            parts.append(escape(re.sub(r'\s+', ' ', str(child))))
            continue
        name = getattr(child, 'name', None)
        if name == 'input' and (child.get('type') or 'text').lower() == 'text':
            idv = child.get('id') or child.get('name') or ''
            m = ID_QNUM_RE.match(idv.strip())
            if m:
                qn = int(m.group(1))
                if qnum_filter is None or qn in qnum_filter:
                    parts.append(f'[[Q:{qn}]]')
                    continue
            parts.append('\u2026\u2026\u2026\u2026\u2026\u2026')
            continue
        if name == 'select':
            parts.append('\u2026\u2026\u2026\u2026\u2026\u2026')
            continue
        if name == 'br':
            parts.append('<br/>')
            continue
        if name in ('ul', 'ol'):
            # nested lists are rendered as their own bullet blocks by the
            # caller, not folded into this element's own inline text
            continue
        if name in ('b', 'strong'):
            parts.append('<b>' + inline_text_with_blanks(child, qnum_filter) + '</b>')
            continue
        if name in ('i', 'em'):
            parts.append('<i>' + inline_text_with_blanks(child, qnum_filter) + '</i>')
            continue
        if hasattr(child, 'children'):
            parts.append(inline_text_with_blanks(child, qnum_filter))
    return ''.join(parts)


BLOCK_TAGS_HEADING = {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}


def html_to_blocks(container, qnum_filter):
    """Walk container's children and emit a list of block dicts:
    {'type': 'heading'|'para'|'bullet'|'table', ...}"""
    blocks = []

    def process_list(ul_el, depth=0):
        for li in ul_el.find_all('li', recursive=False):
            txt = inline_text_with_blanks(li, qnum_filter).strip()
            if txt:
                blocks.append({'type': 'bullet', 'text': txt, 'depth': depth})
            for nested in li.find_all(['ul', 'ol'], recursive=False):
                process_list(nested, depth=depth + 1)

    def walk(el, in_list=False):
        for child in el.children:
            if node_is_skippable(child, qnum_filter):
                continue
            name = getattr(child, 'name', None)
            if name is None:
                text = str(child).strip()
                if text and not in_list:
                    blocks.append({'type': 'para', 'text': text})
                continue
            if name in BLOCK_TAGS_HEADING:
                txt = inline_text_with_blanks(child, qnum_filter).strip()
                if txt:
                    blocks.append({'type': 'heading', 'text': txt})
            elif name == 'table':
                rows = []
                for tr in child.find_all('tr'):
                    cells = tr.find_all(['td', 'th'])
                    row = [inline_text_with_blanks(c, qnum_filter).strip() for c in cells]
                    if row:
                        rows.append(row)
                if rows:
                    blocks.append({'type': 'table', 'rows': rows})
            elif name in ('ul', 'ol'):
                process_list(child, depth=0)
            elif name == 'li':
                txt = inline_text_with_blanks(child, qnum_filter).strip()
                if txt:
                    blocks.append({'type': 'bullet', 'text': txt})
                for nested in child.find_all(['ul', 'ol'], recursive=False):
                    process_list(nested, depth=1)
            elif name == 'p':
                txt = inline_text_with_blanks(child, qnum_filter).strip()
                if txt and not CHROME_TITLE_RE.match(re.sub('<[^>]+>', '', txt)):
                    blocks.append({'type': 'para', 'text': txt})
            elif name == 'div':
                has_block_children = child.find(['p', 'div', 'ul', 'ol', 'table', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                if has_block_children:
                    walk(child)
                else:
                    txt = inline_text_with_blanks(child, qnum_filter).strip()
                    if txt:
                        blocks.append({'type': 'para', 'text': txt})
            elif name == 'span':
                txt = inline_text_with_blanks(child, qnum_filter).strip()
                if txt:
                    blocks.append({'type': 'para', 'text': txt})
            elif name == 'input' and (child.get('type') or 'text').lower() == 'text':
                # a blank with no surrounding block wrapper directly at this
                # level - render it as its own minimal paragraph rather than
                # silently dropping it
                idv = child.get('id') or child.get('name') or ''
                m = ID_QNUM_RE.match(idv.strip())
                qn = int(m.group(1)) if m else None
                if qn is not None and (qnum_filter is None or qn in qnum_filter):
                    blocks.append({'type': 'para', 'text': f'[[Q:{qn}]]'})
            elif name in ('tbody', 'thead', 'tr'):
                walk(child)
            else:
                if hasattr(child, 'children'):
                    walk(child)

    top_name = getattr(container, 'name', None)
    if top_name == 'table':
        rows = []
        for tr in container.find_all('tr'):
            cells = tr.find_all(['td', 'th'])
            row = [inline_text_with_blanks(c, qnum_filter).strip() for c in cells]
            if row:
                rows.append(row)
        if rows:
            blocks.append({'type': 'table', 'rows': rows})
    elif top_name in ('p', 'li', 'td', 'th', 'span'):
        # the container itself is a single inline-content leaf (e.g. a <p> that
        # directly holds the running text with inline blanks) - render it whole
        # rather than shredding its text/input children into separate blocks
        txt = inline_text_with_blanks(container, qnum_filter).strip()
        if txt:
            blocks.append({'type': 'para', 'text': txt})
    else:
        walk(container)
    # drop empty/near-empty paragraphs and dedupe consecutive identical blocks
    cleaned = []
    for b in blocks:
        if b['type'] in ('para', 'heading', 'bullet'):
            b['text'] = finalize_text(b.get('text') or '')
            if len(b['text']) < 2:
                continue
        elif b['type'] == 'table':
            b['rows'] = [[finalize_text(c) for c in row] for row in b['rows']]
        if cleaned and cleaned[-1] == b:
            continue
        cleaned.append(b)
    return cleaned


LEADING_ITEM_NUM_RE = re.compile(r'^\s*\d{1,3}\.\s*')
SPACE_BEFORE_PUNCT_RE = re.compile(r'\s+([.,;:!?])')


def finalize_text(t):
    t = re.sub(r'[ \t]+', ' ', t).strip()
    t = LEADING_ITEM_NUM_RE.sub('', t, count=1)
    t = SPACE_BEFORE_PUNCT_RE.sub(r'\1', t)
    return t.strip()


INLINE_LEAF_TAGS = {'p', 'li', 'td', 'th', 'span', 'strong', 'b', 'div'}


def find_group_container(inputs):
    """Smallest common ancestor wrapping all inputs in this contiguous group."""
    first, last = inputs[0], inputs[-1]
    ancestors_of_first = []
    node = first
    while node is not None:
        ancestors_of_first.append(node)
        node = node.parent
    container = first.parent
    for anc in ancestors_of_first:
        if hasattr(anc, 'descendants'):
            try:
                if any(d is last for d in anc.descendants):
                    container = anc
                    break
            except RecursionError:
                continue
    # normalize: if we landed inside a table's internal structure, use the
    # enclosing <table> itself so rows/cells can be rendered as a real table
    if getattr(container, 'name', None) in ('tbody', 'thead', 'tr'):
        parent_table = container.find_parent('table')
        if parent_table is not None:
            container = parent_table
    # climb one level past a single inline leaf (p/li/td/span) so a sibling
    # heading/label (e.g. "<h5>Soil as Medication</h5>" next to the <p>) is
    # captured too, as long as that doesn't pull in excessive extra content
    if getattr(container, 'name', None) in ('p', 'li', 'td', 'th', 'span') and container.parent is not None:
        parent = container.parent
        if getattr(parent, 'name', None) not in ('body', 'html', None):
            own_len = len(container_text_excluding(container))
            parent_len = len(container_text_excluding(parent))
            if parent_len < own_len + 300:
                container = parent
    return container


def has_wordbank_nearby(container):
    text = container_text_excluding(container).lower() if container else ''
    return bool(re.search(r'word bank|box below|list below|options?:', text))


def extract_file(path):
    with open(path, encoding='utf-8', errors='replace') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'lxml')

    text_inputs = []
    for inp in soup.find_all('input'):
        itype = (inp.get('type') or 'text').lower()
        if itype != 'text':
            continue
        idv = (inp.get('id') or inp.get('name') or '').strip()
        m = ID_QNUM_RE.match(idv)
        if not m:
            continue
        text_inputs.append((int(m.group(1)), inp))
    text_inputs.sort(key=lambda x: x[0])

    # group contiguous qnums sharing the same instruction text
    groups = []
    cur = None
    for qnum, tag in text_inputs:
        instr = find_instruction_block(tag)
        key = instr
        if cur and cur['instr'] == key and qnum == cur['max'] + 1:
            cur['items'].append((qnum, tag))
            cur['max'] = qnum
        else:
            if cur:
                groups.append(cur)
            cur = {'instr': instr, 'min': qnum, 'max': qnum, 'items': [(qnum, tag)]}
    if cur:
        groups.append(cur)

    questions = []
    for g in groups:
        tags = [t for _, t in g['items']]
        container = find_group_container(tags)
        qnum_set = set(q for q, _ in g['items'])
        blocks = html_to_blocks(container, qnum_set)
        has_table = any(b['type'] == 'table' for b in blocks)
        wordbank = has_wordbank_nearby(container.parent if container and container.parent else container)
        subtype = classify_subtype(g['instr'], has_table, wordbank)
        pnum = extract_passage_number_from_instruction(g['instr'])
        if pnum is None:
            pnum = find_part_number_from_ancestors(tags[0])
        qrange = find_questions_range_header(tags[0])
        questions.append({
            'qnums': sorted(qnum_set),
            'min': g['min'], 'max': g['max'],
            'subtype': subtype,
            'instruction': g['instr'],
            'qrange': qrange,
            'passage_num': pnum,
            'blocks': blocks,
        })

    passages = extract_passages(soup, html)
    answer_maps = find_answer_maps(html)
    needed = [q for g in questions for q in g['qnums']]
    best_map = pick_best_completion_answer_map(answer_maps, needed) if answer_maps else None
    answers = {}
    if best_map:
        varname, entries = best_map
        for qnum in needed:
            v = entries.get(qnum)
            if v is not None:
                if isinstance(v, list):
                    v = ' / '.join(str(x) for x in v)
                answers[qnum] = v

    return {
        'file': path,
        'questions': questions,
        'passages': passages,
        'answers': answers,
        'answer_map_var': best_map[0] if best_map else None,
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

    out_path = sys.argv[1] if len(sys.argv) > 1 else "extract_completion_out.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    total_q = sum(len(g['qnums']) for r in results if 'error' not in r for g in r.get('questions', []))
    total_groups = sum(len(r.get('questions', [])) for r in results if 'error' not in r)
    files_with_q = sum(1 for r in results if r.get('questions'))
    errs = [r for r in results if 'error' in r]
    print(f"Files processed: {len(results)}")
    print(f"Files with at least one completion group: {files_with_q}")
    print(f"Total completion question groups: {total_groups}")
    print(f"Total completion questions: {total_q}")
    print(f"Errors: {len(errs)}")
    for r in errs:
        print(' ERR', r['file'], r['error'])
