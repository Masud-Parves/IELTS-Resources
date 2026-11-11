"""List words where the two OCR variants disagree (300 dpi colour vs 450 dpi binarized).

Usage: python passages_ocr_diff.py N [page ...]
Each disagreement is printed with page, y (300 dpi) and a little context, for manual checking.
"""
import json, sys, pathlib, difflib

ROOT = pathlib.Path(__file__).resolve().parent.parent
N = sys.argv[1]
ocr = ROOT / "working" / f"C{N}" / "ocr"
pages = sys.argv[2:] or sorted(f.stem[1:] for f in (ocr / "bin" / "json").glob("p*.json"))
for pg in pages:
    A = json.load(open(ocr / "json" / f"p{int(pg):03d}.json", encoding="utf-8-sig"))
    B = json.load(open(ocr / "bin" / "json" / f"p{int(pg):03d}.json", encoding="utf-8-sig"))
    for a in A:
        cy, cx = a["y"] + a["h"] / 2, a["x"] + a["w"] / 2
        best = [b for b in B if abs(b["y"] / 1.5 + b["h"] / 3 - cy) < a["h"] / 2 and abs(b["x"] / 1.5 + b["w"] / 3 - cx) < a["w"] / 2 + 40]
        if not best:
            print(f"p{pg} y={a['y']}: NO MATCH  {a['text']}")
            continue
        b = min(best, key=lambda b: abs(b["x"] / 1.5 - a["x"]))
        wa, wb = a["text"].split(), b["text"].split()
        for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, wa, wb, autojunk=False).get_opcodes():
            if op != "equal":
                ctx = " ".join(wa[max(0, i1 - 2):i2 + 2])
                print(f"p{pg} y={a['y']}: {' '.join(wa[i1:i2])!s:>18} | {' '.join(wb[j1:j2])!s:<18}  [{ctx}]")
