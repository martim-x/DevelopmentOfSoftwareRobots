"""Сборка отчёта билдером BstuReportBuilder на Windows без LibreOffice/poppler.

Билдер (`app`) используется как библиотека: его build()/prune_media()/fix_spacing()
вызываются без изменений. Недостающие внешние утилиты заменяются:
  * docx -> PDF   : Microsoft Word (COM), уже проверено на этой машине;
  * номера страниц: PyMuPDF вместо `pdfinfo`/`pdftotext` (модуль app/toc.py
    патчится в runtime, файлы репозитория не меняются).

Запуск:
    py -3.13 build_report.py <report.json> <out.docx> [--check]
"""
import os
import re
import sys

BUILDER = r"C:\Users\timof\Documents\Visual Studio Code\BstuReportBuilder"
sys.path.insert(0, BUILDER)

import pymupdf  # noqa: E402
from app import builder as builder_mod  # noqa: E402
from app import toc as toc_mod  # noqa: E402
from app.builder import DEFAULT_TEMPLATE, build, prune_media  # noqa: E402
from app.checks import check  # noqa: E402
from app.model import Model  # noqa: E402
from app.spacing import fix as fix_spacing  # noqa: E402

PDF_FMT = 17  # wdFormatPDF


def word_to_pdf(docx_path):
    """docx -> pdf через Microsoft Word COM.

    Экспорт идёт во временный файл: Word не умеет перезаписывать PDF
    по месту (ошибка «файл доступен только для чтения»), поэтому результат
    переносится на место отдельным шагом.
    """
    import shutil
    import tempfile
    import pythoncom
    import win32com.client as win32

    out = os.path.splitext(docx_path)[0] + ".pdf"
    tmp = os.path.join(tempfile.gettempdir(),
                       "bgtu_" + os.path.basename(docx_path) + ".pdf")
    if os.path.exists(tmp):
        os.remove(tmp)
    pythoncom.CoInitialize()
    word = win32.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    try:
        doc = word.Documents.Open(os.path.abspath(docx_path), ReadOnly=True)
        try:
            # ExportAsFixedFormat надёжнее SaveAs на этой машине
            doc.ExportAsFixedFormat(tmp, PDF_FMT)
        finally:
            doc.Close(False)
    finally:
        word.Quit()
    if not os.path.exists(tmp):
        raise RuntimeError(f"Word не создал PDF для {docx_path}")
    shutil.copyfile(tmp, out)
    os.remove(tmp)
    return out


def _pdf_total_pages(pdf_path):
    with pymupdf.open(pdf_path) as d:
        return d.page_count


def _page_texts(pdf_path):
    flat = {}
    with pymupdf.open(pdf_path) as d:
        for i, page in enumerate(d, start=1):
            flat[i] = " ".join(page.get_text().split())
    return flat


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    report_path, out_path = argv[1], argv[2]
    do_check = "--check" in argv[3:]

    # подмена внешних утилит в модуле app.toc (файлы репозитория не меняются)
    toc_mod.pdf_total_pages = _pdf_total_pages
    toc_mod.page_texts = _page_texts

    model = Model.load(report_path)
    template = DEFAULT_TEMPLATE

    # проход 1 — вёрстка без номеров страниц
    entries = build(model, out_path, template=template)
    prune_media(out_path)
    fixed = fix_spacing(out_path)

    # PDF для второго прохода
    pdf = word_to_pdf(out_path)
    pages = toc_mod.page_numbers(entries, pdf)

    # проход 2 — оглавление с номерами страниц
    entries = build(model, out_path, pages=pages, template=template)
    prune_media(out_path)
    fixed = fix_spacing(out_path)

    filled = len(pages)
    total = sum(1 for e in entries if e["anchor"])
    print(f"оглавление: номера страниц для {filled} из {total} заголовков")
    print(f"готово: {out_path} ({os.path.getsize(out_path) // 1024} КБ), "
          f"стыков исправлено: {fixed}")
    print(f"pdf: {pdf} ({os.path.getsize(pdf) // 1024} КБ)")

    if do_check:
        errors = check(out_path, model)
        return 1 if errors else 0
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
