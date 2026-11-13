"""Rebuild passage text (title, subtitle, paragraphs) from Windows-OCR line JSON.

Usage: python passages_extract.py N
Reads working/C{N}/passages_C{N}.json (which pages hold each passage's text) and
working/C{N}/ocr/json/p###.json; writes working/C{N}/text/T#P#.json with
{test, passage, title, subtitle, paras:[{label, text}], flags:[...]}.
Fixes that OCR can't get right go in passages_C{N}.json -> "fixes" (regex pairs per passage).
"""
import json, re, sys, pathlib, statistics
import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
N = sys.argv[1]
work = ROOT / "working" / f"C{N}"
cfg = json.loads((work / f"passages_C{N}.json").read_text(encoding="utf-8"))
(work / "text").mkdir(exist_ok=True)

RUNNING = re.compile(r"^(Reading|Test( \d)?|\d{1,3}|READING|READING PASSAGE \d)$")
LABEL = re.compile(r"^[A-L]$")


def load(idx):
    L = json.load(open(work / "ocr" / "json" / f"p{idx:03d}.json", encoding="utf-8-sig"))
    for l in L:
        l["text"] = l["text"].strip()
    return L


def page_lines(idx, first, drop_before=None, drop_after=None, drop=(), regions=()):
    L = [l for l in load(idx) if not RUNNING.match(l["text"])]
    for x0, y0, x1, y1 in regions:
        L = [l for l in L if not (x0 <= l["x"] + l["w"] / 2 <= x1 and y0 <= l["y"] + l["h"] / 2 <= y1)]
    if first:  # skip the instructions block above the passage
        cut = [l["y"] for l in L if re.search(r"Passage \d below|^Passage \d\.|^You should spend", l["text"])]
        if cut:
            L = [m for m in L if m["y"] > max(cut) + 10]
    # questions that start below the passage on the same page
    q = [l["y"] for l in L if re.match(r"^Questions? \d", l["text"])]
    if q and drop_after is None:
        drop_after = min(q) - 5
    if drop_before is not None:
        L = [l for l in L if l["y"] >= drop_before]
    if drop_after is not None:
        L = [l for l in L if l["y"] < drop_after]
    L = [l for l in L if not any(re.search(d, l["text"]) for d in list(drop) + cfg.get("drop", []))]
    return L


