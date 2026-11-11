"""Pull the TRUE/FALSE/NOT GIVEN and YES/NO/NOT GIVEN question sets out of the Windows-OCR page JSON (Cambridge 10-14).

Usage: python tfng_extract.py [N ...]
Reads working/tfng/keys.json (from tfng_keys.py: which questions are TFNG/YNNG), working/C{N}/pages_C{N}.json
and working/C{N}/ocr/json/p###.json; optional per-set overrides in working/tfng/overrides.json
({"C12 T4P1": {"ask": "...", "statements": {"9": "..."}, "fixes": [[re, repl]]}}, global fixes under "*").
Writes working/tfng/questions_C{N}.json: [{book, test, passage, kind, first, last, instructions, defs, statements:{q: text}}].
The instructions and the TRUE/FALSE/NOT GIVEN box are standard wording, rebuilt from the book's own first line
("information given in" / "claims of the writer in" / "views of the writer in"); statements come from OCR rows.
"""
import json, re, sys, statistics, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
work = ROOT / "working" / "tfng"
keys = json.loads((work / "keys.json").read_text(encoding="utf-8"))
ov_path = work / "overrides.json"
overrides = json.loads(ov_path.read_text(encoding="utf-8")) if ov_path.exists() else {}
books = [int(a) for a in sys.argv[1:]] or range(10, 15)

HEAD = re.compile(r"^[QCc]uestions? (\d{1,2})\s*[—–-]\s*(\d{1,2})")  # faint scans read Q as C
STOP = re.compile(r"^(Questions? \d|Choose |Complete |Answer the|Write the correct|Look at|Label |Classify )")
ASK = re.compile(r"agree with the (information given in|information in|claims of the writer in|views of the writer in) Reading Passage (\d)")
NUMLIKE = re.compile(r"^[0-9OIl]{1,2}$")
DEFS = {
    "information": [["TRUE", "if the statement agrees with the information"],
                    ["FALSE", "if the statement contradicts the information"],
                    ["NOT GIVEN", "if there is no information on this"]],
    "claims": [["YES", "if the statement agrees with the claims of the writer"],
               ["NO", "if the statement contradicts the claims of the writer"],
               ["NOT GIVEN", "if it is impossible to say what the writer thinks about this"]],
    "views": [["YES", "if the statement agrees with the views of the writer"],
              ["NO", "if the statement contradicts the views of the writer"],
              ["NOT GIVEN", "if it is impossible to say what the writer thinks about this"]],
}


def num(t):
    return int(t.replace("O", "0").replace("I", "1").replace("l", "1")) if NUMLIKE.match(t) else None


def rows(n, idx):
    """OCR lines grouped into visual rows (a question number and its text can be separate OCR lines)."""
    L = json.load(open(ROOT / "working" / f"C{n}" / "ocr" / "json" / f"p{idx:03d}.json", encoding="utf-8-sig"))
    L = sorted(L, key=lambda l: l["y"])
    h = statistics.median(l["h"] for l in L) if L else 40
    out = []
    for l in L:
        l["text"] = re.sub(r"\s+", " ", l["text"]).strip()
        if out and abs(l["y"] - out[-1]["y"]) < 0.5 * h:
            out[-1]["parts"].append(l)
        else:
            out.append({"y": l["y"], "parts": [l]})
    for r in out:
        r["parts"].sort(key=lambda l: l["x"])
        r["x"] = r["parts"][0]["x"]
        r["words"] = [w for l in r["parts"] for w in l["words"]]
        r["text"] = " ".join(l["text"] for l in r["parts"])
    return out, h


