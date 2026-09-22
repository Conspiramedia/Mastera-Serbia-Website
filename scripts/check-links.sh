#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
# check-links.sh — проверка целостности ссылок и hreflang-кластеров
#
# Запускается после fix-urls.sh (и вообще после любой правки путей).
# Ничего не меняет — только читает и сообщает о проблемах.
#
# ЧТО ПРОВЕРЯЕТ
#   1. Внутренние ссылки href="/..." ведут на существующие файлы.
#   2. canonical каждой страницы указывает на неё же саму.
#   3. hreflang-кластеры взаимны: если A ссылается на B, то B обязан
#      ссылаться на A. Односторонняя ссылка Google игнорирует целиком.
#   4. Каждый URL из hreflang и sitemap.xml существует на диске.
#   5. Относительные пути к ассетам (../style.css) разрешаются в файл.
#
# ВЫХОД: 0 — всё чисто, 1 — найдены проблемы.
# ═══════════════════════════════════════════════════════════════════

set -uo pipefail
cd "$(dirname "$0")/.."

python - << 'PYEOF'
# -*- coding: utf-8 -*-
import os
import re
import subprocess
import sys
from urllib.parse import urlparse

# Консоль Windows по умолчанию в cp1251 и падает на эмодзи/кириллице.
# Переключаем поток вывода на UTF-8, иначе скрипт валится на последней строке.
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

SITE = 'https://pravimajstor.rs'
problems = []

files = subprocess.check_output(['git', 'ls-files', '*.html'], text=True).split()


def url_to_path(url):
    """Превращает URL сайта в путь к файлу на диске. None — если внешний."""
    if url.startswith(SITE):
        path = url[len(SITE):]
    elif url.startswith('/'):
        path = url
    else:
        return None
    path = urlparse(path).path
    path = path.lstrip('/')
    if path == '' or path.endswith('/'):
        path += 'index.html'
    elif not path.endswith(('.html', '.xml', '.txt', '.json', '.webmanifest',
                            '.css', '.js', '.png', '.jpg', '.jpeg', '.webp',
                            '.svg', '.ico', '.woff2')):
        path = path + '/index.html'
    return path


# ── Собираем hreflang каждой страницы ──────────────────────────────
HREF_RE = re.compile(r'<link rel="alternate" hreflang="([a-zA-Z-]+)" href="([^"]+)"')
CANON_RE = re.compile(r'<link rel="canonical" href="([^"]+)"')
LINK_RE = re.compile(r'href="(/[^"#]*)"')
REL_RE = re.compile(r'(?:href|src)="((?:\.\./)+[^"#]*)"')

clusters = {}   # файл -> {lang: url}

for f in files:
    html = open(f, encoding='utf-8', newline='').read()

    # 1. Внутренние абсолютные ссылки
    for m in LINK_RE.finditer(html):
        target = url_to_path(m.group(1))
        if target and not os.path.exists(target):
            problems.append(f'{f}: битая внутренняя ссылка → {m.group(1)}')

    # 2. canonical указывает сам на себя
    mc = CANON_RE.search(html)
    if mc:
        cpath = url_to_path(mc.group(1))
        if cpath and os.path.normpath(cpath) != os.path.normpath(f):
            problems.append(
                f'{f}: canonical указывает на {mc.group(1)} — не на себя')

    # 3. Относительные пути к ассетам
    base = os.path.dirname(f)
    for m in REL_RE.finditer(html):
        rel = os.path.normpath(os.path.join(base, m.group(1)))
        if not os.path.exists(rel):
            problems.append(f'{f}: не разрешается относительный путь → {m.group(1)}')

    # 4. hreflang — собираем и проверяем существование цели
    langs = {}
    for m in HREF_RE.finditer(html):
        lang, url = m.group(1), m.group(2)
        langs[lang] = url
        tpath = url_to_path(url)
        if tpath and not os.path.exists(tpath):
            problems.append(f'{f}: hreflang="{lang}" ведёт на несуществующий {url}')
    if langs:
        clusters[f] = langs


# ── 5. Взаимность hreflang ─────────────────────────────────────────
# Если страница A объявляет альтернативу B, то B обязана объявлять A.
for f, langs in clusters.items():
    for lang, url in langs.items():
        if lang == 'x-default':
            continue
        target = url_to_path(url)
        if not target or not os.path.exists(target):
            continue
        target = os.path.normpath(target).replace(os.sep, '/')
        if target == os.path.normpath(f).replace(os.sep, '/'):
            continue            # ссылка на себя — нормально
        back = clusters.get(target)
        if back is None:
            problems.append(f'{f}: {target} не объявляет hreflang вовсе')
            continue
        # У партнёра должен быть тот же набор языков, указывающий сюда
        mine = {url_to_path(u) for l, u in langs.items() if l != 'x-default'}
        theirs = {url_to_path(u) for l, u in back.items() if l != 'x-default'}
        if mine != theirs:
            problems.append(
                f'{f}: кластер не совпадает с {target}\n'
                f'      здесь: {sorted(x for x in mine if x)}\n'
                f'      там:   {sorted(x for x in theirs if x)}')


# ── 6. sitemap.xml ─────────────────────────────────────────────────
if os.path.exists('sitemap.xml'):
    sm = open('sitemap.xml', encoding='utf-8').read()
    locs = re.findall(r'<loc>([^<]+)</loc>', sm)
    for loc in locs:
        p = url_to_path(loc)
        if p and not os.path.exists(p):
            problems.append(f'sitemap.xml: несуществующий URL → {loc}')
    print(f'sitemap.xml: {len(locs)} URL проверено')

# ── Итог ───────────────────────────────────────────────────────────
print(f'Страниц проверено: {len(files)}')
print(f'hreflang-кластеров: {len(clusters)}')

if problems:
    print(f'\n❌ Найдено проблем: {len(problems)}\n')
    # Схлопываем повторы — одна и та же битая ссылка встречается на многих
    # страницах, и полный список был бы нечитаем.
    seen = {}
    for p in problems:
        seen[p] = seen.get(p, 0) + 1
    for p, n in sorted(seen.items())[:60]:
        suffix = f'  (×{n})' if n > 1 else ''
        print(f'  • {p}{suffix}')
    if len(seen) > 60:
        print(f'  … и ещё {len(seen) - 60} уникальных')
    sys.exit(1)

print('\n✅ Все ссылки целы, canonical корректны, hreflang-кластеры взаимны')
PYEOF
