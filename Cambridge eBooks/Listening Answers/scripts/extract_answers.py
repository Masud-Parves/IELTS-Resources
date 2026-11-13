"""Read the OCR'd Listening answer keys into working/answers_<win|rapid>.json: [{book, test, q, answer}].

Each key page has two columns (questions 1-20 left, 21-40 right). Words are split into columns by x,
then each column line that starts with a question number gives one answer.
"""
import json, re, sys, pathlib
from PIL import Image
import pymupdf

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = sys.argv[1] if len(sys.argv) > 1 else "win"   # win = Windows OCR, rapid = RapidOCR
pages = json.loads((ROOT / "scripts" / "key_pages.json").read_text())
SKIP = re.compile(r"Section|Part|Questions|LISTENING|Listening|TEST|answer|Answer|Resource|explanation|score", re.I)


def num(tok):
    """Question number from an OCR token like '12', 'I2', 'IO', '11&12' (first number), else None."""
    t = tok.split("&")[0]
    if not re.fullmatch(r"[0-9IlO|]{1,2}", t) or not re.search(r"[0-9]", t + ("1" if t in ("I", "l", "IO", "Il", "lI", "II") else "")):
        return None
    t = t.replace("I", "1").replace("l", "1").replace("|", "1").replace("O", "0")
    return int(t) if t.isdigit() and 1 <= int(t) <= 40 else None


out = []
for book, plist in pages.items():
    first = 5 if book == "12" else 1          # Cambridge 12 numbers its tests 5-8
    for k, p in enumerate(plist):
        name = f"C{book}_p{p:03d}"
        W = Image.open(ROOT / "working" / "keys" / f"{name}.png").width
        lines = json.load(open(ROOT / "working" / ("keys_json" if SRC == "win" else "keys_rapid") / f"{name}.json", encoding="utf-8-sig"))
        # Prefer the PDF's own text layer when the page has one (C12's scan OCRs badly).
        pg = pymupdf.open(ROOT.parent / f"Cambridge IELTS {book}.pdf")[p - 1]
        if book in ("11", "12"):        # text layers checked: good in C11/C12, garbage in C17
            s = 300 / 72
            tl = [{"x": int(x0 * s), "y": int(y0 * s), "w": int((x1 - x0) * s), "h": int((y1 - y0) * s), "t": w}
                  for x0, y0, x1, y1, w, *_ in pg.get_text("words")]
            lines = [{"y": w["y"], "text": w["t"], "words": [w]} for w in tl]
            W = int(pg.rect.width * s)
            score = [w for w in tl if w["t"] == "If"]
            lines += [{"y": w["y"], "text": "If you score", "words": []} for w in score]
        stop_y = min([l["y"] for l in lines if re.match(r"If you score", l["text"])] or [10**9])
        # Rebuild rows from word boxes: OCR sometimes reads the bold number column as separate lines.
        words = []
        for l in lines:
            for w in l["words"]:
                if w["y"] < stop_y:
                    words.append(w)
        cols = {0: [], 1: []}
        for c in (0, 1):
            ws = sorted([w for w in words if (w["x"] < W * 0.45) == (c == 0)], key=lambda w: w["y"] + w["h"] / 2)
            rows = []
            for w in ws:
                yc = w["y"] + w["h"] / 2
                if rows and abs(yc - rows[-1][0]) < 22:
                    rows[-1][1].append(w)
                else:
                    rows.append([yc, [w]])
            cols[c] = [(int(y), sorted(r, key=lambda w: w["x"])) for y, r in rows]
        found = {}
        for c in (0, 1):
            for y, ws in sorted(cols[c], key=lambda r: r[0]):
                text = " ".join(w["t"] for w in ws)
                if SKIP.search(text) and not num(ws[0]["t"]):
                    continue
                q = num(ws[0]["t"])
                if q is None:
                    continue
                ans = " ".join(w["t"] for w in ws[1:]).strip()
                if q in found:          # OCR misread a number: keep both, flag later
                    q = q + 100
                found[q] = ans
        for q, a in sorted(found.items()):
            out.append({"book": int(book), "test": first + k, "q": q, "answer": a})
        missing = [q for q in range(1, 41) if q not in found and not any(
            re.search(r"EITHER|ANY ORDER", v or "", re.I) for v in found.values())]
        nums = sorted(found)
        print(f"C{book} T{first+k}: {len(found)} numbered lines; missing {[q for q in range(1,41) if q not in found]}")

(ROOT / "working" / f"answers_{SRC}.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
