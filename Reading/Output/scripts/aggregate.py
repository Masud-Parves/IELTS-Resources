import json, re, sys

def norm(s):
    s = s.lower()
    s = re.sub(r'[^a-z0-9\s]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def load(path):
    return json.load(open(path, encoding='utf-8'))

def build_logical_passages(data):
    """Returns list of logical passage dicts:
    {title, paragraphs, level, groups: [...], sources: [...], dup_of: None}
    Deduplicates across files by normalized title + first 200 chars of normalized text.
    """
    logical = {}  # dedup_key -> passage record
    order = []

    for r in data:
        if 'error' in r or not r.get('questions'):
            continue
        passages = r.get('passages', [])
        pass_by_num = {p['passage_num']: p for p in passages}
        # default pnum for single-passage files
        single_pnum = None
        if len(passages) == 1:
            only = passages[0]
            single_pnum = only['passage_num']
            if only.get('pnum_source') == 'fallback' and r.get('questions'):
                qnums = [q['qnum'] for q in r['questions']]
                min_q = min(qnums)
                inferred = 1 if min_q <= 13 else 2 if min_q <= 26 else 3
                if inferred != single_pnum:
                    pass_by_num[inferred] = pass_by_num.pop(only['passage_num'])
                    pass_by_num[inferred]['passage_num'] = inferred
                    single_pnum = inferred

        # group questions by (passage_num_resolved)
        qs_by_pnum = {}
        for q in r['questions']:
            pnum = q['passage_num']
            if pnum is None or pnum not in pass_by_num:
                if single_pnum is not None:
                    pnum = single_pnum
                else:
                    pnum = None
            qs_by_pnum.setdefault(pnum, []).append(q)

        for pnum, qs in qs_by_pnum.items():
            if pnum is None or pnum not in pass_by_num:
                continue  # unresolved ambiguity - excluded, reported separately
            passage = pass_by_num[pnum]
            title = passage['title']
            full_text = ' '.join(passage['paragraphs'])
            key = norm(title) + '|' + norm(full_text)[:200]

            qs_sorted = sorted(qs, key=lambda x: x['qnum'])
            # group into contiguous (subtype, instruction) runs
            groups = []
            cur = None
            for q in qs_sorted:
                gkey = (q['subtype'], q['instruction'])
                if cur and cur['key'] == gkey and q['qnum'] == cur['max'] + 1:
                    cur['max'] = q['qnum']
                    cur['items'].append(q)
                else:
                    if cur:
                        groups.append(cur)
                    cur = {'key': gkey, 'min': q['qnum'], 'max': q['qnum'], 'items': [q]}
            if cur:
                groups.append(cur)

            answers = r.get('answers', {})
            group_records = []
            for g in groups:
                subtype, instr = g['key']
                items = []
                for q in g['items']:
                    ans = answers.get(str(q['qnum']))
                    items.append({
                        'orig_qnum': q['qnum'],
                        'prompt': q['prompt'],
                        'answer': ans,
                    })
                qrange_text = f"{g['min']}–{g['max']}" if g['min'] != g['max'] else str(g['min'])
                group_records.append({
                    'subtype': subtype,
                    'instruction': instr,
                    'orig_range': (g['min'], g['max']),
                    'orig_range_text': qrange_text,
                    'items': items,
                })

            if key not in logical:
                logical[key] = {
                    'title': title,
                    'paragraphs': passage['paragraphs'],
                    'level': pnum,
                    'groups': group_records,
                    'sources': [{'file': r['file'], 'orig_level': pnum,
                                 'qranges': [g['orig_range_text'] for g in group_records]}],
                    'all_files': {r['file']},
                }
                order.append(key)
            else:
                existing = logical[key]
                if r['file'] not in existing['all_files']:
                    existing['sources'].append({'file': r['file'], 'orig_level': pnum,
                                                  'qranges': [g['orig_range_text'] for g in group_records]})
                    existing['all_files'].add(r['file'])
                # keep the richer paragraph text if this one is longer
                if sum(len(p) for p in passage['paragraphs']) > sum(len(p) for p in existing['paragraphs']):
                    existing['paragraphs'] = passage['paragraphs']

    result = [logical[k] for k in order]
    return result


if __name__ == '__main__':
    data = load(sys.argv[1])
    passages = build_logical_passages(data)
    out = sys.argv[2] if len(sys.argv) > 2 else 'aggregated.json'
    # drop the set for json serialization
    for p in passages:
        p['n_sources'] = len(p['all_files'])
        del p['all_files']
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(passages, f, indent=2, ensure_ascii=False)

    total_q = sum(len(g['items']) for p in passages for g in p['groups'])
    dup_passages = [p for p in passages if p['n_sources'] > 1]
    missing_ans = sum(1 for p in passages for g in p['groups'] for it in g['items'] if it['answer'] is None)
    print(f"Unique passages: {len(passages)}")
    print(f"Total question groups: {sum(len(p['groups']) for p in passages)}")
    print(f"Total questions: {total_q}")
    print(f"Passages found in >1 source file (duplicates): {len(dup_passages)}")
    for p in dup_passages:
        print('  DUP:', p['title'], '->', [s['file'] for s in p['sources']])
    print(f"Questions missing an answer: {missing_ans}")
    by_level = {}
    for p in passages:
        by_level.setdefault(p['level'], 0)
        by_level[p['level']] += 1
    print('Passages by level:', by_level)
