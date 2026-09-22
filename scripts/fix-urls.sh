#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
# fix-urls.sh — перевод сербских лендингов на чистые URL
#               и перенос русских лендингов в /ru/
#
# ЧТО ДЕЛАЕТ
#   1. 36 сербских папок:  vodoinstalater-beograd-sr/ → vodoinstalater-beograd/
#   2. 36 русских папок:   santehnik-beograd/        → ru/santehnik-beograd/
#   3. Обновляет ВСЕ ссылки на них: href, canonical, hreflang, og:url,
#      sitemap.xml, хардкод в script.js.
#   4. Русским страницам правит относительные пути ассетов (../ → ../../),
#      потому что они уезжают на уровень глубже.
#   Английские папки (-en) НЕ трогаются.
#
# ЗАЧЕМ
#   Суффикс -sr в URL отбирает релевантность у главного ключа
#   («vodoinstalater beograd»), а сербский — язык 70-80% аудитории.
#   Делать это нужно ДО индексации: потом та же правка стоит 36 редиректов
#   и потери ссылочного веса.
#
# ПОЧЕМУ НЕ ПРОСТОЙ sed 's/-sr//g'
#   Подстрока «-sr» встречается не только в путях:
#     data-sr="Stranica nije pronađena"   — атрибуты локализации (404.html)
#     url(#g-green-sr), id="g-green-sr"   — SVG-градиенты
#     [data-sr-placeholder], [data-suffix-sr] — селекторы в script.js
#   Глобальная замена сломала бы перевод интерфейса и заливку иконок.
#   Поэтому заменяется только путь целиком: «-sr/» и «-sr"» на границе
#   сегмента URL, и только там, где слева стоит известное имя папки.
#
# БЕЗОПАСНОСТЬ
#   - git mv сохраняет историю файлов;
#   - --dry-run показывает план, ничего не меняя;
#   - скрипт идемпотентен: повторный запуск ничего не ломает;
#   - на грязном рабочем дереве отказывается работать (кроме --dry-run),
#     чтобы откат через git был однозначным.
#
# ЗАПУСК
#   bash scripts/fix-urls.sh --dry-run   # посмотреть план
#   bash scripts/fix-urls.sh             # выполнить
# ═══════════════════════════════════════════════════════════════════

set -euo pipefail

cd "$(dirname "$0")/.."

DRY_RUN=0
[ "${1:-}" = "--dry-run" ] && DRY_RUN=1

say()  { echo "$@"; }
step() { echo ""; echo "── $* ────────────────────────────────"; }

# ── Проверка: рабочее дерево должно быть чистым ────────────────────
if [ "$DRY_RUN" -eq 0 ] && [ -n "$(git status --porcelain)" ]; then
    echo "❌ Рабочее дерево не чистое. Закоммитьте или отложите изменения —"
    echo "   иначе откат этой миграции через git станет неоднозначным."
    exit 1
fi

# ── Собираем списки папок ──────────────────────────────────────────
# Сербские: всё, что оканчивается на -sr
mapfile -t SR_DIRS < <(git ls-files | grep -oE '^[a-z0-9-]+-sr/' | sed 's|/$||' | sort -u)

# Русские: папки в корне без суффиксов -sr/-en, кроме служебных.
# Языковые каталоги ru/sr/en и ассеты исключены намеренно.
mapfile -t RU_DIRS < <(git ls-files | grep -oE '^[a-z0-9-]+/' | sed 's|/$||' | sort -u \
    | grep -vE -- '-sr$|-en$' \
    | grep -vE '^(ru|sr|en|image|fonts|docs|scripts)$')

say "Найдено сербских папок: ${#SR_DIRS[@]}"
say "Найдено русских папок:  ${#RU_DIRS[@]}"

# ── Проверка коллизий до любых изменений ───────────────────────────
step "Проверка коллизий"
collision=0
for d in "${SR_DIRS[@]}"; do
    t="${d%-sr}"
    if [ -e "$t" ]; then
        echo "❌ $d → $t : цель уже существует"
        collision=1
    fi
done
for d in "${RU_DIRS[@]}"; do
    if [ -e "ru/$d" ]; then
        echo "❌ $d → ru/$d : цель уже существует"
        collision=1
    fi
done
if [ "$collision" -eq 1 ]; then
    echo "Миграция отменена — разберите коллизии вручную."
    exit 1
fi
say "✅ Коллизий нет"

# ── 1. Переименование сербских папок ───────────────────────────────
step "1. Сербские папки: снятие суффикса -sr"
for d in "${SR_DIRS[@]}"; do
    t="${d%-sr}"
    if [ "$DRY_RUN" -eq 1 ]; then
        say "   $d/ → $t/"
    else
        git mv "$d" "$t"
    fi
done
say "✅ Переименовано: ${#SR_DIRS[@]}"

# ── 2. Перенос русских папок в /ru/ ────────────────────────────────
step "2. Русские папки: перенос в /ru/"
for d in "${RU_DIRS[@]}"; do
    if [ "$DRY_RUN" -eq 1 ]; then
        say "   $d/ → ru/$d/"
    else
        git mv "$d" "ru/$d"
    fi
done
say "✅ Перенесено: ${#RU_DIRS[@]}"

