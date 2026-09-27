# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════
add-novi-sad-local-intro.py — локальный блок на городских страницах НС

ЗАЧЕМ
    Правка хвоста lead и подписи шага (rewrite-novi-sad-city.py) сняла
    дублирование с 92% до 83%, но 18 страниц остались на 89%. Причина
    арифметическая: тело страницы — это 18 блоков прозы (8 пунктов
    услуги + 5 ответов FAQ + шаги), и две правки их не перевешивают.

    Переписывать сами пункты услуги смысла нет: «меняем петли и
    направляющие», «сколько длится генеральная уборка» — это описание
    услуги, которая в Белграде и Нови-Саде действительно одинаковая.
    Перефразировать их ради уникальности значило бы ухудшить текст и
    получить тот же смысл другими словами — Google такое не считает
    уникальностью.

    Поэтому добавляем то, чего на городских страницах нет вовсе:
    локальный абзац про Нови-Сад. На районных страницах такой блок
    («Lokalni intro») уже есть и работает — здесь повторяем его
    структуру с городским содержанием.

ЧТО ДЕЛАЕТ
    Вставляет перед <div class="price-table"> блок из двух абзацев:
    чем застройка Нови-Сада отличается от белградской применительно
    к этой профессии, и какие районы обслуживаются быстрее.
    Разметка копирует районный вариант: section-card + section-icon
    + h2.section-title + два <p> с теми же inline-стилями, поэтому
    новый CSS не нужен.

ЧЕГО НЕ ТРОГАЕТ
    H1, title, description, canonical, hreflang, og/twitter, JSON-LD,
    формы, цены, существующие пункты и FAQ. Блок только добавляется.

ИДЕМПОТЕНТНОСТЬ
    Перед вставкой проверяется маркер NS-LOCAL-INTRO. Если он есть —
    страница пропускается, повторный прогон ничего не дублирует.

ЗАПУСК из корня проекта:
    python scripts/add-novi-sad-local-intro.py --dry-run
    python scripts/add-novi-sad-local-intro.py
