#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make-legal-pages.py — генератор юридических страниц (9 файлов, 3 × 3 языка).

Создаёт скелеты страниц «О нас», «Политика конфиденциальности» и «Условия
использования» на трёх языках. Тексты — рабочие заготовки под сербское
право: закон о защите персональных данных (Zakon o zaštiti podataka o
ličnosti, «Sl. glasnik RS» br. 87/2018) и закон о защите потребителей.

Реквизиты компании оставлены плейсхолдерами в квадратных скобках —
их подставят, когда будут готовы документы и сербский номер:

    [NAZIV_KOMPANIJE]  [PIB_BROJ]  [ADRESA_BEOGRAD]
    [TELEFON_381]      [EMAIL_PODRSKA]

ВАЖНО: до заполнения плейсхолдеров страницы стоят под noindex
(блок PRELAUNCH, как на остальном сайте) — незаполненная юридическая
страница в индексе хуже, чем её отсутствие.

URL-структура повторяет принятую на сайте: сербский — в корне,
остальные языки — в своих папках.

    /o-nama/                  /ru/o-nas/            /en/about/
    /politika-privatnosti/    /ru/politika-konfidencialnosti/  /en/privacy-policy/
    /uslovi-koriscenja/       /ru/usloviya-ispolzovaniya/      /en/terms-of-service/

Запуск из корня проекта:
    python scripts/make-legal-pages.py
    python scripts/make-legal-pages.py --dry-run

Существующие файлы не перезаписываются.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DRY = "--dry-run" in sys.argv

SITE = "https://pravimajstor.rs"

# ── Плейсхолдеры реквизитов ────────────────────────────────────────
PH = {
    "sr": {
        "company": "[NAZIV_KOMPANIJE]",
        "pib": "[PIB_BROJ]",
        "address": "[ADRESA_BEOGRAD]",
        "phone": "[TELEFON_381]",
        "email": "[EMAIL_PODRSKA]",
    },
    "ru": {
        "company": "[НАЗВАНИЕ КОМПАНИИ]",
        "pib": "[ПИБ]",
        "address": "[АДРЕС В БЕЛГРАДЕ]",
        "phone": "[ТЕЛЕФОН +381...]",
        "email": "[EMAIL ПОДДЕРЖКИ]",
    },
    "en": {
        "company": "[NAZIV_KOMPANIJE]",
        "pib": "[PIB_BROJ]",
        "address": "[ADRESA_BEOGRAD]",
        "phone": "[TELEFON_381]",
        "email": "[EMAIL_PODRSKA]",
    },
}

# ── Общие строки интерфейса по языкам ──────────────────────────────
UI = {
    "sr": {
        "home": "/sr/",
        "crumb_home": "Početna",
        "aria": "Putanja",
        "subtitle": "// Majstori za bilo koji zadatak",
        "logo_aria": "Na početnu",
        "masters": "/sr/masters/",
        "masters_text": "Za majstore",
        "online": "Sada na mreži: ",
        "online_tail": " majstora",
        # Ширина плашки языков = ширине счётчика мастеров:
        # перевод разной длины, поэтому значение своё для каждого языка.
        "lang_width": "286",
        "footer_owner": "© 2026 Usluge majstora",
        "price_url": "/cenovnik/",
        "price_text": "Cenovnik",
        "hours": "Radno vreme: 08:00–23:00, svakog dana",
        "privacy_note": "Slanjem bilo koje forme saglasni ste sa obradom ličnih podataka u skladu sa zakonodavstvom Republike Srbije.",
        "updated": "Poslednja izmena",
        "locale": "sr_RS",
    },
    "ru": {
        "home": "/ru/",
        "crumb_home": "Главная",
        "aria": "Хлебные крошки",
        "subtitle": "// Мастера для любых задач",
        "logo_aria": "На главную",
        "masters": "/ru/masters/",
        "masters_text": "Для мастеров",
        "online": "Сейчас онлайн: ",
        "online_tail": " мастеров",
        # Ширина плашки языков = ширине счётчика мастеров:
        # перевод разной длины, поэтому значение своё для каждого языка.
        "lang_width": "306",
        "footer_owner": "© 2026 Handyman Service",
        "price_url": "/ru/cenovnik/",
        "price_text": "Цены на услуги",
        "hours": "Режим работы: 08:00–23:00, ежедневно",
        "privacy_note": "Отправляя форму, вы соглашаетесь на обработку персональных данных в соответствии с законодательством Республики Сербия.",
        "updated": "Последнее изменение",
        "locale": "ru_RS",
    },
    "en": {
        "home": "/en/",
        "crumb_home": "Home",
        "aria": "Breadcrumb",
        "subtitle": "// Masters for any task",
        "logo_aria": "To homepage",
        "masters": "/en/masters/",
        "masters_text": "For masters",
        "online": "Online now: ",
        "online_tail": " masters",
        # Ширина плашки языков = ширине счётчика мастеров:
        # перевод разной длины, поэтому значение своё для каждого языка.
        "lang_width": "258",
        "footer_owner": "© 2026 Handyman Service",
        "price_url": "/en/pricelist/",
        "price_text": "Price list",
        "hours": "Working hours: 08:00–23:00, daily",
        "privacy_note": "By submitting any form you consent to the processing of personal data in accordance with the legislation of the Republic of Serbia.",
        "updated": "Last updated",
        "locale": "en_RS",
    },
}

