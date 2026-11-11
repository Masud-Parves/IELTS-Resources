"""Re-read hard pages: RapidOCR (better letters) on each word Windows OCR found (better spacing).

Usage: python ocr_hybrid.py N page [page ...]
Needs `pip install rapidocr-onnxruntime`. Each word box in working/C{N}/ocr/json/p###.json is re-read with
RapidOCR on its own. The Windows word is kept when the spell checker knows it; otherwise RapidOCR's
reading is used. The old JSON is kept as p###_win.json.
"""
import json, re, sys, pathlib
import numpy as np
from PIL import Image
from rapidocr_onnxruntime import RapidOCR
from spellchecker import SpellChecker

ROOT = pathlib.Path(__file__).resolve().parent.parent
N = sys.argv[1]
ocr = ROOT / "working" / f"C{N}" / "ocr"
eng, sp = RapidOCR(), SpellChecker()


def known(w):
    """True for dictionary words (ignoring edge punctuation), the words a/I, and plain numbers."""
    core = re.sub(r"^[^A-Za-z]+|[^A-Za-z]+$", "", w)
    if not core:
        return bool(re.fullmatch(r"[\d.,;:()'’%£$–-]+", w))
    if len(core) == 1:
        return core in "aAI"
    return all(word_ok(p) for p in core.lower().split("-") if p)


def word_ok(w):
    """Dictionary word, allowing British spellings (behaviour, organise, centre, analyse)."""
    w = re.sub(r"'s$", "", w)
    forms = {w, re.sub(r"our", "or", w), re.sub(r"is(e|ed|es|ing|ation)$", r"iz", w),
             re.sub(r"tre(s?)$", r"ter", w), re.sub(r"yse(d?|s?)$", r"yze", w), w.replace("ll", "l")}
    return any(not sp.unknown([x]) for x in forms)


for pg in sys.argv[2:]:
    jf = ocr / "json" / f"p{int(pg):03d}.json"
    keep = ocr / "json" / f"p{int(pg):03d}_win.json"
    if not keep.exists():
        jf.rename(keep)
    L = json.load(open(keep, encoding="utf-8-sig"))
    im = Image.open(ocr / f"p{int(pg):03d}.png").convert("RGB")
    g = im.convert("L")
    for l in L:
        if len(l["text"]) < 4:
            continue
        out = []
        for w in l["words"]:
            # one word, on a white margin (the recogniser drops letters at a crop's edge)
            box = g.crop((w["x"] - 4, l["y"] - 8, w["x"] + w["w"] + 4, l["y"] + l["h"] + 8))
            pad = Image.new("L", (box.width + 60, box.height + 30), 255)
            pad.paste(box, (30, 15))
            res, _ = eng(np.asarray(pad.convert("RGB")), use_det=False, use_cls=False)
            rap = (res[0][0] if res and res[0][0] else "").replace(" ", "").replace("，", ",").replace("：", ":")
            # Windows word if the dictionary knows it (or it is a number); else RapidOCR's
            if known(w["t"]) or not rap:
                t = w["t"]
            elif known(rap) or re.search(r"[A-Za-z]{2}", rap):
                t = rap
            else:
                t = w["t"]
            if t != w["t"]:
                out.append(f"{w['t']}>{t}")
            w["t"] = t
        new = " ".join(w["t"] for w in l["words"])
        print(f"{l['y']:5d} {new[:80]}\n        {' '.join(out)[:110]}")
        l["text"] = new
    json.dump(L, open(jf, "w", encoding="utf-8"), ensure_ascii=False)
