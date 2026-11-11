import os, re, json, sys
from bs4 import BeautifulSoup

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # the Reading/ folder
FOLDERS = {"Passage 1": "P1", "Passage 2": "P2", "Passage 3": "P3"}

TFNG_SET = frozenset({"TRUE", "FALSE", "NOT GIVEN"})
YNNG_SET = frozenset({"YES", "NO", "NOT GIVEN"})

def find_answer_maps(html):
    """Find all JS object literals assigned to a variable whose first key is 1 (or '1').
    Returns list of (varname, {qnum:int -> answer str/list})."""
    maps = []
    for m in re.finditer(r'(?:const|let|var)\s+(\w+)\s*=\s*\{', html):
        varname = m.group(1)
        start = m.end() - 1  # position of '{'
        depth = 0
        i = start
        in_str = None
        while i < len(html):
            c = html[i]
            if in_str:
                if c == '\\':
                    i += 2
                    continue
                if c == in_str:
                    in_str = None
                i += 1
                continue
            if c in ('"', "'"):
                in_str = c
            elif c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    break
            i += 1
        obj_text = html[start:i+1]
        # quick check it looks like a qnum map: has at least one integer key : value pair
        if not re.search(r"['\"]?\d+['\"]?\s*:\s*[\[\{'\"]", obj_text):
            continue
        cleaned = re.sub(r'//[^\n]*', '', obj_text)
        entries = parse_object_entries(cleaned)
        if entries:
            maps.append((varname, entries))
    return maps


def _find_balanced_end(text, start, open_ch, close_ch):
    depth = 0
    i = start
    in_str = None
    n = len(text)
    while i < n:
        c = text[i]
        if in_str:
            if c == '\\':
                i += 2
                continue
            if c == in_str:
                in_str = None
            i += 1
            continue
        if c in ('"', "'"):
            in_str = c
        elif c == open_ch:
            depth += 1
        elif c == close_ch:
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return n


def parse_object_entries(obj_text):
    """Parse a JS object literal text (already brace-matched, possibly with // comments
    stripped) into {int_key: value}. Supports string values, arrays of strings, and
    nested objects (pulling a 'correct' or 'answer' field from the nested object)."""
    entries = {}
    n = len(obj_text)
    i = 1  # skip opening '{'
    key_re = re.compile(r'''\s*['"]?[A-Za-z_]*(\d+)['"]?\s*:\s*''')
    while i < n:
        while i < n and obj_text[i] in ' \t\r\n,':
            i += 1
        if i >= n or obj_text[i] == '}':
            break
        m = key_re.match(obj_text, i)
        if not m:
            # unparsable key (e.g. a non-numeric field) - skip to the next
            # top-level comma or closing brace and keep going
            j = i
            depth = 0
            in_str = None
            while j < n:
                c = obj_text[j]
                if in_str:
                    if c == '\\':
                        j += 2
                        continue
                    if c == in_str:
                        in_str = None
                    j += 1
                    continue
                if c in ('"', "'"):
                    in_str = c
                elif c in '{[':
                    depth += 1
                elif c in '}]':
                    if depth == 0:
                        break
                    depth -= 1
                elif c == ',' and depth == 0:
                    break
                j += 1
            i = j
            continue
        key = int(m.group(1))
        i = m.end()
        if i >= n:
            break
        c = obj_text[i]
        if c == '{':
            j = _find_balanced_end(obj_text, i, '{', '}')
            value_text = obj_text[i:j]
            vm = re.search(
                r'''['"]?(?:correct|answer)['"]?\s*:\s*(\[[^\]]*\]|'(?:[^'\\]|\\.)*'|"(?:[^"\\]|\\.)*")''',
                value_text)
            if vm:
                raw = vm.group(1)
                if raw.startswith('['):
                    vals = re.findall(r''''((?:[^'\\]|\\.)*)'|"((?:[^"\\]|\\.)*)"''', raw)
                    entries[key] = [a or b for a, b in vals]
                else:
                    entries[key] = raw[1:-1]
            i = j
        elif c == '[':
            j = _find_balanced_end(obj_text, i, '[', ']')
            raw = obj_text[i:j]
            vals = re.findall(r''''((?:[^'\\]|\\.)*)'|"((?:[^"\\]|\\.)*)"''', raw)
            entries[key] = [a or b for a, b in vals]
            i = j
        elif c in ('"', "'"):
            q = c
            j = i + 1
            while j < n:
                if obj_text[j] == '\\':
                    j += 2
                    continue
                if obj_text[j] == q:
                    j += 1
                    break
                j += 1
            entries[key] = obj_text[i+1:j-1]
            i = j
        else:
            j = i
            while j < n and obj_text[j] not in ',}':
                j += 1
            i = j
    return entries

