"""Pull the List of Headings question sets out of the Windows-OCR page JSON (Cambridge 10-14).

Usage: python headings_extract.py
Reads working/headings/sets.json (which book/test/passage/page) and working/C{N}/ocr/json/p###.json;
writes working/headings/questions.json with
{book, test, passage, instructions:[...], headings:[{roman, text}], questions:[{q, label}], example:{label, roman}}.
The OCR drops some Roman numerals, so numerals are assigned by position and checked against what OCR read.
"""
import json, re, pathlib, statistics

ROOT = pathlib.Path(__file__).resolve().parent.parent
work = ROOT / "working" / "headings"
sets = json.loads((work / "sets.json").read_text(encoding="utf-8"))

ROMANS = "i ii iii iv v vi vii viii ix x xi xii".split()
ROMAN = re.compile(r"^(i{1,3}|iv|v|vi{1,3}|ix|x|xi{1,2}|[lI1]{1,3})$")
LEAD_ROMAN = re.compile(r"^(i{1,3}|iv|vi{0,3}|ix|xi{0,2}) (?=[A-Z])")
QLABEL = re.compile(r"\b(Paragraph|Section) ([A-Z])\b")


def load(n, idx):
    L = json.load(open(ROOT / "working" / f"C{n}" / "ocr" / "json" / f"p{idx:03d}.json", encoding="utf-8-sig"))
    for l in L:
        l["text"] = l["text"].strip()
    return sorted(L, key=lambda l: l["y"])


out = []
for s in sets:
    L = load(s["book"], s["page"])
    drop = [re.compile(d) for d in s.get("drop", [])]
    L = [l for l in L if not any(d.search(l["text"]) for d in drop)]
    y_list = next(l["y"] for l in L if l["text"] == "List of Headings")
    y_ins = max((l["y"] for l in L if re.search(r"Passage \d (on|below|\.)|^Passage \d\.", l["text"]) and l["y"] < y_list), default=0)
    ins = [l for l in L if y_ins < l["y"] < y_list and not re.match(r"^Questions? \d", l["text"])]
    instructions = s.get("instructions") or [l["text"] for l in ins]

    # the first question row or Example box closes the list
    rows = [l for l in L if l["y"] > y_list]
    y_end = min(l["y"] for l in rows if QLABEL.search(l["text"]) or l["text"] == "Example")
    box = [l for l in rows if l["y"] < y_end - 5]
    romans = [l for l in box if ROMAN.match(l["text"])]
    lines = [l for l in box if not ROMAN.match(l["text"])]
    for l in lines:
        m = LEAD_ROMAN.match(l["text"])
        if m:
            l["text"] = l["text"][m.end():]
            l["read"] = m.group(1)
    # wrapped headings sit closer together than the gap between headings
    gaps = [b["y"] - a["y"] for a, b in zip(lines, lines[1:])]
    pitch = statistics.median(gaps)
    items = []
    for l in lines:
        if items and l["y"] - items[-1]["last"] < 0.8 * pitch:
            items[-1]["text"] += " " + l["text"]
            items[-1]["last"] = l["y"]
        else:
            items.append({"text": l["text"], "y": l["y"], "last": l["y"], "read": l.get("read")})
    headings = []
    for i, it in enumerate(items):
        rom = ROMANS[i]
        near = [r["text"] for r in romans if abs(r["y"] - it["y"]) < 15]
        seen = it["read"] or (near[0] if near else None)
        if seen != rom:
            print(f'  note C{s["book"]} {s["test"]}{s["passage"]}: {rom} read by OCR as {seen!r}: {it["text"]}')
        text = it["text"]
        for a, b in s.get("fixes", []):
            text = re.sub(a, b, text)
        headings.append({"roman": rom, "text": text})

    # question rows: the number sits left of "Paragraph X" on the same row (rows can be in two columns)
    below = [l for l in L if l["y"] >= y_end - 5]
    nums = [l for l in below if re.fullmatch(r"\d{1,2}", l["text"])]
    questions, example = [], None
    for l in below:
        m = QLABEL.search(l["text"])
        if not m:
            continue
        cand = [n for n in nums if abs(n["y"] - l["y"]) < 28 and n["x"] < l["x"] and l["x"] - n["x"] < 260]
        if cand:
            n = max(cand, key=lambda n: n["x"])
            questions.append({"q": int(n["text"]), "label": f"{m.group(1)} {m.group(2)}"})
        else:
            example = {"label": f"{m.group(1)} {m.group(2)}"}
            near = [r for r in below if abs(r["y"] - l["y"]) < 20 and r is not l]
            example["roman"] = near[0]["text"] if near else "?"
    questions.sort(key=lambda q: q["q"])
    if s.get("questions"):
        questions = s["questions"]
    res = {k: s[k] for k in ("book", "test", "passage", "page")}
    res.update(instructions=instructions, headings=headings, questions=questions, example=example)
    out.append(res)
    print(f'== C{s["book"]} {s["test"]}{s["passage"]}: {len(headings)} headings, {len(questions)} questions, example {example}')
    for t in instructions:
        print("   I:", t)
    for h in headings:
        print(f'   {h["roman"]:>5}  {h["text"]}')
    print("   Q:", " ".join(f'{q["q"]}={q["label"].split()[1]}' for q in questions))

(work / "questions.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
