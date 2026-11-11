"""Reorder original Cambridge Reading pages by category into one PDF per book.

Usage: python assemble_pages.py 10
Inputs : plans/plan_C{N}.json, working/C{N}/pages_C{N}.json, ../Cambridge IELTS {N}.pdf
Output : Output/Cambridge_{N}_Reading_By_Category.pdf
No text is retyped: original scanned pages are cropped to their content and scaled up to fill A4.
"""
import json
import sys
from pathlib import Path

import fitz
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
EBOOKS = ROOT.parent
A4_W, A4_H = 595, 842
M = 22  # page margin in points after scaling


def content_rect(page):
    pix = page.get_pixmap(dpi=60, colorspace=fitz.csGRAY)
    img = Image.frombytes("L", (pix.width, pix.height), pix.samples)
    bb = img.point(lambda v: 255 if v < 170 else 0).getbbox()
    if not bb:
        return page.rect
    sx, sy = page.rect.width / pix.width, page.rect.height / pix.height
    pad = 6
    return fitz.Rect(max(0, bb[0] * sx - pad), max(0, bb[1] * sy - pad),
                     min(page.rect.width, bb[2] * sx + pad), min(page.rect.height, bb[3] * sy + pad))


def add_text_page(out, title, lines, size=14):
    pg = out.new_page(width=A4_W, height=A4_H)
    pg.insert_textbox(fitz.Rect(40, 40, A4_W - 40, 110), title, fontsize=24, fontname="hebo", align=1)
    y = 130
    for text, bold in lines:
        pg.insert_text((50, y), text, fontsize=size, fontname="hebo" if bold else "helv")
        y += size + 8
    return pg


def build(n):
    plan = json.load(open(ROOT / "plans" / f"plan_C{n}.json", encoding="utf-8"))
    pages = json.load(open(ROOT / "working" / f"C{n}" / f"pages_C{n}.json", encoding="utf-8"))
    by_key = {(p["test"], p["passage"]): p["pages"] for p in pages["passages"]}
    src = fitz.open(EBOOKS / f"Cambridge IELTS {n}.pdf")
    out = fitz.open()

    lines = []
    cat = None
    for e in plan:
        if e["category"] != cat:
            cat = e["category"]
            lines.append((cat, True))
        lines.append((f"    {e['title']}  ({e['test']} {e['passage']})", False))
    add_text_page(out, f"Cambridge IELTS {n}\nReading by Category", lines, size=11)

    def add_src(i):
        p = src[i]
        r = content_rect(p)
        s = min((A4_W - 2 * M) / r.width, (A4_H - 2 * M) / r.height)
        w, h = r.width * s, r.height * s
        pg = out.new_page(width=A4_W, height=A4_H)
        x0, y0 = (A4_W - w) / 2, (A4_H - h) / 2
        pg.show_pdf_page(fitz.Rect(x0, y0, x0 + w, y0 + h), src, i, clip=r)

    cat = None
    for e in plan:
        if e["category"] != cat:
            cat = e["category"]
            n_in = sum(1 for x in plan if x["category"] == cat)
            add_text_page(out, cat, [(f"{n_in} passage(s)", False)])
        for i in by_key[(e["test"], e["passage"])]:
            add_src(i)

    add_text_page(out, "Answer Key", [("Reading answer keys from the original book follow.", False)])
    ak = pages.get("answer_key_pages", [])
    if isinstance(ak, dict):
        ak = [x for v in ak.values() for x in (v if isinstance(v, list) else [v])]
    for i in ak:
        add_src(i)

    dest = ROOT / "Output" / f"Cambridge_{n}_Reading_By_Category.pdf"
    out.save(dest, garbage=3, deflate=True)
    print(dest, out.page_count, "pages")


if __name__ == "__main__":
    build(int(sys.argv[1]))