def _value_matches_option_set(v, option_set):
    vals = v if isinstance(v, list) else [v]
    return any(isinstance(x, str) and x.strip().upper() in option_set for x in vals)


def pick_best_answer_map(maps, needed_qnum_to_options):
    """needed_qnum_to_options: {qnum: frozenset of valid option strings (e.g. TFNG_SET)}.
    Scores each candidate object by how many needed questions it gives a value that is
    actually a valid option for that question's subtype (TRUE/FALSE/NOT GIVEN or
    YES/NO/NOT GIVEN) - this rejects decoy objects (e.g. ARIA-label lookups) that
    happen to have the right numeric keys but nonsense values."""
    best = None
    best_score = -1
    for varname, entries in maps:
        score = 0
        for q, option_set in needed_qnum_to_options.items():
            v = entries.get(q)
            if v is not None and _value_matches_option_set(v, option_set):
                score += 1
        if score > best_score:
            best_score = score
            best = (varname, entries)
    return best if best_score > 0 else None

NUM_PREFIX_RE = re.compile(r'^\s*(?:Q(?:uestion)?\s*)?\d{1,3}[\.\)]?\s*')
CHROME_PREFIX_RE = re.compile(r'^\s*(?:Review\s*)+', re.IGNORECASE)

def _strip_option_tokens(t, option_values, at_end):
    opts_sorted = sorted(option_values, key=len, reverse=True)
    changed = True
    guard = 0
    while changed and guard < 20:
        changed = False
        guard += 1
        for ov in opts_sorted:
            pat_str = re.escape(ov) + r'\s*$' if at_end else r'^\s*' + re.escape(ov)
            pat = re.compile(pat_str, re.IGNORECASE)
            new_t = pat.sub('', t).strip()
            if new_t != t:
                t = new_t
                changed = True
    return t


def clean_prompt(text, option_values):
    t = text.strip()
    # some templates render the option labels (TRUE/FALSE/NOT GIVEN) before the
    # numbered statement in the DOM; strip those first
    t = _strip_option_tokens(t, option_values, at_end=False)
    t = CHROME_PREFIX_RE.sub('', t)
    t = NUM_PREFIX_RE.sub('', t, count=1)
    # other templates render the option labels after the statement instead
    t = _strip_option_tokens(t, option_values, at_end=True)
    return t.strip()

BOILERPLATE_OPTION_LINE_RE = re.compile(
    r'^(TRUE|FALSE|NOT\s+GIVEN|YES|NO|if|or)\b', re.I)


def find_instruction_block(radio_tag, subtype_marker_regex):
    """Walk backwards through the document to find the nearest text block containing
    the TFNG/YNNG rubric phrase (skipping the short per-option boilerplate lines like
    'TRUE if the statement agrees with the information'), and also look for a
    'Questions X-Y' header near it."""
    count = 0
    for prev in radio_tag.find_all_previous(string=True):
        count += 1
        if count > 4000:
            break
        s = str(prev)
        if subtype_marker_regex.search(s):
            parent = prev.parent
            block_text = parent.get_text(" ", strip=True)
            if len(block_text) < 40 and parent.parent:
                block_text = parent.parent.get_text(" ", strip=True)
            if not block_text:
                # rare parser-tree quirk where the matched text node's parent
                # reports no text via get_text(); fall back to the raw matched
                # string itself, which is still verbatim source text
                block_text = s.strip()
            if BOILERPLATE_OPTION_LINE_RE.match(block_text) and len(block_text) < 70:
                continue
            return block_text
    return None

def find_questions_range_header(radio_tag):
    for prev in radio_tag.find_all_previous(string=re.compile(r'Questions?\s*\d+\s*[\u2013\-]\s*\d+', re.I)):
        m = re.search(r'Questions?\s*(\d+)\s*[\u2013\-]\s*(\d+)', str(prev), re.I)
        if m:
            return int(m.group(1)), int(m.group(2))
    return None

def extract_passage_number_from_instruction(instr_text):
    if not instr_text:
        return None
    m = re.search(r'Reading Passage\s*(\d+)', instr_text, re.I)
    if m:
        return int(m.group(1))
    return None