UPDATED = "2026-09-24"


def P(text):
    return "      <p>" + text + "</p>"


def H(text):
    return "      <h2>" + text + "</h2>"


# ══════════════════════════════════════════════════════════════════
# Содержимое страниц
# Для каждой страницы: slug по языкам, title, description, H1 и тело.
# ══════════════════════════════════════════════════════════════════

def body_about(lang):
    p = PH[lang]
    if lang == "sr":
        return "\n".join([
            P(f"<strong>Pravi Majstor</strong> je servis koji povezuje naručioce sa proverenim majstorima u Beogradu i Novom Sadu. Ne izvodimo radove sami — naš posao je da za vaš zadatak brzo pronađemo majstora koji mu odgovara."),
            H("Kako radimo"),
            P("Ostavljate prijavu sa opisom zadatka. Prijava odlazi majstorima koji rade u vašem gradu i u vašoj oblasti. Prvi slobodan majstor javlja se u proseku za 15–60 minuta, dogovarate cenu i vreme dolaska direktno sa njim."),
            P("Za naručioce je pretraga majstora <strong>besplatna</strong>. Plaćate samo rad majstora i to direktno njemu — servis ne uzima proviziju od naručioca."),
            H("Provera majstora"),
            P("Svaki majstor pre prvog posla prolazi proveru: lična identifikacija, selfi-potvrda i podaci o iskustvu. Majstori sa niskom ocenom prestaju da dobijaju prijave — ocenu daju sami naručioci posle završenog posla."),
            H("Podaci o firmi"),
            P(f"Naziv: {p['company']}<br>PIB: {p['pib']}<br>Adresa: {p['address']}<br>Telefon: {p['phone']}<br>E-pošta: {p['email']}"),
            H("Kontakt"),
            P(f"Za pitanja o radu servisa pišite na {p['email']} ili na Telegram <a href=\"https://t.me/masterasupport\" class=\"inline-link\">@masterasupport</a>. Radno vreme podrške: 08:00–23:00, svakog dana."),
        ])
    if lang == "ru":
        return "\n".join([
            P("<strong>Pravi Majstor</strong> — сервис, который сводит заказчиков с проверенными мастерами в Белграде и Нови-Саде. Мы не выполняем работы сами — наша задача быстро найти под вашу задачу подходящего мастера."),
            H("Как это работает"),
            P("Вы оставляете заявку с описанием задачи. Заявка уходит мастерам, которые работают в вашем городе и вашем районе. Первый свободный мастер откликается в среднем за 15–60 минут; цену и время визита вы обсуждаете напрямую с ним."),
            P("Для заказчиков поиск мастера <strong>бесплатен</strong>. Вы платите только за работу мастера и напрямую ему — сервис не берёт комиссию с заказчика."),
            H("Проверка мастеров"),
            P("Каждый мастер до первого заказа проходит проверку: идентификация личности, селфи-подтверждение и данные об опыте. Мастера с низким рейтингом перестают получать заявки — оценку ставят сами заказчики после выполненной работы."),
            H("Реквизиты"),
            P(f"Название: {p['company']}<br>ПИБ (налоговый номер): {p['pib']}<br>Адрес: {p['address']}<br>Телефон: {p['phone']}<br>E-mail: {p['email']}"),
            H("Контакты"),
            P(f"По вопросам работы сервиса пишите на {p['email']} или в Telegram <a href=\"https://t.me/masterasupport\" class=\"inline-link\">@masterasupport</a>. Режим работы поддержки: 08:00–23:00, ежедневно."),
        ])
    return "\n".join([
        P("<strong>Pravi Majstor</strong> is a service that connects customers with verified handymen in Belgrade and Novi Sad. We do not carry out the work ourselves — our job is to quickly find a master who fits your task."),
        H("How it works"),
        P("You submit a request describing the task. The request goes to masters working in your city and your district. The first available master replies within 15–60 minutes on average; you agree the price and the visit time directly with them."),
        P("For customers, finding a master is <strong>free</strong>. You pay only for the master's work and pay them directly — the service takes no commission from the customer."),
        H("Master verification"),
        P("Before the first job, every master passes a check: identity verification, a selfie confirmation and details of their experience. Masters with a low rating stop receiving requests — the rating is given by customers themselves after the job is done."),
        H("Company details"),
        P(f"Name: {p['company']}<br>PIB (tax number): {p['pib']}<br>Address: {p['address']}<br>Phone: {p['phone']}<br>E-mail: {p['email']}"),
        H("Contact"),
        P(f"For questions about the service, write to {p['email']} or via Telegram <a href=\"https://t.me/masterasupport\" class=\"inline-link\">@masterasupport</a>. Support hours: 08:00–23:00, daily."),
    ])


