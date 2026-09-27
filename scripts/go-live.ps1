<#
═══════════════════════════════════════════════════════════════════
 go-live.ps1 — снятие защиты от индексации перед запуском сайта
                (версия для Windows PowerShell 5.1)

 Аналог scripts/go-live.sh для тех, у кого нет bash. Делает то же
 самое и в том же порядке, чтобы результат двух скриптов совпадал:

   1. Во всех index.html убирает блок PRELAUNCH, возвращая исходную
      мету robots из комментария PRELAUNCH:ORIGINAL.
   2. Раскомментирует строку Sitemap в robots.txt (боевая версия).
   3. Обновляет <lastmod> в sitemap.xml на текущую дату.
   4. Прогоняет проверку целостности ссылок.

 ⚠️ ЗАПУСКАТЬ ТОЛЬКО когда в боте набрано 20–30 мастеров.
    Открытый сайт без мастеров = заявка уходит в пустоту: клиент не
    дожидается звонка и больше не возвращается.

 ЗАПУСК из корня проекта:
    powershell -ExecutionPolicy Bypass -File scripts\go-live.ps1
    powershell -ExecutionPolicy Bypass -File scripts\go-live.ps1 -DryRun

 -DryRun показывает, что будет изменено, но не пишет файлы.
═══════════════════════════════════════════════════════════════════
#>

[CmdletBinding()]
param(
    # Прогон без записи: посмотреть объём правок перед боевым запуском
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'

# Переходим в корень проекта (на уровень выше scripts/), чтобы скрипт
# работал одинаково независимо от текущего каталога вызова.
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

if ($DryRun) {
    Write-Host ''
    Write-Host '=== DRY-RUN: файлы не изменяются ===' -ForegroundColor Yellow
}
Write-Host ''
Write-Host "Корень проекта: $root"
Write-Host ('─' * 62)

# ═══════════════════════════════════════════════════════════════════
# UTF-8 без BOM. Set-Content -Encoding utf8 в PS 5.1 добавляет BOM,
# а BOM в начале index.html выводится браузером как мусорный символ
# перед <!DOCTYPE>. Поэтому пишем через .NET с явным UTF8Encoding($false).
# ═══════════════════════════════════════════════════════════════════
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)

function Write-TextFile {
    param([string]$Path, [string]$Content)
    [System.IO.File]::WriteAllText($Path, $Content, $script:utf8NoBom)
}

# ═══════════════════════════════════════════════════════════════════
# ШАГ 1. Возврат боевой меты robots
#
# Структура блока в каждом файле:
#   <!-- PRELAUNCH:START — убрать этот блок при запуске... -->
#   <meta name="robots" content="noindex, nofollow">
#   <!-- PRELAUNCH:ORIGINAL <meta name="robots" content="index, follow..."> -->
#   <!-- PRELAUNCH:END -->
#
# Заменяем весь блок на тег из PRELAUNCH:ORIGINAL. Именно возвращаем
# сохранённый тег, а не пишем "index, follow" руками: у страниц разные
# директивы (max-snippet, max-image-preview), и своя версия их потеряла бы.
# ═══════════════════════════════════════════════════════════════════
Write-Host ''
Write-Host 'ШАГ 1. Мета robots: снимаем предзапускной noindex' -ForegroundColor Cyan

# (?s) — точка матчит перевод строки, блок ищем целиком.
# \r?\n — файлы могут лежать и с CRLF, и с LF.
# Шаблон собран конкатенацией одинарных кавычек: здесь нет ни одной
# подстановки, а here-string с таким содержимым ломает парсер PS 5.1.
$prelaunchPattern = '(?s)[ \t]*<!--[ ]*PRELAUNCH:START.*?-->[ \t]*\r?\n' +
                    '[ \t]*<meta\s+name="robots"[^>]*>[ \t]*\r?\n' +
                    '[ \t]*<!--[ ]*PRELAUNCH:ORIGINAL[ ]*(?<orig><meta[^>]*>)[ ]*-->[ \t]*\r?\n' +
                    '[ \t]*<!--[ ]*PRELAUNCH:END[ ]*-->[ \t]*\r?\n'
$prelaunchRe = [regex]$prelaunchPattern

$restored = 0
$failed   = @()

