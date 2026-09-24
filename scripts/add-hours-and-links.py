#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
add-hours-and-links.py — часы работы в футер и ссылка на прайс в текст услуги.

Две правки за один проход:

  1. Часы работы. Строка «Radno vreme: 08:00–23:00, svakog dana» вставляется
     в футер перед абзацем .footer-privacy. Раньше график жил только в
     JSON-LD (openingHours) — робот его видел, живой человек нет. Google
     сверяет разметку с содержимым страницы, поэтому график должен быть
     и текстом тоже.

     Значение совпадает с config.quiet_hours бота и с openingHours в схеме:
     08:00–23:00 без выходных.

  2. Контекстная ссылка на прайс — только для 9 хабовых страниц
     (/sr/, /ru/, /en/ и их города + разделы «для мастеров»).

     На 108 сервисных лендингах такая ссылка уже есть — «Pogledaj ceo
     cenovnik →» под таблицей цен. Вторая ссылка на тот же URL рядом
     размывала бы анкор, поэтому те страницы не трогаем.

     У хабов же блока цен нет вовсе, и на прайс они ссылались только из
     футера — там ссылка весит мало. Добавляем предложение после блока
     услуг, с осмысленным анкором, а не «кликните здесь».

Запуск из корня проекта:
    python scripts/add-hours-and-links.py
    python scripts/add-hours-and-links.py --dry-run

Скрипт идемпотентен: уже обработанные страницы пропускаются.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DRY = "--dry-run" in sys.argv

# ── Часы работы по языкам ──────────────────────────────────────────
# Тире — типографское (–), как в остальных текстах сайта.
HOURS = {
    "sr": "Radno vreme: 08:00–23:00, svakog dana",
    "ru": "Режим работы: 08:00–23:00, ежедневно",
    "en": "Working hours: 08:00–23:00, daily",
}

# ── Контекстная ссылка на прайс ────────────────────────────────────
# Для каждого языка: (url прайса, готовое предложение).
PRICE_LINK = {
    "sr": (
        "/cenovnik/",
        'Pogledajte tačne cene radova u našem '
        '<a href="/cenovnik/" class="inline-link">cenovniku</a>.',
    ),
    "ru": (
        "/ru/cenovnik/",
        'Посмотрите точные цены на работы в нашем '
        '<a href="/ru/cenovnik/" class="inline-link">прайс-листе</a>.',
    ),
    "en": (
        "/en/pricelist/",
        'Check exact prices for services in our '
        '<a href="/en/pricelist/" class="inline-link">pricelist</a>.',
    ),
}

# Хабы, которым нужна контекстная ссылка на прайс. Остальные страницы либо
# уже её имеют (.cen-inline-link под таблицей цен), либо сами являются
# прайсом, либо это корневой редирект.
PRICE_LINK_TARGETS = {
    "sr/index.html", "sr/novi-sad/index.html", "sr/masters/index.html",
    "ru/index.html", "ru/novi-sad/index.html", "ru/masters/index.html",
    "en/index.html", "en/novi-sad/index.html", "en/masters/index.html",
}


def page_lang(html):
    m = re.search(r'<html lang="(\w+)"', html)
    return m.group(1) if m else "sr"


def add_hours(html, lang):
    """Вставляет строку графика перед абзацем .footer-privacy."""
    if "footer-hours" in html:
        return None
    m = re.search(r'([ \t]*)<p class="footer-privacy">', html)
    if not m:
        return None
    indent = m.group(1)
    line = f'{indent}<p class="footer-hours">{HOURS[lang]}</p>\n'
    return html[: m.start()] + line + html[m.start():]


def add_price_link(html, lang):
    """Дописывает предложение со ссылкой на прайс после блока услуг.

    Якорь — закрывающий </section> секции с карточками услуг: там человек
    только что посмотрел список работ, и вопрос «сколько это стоит»
    возникает естественно.
    """
    if "price-note" in html:
        return None
    sentence = PRICE_LINK[lang][1]
    m = re.search(r'<a[^>]*class="service-card"', html)
    if not m:
        return None
    end = html.find("</section>", m.end())
    if end == -1:
        return None
    para = f'\n      <p class="price-note">{sentence}</p>\n    '
    return html[:end] + para + html[end:]


def main():
    targets = sorted(ROOT.glob("**/index.html"))
    hours_done = link_done = skipped = 0

    for path in targets:
        rel = path.relative_to(ROOT).as_posix()
        if ".claude" in rel or rel == "index.html":
            continue
        html = path.read_text(encoding="utf-8")
        lang = page_lang(html)
        changed = []

        patched = add_hours(html, lang)
        if patched:
            html = patched
            hours_done += 1
            changed.append("hours")

        if rel in PRICE_LINK_TARGETS:
            patched = add_price_link(html, lang)
            if patched:
                html = patched
                link_done += 1
                changed.append("price-link")

        if not changed:
            skipped += 1
            continue
        if not DRY:
            path.write_text(html, encoding="utf-8")
        print(f"  ✓ {'+'.join(changed):18} {rel}")

    print(f"\nЧасы работы: {hours_done}, ссылка на прайс: {link_done}, без изменений: {skipped}")
    if DRY:
        print("(--dry-run: файлы не изменялись)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
