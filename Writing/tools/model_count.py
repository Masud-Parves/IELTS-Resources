"""Word-count and reuse checker for model-answer essays.

Usage:
  python tools/model_count.py source/model_answers/NN_Topic/essays_*.txt
  python tools/model_count.py --source source/02_Technology.md source/model_answers/02_Technology/essays_*.txt
  python tools/model_count.py --source source/06_Work.md,source/01_Education.md source/model_answers/06_Work/essays_*.txt

Limits: total 260-280; Intro >=30; BP1 >=100; BP2 >=100; Conclusion >=30.
Essays with "format: advdis" follow IELTS_Advantages_Disadvantages_Essay_Guide.md instead:
the guide's exact limits (Types 2/3: total 330-360, Intro 40-50, Conclusion 35-45;
Type 1: total 310-340, Intro 30-40, Conclusion 25-35, no opinion or plan sentence;
each body 120-135), plus the fixed
7-sentence body pattern ({T}{P}{E}{X}{P}{E}{S}), linker chain, Although-intro, While-conclusion and
the opinion sentences for the type (add "side: disadvantages" when that side is supported).
Essays with "format: agree" follow IELTS_Agree_Disagree_Essay_Guide.md: 2-sentence intro (35-50) and
conclusion (35-55), each body 100-120, total 270-345, BP1 {P}{E}{E}{X}{L}, BP2 {P}{E}{X}{R}{L} (one extra {E}
allowed in each), the guide's fixed openers, and no partial-position phrases.
Essays with "format: discuss" follow IELTS_Discuss_Both_Views_Essay_Guide.md: intro (35-45) ending
"I completely support the latter view because", each body 90-120, conclusion (35-45), total 260-299,
BP1 {P}{E}{E}{X}{L} with no "I", BP2 {P}{E}{X}{R}{L}, the guide's fixed openers, no partial-position phrases.
Essays with "format: causesol" follow IELTS_Cause_Problem_Solution_Essay_Guide.md: 2-sentence intro (30-40) and
conclusion (30-40), each body 90-120, total 260-300, BP1 {P}{E}{X}{P}{E}{L}, BP2 {N}{E}{X}{N}{E}{L} (N = Solution),
no opinion and no plan sentence. Add "shape: solutions", "shape: groups" or "shape: problems" for the guide's
Section 14 relatives: one idea in each body, both tagged P E E X L ({N} for a solution), no ", but" needed.
Essays with "format: double" follow IELTS_Double_Question_Essay_Guide.md and name their blocks in "pattern:"
("List + Opinion", "Opinion + List" or "List + List"): 2-sentence intro (30-40) and conclusion (30-40),
each body 90-120, total 260-300; List block P E X P E L (no "I"), Opinion block P E X R L with
"I firmly believe that" ("As for whether …" in BP2) and "Therefore,"; For example in BP1, For instance in BP2.
With --source, every [[reused sentence]] is compared with the Idea Bank chapter and
flagged if it does not closely match any sentence there (similarity < 0.75).
"""
import re, sys, difflib

TAGS = 'PEXLRTSN'

def clean(s):
    return re.sub(r'\{[%s]\}' % TAGS, '', s).replace('**', '').replace('[[', '').replace(']]', '')

def wc(s):
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’-]*", clean(s)))

def parse(files):
    out = []
    for f in files:
        for blk in open(f, encoding='utf-8').read().split('@@ ')[1:]:
            lines = blk.strip().split('\n'); d = {'code': lines[0].strip()}
            for ln in lines[1:]:
                if ':' in ln:
                    k, v = ln.split(':', 1); d[k.strip()] = v.strip()
            out.append(d)
    return out

def reused(d):
    return [m for k in ('I', 'B1', 'B2', 'C') for m in re.findall(r'\[\[(.*?)\]\]', d.get(k, ''))]

def source_sentences(path):
    t = open(path, encoding='utf-8').read().replace('**', '')
    t = re.sub(r'<[^>]+>', ' ', t)
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+|\n+', t) if len(s.split()) >= 5]

def best_ratio(s, pool):
    s = s.lower()
    return max(difflib.SequenceMatcher(None, s, p.lower()).ratio() for p in pool)

# Fixed openers from the Advantages & Disadvantages guide (Sections 4 and 4C)
BP1_CHAIN = ['There is little doubt that', 'To begin with', 'This is because', 'For example',
             'In addition', 'As a result', 'Overall']
BP2_CHAIN = ['On the other hand, it cannot be denied that', 'Firstly', None, 'For instance',
             'Secondly', 'If', None]