def body_privacy(lang):
    p = PH[lang]
    if lang == "sr":
        return "\n".join([
            P(f"Ova politika objašnjava koje podatke {p['company']} (u daljem tekstu — „servis“) prikuplja preko sajta pravimajstor.rs i šta sa njima radi. Obrada se vrši u skladu sa Zakonom o zaštiti podataka o ličnosti („Sl. glasnik RS“ br. 87/2018)."),
            H("1. Rukovalac podacima"),
            P(f"{p['company']}, PIB {p['pib']}, {p['address']}. Kontakt za pitanja o podacima: {p['email']}, telefon {p['phone']}."),
            H("2. Koje podatke prikupljamo"),
            P("<strong>Podaci iz prijave:</strong> ime, broj telefona ili Telegram, grad i opština, opis zadatka i, ako ih priložite, fotografije zadatka."),
            P("<strong>Tehnički podaci:</strong> IP adresa, tip uređaja i pretraživača, stranice koje ste posetili — preko Google Analytics."),
            P("Ne prikupljamo posebne kategorije podataka (zdravlje, veroispovest, politička uverenja) i ne tražimo ih u prijavi."),
            H("3. Zašto ih obrađujemo"),
            P("Podaci iz prijave služe isključivo da bismo vaš zadatak prosledili majstorima i da bi majstor mogao da vas kontaktira. Tehnički podaci služe za statistiku poseta i poboljšanje sajta."),
            H("4. Kome se podaci prosleđuju"),
            P("Opis zadatka, grad i opština vide se majstorima koji rade u toj oblasti. <strong>Vaš kontakt (telefon ili Telegram) vidi samo onaj majstor koji je preuzeo prijavu</strong> — do tog trenutka kontakt je sakriven."),
            P("Podatke ne prodajemo i ne ustupamo trećim licima u marketinške svrhe."),
            H("5. Čuvanje i bezbednost"),
            P("Kontakt podaci se čuvaju u šifrovanom obliku. Pristup imaju samo administrator servisa i majstor koji je preuzeo prijavu. Podaci se čuvaju dok je to potrebno za izvršenje posla i rešavanje eventualnih reklamacija."),
            H("6. Vaša prava"),
            P("Imate pravo da zatražite uvid u svoje podatke, njihovu ispravku ili brisanje, kao i da povučete saglasnost za obradu. Zahtev pošaljite na {email}.".replace("{email}", p["email"])),
            P("Ako smatrate da su vaša prava povređena, možete se obratiti Povereniku za informacije od javnog značaja i zaštitu podataka o ličnosti."),
            H("7. Kolačići (cookies)"),
            P("Sajt koristi kolačiće za rad Google Analytics i za pamćenje izabranog jezika i grada. Kolačiće možete obrisati ili blokirati u podešavanjima pretraživača — sajt će i dalje raditi."),
            H("8. Izmene politike"),
            P("Politiku možemo menjati. Datum poslednje izmene naveden je na dnu ove stranice."),
        ])
    if lang == "ru":
        return "\n".join([
            P(f"Эта политика объясняет, какие данные {p['company']} (далее — «сервис») собирает через сайт pravimajstor.rs и что с ними делает. Обработка ведётся по Закону о защите персональных данных Республики Сербия („Sl. glasnik RS“ № 87/2018)."),
            H("1. Кто обрабатывает данные"),
            P(f"{p['company']}, ПИБ {p['pib']}, {p['address']}. Контакт по вопросам данных: {p['email']}, телефон {p['phone']}."),
            H("2. Какие данные мы собираем"),
            P("<strong>Данные из заявки:</strong> имя, телефон или Telegram, город и район, описание задачи и, если вы их приложили, фотографии."),
            P("<strong>Технические данные:</strong> IP-адрес, тип устройства и браузера, просмотренные страницы — через Google Analytics."),
            P("Мы не собираем особые категории данных (здоровье, вероисповедание, политические взгляды) и не запрашиваем их в форме."),
            H("3. Зачем мы их обрабатываем"),
            P("Данные из заявки нужны только для того, чтобы передать вашу задачу мастерам и чтобы мастер мог с вами связаться. Технические данные — для статистики посещений и улучшения сайта."),
            H("4. Кому передаются данные"),
            P("Описание задачи, город и район видны мастерам, работающим в этой зоне. <strong>Ваш контакт (телефон или Telegram) видит только тот мастер, который взял заявку</strong> — до этого момента контакт скрыт."),
            P("Мы не продаём данные и не передаём их третьим лицам в маркетинговых целях."),
            H("5. Хранение и безопасность"),
            P("Контактные данные хранятся в зашифрованном виде. Доступ есть только у администратора сервиса и у мастера, взявшего заявку. Данные хранятся столько, сколько нужно для выполнения работы и разбора возможных претензий."),
            H("6. Ваши права"),
            P(f"Вы вправе запросить доступ к своим данным, их исправление или удаление, а также отозвать согласие на обработку. Запрос направляйте на {p['email']}."),
            P("Если вы считаете, что ваши права нарушены, вы можете обратиться к Уполномоченному по защите персональных данных Республики Сербия."),
            H("7. Файлы cookie"),
            P("Сайт использует cookie для работы Google Analytics и чтобы запомнить выбранный язык и город. Cookie можно удалить или заблокировать в настройках браузера — сайт продолжит работать."),
            H("8. Изменения политики"),
            P("Мы можем менять эту политику. Дата последнего изменения указана внизу страницы."),
        ])
    return "\n".join([
        P(f"This policy explains what data {p['company']} (the “service”) collects through pravimajstor.rs and what we do with it. Processing follows the Serbian Personal Data Protection Act (“Sl. glasnik RS” No. 87/2018)."),
        H("1. Data controller"),
        P(f"{p['company']}, PIB {p['pib']}, {p['address']}. Contact for data questions: {p['email']}, phone {p['phone']}."),
        H("2. What we collect"),
        P("<strong>Request data:</strong> name, phone number or Telegram, city and district, task description and, if you attach them, photos of the task."),
        P("<strong>Technical data:</strong> IP address, device and browser type, pages visited — via Google Analytics."),
        P("We do not collect special categories of data (health, religion, political views) and do not ask for them in the form."),
        H("3. Why we process it"),
        P("Request data is used solely to pass your task to masters and to let a master contact you. Technical data is used for visit statistics and improving the site."),
        H("4. Who receives the data"),
        P("The task description, city and district are visible to masters working in that area. <strong>Your contact details (phone or Telegram) are seen only by the master who accepts the request</strong> — until then the contact stays hidden."),
        P("We do not sell your data and do not pass it to third parties for marketing."),
        H("5. Storage and security"),
        P("Contact details are stored encrypted. Access is limited to the service administrator and the master who accepted the request. Data is kept only as long as needed to complete the job and handle any complaints."),
        H("6. Your rights"),
        P(f"You may request access to your data, its correction or deletion, and you may withdraw your consent to processing. Send requests to {p['email']}."),
        P("If you believe your rights have been violated, you may contact the Serbian Commissioner for Information of Public Importance and Personal Data Protection."),
        H("7. Cookies"),
        P("The site uses cookies for Google Analytics and to remember your chosen language and city. You can delete or block cookies in your browser settings — the site will keep working."),
        H("8. Changes to this policy"),
        P("We may update this policy. The date of the last change is shown at the bottom of this page."),
    ])


