#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
add-breadcrumbs.py — хлебные крошки на страницы, где их ещё нет.

Что делает за один проход:
  1. JSON-LD BreadcrumbList в <script type="application/ld+json"> — дописывает
     объект в конец существующего массива схем (у всех целевых страниц схема
     оформлена массивом, поэтому новый узел просто добавляется элементом).
  2. Видимый <nav class="breadcrumb"> сразу после <main> — ссылки один в один
     повторяют JSON-LD, иначе Google считает разметку несоответствующей
     содержимому страницы и игнорирует её.

Схема пути — ровно та же, что на 53 страницах, где крошки уже стоят:
    Главная → Услуга в городе → Район        (районные лендинги)
    Главная → Город → Услуга                 (сервисные страницы)

Последний элемент — текущая страница: в JSON-LD он с "item" (так сделано в
эталонных страницах), в видимой навигации — <span aria-current="page"> без
ссылки, чтобы не давать ссылку на саму себя.

Запуск из корня проекта:
    python scripts/add-breadcrumbs.py            # правит файлы
    python scripts/add-breadcrumbs.py --dry-run  # только показывает план

Скрипт идемпотентен: страницы, где уже есть BreadcrumbList или nav.breadcrumb,
пропускаются. Повторный запуск ничего не сломает.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DRY = "--dry-run" in sys.argv

# ── Подписи по языкам ──────────────────────────────────────────────
# "home" — имя первой крошки, "hub" — как называется городской хаб.
LANG = {
    "sr": {"home": "Početna", "aria": "Putanja", "sep": "/"},
    "ru": {"home": "Главная", "aria": "Хлебные крошки", "sep": "/"},
    "en": {"home": "Home", "aria": "Breadcrumb", "sep": "/"},
}

# Корень языка — первая крошка ведёт сюда.
HOME = {"sr": "/sr/", "ru": "/ru/", "en": "/en/"}

# Городские хабы: (язык, город) → (url, подпись).
CITY_HUB = {
    ("sr", "bg"): ("/sr/", "Beograd"),
    ("sr", "ns"): ("/sr/novi-sad/", "Novi Sad"),
    ("ru", "bg"): ("/ru/", "Белград"),
    ("ru", "ns"): ("/ru/novi-sad/", "Нови-Сад"),
    ("en", "bg"): ("/en/", "Belgrade"),
    ("en", "ns"): ("/en/novi-sad/", "Novi Sad"),
}

# ── Районные лендинги «мастер на час» ──────────────────────────────
# Крошка: Главная → «Мастер на час в <городе>» → Район.
# Ключ — каталог страницы, значение — (язык, город, подпись района).
DISTRICTS = {
    # Нови-Сад, сербский
    "majstor-za-sve-detelinara-novi-sad":      ("sr", "ns", "Detelinara"),
    "majstor-za-sve-grbavica-novi-sad":        ("sr", "ns", "Grbavica"),
    "majstor-za-sve-liman-novi-sad":           ("sr", "ns", "Liman"),
    "majstor-za-sve-novo-naselje-novi-sad":    ("sr", "ns", "Novo Naselje"),
    "majstor-za-sve-petrovaradin-novi-sad":    ("sr", "ns", "Petrovaradin"),
    "majstor-za-sve-podbara-novi-sad":         ("sr", "ns", "Podbara"),
    "majstor-za-sve-stari-grad-novi-sad":      ("sr", "ns", "Stari Grad"),
    "majstor-za-sve-telep-novi-sad":           ("sr", "ns", "Telep"),
    # Нови-Сад, английский
    "master-na-chas-detelinara-novi-sad-en":   ("en", "ns", "Detelinara"),
    "master-na-chas-grbavica-novi-sad-en":     ("en", "ns", "Grbavica"),
    "master-na-chas-liman-novi-sad-en":        ("en", "ns", "Liman"),
    "master-na-chas-novo-naselje-novi-sad-en": ("en", "ns", "Novo Naselje"),
    "master-na-chas-petrovaradin-novi-sad-en": ("en", "ns", "Petrovaradin"),
    "master-na-chas-podbara-novi-sad-en":      ("en", "ns", "Podbara"),
    "master-na-chas-stari-grad-novi-sad-en":   ("en", "ns", "Stari Grad"),
    "master-na-chas-telep-novi-sad-en":        ("en", "ns", "Telep"),
    # Нови-Сад, русский
    "ru/master-na-chas-detelinara-novi-sad":   ("ru", "ns", "Детелинара"),
    "ru/master-na-chas-grbavica-novi-sad":     ("ru", "ns", "Грбавица"),
    "ru/master-na-chas-liman-novi-sad":        ("ru", "ns", "Лиман"),
    "ru/master-na-chas-novo-naselje-novi-sad": ("ru", "ns", "Ново-Насельe"),
    "ru/master-na-chas-petrovaradin-novi-sad": ("ru", "ns", "Петроварадин"),
    "ru/master-na-chas-podbara-novi-sad":      ("ru", "ns", "Подбара"),
    "ru/master-na-chas-stari-grad-novi-sad":   ("ru", "ns", "Стари-Град"),
    "ru/master-na-chas-telep-novi-sad":        ("ru", "ns", "Телеп"),
}