# Guide Sections 3c, 4B and 6c: the opinion sentences and the BP2 summary depend on the type
# and on the side supported ("side: disadvantages" in the essay block; advantages by default).
# The emphasis rule (supported side after the comma in Although/While) is checked by eye.
def type_rules(d):
    typ = d.get('type', '')
    kind = '1' if 'Type 1' in typ else '3' if 'Type 3' in typ else '2'
    dis = d.get('side') == 'disadvantages'
    bp2_s6 = 'Overall' if kind == '1' else 'Although some' if dis else 'Although these'
    # Type 1 has no sentence c: the intro ends on Although, the conclusion on While
    intro_c = {'1': None, '2': 'In my opinion', '3': 'In my view'}[kind]
    concl_c = {'1': None, '2': 'Therefore, I', '3': 'Overall, I believe'}[kind]
    return bp2_s6, intro_c, concl_c

# (total, intro, conclusion) word ranges from the guide, Section 2
LIMITS = {True: ((310, 340), (30, 40), (25, 35)), False: ((330, 360), (40, 50), (35, 45))}

def tagged(text):
    parts = re.split(r'\{([%s])\}' % TAGS, text)[1:]
    return [(parts[i], clean(parts[i + 1]).strip()) for i in range(0, len(parts), 2)]

def advdis_problems(d):
    probs = []
    bp2_s6, intro_c, concl_c = type_rules(d)
    for key, chain in (('B1', BP1_CHAIN), ('B2', BP2_CHAIN[:6] + [bp2_s6])):
        sents = tagged(d[key])
        if ''.join(t for t, _ in sents) != 'TPEXPES':
            probs.append(f'{key} tags {"".join(t for t, _ in sents)} (want TPEXPES)')
            continue
        for i, (start, (_, s)) in enumerate(zip(chain, sents)):
            starts = start if isinstance(start, tuple) else (start,)
            if start and not s.startswith(starts):
                probs.append(f'{key} S{i} should start "{starts[0]}"')
        if key == 'B2':
            if 'as a result' not in sents[2][1]:
                probs.append('B2 S2 needs "as a result"')
            if 'consequently' not in sents[5][1]:
                probs.append('B2 S5 needs "consequently"')
    for key, word, last in (('I', 'Although', intro_c), ('C', 'While', concl_c)):
        sents = re.split(r'(?<=[.!?])\s+', clean(d[key]).strip())
        want = 3 if last else 2
        if len(sents) != want:
            probs.append(f'{key} has {len(sents)} sentences (want {want})')
            continue
        if not sents[1].startswith(word):
            probs.append(f'{key} sentence 2 should start "{word}"')
        elif ', but ' in sents[1]:
            probs.append(f'{key} sentence 2 uses "but" after "{word}"')
        if last and not sents[2].startswith(last):
            probs.append(f'{key} sentence 3 should start "{last}"')
        if 'this essay will' in sents[-1].lower():
            probs.append(f'{key} has a plan sentence ("This essay will …")')
    if not clean(d['C']).startswith('In conclusion'):
        probs.append('C should start "In conclusion"')
    return probs

# Fixed openers from the Agree / Disagree guide (Sections 1 and 6)
BANNED = ['partly', 'partially', 'largely', 'to some extent', 'to a large extent', 'to a certain extent',
          'it depends', 'on the other hand', 'this essay will', 'both sides', 'up to a point']

def sentences(text):
    return re.split(r'(?<=[.!?])\s+', clean(text).strip())