def body_terms(lang):
    p = PH[lang]
    if lang == "sr":
        return "\n".join([
            P(f"Korišćenjem sajta pravimajstor.rs prihvatate ove uslove. Servis vodi {p['company']}, PIB {p['pib']}, {p['address']}."),
            H("1. Šta servis radi"),
            P("Servis je <strong>posrednik</strong>: povezuje naručioce i majstore. Servis ne izvodi radove, ne zapošljava majstore i nije strana u dogovoru između vas i majstora."),
            H("2. Cena i plaćanje"),
            P("Za naručioce je korišćenje servisa besplatno. Cenu radova dogovarate direktno sa majstorom i njemu plaćate. Cene na stranici <a href=\"/cenovnik/\" class=\"inline-link\">Cenovnik</a> su <strong>okvirne</strong> — tačnu cenu majstor potvrđuje pre početka posla."),
            H("3. Odgovornost"),
            P("Za kvalitet radova, rokove i štetu nastalu tokom rada odgovara majstor koji je posao preuzeo. Servis proverava majstore pri registraciji, ali ne može da garantuje ishod svakog pojedinačnog posla."),
            P(f"Ako je došlo do problema, javite se na {p['email']} — razmatramo svaku pritužbu i možemo majstoru smanjiti ocenu ili mu ukinuti pristup prijavama."),
            H("4. Obaveze naručioca"),
            P("Prijava treba da sadrži tačan opis zadatka i ispravan kontakt. Zloupotreba servisa — lažne prijave, uvrede majstorima, pokušaj da se majstor izbegne posle preuzete prijave — povlači ograničenje pristupa."),
            H("5. Obaveze majstora"),
            P("Majstor se obavezuje da navede tačne podatke o sebi i svom iskustvu, da cenu kaže pre početka rada i da je ne menja usput bez dogovora sa naručiocem."),
            H("6. Reklamacije"),
            P(f"Reklamacije primamo na {p['email']} i telefonom {p['phone']}, radnim danima i vikendom od 08:00 do 23:00. Odgovaramo u roku od 8 dana, u skladu sa Zakonom o zaštiti potrošača."),
            H("7. Izmene uslova"),
            P("Uslove možemo menjati. Važeća verzija je uvek ona objavljena na ovoj stranici; datum poslednje izmene naveden je na dnu."),
            H("8. Merodavno pravo"),
            P("Na ove uslove primenjuje se pravo Republike Srbije. Sporove rešavamo dogovorom, a ako to nije moguće — pred nadležnim sudom u Beogradu."),
        ])
    if lang == "ru":
        return "\n".join([
            P(f"Используя сайт pravimajstor.rs, вы принимаете эти условия. Сервис ведёт {p['company']}, ПИБ {p['pib']}, {p['address']}."),
            H("1. Что делает сервис"),
            P("Сервис — это <strong>посредник</strong>: он сводит заказчиков и мастеров. Сервис не выполняет работы, не нанимает мастеров и не является стороной договорённости между вами и мастером."),
            H("2. Цена и оплата"),
            P("Для заказчиков сервис бесплатен. Цену работ вы обсуждаете напрямую с мастером и платите ему. Цены на странице <a href=\"/ru/cenovnik/\" class=\"inline-link\">Цены на услуги</a> — <strong>ориентировочные</strong>; точную цену мастер называет до начала работы."),
            H("3. Ответственность"),
            P("За качество работ, сроки и ущерб, причинённый во время работы, отвечает мастер, взявший заказ. Сервис проверяет мастеров при регистрации, но не может гарантировать исход каждой конкретной работы."),
            P(f"Если возникла проблема, напишите на {p['email']} — мы разбираем каждую жалобу и можем снизить мастеру рейтинг или закрыть доступ к заявкам."),
            H("4. Обязанности заказчика"),
            P("В заявке нужно указать точное описание задачи и верный контакт. Злоупотребление сервисом — ложные заявки, оскорбления мастеров, попытка обойти мастера после взятой заявки — ведёт к ограничению доступа."),
            H("5. Обязанности мастера"),
            P("Мастер обязуется указывать достоверные данные о себе и своём опыте, называть цену до начала работы и не менять её по ходу без согласия заказчика."),
            H("6. Рекламации"),
            P(f"Жалобы принимаем на {p['email']} и по телефону {p['phone']}, ежедневно с 08:00 до 23:00. Отвечаем в течение 8 дней согласно Закону о защите потребителей Республики Сербия."),
            H("7. Изменения условий"),
            P("Мы можем менять условия. Действует всегда та версия, что опубликована на этой странице; дата последнего изменения — внизу."),
            H("8. Применимое право"),
            P("К этим условиям применяется право Республики Сербия. Споры решаем переговорами, а если это невозможно — в компетентном суде в Белграде."),
        ])
    return "\n".join([
        P(f"By using pravimajstor.rs you accept these terms. The service is operated by {p['company']}, PIB {p['pib']}, {p['address']}."),
        H("1. What the service does"),
        P("The service is an <strong>intermediary</strong>: it connects customers and masters. It does not perform the work, does not employ masters and is not a party to the agreement between you and the master."),
        H("2. Price and payment"),
        P("For customers the service is free. You agree the price directly with the master and pay them. Prices on the <a href=\"/en/pricelist/\" class=\"inline-link\">Price list</a> page are <strong>indicative</strong> — the master confirms the exact price before starting."),
        H("3. Liability"),
        P("The master who accepted the job is responsible for the quality of the work, deadlines and any damage caused during it. The service verifies masters at registration but cannot guarantee the outcome of each individual job."),
        P(f"If something went wrong, write to {p['email']} — we review every complaint and may lower a master's rating or revoke their access to requests."),
        H("4. Customer obligations"),
        P("A request must contain an accurate task description and valid contact details. Misuse of the service — fake requests, abuse towards masters, attempts to bypass a master after they accepted the request — leads to restricted access."),
        H("5. Master obligations"),
        P("The master undertakes to provide accurate information about themselves and their experience, to state the price before starting work and not to change it midway without the customer's agreement."),
        H("6. Complaints"),
        P(f"We accept complaints at {p['email']} and by phone {p['phone']}, daily from 08:00 to 23:00. We respond within 8 days in accordance with the Serbian Consumer Protection Act."),
        H("7. Changes to the terms"),
        P("We may amend these terms. The version published on this page is the one in force; the date of the last change is shown at the bottom."),
        H("8. Governing law"),
        P("These terms are governed by the law of the Republic of Serbia. Disputes are resolved by agreement, and failing that before the competent court in Belgrade."),
    ])


