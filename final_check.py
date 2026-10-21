"""Финальный контроль собранных отчётов: ссылки на рисунки, кавычки, тире,
дубли, структура. Печатает сводку по каждой лабе.

Запуск:
    py -3.13 final_check.py <labN.docx> [<labN.docx> ...]
"""
import collections
import os
import re
import sys

import docx

FIG_RE = re.compile(r"Рисунок (\d+\.\d+)")
CAP_RE = re.compile(r"^Рисунок \d+\.\d+ – ")


def check(path):
    d = docx.Document(path)
    ps = d.paragraphs
    name = os.path.basename(path)

    caps, texts = [], []
    for p in ps:
        t = p.text.strip()
        if not t:
            continue
        texts.append(t)
        if p.style is not None and p.style.name == "Рисунок":
            caps.append(t)

    nums = [FIG_RE.match(c).group(1) for c in caps if FIG_RE.match(c)]
    dup_nums = {k: v for k, v in collections.Counter(nums).items() if v > 1}
    bad_cap = [c for c in caps if not CAP_RE.match(c)]

    # ссылка на каждый рисунок должна встречаться в тексте ДО подписи
    refs = collections.Counter()
    for t in texts:
        if t in caps:
            continue
        for m in re.finditer(r"рисун[а-яё]*\s+(\d+\.\d+)", t, re.I):
            refs[m.group(1)] += 1
    no_ref = [n for n in nums if refs.get(n, 0) == 0]

    body = "\n".join(texts)
    straight = body.count('"')
    emdash = body.count("—")
    quotes_ok = body.count("«"), body.count("»")
    dups = {k: v for k, v in collections.Counter(texts).items() if v > 1}

    print(f"=== {name} ===")
    print(f"  абзацев: {len(ps)}, рисунков в документе: {len(d.inline_shapes)}, "
          f"подписей: {len(caps)}")
    print(f"  разделов: {sum(1 for p in ps if p.style and p.style.name == 'Раздел')}, "
          f"подразделов: {sum(1 for p in ps if p.style and p.style.name == 'Подраздел')}, "
          f"элементов: {sum(1 for p in ps if p.style and p.style.name == 'Заголовок элемента')}")
    print(f"  дублей номеров рисунков: {dup_nums if dup_nums else 'нет'}")
    print(f"  подписей неверного формата: {len(bad_cap)}")
    print(f"  рисунков без ссылки в тексте: {no_ref if no_ref else 'нет'}")
    print(f"  прямых кавычек: {straight} | ёлочек: {quotes_ok[0]}/{quotes_ok[1]} | "
          f"длинных тире: {emdash}")
    print(f"  дублирующихся абзацев: {len(dups)}")
    for k in list(dups)[:3]:
        print(f"     - {k[:80]}")
    ok = (not dup_nums and not bad_cap and not no_ref and straight == 0
          and emdash == 0 and quotes_ok[0] == quotes_ok[1])
    print(f"  ИТОГ: {'ЧИСТО' if ok else 'ЕСТЬ ЗАМЕЧАНИЯ'}")
    return ok


if __name__ == "__main__":
    allok = all(check(p) for p in sys.argv[1:])
    print("\nВСЕ ОТЧЁТЫ ЧИСТЫЕ" if allok else "\nЕСТЬ ЗАМЕЧАНИЯ — см. выше")
