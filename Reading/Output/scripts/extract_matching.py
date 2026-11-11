import os, re, json, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_tfng import (
    BeautifulSoup, find_answer_maps, extract_passages,
    find_part_number_from_ancestors, container_text_excluding,
    find_questions_range_header, pick_best_answer_map, _value_matches_option_set,
)
from js_obj import find_js_object_assignment

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # the Reading/ folder
FOLDERS = {"Passage 1": "P1", "Passage 2": "P2", "Passage 3": "P3"}

ROMAN_SET = {'i','ii','iii','iv','v','vi','vii','viii','ix','x','xi','xii'}
LETTER_RE = re.compile(r'^[A-L]$')
ID_QNUM_RE = re.compile(r'^q?0*(\d{1,3})$', re.I)


PLACEHOLDER_OPT_RE = re.compile(r'select|choose|^--+$|^\s*$|^[–—\-\s]+$', re.I)


def select_code_scheme(select_tag):
    """Return ('roman'|'letter', [codes in document order]) if every real
    (non-placeholder) option of this <select> is a bare roman numeral or a
    single letter A-L, else None. (Across this whole corpus every <select> is
    used exclusively for a Matching sub-type, never for Completion.)"""
    options = select_tag.find_all('option')
    if not options:
        return None
    has_real_value_attr = any((o.get('value') or '').strip() for o in options)
    codes = []
    for opt in options:
        if has_real_value_attr:
            v = (opt.get('value') or '').strip()
            if not v:
                continue
        else:
            v = opt.get_text(strip=True)
            if not v or PLACEHOLDER_OPT_RE.match(v):
                continue
        codes.append(v)
    if not codes:
        return None
    if all(c.lower() in ROMAN_SET for c in codes):
        return ('roman', codes)
    if all(LETTER_RE.match(c) for c in codes):
        return ('letter', codes)
    return None


# ---------------------------------------------------------------------------
# instruction / rubric detection for <select>-based groups
# ---------------------------------------------------------------------------

RUBRIC_MARKER_RE = re.compile(
    r'heading for each|list of headings|which (?:paragraph|section) contains|'
    r'match each|correct ending|matching sentence endings|'
    r'complete the summary using|complete the summary below|'
    r'correct person|correct researcher|correct writer|correct letter.{0,20}people|'
    r'the correct (?:name|date|place|feature)', re.I)

BOILERPLATE_LINE_RE = re.compile(r'^(write|choose\.\.\.|--|select)\b', re.I)
BLOCK_TAGS = {'p', 'div', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'td', 'th'}


def nearest_block_ancestor(el):
    node = el
    while node is not None and getattr(node, 'name', None) not in BLOCK_TAGS:
        node = node.parent
    return node


BARE_BANK_TITLE_RE = re.compile(r'^\s*List of [A-Za-z ]+\s*$', re.I)


def find_rubric_block(tag):
    """Walk backward for the nearest text node matching a Matching-family
    rubric marker, and return its nearest block-level ancestor element (so a
    bank box can be found by sibling-walking forward from a real <p>/<div>,
    not from a bare inline <strong> with no siblings of its own). A bare bank
    title line ("List of Headings") is skipped in favour of the fuller
    instruction sentence that should appear a little further back."""
    count = 0
    best_bare = None
    for prev in tag.find_all_previous(string=True):
        count += 1
        if count > 6000:
            break
        s = str(prev).strip()
        if RUBRIC_MARKER_RE.search(s):
            block = nearest_block_ancestor(prev.parent)
            if block is None:
                continue
            if BARE_BANK_TITLE_RE.match(s):
                if best_bare is None:
                    best_bare = block
                continue
            return block
    return best_bare


