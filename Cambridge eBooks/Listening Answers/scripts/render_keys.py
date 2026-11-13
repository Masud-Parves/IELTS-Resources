"""Render the 40 Listening answer-key pages (scripts/key_pages.json) at 300 dpi to working/keys/C{N}_p###.png."""
import json, pathlib, pymupdf
ROOT = pathlib.Path(__file__).resolve().parent.parent
out = ROOT / "working" / "keys"; out.mkdir(parents=True, exist_ok=True)
for n, pages in json.loads((ROOT / "scripts" / "key_pages.json").read_text()).items():
    d = pymupdf.open(ROOT.parent / f"Cambridge IELTS {n}.pdf")
    for p in pages:
        d[p - 1].get_pixmap(dpi=300, colorspace=pymupdf.csGRAY).save(out / f"C{n}_p{p:03d}.png")
print("done")
