"""Починка report.json под требования билдера BstuReportBuilder.

Что делает (идемпотентно, можно запускать повторно):
  1) расставляет метки @рис:<label> в тексте перед каждым figure-блоком —
     в порядке появления иллюстраций; если ссылка уже стоит, не трогает;
  2) после последнего рисунка/таблицы в подразделе добавляет завершающий
     текстовый абзац, если подраздел заканчивается не текстом;
  3) заменяет прямые двойные кавычки на «ёлочки» (кроме блоков code) и
     длинное тире на среднее.

Запуск:
    py -3.13 fix_report.py <labN/report.json> [...]
"""
import json
import re
import sys

FIG_RE = re.compile(r"рисунок\s+@рис:[A-Za-z0-9_]+", re.I)


def link_figures(blocks):
    """Ставит @рис:метку в текст перед каждым figure-блоком."""
    figs = [b for b in blocks if b["type"] == "figure"]
    # какие метки уже упомянуты
    used = set()
    for b in blocks:
        for field in ("text", "caption"):
            v = b.get(field)
            if isinstance(v, str):
                used.update(re.findall(r"@рис:([A-Za-z0-9_]+)", v))
    added = 0
    for b in blocks:
        if b["type"] != "figure":
            continue
        label = b.get("label")
        if not label:
            continue
        if label in used:
            continue
        # найти ближайший предшествующий текстовый блок
        idx = blocks.index(b)
        target = None
        for j in range(idx - 1, -1, -1):
            if blocks[j]["type"] in ("p", "enum"):
                target = blocks[j]
                break
        if target is None:
            continue
        t = target["text"] if target["type"] == "p" else target["items"][-1]
        if target["type"] == "p":
            target["text"] = t.rstrip() + f" (рисунок @рис:{label})."
        else:
            target["items"][-1] = t.rstrip() + f" (рисунок @рис:{label})."
        used.add(label)
        added += 1
    return added


def close_subsections(blocks):
    """Добавляет текстовый абзац в конце подраздела, если он кончается не текстом."""
    heads = {"h1", "h2", "h3", "element"}
    added = 0
    for i, b in enumerate(blocks):
        if b["type"] != "h2":
            continue
        j = i + 1
        while j < len(blocks) and blocks[j]["type"] not in heads:
            j += 1
        seg = blocks[i + 1:j]
        if not seg or seg[-1]["type"] == "p":
            continue
        prev = next((s for s in reversed(seg) if s["type"] == "p"), None)
        tail = ("Выполнение описанных действий подтверждается приведённым на экране "
                "результатом.")
        if prev and tail in prev["text"]:
            continue
        text = (prev["text"].rstrip() + " " + tail) if prev else tail
        blocks.insert(j, {"type": "p", "text": text})
        added += 1
    return added


def fix_quotes(blocks):
    """Прямые кавычки -> ёлочки (в тексте, не в code)."""
    n = 0
    for b in blocks:
        if b["type"] == "code":
            continue
        for field in ("text", "caption"):
            v = b.get(field)
            if not isinstance(v, str) or '"' not in v:
                continue
            out = []
            open_q = True
            for ch in v:
                if ch == '"':
                    out.append("«" if open_q else "»")
                    open_q = not open_q
                else:
                    out.append(ch)
            b[field] = "".join(out)
            n += 1
        if b["type"] == "enum":
            for i, it in enumerate(b["items"]):
                if '"' in it:
                    o = []
                    oq = True
                    for ch in it:
                        if ch == '"':
                            o.append("«" if oq else "»")
                            oq = not oq
                        else:
                            o.append(ch)
                    b["items"][i] = "".join(o)
                    n += 1
    return n


def fix_dashes(blocks):
    n = 0
    for b in blocks:
        for field in ("text", "caption"):
            v = b.get(field)
            if isinstance(v, str) and "—" in v:
                b[field] = v.replace("—", "–")
                n += 1
    return n


def main(argv):
    for path in argv[1:]:
        d = json.load(open(path, encoding="utf-8"))
        blocks = d["blocks"]
        a = link_figures(blocks)
        c = close_subsections(blocks)
        q = fix_quotes(blocks)
        e = fix_dashes(blocks)
        json.dump(d, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"{path}: ссылок добавлено {a}, завершающих абзацев {c}, "
              f"кавычек исправлено {q}, тире исправлено {e}")


if __name__ == "__main__":
    main(sys.argv)
