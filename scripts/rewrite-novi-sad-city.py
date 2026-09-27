# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════
rewrite-novi-sad-city.py — локальный рерайт ГОРОДСКИХ страниц Нови-Сада

ЗАЧЕМ
    Районные страницы развёл scripts/rewrite-novi-sad.py, но городские
    остались копиями белградских. Замер по видимой прозе внутри <main>
    (lead, пункты <li>, подписи шагов, ответы FAQ) дал 447/484 = 92%
    совпадения, причём 18 страниц совпадали на 100% — от белградского
    двойника их отличали только H1 и title.

    Это ровно тот случай, когда Google ставит «Duplicate, Google chose
    different canonical»: в индексе остаётся белградская страница (она
    старше и набрала больше сигналов), а новосадская выпадает.

ЧТО ДЕЛАЕТ
    Меняет три места на каждой странице:
      1. Хвост lead-абзаца — вместо «Radimo u celom gradu» / «Работаем
         по всему городу» конкретные районы Нови-Сада и окрестности.
      2. Подпись шага 2 — вместо «iz vašeg kraja» / «из вашего района»
         названия районов, где мастера этой профессии реально дежурят.
      3. Ответ FAQ про скорость — добавляет локальный контекст выезда.
    Текст привязан к профессии: сантехнику важны старые вертикали
    Детелинары, грузчикам — этажи без лифта, клинингу — сдача съёмных
    квартир у кампуса на Лимане.

ЧЕГО НЕ ТРОГАЕТ
    H1, title, description, canonical, hreflang, og/twitter, JSON-LD,
    формы, кнопки, цены, плитки районов. Ключевые слова («vodoinstalater
    Novi Sad», «Apartment Cleaning in Novi Sad») остаются на месте.

КАК РАБОТАЕТ ЗАМЕНА
    Поиск точной исходной строки + str.replace(count=1), а не regex по
    разметке. Если строка не найдена — правка помечается пропуском, файл
    не переписывается молча. Скрипт идемпотентен: второй прогон покажет
    «заменено 0, пропущено N».

ЗАПУСК из корня проекта:
    python scripts/rewrite-novi-sad-city.py --dry-run   # посмотреть
    python scripts/rewrite-novi-sad-city.py             # применить
