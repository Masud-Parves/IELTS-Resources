"""Second OCR variant for cross-checking: 450 dpi, blurred + binarized (removes halftone tint).

Usage: python passages_ocr_alt.py N   -> working/C{N}/ocr/bin/p###.png (then run winocr.ps1 on them)
"""
import json, sys, pathlib
import pymupdf
from PIL import Image, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parent.parent
N = sys.argv[1]
work = ROOT / "working" / f"C{N}"
out = work / "ocr" / "bin"
out.mkdir(parents=True, exist_ok=True)
cfg = json.loads((work / f"passages_C{N}.json").read_text(encoding="utf-8"))
doc = pymupdf.open(ROOT.parent / f"Cambridge IELTS {N}.pdf")
for p in cfg["passages"]:
    for idx in p["pages"]:
        pix = doc[idx].get_pixmap(dpi=450)
        im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples).convert("L")
        im = im.filter(ImageFilter.GaussianBlur(1.2)).point(lambda v: 0 if v < 140 else 255)
        im.save(out / f"p{idx:03d}.png")
