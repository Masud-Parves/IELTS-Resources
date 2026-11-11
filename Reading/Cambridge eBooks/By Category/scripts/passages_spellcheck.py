"""List words in extracted passage text that a spell checker doesn't know (to catch OCR errors
both OCR passes made the same way). Usage: python passages_spellcheck.py N
"""
import json, re, sys, pathlib
from spellchecker import SpellChecker

ROOT = pathlib.Path(__file__).resolve().parent.parent
sp = SpellChecker()
for f in sorted((ROOT / "working" / f"C{sys.argv[1]}" / "text").glob("*.json")):
    d = json.loads(f.read_text(encoding="utf-8"))
    t = " ".join([d["title"], d["subtitle"]] + [p["text"] for p in d["paras"]] + d["notes"])
    words = {w for w in re.findall(r"[A-Za-z]+(?:'[a-z]+)?", t) if not w[0].isupper() and len(w) > 2}
    bad = sorted(w for w in sp.unknown(words) if not w.endswith("'s"))
    print(f.stem, bad)
    # capitalised mid-sentence words the dictionary doesn't know (OCR "rn"->"In", "m"->"Ill"); names show up too
    caps = {m.group(1) for m in re.finditer(r"(?<=[a-z,;] )([A-Z][a-z]+)\b", t)}
    odd = sorted(w for w in sp.unknown({w.lower() for w in caps}) if len(w) > 2)
    if odd:
        print("   caps:", odd)
    for m in re.finditer(r" [,.;:)](?!\.)|\( ", t):
        print("   spacing:", t[max(0, m.start() - 25):m.end() + 10])