═══════════════════════════════════════════════════════════════════
"""

import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DRY_RUN = '--dry-run' in sys.argv

ANCHOR = '    <div class="price-table">'
MARKER = 'NS-LOCAL-INTRO'

# Иконка «место на карте» — та же, что в районном локальном блоке
ICON = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">\n'
        '              <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>\n'
        '              <circle cx="12" cy="10" r="3"/>\n'
        '            </svg>')


def block(title, p1, p2):
    """Собирает разметку локального блока (структура как на районных страницах)."""
    return (
        '    <!-- ' + MARKER + ': локальный абзац про Нови-Сад. Отличает\n'
        '         страницу от белградского двойника не перефразировкой услуги,\n'
        '         а фактами о городе — застройка, районы, типовые задачи. -->\n'
        '    <div class="sections-container">\n'
        '      <div class="split-sections" style="grid-template-columns: 1fr; '
        'max-width: 700px; margin: 3rem auto 0;">\n'
        '        <div class="section-card">\n'
        '          <div class="section-icon icon-masters">\n'
        '            ' + ICON + '\n'
        '          </div>\n'
        '          <h2 class="section-title" style="text-align:center;">'
        + title + '</h2>\n'
        '          <p style="color:#cfcfcf; line-height:1.7;">\n'
        '            ' + p1 + '\n'
        '          </p>\n'
        '          <p style="color:#cfcfcf; line-height:1.7; margin-top:1rem;">\n'
        '            ' + p2 + '\n'
        '          </p>\n'
        '        </div>\n'
        '      </div>\n'
        '    </div>\n'
        '\n'
    )


# ═══════════════════════════════════════════════════════════════════
# Содержание блоков. Нови-Сад ~380 тыс. жителей против ~1,7 млн в
# Белграде: компактнее, меньше пробок, другой жилой фонд — и это
# действительно влияет на работу мастера, а не просто «другой город».
# ═══════════════════════════════════════════════════════════════════
PAGES = {
    # ────────────────────────── SR ──────────────────────────
    'vodoinstalater-novi-sad/index.html': dict(
        title='Vodoinstalater u Novom Sadu — kakav je grad',
        p1=('Novi Sad je kompaktniji od Beograda i majstor po pravilu stiže '
            'brže: sa Limana do Detelinare vozi se desetak minuta. Najviše '
            'poziva dolazi iz blokova sa Detelinare i Novog Naselja, gde su '
            'vodovodne vertikale iz 1970-ih i čelične cevi na kraju veka. '
            'U starom fondu Petrovaradina i Starog Grada zidovi su debeli, a '
            'instalacija često vođena netipično — tamo se prvo radi pregled.'),
        p2=('Na Limanu i Grbavici najčešći su stanovi za izdavanje: curenje '
            'treba otkloniti isti dan, dok stanar ne ostane bez vode. '
            'Vodoinstalateri koji već rade u vašem kraju javljaju se prvi — '
            'ne čekate izlazak sa druge strane grada.'),
    ),
    'elektricar-novi-sad/index.html': dict(
        title='Električar u Novom Sadu — kakav je grad',
        p1=('Jedna trećina stanova u Novom Sadu je iz blokovske gradnje '
            '1960–1980: aluminijumska instalacija, table bez FID sklopke i '
            'dve linije na celu kuhinju. Na Detelinari i Novom Naselju to je '
            'najčešći posao — zamena aluminijuma bakrom i proračun '
            'opterećenja za savremene uređaje.'),
        p2=('U Petrovaradinu i na Telepu preteže privatna gradnja: '
            'uzemljenje, gromobran, struja u dvorištu i pomoćnim '
            'prostorijama. Novogradnja na Grbavici traži drugo — montažu bez '
            'oštećenja sveže obrađenih zidova. Električar iz vašeg kraja '
            'javlja se za 60 minuta.'),
    ),
    'kucni-popravci-novi-sad/index.html': dict(
        title='Kućne popravke u Novom Sadu — kakav je grad',
        p1=('Novi Sad je grad malih rastojanja: majstor za sitne popravke '
            'obično stigne isti dan, a ne „negde ove nedelje". Na Limanu i '
            'Grbavici najviše traže podešavanje vrata i prozora u '
            'iznajmljenim stanovima, na Detelinari — popravku starog '
            'nameštaja i zamenu dotrajalog okova.'),
        p2=('U Petrovaradinu i na Telepu posao je drugačiji: stara stolarija, '
            'drvene konstrukcije u dvorištu, brave na kapijama. Opišite '
            'zadatak i najbliži slobodan majstor kontaktiraće vas za '
            '60 minuta.'),
    ),
    'montaza-namestaja-novi-sad/index.html': dict(
        title='Montaža nameštaja u Novom Sadu — kakav je grad',
        p1=('Novi Sad je univerzitetski grad: svakog septembra Liman i '
            'Grbavica menjaju stanare, pa montaža i demontaža nameštaja ide '
            'u sezoni. Stanovi su uglavnom manje kvadrature — ormar se '
            'sklapa u sobi, bez prostora za razmeštanje delova, i to traži '
            'pažljiviji rad.'),
        p2=('Na Novom Naselju i Detelinari preteže tipsko stanovanje: monteri '
            'znaju rasporede unapred i tačnije procenjuju vreme. '
            'Montiramo nameštaj iz svih prodavnica — po uputstvu i '
            'artiklima, sa donošenjem okova koji nedostaje.'),
    ),
    'montaza-na-zid-novi-sad/index.html': dict(
        title='Kačenje i montaža u Novom Sadu — kakav je grad',
        p1=('Ono što drži na jednom zidu, na drugom se izvlači. U Novom Sadu '
            'razlika je velika: montažni betonski paneli na Novom Naselju, '
            'nosivi beton starih blokova na Detelinari, gips-karton u '
            'renoviranim stanovima na Grbavici i puni stari zid u '
            'Petrovaradinu.'),
        p2=('Zato majstor pričvršćivač bira na licu mesta, posle pregleda '
            'zida — televizor od 40 kilograma i polica za knjige ne traže '
            'isto rešenje. Kažite šta kačite i na kakav zid, i dobićete '
            'procenu za 60 minuta.'),
    ),
    'ciscenje-i-odrzavanje-novi-sad/index.html': dict(
        title='Čišćenje i održavanje u Novom Sadu — kakav je grad',
        p1=('U Novom Sadu veliki deo poslova vezan je za izdavanje stanova: '
            'Liman i Grbavica su blizu kampusa, stanari se menjaju svake '
            'godine, a između useljenja treba temeljno čišćenje — da se '
            'depozit vrati bez spora.'),
        p2=('Na Telepu i u Petrovaradinu preteže privatna gradnja: kuće sa '
            'dvorištem, više prozora, terase i pomoćne prostorije. '
            'Čistači iz vašeg kraja javljaju se u roku od 60 minuta, sa '
            'svojim sredstvima i opremom.'),
    ),
    'majstor-za-racunare-novi-sad/index.html': dict(
        title='Majstor za računare u Novom Sadu — kakav je grad',
        p1=('Novi Sad je univerzitetski i IT grad: veliki deo poziva su '
            'studentski laptopovi pred rokovima i računari za rad od kuće, '
            'gde popravka ne može da čeka nedelju dana. Najviše izlazaka '
            'ide na Liman i Grbavicu, blizu kampusa.'),
        p2=('Za firme i poslovne prostore u Starom Gradu i na Novom Naselju '
            'radimo i mrežu — ruter, Wi-Fi pokrivanje, štampač na više '
            'radnih mesta. Dolazak na kućnu i poslovnu adresu, javljanje '
            'za 60 minuta.'),
    ),
    'selidbe-i-nosaci-novi-sad/index.html': dict(
        title='Selidbe i nosači u Novom Sadu — kakav je grad',
        p1=('Cenu selidbe u Novom Sadu određuje sprat, a ne kilometraža — '
            'grad je kompaktan, ali zgrade na Detelinari i Podbari često su '
            'bez lifta, a u Petrovaradinu se prilazi uzbrdo i ulicama u '
            'kojima kombi ne može do ulaza.'),
        p2=('Zato pitamo sprat, lift i prilaz pre izlaska — da cena ne '
            'poraste na licu mesta. Septembar i oktobar su sezona studentskih '
            'selidbi na Limanu: termin je bolje dogovoriti dan ranije. '
            'Ekipa se javlja u roku od 60 minuta.'),
    ),

    # ────────────────────────── RU ──────────────────────────
    'ru/santehnik-novi-sad/index.html': dict(
        title='Сантехник в Нови-Саде — какой это город',
        p1=('Нови-Сад компактнее Белграда, и мастер обычно доезжает быстрее: '
            'с Лимана до Детелинары — минут десять. Больше всего вызовов '
            'приходит из домов Детелинары и Ново Населья, где стояки 1970-х '
            'и стальные трубы на исходе срока. В старом фонде Петроварадина '
            'и Стари Града стены толстые, а разводка нередко нетиповая — '
            'там сначала осмотр.'),
        p2=('На Лимане и Грбавице много съёмного жилья: течь нужно устранить '
            'в тот же день, пока арендатор не остался без воды. Сантехники, '
            'которые уже работают в вашем районе, откликаются первыми — '
            'не нужно ждать выезд с другого конца города.'),
    ),
    'ru/elektrik-novi-sad/index.html': dict(
        title='Электрик в Нови-Саде — какой это город',
        p1=('Примерно треть квартир Нови-Сада — блочная застройка 1960–1980-х: '
            'алюминиевая проводка, щитки без УЗО и две линии на всю кухню. '
            'На Детелинаре и в Ново Населье это самая частая работа — замена '
            'алюминия медью и расчёт нагрузки под современную технику.'),
        p2=('В Петроварадине и на Телепе преобладает частный сектор: '
            'заземление, громоотвод, электрика во дворе и подсобных '
            'помещениях. Новостройки Грбавицы требуют другого — монтажа без '
            'повреждения свежей отделки. Электрик из вашего района '
            'откликнется за 60 минут.'),
    ),
    'ru/bytovoy-remont-novi-sad/index.html': dict(
        title='Бытовой ремонт в Нови-Саде — какой это город',
        p1=('Нови-Сад — город небольших расстояний: мастер по мелкому ремонту '
            'обычно приезжает в тот же день, а не «когда-нибудь на этой '
            'неделе». На Лимане и Грбавице чаще всего просят отрегулировать '
            'двери и окна в съёмных квартирах, на Детелинаре — починить '
            'старую мебель и заменить изношенную фурнитуру.'),
        p2=('В Петроварадине и на Телепе работа другая: старая столярка, '
            'деревянные конструкции во дворе, замки на калитках. Опишите '
            'задачу — ближайший свободный мастер свяжется с вами '
            'за 60 минут.'),
    ),
    'ru/sborka-mebeli-novi-sad/index.html': dict(
        title='Сборка мебели в Нови-Саде — какой это город',
        p1=('Нови-Сад — университетский город: каждый сентябрь Лиман и '
            'Грбавица меняют жильцов, поэтому сборка и разборка мебели идёт '
            'сезонами. Квартиры в основном небольшие — шкаф собирают прямо '
            'в комнате, без места разложить детали, и это требует '
            'аккуратности.'),
        p2=('В Ново Населье и на Детелинаре преобладает типовое жильё: '
            'сборщики знают планировки заранее и точнее оценивают время. '
            'Собираем мебель из любых магазинов — по инструкции и артикулам, '
            'с доставкой недостающей фурнитуры.'),
    ),
    'ru/naveska-montazh-novi-sad/index.html': dict(
        title='Навеска и монтаж в Нови-Саде — какой это город',
        p1=('То, что держится в одной стене, из другой вырывает. В Нови-Саде '
            'разброс большой: сборные бетонные панели в Ново Населье, '
            'несущий бетон старых блоков на Детелинаре, гипсокартон в '
            'отремонтированных квартирах Грбавицы и полнотелая старая кладка '
            'в Петроварадине.'),
        p2=('Поэтому крепёж мастер подбирает на месте, после осмотра стены: '
            'телевизор на 40 килограммов и книжная полка требуют разных '
            'решений. Скажите, что вешаете и на какую стену, — оценку '
            'получите за 60 минут.'),
    ),
    'ru/klining-novi-sad/index.html': dict(
        title='Уборка квартир в Нови-Саде — какой это город',
        p1=('В Нови-Саде значительная часть заказов связана со сдачей жилья: '
            'Лиман и Грбавица рядом с кампусом, жильцы меняются каждый год, '
            'и между заселениями нужна генеральная уборка — чтобы депозит '
            'вернули без спора.'),
        p2=('На Телепе и в Петроварадине преобладает частная застройка: дома '
            'с двором, больше окон, террасы и подсобные помещения. Клинеры '
            'из вашего района откликнутся в течение 60 минут, со своими '
            'средствами и инвентарём.'),
    ),
    'ru/remont-kompyuterov-novi-sad/index.html': dict(
        title='Ремонт компьютеров в Нови-Саде — какой это город',
        p1=('Нови-Сад — университетский и IT-город: большая часть вызовов — '
            'студенческие ноутбуки перед сессией и рабочие компьютеры на '
            'удалёнке, где ремонт не может ждать неделю. Больше всего '
            'выездов на Лиман и Грбавицу, рядом с кампусом.'),
        p2=('Для фирм и офисов в Стари Граде и Ново Населье делаем и сеть — '
            'роутер, покрытие Wi-Fi, принтер на несколько рабочих мест. '
            'Выезд на дом и в офис, отклик за 60 минут.'),
    ),
    'ru/gruzchiki-novi-sad/index.html': dict(
        title='Грузчики в Нови-Саде — какой это город',
        p1=('Стоимость переезда в Нови-Саде определяет этаж, а не километраж: '
            'город компактный, но дома на Детелинаре и Подбаре часто без '
            'лифта, а в Петроварадине подъезд идёт в гору и по улицам, где '
            'фургон не встанет у входа.'),
        p2=('Поэтому мы спрашиваем этаж, лифт и подъезд заранее — чтобы цена '
            'не выросла на месте. Сентябрь и октябрь — сезон студенческих '
            'переездов на Лимане: бригаду лучше согласовать за день. '
            'Отклик за 60 минут.'),
    ),

    # ────────────────────────── EN ──────────────────────────
    'santehnik-novi-sad-en/index.html': dict(
        title='Plumbing in Novi Sad — what the city is like',
        p1=('Novi Sad is more compact than Belgrade, so a plumber usually '
            'arrives sooner: Liman to Detelinara is about ten minutes. Most '
            'call-outs come from the blocks on Detelinara and Novo Naselje, '
            'where the risers date from the 1970s and the steel pipe is at '
            'the end of its life. In the older stock of Petrovaradin and '
            'Stari Grad the walls are thick and the runs often unusual, so '
            'the job starts with an inspection.'),
        p2=('Liman and Grbavica are mostly rentals: a leak has to be fixed '
            'the same day, before the tenant is left without water. Plumbers '
            'already working in your district respond first — no waiting for '
            'someone to cross the city.'),
    ),
    'elektrik-novi-sad-en/index.html': dict(
        title='Electrical work in Novi Sad — what the city is like',
        p1=('Roughly a third of flats in Novi Sad come from the 1960s–80s '
            'blocks: aluminium wiring, panels with no RCD, and two circuits '
            'for an entire kitchen. On Detelinara and in Novo Naselje that is '
            'the most common job — swapping aluminium for copper and sizing '
            'the load for modern appliances.'),
        p2=('Petrovaradin and Telep are mainly private houses: earthing, '
            'lightning protection, power in the yard and outbuildings. New '
            'builds on Grbavica need the opposite — installation without '
            'marking freshly finished walls. An electrician from your '
            'district responds within 60 minutes.'),
    ),
    'bytovoy-remont-novi-sad-en/index.html': dict(
        title='Home repairs in Novi Sad — what the city is like',
        p1=('Novi Sad is a city of short distances: a handyman for small jobs '
            'usually comes the same day rather than "sometime this week". On '
            'Liman and Grbavica the common request is adjusting doors and '
            'windows in rented flats; on Detelinara it is repairing older '
            'furniture and replacing worn fittings.'),
        p2=('Petrovaradin and Telep are different work again: old joinery, '
            'timber structures in the yard, locks on gates. Describe the job '
            'and the nearest available handyman will contact you within '
            '60 minutes.'),
    ),
    'sborka-mebeli-novi-sad-en/index.html': dict(
        title='Furniture assembly in Novi Sad — what the city is like',
        p1=('Novi Sad is a university city: every September Liman and '
            'Grbavica change tenants, so assembly and disassembly run in '
            'seasons. Flats are mostly small — a wardrobe gets built inside '
            'the room with no space to lay the parts out, which calls for '
            'more careful work.'),
        p2=('Novo Naselje and Detelinara are mainly standard layouts, so '
            'assemblers know the floor plans in advance and estimate the time '
            'more accurately. We assemble furniture from any store — by the '
            'instructions and part numbers, bringing any missing fittings.'),
    ),
    'naveska-montazh-novi-sad-en/index.html': dict(
        title='Mounting and installation in Novi Sad — what the city is like',
        p1=('What holds in one wall pulls straight out of another. In Novi Sad '
            'the range is wide: precast concrete panels in Novo Naselje, '
            'load-bearing concrete in the older Detelinara blocks, '
            'plasterboard in renovated flats on Grbavica, and solid old brick '
            'in Petrovaradin.'),
        p2=('That is why the anchor is chosen on site, after looking at the '
            'wall — a 40-kilogram television and a bookshelf do not call for '
            'the same fixing. Tell us what you are mounting and on what wall, '
            'and you will have an estimate within 60 minutes.'),
    ),
    'klining-novi-sad-en/index.html': dict(
        title='Apartment cleaning in Novi Sad — what the city is like',
        p1=('In Novi Sad a large share of the work comes from rentals: Liman '
            'and Grbavica sit next to the campus, tenants change every year, '
            'and a deep clean between move-outs is what gets the deposit '
            'returned without argument.'),
        p2=('Telep and Petrovaradin are mostly private houses: yards, more '
            'windows, terraces and outbuildings. Cleaners from your district '
            'respond within 60 minutes, with their own products and '
            'equipment.'),
    ),
    'remont-kompyuterov-novi-sad-en/index.html': dict(
        title='Computer repair in Novi Sad — what the city is like',
        p1=('Novi Sad is a university and IT city: much of the work is student '
            'laptops before deadlines and home-office machines where a repair '
            'cannot wait a week. Most visits go to Liman and Grbavica, close '
            'to the campus.'),
        p2=('For companies and offices in Stari Grad and Novo Naselje we also '
            'handle the network — router, Wi-Fi coverage, a printer shared '
            'across several desks. Home and office visits, a response within '
            '60 minutes.'),
    ),
    'gruzchiki-novi-sad-en/index.html': dict(
        title='Movers in Novi Sad — what the city is like',
        p1=('In Novi Sad the price of a move is set by the floor, not the '
            'distance — the city is compact, but buildings on Detelinara and '
            'Podbara are often walk-ups, and in Petrovaradin the approach '
            'climbs through streets where a van cannot reach the entrance.'),
        p2=('So we ask about the floor, the lift and the access before coming '
            'out, so the price does not rise on the spot. September and '
            'October are the student moving season on Liman: it is better to '
            'book a day ahead. A crew responds within 60 minutes.'),
    ),
}


def apply_page(rel, spec):
    path = os.path.join(ROOT, rel)
    if not os.path.isfile(path):
        print('  ОТСУТСТВУЕТ: {}'.format(rel))
        return 0, 0

    with open(path, encoding='utf-8') as fh:
        html = fh.read()

    if MARKER in html:
        print('  {:<46} уже есть  [пропуск]'.format(rel))
        return 0, 1

    if ANCHOR not in html:
        print('  {:<46} НЕТ ЯКОРЯ price-table  [пропуск]'.format(rel))
        return 0, 1

    new = html.replace(
        ANCHOR,
        block(spec['title'], spec['p1'], spec['p2']) + ANCHOR,
        1
    )

    if not DRY_RUN:
        with open(path, 'w', encoding='utf-8', newline='') as fh:
            fh.write(new)

    words = len((spec['p1'] + ' ' + spec['p2']).split())
    print('  {:<46} вставлено (+{} слов)  [OK]'.format(rel, words))
    return 1, 0


def main():
    print('═' * 70)
    print('Локальный блок на городских страницах Нови-Сада'
          + ('  [DRY-RUN]' if DRY_RUN else ''))
    print('═' * 70)

    td = ts = 0
    for rel, spec in PAGES.items():
        a, b = apply_page(rel, spec)
        td += a
        ts += b

    print('\n' + '─' * 70)
    print('Итого: страниц {}, вставлено {}, пропущено {}'
          .format(len(PAGES), td, ts))
    print('─' * 70)


if __name__ == '__main__':
    main()
