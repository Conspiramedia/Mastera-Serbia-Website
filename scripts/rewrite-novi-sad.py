# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════
rewrite-novi-sad.py — локальный рерайт страниц Нови-Сада

ЗАЧЕМ
    Страницы Нови-Сада собирались копированием белградских и друг из
    друга. В результате видимая проза совпадала побайтово:
        • 8 районных страниц SR — 7/7 lead, 28/28 FAQ, 49/56 пунктов;
        • 8 районных страниц RU — 7/7 lead, 28/28 FAQ, 56/56 пунктов;
        • городские vodoinstalater/elektricar — 5/5 FAQ и 7/8 пунктов
          совпадают с белградскими.
    Для Google это «Duplicate, Google chose different canonical»:
    в индекс попадает одна страница кластера, остальные выпадают.

ЧТО ДЕЛАЕТ
    Заменяет РОВНО перечисленные ниже текстовые блоки внутри <main>:
    lead-абзац, пункты <li> списка услуг, подписи шагов и ответы FAQ.
    Каждому району — свой текст с местными ориентирами и спецификой
    застройки, поэтому страницы расходятся не косметически, а по смыслу.

ЧЕГО НЕ ТРОГАЕТ (сознательно)
    H1, title, description, canonical, hreflang, og/twitter, JSON-LD,
    формы, кнопки, цены, структуру HTML. Ключевые слова
    («vodoinstalater Novi Sad», «мастер на час») остаются на месте —
    цель рерайта уникальность текста, а не смена семантики.

КАК РАБОТАЕТ ЗАМЕНА
    Не regex по разметке, а поиск точной исходной строки и подстановка
    новой (str.replace с count=1). Если исходная строка не найдена —
    правка помечается как SKIP и файл не переписывается молча. Это
    защита от тихой порчи вёрстки при повторном прогоне: скрипт
    идемпотентен, второй запуск сообщит «уже применено».

ЗАПУСК из корня проекта:
    python scripts/rewrite-novi-sad.py          # применить
    python scripts/rewrite-novi-sad.py --dry-run  # только показать