# Городская страница «мастер на час», на которую ссылается вторая крошка
# районных лендингов. Ровно так сделано на 53 готовых страницах.
HANDYMAN_CITY = {
    ("sr", "ns"): ("/majstor-za-sve-novi-sad/", "Majstor na sat u Novom Sadu"),
    ("en", "ns"): ("/master-na-chas-novi-sad-en/", "Handyman in Novi Sad"),
    ("ru", "ns"): ("/ru/master-na-chas-novi-sad/", "Мастер на час в Нови-Саде"),
}

# ── Сервисные страницы «услуга + город» ────────────────────────────
# Крошка: Главная → Город → Услуга.
# Ключ — каталог, значение — (язык, город, название услуги).
SERVICES = {
    # ---- сербский, Белград
    "vodoinstalater-beograd":        ("sr", "bg", "Vodoinstalater"),
    "elektricar-beograd":            ("sr", "bg", "Električar"),
    "majstor-za-sve-beograd":        ("sr", "bg", "Majstor na sat"),
    "montaza-namestaja-beograd":     ("sr", "bg", "Montaža nameštaja"),
    "montaza-na-zid-beograd":        ("sr", "bg", "Kačenje i montaža"),
    "kucni-popravci-beograd":        ("sr", "bg", "Kućne popravke"),
    "ciscenje-i-odrzavanje-beograd": ("sr", "bg", "Čišćenje stanova"),
    "selidbe-i-nosaci-beograd":      ("sr", "bg", "Selidbe i nosači"),
    "majstor-za-racunare-beograd":   ("sr", "bg", "Majstor za računare"),
    # ---- сербский, Нови-Сад
    "vodoinstalater-novi-sad":        ("sr", "ns", "Vodoinstalater"),
    "elektricar-novi-sad":            ("sr", "ns", "Električar"),
    "majstor-za-sve-novi-sad":        ("sr", "ns", "Majstor na sat"),
    "montaza-namestaja-novi-sad":     ("sr", "ns", "Montaža nameštaja"),
    "montaza-na-zid-novi-sad":        ("sr", "ns", "Kačenje i montaža"),
    "kucni-popravci-novi-sad":        ("sr", "ns", "Kućne popravke"),
    "ciscenje-i-odrzavanje-novi-sad": ("sr", "ns", "Čišćenje stanova"),
    "selidbe-i-nosaci-novi-sad":      ("sr", "ns", "Selidbe i nosači"),
    "majstor-za-racunare-novi-sad":   ("sr", "ns", "Majstor za računare"),
    # ---- английский, Белград
    "santehnik-beograd-en":        ("en", "bg", "Plumber"),
    "elektrik-beograd-en":         ("en", "bg", "Electrician"),
    "master-na-chas-beograd-en":   ("en", "bg", "Handyman"),
    "sborka-mebeli-beograd-en":    ("en", "bg", "Furniture Assembly"),
    "naveska-montazh-beograd-en":  ("en", "bg", "Mounting & Installation"),
    "bytovoy-remont-beograd-en":   ("en", "bg", "Home Repairs"),
    "klining-beograd-en":          ("en", "bg", "Apartment Cleaning"),
    "gruzchiki-beograd-en":        ("en", "bg", "Movers"),
    "remont-kompyuterov-beograd-en": ("en", "bg", "Computer Repair"),
    # ---- английский, Нови-Сад
    "santehnik-novi-sad-en":        ("en", "ns", "Plumber"),
    "elektrik-novi-sad-en":         ("en", "ns", "Electrician"),
    "master-na-chas-novi-sad-en":   ("en", "ns", "Handyman"),
    "sborka-mebeli-novi-sad-en":    ("en", "ns", "Furniture Assembly"),
    "naveska-montazh-novi-sad-en":  ("en", "ns", "Mounting & Installation"),
    "bytovoy-remont-novi-sad-en":   ("en", "ns", "Home Repairs"),
    "klining-novi-sad-en":          ("en", "ns", "Apartment Cleaning"),
    "gruzchiki-novi-sad-en":        ("en", "ns", "Movers"),
    "remont-kompyuterov-novi-sad-en": ("en", "ns", "Computer Repair"),
    # ---- русский (в ru/ крошек не хватало только у части услуг)
    "ru/klining-beograd":           ("ru", "bg", "Уборка квартир"),
    "ru/gruzchiki-beograd":         ("ru", "bg", "Грузчики"),
    "ru/remont-kompyuterov-beograd": ("ru", "bg", "Компьютерный мастер"),
    "ru/klining-novi-sad":           ("ru", "ns", "Уборка квартир"),
    "ru/gruzchiki-novi-sad":         ("ru", "ns", "Грузчики"),
    "ru/remont-kompyuterov-novi-sad": ("ru", "ns", "Компьютерный мастер"),
    "ru/master-na-chas-novi-sad":     ("ru", "ns", "Мастер на час"),
}

