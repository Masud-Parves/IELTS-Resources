"""Render the Reading pages of a Cambridge book at 300 dpi and locate the blue passage box.

Usage: python passages_render.py N
Reads working/C{N}/pages_C{N}.json, writes working/C{N}/ocr/p{idx:03d}.png and boxes.json
(per page: bbox of the light-blue passage panel in pixels, or null if none).
"""
import json, sys, pathlib
import pymupdf
import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
N = sys.argv[1]
work = ROOT / "working" / f"C{N}"
out = work / "ocr"
out.mkdir(exist_ok=True)
plan = json.loads((work / f"pages_C{N}.json").read_text())
doc = pymupdf.open(ROOT.parent / f"Cambridge IELTS {N}.pdf")

boxes = {}
for p in plan["passages"]:
    for idx in p["pages"]:
        png = out / f"p{idx:03d}.png"
        if not png.exists():
            doc[idx].get_pixmap(dpi=300).save(png)
        a = np.asarray(Image.open(png).convert("RGB")).astype(int)
        r, g, b = a[..., 0], a[..., 1], a[..., 2]
        blue = (b > 200) & (b - r > 18) & (r > 140)
        rows = np.where(blue.mean(axis=1) > 0.35)[0]
        cols = np.where(blue.mean(axis=0) > 0.20)[0]
        if len(rows) < 200 or len(cols) == 0:
            boxes[idx] = None
        else:
            boxes[idx] = [int(cols.min()), int(rows.min()), int(cols.max()), int(rows.max())]
        print(p["test"], p["passage"], idx, a.shape[1], a.shape[0], boxes[idx])
(out / "boxes.json").write_text(json.dumps(boxes, indent=1))
