"""Read TRUE/FALSE/NOT GIVEN and YES/NO/NOT GIVEN answers from the OCR'd Reading answer keys (Cambridge 10-14).

Usage: python tfng_keys.py
Reads working/headings/keys/json/C{N}_p###.json (from headings_render_keys.py + winocr.ps1);
writes working/tfng/keys.json: [{book, test, passage, kind, answers:{q: ans}}], one entry per run of questions.
"""
import json, re, glob, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
WORDS = {"TRUE", "FALSE", "NOT GIVEN", "YES", "NO"}
out = []
for f in sorted(glob.glob(str(ROOT / "working" / "headings" / "keys" / "json" / "*.json"))):
    name = pathlib.Path(f).stem
    n = int(name[1:3])
    pages = sorted(glob.glob(str(ROOT / "working" / "headings" / "keys" / "json" / f"C{n}_*.json")))
    test = f"T{pages.index(f) + 1}"
    L = json.load(open(f, encoding="utf-8-sig"))
    toks = [(w["x"], w["y"], w["t"]) for l in L for w in l["words"]]
    ans = {}
    for l in L:
        t = re.sub(r"^\d{1,2}\s+", "", l["text"]).strip()
        t = re.sub(r"\s+", " ", t)
        if t not in WORDS and l["text"].strip() not in WORDS:
            continue
        word = t if t in WORDS else l["text"].strip()
        x0, y0 = l["x"], l["y"]
        nums = [(x, tt) for x, y, tt in toks if abs(y - y0) < 25 and x < x0 + 5 and x0 - x < 260 and re.fullmatch(r"\d{1,2}", tt)]
        if nums:
            ans[int(max(nums)[1])] = word
    runs = []
    for q in sorted(ans):
        p = "P1" if q <= 13 else "P2" if q <= 26 else "P3"
        if runs and q == runs[-1]["last"] + 1 and runs[-1]["passage"] == p:
            runs[-1]["answers"][q] = ans[q]; runs[-1]["last"] = q
        else:
            runs.append({"book": n, "test": test, "passage": p, "answers": {q: ans[q]}, "last": q})
    for r in runs:
        r["kind"] = "YNNG" if set(r["answers"].values()) & {"YES", "NO"} else "TFNG"
        del r["last"]
        out.append(r)
        print(f'C{n} {test} {r["passage"]} {r["kind"]} ' + " ".join(f"{q}={a.replace('NOT GIVEN','NG')}" for q, a in r["answers"].items()))
(ROOT / "working" / "tfng" / "keys.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print(len(out), "runs,", sum(len(r["answers"]) for r in out), "questions")
