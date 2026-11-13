"""Render the Reading answer-key pages of Cambridge 10-14 at 300 dpi for OCR.

Usage: python headings_render_keys.py
Reads working/C{N}/pages_C{N}.json, writes working/headings/keys/C{N}_p###.png.
"""
import json, pathlib
import pymupdf

ROOT = pathlib.Path(__file__).resolve().parent.parent
out = ROOT / "working" / "headings" / "keys"
for N in range(10, 15):
    plan = json.loads((ROOT / "working" / f"C{N}" / f"pages_C{N}.json").read_text())
    k = plan["answer_key_pages"]
    pages = k if isinstance(k, list) else [x for v in k.values() for x in (v if isinstance(v, list) else [v])]
    doc = pymupdf.open(ROOT.parent / f"Cambridge IELTS {N}.pdf")
    for idx in pages:
        png = out / f"C{N}_p{idx:03d}.png"
        doc[idx].get_pixmap(dpi=300).save(png)
        print(png.name, doc.page_count)
