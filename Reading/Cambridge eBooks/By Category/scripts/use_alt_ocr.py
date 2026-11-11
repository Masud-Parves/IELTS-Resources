"""Use the 450 dpi binarized OCR pass (ocr/bin/json) as a page's main OCR, scaled to 300 dpi.

Usage: python use_alt_ocr.py N page [page ...]   (old JSON kept as p###_win.json)
For pages where ocr_quality.py shows the binarized pass is clearly better.
"""
import json, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ocr = ROOT / "working" / f"C{sys.argv[1]}" / "ocr"
for pg in sys.argv[2:]:
    jf, keep = ocr / "json" / f"p{int(pg):03d}.json", ocr / "json" / f"p{int(pg):03d}_win.json"
    if not keep.exists():
        jf.rename(keep)
    L = json.load(open(ocr / "bin" / "json" / f"p{int(pg):03d}.json", encoding="utf-8-sig"))
    for l in [l for l in L] + [w for l in L for w in l["words"]]:
        for k in ("x", "y", "w", "h"):
            l[k] = round(l[k] / 1.5)
    json.dump(L, open(jf, "w", encoding="utf-8"), ensure_ascii=False)