# Описание трёх страниц: slug по языкам, заголовки, тексты.
PAGES = [
    {
        "key": "about",
        "slug": {"sr": "o-nama", "ru": "ru/o-nas", "en": "en/about"},
        "title": {
            "sr": "O nama — Pravi Majstor",
            "ru": "О нас — Pravi Majstor",
            "en": "About us — Pravi Majstor",
        },
        "desc": {
            "sr": "Ko smo i kako radimo: servis za pronalaženje proverenih majstora u Beogradu i Novom Sadu. Podaci o firmi i kontakt.",
            "ru": "Кто мы и как работаем: сервис поиска проверенных мастеров в Белграде и Нови-Саде. Реквизиты и контакты.",
            "en": "Who we are and how we work: a service for finding verified handymen in Belgrade and Novi Sad. Company details and contact.",
        },
        "h1": {"sr": "O nama", "ru": "О нас", "en": "About us"},
        "body": body_about,
    },
    {
        "key": "privacy",
        "slug": {
            "sr": "politika-privatnosti",
            "ru": "ru/politika-konfidencialnosti",
            "en": "en/privacy-policy",
        },
        "title": {
            "sr": "Politika privatnosti — Pravi Majstor",
            "ru": "Политика конфиденциальности — Pravi Majstor",
            "en": "Privacy Policy — Pravi Majstor",
        },
        "desc": {
            "sr": "Koje podatke prikupljamo preko sajta, zašto ih obrađujemo, kome se prosleđuju i koja su vaša prava.",
            "ru": "Какие данные мы собираем через сайт, зачем их обрабатываем, кому передаём и какие у вас права.",
            "en": "What data we collect through the site, why we process it, who receives it and what your rights are.",
        },
        "h1": {
            "sr": "Politika privatnosti",
            "ru": "Политика конфиденциальности",
            "en": "Privacy Policy",
        },
        "body": body_privacy,
    },
    {
        "key": "terms",
        "slug": {
            "sr": "uslovi-koriscenja",
            "ru": "ru/usloviya-ispolzovaniya",
            "en": "en/terms-of-service",
        },
        "title": {
            "sr": "Uslovi korišćenja — Pravi Majstor",
            "ru": "Условия использования — Pravi Majstor",
            "en": "Terms of Service — Pravi Majstor",
        },
        "desc": {
            "sr": "Pravila korišćenja servisa: uloga posrednika, cena i plaćanje, odgovornost, reklamacije.",
            "ru": "Правила пользования сервисом: роль посредника, цена и оплата, ответственность, рекламации.",
            "en": "Rules for using the service: intermediary role, price and payment, liability, complaints.",
        },
        "h1": {
            "sr": "Uslovi korišćenja",
            "ru": "Условия использования",
            "en": "Terms of Service",
        },
        "body": body_terms,
    },
]


