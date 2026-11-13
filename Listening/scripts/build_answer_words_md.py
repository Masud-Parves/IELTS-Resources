"""Write the "Real Answer Words" chapter of the spelling workbook from cambridge_answer_words.json.

Usage: python build_answer_words_md.py   (build_spelling_workbook_pdf.py also runs it first)
Input : Listening/Spelling Workbook/cambridge_answer_words.json  (made by Cambridge eBooks/Listening Answers/scripts)
Output: Listening/Spelling Workbook/09_answer_words.md, and dictation sets aw1-aw7 in dictation.json
        (the 7 daily blocks of frequent words, in shuffled order, word only).
"""
import json, re, random, pathlib, html

WB = pathlib.Path(__file__).resolve().parent.parent / "Spelling Workbook"
rows = json.loads((WB / "cambridge_answer_words.json").read_text(encoding="utf-8"))

# Words the lessons already teach: the bold first cell of each table row in Days 1-7.
taught = set()
for f in sorted(WB.glob("0[1-7]_*.md")):
    taught |= {m.lower() for m in re.findall(r"^\| \*\*([A-Za-z][A-Za-z' -]*)\*\*", f.read_text(encoding="utf-8"), re.M)}
in_wb = lambda r: any(f.lower() in taught for f in r["forms"] + [r["word"]])

frequent = [r for r in rows if r["count"] >= 2]
n_blocks = 7
size = -(-len(frequent) // n_blocks)
blocks = [frequent[i:i + size] for i in range(0, len(frequent), size)]
total_answers = 825


def other_forms(r):
    s = [f for f in r["forms"] if f != r["word"]]
    if r["us"]:
        s.append("AmE: " + ", ".join(r["us"]))
    return ", ".join(s)


md = [f"""## [Bank] Real Answer Words: Cambridge 10–19

### What this list is

Every **gap-fill answer** in the Listening answer keys of **Cambridge IELTS 10–19** (40 tests, 1,600 questions) was collected. Letter answers (A–H), numbers, times, postcodes and people's or place names were removed. Alternatives such as *garden(s)* or *colour / color* were joined, so singular and plural, and British and American spellings, count as **one word**. Then all duplicates were removed.

| | |
|---|---|
| Gap-fill answers with words | **{total_answers}** |
| Different words after removing duplicates | **{len(rows)}** |
| Words used **2 or more times** (Part A) | **{len(frequent)}** |
| Words also taught in Days 1–7 | **{sum(in_wb(r) for r in rows)}** (marked ●) |

> 💡 **What the list shows:** most answers are **short, everyday words** (*parking, bridge, map, food, week, insects*), not rare academic words. You lose marks on easy words spelt wrong, a missing **-s**, or a doubled letter. That is why each block below includes the plural forms the key accepted.

### How to practise

| When | What to do |
|---|---|
| **Each day of the 7-day plan** | Learn **one block** of Part A (about {size} words), using Look-Say-Cover-Write-Check. Then play that block's dictation (**AnswerWords_Block1.wav … Block7.wav**) and write the words in the answer lines. The words are read in a different order from the list. |
| **After the 7 days** | Work through Part B, **one or two letters a day**. Say each word, cover it and write it. Put every word you get wrong in the Error Log. |
| **Before every mock test** | Read Part A again quickly. These words have already appeared in real tests more than once. |

**Times** = how many different answers in Cambridge 10–19 used the word.
"""]

for i, b in enumerate(blocks, 1):
    md.append(f"### Part A, Block {i} (Day {i}): words {sum(len(x) for x in blocks[:i-1]) + 1}–{sum(len(x) for x in blocks[:i])}\n")
    md.append("| # | Word | Other forms in the key | Times | Cover and write |\n|---|---|---|---|---|")
    start = sum(len(x) for x in blocks[:i - 1])
    for k, r in enumerate(b, start + 1):
        mark = " ●" if in_wb(r) else ""
        md.append(f"| {k} | **{r['word']}**{mark} | {other_forms(r)} | {r['count']} | [[blank]] |")
    md.append("")

md.append("""### Part A dictations

▶ Play **AnswerWords_Block1.wav** after studying Block 1, and so on. Each word is read twice. Write the singular form unless you hear a plural.
""")
for i in range(1, len(blocks) + 1):
    md.append(f"#### Block {i}\n\n[[dictation:aw{i}]]\n")

md.append(f"""### Part B: All {len(rows)} answer words A–Z

A small number after a word = it was used that many times. ● = also taught in Days 1–7.
""")
letters = {}
for r in sorted(rows, key=lambda r: r["word"].lower()):
    letters.setdefault(r["word"][0].upper(), []).append(r)
parts = ["<ul class='az'>"]                 # one continuous list, so the columns fill every page
for L, rs in letters.items():
    parts.append(f"<li class='azletter'>{L}</li>")
    parts += [f"<li>{html.escape(r['word'])}" + (f"<sup>{r['count']}</sup>" if r["count"] >= 2 else "")
              + (" ●" if in_wb(r) else "") + "</li>" for r in rs]
parts.append("</ul>")
md.append("\n".join(parts) + "\n")

(WB / "09_answer_words.md").write_text("\n".join(md), encoding="utf-8")

# Dictation sets: each block in a fixed shuffled order, word only (empty sentence).
dpath = WB / "dictation.json"
dic = json.loads(dpath.read_text(encoding="utf-8"))
rng = random.Random(19)
for i, b in enumerate(blocks, 1):
    words = [r["word"] for r in b]
    rng.shuffle(words)
    dic[f"aw{i}"] = {"title": f"Real answer words, block {i}", "items": [[w, ""] for w in words]}
dpath.write_text(json.dumps(dic, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"{len(rows)} words, {len(frequent)} frequent in {len(blocks)} blocks of up to {size}")
