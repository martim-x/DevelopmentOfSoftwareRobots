"""Сборка отчёта билдером BstuReportBuilder на Windows без LibreOffice/poppler.

Билдер (`app`) используется как библиотека: его файлы не изменяются.
Недостающие внешние утилиты заменяются:
  * docx -> PDF   : Microsoft Word (COM), проверено на этой машине;
  * номера страниц: PyMuPDF вместо `pdfinfo`/`pdftotext`.

Порядок (как в `app build`): один проход сборки -> PDF -> номера страниц
заголовков -> патч поля оглавления в готовом docx -> PDF для контроля.

Запуск:
    py -3.13 build_report.py <report.json> <out.docx> [--check] [--single-pass]
"""
import os
import sys

BUILDER = r"C:\Users\timof\Documents\Visual Studio Code\BstuReportBuilder"
sys.path.insert(0, BUILDER)

import pymupdf  # noqa: E402
from app.checks import check  # noqa: E402
from app.model import Model  # noqa: E402
from app.render.docx_builder import DEFAULT_TEMPLATE, build  # noqa: E402
from app.render.docx_toc_patch import patch_toc_pages  # noqa: E402
from app.render.media import prune_media  # noqa: E402
from app.render.spacing import fix as fix_spacing  # noqa: E402
from app.rules import Severity  # noqa: E402
from app.toc import page_numbers  # noqa: E402

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


def page_texts(pdf_path):
    """Текст страниц PDF {номер: нормализованная строка} — замена pdftotext."""
    flat = {}
    with pymupdf.open(pdf_path) as d:
        for i, page in enumerate(d, start=1):
            flat[i] = " ".join(page.get_text().split())
    return flat


def build_one(report_path, out_path, single_pass=False):
    model = Model.load(report_path)
    entries = build(model, out_path, template=DEFAULT_TEMPLATE)
    prune_media(out_path)
    fix_spacing(out_path)

    if not single_pass:
        pdf = word_to_pdf(out_path)
        pages = page_numbers(entries, pdf, flat=page_texts(pdf))
        patch_toc_pages(out_path, pages)
        prune_media(out_path)
        fix_spacing(out_path)
        filled = len(pages)
        total = sum(1 for e in entries if e["anchor"])
        print(f"оглавление: номера страниц для {filled} из {total} заголовков")
    else:
        pages = {}

    pdf = word_to_pdf(out_path)
    print(f"pdf: {pdf} ({os.path.getsize(pdf) // 1024} КБ, "
          f"{pymupdf.open(pdf).page_count} стр.)")
    print(f"готово: {out_path} ({os.path.getsize(out_path) // 1024} КБ)")
    return model, pages


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    report_path, out_path = argv[1], argv[2]
    flags = argv[3:]
    model, _ = build_one(report_path, out_path, "--single-pass" in flags)

    if "--check" not in flags:
        return 0
    findings = check(out_path, model)
    errors = [f for f in findings if f.severity == Severity.ERROR]
    warns = [f for f in findings if f.severity == Severity.WARNING]
    for f in errors:
        print(f"ОШИБКА [{f.code}] {f.message}"
              + (f" ({f.clause})" if f.clause else ""))
    for f in warns:
        print(f"ПРЕДУПРЕЖДЕНИЕ [{f.code}] {f.message}")
    print(f"проверка: ошибок {len(errors)}, предупреждений {len(warns)}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
