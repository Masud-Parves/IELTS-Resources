"""Straighten curved / tilted text lines on a scanned page (photocopies of a bent book).

Usage: python dewarp.py N page [page ...]
For each page, working/C{N}/ocr/p###.png is kept as p###_orig.png and replaced by a version in
which every vertical strip is shifted up/down so its text rows line up with the centre strip
(shift measured per strip and per horizontal zone, then smoothed). Only vertical shifts, so
OCR coordinates stay close to the original. Re-run winocr.ps1 on the page afterwards.
"""
import sys, pathlib
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates, gaussian_filter, gaussian_filter1d

ROOT = pathlib.Path(__file__).resolve().parent.parent
N = sys.argv[1]
ocr = ROOT / "working" / f"C{N}" / "ocr"
BAND, ZONE, MAXS = 80, 360, 60


def shifts(a):
    """Vertical shift of each band (columns) in each zone (rows), relative to the centre band."""
    ink = 255.0 - a
    H, W = a.shape
    cols = np.where(ink.mean(axis=0) > 6)[0]
    x0, x1 = cols.min(), cols.max()
    xs = np.arange(x0 + BAND // 2, x1 - BAND // 2, BAND)
    ys = np.arange(ZONE // 2, H - ZONE // 2, ZONE // 2)
    prof = np.stack([gaussian_filter1d(ink[:, x - BAND // 2:x + BAND // 2].mean(axis=1), 2) for x in xs])
    S = np.zeros((len(ys), len(xs)))
    c = len(xs) // 2
    for i, y in enumerate(ys):
        lo, hi = y - ZONE // 2, y + ZONE // 2
        # chain neighbouring bands outward from the centre (neighbours look alike even when far bands don't)
        for rng in (range(c + 1, len(xs)), range(c - 1, -1, -1)):
            for j in rng:
                k = j - 1 if j > c else j + 1
                ref = prof[k, lo:hi] - prof[k, lo:hi].mean()
                best, bs = -1e18, 0
                for s in range(-12, 13):
                    seg = prof[j, max(0, lo + s):hi + s]
                    if len(seg) != len(ref):
                        continue
                    v = float(((seg - seg.mean()) * ref).sum())
                    if v > best:
                        best, bs = v, s
                S[i, j] = np.clip(S[i, k] + bs, -MAXS, MAXS)
    return xs, ys, gaussian_filter(S, (1, 1.5))


for pg in sys.argv[2:]:
    src = ocr / f"p{int(pg):03d}.png"
    orig = ocr / f"p{int(pg):03d}_orig.png"
    if not orig.exists():
        src.rename(orig)
    a = np.asarray(Image.open(orig).convert("L")).astype(float)
    xs, ys, S = shifts(a)
    H, W = a.shape
    # interpolate the shift grid to every pixel
    yy, xx = np.mgrid[0:H, 0:W]
    gy = np.interp(np.arange(H), ys, np.arange(len(ys)))
    gx = np.interp(np.arange(W), xs, np.arange(len(xs)))
    field = map_coordinates(S, [np.repeat(gy[:, None], W, 1), np.repeat(gx[None, :], H, 0)], order=1, mode="nearest")
    out = map_coordinates(a, [yy + field, xx], order=1, mode="constant", cval=255)
    Image.fromarray(out.clip(0, 255).astype(np.uint8)).save(src)
    print(pg, "max shift", float(np.abs(S).max()))
