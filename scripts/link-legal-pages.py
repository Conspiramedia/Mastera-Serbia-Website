#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
link-legal-pages.py — ссылки на юридические страницы в футер всех страниц.

Без этого o-nama / politika-privatnosti / uslovi-koriscenja остались бы
orphan-страницами: в sitemap есть, входящих ссылок нет. Для доверия
(E-E-A-T) эти ссылки должны быть на каждой странице, как принято.

Ссылки идут отдельной строкой .footer-legal между графиком работы и
абзацем о согласии на обработку данных — там же, где их ищут по привычке.

Язык ссылок берётся из <html lang> страницы, чтобы русский посетитель
не уходил на сербскую политику.

Запуск из корня проекта:
    python scripts/link-legal-pages.py
    python scripts/link-legal-pages.py --dry-run

Идемпотентен: страницы с уже готовой строкой пропускаются.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DRY = "--dry-run" in sys.argv

# Подписи и адреса по языкам. Порядок тот же, что в HTML.
LEGAL = {
    "sr": [
        ("/o-nama/", "O nama"),
        ("/politika-privatnosti/", "Politika privatnosti"),
        ("/uslovi-koriscenja/", "Uslovi korišćenja"),
    ],
    "ru": [
        ("/ru/o-nas/", "О нас"),
        ("/ru/politika-konfidencialnosti/", "Политика конфиденциальности"),
        ("/ru/usloviya-ispolzovaniya/", "Условия использования"),
    ],
    "en": [
        ("/en/about/", "About us"),
        ("/en/privacy-policy/", "Privacy Policy"),
        ("/en/terms-of-service/", "Terms of Service"),
    ],
}


def build_line(lang, indent, current_url):
    """Строка футера. Ссылка на саму себя не ставится — остаётся текстом."""
    parts = []
    for url, name in LEGAL[lang]:
        if url == current_url:
            parts.append(f'<span class="footer-legal-current">{name}</span>')
        else:
            parts.append(f'<a href="{url}" class="footer-link">{name}</a>')
    inner = ' <span aria-hidden="true">•</span> '.join(parts)
    return f'{indent}<p class="footer-legal">{inner}</p>\n'


def main():
    done = skipped = 0
    for path in sorted(ROOT.glob("**/index.html")):
        rel = path.relative_to(ROOT).as_posix()
        if ".claude" in rel or rel == "index.html":
            continue
        html = path.read_text(encoding="utf-8")
        if "footer-legal" in html:
            skipped += 1
            continue
        m = re.search(r'([ \t]*)<p class="footer-privacy">', html)
        if not m:
            skipped += 1
            continue
        lang_m = re.search(r'<html lang="(\w+)"', html)
        lang = lang_m.group(1) if lang_m else "sr"
        current = "/" + rel[: -len("index.html")]
        line = build_line(lang, m.group(1), current)
        html = html[: m.start()] + line + html[m.start():]
        if not DRY:
            path.write_text(html, encoding="utf-8")
        done += 1

    print(f"Добавлено: {done}, пропущено: {skipped}")
    if DRY:
        print("(--dry-run: файлы не изменялись)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
