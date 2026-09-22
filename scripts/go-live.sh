#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
# go-live.sh — снятие защиты от индексации перед запуском сайта
#
# Что делает:
#   1. Во всех index.html убирает блоки PRELAUNCH, возвращая
#      исходную мету robots из комментария PRELAUNCH:ORIGINAL
#   2. Возвращает боевой robots.txt с картой сайта
#
# ⚠️ ЗАПУСКАТЬ ТОЛЬКО когда в боте набрано 20–30 мастеров.
#    Открытый сайт без мастеров = заявка уходит в пустоту,
#    клиент не дожидается звонка и не возвращается.
#
# Запуск из корня проекта:
#   bash scripts/go-live.sh
# ═══════════════════════════════════════════════════════════════════

set -euo pipefail

# Переходим в корень проекта (на уровень выше scripts/)
cd "$(dirname "$0")/.."

echo "🔍 Ищу страницы в режиме предзапуска…"
files=$(grep -rl "PRELAUNCH:START" --include="index.html" . || true)

if [ -z "$files" ]; then
    echo "ℹ️  Блоков PRELAUNCH не найдено — сайт уже открыт для индексации."
else
    count=0
    for f in $files; do
        # Восстанавливаем оригинальную мету: строку из PRELAUNCH:ORIGINAL
        # превращаем обратно в живой тег, а служебные строки удаляем.
        python - "$f" << 'PYEOF'
import re, sys

path = sys.argv[1]
with open(path, encoding='utf-8') as fh:
    html = fh.read()

# Блок целиком: от маркера START до маркера END включительно
pattern = re.compile(
    r'[ \t]*<!-- PRELAUNCH:START.*?-->\s*\n'
    r'[ \t]*<meta name="robots"[^>]*>\s*\n'
    r'[ \t]*<!-- PRELAUNCH:ORIGINAL (.*?) -->\s*\n'
    r'[ \t]*<!-- PRELAUNCH:END -->[ \t]*\n',
    re.DOTALL
)

def restore(m):
    # Возвращаем исходный тег с отступом в два пробела, как в остальной вёрстке
    return '  ' + m.group(1).strip() + '\n'

new_html, n = pattern.subn(restore, html)

if n:
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(new_html)
PYEOF
        count=$((count+1))
    done
    echo "✅ Восстановлена мета robots: $count файлов"
fi

# ── robots.txt: боевая версия ──────────────────────────────────────
cat > robots.txt << 'EOF'
User-agent: *
Allow: /

Sitemap: https://pravimajstor.rs/sitemap.xml
EOF
echo "✅ robots.txt переведён в боевой режим (sitemap открыт)"

# ── Проверка: не осталось ли лишнего noindex ───────────────────────
#
# Исключения — страницы, где noindex стоит НАМЕРЕННО и должен остаться:
#   ./index.html — корневая страница-распределитель (JS-редирект на
#                  /ru/, /sr/, /en/). Индексировать нужно языковые
#                  версии, а не редирект. Стоит "noindex, follow":
#                  follow передаёт вес ссылок дальше.
#   ./404.html   — страница ошибки, в индексе не нужна.
left=$(grep -rl 'content="noindex' --include="index.html" . \
       | grep -vE '^\./index\.html$' || true)

if [ -n "$left" ]; then
    echo ""
    echo "⚠️  ВНИМАНИЕ: noindex остался в файлах:"
    echo "$left"
    echo "   Проверьте вручную — это может быть недоработка отката."
else
    echo "✅ Лишних noindex не осталось"
    echo "   (корневая index.html сохраняет noindex намеренно — это редирект)"
fi

echo ""
echo "─────────────────────────────────────────────"
echo "Дальше вручную:"
echo "  1. git add -A && git commit && git push"
echo "  2. Search Console → отправить sitemap.xml"
echo "  3. Проверить: https://pravimajstor.rs/robots.txt"
echo "─────────────────────────────────────────────"