def find_instruction_block(tag):
    block = find_rubric_block(tag)
    if block is None:
        return None
    block_text = container_text_excluding_noselect(block)
    if len(block_text) < 25 and block.parent is not None:
        parent_text = container_text_excluding_noselect(block.parent)
        if len(parent_text) < 400:
            block_text = parent_text
    if not block_text:
        return None
    if BOILERPLATE_LINE_RE.match(block_text) and len(block_text) < 40:
        return None
    # a bare bank-title line ("List of Headings") is not the real rubric
    # sentence - keep its text anyway (classify_subtype still works off it)
    # only when nothing fuller is available; callers needing the bank box
    # itself use find_rubric_block directly.
    return block_text


def container_text_excluding_noselect(container):
    """Like container_text_excluding, but also drops text inside any
    descendant <select> (its <option> labels are UI chrome, not source
    wording) and inside hidden analysis/explanation blocks."""
    parts = []
    for desc in container.descendants:
        if not isinstance(desc, str):
            continue
        skip = False
        anc = desc.parent
        while anc is not None:
            if getattr(anc, 'name', None) == 'select':
                skip = True
                break
            if anc.has_attr('class') and re.search(
                    r'analysis|explain|answer-?key|review-flag|ca-display|correct-answer-display',
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
    return ' '.join(parts)


def extract_passage_number_from_instruction(instr_text):
    if not instr_text:
        return None
    m = re.search(r'Reading Passage\s*(\d+)', instr_text, re.I)
    return int(m.group(1)) if m else None


# ---------------------------------------------------------------------------
# sub-type classification
# ---------------------------------------------------------------------------

def classify_subtype(instr_text, code_scheme):
    t = (instr_text or '').lower()
    if 'summary' in t and ('word' in t or 'list of words' in t or 'box' in t):
        return 'Summary Completion (options)'
    if 'heading' in t or 'list of headings' in t:
        return 'Matching Headings'
    if ('paragraph' in t and 'contain' in t) or ('section' in t and 'contain' in t):
        return 'Matching Information'
    if 'ending' in t:
        return 'Matching Sentence Endings'
    if 'match each' in t or 'correct person' in t or 'correct researcher' in t or \
       'correct writer' in t or 'correct name' in t or 'correct date' in t or 'correct place' in t:
        return 'Matching Features'
    # fallback purely from the option code scheme
    if code_scheme == 'roman':
        return 'Matching Headings'
    return 'Matching Information'


# ---------------------------------------------------------------------------
# bank / legend detection for <select>-based groups
# ---------------------------------------------------------------------------

BANK_LINE_RE = re.compile(r'^\s*([ivx]{1,5}|[A-L])[\.\)\u2013\u2014:]?\s+(\S.*\S|\S)\s*$', re.I)
LIST_OF_RE = re.compile(r'^\s*(List of [A-Za-z ]+)\s*$', re.I)


def split_lines_on_br(tag):
    """Split a leaf <p>/<li>'s rendered text into separate lines wherever a
    <br> tag occurs (BeautifulSoup's get_text() otherwise runs everything
    together), so a bank packed as "<strong>List of X</strong><br>A ...<br>B
    ..." in a single <p> can still be read one option per line."""
    lines = []
    cur = []
    for child in tag.contents:
        if getattr(child, 'name', None) == 'br':
            lines.append(''.join(cur).strip())
            cur = []
        elif hasattr(child, 'get_text'):
            cur.append(child.get_text(' ', strip=False))
        else:
            cur.append(str(child))
    if cur:
        lines.append(''.join(cur).strip())
    return [re.sub(r'\s+', ' ', l).strip() for l in lines if l and l.strip()]


def find_bank_near(rubric_el, codes, code_scheme):
    """Look for a named box (.headings-box / .features-box / .answers-box) or
    a plain run of '<code> <text>' lines following the rubric paragraph, that
    supplies full option text for each code (e.g. headings, people, endings).
    Stops once it reaches the first real question item (a <select>). Walks
    forward in full document order (not just same-level siblings), since the
    bank is sometimes nested one level deeper than the rubric paragraph (a
    sibling of the rubric's own *container* div, not of the <p> itself)."""
    if rubric_el is None:
        return None, None
    valid_codes = set(c.lower() if code_scheme == 'roman' else c for c in codes)
    bank_title = None
    bank = {}
    hops = 0
    for node in rubric_el.find_all_next(['p', 'div', 'li']):
        hops += 1
        if hops > 120:
            break
        has_block_children = node.find(['p', 'div', 'li']) is not None
        cls = ' '.join(node.get('class', [])) if hasattr(node, 'get') and node.get('class') else ''
        if re.search(r'headings-box|features-box|answers-box', cls, re.I):
            for child in (node.find_all(['div', 'p', 'li'], recursive=False) or node.find_all(['div', 'p', 'li'])):
                txt = child.get_text(' ', strip=True)
                m = BANK_LINE_RE.match(txt)
                if m:
                    code = m.group(1)
                    key = code.lower() if code_scheme == 'roman' else code
                    if key in valid_codes:
                        bank[code] = m.group(2).strip()
            if bank:
                break
            continue
        if has_block_children:
            # a pass-through ancestor (e.g. the whole question block) - its
            # own children will each be visited individually next; only
            # treat it as the "reached the first item" stop signal once that
            # item's own (leaf) wrapper is reached below
            continue
        if node.find('select') is not None:
            # this leaf node directly wraps a <select> - we've reached the
            # first real question item, stop looking for more bank lines
            break
        # a leaf <p>/<li> may itself pack the whole bank as one block of text
        # separated only by <br> tags (no nested <p>/<div>) - split on those
        # so each "A  Full Name" line is tested on its own
        if node.find('br') is not None:
            lines = split_lines_on_br(node)
        else:
            one = node.get_text(' ', strip=True)
            lines = [one] if one else []
        stop = False
        for txt in lines:
            lm = LIST_OF_RE.match(txt)
            if lm:
                bank_title = lm.group(1)
                continue
            m = BANK_LINE_RE.match(txt)
            if m:
                code = m.group(1)
                key = code.lower() if code_scheme == 'roman' else code
                if key in valid_codes:
                    bank[code] = m.group(2).strip()
                    continue
            if bank:
                # mid-bank-list and hit a non-matching line - stop
                stop = True
                break
        if stop:
            break
    if len(bank) >= max(2, len(valid_codes) - 1):
        ordered = sorted(bank.items(), key=lambda kv: (
            list(ROMAN_SET).index(kv[0].lower()) if code_scheme == 'roman' and kv[0].lower() in ROMAN_SET else ord(kv[0][0])
        ))
        # keep original insertion/alpha order instead: codes param order
        order_index = {c: i for i, c in enumerate(codes)}
        ordered = sorted(bank.items(), key=lambda kv: order_index.get(kv[0], 999))
        return bank_title, ordered
    return None, None


# ---------------------------------------------------------------------------
# item statement text for a single <select>
# ---------------------------------------------------------------------------

LEADING_QNUM_RE = re.compile(r'^\s*(?:Questions?\s*)?\d{1,3}[\.\)]?\s*')


def find_item_statement(select_tag, qnum):
    node = select_tag
    for _ in range(6):
        node = node.parent
        if node is None:
            break
        text = container_text_excluding_noselect(node)
        if len(text) > 2:
            text = LEADING_QNUM_RE.sub('', text, count=1).strip()
            # strip a trailing/leading lone "Select"/"--" placeholder artefact
            text = re.sub(r'^(Select|--)\s*', '', text, flags=re.I).strip()
            if text:
                return text
    return f'Q{qnum}'


# ---------------------------------------------------------------------------
# template A: static <select> dropdown groups
# ---------------------------------------------------------------------------

def extract_select_groups(soup):
    selects = []
    for sel in soup.find_all('select'):
        idv = (sel.get('id') or sel.get('name') or sel.get('data-question') or
               sel.get('data-q') or '').strip()
        m = ID_QNUM_RE.match(idv)
        if not m:
            continue
        scheme_codes = select_code_scheme(sel)
        if not scheme_codes:
            continue
        scheme, codes = scheme_codes
        qnum = int(m.group(1))
        selects.append({'qnum': qnum, 'tag': sel, 'scheme': scheme, 'codes': codes})
    selects.sort(key=lambda x: x['qnum'])

    groups = []
    cur = None
    for s in selects:
        instr_el_text = find_instruction_block(s['tag'])
        if cur and cur['instr'] == instr_el_text and s['qnum'] == cur['max'] + 1 and cur['scheme'] == s['scheme']:
            cur['items'].append(s)
            cur['max'] = s['qnum']
        else:
            if cur:
                groups.append(cur)
            cur = {'instr': instr_el_text, 'min': s['qnum'], 'max': s['qnum'],
                   'items': [s], 'scheme': s['scheme']}
    if cur:
        groups.append(cur)

    out = []
    for g in groups:
        subtype = classify_subtype(g['instr'], g['scheme'])
        codes = g['items'][0]['codes']
        first_tag = g['items'][0]['tag']
        rubric_el = find_rubric_block(first_tag)
        bank_title, bank = (None, None)
        if subtype in ('Matching Headings', 'Matching Features', 'Matching Sentence Endings'):
            bank_title, bank = find_bank_near(rubric_el, codes, g['scheme'])
        items = []
        for s in g['items']:
            stmt = find_item_statement(s['tag'], s['qnum'])
            items.append({'qnum': s['qnum'], 'statement': stmt})
        pnum = extract_passage_number_from_instruction(g['instr'])
        if pnum is None:
            pnum = find_part_number_from_ancestors(first_tag)
        qrange = find_questions_range_header(first_tag)
        out.append({
            'subtype': subtype,
            'instruction': g['instr'],
            'bank_title': bank_title,
            'bank': bank,
            'items': items,
            'qnums': [it['qnum'] for it in items],
            'min': g['min'], 'max': g['max'],
            'codes': codes,
            'code_scheme': g['scheme'],
            'passage_num': pnum,
            'qrange': qrange,
            'template': 'select',
        })
    return out


# ---------------------------------------------------------------------------
# template B: matrixDefs (JS data object) groups, CD-IELTS engine
# ---------------------------------------------------------------------------

def extract_matrix_groups(soup, html):
    matrix_defs = find_js_object_assignment(html, 'matrixDefs')
    if not matrix_defs:
        return []
    out = []
    for key, entry in matrix_defs.items():
        if not isinstance(entry, dict):
            continue
        items = entry.get('items') or {}
        if not items:
            continue
        codes = entry.get('codes') or entry.get('cols') or []
        container_id = entry.get('container')
        # recover the *static* rubric paragraph that precedes the (JS-filled)
        # empty container div, so we quote the file's own wording verbatim
        instr = None
        qrange = None
        if container_id:
            cont = soup.find(id=container_id)
            if cont is not None:
                count = 0
                for prev in cont.find_all_previous(string=True):
                    count += 1
                    if count > 400:
                        break
                    s = str(prev).strip()
                    if re.search(r'\bmatch|choose|complete|which (?:paragraph|section)', s, re.I) and len(s) > 15:
                        block = nearest_block_ancestor(prev.parent)
                        instr = container_text_excluding_noselect(block) if block is not None else s
                        break
                for prev in cont.find_all_previous(string=re.compile(r'Questions?\s*\d+\s*[\u2013\-]\s*\d+', re.I)):
                    m = re.search(r'Questions?\s*(\d+)\s*[\u2013\-]\s*(\d+)', str(prev), re.I)
                    if m:
                        qrange = (int(m.group(1)), int(m.group(2)))
                    break
        if instr is None:
            instr = entry.get('help') or entry.get('title') or entry.get('header') or ''
        qnums = sorted(int(k) for k in items.keys())
        pnum = extract_passage_number_from_instruction(instr)
        legend = entry.get('legend') or {}
        legend_title = entry.get('legendTitle') or entry.get('legend_title')
        subtype = classify_subtype(instr, 'roman' if all(str(c).lower() in ROMAN_SET for c in codes) else 'letter')
        bank = None
        if legend:
            order_index = {c: i for i, c in enumerate(codes)} if codes else {}
            bank = sorted(legend.items(), key=lambda kv: order_index.get(kv[0], 999))
            # a plain "A: Paragraph A" legend (auto-generated for which-paragraph
            # groups) carries no real information - drop it
            if subtype == 'Matching Information' and all(
                    re.match(r'^(Paragraph|Section)\s+[A-Z]$', v, re.I) for _, v in bank):
                bank = None
                legend_title = None
        items_list = [{'qnum': int(k), 'statement': v} for k, v in items.items()]
        items_list.sort(key=lambda d: d['qnum'])
        out.append({
            'subtype': subtype,
            'instruction': instr,
            'bank_title': legend_title,
            'bank': bank,
            'items': items_list,
            'qnums': qnums,
            'min': qnums[0], 'max': qnums[-1],
            'codes': codes,
            'code_scheme': 'roman' if all(str(c).lower() in ROMAN_SET for c in codes) else 'letter',
            'passage_num': pnum,
            'qrange': qrange,
            'template': 'matrix:' + key,
        })
    return out


# ---------------------------------------------------------------------------
# template C: drag-and-drop Matching Headings (.headings-box / mh-heading-card
# + mh-drop-slot[data-question] placed against lettered paragraphs)
# ---------------------------------------------------------------------------

PARA_LETTER_RE = re.compile(r'^([A-Z])\b')


def extract_drag_heading_groups(soup):
    out = []
    for box in soup.find_all(class_=re.compile(r'\bheadings-box\b')):
        cards = box.find_all(class_=re.compile(r'\bmh-heading-card\b'))
        bank = []
        for c in cards:
            code = (c.get('data-code') or '').strip()
            txt = c.get_text(' ', strip=True)
            txt = re.sub(r'^' + re.escape(code) + r'\s*', '', txt, count=1).strip()
            if code:
                bank.append((code, txt))
        if not bank:
            continue
        # a bank keyed A/B/C... (not roman numerals) is a word bank for a
        # Summary-Completion-with-options exercise reusing the same drag
        # widget/CSS, not a genuine heading-matching group - handled instead
        # by extract_wordbank_summary_groups()
        if not all(c.lower() in ROMAN_SET for c in (code for code, _ in bank)):
            continue
        # rubric: nearest preceding element with class instruction/q-title, or
        # just the previous sibling paragraph
        instr = None
        qrange = None
        prev = box.find_previous(class_=re.compile(r'\binstruction\b'))
        if prev is not None:
            instr = prev.get_text(' ', strip=True)
        qt = box.find_previous(class_=re.compile(r'\bq-title\b'))
        if qt is not None:
            m = re.search(r'Questions?\s*(\d+)\s*[\u2013\-]\s*(\d+)', qt.get_text(' ', strip=True), re.I)
            if m:
                qrange = (int(m.group(1)), int(m.group(2)))
        slots = soup.find_all(class_=re.compile(r'\bmh-drop-slot\b'))
        items = []
        for slot in slots:
            qn = slot.get('data-question')
            if not qn or not qn.isdigit():
                continue
            qn = int(qn)
            if qrange and not (qrange[0] <= qn <= qrange[1]):
                continue
            # paragraph letter: look at the following sibling paragraph's
            # leading bold letter (A/B/C...), which is how this passage marks
            # its own paragraphs
            letter = None
            host = slot.find_parent(['p', 'div'])
            hop = host
            for _ in range(5):
                if hop is None:
                    break
                nxt = hop.find_next_sibling(['p', 'div'])
                if nxt is not None:
                    strong = nxt.find(['strong', 'b'])
                    cand = strong.get_text(strip=True) if strong else nxt.get_text(strip=True)[:1]
                    m = PARA_LETTER_RE.match(cand)
                    if m:
                        letter = m.group(1)
                        break
                hop = nxt
            items.append({'qnum': qn, 'statement': f'Paragraph {letter}' if letter else f'Q{qn}'})
        if not items:
            continue
        items.sort(key=lambda d: d['qnum'])
        qnums = [it['qnum'] for it in items]
        pnum = extract_passage_number_from_instruction(instr) or find_part_number_from_ancestors(box)
        out.append({
            'subtype': 'Matching Headings',
            'instruction': instr,
            'bank_title': 'List of Headings',
            'bank': bank,
            'items': items,
            'qnums': qnums,
            'min': min(qnums), 'max': max(qnums),
            'codes': [c for c, _ in bank],
            'code_scheme': 'roman',
            'passage_num': pnum,
            'qrange': qrange,
            'template': 'drag-heading',
        })
    return out


# ---------------------------------------------------------------------------
# template D: drag-word-bank Summary Completion (reuses the mh-drop-slot
# widget for prose blanks instead of per-paragraph headings; bank is keyed
# A/B/C... with short single-word/phrase options, not roman numerals)
# ---------------------------------------------------------------------------

def extract_wordbank_summary_groups(soup):
    out = []
    for box in soup.find_all(class_=re.compile(r'\bheadings-box\b|\bfeatures-box\b')):
        cards = box.find_all(class_=re.compile(r'\bmh-heading-card\b'))
        bank = []
        for c in cards:
            code = (c.get('data-code') or '').strip()
            txt = c.get_text(' ', strip=True)
            txt = re.sub(r'^' + re.escape(code) + r'\s*', '', txt, count=1).strip()
            if code:
                bank.append((code, txt))
        if not bank or all(c.lower() in ROMAN_SET for c, _ in bank):
            continue
        instr = None
        prev = box.find_previous(class_=re.compile(r'\binstruction\b'))
        if prev is not None:
            instr = prev.get_text(' ', strip=True)
        if not instr or not re.search(r'summary|word', instr, re.I):
            continue
        qrange = None
        qt = box.find_previous(class_=re.compile(r'\bq-title\b'))
        if qt is not None:
            m = re.search(r'Questions?\s*(\d+)\s*[–\-]\s*(\d+)', qt.get_text(' ', strip=True), re.I)
            if m:
                qrange = (int(m.group(1)), int(m.group(2)))
        container = box.find_previous(class_=re.compile(r'note-box|completion-list|summary'))
        if container is None:
            for cand in box.find_all_previous('div'):
                if cand is box:
                    continue
                if cand.find(class_=re.compile(r'\bmh-drop-slot\b')) is not None:
                    container = cand
                    break
        if container is None:
            continue
        slots = container.find_all(class_=re.compile(r'\bmh-drop-slot\b'))
        qnums = sorted({int(s.get('data-question')) for s in slots
                        if (s.get('data-question') or '').isdigit()})
        if qrange:
            qnums = [q for q in qnums if qrange[0] <= q <= qrange[1]]
        if not qnums:
            continue

        blocks = []
        h = container.find(['h3', 'h4'])
        if h:
            blocks.append({'type': 'heading', 'text': h.get_text(' ', strip=True)})

        parts = []

        def walk(el):
            for child in el.children:
                name = getattr(child, 'name', None)
                if name in ('h3', 'h4'):
                    continue
                if name is None:
                    parts.append(re.sub(r'\s+', ' ', str(child)))
                    continue
                cls = ' '.join(child.get('class', [])) if child.has_attr('class') else ''
                if 'mh-drop-slot' in cls:
                    qn = child.get('data-question')
                    parts.append(f'[[Q:{qn}]]')
                elif name in ('strong', 'b'):
                    parts.append('<b>' + child.get_text(' ', strip=True) + '</b>')
                elif name == 'br':
                    parts.append(' ')
                elif hasattr(child, 'children'):
                    walk(child)
                else:
                    parts.append(child.get_text(' ', strip=True))

        walk(container)
        text = re.sub(r'\s+', ' ', ''.join(parts)).strip()
        blocks.append({'type': 'para', 'text': text})
        items = [{'qnum': q, 'statement': None} for q in qnums]
        pnum = extract_passage_number_from_instruction(instr) or find_part_number_from_ancestors(box)
        out.append({
            'subtype': 'Summary Completion (options)',
            'instruction': instr,
            'bank_title': 'Word Bank',
            'bank': bank,
            'items': items,
            'blocks': blocks,
            'qnums': qnums,
            'min': qnums[0], 'max': qnums[-1],
            'codes': [c for c, _ in bank],
            'code_scheme': 'letter',
            'passage_num': pnum,
            'qrange': qrange,
            'template': 'wordbank-summary',
        })
    return out


# ---------------------------------------------------------------------------

def extract_file(path):
    with open(path, encoding='utf-8', errors='replace') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'lxml')

    groups = extract_select_groups(soup)
    groups += extract_matrix_groups(soup, html)
    groups += extract_drag_heading_groups(soup)
    groups += extract_wordbank_summary_groups(soup)

    # de-dup by qnum set overlap (same question covered by >1 detector) -
    # prefer the richer group (one with a bank) when overlapping
    # universal fallback for groups whose passage number couldn't be read off
    # an explicit "Reading Passage N" phrase or DOM ancestor: IELTS Academic
    # Reading parts have fixed question-number boundaries (1-13/14-26/27-40)
    for g in groups:
        if g['passage_num'] is None:
            lo = g['min']
            g['passage_num'] = 1 if lo <= 13 else 2 if lo <= 26 else 3

    seen_qnums = set()
    deduped = []
    for g in sorted(groups, key=lambda g: (0 if g.get('bank') else 1, g['min'])):
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
        # _value_matches_option_set() upper-cases the candidate value before
        # comparing, so the option set it is checked against must itself be
        # upper-case (true for both roman numerals and letters here)
        valid = frozenset(c.upper() for c in g['codes'])
        for q in g['qnums']:
            needed[q] = valid
    best_map = pick_best_answer_map(answer_maps, needed) if answer_maps and needed else None
    answers = {}
    if best_map:
        varname, entries = best_map
        for q, valid in needed.items():
            v = entries.get(q)
            if v is not None and _value_matches_option_set(v, valid):
                answers[q] = v if not isinstance(v, list) else ' / '.join(v)

    return {
        'file': path,
        'questions': deduped,
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

    out_path = sys.argv[1] if len(sys.argv) > 1 else "extract_matching_out.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    total_q = sum(len(g['qnums']) for r in results if 'error' not in r for g in r.get('questions', []))
    total_groups = sum(len(r.get('questions', [])) for r in results if 'error' not in r)
    files_with_q = sum(1 for r in results if r.get('questions'))
    errs = [r for r in results if 'error' in r]
    print(f"Files processed: {len(results)}")
    print(f"Files with at least one matching group: {files_with_q}")
    print(f"Total matching question groups: {total_groups}")
    print(f"Total matching questions: {total_q}")
    print(f"Errors: {len(errs)}")
    for r in errs:
        print(' ERR', r['file'], r['error'])
    by_subtype = {}
    for r in results:
        if 'error' in r:
            continue
        for g in r.get('questions', []):
            by_subtype[g['subtype']] = by_subtype.get(g['subtype'], 0) + len(g['qnums'])
    print('By subtype:', by_subtype)