PART_ID_RE = re.compile(r'(?:pc|qs-?part|qs|passage-?text|questions|part|passage)-?0*(\d+)', re.I)


def find_part_number_from_ancestors(node, max_levels=12):
    cur = node
    for _ in range(max_levels):
        if cur is None:
            break
        if cur.has_attr('data-part'):
            dm = re.search(r'\d+', cur['data-part'])
            if dm:
                return int(dm.group())
        if cur.has_attr('id'):
            im = PART_ID_RE.search(cur['id'])
            if im:
                return int(im.group(1))
        if cur.has_attr('class'):
            cm = PART_ID_RE.search(' '.join(cur['class']))
            if cm:
                return int(cm.group(1))
        cur = cur.parent
    return None

EXCLUDE_DESC_CLASS_RE = re.compile(r'analysis|explain|answer-?key|review-flag', re.I)


def container_text_excluding(container, exclude_class_re=EXCLUDE_DESC_CLASS_RE):
    """Like container.get_text(' ', strip=True), but skips text inside any
    descendant element whose class matches exclude_class_re (e.g. a hidden
    per-question 'analysis'/explanation block that reveals the answer)."""
    parts = []
    for desc in container.descendants:
        if not isinstance(desc, str):
            continue
        skip = False
        anc = desc.parent
        while anc is not None:
            if anc.has_attr('class') and exclude_class_re.search(' '.join(anc['class'])):
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


def find_item_container(radio_tag):
    """Find the smallest ancestor div/section that contains readable prompt text
    beyond just the option labels (ignoring hidden analysis/explanation blocks)."""
    node = radio_tag
    for _ in range(8):
        node = node.parent
        if node is None:
            break
        text = container_text_excluding(node)
        if len(text) > 25:
            return node
    return radio_tag.parent

CHROME_TITLE_RE = re.compile(
    r'^\s*(reading passage\s*\d+|questions?\b.*|answer key|part\s*\d+|passage\s*\d+)\s*$', re.I)
STOP_CLASS_RE = re.compile(
    r'question|qsec|qitem|qblock|right-pane|questions-panel|questions-container|'
    r'questions-part|answer|rgroup|notes-completion|mh-list|summary-card', re.I)
ID_NUM_RE = re.compile(r'(?:pc|part|passage)-?0*(\d+)', re.I)


def passage_number_for(heading_el, html_before_text):
    # (a) explicit 'Reading Passage N' within ~400 chars before the heading in raw text
    m = None
    for mm in re.finditer(r'Reading Passage\s*(\d+)', html_before_text[-600:], re.I):
        m = mm
    if m:
        return int(m.group(1))
    # (b)/(c) data-part or id-based number on self/ancestors
    return find_part_number_from_ancestors(heading_el, max_levels=6)


TITLE_CLASS_RE = re.compile(r'passage-?title|^ptitle$', re.I)


def is_title_el(el):
    if el.name in ('h1', 'h2', 'h3', 'h4'):
        return True
    if el.name in ('div', 'p', 'span') and el.has_attr('class'):
        return bool(TITLE_CLASS_RE.search(' '.join(el['class'])))
    return False


def extract_passages(soup, full_html):
    """Heading-driven passage detection: scan all h1-h4 headings (and div/p/span
    elements with a passage-title-like class) in document order, treat ones that
    are not UI chrome as passage titles, collect following <p> siblings/descendants
    until hitting question-related content or the next heading."""
    headings = soup.find_all(is_title_el)
    accepted = []
    for h in headings:
        title = h.get_text(' ', strip=True)
        if not title or len(title) < 3 or len(title) > 150:
            continue
        if CHROME_TITLE_RE.match(title):
            continue
        following = list(h.find_all_next())
        paras = []
        count = 0
        for el in following:
            count += 1
            if count > 500:
                break
            if is_title_el(el):
                break
            cls = ' '.join(el.get('class', [])) if el.has_attr('class') else ''
            elid = el.get('id', '') if el.has_attr('id') else ''
            if STOP_CLASS_RE.search(cls) or STOP_CLASS_RE.search(elid):
                break
            if el.name == 'p':
                t = el.get_text(' ', strip=True)
                if len(t) > 15 and not CHROME_TITLE_RE.match(t):
                    paras.append(t)
        total_len = sum(len(p) for p in paras)
        if len(paras) >= 2 and total_len > 300:
            h_pos = full_html.find(title)
            if h_pos > 0:
                raw_slice = full_html[max(0, h_pos - 1000):h_pos]
                before_text = re.sub(r'<[^>]+>', ' ', raw_slice)
            else:
                before_text = ''
            pnum = passage_number_for(h, before_text)
            accepted.append({'title': title, 'paragraphs': paras, 'pnum': pnum, 'heading': h})

    # assign fallback sequential numbers where pnum is None (no real signal found)
    results = {}
    next_fallback = 1
    used_nums = set(a['pnum'] for a in accepted if a['pnum'])
    for a in accepted:
        pnum = a['pnum']
        pnum_source = 'signal'
        if pnum is None:
            while next_fallback in used_nums:
                next_fallback += 1
            pnum = next_fallback
            used_nums.add(pnum)
            pnum_source = 'fallback'
        total_len = sum(len(p) for p in a['paragraphs'])
        if pnum not in results or total_len > results[pnum]['_len']:
            results[pnum] = {'passage_num': pnum, 'title': a['title'],
                              'paragraphs': a['paragraphs'], '_len': total_len,
                              'pnum_source': pnum_source}
    for v in results.values():
        v.pop('_len', None)
    return list(results.values())


