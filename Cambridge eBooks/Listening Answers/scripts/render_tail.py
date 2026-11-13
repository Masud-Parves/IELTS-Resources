"""Render the last K pages of each Cambridge book (to find the answer keys). Usage: python render_tail.py K DPI [books...]"""
import sys, pathlib, pymupdf
ROOT = pathlib.Path(__file__).resolve().parent.parent
K, DPI = int(sys.argv[1]), int(sys.argv[2])
books = sys.argv[3:] or [str(n) for n in range(10, 20)]
for n in books:
    d = pymupdf.open(ROOT.parent / f"Cambridge IELTS {n}.pdf")
    out = ROOT / "working" / f"C{n}" / f"tail{DPI}"
    out.mkdir(parents=True, exist_ok=True)
    for i in range(max(0, len(d) - K), len(d)):
        d[i].get_pixmap(dpi=DPI, colorspace=pymupdf.csGRAY).save(out / f"p{i+1:03d}.png")
    print(n, len(d))
