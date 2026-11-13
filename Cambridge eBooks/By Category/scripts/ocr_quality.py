"""Share of lowercase words the spell checker doesn't know, per page and OCR pass (lower is better).

Usage: python ocr_quality.py N [subdir ...]   (subdirs of working/C{N}/ocr holding json/, default: . and bin)
"""
import json, re, sys, pathlib
from spellchecker import SpellChecker

ROOT = pathlib.Path(__file__).resolve().parent.parent
sp = SpellChecker()
ocr = ROOT / "working" / f"C{sys.argv[1]}" / "ocr"
subs = sys.argv[2:] or [".", "bin"]
cfg = json.loads((ROOT / "working" / f"C{sys.argv[1]}" / f"passages_C{sys.argv[1]}.json").read_text(encoding="utf-8"))
for p in cfg["passages"]:
    for idx in p["pages"]:
        row = []
        for s in subs:
            f = ocr / s / "json" / f"p{idx:03d}.json"
            if not f.exists():
                row.append("   -  "); continue
            t = " ".join(l["text"] for l in json.load(open(f, encoding="utf-8-sig")))
            w = [x for x in re.findall(r"[A-Za-z]+", t) if x.islower() and len(x) > 2]
            row.append(f"{100 * len(sp.unknown(w)) / max(1, len(w)):5.1f}%")
        print(p["test"] + p["passage"], idx, *row)
