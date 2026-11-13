import sys
import fitz
from PIL import Image, ImageDraw, ImageFont

def make_sheets(pdf_path, out_dir, start, end, per_sheet=12, cols=3, thumb_w=260):
    doc = fitz.open(pdf_path)
    end = min(end, doc.page_count)
    pages = list(range(start, end))
    rows = (per_sheet + cols - 1) // cols
    for s in range(0, len(pages), per_sheet):
        chunk = pages[s:s+per_sheet]
        thumbs = []
        for p in chunk:
            pix = doc[p].get_pixmap(dpi=90)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            ratio = thumb_w / img.width
            img = img.resize((thumb_w, int(img.height*ratio)))
            thumbs.append((p, img))
        th = thumbs[0][1].height
        sheet = Image.new("RGB", (cols*thumb_w + (cols+1)*10, rows*(th+24) + 10), "white")
        draw = ImageDraw.Draw(sheet)
        for i, (p, img) in enumerate(thumbs):
            cx = (i % cols) * (thumb_w+10) + 10
            cy = (i // cols) * (th+24) + 10
            sheet.paste(img, (cx, cy))
            draw.text((cx, cy+th+2), f"page idx {p} (pdf page {p+1})", fill="red")
        name = f"{out_dir}/sheet_{chunk[0]:03d}-{chunk[-1]:03d}.png"
        sheet.save(name)
        print("saved", name)

if __name__ == "__main__":
    pdf_path, out_dir, start, end = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    make_sheets(pdf_path, out_dir, start, end)
