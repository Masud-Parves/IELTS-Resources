"""Stack thin full-width strips of 300 dpi page renders into one image for proofreading.

Usage: python strips.py N out.png page:y [page:y ...]
"""
import sys, pathlib
from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parent.parent
N, out = sys.argv[1], sys.argv[2]
strips = []
for spec in sys.argv[3:]:
    pg, y = map(int, spec.split(":"))
    im = Image.open(ROOT / "working" / f"C{N}" / "ocr" / f"p{pg:03d}.png").convert("RGB")
    s = im.crop((0, y - 8, im.width, y + 58))
    ImageDraw.Draw(s).text((2, 2), spec, fill=(255, 0, 0))
    strips.append(s)
W = max(s.width for s in strips)
canvas = Image.new("RGB", (W, sum(s.height for s in strips)), "white")
y = 0
for s in strips:
    canvas.paste(s, (0, y)); y += s.height
canvas.save(out)