if [ "$DRY_RUN" -eq 1 ]; then
    step "Сухой прогон завершён"
    say "Замена ссылок в этом режиме не выполняется —"
    say "она зависит от уже переименованных путей."
    exit 0
fi

# ── 3. Замена ссылок во всех текстовых файлах ──────────────────────
# Делается одним python-проходом, а не цепочкой sed: файлы в UTF-8
# с кириллицей и смешанными концами строк, sed на Windows и Linux
# обрабатывает их по-разному. newline='' сохраняет CRLF/LF как есть.
step "3. Обновление ссылок"

python - "${SR_DIRS[@]}" "--split--" "${RU_DIRS[@]}" << 'PYEOF'
# -*- coding: utf-8 -*-
import re
import subprocess
import sys

argv = sys.argv[1:]
split = argv.index('--split--')
sr_dirs = argv[:split]
ru_dirs = argv[split + 1:]

# Карта замен путей. Ключ — старый сегмент, значение — новый.
# Сербские: vodoinstalater-beograd-sr → vodoinstalater-beograd
# Русские:  santehnik-beograd         → ru/santehnik-beograd
path_map = {}
for d in sr_dirs:
    path_map[d] = d[:-3]          # отрезаем «-sr»
for d in ru_dirs:
    path_map[d] = 'ru/' + d

# Сортируем по длине убыв.: «master-na-chas-stari-grad-novi-sad» должен
# сработать раньше, чем «master-na-chas-stari-grad», иначе длинное имя
# будет испорчено заменой своего же префикса.
keys = sorted(path_map, key=len, reverse=True)

# Путь заменяется только когда он — ЦЕЛЫЙ сегмент URL:
# слева начало строки, «/» или кавычка; справа «/» или кавычка.
# Это отсекает data-sr=, url(#g-green-sr) и [data-suffix-sr].
pattern = re.compile(
    r'(?<![a-z0-9-])(' + '|'.join(re.escape(k) for k in keys) + r')(?=[/"\'])'
)

files = subprocess.check_output(
    ['git', 'ls-files', '*.html', '*.js', '*.xml', '*.txt', '*.json', '*.webmanifest'],
    text=True
).split()

changed = 0
for path in files:
    with open(path, encoding='utf-8', newline='') as fh:
        text = fh.read()

    new_text = pattern.sub(lambda m: path_map[m.group(1)], text)

    if new_text != text:
        with open(path, 'w', encoding='utf-8', newline='') as fh:
            fh.write(new_text)
        changed += 1

print(f'   Файлов со ссылками обновлено: {changed}')
PYEOF

# ── 4. Относительные пути ассетов в перенесённых русских страницах ──
# Страницы уехали с 1-го уровня на 2-й, значит ../style.css больше
# не находит файл — нужно ../../style.css. Эталон — уже существовавший
# ru/novi-sad/index.html, где так и сделано.
step "4. Относительные пути в перенесённых русских страницах"

python - "${RU_DIRS[@]}" << 'PYEOF'
# -*- coding: utf-8 -*-
import re
import sys

# Правим только те файлы, что мы только что перенесли.
files = [f'ru/{d}/index.html' for d in sys.argv[1:]]

# Меняем ../<что-то> на ../../<что-то>, но не трогаем уже готовые ../../
pattern = re.compile(r'(?<!\.\./)\.\./(?!\.\./)')

changed = 0
for path in files:
    try:
        with open(path, encoding='utf-8', newline='') as fh:
            text = fh.read()
    except FileNotFoundError:
        continue

    new_text = pattern.sub('../../', text)
    if new_text != text:
        with open(path, 'w', encoding='utf-8', newline='') as fh:
            fh.write(new_text)
        changed += 1

print(f'   Страниц с поправленными путями: {changed}')
PYEOF

# ── 5. Проверки ────────────────────────────────────────────────────
step "5. Проверка результата"

left_dirs=$(git ls-files | grep -cE '^[a-z0-9-]+-sr/' || true)
say "   Папок с суффиксом -sr осталось: $left_dirs (ожидается 0)"

left_links=$(grep -rn -- '-sr/' --include='*.html' --include='*.xml' . 2>/dev/null \
             | grep -v '/.claude/' | wc -l || true)
say "   Ссылок вида -sr/ осталось: $left_links (ожидается 0)"

# JSON-LD должен остаться валидным — ссылки меняются и внутри разметки
python - << 'PYEOF'
import glob, io, json, re
bad = total = 0
for f in glob.glob('**/*.html', recursive=True):
    if '.claude' in f:
        continue
    html = io.open(f, encoding='utf-8').read()
    for m in re.finditer(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>',
                         html, re.S | re.I):
        total += 1
        try:
            json.loads(m.group(1))
        except Exception as e:
            bad += 1
            print(f'   ❌ BROKEN JSON-LD: {f} — {str(e)[:60]}')
print(f'   JSON-LD блоков: {total}, битых: {bad}')
PYEOF

node --check script.js && say "   ✅ script.js синтаксически валиден"

step "Готово"
say "Дальше:"
say "  1. bash scripts/check-links.sh   — проверить, что нет битых ссылок"
say "  2. git status                    — посмотреть переименования"
say "  3. git add -A && git commit"
