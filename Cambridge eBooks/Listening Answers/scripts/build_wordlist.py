"""Turn working/answers.json into working/wordlist.json: unique answer words with frequency.

- Only gap-fill answers with words (letters, numbers, codes and times are dropped).
- Alternatives ("/") and optional parts ("garden(s)", "(the) river") are expanded.
- Function words, number words and proper names (capitalised and not in the dictionary) are dropped.
- American alternatives go under the British headword; singular and plural are merged under one headword; "forms" lists the spellings seen.
- count = number of answers (questions) the word appears in, across Cambridge 10-19.
"""
import json, re, pathlib
from collections import defaultdict
from spellchecker import SpellChecker

ROOT = pathlib.Path(__file__).resolve().parent.parent
SP = SpellChecker()
STOP = set("""a an the of and or to in on for with at by from per not no as into its it is be are very
than then up out off over under about after before more most some any each every all both this that""".split())
NUMS = set("""one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen
seventeen eighteen nineteen twenty thirty forty fifty sixty seventy eighty ninety hundred thousand million
half quarter self first second third fourth fifth am pm th st nd rd""".split())
KEEP_CAPS = {"Maths"}
DAYS_MONTHS = {"monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", "january",
               "february", "march", "april", "may", "june", "july", "august", "september", "october",
               "november", "december"}
BRIT = {"behaviour", "colour", "harbour", "litre", "fertilisers", "fertiliser", "socialise", "smartphone",
        "smartphones", "wifi", "café", "cafe"}


def expand(ans):
    """All spellings an answer allows: split '/', and take optional '(s)'/'(the)' parts both ways."""
    out = []
    for alt in re.split(r"\s+/\s+|/", ans):
        alt = alt.strip()
        with_opt = re.sub(r"[()]", "", alt)
        without = re.sub(r"\([^)]*\)", "", alt)
        out += [with_opt, without]
    return out


def is_name(w):
    """Answer keys are lower case, so a capital means a name or title (except days, months and Maths)."""
    return w[0].isupper() and w not in KEEP_CAPS and w.lower() not in DAYS_MONTHS


def british(w, vocab):
    """Map an American alternative to the British spelling when the key also gives that spelling."""
    for pat, rep in ((r"or(s?)$", r"our\1"), (r"er(s?)$", r"re\1"), (r"iz(e|es|ed|ing|ation|er|ers)$", r"is\1"),
                     (r"yz(e|es|ed|ing)$", r"ys\1"), (r"([aeiou])l(ing|ed|er)$", r"\1ll\2")):
        b = re.sub(pat, rep, w)
        if b != w and b in vocab:
            return b
    return w


def singular(w, vocab):
    for suf, rep in (("ies", "y"), ("ves", "f"), ("ves", "fe"), ("es", ""), ("s", "")):
        if w.endswith(suf) and len(w) > len(suf) + 2:
            stem = w[: -len(suf)] + rep
            if stem in vocab and not w.endswith("ss"):
                return stem
    return w


answers = [r for r in json.loads((ROOT / "working" / "answers.json").read_text(encoding="utf-8")) if r["kind"] == "words"]
per_answer = []
for r in answers:
    words = set()
    for spelling in expand(r["answer"]):
        for w in re.findall(r"[A-Za-zé]+(?:[-'][A-Za-zé]+)*", spelling):
            if w.lower() in STOP or w.lower() in NUMS or all(p in NUMS for p in w.lower().split("-")) or len(w) < 2 or is_name(w):
                continue
            if re.fullmatch(r"[A-Z]{1,3}", w):        # codes like GT, DW
                continue
            words.add(w if w in KEEP_CAPS or w.lower() in DAYS_MONTHS and w[0].isupper() else w.lower())
    per_answer.append(words)

vocab = set().union(*per_answer)
count, forms, us = defaultdict(int), defaultdict(set), defaultdict(set)
for words in per_answer:
    heads = set()
    for w in words:
        b = british(w, vocab)
        h = singular(b, vocab)
        (us if b != w else forms)[h].add(w)
        heads.add(h)
    for h in heads:
        count[h] += 1

rows = [{"word": h, "count": count[h], "forms": sorted(forms[h], key=lambda f: (len(f), f)),
         "us": sorted(us[h])} for h in count]
rows.sort(key=lambda r: (-r["count"], r["word"].lower()))
(ROOT / "working" / "wordlist.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding="utf-8")
# The workbook keeps its own copy (words and counts only, no test/question references).
WB = ROOT.parent.parent / "Listening" / "Spelling Workbook" / "cambridge_answer_words.json"
WB.write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding="utf-8")
print(len(answers), "word answers ->", len(rows), "unique headwords;",
      sum(r["count"] >= 2 for r in rows), "appear 2+ times;", sum(r["count"] >= 3 for r in rows), "3+ times")
print(", ".join(f"{r['word']}({r['count']})" for r in rows[:120]))