def depth_prefix(slug):
    """Относительный путь до корня — для ссылок на иконки, как на других страницах."""
    return "../" * (slug.count("/") + 1)


def render(page, lang):
    ui = UI[lang]
    slug = page["slug"][lang]
    url = f"{SITE}/{slug}/"
    alts = {l: f"{SITE}/{page['slug'][l]}/" for l in ("ru", "sr", "en")}
    up = depth_prefix(slug)
    body = page["body"](lang)

    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="preload" as="font" type="font/woff2" href="/fonts/montserrat-regular.woff2" crossorigin>
  <link rel="preload" as="font" type="font/woff2" href="/fonts/montserrat-bold.woff2" crossorigin>

  <title>{page['title'][lang]}</title>
  <meta name="description" content="{page['desc'][lang]}">
  <meta name="author" content="Pravi Majstor">
  <!-- PRELAUNCH:START — убрать этот блок при запуске, вернув строку из PRELAUNCH:ORIGINAL -->
  <meta name="robots" content="noindex, nofollow">
  <!-- PRELAUNCH:ORIGINAL <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large"> -->
  <!-- PRELAUNCH:END -->
  <link rel="canonical" href="{url}">

  <link rel="alternate" hreflang="ru" href="{alts['ru']}">
  <link rel="alternate" hreflang="sr" href="{alts['sr']}">
  <link rel="alternate" hreflang="en" href="{alts['en']}">
  <link rel="alternate" hreflang="x-default" href="{alts['sr']}">

  <meta property="og:type" content="website">
  <meta property="og:url" content="{url}">
  <meta property="og:title" content="{page['title'][lang]}">
  <meta property="og:description" content="{page['desc'][lang]}">
  <meta property="og:image" content="{SITE}/image/og-preview.png">
  <meta property="og:locale" content="{ui['locale']}">

  <link rel="icon" type="image/svg+xml" href="{up}image/favicon.svg">
  <link rel="icon" type="image/x-icon" href="{up}image/favicon.ico">
  <link rel="manifest" href="/site.webmanifest">
  <meta name="theme-color" content="#FDB913">

  <script>window.__FORCE_LANG__ = '{lang}';</script>

  <script type="application/ld+json">
  [
    {{
      "@context": "https://schema.org",
      "@type": "WebPage",
      "name": "{page['h1'][lang]}",
      "url": "{url}",
      "inLanguage": "{lang}",
      "isPartOf": {{ "@type": "WebSite", "name": "Pravi Majstor", "url": "{SITE}" }},
      "publisher": {{ "@type": "Organization", "name": "Pravi Majstor", "url": "{SITE}" }}
    }},
    {{
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      "itemListElement": [
        {{ "@type": "ListItem", "position": 1, "name": "{ui['crumb_home']}", "item": "{SITE}{ui['home']}" }},
        {{ "@type": "ListItem", "position": 2, "name": "{page['h1'][lang]}", "item": "{url}" }}
      ]
    }}
  ]
  </script>

  <link rel="stylesheet" href="{up}style.css">
  <link rel="stylesheet" href="{up}service.css">
  <script src="{up}script.js" defer></script>