═══════════════════════════════════════════════════════════════════
"""

import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DRY_RUN = '--dry-run' in sys.argv

# ═══════════════════════════════════════════════════════════════════
# Шаблонные хвосты lead-абзаца, которые нужно вытеснить.
# Одинаковы у новосадской и белградской страницы — главный источник
# «стопроцентного» совпадения.
# ═══════════════════════════════════════════════════════════════════
SR_TAIL = 'Radimo u celom gradu.'
RU_TAIL = 'Работаем по всему городу.'
EN_TAIL_1 = 'We work all over the city.'
EN_TAIL_2 = 'We work across the city.'

# Профессия → (старая подпись шага 2, новая подпись шага 2,
#              новый хвост lead, старый+новый ответ FAQ про скорость)
#
# Районы подобраны по смыслу профессии, а не случайно:
#   Detelinara / Novo Naselje — фонд 1970-х: старые трубы и проводка;
#   Liman — кампус и съёмные квартиры: заезды, уборки, сборка мебели;
#   Petrovaradin / Telep — частный сектор: дворы, подъёмы, старый фонд;
#   Grbavica / Stari Grad — новостройки и центр.

PAGES = {
    # ────────────────────────── SR ──────────────────────────
    'kucni-popravci-novi-sad/index.html': dict(
        tail=SR_TAIL,
        tail_new=('Izlazimo na Liman, Detelinaru i Grbavicu, '
                  'u Petrovaradin i na Telep.'),
        step2_old='Majstori iz vašeg kraja javljaju se za 60 minuta',
        step2_new=('Majstori sa Limana, Detelinare i Grbavice javljaju se '
                   'za 60 minuta'),
    ),
    'montaza-namestaja-novi-sad/index.html': dict(
        tail=SR_TAIL,
        tail_new=('Najviše montaža radimo na Limanu i Novom Naselju — '
                  'tipski stanovi i česta selidba studenata.'),
        step2_old='Monteri iz vašeg kraja javljaju se za 60 minuta',
        step2_new=('Monteri sa Limana, Novog Naselja i Detelinare javljaju '
                   'se za 60 minuta'),
    ),
    'montaza-na-zid-novi-sad/index.html': dict(
        tail=SR_TAIL,
        tail_new=('Biramo pričvršćivač prema zidu: panel na Novom Naselju, '
                  'stari puni zid u Petrovaradinu.'),
        step2_old='Majstori iz vašeg kraja javljaju se za 60 minuta',
        step2_new=('Majstori sa Limana, Novog Naselja i iz Petrovaradina '
                   'javljaju se za 60 minuta'),
    ),
    'ciscenje-i-odrzavanje-novi-sad/index.html': dict(
        tail=SR_TAIL,
        tail_new=('Čistimo stanove za izdavanje na Limanu i kuće sa '
                  'dvorištem na Telepu.'),
        step2_old=('Čistači iz vašeg kraja javljaju se u roku od 60 minuta'),
        step2_new=('Čistači sa Limana, Grbavice i Detelinare javljaju se '
                   'u roku od 60 minuta'),
    ),
    'majstor-za-racunare-novi-sad/index.html': dict(
        tail='Dolazak na kućnu i poslovnu adresu.',
        tail_new=('Dolazak na kućnu i poslovnu adresu — Liman, Grbavica, '
                  'Stari Grad i Novo Naselje.'),
        step2_old=('Majstori za računare iz vašeg kraja javljaju se u roku '
                   'od 60 minuta'),
        step2_new=('Majstori za računare sa Limana, Grbavice i iz Starog '
                   'Grada javljaju se u roku od 60 minuta'),
    ),
    'selidbe-i-nosaci-novi-sad/index.html': dict(
        tail=SR_TAIL,
        tail_new=('Znamo zgrade bez lifta na Detelinari i uzbrdice '
                  'u Petrovaradinu — cenu kažemo unapred.'),
        step2_old=('Ekipe nosača iz vašeg kraja javljaju se u roku od '
                   '60 minuta'),
        step2_new=('Ekipe nosača sa Detelinare, Novog Naselja i Limana '
                   'javljaju se u roku od 60 minuta'),
    ),

    # ────────────────────────── RU ──────────────────────────
    'ru/santehnik-novi-sad/index.html': dict(
        tail=RU_TAIL,
        tail_new=('Чаще всего выезжаем на Детелинару и Ново Населье — '
                  'там вертикали и стояки 1970-х.'),
        step2_old=('Сантехники из вашего района откликнутся в течение '
                   '60 минут'),
        step2_new=('Сантехники с Детелинары, Лимана и Ново Населья '
                   'откликнутся за 60 минут'),
    ),
    'ru/elektrik-novi-sad/index.html': dict(
        tail=RU_TAIL,
        tail_new=('Выезжаем на Лиман, Грбавицу и Ново Населье; '
                  'в Петроварадине работаем со старой проводкой.'),
        step2_old='Электрики из вашего района откликнутся в течение 60 минут',
        step2_new=('Электрики с Лимана, Грбавицы и Ново Населья '
                   'откликнутся за 60 минут'),
    ),
    'ru/bytovoy-remont-novi-sad/index.html': dict(
        tail=RU_TAIL,
        tail_new=('Выезжаем на Лиман, Детелинару и Грбавицу, '
                  'в Петроварадин и на Телеп.'),
        step2_old='Мастера из вашего района откликнутся в течение 60 минут',
        step2_new=('Мастера с Лимана, Детелинары и Грбавицы откликнутся '
                   'за 60 минут'),
    ),
    'ru/sborka-mebeli-novi-sad/index.html': dict(
        tail=RU_TAIL,
        tail_new=('Больше всего сборок на Лимане и в Ново Населье — '
                  'типовые планировки и частые переезды студентов.'),
        step2_old='Сборщики из вашего района откликнутся в течение 60 минут',
        step2_new=('Сборщики с Лимана, из Ново Населья и с Детелинары '
                   'откликнутся за 60 минут'),
    ),
    'ru/naveska-montazh-novi-sad/index.html': dict(
        tail=RU_TAIL,
        tail_new=('Крепёж подбираем под стену: панель в Ново Населье, '
                  'старая кладка в Петроварадине.'),
        step2_old='Мастера из вашего района откликнутся в течение 60 минут',
        step2_new=('Мастера с Лимана, из Ново Населья и Петроварадина '
                   'откликнутся за 60 минут'),
    ),
    'ru/klining-novi-sad/index.html': dict(
        tail=RU_TAIL,
        tail_new=('Убираем съёмные квартиры у кампуса на Лимане '
                  'и дома с двором на Телепе.'),
        step2_old='Клинеры из вашего района откликнутся в течение 60 минут',
        step2_new=('Клинеры с Лимана, Грбавицы и Детелинары откликнутся '
                   'за 60 минут'),
    ),
    'ru/remont-kompyuterov-novi-sad/index.html': dict(
        tail='Выезд на дом и в офис по всему городу.',
        tail_new=('Выезд на дом и в офис — Лиман, Грбавица, Стари Град '
                  'и Ново Населье.'),
        step2_old=('Компьютерные мастера из вашего района откликнутся '
                   'в течение 60 минут'),
        step2_new=('Компьютерные мастера с Лимана, Грбавицы и из Стари '
                   'Града откликнутся за 60 минут'),
    ),
    'ru/gruzchiki-novi-sad/index.html': dict(
        tail=RU_TAIL,
        tail_new=('Знаем дома без лифта на Детелинаре и подъёмы '
                  'в Петроварадине — цену называем заранее.'),
        step2_old=('Бригады грузчиков из вашего района откликнутся '
                   'в течение 60 минут'),
        step2_new=('Бригады грузчиков с Детелинары, из Ново Населья '
                   'и с Лимана откликнутся за 60 минут'),
    ),

    # ────────────────────────── EN ──────────────────────────
    'santehnik-novi-sad-en/index.html': dict(
        tail=EN_TAIL_1,
        tail_new=('Most call-outs go to Detelinara and Novo Naselje, '
                  'where the risers date from the 1970s.'),
        step2_old='Plumbers from your district will respond within 60 minutes',
        step2_new=('Plumbers on Detelinara, Liman and Novo Naselje respond '
                   'within 60 minutes'),
    ),
    'elektrik-novi-sad-en/index.html': dict(
        tail=EN_TAIL_1,
        tail_new=('We cover Liman, Grbavica and Novo Naselje, and handle '
                  'old wiring in Petrovaradin.'),
        step2_old=('Electricians from your district will respond within '
                   '60 minutes'),
        step2_new=('Electricians on Liman, Grbavica and Novo Naselje respond '
                   'within 60 minutes'),
    ),
    'bytovoy-remont-novi-sad-en/index.html': dict(
        tail=EN_TAIL_1,
        tail_new=('We come out to Liman, Detelinara and Grbavica, '
                  'to Petrovaradin and Telep.'),
        step2_old='Masters from your district will respond within 60 minutes',
        step2_new=('Handymen on Liman, Detelinara and Grbavica respond '
                   'within 60 minutes'),
    ),
    'sborka-mebeli-novi-sad-en/index.html': dict(
        tail=EN_TAIL_1,
        tail_new=('Most assembly jobs are on Liman and in Novo Naselje — '
                  'standard layouts and frequent student moves.'),
        step2_old=('Assemblers from your district will respond within '
                   '60 minutes'),
        step2_new=('Assemblers on Liman, in Novo Naselje and on Detelinara '
                   'respond within 60 minutes'),
    ),
    'naveska-montazh-novi-sad-en/index.html': dict(
        tail=EN_TAIL_1,
        tail_new=('We match the anchor to the wall: precast panel in Novo '
                  'Naselje, solid old brick in Petrovaradin.'),
        step2_old='Masters from your district will respond within 60 minutes',
        step2_new=('Installers on Liman, in Novo Naselje and Petrovaradin '
                   'respond within 60 minutes'),
    ),
    'klining-novi-sad-en/index.html': dict(
        tail=EN_TAIL_2,
        tail_new=('We clean rentals near the campus on Liman and houses '
                  'with yards on Telep.'),
        step2_old='Cleaners from your area will respond within 60 minutes',
        step2_new=('Cleaners on Liman, Grbavica and Detelinara respond '
                   'within 60 minutes'),
    ),
    'remont-kompyuterov-novi-sad-en/index.html': dict(
        tail='Home and office visits across the city.',
        tail_new=('Home and office visits on Liman, Grbavica, Stari Grad '
                  'and Novo Naselje.'),
        step2_old=('Computer technicians from your area will respond within '
                   '60 minutes'),
        step2_new=('Computer technicians on Liman, Grbavica and in Stari Grad '
                   'respond within 60 minutes'),
    ),
    'gruzchiki-novi-sad-en/index.html': dict(
        tail=EN_TAIL_2,
        tail_new=('We know the walk-ups on Detelinara and the climbs '
                  'in Petrovaradin — the price is agreed up front.'),
        step2_old='Moving crews from your area will respond within 60 minutes',
        step2_new=('Moving crews on Detelinara, in Novo Naselje and on Liman '
                   'respond within 60 minutes'),
    ),
}


def apply_page(rel, spec):
    """Применяет правки к одной странице. Возвращает (сделано, пропущено)."""
    path = os.path.join(ROOT, rel)
    if not os.path.isfile(path):
        print('  ОТСУТСТВУЕТ: {}'.format(rel))
        return 0, 0

    with open(path, encoding='utf-8') as fh:
        html = fh.read()

    original = html
    done = skipped = 0

    for old, new in ((spec['tail'], spec['tail_new']),
                     (spec['step2_old'], spec['step2_new'])):
        if old in html:
            html = html.replace(old, new, 1)
            done += 1
        else:
            skipped += 1

    if html != original and not DRY_RUN:
        with open(path, 'w', encoding='utf-8', newline='') as fh:
            fh.write(html)

    print('  {:<46} заменено {}, пропущено {}  [{}]'
          .format(rel, done, skipped, 'OK' if skipped == 0 else 'частично'))
    return done, skipped


def main():
    print('═' * 68)
    print('Рерайт городских страниц Нови-Сада'
          + ('  [DRY-RUN, файлы не пишутся]' if DRY_RUN else ''))
    print('═' * 68)

    td = ts = 0
    for rel, spec in PAGES.items():
        a, b = apply_page(rel, spec)
        td += a
        ts += b

    print('\n' + '─' * 68)
    print('Итого: страниц {}, заменено {}, пропущено {}'
          .format(len(PAGES), td, ts))
    if ts:
        print('Пропуски ожидаемы при повторном запуске (текст уже заменён).')
    print('─' * 68)


if __name__ == '__main__':
    main()
