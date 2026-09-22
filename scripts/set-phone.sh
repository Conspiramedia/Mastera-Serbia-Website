#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
# set-phone.sh — замена телефона по всему сайту
#
# Зачем: сайт — форк грузинского проекта, и в нём остался грузинский
# номер +995 557 645 196. Своей сим-карты в Сербии на момент форка не
# было, номер выдумывать нельзя (на него будут звонить), поэтому
# замена отложена до покупки реального +381.
#
# Что делает:
#   1. Меняет номер во ВСЕХ формах, в которых он встречается:
#        tel:+995557645196            — ссылка «позвонить» в шапке
#        // +995 557 645 196          — видимый текст в шапке
#        wa.me/995557645196           — плавающая кнопка WhatsApp
#        "telephone": "+995557645196" — JSON-LD (schema.org)
#   2. Чинит TODO-комментарий в script.js
#   3. Проверяет, что JSON-LD остался валидным, а старый номер исчез
#
# Запуск из корня проекта:
#   bash scripts/set-phone.sh +381601234567
#
# Прогон вхолостую (ничего не пишет, только показывает план):
#   bash scripts/set-phone.sh --dry-run +381601234567
#
# Номер принимается в любом виде: +381601234567, 381 60 123 4567,
# 060/123-4567 — скрипт сам приведёт его к формату сайта.
# ═══════════════════════════════════════════════════════════════════

set -euo pipefail

cd "$(dirname "$0")/.."

# Вывод python — в UTF-8. Без этого на Windows консоль в cp1251
# спотыкается о кириллицу и эмодзи в сообщениях (UnicodeEncodeError),
# и скрипт падает уже после того, как файлы изменены.
export PYTHONIOENCODING=utf-8

# ── Разбор аргументов ──────────────────────────────────────────────
DRY_RUN=0
NEW_RAW=""

for arg in "$@"; do
    case "$arg" in
        --dry-run|-n) DRY_RUN=1 ;;
        -h|--help)
            sed -n '2,27p' "$0" | sed 's/^# \{0,1\}//'
            exit 0 ;;
        -*)
            echo "❌ Неизвестный ключ: $arg" >&2
            exit 1 ;;
        *)  NEW_RAW="$arg" ;;
    esac
done

if [ -z "$NEW_RAW" ]; then
    echo "❌ Не указан новый номер." >&2
    echo "   Пример: bash scripts/set-phone.sh +381601234567" >&2
    exit 1
fi

# ── Старый номер (грузинский, из форка) ────────────────────────────
OLD_DIGITS="995557645196"
OLD_PRETTY="+995 557 645 196"

# ── Нормализация и проверка нового номера ──────────────────────────
#
# Формат разбивки — ровно как в formatSerbianPhone() в script.js:
# код страны, код оператора (2 цифры), затем 3 и остаток.
# Если развести эти правила по разным местам, шапка и поле ввода
# начнут показывать один номер по-разному.
read -r NEW_DIGITS NEW_PRETTY < <(python - "$NEW_RAW" << 'PYEOF'
import re, sys

raw = sys.argv[1]
digits = re.sub(r'\D', '', raw)

if not digits:
    sys.exit("❌ В аргументе нет ни одной цифры: " + raw)

# Локальный ввод «06012…» → международный, как в script.js
if digits.startswith('0'):
    digits = '381' + digits.lstrip('0')
elif not digits.startswith('381'):
    digits = '381' + digits

# PHONE_PATTERN в script.js: +381 и 8–10 цифр после
rest = digits[3:]
if not 8 <= len(rest) <= 10:
    sys.exit(
        "❌ После +381 должно быть 8–10 цифр, а получилось %d (%s).\n"
        "   Проверьте номер: %s" % (len(rest), digits, raw)
    )

parts = ['+381', rest[:2], rest[2:5], rest[5:]]
print(digits, ' '.join(p for p in parts if p))
PYEOF
)

echo "📞 Старый номер: $OLD_PRETTY  ($OLD_DIGITS)"
echo "📞 Новый номер:  $NEW_PRETTY  ($NEW_DIGITS)"
echo ""

# ── Сколько и где менять ───────────────────────────────────────────
# Только файлы под контролем git. Раньше здесь был обход всего дерева,
# и скрипт заодно правил ./.claude/worktrees/ — служебные копии репозитория,
# которые к сайту отношения не имеют и в коммит не попадают.
files=$(git ls-files '*.html' '*.js' | xargs grep -l "$OLD_DIGITS" 2>/dev/null || true)

if [ -z "$files" ]; then
    echo "ℹ️  Старый номер не найден — похоже, замена уже сделана."
    echo "   Проверить: grep -rn '$OLD_DIGITS' --include='*.html' --include='*.js' ."
    exit 0
fi

file_count=$(echo "$files" | wc -l | tr -d ' ')
# Считаем обе формы: слитную и «красивую» с пробелами. Одна строка шапки
# содержит сразу обе (href и видимый текст), поэтому вхождений больше,
# чем строк с номером — так и должно быть.
hit_count=$(grep -roh "$OLD_DIGITS\|$OLD_PRETTY" --include="*.html" --include="*.js" . | wc -l | tr -d ' ')