def agree_problems(d):
    probs = []
    intro, concl = sentences(d['I']), sentences(d['C'])
    m = re.search(r'I completely (agree|disagree) with this view because ', clean(d['I']))
    if not m:
        return ['I needs "I completely agree/disagree with this view because"']
    side = m.group(1)
    noun = {'agree': 'agreement', 'disagree': 'disagreement'}[side]
    if len(intro) != 2 or not intro[1].startswith('I completely'):
        probs.append(f'I has {len(intro)} sentences (want 2, the second being the opinion)')
    if len(concl) != 2:
        probs.append(f'C has {len(concl)} sentences (want 2)')
    if not concl[0].startswith('In conclusion, I firmly believe that'):
        probs.append('C should start "In conclusion, I firmly believe that"')
    whole = clean(' '.join(d[k] for k in ('I', 'B1', 'B2', 'C'))).lower()
    for phrase in BANNED:
        if phrase in whole:
            probs.append(f'banned phrase "{phrase}"')
    starts = {'B1': {'P': f'The main reason why I {side} with this idea is that', 'X': 'For example,', 'L': 'Therefore,'},
              'B2': {'P': f'Another important reason for my {noun} is that', 'E': 'When ', 'X': 'For instance,',
                     'R': 'Although some people argue that', 'L': 'Consequently,'}}
    wanted = {'B1': ('PEEXL', 'PEEEXL'), 'B2': ('PEXRL', 'PEEXRL')}
    for key in ('B1', 'B2'):
        sents = tagged(d[key])
        tags = ''.join(t for t, _ in sents)
        if tags not in wanted[key]:
            probs.append(f'{key} tags {tags} (want {wanted[key][0]})')
            continue
        seen = set()
        for tag, s in sents:
            start = starts[key].get(tag)
            if start and tag not in seen and not s.startswith(start):
                probs.append(f'{key} {tag} should start "{start}"')
            seen.add(tag)
            if tag == 'X' and wc(s) < 15:
                probs.append(f'{key} example is too short ({wc(s)} words)')
            if tag == 'R' and ', but ' in s:
                probs.append('R uses "but" after "Although"')
        if key == 'B1':
            es = [s for t, s in sents if t == 'E']
            if not es[0].startswith('This is because'):
                probs.append('B1 first E should start "This is because"')
            if '; as a result,' not in es[-1]:
                probs.append('B1 last E needs "; as a result,"')
    return probs

# Fixed openers from the Discuss Both Views guide (Sections 1, 6, 7, 8 and 10)
DISCUSS_BANNED = ['partly', 'partially', 'to some extent', 'it depends', 'this essay will', 'both views',
                  'both sides', 'both are', 'balanced approach', 'combine both', 'work together']

def discuss_problems(d):
    probs = []
    intro, concl = sentences(d['I']), sentences(d['C'])
    if len(intro) not in (2, 3):
        probs.append(f'I has {len(intro)} sentences (want 2, or 3 with a general statement)')
    if not intro[-1].startswith('I completely support the latter view because'):
        probs.append('I should end "I completely support the latter view because"')
    if len(intro) < 2 or not intro[-2].startswith('While '):
        probs.append('I paraphrase should start "While"')
    if len(concl) != 2:
        probs.append(f'C has {len(concl)} sentences (want 2)')
    else:
        if not concl[0].startswith('In conclusion, people hold different views on whether'):
            probs.append('C should start "In conclusion, people hold different views on whether"')
        if not concl[1].startswith('While ') or 'I firmly believe that' not in concl[1]:
            probs.append('C sentence 2 should be "While …, I firmly believe that …"')
    whole = clean(' '.join(d[k] for k in ('I', 'B1', 'B2', 'C'))).lower()
    for phrase in DISCUSS_BANNED:
        if phrase in whole:
            probs.append(f'banned phrase "{phrase}"')
    starts = {'B1': {'P': 'On the one hand,', 'X': 'For example,', 'L': 'For this reason,'},
              'B2': {'P': 'On the other hand, I firmly believe that', 'X': 'For instance,',
                     'R': 'Although some people argue that', 'L': 'Consequently,'}}
    wanted = {'B1': 'PEEXL', 'B2': 'PEXRL'}
    for key in ('B1', 'B2'):
        sents = tagged(d[key])
        tags = ''.join(t for t, _ in sents)
        if tags != wanted[key]:
            probs.append(f'{key} tags {tags} (want {wanted[key]})')
            continue
        for tag, s in sents:
            start = starts[key].get(tag)
            if start and not s.startswith(start):
                probs.append(f'{key} {tag} should start "{start}"')
            if tag == 'X' and wc(s) < 15:
                probs.append(f'{key} example is too short ({wc(s)} words)')
            if tag == 'R' and ', but ' in s:
                probs.append('R uses "but" after "Although"')
            if wc(s) > 35:
                probs.append(f'{key} {tag} is over 35 words ({wc(s)})')
    if re.search(r"\b(I|my|me)\b", clean(d['B1'])):
        probs.append('B1 should not use "I" or "my"')
    return probs

# Cause/Problem + Solution guide (Sections 5, 7, 8, 9 and 12). Openers may vary if they sound unnatural,
# so only the linkers that carry the structure are checked.
CAUSESOL_BANNED = ['this essay will', 'in my opinion', 'in my view', 'i think', 'i believe']