# ── Что считаем страницами сайта ───────────────────────────────────
# Служебные каталоги, начинающиеся с точки, из обхода исключаем.
# Это не косметика: в .claude/worktrees лежит рабочая копия всего
# сайта (118 своих index.html). Без фильтра скрипт «починил» бы мету
# и там — правки ушли бы в gitignore-каталог, а отчёт об остатках
# noindex утонул бы в чужих путях.
function Get-SitePages {
    param([string]$Filter)
    Get-ChildItem -Path $root -Filter $Filter -Recurse -File |
        Where-Object {
            $rel = $_.FullName.Substring($root.Length + 1)
            # Ни один сегмент пути не начинается с точки
            -not ($rel -split '[\\/]' | Where-Object { $_.StartsWith('.') })
        }
}

# Ищем только index.html — остальные файлы (404.html, google.html) правим
# отдельно и осознанно, у них нет блоков PRELAUNCH.
$htmlFiles = Get-SitePages -Filter 'index.html'

foreach ($file in $htmlFiles) {
    $html = [System.IO.File]::ReadAllText($file.FullName)

    if ($html -notmatch 'PRELAUNCH:START') { continue }

    # Отступ в два пробела — как в остальной вёрстке проекта
    $new = $prelaunchRe.Replace($html, {
        param($m)
        '  ' + $m.Groups['orig'].Value + "`n"
    })

    if ($new -eq $html) {
        # Маркер есть, а шаблон не сработал — вёрстка отличается.
        # Молча пропускать нельзя: страница останется с noindex.
        $failed += $file.FullName.Substring($root.Length + 1)
        continue
    }

    if (-not $DryRun) { Write-TextFile -Path $file.FullName -Content $new }
    $restored++
}

Write-Host "  Восстановлена мета robots: $restored файл(ов)"

if ($failed.Count -gt 0) {
    Write-Host ''
    Write-Host '  ⚠️  Блок PRELAUNCH найден, но не разобран:' -ForegroundColor Red
    $failed | ForEach-Object { Write-Host "       $_" }
    Write-Host '     Проверьте эти файлы вручную — иначе останутся с noindex.' -ForegroundColor Red
}

# ═══════════════════════════════════════════════════════════════════
# ШАГ 2. Боевой robots.txt
#
# На предзапуске краулинг РАЗРЕШЁН намеренно: закрытому роботу нечем
# прочитать мету noindex со страницы. Поэтому меняется только строка
# Sitemap — её на предзапуске держали закомментированной.
# ═══════════════════════════════════════════════════════════════════
Write-Host ''
Write-Host 'ШАГ 2. robots.txt: открываем карту сайта' -ForegroundColor Cyan

$robotsPath = Join-Path $root 'robots.txt'
# Собираем через -join "`n": LF-переводы строк без оглядки на то, чем
# закончится here-string в конкретной кодировке файла.
$robotsBody = (@(
    'User-agent: *',
    'Allow: /',
    '',
    'Sitemap: https://pravimajstor.rs/sitemap.xml',
    ''
) -join "`n")

if (Test-Path $robotsPath) {
    $current = [System.IO.File]::ReadAllText($robotsPath)
    if ($current -match '(?m)^\s*Sitemap:') {
        Write-Host '  Sitemap уже раскомментирован — файл переписан в боевой вид'
    } else {
        Write-Host '  Sitemap был закомментирован — включаем'
    }
} else {
    Write-Host '  robots.txt отсутствовал — создаём'
}

if (-not $DryRun) { Write-TextFile -Path $robotsPath -Content $robotsBody }
Write-Host '  ✅ robots.txt переведён в боевой режим'

# ═══════════════════════════════════════════════════════════════════
# ШАГ 3. Актуальный <lastmod> в sitemap.xml
#
# Дата в формате W3C (YYYY-MM-DD), как того ждёт протокол sitemap.
# Ставим одну и ту же дату всем URL: на запуске содержимое действительно
# публикуется целиком, а расхождение дат ничего не даёт.
# ═══════════════════════════════════════════════════════════════════
Write-Host ''
Write-Host 'ШАГ 3. sitemap.xml: обновляем lastmod' -ForegroundColor Cyan

$sitemapPath = Join-Path $root 'sitemap.xml'
$today = (Get-Date).ToString('yyyy-MM-dd')

if (Test-Path $sitemapPath) {
    $xml = [System.IO.File]::ReadAllText($sitemapPath)

    $locCount = ([regex]'<loc>').Matches($xml).Count
    $before   = ([regex]'<lastmod>').Matches($xml).Count

    $xml = [regex]::Replace($xml, '<lastmod>[^<]*</lastmod>', "<lastmod>$today</lastmod>")

    if (-not $DryRun) { Write-TextFile -Path $sitemapPath -Content $xml }

    Write-Host "  URL в карте: $locCount, обновлено lastmod: $before → дата $today"

    # Каждому <loc> положен свой <lastmod>: расхождение означает, что
    # страницу добавили в карту руками и забыли дату.
    if ($locCount -ne $before) {
        Write-Host "  ⚠️  <loc> ($locCount) и <lastmod> ($before) не совпадают — проверьте sitemap.xml" -ForegroundColor Yellow
    }
} else {
    Write-Host '  ⚠️  sitemap.xml не найден' -ForegroundColor Red
}

