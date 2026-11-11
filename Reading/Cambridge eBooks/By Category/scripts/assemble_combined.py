"""Merge Cambridge 10-14 Reading pages into ONE category-wise PDF (original pages, cropped and scaled).

Usage: python assemble_combined.py
Output: Output/Cambridge_10-14_Reading_By_Category_Combined.pdf
"""
import json
from pathlib import Path

import fitz
from assemble_pages import ROOT, EBOOKS, A4_W, A4_H, content_rect, M

BOOKS = [10, 11, 12, 13, 14]
CANON = ["Environment & Nature", "Psychology, Health & Human Behaviour",
         "Technology, Transport & Engineering", "Animals & Biology", "Arts, Culture & Media",
         "History & Archaeology", "Education & Language", "Business, Economics & Work",
         "Science & Discovery"]


def main():
    items, srcs, keys = [], {}, {}
    for n in BOOKS:
        plan = json.load(open(ROOT / "plans" / f"plan_C{n}.json", encoding="utf-8"))
        pj = json.load(open(ROOT / "working" / f"C{n}" / f"pages_C{n}.json", encoding="utf-8"))
        pg = {(p["test"], p["passage"]): p["pages"] for p in pj["passages"]}
        ak = pj.get("answer_key_pages", [])
        if isinstance(ak, dict):
            ak = [x for v in ak.values() for x in (v if isinstance(v, list) else [v])]
        keys[n] = ak
        srcs[n] = fitz.open(EBOOKS / f"Cambridge IELTS {n}.pdf")
        for e in plan:
            items.append(dict(book=n, **e, pages=pg[(e["test"], e["passage"])]))
    items.sort(key=lambda e: (CANON.index(e["category"]), e["book"], e["test"], e["passage"]))

    out = fitz.open()

    def text_pages(title, lines, size=11):
        pg, y = None, 0
        for text, bold in lines:
            if pg is None or y > A4_H - 50:
                pg = out.new_page(width=A4_W, height=A4_H)
                pg.insert_textbox(fitz.Rect(40, 30, A4_W - 40, 90), title, fontsize=20, fontname="hebo", align=1)
                y = 110
            pg.insert_text((50, y), text, fontsize=size, fontname="hebo" if bold else "helv")
            y += size + 7

    def add_src(n, i):
        p = srcs[n][i]
        r = content_rect(p)
        s = min((A4_W - 2 * M) / r.width, (A4_H - 2 * M) / r.height)
        w, h = r.width * s, r.height * s
        pg = out.new_page(width=A4_W, height=A4_H)
        x0, y0 = (A4_W - w) / 2, (A4_H - h) / 2
        pg.show_pdf_page(fitz.Rect(x0, y0, x0 + w, y0 + h), srcs[n], i, clip=r)

    lines, cat = [], None
    for e in items:
        if e["category"] != cat:
            cat = e["category"]
            lines.append((cat, True))
        lines.append((f"    {e['title']}  (Cambridge {e['book']}, {e['test']} {e['passage']})", False))
    text_pages("Cambridge IELTS 10-14\nReading by Category", lines)

    cat = None
    for e in items:
        if e["category"] != cat:
            cat = e["category"]
            c = sum(1 for x in items if x["category"] == cat)
            pg = out.new_page(width=A4_W, height=A4_H)
            pg.insert_textbox(fitz.Rect(40, 300, A4_W - 40, 400), cat, fontsize=26, fontname="hebo", align=1)
            pg.insert_textbox(fitz.Rect(40, 410, A4_W - 40, 440), f"{c} passages", fontsize=14, fontname="helv", align=1)
        pg = out.new_page(width=A4_W, height=A4_H)
        pg.insert_textbox(fitz.Rect(40, 380, A4_W - 40, 460),
                          f"{e['title']}\nCambridge {e['book']}, {e['test']} {e['passage']}",
                          fontsize=16, fontname="hebo", align=1)
        for i in e["pages"]:
            add_src(e["book"], i)

    pg = out.new_page(width=A4_W, height=A4_H)
    pg.insert_textbox(fitz.Rect(40, 380, A4_W - 40, 460), "Answer Keys\nBooks 10-14", fontsize=24, fontname="hebo", align=1)
    for n in BOOKS:
        for i in keys[n]:
            add_src(n, i)

    dest = ROOT / "Output" / "Cambridge_10-14_Reading_By_Category_Combined.pdf"
    out.save(dest, garbage=3, deflate=True)
    print(dest, out.page_count, "pages")


if __name__ == "__main__":
    main()
