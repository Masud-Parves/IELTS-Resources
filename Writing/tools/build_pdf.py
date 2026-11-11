"""Build an IELTS Writing Task 2 topic PDF from a Markdown source file.

Usage:
    python tools/build_pdf.py source/02_Technology.md Output/T2_02_Technology_Idea_Bank.pdf

Pipeline: Markdown -> HTML (with tools/style.css) -> headless Chrome/Edge -> PDF.
Chrome is used (not ReportLab) because it shapes Bangla script correctly
(juktakkhor and vowel signs). Raw HTML blocks such as <div class="bn" markdown="1">
are allowed in the source.
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import markdown

TOOLS = Path(__file__).resolve().parent
BROWSERS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]


def find_browser():
    for b in BROWSERS:
        if os.path.exists(b):
            return b
    sys.exit("No Chrome or Edge found. Install one, or add its path to BROWSERS.")


def md_to_html(src: Path) -> str:
    text = src.read_text(encoding="utf-8")
    body = markdown.markdown(text, extensions=["tables", "attr_list", "md_in_html", "sane_lists", "fenced_code"])
    css = (TOOLS / "style.css").read_text(encoding="utf-8")
    title = src.stem.replace("_", " ")
    return (
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        f"<title>{title}</title><style>{css}</style></head><body>{body}</body></html>"
    )


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    src, out = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    html = md_to_html(src)
    with tempfile.TemporaryDirectory() as tmp:
        html_path = Path(tmp) / "page.html"
        html_path.write_text(html, encoding="utf-8")
        cmd = [
            find_browser(), "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
            f"--user-data-dir={Path(tmp) / 'profile'}",
            f"--print-to-pdf={out}", html_path.as_uri(),
        ]
        subprocess.run(cmd, check=True, capture_output=True, timeout=180)
    if not out.exists():
        sys.exit("PDF was not created.")
    print(f"Built {out} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
