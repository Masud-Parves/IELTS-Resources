import json, re, sys


def norm(s):
    s = s.lower()
    s = re.sub(r'[^a-z0-9\s]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def build_logical_passages(data):
    logical = {}
    order = []
    unresolved = []

    for r in data:
        if 'error' in r or not r.get('questions'):
            continue
        passages = r.get('passages', [])
        pass_by_num = {p['passage_num']: p for p in passages}
        single_pnum = None
        if len(passages) == 1:
            only = passages[0]
            single_pnum = only['passage_num']
            if only.get('pnum_source') == 'fallback':
                qnums_in_file = [q for g in r['questions'] for q in g['qnums']]
                if qnums_in_file:
                    min_q = min(qnums_in_file)
                    inferred = 1 if min_q <= 13 else 2 if min_q <= 26 else 3
                    if inferred != single_pnum:
                        pass_by_num[inferred] = pass_by_num.pop(only['passage_num'])
                        pass_by_num[inferred]['passage_num'] = inferred
                        single_pnum = inferred

        answers = r.get('answers', {})
        # batch this file's own groups by logical passage key first, so a
        # duplicate-file decision ("skip - already have this passage from
        # another file") is made once per (file, passage), not once per
        # group - a single file legitimately contributing several *different*
        # question groups to the *same* passage must keep all of them.
        per_key = {}
        for g in r['questions']:
            pnum = g['passage_num']
            if pnum is None or pnum not in pass_by_num:
                if single_pnum is not None:
                    pnum = single_pnum
                else:
                    unresolved.append({'file': r['file'], 'qnums': g['qnums'],
                                        'subtype': g['subtype'],
                                        'candidate_passages': [p['title'] for p in passages]})
                    continue
            passage = pass_by_num[pnum]
            title = passage['title']
            full_text = ' '.join(passage['paragraphs'])
            key = norm(title) + '|' + norm(full_text)[:200]

            items = []
            for it in g['items']:
                q = it['qnum']
                v = answers.get(q) if q in answers else answers.get(str(q))
                items.append({'qnum': q, 'statement': it.get('statement'), 'answer': v})

            group_record = {
                'subtype': g['subtype'],
                'instruction': g['instruction'],
                'bank_title': g.get('bank_title'),
                'bank': g.get('bank'),
                'codes': g.get('codes'),
                'code_scheme': g.get('code_scheme'),
                'blocks': g.get('blocks'),
                'qnums': g['qnums'],
                'min': g['min'], 'max': g['max'],
                'items': items,
                'source_file': r['file'],
            }
            per_key.setdefault(key, {'passage': passage, 'pnum': pnum, 'groups': []})
            per_key[key]['groups'].append((group_record, g))

        for key, bundle in per_key.items():
            passage = bundle['passage']
            pnum = bundle['pnum']
            file_groups = bundle['groups']
            qrange_label = f"{min(g['min'] for _, g in file_groups)}-{max(g['max'] for _, g in file_groups)}"
            if key not in logical:
                logical[key] = {
                    'title': passage['title'],
                    'paragraphs': passage['paragraphs'],
                    'level': pnum,
                    'groups': [gr for gr, _ in file_groups],
                    'sources': [{'file': r['file'], 'orig_level': pnum, 'qrange': qrange_label}],
                    'all_files': {r['file']},
                }
                order.append(key)
            else:
                # a second (or further) file mapping to an already-seen
                # passage key is a confirmed duplicate of the same passage:
                # keep only the first-seen file's groups, and just record
                # this file as an additional source for the report/answer
                # sheet, so the sheet never asks the same questions twice.
                existing = logical[key]
                if r['file'] not in existing['all_files']:
                    existing['sources'].append({'file': r['file'], 'orig_level': pnum, 'qrange': qrange_label})
                    existing['all_files'].add(r['file'])

    result = [logical[k] for k in order]
    return result, unresolved


if __name__ == '__main__':
    data = json.load(open(sys.argv[1], encoding='utf-8'))
    passages, unresolved = build_logical_passages(data)
    out = sys.argv[2] if len(sys.argv) > 2 else 'aggregated_matching.json'
    for p in passages:
        p['n_sources'] = len(p['all_files'])
        del p['all_files']
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(passages, f, indent=2, ensure_ascii=False)

    total_q = sum(len(g['qnums']) for p in passages for g in p['groups'])
    total_groups = sum(len(p['groups']) for p in passages)
    dup_passages = [p for p in passages if p['n_sources'] > 1]
    missing_ans = sum(1 for p in passages for g in p['groups'] for it in g['items'] if it['answer'] is None)
    print(f"Unique passages: {len(passages)}")
    print(f"Total question groups: {total_groups}")
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
    by_subtype = {}
    for p in passages:
        for g in p['groups']:
            by_subtype[g['subtype']] = by_subtype.get(g['subtype'], 0) + len(g['qnums'])
    print('Questions by sub-type:', by_subtype)
    print(f"Unresolved (excluded, ambiguous passage pairing): {len(unresolved)}")
    for u in unresolved:
        print('  UNRESOLVED:', u['file'], u['qnums'], u['subtype'], '-> candidates:', u['candidate_passages'])
