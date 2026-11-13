"""Merge the two OCR readings (+ scripts/overrides.json) into working/answers.json and list disagreements.

Each answer is classified: letter (A-K), number (digits, times, prices, codes), or words.
"""
import json, re, pathlib
from collections import defaultdict
from spellchecker import SpellChecker
SP = SpellChecker()
ROOT = pathlib.Path(__file__).resolve().parent.parent
W = ROOT / "working"
CYR = str.maketrans("АВСЕНКМОРТХаеосрх", "ABCEHKMOPTXaeocpx")


def norm(a):
    a = (a or "").translate(CYR).replace("’", "'").replace("—", "-").replace("–", "-")
    a = re.sub(r"\s*/\s*", " / ", a)
    a = re.sub(r"\(\s*", "(", re.sub(r"\s*\)", ")", a))
    return re.sub(r"\s+", " ", a).strip(" .,;:")


def kind(a):
    if not a or re.search(r"EITHER|ANY ORDER", a, re.I):
        return "skip"
    if re.fullmatch(r"[A-KIi1l|]|[A-K]\s*[,&]?\s*[A-K]", a):
        return "letter"
    if not re.search(r"[A-Za-z]{2}", a) or re.fullmatch(r"[\d\s.:/£$%,-]*(am|pm|a\.m\.|p\.m\.|km|kg|cm|m|th|st|nd|rd)?", a, re.I):
        return "number"
    return "words"


def known_share(a):
    ws = re.findall(r"[A-Za-z]{2,}", a)
    return sum(1 for w in ws if not SP.unknown([w.lower()])) / max(1, len(ws))


def load(src):
    d = defaultdict(dict)
    for r in json.loads((W / f"answers_{src}.json").read_text(encoding="utf-8")):
        if r["q"] <= 40:
            d[(r["book"], r["test"])][r["q"]] = norm(r["answer"])
    return d


win, rap = load("win"), load("rapid")
ov = json.loads((ROOT / "scripts" / "overrides.json").read_text(encoding="utf-8"))   # fixes checked by eye
out, review = [], []
for key in sorted(set(win) | set(rap)):
    for q in range(1, 41):
        a, b = win[key].get(q, ""), rap[key].get(q, "")
        tag = f"C{key[0]} T{key[1]} Q{q}"
        if tag in ov:
            ans = ov[tag]
        elif a == b or kind(b) in ("skip", "letter") and kind(a) == "words" and not b:
            ans = a
        elif kind(a) == "words" and kind(b) == "words" and a.lower() != b.lower():
            if a.replace(" ", "").lower() == b.replace(" ", "").lower():
                ans = a                      # RapidOCR often loses spaces
            else:
                ans = b if known_share(b) > known_share(a) else a
                review.append(f"{tag}: win={a!r} rapid={b!r} -> {ans!r}")
        else:
            # one side empty or a letter: keep the side that has words, else win's reading
            ans = a if kind(a) == "words" else b if kind(b) == "words" else (a or b)
            if kind(a) != kind(b) and "words" in (kind(a), kind(b)):
                review.append(f"{tag}: win={a!r} rapid={b!r}")
        out.append({"book": key[0], "test": key[1], "q": q, "answer": ans, "kind": kind(ans)})
(W / "answers.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
print(len(review), "to review")
print("\n".join(review))