def causesol_problems(d):
    probs = []
    intro, concl = sentences(d['I']), sentences(d['C'])
    shape = d.get('shape')  # guide Section 14: solutions | groups | problems (one idea in each body)
    if len(intro) != 2:
        probs.append(f'I has {len(intro)} sentences (want 2)')
    elif ', but ' not in intro[1] and not shape:
        probs.append('I sentence 2 needs ", but" before the solutions')
    if len(concl) != 2:
        probs.append(f'C has {len(concl)} sentences (want 2)')
    if not clean(d['C']).startswith('In conclusion'):
        probs.append('C should start "In conclusion"')
    whole = clean(' '.join(d[k] for k in ('I', 'B1', 'B2', 'C')))
    for phrase in CAUSESOL_BANNED:
        if phrase in whole.lower():
            probs.append(f'banned phrase "{phrase}"')
    if re.search(r"\b(I|my|me)\b", whole):
        probs.append('no opinion is asked, so do not use "I" or "my"')
    if shape:
        tag = 'N' if shape in ('solutions', 'groups') else 'P'
        for key, opener in (('B1', 'For example,'), ('B2', 'For instance,')):
            sents = tagged(d[key])
            tags = ''.join(t for t, _ in sents)
            if tags != tag + 'EEXL':
                probs.append(f'{key} tags {tags} (want {tag}EEXL)')
                continue
            x = sents[3][1]
            if not x.startswith(opener):
                probs.append(f'{key} X should start "{opener}"')
            if wc(x) < 15:
                probs.append(f'{key} example is too short ({wc(x)} words)')
            for t, s in sents:
                if wc(s) > 35:
                    probs.append(f'{key} {t} is over 35 words ({wc(s)})')
        return probs
    wanted = {'B1': 'PEXPEL', 'B2': 'NEXNEL'}
    starts = {'B1': ('For example,', 'Consequently,'), 'B2': ('For instance,', 'Together,')}
    for key in ('B1', 'B2'):
        sents = tagged(d[key])
        tags = ''.join(t for t, _ in sents)
        if tags != wanted[key]:
            probs.append(f'{key} tags {tags} (want {wanted[key]})')
            continue
        if not sents[2][1].startswith(starts[key][0]):
            probs.append(f'{key} X should start "{starts[key][0]}"')
        if not sents[5][1].startswith(starts[key][1]):
            probs.append(f'{key} L should start "{starts[key][1]}"')
        if wc(sents[2][1]) < 15:
            probs.append(f'{key} example is too short ({wc(sents[2][1])} words)')
        for tag, s in sents:
            if wc(s) > 35:
                probs.append(f'{key} {tag} is over 35 words ({wc(s)})')
        if key == 'B2' and not sents[3][1].startswith('In addition,'):
            probs.append('B2 second solution should start "In addition,"')
    return probs

# Double Question guide (Sections 1, 4, 6, 7, 8 and 10). "pattern:" names the block for each question,
# e.g. "List + Opinion". A List block naming solutions may tag its points {N}.
DOUBLE_BANNED = ['this essay will', 'partly', 'partially', 'largely', 'to some extent', 'it depends',
                 'both positive and negative', 'in my opinion', 'in my view', 'i think']
LIST_TAGS = ('PEXPEL', 'NEXNEL', 'PEEXL', 'NEEXL')   # P E E X L is the guide's emergency exit
OPINION_TAGS = ('PEXRL', 'PEEXL')