</head>

<body>
  <div class="gradient-dots-bg"></div>

  <header>
    <div class="logo">
      <div class="logo-text">
        <a href="{ui['home']}" class="logo-link" aria-label="{ui['logo_aria']}"><div class="logo-title">Pravi Majstor</div></a>
        <div class="subtitle">{ui['subtitle']}</div>
        <div class="subtitle header-phone">
          <a href="tel:+995557645196" class="header-phone-link">// +995 557 645 196</a>
        </div>
        <div class="subtitle header-support">
          <a href="https://t.me/masterasupport" target="_blank" class="header-support-link">// @masterasupport</a>
        </div>
      </div>
    </div>
    <div class="header-controls cen-header-controls" style="--cen-lang-width: {ui['lang_width']}px">
      <!-- Переключателя города нет: страница общая для Белграда и Нови-Сада. -->
      <div class="header-group">
        <div class="language-switcher">
          <a href="/{page['slug']['ru']}/" class="lang-btn{' active' if lang == 'ru' else ''}" data-lang="ru">RUS</a>
          <a href="/{page['slug']['sr']}/" class="lang-btn{' active' if lang == 'sr' else ''}" data-lang="sr">SRB</a>
          <a href="/{page['slug']['en']}/" class="lang-btn{' active' if lang == 'en' else ''}" data-lang="en">ENG</a>
        </div>
      </div>

      <div class="header-group">
        <a href="{ui['masters']}" class="audience-link"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10"/><path d="M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg> <span class="audience-link-text">{ui['masters_text']}</span></a>

        <div class="online-counter">
          <span class="online-indicator"></span>
          <span class="online-text">{ui['online']}<strong class="online-count" data-base="3">3</strong>{ui['online_tail']}</span>
        </div>
      </div>
    </div>
  </header>

  <main class="cen-page">
    <nav class="breadcrumb" aria-label="{ui['aria']}">
      <div class="breadcrumb-inner">
        <a href="{ui['home']}">{ui['crumb_home']}</a>
        <span class="breadcrumb-sep" aria-hidden="true">/</span>
        <span aria-current="page">{page['h1'][lang]}</span>
      </div>
    </nav>

    <section class="cen-hero">
      <h1 class="service-title">{page['h1'][lang]}</h1>
    </section>

    <section class="legal-content">
{body}
      <p class="legal-updated">{ui['updated']}: {UPDATED}</p>
    </section>
  </main>

  <footer>
    <p class="footer-text">
      {ui['footer_owner']} • <a href="{ui['price_url']}" class="footer-link cen-footer-link">{ui['price_text']}</a>
    </p>
    <p class="footer-hours">{ui['hours']}</p>
    <p class="footer-privacy">
      {ui['privacy_note']}
    </p>
  </footer>
</body>
</html>
"""


def main():
    created = existed = 0
    for page in PAGES:
        for lang in ("sr", "ru", "en"):
            slug = page["slug"][lang]
            path = ROOT / slug / "index.html"
            if path.exists():
                print(f"  = уже есть  /{slug}/")
                existed += 1
                continue
            if not DRY:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(render(page, lang), encoding="utf-8")
            created += 1
            print(f"  ✓ создано   /{slug}/")

    print(f"\nСоздано: {created}, уже существовало: {existed}")
    if DRY:
        print("(--dry-run: файлы не создавались)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