SITE = "https://pravimajstor.rs"


def crumbs_for(rel_dir):
    """Возвращает список крошек [(подпись, url), …] или None, если страница не наша."""
    if rel_dir in DISTRICTS:
        lang, city, name = DISTRICTS[rel_dir]
        hub_url, hub_name = HANDYMAN_CITY[(lang, city)]
        return lang, [
            (LANG[lang]["home"], HOME[lang]),
            (hub_name, hub_url),
            (name, f"/{rel_dir}/"),
        ]
    if rel_dir in SERVICES:
        lang, city, name = SERVICES[rel_dir]
        hub_url, hub_name = CITY_HUB[(lang, city)]
        path = [(LANG[lang]["home"], HOME[lang])]
        # Хаб Белграда и есть главная языка (/sr/, /ru/, /en/) — отдельной
        # крошкой он дал бы две подряд ссылки на один URL. Поэтому для
        # Белграда крошка города не добавляется, для Нови-Сада добавляется.
        if hub_url != HOME[lang]:
            path.append((hub_name, hub_url))
        path.append((name, f"/{rel_dir}/"))
        return lang, path
    return None, None


def build_jsonld(crumbs):
    """JSON-LD BreadcrumbList в том же стиле, что на готовых страницах."""
    items = []
    for i, (name, url) in enumerate(crumbs, 1):
        items.append(
            f'        {{ "@type": "ListItem", "position": {i}, '
            f'"name": {json.dumps(name, ensure_ascii=False)}, '
            f'"item": "{SITE}{url}" }}'
        )
    return (
        "    {\n"
        '      "@context": "https://schema.org",\n'
        '      "@type": "BreadcrumbList",\n'
        '      "itemListElement": [\n'
        + ",\n".join(items)
        + "\n      ]\n"
        "    }"
    )


def build_nav(lang, crumbs):
    """Видимая навигация. Последний элемент — без ссылки (это текущая страница)."""
    parts = []
    for name, url in crumbs[:-1]:
        parts.append(f'<a href="{url}">{name}</a>')
    parts.append(f'<span aria-current="page">{crumbs[-1][0]}</span>')
    sep = f'\n        <span class="breadcrumb-sep" aria-hidden="true">{LANG[lang]["sep"]}</span>\n        '
    return (
        f'    <nav class="breadcrumb" aria-label="{LANG[lang]["aria"]}">\n'
        f'      <div class="breadcrumb-inner">\n        '
        + sep.join(parts)
        + "\n      </div>\n    </nav>\n"
    )


def read_existing_crumbs(html):
    """Вытаскивает крошки из уже стоящего в странице JSON-LD.

    Нужно для второго прохода: на 53 страницах разметка есть, а видимой
    навигации нет. Берём подписи и ссылки прямо из схемы — так видимые
    крошки гарантированно совпадают с JSON-LD, а не расходятся с ним.
    """
    m = re.search(
        r'"@type":\s*"BreadcrumbList",\s*"itemListElement":\s*\[(.*?)\n\s*\]',
        html,
        re.S,
    )
    if not m:
        return None
    pairs = re.findall(r'"name":\s*"([^"]*)",\s*"item":\s*"([^"]*)"', m.group(1))
    if not pairs:
        return None
    # Абсолютные ссылки превращаем в относительные — как в остальной вёрстке.
    return [(n, u.replace(SITE, "")) for n, u in pairs]