def double_problems(d):
    probs = []
    blocks = [b.strip() for b in d.get('pattern', '').split('+')]
    if len(blocks) != 2 or any(b not in ('List', 'Opinion') for b in blocks):
        return ['pattern should be "List + Opinion", "Opinion + List" or "List + List"']
    intro, concl = sentences(d['I']), sentences(d['C'])
    if len(intro) != 2:
        probs.append(f'I has {len(intro)} sentences (want 2)')
    if len(concl) != 2:
        probs.append(f'C has {len(concl)} sentences (want 2)')
    if not clean(d['C']).startswith('In conclusion,'):
        probs.append('C should start "In conclusion,"')
    whole = clean(' '.join(d[k] for k in ('I', 'B1', 'B2', 'C')))
    for phrase in DOUBLE_BANNED:
        if phrase in whole.lower():
            probs.append(f'banned phrase "{phrase}"')
    has_opinion = 'Opinion' in blocks
    for key in ('I', 'C'):
        said = 'I firmly believe that' in clean(d[key])
        if has_opinion and not said:
            probs.append(f'{key} should give the opinion with "I firmly believe that"')
        if not has_opinion and re.search(r"\b(I|my|me)\b", clean(d[key])):
            probs.append(f'{key}: no opinion is asked, so do not use "I" or "my"')
    for n, (key, block) in enumerate(zip(('B1', 'B2'), blocks)):
        sents = tagged(d[key])
        tags = ''.join(t for t, _ in sents)
        if tags not in (LIST_TAGS if block == 'List' else OPINION_TAGS):
            probs.append(f'{key} tags {tags} (want {"PEXPEL" if block == "List" else "PEXRL"})')
            continue
        x = next(s for t, s in sents if t == 'X')
        opener = 'For example,' if n == 0 else 'For instance,'
        if not x.startswith(opener):
            probs.append(f'{key} X should start "{opener}"')
        if wc(x) < 15:
            probs.append(f'{key} example is too short ({wc(x)} words)')
        for t, s in sents:
            if wc(s) > 35:
                probs.append(f'{key} {t} is over 35 words ({wc(s)})')
        last = sents[-1][1]
        if block == 'List':
            if re.search(r"\b(I|my|me)\b", clean(d[key])):
                probs.append(f'{key} is a List block, so do not use "I" or "my"')
            if not last.startswith(('Consequently,', 'As a result,', 'Together, these measures would')):
                probs.append(f'{key} L should start "Consequently," or "Together, these measures would"')
        else:
            p = sents[0][1]
            if 'I firmly believe that' not in p:
                probs.append(f'{key} P needs "I firmly believe that"')
            elif n == 1 and not p.startswith('As for whether'):
                probs.append('B2 Opinion P should start "As for whether"')
            r = [s for t, s in sents if t == 'R']
            if r and not r[0].startswith('Although some people argue that'):
                probs.append(f'{key} R should start "Although some people argue that"')
            if r and ', but ' in r[0]:
                probs.append('R uses "but" after "Although"')
            if not last.startswith('Therefore,'):
                probs.append(f'{key} L should start "Therefore,"')
    return probs

if __name__ == '__main__':
    args = sys.argv[1:]; pool = None
    if args and args[0] == '--source':
        paths = args[1].split(',')  # several chapters allowed: a.md,b.md
        pool = [s for p in paths for s in source_sentences(p)]
        full = ' '.join(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', open(p, encoding='utf-8').read().replace('**', ''))).lower() for p in paths)
        args = args[2:]
    total_reuse = 0
    for d in parse(args):
        c = [wc(d[k]) for k in ('I', 'B1', 'B2', 'C')]; t = sum(c)
        if d.get('format') == 'advdis':
            probs = advdis_problems(d)
            (t0, t1), (i0, i1), (c0, c1) = LIMITS['Type 1' in d.get('type', '')]
            ok = (t0 <= t <= t1 and i0 <= c[0] <= i1 and 120 <= c[1] <= 135 and 120 <= c[2] <= 135
                  and c0 <= c[3] <= c1 and not probs)
        elif d.get('format') == 'agree':
            probs = agree_problems(d)
            ok = (270 <= t <= 345 and 35 <= c[0] <= 50 and 100 <= c[1] <= 120 and 100 <= c[2] <= 120
                  and 35 <= c[3] <= 55 and not probs)
        elif d.get('format') == 'discuss':
            probs = discuss_problems(d)
            ok = (260 <= t <= 299 and 35 <= c[0] <= 45 and 90 <= c[1] <= 120 and 90 <= c[2] <= 120
                  and 35 <= c[3] <= 45 and not probs)
        elif d.get('format') in ('causesol', 'double'):
            probs = causesol_problems(d) if d['format'] == 'causesol' else double_problems(d)
            ok = (260 <= t <= 300 and 30 <= c[0] <= 40 and 90 <= c[1] <= 120 and 90 <= c[2] <= 120
                  and 30 <= c[3] <= 40 and not probs)
        else:
            probs = []
            ok = 260 <= t <= 280 and c[0] >= 30 and c[1] >= 100 and c[2] >= 100 and c[3] >= 30
        r = reused(d); total_reuse += len(r)
        print(d['code'], c, t, f'reused={len(r)}', '' if ok else '  <-- FIX')
        for p in probs:
            print('    structure:', p)
        if pool:
            for s in r:
                frag = re.sub(r'\s+', ' ', clean(s)).strip().rstrip('.').lower()
                if frag and frag[0].lower() + frag[1:] in full:
                    continue  # exact phrase found in the chapter (whole or part of a sentence)
                ratio = best_ratio(clean(s), pool)
                if ratio < 0.75:
                    print(f'    weak reuse match {ratio:.2f}: {clean(s)[:90]}')
    print('total reused sentences:', total_reuse)