def extract_file(path):
    with open(path, encoding='utf-8', errors='replace') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'lxml')
    radios = soup.find_all('input', attrs={'type': 'radio'})
    groups = {}  # name -> list of (value, tag)
    for r in radios:
        name = r.get('name')
        val = (r.get('value') or '').strip().upper()
        if not name or val not in TFNG_SET and val not in YNNG_SET:
            continue
        groups.setdefault(name, []).append((val, r))

    questions = []  # list of dicts
    for name, pairs in groups.items():
        values = set(v for v, t in pairs)
        if values == TFNG_SET:
            subtype = 'TFNG'
        elif values == YNNG_SET:
            subtype = 'YNNG'
        else:
            continue
        qnum_m = re.search(r'(\d+)', name)
        if not qnum_m:
            continue
        qnum = int(qnum_m.group(1))
        first_radio = pairs[0][1]
        container = find_item_container(first_radio)
        opt_values = TFNG_SET if subtype == 'TFNG' else YNNG_SET
        raw_text = container_text_excluding(container)
        prompt = clean_prompt(raw_text, opt_values)
        marker_re = re.compile(
            r'agrees?\s+with\s+the\s+(information|views|claims)'
            r'|TRUE\s*/\s*FALSE\s*/\s*NOT\s*GIVEN|YES\s*/\s*NO\s*/\s*NOT\s*GIVEN',
            re.I)
        instr = find_instruction_block(first_radio, marker_re)
        qrange = find_questions_range_header(first_radio)
        pnum = extract_passage_number_from_instruction(instr)
        if pnum is None:
            pnum = find_part_number_from_ancestors(first_radio)
        questions.append({
            'qnum': qnum, 'subtype': subtype, 'prompt': prompt,
            'instruction': instr, 'qrange': qrange, 'passage_num': pnum,
        })

    passages = extract_passages(soup, html)
    answer_maps = find_answer_maps(html)
    needed = {q['qnum']: (TFNG_SET if q['subtype'] == 'TFNG' else YNNG_SET) for q in questions}
    best_map = pick_best_answer_map(answer_maps, needed) if answer_maps else None
    answers = {}
    if best_map:
        varname, entries = best_map
        for q in questions:
            v = entries.get(q['qnum'])
            option_set = TFNG_SET if q['subtype'] == 'TFNG' else YNNG_SET
            if v is not None and _value_matches_option_set(v, option_set):
                if isinstance(v, list):
                    v = ' / '.join(v)
                answers[q['qnum']] = v

    return {
        'file': path,
        'questions': questions,
        'passages': passages,
        'answers': answers,
        'n_radio_groups': len(groups),
        'answer_map_var': best_map[0] if best_map else None,
    }


if __name__ == '__main__':
    import sys
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
                res = {'file': path, 'error': str(e), 'folder_level': code}
            results.append(res)

    out_path = sys.argv[1] if len(sys.argv) > 1 else "extract_out.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    total_q = sum(len(r.get('questions', [])) for r in results)
    total_tfng_files = sum(1 for r in results if r.get('questions'))
    print(f"Files processed: {len(results)}")
    print(f"Files with at least one TFNG/YNNG question: {total_tfng_files}")
    print(f"Total TFNG/YNNG questions found: {total_q}")
    errs = [r for r in results if 'error' in r]
    print(f"Errors: {len(errs)}")
    for r in errs:
        print(' ERR', r['file'], r['error'])