def insert_nav(html, lang, crumbs):
    """Вставляет видимую навигацию сразу после открывающего <main …>."""
    m = re.search(r"\n  <main[^>]*>\n", html)
    if not m:
        return None
    return html[: m.end()] + build_nav(lang, crumbs) + html[m.end():]


def patch(path, lang, crumbs):
    html = path.read_text(encoding="utf-8")
    changed = []

    # ── 1. JSON-LD ────────────────────────────────────────────────
    if "BreadcrumbList" not in html:
        # Ищем блок ld+json, оформленный массивом: "<script …>\n  [ … ]\n  </script>".
        m = re.search(
            r'(<script type="application/ld\+json">\s*\[)(.*?)(\n  \]\n  </script>)',
            html,
            re.S,
        )
        if not m:
            return None, "нет ld+json-массива"
        block = m.group(2).rstrip()
        new_block = block + ",\n" + build_jsonld(crumbs)
        html = html[: m.start(2)] + new_block + html[m.end(2):]
        changed.append("json-ld")

    # ── 2. Видимая навигация ──────────────────────────────────────
    if 'class="breadcrumb"' not in html:
        patched = insert_nav(html, lang, crumbs)
        if patched is None:
            return None, "нет <main>"
        html = patched
        changed.append("nav")

    if not changed:
        return None, "уже есть"
    if not DRY:
        path.write_text(html, encoding="utf-8")
    return changed, None


def patch_existing(path):
    """Второй проход: видимый nav на страницах, где JSON-LD уже стоял.

    Крошки читаются из самой страницы. Страницы-корни языков (/sr/, /ru/,
    /en/) пропускаем: там крошка вела бы сама на себя.
    """
    html = path.read_text(encoding="utf-8")
    if 'class="breadcrumb"' in html:
        return None, "уже есть"
    crumbs = read_existing_crumbs(html)
    if not crumbs:
        return None, "не разобрал JSON-LD"
    if len(crumbs) < 2 or crumbs[-1][1] == crumbs[0][1]:
        return None, "корень языка"
    m = re.search(r'<html lang="(\w+)"', html)
    lang = m.group(1) if m else "sr"
    patched = insert_nav(html, lang, crumbs)
    if patched is None:
        return None, "нет <main>"
    if not DRY:
        path.write_text(patched, encoding="utf-8")
    return ["nav"], None


def main():
    done = skipped = failed = 0

    # ── Проход 1: страницы без крошек вообще ──────────────────────
    print("▶ Проход 1 — JSON-LD + видимая навигация\n")
    targets = sorted(set(DISTRICTS) | set(SERVICES))
    for rel in targets:
        path = ROOT / rel / "index.html"
        if not path.exists():
            print(f"  ✗ НЕТ ФАЙЛА  {rel}")
            failed += 1
            continue
        lang, crumbs = crumbs_for(rel)
        changed, err = patch(path, lang, crumbs)
        if err:
            if err == "уже есть":
                skipped += 1
            else:
                print(f"  ✗ {err:20} {rel}")
                failed += 1
            continue
        done += 1
        print(f"  ✓ {'+'.join(changed):12} {rel}")

    # ── Проход 2: JSON-LD был, видимой навигации не было ──────────
    print("\n▶ Проход 2 — видимая навигация к готовому JSON-LD\n")
    handled = {r + "/index.html" for r in targets}
    # Корни языков: их JSON-LD-крошка («Pravi Majstor → Srpski») описывает
    # выбор языка, а не путь по сайту. Видимая навигация там была бы шумом —
    # пользователь уже на главной. Схему не трогаем, она валидна.
    lang_roots = {"sr/index.html", "ru/index.html", "en/index.html"}
    for path in sorted(ROOT.glob("**/index.html")):
        rel = path.relative_to(ROOT).as_posix()
        if ".claude" in rel or rel in handled or rel == "index.html":
            continue
        if rel in lang_roots:
            continue
        if "BreadcrumbList" not in path.read_text(encoding="utf-8"):
            continue
        changed, err = patch_existing(path)
        if err:
            if err in ("уже есть", "корень языка"):
                skipped += 1
            else:
                print(f"  ✗ {err:20} {rel}")
                failed += 1
            continue
        done += 1
        print(f"  ✓ {'+'.join(changed):12} {rel}")

    print(f"\nИзменено: {done}, пропущено: {skipped}, ошибок: {failed}")
    if DRY:
        print("(--dry-run: файлы не изменялись)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