═══════════════════════════════════════════════════════════════════
"""

import os
import sys
import io

# Вывод в UTF-8: консоль Windows по умолчанию cp1251 и ломает кириллицу
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

DRY_RUN = '--dry-run' in sys.argv

# ═══════════════════════════════════════════════════════════════════
# Общие («белградские») формулировки, которые нужно вытеснить.
# Ключ — то, что лежит в файлах сейчас, одинаково на всех страницах.
# ═══════════════════════════════════════════════════════════════════

# --- SR: районные страницы «majstor na sat» ------------------------
SR_LEAD_OLD = (
    'Okačiti, pričvrstiti, učvrstiti, fiksirati ili pomoći u kućnim '
    'poslovima?<br>Pozovite univerzalnog majstora na sat — obaviće više '
    'sitnih poslova u jednoj poseti.<br>Ostavite prijavu — majstor se '
    'javlja za 60 minuta. Radimo po celom gradu.'
)

SR_STEP1_OLD = ('<p class="step-description">Opišite šta vam treba: '
                'sklapanje ormara, kačenje polica, lepljenje tapeta</p>')
SR_STEP3_OLD = ('<p class="step-description">Proverite rejting i recenzije, '
                'izaberite odgovarajućeg po ceni i vremenu</p>')

SR_LI_HANG_OLD = ('<li><strong>Pažljivo kačenje</strong> — televizor, police, '
                  'ogledala i slike u novogradnji i renoviranim stanovima, '
                  'uz izbor pričvršćivača prema tipu zida</li>')
SR_LI_HOME_OLD = ('<li><strong>Pomoć u kući i kućnim poslovima</strong> — '
                  '„majstor na sat": svakodnevne sitnice i jednokratni '
                  'zadaci gde nije potreban profilni specijalista</li>')

SR_FAQ_SPEED_OLD = ('<div class="faq-answer"><p>Prvi odgovor — u proseku '
                    '<strong>15–60 minuta</strong>. Možete navesti željeno '
                    'vreme dolaska u opisu prijave.</p></div>')
SR_FAQ_MAT_OLD = ('<div class="faq-answer"><p>Zavisi od posla. Majstor obično '
                  'dolazi sa svojim alatom, ali materijal (tiplove, šrafove, '
                  'boju) treba pripremiti unapred ili se dogovoriti sa '
                  'majstorom prilikom javljanja.</p></div>')

# --- RU: районные страницы «мастер на час» ------------------------
RU_LEAD_OLD = (
    'Повесить, прикрутить, подтянуть, закрепить или помочь по хозяйству?<br>'
    'Вызовите универсального мастера на час — сделает несколько мелких дел '
    'за один визит.<br>Оставьте заявку — мастер откликнется за 60 минут. '
    'Работаем по всему городу.'
)

RU_STEP1_OLD = ('<p class="step-description">Опишите что нужно сделать: '
                'собрать шкаф, повесить полки, поклеить обои</p>')
RU_STEP2_OLD = ('<p class="step-description">Мастера из вашего района '
                'откликнутся в течение 60 минут с ценой</p>')
# На части страниц шаг 2 уже локализован («Мастера с Лимана…»), тогда
# эта замена пропускается — это ожидаемо, не ошибка.
RU_STEP3_OLD = ('<p class="step-description">Посмотрите рейтинг и отзывы, '
                'выберите подходящего по цене и времени</p>')

RU_LI_HANG_OLD = ('<li><strong>Аккуратная навеска</strong> — ТВ, полки, '
                  'зеркала и картины в новостройках и отремонтированных '
                  'квартирах с учётом состояния стен</li>')
RU_LI_HOME_OLD = ('<li><strong>Помощь по дому и хозяйству</strong> — '
                  '«муж на час»: бытовые мелочи и разовые поручения там, '
                  'где не нужен профильный специалист</li>')

RU_FAQ_SPEED_OLD = ('<div class="faq-answer"><p>Первый отклик — в среднем '
                    '<strong>15–60 минут</strong>. Можно указать удобное '
                    'время приезда в описании заявки.</p></div>')
RU_FAQ_MAT_OLD = ('<div class="faq-answer"><p>Зависит от задачи. Обычно мастер '
                  'приезжает со своим инструментом, но материалы (дюбели, '
                  'саморезы, краску) нужно подготовить заранее или уточнить '
                  'у мастера при отклике.</p></div>')

# ═══════════════════════════════════════════════════════════════════
# Портреты районов. Из них собираются уникальные тексты.
#   sr_loc  — местный падеж «na Limanu» / «u Petrovaradinu»
#   sr_from — «sa Limana» / «iz Petrovaradina» (откуда мастер)
#   ru_loc / ru_from — то же по-русски
#   housing — чем застройка отличается (главный источник уникальности)
#   marks   — 2–3 ориентира для текста шагов и FAQ
# ═══════════════════════════════════════════════════════════════════
DISTRICTS = {
    'liman': {
        'sr_name': 'Liman', 'sr_loc': 'na Limanu', 'sr_from': 'sa Limana',
        'ru_name': 'Лиман', 'ru_to': 'на Лиман', 'ru_loc': 'на Лимане', 'ru_from': 'с Лимана',
        'sr_housing': 'studentski stanovi i gusta blokovska gradnja uz Dunav',
        'ru_housing': 'студенческое жилье и плотная блочная застройка у Дуная',
        'sr_marks': 'Štrand, Limanski park, kampus Univerziteta',
        'ru_marks': 'Штранд, Лиманский парк, кампус университета',
        'sr_task': 'opremanje studentskog stana, kačenje polica u maloj sobi',
        'ru_task': 'обустройство студенческой квартиры, полки в маленькой комнате',
        'sr_wall': 'betonski paneli i pregrade od gips-kartona u studentskim stanovima',
        'ru_wall': 'бетонные панели и гипсокартонные перегородки съёмных квартир',
    },
    'detelinara': {
        'sr_name': 'Detelinara', 'sr_loc': 'na Detelinari', 'sr_from': 'sa Detelinare',
        'ru_name': 'Детелинара', 'ru_to': 'на Детелинару', 'ru_loc': 'на Детелинаре', 'ru_from': 'с Детелинары',
        'sr_housing': 'spavaći kraj sa blokovima iz 1970-ih i starim instalacijama',
        'ru_housing': 'спальный район с домами 1970-х и старыми коммуникациями',
        'sr_marks': 'pijaca Detelinara, Bulevar oslobođenja, kvartovski park',
        'ru_marks': 'рынок Детелинара, Бульвар освобождения, квартальный парк',
        'sr_task': 'popravka starog nameštaja, zamena dotrajale armature',
        'ru_task': 'ремонт старой мебели, замена изношенной фурнитуры',
        'sr_wall': 'nosivi beton starih blokova, gde običan tipl ne drži',
        'ru_wall': 'несущий бетон старых блоков, где обычный дюбель не держит',
    },
    'telep': {
        'sr_name': 'Telep', 'sr_loc': 'na Telepu', 'sr_from': 'sa Telepa',
        'ru_name': 'Телеп', 'ru_to': 'на Телеп', 'ru_loc': 'на Телепе', 'ru_from': 'с Телепа',
        'sr_housing': 'privatne kuće sa dvorištima i pomoćnim prostorijama',
        'ru_housing': 'частные дома с дворами и подсобными помещениями',
        'sr_marks': 'Futoški put, Telepska pijaca, nasip prema Dunavu',
        'ru_marks': 'Футошская дорога, рынок Телепа, насыпь к Дунаю',
        'sr_task': 'poslovi u dvorištu, garaži i letnjoj kuhinji',
        'ru_task': 'работы во дворе, гараже и летней кухне',
        'sr_wall': 'ciglani zidovi kuća i drvene konstrukcije u dvorištu',
        'ru_wall': 'кирпичные стены домов и деревянные конструкции во дворе',
    },
    'petrovaradin': {
        'sr_name': 'Petrovaradin', 'sr_loc': 'u Petrovaradinu', 'sr_from': 'iz Petrovaradina',
        'ru_name': 'Петроварадин', 'ru_to': 'в Петроварадин', 'ru_loc': 'в Петроварадине', 'ru_from': 'из Петроварадина',
        'sr_housing': 'stari fond pod Tvrđavom: debeli zidovi, specifični krovovi i cevi',
        'ru_housing': 'старый фонд под Крепостью: толстые стены, особые крыши и трубы',
        'sr_marks': 'Petrovaradinska tvrđava, Podgrađe, uzbrdice prema Sremskoj strani',
        'ru_marks': 'Петроварадинская крепость, Подградье, подъёмы к сремской стороне',
        'sr_task': 'poslovi u starim kućama, gde standardno rešenje ne odgovara',
        'ru_task': 'работы в старых домах, где стандартное решение не подходит',
        'sr_wall': 'stari puni zid i svodovi, gde je potrebno bušenje bez oštećenja',
        'ru_wall': 'старая полнотелая кладка и своды — сверлить нужно аккуратно',
    },
    'grbavica': {
        'sr_name': 'Grbavica', 'sr_loc': 'na Grbavici', 'sr_from': 'sa Grbavice',
        'ru_name': 'Грбавица', 'ru_to': 'на Грбавицу', 'ru_loc': 'на Грбавице', 'ru_from': 'с Грбавицы',
        'sr_housing': 'novogradnja i renovirani stanovi u mirnom delu uz Liman',
        'ru_housing': 'новостройки и свежие ремонты в тихой части у Лимана',
        'sr_marks': 'Bulevar cara Lazara, Futoški park, obala Dunava',
        'ru_marks': 'Бульвар царя Лазаря, Футошский парк, берег Дуная',
        'sr_task': 'montaža u novom stanu bez oštećenja svežih površina',
        'ru_task': 'монтаж в новой квартире без повреждения свежей отделки',
        'sr_wall': 'sveže gletovani zidovi i gips-karton u novogradnji',
        'ru_wall': 'свежая шпаклёвка и гипсокартон в новостройках',
    },
    'podbara': {
        'sr_name': 'Podbara', 'sr_loc': 'na Podbari', 'sr_from': 'sa Podbare',
        'ru_name': 'Подбара', 'ru_to': 'на Подбару', 'ru_loc': 'на Подбаре', 'ru_from': 'с Подбары',
        'sr_housing': 'niske stare kuće i mali stanovi blizu centra',
        'ru_housing': 'малоэтажный старый фонд и небольшие квартиры у центра',
        'sr_marks': 'Almaška crkva, Podbarska pijaca, Beogradski kej',
        'ru_marks': 'Алмашская церковь, рынок Подбары, Белградская набережная',
        'sr_task': 'sitne popravke u stanu male kvadrature',
        'ru_task': 'мелкий ремонт в квартире небольшой площади',
        'sr_wall': 'stara cigla i malter koji se lako kruni',
        'ru_wall': 'старый кирпич и штукатурка, которая легко крошится',
    },
    'novo-naselje': {
        'sr_name': 'Novo Naselje', 'sr_loc': 'na Novom Naselju', 'sr_from': 'sa Novog Naselja',
        'ru_name': 'Ново Населье', 'ru_to': 'в Ново Населье', 'ru_loc': 'в Ново Населье', 'ru_from': 'из Ново Населья',
        'sr_housing': 'veliki soliteri i tipski stanovi („Bistrica")',
        'ru_housing': 'высотки и типовые квартиры («Бистрица»)',
        'sr_marks': 'Bulevar Evrope, tržni centar, kvartovske škole',
        'ru_marks': 'Бульвар Европы, торговый центр, квартальные школы',
        'sr_task': 'tipska montaža nameštaja u stanovima istog rasporeda',
        'ru_task': 'типовая сборка мебели в квартирах одной планировки',
        'sr_wall': 'montažni betonski paneli solitera',
        'ru_wall': 'сборные бетонные панели высоток',
    },
    'stari-grad': {
        'sr_name': 'Stari Grad', 'sr_loc': 'u Starom Gradu', 'sr_from': 'iz Starog Grada',
        'ru_name': 'Стари Град', 'ru_to': 'в Стари Град', 'ru_loc': 'в Стари Граде', 'ru_from': 'из Стари Града',
        'sr_housing': 'austrougarske zgrade u centru, visoki plafoni, zaštićene fasade',
        'ru_housing': 'австро-венгерские дома в центре, высокие потолки, охранные фасады',
        'sr_marks': 'Zmaj Jovina, Trg slobode, Dunavski park, Novosadski sajam',
        'ru_marks': 'Змай Йовина, площадь Свободы, Дунайский парк, Новосадская ярмарка',
        'sr_task': 'poslovi u stanu sa visokim plafonima i starim stolarijom',
        'ru_task': 'работы в квартире с высокими потолками и старой столяркой',
        'sr_wall': 'zidovi debeli preko pola metra i drvene tavanice',
        'ru_wall': 'стены толще полуметра и деревянные перекрытия',
    },
}


def sr_district_edits(d):
    """Правки для сербской районной страницы."""
    return [
        # lead: вместо «radimo po celom gradu» — конкретный район и застройка
        (SR_LEAD_OLD,
         'Okačiti, pričvrstiti, zategnuti ili pomoći u kući {loc}?<br>'
         'Univerzalni majstor obavlja nekoliko sitnih poslova u jednoj '
         'poseti — bez čekanja ekipe za velike radove.<br>'
         'Brza intervencija {loc} i u okolnim delovima Novog Sada: '
         'ostavite prijavu, majstor {frm} javlja se za 60 minuta.'
         .format(loc=d['sr_loc'], frm=d['sr_from'])),

        # шаг 1: типичная для района задача вместо общего списка.
        # Адрес формулируем через готовый местный падеж (sr_loc) —
        # так не нужно склонять название района в коде.
        (SR_STEP1_OLD,
         '<p class="step-description">Opišite zadatak — {task}. '
         'Navedite adresu {loc} i kontakt</p>'
         .format(task=d['sr_task'], loc=d['sr_loc'])),

        # шаг 3: ориентиры района
        (SR_STEP3_OLD,
         '<p class="step-description">Uporedite rejting i recenzije — '
         'majstori koji rade u okolini lokacija: {marks}</p>'.format(marks=d['sr_marks'])),

        # пункт про навеску: тип стен района
        (SR_LI_HANG_OLD,
         '<li><strong>Pažljivo kačenje</strong> — televizor, police, ogledala '
         'i slike {loc}, uz izbor pričvršćivača prema tipu zida: {wall}</li>'
         .format(loc=d['sr_loc'], wall=d['sr_wall'])),

        # пункт про помощь по дому: специфика фонда
        (SR_LI_HOME_OLD,
         '<li><strong>Pomoć u kući {loc}</strong> — „majstor na sat" za '
         'svakodnevne sitnice. Ovde {housing} — zato tražite majstora sa '
         'iskustvom rada u ovakvom fondu</li>'
         .format(loc=d['sr_loc'], housing=d['sr_housing'])),

        # FAQ «как быстро»: район вместо города
        (SR_FAQ_SPEED_OLD,
         '<div class="faq-answer"><p>Prvi odgovor — u proseku '
         '<strong>15–60 minuta</strong>. Majstori koji su već {loc} '
         'stižu najbrže, jer ne putuju sa druge strane Novog Sada. '
         'Željeno vreme dolaska navedite u opisu prijave.</p></div>'
         .format(loc=d['sr_loc'])),

        # FAQ «материалы»: привязка к стенам района
        (SR_FAQ_MAT_OLD,
         '<div class="faq-answer"><p>Majstor dolazi sa svojim alatom, a '
         'materijal (tiplove, šrafove, silikon) pripremite unapred ili se '
         'dogovorite prilikom javljanja. {loc_cap} je ovo važno: {wall} — '
         'pričvršćivač se bira na licu mesta, posle pregleda.</p></div>'
         .format(loc_cap=d['sr_loc'][0].upper() + d['sr_loc'][1:],
                 wall=d['sr_wall'])),
    ]


def ru_district_edits(d):
    """Правки для русской районной страницы."""
    return [
        (RU_LEAD_OLD,
         'Повесить, прикрутить, подтянуть или помочь по хозяйству {loc}?<br>'
         'Универсальный мастер сделает несколько мелких дел за один визит — '
         'не нужно вызывать бригаду под большой ремонт.<br>'
         'Быстрый выезд {to} и по соседним районам Нови-Сада: оставьте '
         'заявку, мастер {frm} откликнется за 60 минут.'
         # loc — предложный падеж («по хозяйству на Детелинаре»),
         # to — винительный («выезд на Детелинару»), frm — откуда мастер
         .format(loc=d['ru_loc'], to=d['ru_to'], frm=d['ru_from'])),

        (RU_STEP1_OLD,
         '<p class="step-description">Опишите задачу — {task}. '
         'Укажите адрес {loc} и контакт</p>'
         .format(task=d['ru_task'], loc=d['ru_loc'])),

        (RU_STEP2_OLD,
         '<p class="step-description">Мастера {loc} откликнутся за 60 минут '
         'с ценой</p>'.format(loc=d['ru_loc'])),

        (RU_STEP3_OLD,
         '<p class="step-description">Сравните рейтинг и отзывы — мастера, '
         'работающие у {marks}</p>'.format(marks=d['ru_marks'])),

        (RU_LI_HANG_OLD,
         '<li><strong>Аккуратная навеска</strong> — ТВ, полки, зеркала и '
         'картины {loc}, с подбором крепежа под {wall}</li>'
         .format(loc=d['ru_loc'], wall=d['ru_wall'])),

        (RU_LI_HOME_OLD,
         '<li><strong>Помощь по дому {loc}</strong> — «мастер на час» для '
         'бытовых мелочей: {housing} требуют мастера с опытом работы '
         'именно в таком фонде</li>'
         .format(loc=d['ru_loc'], housing=d['ru_housing'])),

        (RU_FAQ_SPEED_OLD,
         '<div class="faq-answer"><p>Первый отклик — в среднем '
         '<strong>15–60 минут</strong>. Быстрее всех приезжают мастера, '
         'которые уже работают {loc}, — им не нужно ехать с другого конца '
         'Нови-Сада. Желаемое время визита укажите в описании '
         'заявки.</p></div>'.format(loc=d['ru_loc'])),

        (RU_FAQ_MAT_OLD,
         '<div class="faq-answer"><p>Мастер приезжает со своим инструментом, '
         'а материалы (дюбели, саморезы, герметик) подготовьте заранее или '
         'обсудите при отклике. {loc_cap} это особенно важно: {wall}, '
         'поэтому крепёж подбирают на месте, после осмотра.</p></div>'
         .format(loc_cap=d['ru_loc'][0].upper() + d['ru_loc'][1:],
                 wall=d['ru_wall'])),
    ]


# ═══════════════════════════════════════════════════════════════════
# Городские страницы услуг: разводим с белградскими двойниками.
# Здесь ключевые слова важнее всего, поэтому меняем окружающий текст,
# а не сами формулировки услуги.
# ═══════════════════════════════════════════════════════════════════
CITY_EDITS = {
    'vodoinstalater-novi-sad/index.html': [
        # FAQ про районы: на странице стояли БЕЛГРАДСКИЕ общины
        ('Vodoinstalateri rade u celom Novom Sadu: Vračar, Novi Novi Sad, '
         'Stari Grad, Savski Venac, Voždovac, Zemun, Zvezdara, Palilula, '
         'Čukarica, Rakovica i druge opštine.',
         'Vodoinstalateri rade u celom Novom Sadu i okolini: Stari Grad, '
         'Liman, Grbavica, Detelinara, Telep, Podbara, Novo Naselje, '
         'Petrovaradin, Sremska Kamenica i Futog.'),

        ('<div class="faq-answer"><p>Prvi odgovor — u proseku za '
         '<strong>15–60 minuta</strong>. U slučaju havarije (pukla cev, '
         'jako curenje) označite prijavu kao „hitno".</p></div>',
         '<div class="faq-answer"><p>Prvi odgovor — u proseku za '
         '<strong>15–60 minuta</strong>. Brza intervencija na Limanu i '
         'Detelinari ide najbrže — tamo dežura najviše majstora. '
         'U slučaju havarije (pukla cev, jako curenje) označite prijavu '
         'kao „hitno".</p></div>'),

        ('<li><strong>Postavljanje i zamena cevi</strong> — postavljanje '
         'vodovoda i kanalizacije. Zamena čeličnih cevi polipropilenom i '
         'metalo-plastikom. Uzidna i vidna montaža</li>',
         '<li><strong>Postavljanje i zamena cevi</strong> — vodovod i '
         'kanalizacija u Novom Sadu i okolini. Zamena dotrajalih čeličnih '
         'cevi polipropilenom — najčešći posao na Detelinari i Novom '
         'Naselju, gde su instalacije iz 1970-ih. U starom fondu '
         'Petrovaradina radimo sa specifičnim vertikalama i debelim '
         'zidovima</li>'),

        ('<li><strong>Otklanjanje curenja i havarija</strong> — hitna '
         'popravka cevi, radijatora i vertikala u Novom Sadu. Poziv '
         'vodoinstalatera za 60 minuta, otklanjanje curenja bilo koje '
         'složenosti</li>',
         '<li><strong>Otklanjanje curenja i havarija</strong> — hitna '
         'popravka cevi, radijatora i vertikala. Brza intervencija na '
         'Limanu i Detelinari, izlazak u Petrovaradin i Sremsku Kamenicu. '
         'Poziv vodoinstalatera za 60 minuta, curenje bilo koje '
         'složenosti</li>'),
    ],

    'elektricar-novi-sad/index.html': [
        # Замена проводки: привязка к фонду районов вместо общей формулировки
        ('<li><strong>Zamena instalacije</strong> — potpuna i delimična '
         'zamena elektro provodnika. Zamena aluminijuma bakrom, proračun '
         'opterećenja za savremene uređaje</li>',
         '<li><strong>Zamena instalacije</strong> — potpuna i delimična '
         'zamena provodnika. Zamena aluminijuma bakrom je najčešći posao na '
         'Detelinari i Novom Naselju: instalacija iz 1970-ih ne nosi '
         'savremene uređaje. U starom fondu Petrovaradina i Starog Grada '
         'radimo bez oštećenja zaštićenih obloga</li>'),

        # Заземление: вместо «u Novom Sadu» — конкретные районы частной застройки
        ('<li><strong>Uzemljenje i gromobranska zaštita</strong> — montaža '
         'uzemljenja i sistema zaštite od udara struje. Za privatne kuće i '
         'komercijalne objekte u Novom Sadu</li>',
         '<li><strong>Uzemljenje i gromobranska zaštita</strong> — montaža '
         'uzemljenja i zaštite od udara struje. Za privatne kuće na Telepu, '
         'u Petrovaradinu i Sremskoj Kamenici, kao i za poslovne prostore '
         'u Novom Sadu i okolini</li>'),

        # Диагностика: добавляем местный контекст вызова
        ('<li><strong>Dijagnostika kvarova</strong> — traženje uzroka '
         'prekida, kratkih spojeva i iskakanja osigurača. Izlazak sa '
         'profesionalnim multimetrom</li>',
         '<li><strong>Dijagnostika kvarova</strong> — traženje uzroka '
         'prekida, kratkih spojeva i iskakanja osigurača. Brza intervencija '
         'na Limanu i Detelinari, izlazak sa profesionalnim multimetrom</li>'),
    ],
}


def apply_edits(rel_path, edits):
    """
    Применяет список замен к файлу. Возвращает (сделано, пропущено).
    Пропуск = исходной строки нет: либо правка уже применена, либо
    вёрстка изменилась. В обоих случаях лучше сообщить, чем угадывать.
    """
    path = os.path.join(ROOT, rel_path)
    if not os.path.isfile(path):
        print('  ОТСУТСТВУЕТ: {}'.format(rel_path))
        return 0, 0

    with open(path, encoding='utf-8') as fh:
        html = fh.read()

    original = html
    done = skipped = 0

    for old, new in edits:
        if old in html:
            html = html.replace(old, new, 1)
            done += 1
        else:
            skipped += 1

    if html != original and not DRY_RUN:
        with open(path, 'w', encoding='utf-8', newline='') as fh:
            fh.write(html)

    status = 'OK' if skipped == 0 else 'частично'
    print('  {:<46} заменено {}, пропущено {}  [{}]'
          .format(rel_path, done, skipped, status))
    return done, skipped


def main():
    print('═' * 66)
    print('Рерайт страниц Нови-Сада' + ('  [DRY-RUN, файлы не пишутся]'
                                        if DRY_RUN else ''))
    print('═' * 66)

    total_done = total_skipped = 0

    print('\nСербские районные страницы:')
    for slug, d in DISTRICTS.items():
        rel = 'majstor-za-sve-{}-novi-sad/index.html'.format(slug)
        a, b = apply_edits(rel, sr_district_edits(d))
        total_done += a
        total_skipped += b

    print('\nРусские районные страницы:')
    for slug, d in DISTRICTS.items():
        rel = 'ru/master-na-chas-{}-novi-sad/index.html'.format(slug)
        a, b = apply_edits(rel, ru_district_edits(d))
        total_done += a
        total_skipped += b

    print('\nГородские страницы услуг:')
    for rel, edits in CITY_EDITS.items():
        a, b = apply_edits(rel, edits)
        total_done += a
        total_skipped += b

    print('\n' + '─' * 66)
    print('Итого: заменено {}, пропущено {}'.format(total_done, total_skipped))
    if total_skipped:
        print('Пропуски — это норма при повторном запуске (текст уже заменён).')
    print('─' * 66)


if __name__ == '__main__':
    main()
