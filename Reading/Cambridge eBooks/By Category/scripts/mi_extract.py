"""Pull the Matching Information sets ("Which paragraph/section contains the following information?") out of the
Windows-OCR page JSON (Cambridge 10-14).

Usage: python mi_extract.py [N ...]
Reads working/mi/keys.json (which questions, official answers), working/C{N}/pages_C{N}.json and
working/C{N}/ocr/json/p###.json; optional per-set overrides in working/mi/overrides.json
({"C12 T2P3": {"instructions": [...], "statements": {"37": "..."}, "fixes": [[re, repl]]}}, global fixes under "*").
Writes working/mi/questions_C{N}.json: [{book, test, passage, kind, first, last, instructions, statements:{q: text}}].
"""
import json, re, sys, statistics, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
work = ROOT / "working" / "mi"
keys = json.loads((work / "keys.json").read_text(encoding="utf-8"))
ov_path = work / "overrides.json"
overrides = json.loads(ov_path.read_text(encoding="utf-8")) if ov_path.exists() else {}
books = [int(a) for a in sys.argv[1:]] or range(10, 15)

HEAD = re.compile(r"^[QCc]uestions? (\d{1,2})\s*[—–-]\s*(\d{1,2})")  # faint scans read Q as C
STOP = re.compile(r"^([QCc]uestions? \d|Choose |Complete |Answer the|Look at|Label |Classify |Match each)")
NUMLIKE = re.compile(r"^[0-9OIl]{1,2}$")


def num(t):
    return int(t.replace("O", "0").replace("I", "1").replace("l", "1")) if NUMLIKE.match(t) else None


def rows(n, idx):
    """OCR lines grouped into visual rows (a question number and its text can be separate OCR lines)."""
    f = ROOT / "working" / f"C{n}" / "ocr" / "json" / f"p{idx:03d}.json"
    if not f.exists():  # the page after the last passage page was never rendered
        return [], 40
    L = sorted(json.load(open(f, encoding="utf-8-sig")), key=lambda l: l["y"])
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
        r["words"] = [w for l in r["parts"] for w in l["words"]]
        r["text"] = " ".join(l["text"] for l in r["parts"])
    return out, h


def dash(t):
    return re.sub(r"\b([A-Z]|\d+)\s*[—–-]\s*([A-Z]|\d+)\b", r"\1–\2", t)


for n in books:
    plan = json.loads((ROOT / "working" / f"C{n}" / f"pages_C{n}.json").read_text())
    out = []
    for k in [k for k in keys if k["book"] == n]:
        name = f"C{n} {k['test']}{k['passage']}"
        o = overrides.get(name, {})
        first, last = k["first"], k["last"]
        pages = next(p["pages"] for p in plan["passages"] if p["test"] == k["test"] and p["passage"] == k["passage"])
        pages = pages + [pages[-1] + 1]  # a set can run on to the first page of the next passage
        start = None
        for pi, idx in enumerate(pages):
            R, _ = rows(n, idx)
            for r in R:
                m = HEAD.match(r["text"])
                if m and int(m.group(1)) == first:
                    start = (pi, r["y"]); break
            if start:
                break
        if not start:  # heading misread: start at the "Reading Passage n has ..." line above "Which ... contains"
            for pi, idx in enumerate(pages):
                R, _ = rows(n, idx)
                hit = [i for i, r in enumerate(R) if re.search(r"^Which (paragraph|section) cont", r["text"])]
                if hit:
                    i = hit[0] - 1 if hit[0] and R[hit[0] - 1]["text"].startswith("Reading Passage") else hit[0]
                    start = (pi, R[i]["y"] - 20); break
        if not start:
            print(f"!! {name}: heading for Q{first} not found"); continue
        ins, stm, cur, prev_y, gaps, done = [], {}, None, None, [], False
        for j, idx in enumerate(pages[start[0]:start[0] + 2]):
            R, h = rows(n, idx)
            R = [r for r in R if r["y"] > (start[1] + 10 if j == 0 else 150)]
            bottom = max((r["y"] for r in R), default=0)
            for r in R:
                t = r["text"]
                if re.fullmatch(r"\d{1,3}", t) and r["y"] >= bottom - 5:
                    continue  # page number
                if STOP.match(t) and (stm or HEAD.match(t)):
                    done = True; break
                q = num(r["words"][0]["t"])
                if q is not None and first <= q <= last and q not in stm and (cur is None or q > cur):
                    if cur is not None and j == 0:
                        gaps.append(r["y"] - prev_y)
                    cur, prev_y = q, r["y"]
                    stm[q] = t.split(" ", 1)[1] if " " in t else ""
                    continue
                if cur is None:
                    ins.append(t)
                    continue
                lim = 0.8 * min(gaps) if gaps else 1.6 * h
                if r["y"] - prev_y > (lim if cur == last else 3 * h):
                    if cur == last:
                        done = True; break
                    continue
                stm[cur] = (stm[cur] + " " + t).strip()
                prev_y = r["y"]
            if done:
                break
        instructions = o.get("instructions", [dash(t) for t in ins])
        for a, b in overrides.get("*", {}).get("ifixes", []):
            instructions = [re.sub(a, b, t) for t in instructions]
        for q, t in o.get("statements", {}).items():
            stm[int(q)] = t
        for q in list(stm):
            for a, b in o.get("fixes", []) + overrides.get("*", {}).get("fixes", []):
                stm[q] = re.sub(a, b, stm[q])
            stm[q] = stm[q].strip()
        res = {"book": n, "test": k["test"], "passage": k["passage"], "kind": "MI", "first": first, "last": last,
               "instructions": instructions, "statements": {str(q): stm[q] for q in sorted(stm)}}
        out.append(res)
        missing = [q for q in range(first, last + 1) if q not in stm]
        print(f"== {name} Q{first}-{last}" + (f"  !! missing {missing}" if missing else ""))
        for t in instructions:
            print("   I:", t)
        for q in sorted(stm):
            print(f"   {q:>2} {stm[q]}")
    (work / f"questions_C{n}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
