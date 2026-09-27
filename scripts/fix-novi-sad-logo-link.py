# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════
fix-novi-sad-logo-link.py — логотип на страницах Нови-Сада

ПРОБЛЕМА
    На всех 53 страницах Нови-Сада логотип «Pravi Majstor» в шапке вёл
    на языковой хаб Белграда:

        /ru/novi-sad/            → логотип → /ru/   (Белград)
        /elektricar-novi-sad/    → логотип → /sr/   (Белград)
        /santehnik-novi-sad-en/  → логотип → /en/   (Белград)

    Язык сохранялся, город терялся. Пользователь выбирал Нови-Сад,
    кликал по логотипу и молча оказывался в Белграде — там другие
    районы и другие мастера.

    На страницах Белграда поведение было верным изначально: языковой
    хаб и есть их «домой», поэтому их не трогаем.

ЧТО ДЕЛАЕТ
    Заменяет href на хаб СВОЕГО города и языка:
        /ru/ → /ru/novi-sad/,  /sr/ → /sr/novi-sad/,  /en/ → /en/novi-sad/

    Правятся две ссылки «домой», обе вели в Белград:
      1. логотип в шапке          — class="logo-link"  (54 страницы);
      2. карточка «На главную»    — class="service-card" в блоке
         «Другие сервисы» внизу страницы (51 страница).

    Языковой переключатель и city-switcher не трогаем: там ссылка на
    белградский хаб осмысленна — это и есть «переключить город/язык».

ЧЕГО НЕ ТРОГАЕТ
    Хабы самого Нови-Сада (/ru/novi-sad/ и т.д.) — у них логотип уже
    указывает на себя же после правки, это нормально: клик по логотипу
    на главной странице города возвращает на неё.
    Страницы Белграда, canonical, hreflang, JSON-LD, формы.

ИДЕМПОТЕНТНОСТЬ
    Ищем точную исходную строку. Если её нет (уже исправлено или
    разметка другая) — правка помечается пропуском, файл не
    переписывается молча.

ЗАПУСК из корня проекта:
    python scripts/fix-novi-sad-logo-link.py --dry-run
    python scripts/fix-novi-sad-logo-link.py
═══════════════════════════════════════════════════════════════════
"""

import os
import re
import sys
import glob

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DRY_RUN = '--dry-run' in sys.argv

# Языковой хаб → хаб того же языка, но Нови-Сада
HUB = {
    '/ru/': '/ru/novi-sad/',
    '/sr/': '/sr/novi-sad/',
    '/en/': '/en/novi-sad/',
}


def novi_sad_pages():
    """
    Все страницы Нови-Сада. Служебные каталоги, начинающиеся с точки,
    пропускаем: в .claude/worktrees лежит копия сайта, её править нельзя.
    """
    out = []
    for path in glob.glob(os.path.join(ROOT, '**', 'index.html'), recursive=True):
        rel = os.path.relpath(path, ROOT).replace(os.sep, '/')
        if any(seg.startswith('.') for seg in rel.split('/')):
            continue
        if 'novi-sad' not in rel:
            continue
        out.append(rel)
    return sorted(out)


# Классы ссылок «домой», которые нужно увести на хаб своего города.
# Оба варианта ведут на языковой хаб, то есть в Белград.
HOME_LINK_CLASSES = ('logo-link', 'service-card')


def fix(rel):
    path = os.path.join(ROOT, rel)
    with open(path, encoding='utf-8') as fh:
        html = fh.read()

    original = html
    changed = []

    for cls in HOME_LINK_CLASSES:
        pattern = r'<a href="(/(?:ru|sr|en)/)" class="{}"'.format(re.escape(cls))
        m = re.search(pattern, html)
        if not m:
            continue

        old_href = m.group(1)
        new_href = HUB[old_href]

        old = '<a href="{}" class="{}"'.format(old_href, cls)
        new = '<a href="{}" class="{}"'.format(new_href, cls)

        # count=1: каждая такая ссылка на странице одна. Карточек
        # .service-card много, но на языковой хаб ведёт только «На главную» —
        # остальные указывают на конкретные услуги.
        html = html.replace(old, new, 1)
        changed.append('{}: {} → {}'.format(cls, old_href, new_href))

    if not changed:
        already = re.search(r'<a href="/(?:ru|sr|en)/novi-sad/" class="logo-link"', html)
        state = 'уже исправлено' if already else 'ссылок «домой» не найдено'
        print('  {:<50} [{}]'.format(rel, state))
        return 0, 1

    if html != original and not DRY_RUN:
        with open(path, 'w', encoding='utf-8', newline='') as fh:
            fh.write(html)

    print('  {:<50} {}'.format(rel, '; '.join(changed)))
    return len(changed), 0


def main():
    print('═' * 76)
    print('Логотип на страницах Нови-Сада'
          + ('  [DRY-RUN, файлы не пишутся]' if DRY_RUN else ''))
    print('═' * 76)

    pages = novi_sad_pages()
    done = skipped = 0
    for rel in pages:
        a, b = fix(rel)
        done += a
        skipped += b

    print('\n' + '─' * 76)
    print('Итого: страниц {}, исправлено {}, пропущено {}'
          .format(len(pages), done, skipped))
    print('─' * 76)


if __name__ == '__main__':
    main()