def order(L, pw, single=False, relabel=False):
    """Full-width lines split the page into bands; read each band left column, then right.
    single: one-column page, read top to bottom. relabel: any tiny line left of the text is a
    paragraph letter (faint letters get misread; build() renumbers them A, B, C ...)."""
    mid = pw / 2
    def kind(l):
        if single:
            return "L"
        if l["x"] < mid - 40 and l["x"] + l["w"] > mid + 40:
            return "F"
        return "L" if l["x"] + l["w"] / 2 < mid else "R"
    # OCR sometimes joins a left-column line with the right-column line beside it: split at the right column's edge
    rxs = sorted(l["x"] for l in L if l["x"] > mid - 40)
    hmed = statistics.median(l["h"] for l in L) if L else 0
    lxs = sorted(l["x"] for l in L if l["x"] < mid - 40) or [0]
    lx = lxs[len(lxs) // 5]
    if len(rxs) > 5 and not single:
        rx = rxs[len(rxs) // 2]
        for l in list(L):
            w = l["words"]
            cut = [i for i in range(1, len(w)) if abs(w[i]["x"] - rx) < 14 and w[i - 1]["x"] + w[i - 1]["w"] < rx - 4]
            if l["x"] < lx + 90 and cut and l["h"] < 1.15 * hmed:
                i = cut[0]
                mk = lambda ws: {"x": ws[0]["x"], "y": l["y"], "w": ws[-1]["x"] + ws[-1]["w"] - ws[0]["x"], "h": l["h"],
                                 "text": " ".join(x["t"] for x in ws), "words": ws}
                L[L.index(l):L.index(l) + 1] = [mk(w[:i]), mk(w[i:])]
    for l in L:
        # a small line starting with a bullet is a footnote whose star OCR read as a bullet
        if len(l["words"]) > 1 and l["words"][0]["t"] in ("•", "·") and l["h"] < 0.85 * hmed:
            l["text"] = "* " + l["text"].split(" ", 1)[1]
            l["words"] = l["words"][1:]
        # dots of a dotted box border read as text at the start of a line
        while l["words"] and l["words"][0]["t"] in (".", ":", "•", "·", ";") and len(l["words"]) > 1:
            l["words"] = l["words"][1:]
            l["x"] = l["words"][0]["x"]
            l["text"] = l["text"].split(" ", 1)[1]
        l["text"] = l["text"].replace(" • ", " ")
        l["k"] = kind(l)
    # a label letter sits left of its line, same row: merge into that line
    if relabel:
        labels = [l for l in L if l["w"] < 60 and len(l["text"]) <= 2 and l["x"] < lx - 20]
    else:
        labels = [l for l in L if LABEL.match(l["text"]) and l["w"] < 60]
    body = [l for l in L if l not in labels]
    for lab in labels:
        cands = [b for b in body if abs(b["y"] - lab["y"]) < 30 and b["x"] > lab["x"]]
        if cands:
            b = min(cands, key=lambda b: b["x"])
            b["label"] = lab["text"]
            b["x"] = min(b["x"], lab["x"])
            if b["k"] == "R" and lab["x"] + lab["w"] / 2 < mid:
                pass
    body.sort(key=lambda l: l["y"])
    out, band = [], []
    def flush():
        for side in ("L", "R"):
            col = [l for l in band if l["k"] == side]
            if col:
                out.append(("col", col))
    for l in body:
        if l["k"] == "F":
            flush(); band = []
            out.append(("col", [l]) if not out or out[-1][0] != "full" else None)
            if out[-1] is None:
                out.pop(); out[-1][1].append(l)
            else:
                out[-1] = ("full", [l])
        else:
            band.append(l)
    flush()
    return out


_img = {}
MISSED = []


def ink(idx, x0, y0, x1, y1):
    """Count dark pixels in a box of the 300 dpi page render (to spot words OCR skipped)."""
    if idx not in _img:
        _img[idx] = np.asarray(Image.open(work / "ocr" / f"p{idx:03d}.png").convert("L"))
    a = _img[idx][max(0, y0):y1, max(0, x0):x1]
    return int((a < 150).sum()) if a.size else 0


def missed(idx, ls):
    """Flag lines with ink left of the first word, between words, or right of the last word."""
    out = []
    left = sorted(l["x"] for l in ls)[len(ls) // 5]
    right = sorted(l["x"] + l["w"] for l in ls)[len(ls) * 4 // 5]
    for l in ls:
        y0, y1 = l["y"] + 6, l["y"] + l["h"] - 6
        w = l["words"]
        gaps = [] if l.get("label") else [(left - 5, w[0]["x"] - 12)]
        gaps += [(a["x"] + a["w"] + 4, b["x"] - 4) for a, b in zip(w, w[1:])]
        gaps.append((w[-1]["x"] + w[-1]["w"] + 12, right + 5))
        for g0, g1 in gaps:
            if g1 - g0 > 14 and ink(idx, g0, y0, g1, y1) > 35:
                out.append(f"p{idx} y={l['y']} x={g0}-{g1}: {l['text'][:60]}")
                break
    return out


def build(p):
    blocks = []
    for n, idx in enumerate(p["pages"]):
        opt = p.get("page_opts", {}).get(str(idx), {})
        L = page_lines(idx, n == 0, opt.get("drop_before"), opt.get("drop_after"), p.get("drop", []), opt.get("regions", []))
        A = load(idx)
        # centre of the text block (scans are not centred on the page)
        pw = min(l["x"] for l in A) + max(l["x"] + l["w"] for l in A)
        ob = order(L, pw, p.get("single", cfg.get("single", False)), p.get("relabel", False))
        for _, ls in ob:
            if len(ls) > 3:
                MISSED.extend(missed(idx, ls))
        blocks += ob
    # merge consecutive "full" blocks that are really one column (single-column layouts)
    lines = []
    for kind, ls in blocks:
        left = sorted(l["x"] for l in ls)[len(ls) // 5]
        for i, l in enumerate(ls):
            l["colstart"] = i == 0
            l["left"] = left
            lines.append(l)
    body_h = statistics.median([l["h"] for l in lines])
    # title/subtitle: leading lines taller than body text, or listed explicitly
    nt = p.get("title_lines", 0); ns = p.get("subtitle_lines", 0)
    title = p.get("title_text") or " ".join(l["text"] for l in lines[:nt])
    subtitle = " ".join(l["text"] for l in lines[nt:nt + ns])
    rest = lines[nt + ns:]
    # footnotes: small lines starting with '*' (plus their small continuation lines)
    notes, keep, in_note = [], [], False
    for l in rest:
        if l["text"][:1] in "•·" and l["h"] < 0.85 * body_h:  # footnote star read as a bullet
            l["text"] = "*" + l["text"][1:].lstrip()
        if l["text"].startswith("*") and (l["h"] < 0.85 * body_h or re.match(r"\* ?[\w ]+:", l["text"])):
            notes.append(l["text"]); in_note = True; continue
        if in_note and l["h"] < 0.85 * body_h and not l.get("label"):
            notes[-1] += " " + l["text"]; continue
        in_note = False
        keep.append(l)
    rest = keep
    if p.get("labelled"):
        for l in rest:
            w = l["words"]
            if len(w) > 1 and LABEL.match(w[0]["t"]) and w[1]["x"] - (w[0]["x"] + w[0]["w"]) > 18 and w[0]["x"] < l["left"] - 20:
                l["label"] = w[0]["t"]
                l["text"] = l["text"].split(" ", 1)[1]
    pitches = [b["y"] - a["y"] for a, b in zip(rest, rest[1:]) if 0 < b["y"] - a["y"] < 3 * body_h and not b["colstart"]]
    pitch = statistics.median(pitches)
    paras, cur, prev = [], None, None
    for l in rest:
        new = False
        indented = p.get("indent") and l["x"] > l["left"] + 35
        if cur is None or l.get("label"):
            new = True
        elif indented:
            new = True
        elif not l["colstart"] and l["y"] - prev["y"] > 1.45 * pitch:
            new = True
        elif l["colstart"] and not p.get("indent"):
            # new column/page: continue the paragraph unless the previous line ended one
            colw = max(x["w"] for x in rest)
            ended = re.search(r"[.!?:'’”)]$", prev["text"]) and prev["w"] < 0.8 * colw
            new = bool(ended)
        if new:
            cur = {"label": l.get("label", ""), "lines": []}
            paras.append(cur)
        cur["lines"].append(l["text"])
        prev = l
    flags = list(MISSED)
    MISSED.clear()
    out = []
    for para in paras:
        t = ""
        for s in para["lines"]:
            if t.endswith("-") and not t.endswith(" -"):
                flags.append(f"hyphen join: ...{t[-20:]}|{s[:20]}...")
                t += s
            else:
                t = (t + " " + s) if t else s
        if para["label"] and p.get("relabel"):
            para["label"] = "ABCDEFGHIJKL"[sum(1 for q in out if q["label"])]
        if any(t.startswith(m) for m in p.get("as_note", [])):
            notes.append("* " + t)
            continue
        if out and any(t.startswith(m) for m in p.get("merge", [])):
            out[-1]["text"] += " " + t
            continue
        # paragraph starts the layout hides (e.g. at a page break): split there
        for m in p.get("split", []):
            i = t.find(" " + m)
            if i > 0:
                head, tail = t[:i], t[i + 1:]
                if any(tail.startswith(a) for a in p.get("as_note", [])):  # footnote run into the text
                    notes.append("* " + tail.lstrip("•·* "))
                    t = head
                    continue
                out.append({"label": para["label"], "text": head})
                para = {"label": ""}
                t = tail
        out.append({"label": para["label"], "text": t})
    if p.get("labels"):  # explicit letters, one per paragraph ("·" = none), for letters OCR missed
        if len(p["labels"]) == len(out):
            for q, lab in zip(out, p["labels"]):
                q["label"] = "" if lab == "·" else lab
        else:
            flags.append(f'labels: {len(p["labels"])} given, {len(out)} paragraphs')
    full = {"test": p["test"], "passage": p["passage"], "title": title, "subtitle": subtitle, "paras": out, "notes": notes}
    def fix(t):
        for a, b in p.get("fixes", []) + cfg.get("fixes", []):
            t2 = re.sub(a, b, t)
            if t2 != t:
                used.add(a)
            t = t2
        return t
    used = set()
    full["title"], full["subtitle"] = fix(title), fix(subtitle)
    full["notes"] = [fix(n) for n in notes]
    for q in out:
        q["text"] = fix(q["text"])
    flags += [f"fix not applied: {a}" for a, _ in p.get("fixes", []) if a not in used]
    full["flags"] = flags
    return full


for p in cfg["passages"]:
    if len(sys.argv) > 2 and f'{p["test"]}{p["passage"]}' not in sys.argv[2:]:
        continue
    res = build(p)
    (work / "text" / f'{p["test"]}{p["passage"]}.json').write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f'== {p["test"]}{p["passage"]} | {res["title"]} | {res["subtitle"][:60]} | {len(res["paras"])} paras')
    for q in res["paras"]:
        print(f'   [{q["label"]}] {q["text"][:50]} ... {q["text"][-30:]}')
    for f in res["flags"]:
        print("   !", f)
