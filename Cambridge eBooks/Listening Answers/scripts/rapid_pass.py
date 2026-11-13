"""Second OCR pass with RapidOCR over the 40 key pages -> working/keys_rapid/<name>.json (same format as winocr.ps1)."""
import json, pathlib
from rapidocr_onnxruntime import RapidOCR
ROOT = pathlib.Path(__file__).resolve().parent.parent
src, out = ROOT / "working" / "keys", ROOT / "working" / "keys_rapid"
out.mkdir(exist_ok=True)
eng = RapidOCR()
for png in sorted(src.glob("*.png")):
    res, _ = eng(str(png))
    lines = []
    for box, text, _conf in res or []:
        xs, ys = [p[0] for p in box], [p[1] for p in box]
        x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
        parts = text.split()
        n = max(1, len(text))
        words, pos = [], 0
        for part in parts:            # spread the words over the box in proportion to their length
            i = text.index(part, pos); pos = i + len(part)
            words.append({"x": int(x0 + (x1 - x0) * i / n), "y": int(y0), "w": int((x1 - x0) * len(part) / n),
                          "h": int(y1 - y0), "t": part})
        lines.append({"x": int(x0), "y": int(y0), "w": int(x1 - x0), "h": int(y1 - y0), "text": text, "words": words})
    (out / f"{png.stem}.json").write_text(json.dumps(lines, ensure_ascii=False), encoding="utf-8")
    print(png.stem, len(lines))
