#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
remove-visible-breadcrumbs.py — убирает видимый блок хлебных крошек.

Зачем: полоса «Početna / Novi Sad / Liman» над заголовком спорила с
дизайном — сайт строится на крупном hero-экране, и мелкая служебная
строка перед ним ломала картинку.

Что остаётся: JSON-LD BreadcrumbList в <head>. Именно он рисует путь
в сниппете Google вместо голого URL:

    pravimajstor.rs › Početna › Novi Sad › Liman

Google рекомендует, чтобы разметка соответствовала видимому содержимому,
но крошки в выдаче работают и без видимого блока — это рекомендация,
а не требование. Весь SEO-смысл задачи сохраняется.

Что теряется: навигация к родительской странице внутри самой страницы.
На районных лендингах это была единственная прямая ссылка на городскую
страницу услуги, но у каждого из них 11–12 входящих ссылок из других
мест, так что перелинковка не рушится.

Запуск из корня проекта:
    python scripts/remove-visible-breadcrumbs.py
    python scripts/remove-visible-breadcrumbs.py --dry-run

Идемпотентен: страницы без блока пропускаются.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DRY = "--dry-run" in sys.argv

# Блок целиком, вместе с отступом и переводом строки после него.
NAV_RE = re.compile(
    r'[ \t]*<nav class="breadcrumb".*?</nav>\n(?:[ \t]*\n)?',
    re.S,
)


def main():
    removed = skipped = 0
    for path in sorted(ROOT.glob("**/index.html")):
        rel = path.relative_to(ROOT).as_posix()
        if ".claude" in rel:
            continue
        html = path.read_text(encoding="utf-8")
        new_html, n = NAV_RE.subn("", html)
        if not n:
            skipped += 1
            continue
        if n > 1:
            print(f"  ! {rel}: блоков {n} (ожидался один)")
        if not DRY:
            path.write_text(new_html, encoding="utf-8")
        removed += 1
        print(f"  ✓ {rel}")

    print(f"\nУбрано: {removed}, без изменений: {skipped}")
    if DRY:
        print("(--dry-run: файлы не изменялись)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
