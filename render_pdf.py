"""Рендер страниц PDF в PNG + контактный лист (для визуальной проверки вёрстки).

Запуск:
    py -3.13 render_pdf.py <lab.pdf> <каталог_для_png> [dpi] [cols]
"""
import os
import sys

import pymupdf
from PIL import Image


def render(pdf_path, out_dir, dpi=90, cols=3, width=460):
    os.makedirs(out_dir, exist_ok=True)
    doc = pymupdf.open(pdf_path)
    pages = []
    for i, page in enumerate(doc, 1):
        pix = page.get_pixmap(dpi=dpi)
        p = os.path.join(out_dir, f"p{i:02d}.png")
        pix.save(p)
        pages.append(p)
    ims = [Image.open(p).convert("RGB") for p in pages]
    th = [im.resize((width, int(im.size[1] * width / im.size[0])), Image.LANCZOS)
          for im in ims]
    rows = (len(th) + cols - 1) // cols
    row_h = [max(th[r * cols + j].size[1] for j in range(cols)
                 if r * cols + j < len(th)) for r in range(rows)]
    H = sum(row_h) + rows * 8 + 8
    sheet = Image.new("RGB", (cols * (width + 8) + 8, H), "white")
    y = 8
    for r in range(rows):
        x = 8
        for im in th[r * cols:(r + 1) * cols]:
            sheet.paste(im, (x, y))
            x += width + 8
        y += row_h[r] + 8
    sheet_path = os.path.join(out_dir, "sheet.png")
    sheet.save(sheet_path)
    print(f"страниц: {doc.page_count}")
    print(f"png: {out_dir}")
    print(f"контактный лист: {sheet_path} {sheet.size}")
    return doc.page_count


if __name__ == "__main__":
    pdf = sys.argv[1]
    out = sys.argv[2]
    dpi = int(sys.argv[3]) if len(sys.argv) > 3 else 90
    cols = int(sys.argv[4]) if len(sys.argv) > 4 else 3
    render(pdf, out, dpi, cols)