echo "🔍 Найдено вхождений: $hit_count в $file_count файлах"

if [ "$DRY_RUN" = "1" ]; then
    echo ""
    echo "🧪 Холостой прогон — ничего не изменено."
    echo "   Файлы, которые будут затронуты:"
    echo "$files" | sed 's/^/     /'
    echo ""
    echo "   Запустить по-настоящему:"
    echo "     bash scripts/set-phone.sh $NEW_RAW"
    exit 0
fi

# ── Замена ─────────────────────────────────────────────────────────
#
# Через python, а не sed: файлы в UTF-8 с кириллицей и CRLF,
# а поведение sed с ними разное на Windows/Git Bash и на Linux.
# newline='' — чтобы не переписать концы строк во всех 118 файлах
# и не получить diff на весь репозиторий вместо одной строки.
python - "$OLD_DIGITS" "$OLD_PRETTY" "$NEW_DIGITS" "$NEW_PRETTY" $files << 'PYEOF'
import io, sys

old_digits, old_pretty, new_digits, new_pretty = sys.argv[1:5]
paths = sys.argv[5:]

changed = 0
total = 0

for path in paths:
    with io.open(path, encoding='utf-8', newline='') as fh:
        text = fh.read()

    before = text
    # Сначала «красивая» форма: она содержит цифры с пробелами и
    # не пересекается со слитной, но порядок оставлен явным.
    text = text.replace(old_pretty, new_pretty)
    text = text.replace(old_digits, new_digits)

    if text != before:
        n = before.count(old_digits) + before.count(old_pretty)
        total += n
        changed += 1
        with io.open(path, 'w', encoding='utf-8', newline='') as fh:
            fh.write(text)

print("✅ Заменено: %d вхождений в %d файлах" % (total, changed))
PYEOF

# ── TODO в script.js больше не актуален ────────────────────────────
python - "$NEW_PRETTY" << 'PYEOF'
import io, re, sys

new_pretty = sys.argv[1]
path = 'script.js'

with io.open(path, encoding='utf-8', newline='') as fh:
    text = fh.read()

# Блок TODO про замену номера — от строки TODO(Сербия) до строки
# с командой sed включительно. Уходит целиком: задача закрыта.
pattern = re.compile(
    r'[ \t]*// TODO\(Сербия\): номер грузинский.*?'
    r'Подробности — docs/phone-migration\.md\r?\n',
    re.DOTALL
)

text, n = pattern.subn('', text)

if n:
    with io.open(path, 'w', encoding='utf-8', newline='') as fh:
        fh.write(text)
    print("✅ TODO о замене номера убран из script.js")
else:
    print("ℹ️  TODO о замене номера в script.js не найден (уже убран?)")
PYEOF

echo ""
echo "🔍 Проверки…"

# ── 1. Старого номера не осталось ──────────────────────────────────
left=$(grep -rn "$OLD_DIGITS\|995 557 645 196" --include="*.html" --include="*.js" . || true)
if [ -n "$left" ]; then
    echo "⚠️  Старый номер всё ещё встречается:"
    echo "$left" | sed 's/^/     /'
else
    echo "✅ Старого номера не осталось"
fi

# ── 2. JSON-LD остался валидным ────────────────────────────────────
python - << 'PYEOF'
import io, json, re, glob

pattern = re.compile(
    r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.DOTALL | re.IGNORECASE
)

bad = 0
total = 0
for path in sorted(glob.glob('**/*.html', recursive=True)):
    with io.open(path, encoding='utf-8') as fh:
        for block in pattern.findall(fh.read()):
            total += 1
            try:
                json.loads(block)
            except Exception as exc:
                bad += 1
                print("⚠️  Битый JSON-LD: %s — %s" % (path, exc))

if bad:
    print("⚠️  Невалидных блоков JSON-LD: %d из %d" % (bad, total))
else:
    print("✅ JSON-LD валиден во всех блоках (%d)" % total)
PYEOF

# ── 3. script.js не сломан ─────────────────────────────────────────
if command -v node > /dev/null 2>&1; then
    if node --check script.js > /dev/null 2>&1; then
        echo "✅ script.js синтаксически корректен"
    else
        echo "⚠️  script.js не проходит node --check — посмотрите вручную"
    fi
else
    echo "ℹ️  node не найден — проверку синтаксиса script.js пропустил"
fi

echo ""
echo "─────────────────────────────────────────────"
echo "Дальше вручную:"
echo "  1. Посмотреть изменения:  git diff --stat"
echo "  2. Открыть сайт и проверить шапку и кнопку WhatsApp:"
echo "       npx serve . -l 3000"
echo "  3. Закоммитить и выложить (main = продакшен):"
echo "       git add -A"
echo "       git commit -m 'Телефон: сербский номер $NEW_PRETTY'"
echo "       git push origin main"
echo "─────────────────────────────────────────────"
