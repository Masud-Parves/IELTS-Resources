"""Pull the Matching Sentence Endings sets ("Complete each sentence with the correct ending") out of the
Windows-OCR page JSON (Cambridge 10-14).

Usage: python me_extract.py [N ...]
Reads working/me/keys.json (which questions, official answers), working/C{N}/pages_C{N}.json and
working/C{N}/ocr/json/p###.json; optional per-set overrides in working/me/overrides.json
({"C13 T2P3": {"instructions": [...], "statements": {"38": "..."}, "options": {"A": "..."}}}, global
statement/option fixes under "*" -> "fixes", instruction fixes under "*" -> "ifixes").
Writes working/me/questions_C{N}.json: [{book, test, passage, kind, first, last, instructions,
statements:{q: sentence beginning}, options:{letter: ending}}].
"""
import json, re, sys, statistics, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
work = ROOT / "working" / "me"
keys = json.loads((work / "keys.json").read_text(encoding="utf-8"))
ov_path = work / "overrides.json"
overrides = json.loads(ov_path.read_text(encoding="utf-8")) if ov_path.exists() else {}
books = [int(a) for a in sys.argv[1:]] or range(10, 15)

HEAD = re.compile(r"^[QCc]uestions? (\d{1,2})\s*[—–-]\s*(\S{1,2})")  # faint scans read Q as C, and 38 as 3E
STOP = re.compile(r"^([QCc]uestions? \d|Choose |Complete the |Answer the|Look at|Label |Classify |Match each|Do the following)")
NUMLIKE = re.compile(r"^[0-9OIl]{1,2}$")
LETTER = re.compile(r"^[A-Ja-j]$")


def num(t):
    return int(t.replace("O", "0").replace("I", "1").replace("l", "1")) if NUMLIKE.match(t) else None


def rows(n, idx):
    """OCR lines grouped into visual rows (a number or letter and its text can be separate OCR lines)."""
    f = ROOT / "working" / f"C{n}" / "ocr" / "json" / f"p{idx:03d}.json"
    if not f.exists():
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
            for i, r in enumerate(R):
                nxt = R[i + 1]["text"] if i + 1 < len(R) else ""
                if HEAD.match(r["text"]) and "correct ending" in nxt and str(first)[0] == HEAD.match(r["text"]).group(1)[0]:
                    start = (pi, r["y"]); break
            if start:
                break
        if not start:  # heading misread (C13 has "Questions 3E40"): start just above the "correct ending" line
            for pi, idx in enumerate(pages):
                R, _ = rows(n, idx)
                hit = [i for i, r in enumerate(R) if "correct ending" in r["text"]
                       and i + 1 < len(R) and f"{first}" in R[i + 1]["text"]]
                if hit:
                    start = (pi, R[hit[0]]["y"] - 20); break
        if not start:
            print(f"!! {name}: heading for Q{first} not found"); continue
        ins, stm, opts, cur, prev_y, done = [], {}, {}, None, None, False
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
                w0 = r["words"][0]["t"]
                q = num(w0)
                if not opts and q is not None and first <= q <= last and q not in stm:
                    cur, prev_y = q, r["y"]
                    stm[q] = t.split(" ", 1)[1] if " " in t else ""
                    continue
                if stm and LETTER.match(w0) and " " in t:
                    cur, prev_y = w0.upper(), r["y"]
                    opts[cur] = t.split(" ", 1)[1]
                    continue
                if cur is None:
                    ins.append(t)
                    continue
                if r["y"] - prev_y > (2.2 * h if opts else 3 * h):
                    if opts:
                        done = True; break
                    continue
                if isinstance(cur, int):
                    stm[cur] = (stm[cur] + " " + t).strip()
                else:
                    opts[cur] = (opts[cur] + " " + t).strip()
                prev_y = r["y"]
            if done or opts:
                break
        instructions = o.get("instructions", ins)
        for a, b in overrides.get("*", {}).get("ifixes", []):
            instructions = [re.sub(a, b, t) for t in instructions]
        instructions = [dash(t) for t in instructions]  # after the fixes: "A—GI in" only becomes "A—G, in" there
        for q, t in o.get("statements", {}).items():
            stm[int(q)] = t
        opts.update(o.get("options", {}))
        fixes = o.get("fixes", []) + overrides.get("*", {}).get("fixes", [])
        for d in (stm, opts):
            for key in list(d):
                for a, b in fixes:
                    d[key] = re.sub(a, b, d[key])
                d[key] = d[key].strip()
        res = {"book": n, "test": k["test"], "passage": k["passage"], "kind": "ME", "first": first, "last": last,
               "instructions": instructions, "statements": {str(q): stm[q] for q in sorted(stm)},
               "options": {c: opts[c] for c in sorted(opts)}, "options_title": o.get("options_title", "")}
        out.append(res)
        missing = [q for q in range(first, last + 1) if q not in stm]
        letters = "".join(sorted(opts))
        expect = "ABCDEFGHIJ"[:len(opts)]
        print(f"== {name} Q{first}-{last}" + (f"  !! missing {missing}" if missing else "")
              + (f"  !! options {letters}" if letters != expect else ""))
        for t in instructions:
            print("   I:", t)
        for q in sorted(stm):
            print(f"   {q:>2} {stm[q]}")
        for c in sorted(opts):
            print(f"    {c} {opts[c]}")
    (work / f"questions_C{n}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