# ═══════════════════════════════════════════════════════════════════
# ШАГ 4. Контроль: не остался ли лишний noindex
#
# Исключения, где noindex стоит НАМЕРЕННО и должен остаться:
#   index.html (корень) — страница-распределитель с JS-редиректом на
#                         /ru/, /sr/, /en/. Индексировать нужно языковые
#                         версии. "noindex, follow" — follow передаёт вес.
#   404.html            — страница ошибки, в индексе не нужна.
# ═══════════════════════════════════════════════════════════════════
Write-Host ''
Write-Host 'ШАГ 4. Проверка остатков noindex' -ForegroundColor Cyan

$allowedNoindex = @('index.html', '404.html')   # относительно корня

# Тот же фильтр служебных каталогов, что и в шаге 1 — иначе в отчёт
# попадут страницы из .claude/worktrees, которые сайтом не являются.
$leftovers = Get-SitePages -Filter '*.html' |
    Where-Object {
        $rel = $_.FullName.Substring($root.Length + 1)
        # Пропускаем намеренные исключения (только в корне, не во вложенных)
        if ($allowedNoindex -contains $rel) { return $false }
        (Select-String -Path $_.FullName -Pattern 'content="noindex' -Quiet -SimpleMatch)
    } |
    ForEach-Object { $_.FullName.Substring($root.Length + 1) }

if ($leftovers) {
    Write-Host '  ⚠️  noindex остался в файлах:' -ForegroundColor Yellow
    $leftovers | ForEach-Object { Write-Host "       $_" }
    if ($DryRun) {
        Write-Host '     (ожидаемо в DRY-RUN: файлы не переписывались)'
    } else {
        Write-Host '     Проверьте вручную — возможно, недоработка откатa.' -ForegroundColor Yellow
    }
} else {
    Write-Host '  ✅ Лишних noindex не осталось'
    Write-Host '     (корневой index.html и 404.html сохраняют noindex намеренно)'
}

# ═══════════════════════════════════════════════════════════════════
# ШАГ 5. Целостность ссылок
#
# check-links.sh написан на bash+python. Если bash есть (Git for Windows
# кладёт его в PATH) — запускаем как есть. Если нет — вызываем питоновскую
# часть нельзя, поэтому честно сообщаем, а не делаем вид, что проверили.
# ═══════════════════════════════════════════════════════════════════
Write-Host ''
Write-Host 'ШАГ 5. Проверка целостности ссылок' -ForegroundColor Cyan

$bash = Get-Command bash -ErrorAction SilentlyContinue

if ($bash) {
    & $bash.Source 'scripts/check-links.sh'
    if ($LASTEXITCODE -ne 0) {
        Write-Host ''
        Write-Host "  ⚠️  check-links.sh вернул код $LASTEXITCODE — есть битые ссылки." -ForegroundColor Red
        Write-Host '     Исправьте ДО пуша: Google увидит их сразу после открытия индексации.' -ForegroundColor Red
    }
} else {
    Write-Host '  ⚠️  bash не найден — проверка пропущена.' -ForegroundColor Yellow
    Write-Host '     Запустите вручную:  bash scripts/check-links.sh' -ForegroundColor Yellow
}

# ═══════════════════════════════════════════════════════════════════
Write-Host ''
Write-Host ('─' * 62)
if ($DryRun) {
    Write-Host 'DRY-RUN завершён. Файлы не изменены.' -ForegroundColor Yellow
    Write-Host 'Боевой запуск: powershell -ExecutionPolicy Bypass -File scripts\go-live.ps1'
} else {
    Write-Host 'Дальше вручную:' -ForegroundColor Green
    Write-Host '  1. git add -A ; git commit -m "feat: go-live, открываем индексацию" ; git push'
    Write-Host '  2. Search Console → отправить sitemap.xml'
    Write-Host '  3. Проверить: https://pravimajstor.rs/robots.txt'
    Write-Host '  4. Проверить мету на любой странице: должно быть index, follow'
}
Write-Host ('─' * 62)
Write-Host ''