for n in books:
    plan = json.loads((ROOT / "working" / f"C{n}" / f"pages_C{n}.json").read_text())
    out = []
    for k in [k for k in keys if k["book"] == n]:
        name = f"C{n} {k['test']}{k['passage']}"
        o = overrides.get(name, {})
        qs = sorted(int(q) for q in k["answers"])
        first, last = qs[0], qs[-1]
        pages = next(p["pages"] for p in plan["passages"] if p["test"] == k["test"] and p["passage"] == k["passage"])
        pages = pages + [pages[-1] + 1]  # a set can run on to the first page of the next passage
        start = None
        for pi, idx in enumerate(pages):
            R, _ = rows(n, idx)
            for r in R:
                m = HEAD.match(r["text"])
                if m and int(m.group(1)) <= first <= int(m.group(2)):
                    start = (pi, r["y"]); break
            if start:
                break
        if not start:  # heading lost or misread: start at the "Do the following statements agree" line
            for pi, idx in enumerate(pages):
                R, _ = rows(n, idx)
                hit = [r["y"] for r in R if ASK.search(r["text"]) and not re.search(r"Questions? 1\D", r["text"])]
                if hit:
                    start = (pi, hit[0] - 30); break
        if not start:
            print(f"!! {name}: heading for Q{first} not found"); continue
        ask, stm, cur, prev_y, gaps, done = None, {}, None, None, [], False
        for j, idx in enumerate(pages[start[0]:start[0] + 2]):
            R, h = rows(n, idx)
            R = [r for r in R if r["y"] > (start[1] + 10 if j == 0 else 150)]
            bottom = max((r["y"] for r in R), default=0)
            for r in R:
                t = r["text"]
                if re.fullmatch(r"\d{1,3}", t) and r["y"] >= bottom - 5:
                    continue  # page number
                if ask is None and ASK.search(t):
                    ask = ASK.search(t)
                    continue
                if STOP.match(t) and (stm or HEAD.match(t)):
                    done = True; break
                w0 = r["words"][0]["t"]
                q = num(w0)
                if q is not None and first <= q <= last and q not in stm and (cur is None or q > cur):
                    if cur is not None and prev_y is not None and j == 0:
                        gaps.append(r["y"] - prev_y)
                    cur, prev_y = q, r["y"]
                    stm[q] = t.split(" ", 1)[1] if " " in t else ""
                    continue
                if cur is None:
                    continue
                # a row that holds the next number in the middle (OCR joined two statements)
                m = re.search(rf" ({cur + 1}|{str(cur + 1).replace('0', 'O').replace('1', 'I')}) (?=[A-Z])", t)
                if m and cur + 1 <= last:
                    stm[cur] += " " + t[:m.start()]
                    cur += 1
                    stm[cur] = t[m.end():]
                    prev_y = r["y"]; continue
                # continuation of the current statement: close below it; after the last one, stop at a gap
                lim = 0.8 * min(gaps) if gaps else 1.6 * h
                if r["y"] - prev_y > (lim if cur == last else 3 * h):
                    if cur == last:
                        done = True; break
                    continue
                stm[cur] = (stm[cur] + " " + t).strip()
                prev_y = r["y"]
            if done or (last in stm and j == 0 and any(r["y"] > prev_y + 3 * h for r in R)):
                break
        word = ask.group(1) if ask else o.get("ask", "information given in")
        kind_word = "claims" if "claims" in word else "views" if "views" in word else "information"
        pnum = ask.group(2) if ask else k["passage"][1]
        instructions = [f"Do the following statements agree with the {word} Reading Passage {pnum}?",
                        f"In boxes {first}–{last} on your answer sheet, write"]
        for q, t in o.get("statements", {}).items():
            stm[int(q)] = t
        for q in list(stm):
            for a, b in o.get("fixes", []) + overrides.get("*", {}).get("fixes", []):
                stm[q] = re.sub(a, b, stm[q])
            stm[q] = stm[q].strip()
        if (kind_word == "information") != (k["kind"] == "TFNG"):
            print(f"!! {name}: key says {k['kind']} but the question says '{word}'")
        res = {"book": n, "test": k["test"], "passage": k["passage"], "kind": k["kind"], "first": first, "last": last,
               "instructions": instructions, "defs": o.get("defs", DEFS[kind_word]), "statements": {str(q): stm[q] for q in sorted(stm)}}
        out.append(res)
        missing = [q for q in qs if q not in stm]
        print(f"== {name} {k['kind']} Q{first}-{last} ({word}{'' if ask else ' ?? not read'})" + (f"  !! missing {missing}" if missing else ""))
        for q in sorted(stm):
            print(f"   {q:>2} {stm[q]}")
    (work / f"questions_C{n}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
