// ============================================
// ОПТИМИЗИРОВАННЫЙ SCRIPT.JS — MULTILINGUAL
// Языки: RU / SR / EN
// ============================================

// ============================================
// ГЛОБАЛЬНЫЕ ПЕРЕВОДЫ (все alert и тексты)
// ============================================

const i18n = {
    ru: {
        phoneInvalid:        'Пожалуйста, введите корректный сербский номер телефона в формате: +381XXXXXXXX (8–10 цифр после +381)',
        telegramInvalid:     'Пожалуйста, введите корректный Telegram username (например: @username) или номер телефона',
        contactRequired:     'Пожалуйста, заполните хотя бы один из контактов: Telegram или WhatsApp',
        submitError:         'Ошибка при отправке. Попробуйте ещё раз.',
        photoLabel:          '📷 Фото проблемы (по желанию, до 3)',
        photoAdd:            'Прикрепить фото',
        photoTooMany:        'Можно прикрепить не более 3 фото',
        photoBadType:        'Можно прикреплять только изображения',
        photoTooBig:         'Файл слишком большой (до 10 МБ)',
        photoRemove:         'Удалить',
        masterFinishTelegram:'✅ Завершить регистрацию в Telegram',
        urgentLabel:         '🚨 Срочный заказ',
    },
    sr: {
        phoneInvalid:        'Molimo unesite ispravan srpski broj telefona u formatu: +381XXXXXXXX (8–10 cifara posle +381)',
        telegramInvalid:     'Molimo unesite ispravno Telegram korisničko ime (npr: @username) ili broj telefona',
        contactRequired:     'Molimo popunite bar jedno polje za kontakt: Telegram ili WhatsApp',
        submitError:         'Došlo je do greške pri slanju. Pokušajte ponovo.',
        photoLabel:          '📷 Fotografija problema (opciono, do 3)',
        photoAdd:            'Priloži fotografiju',
        photoTooMany:        'Možete priložiti najviše 3 fotografije',
        photoBadType:        'Mogu se priložiti samo slike',
        photoTooBig:         'Fajl je prevelik (do 10 MB)',
        photoRemove:         'Ukloni',
        masterFinishTelegram:'✅ Završi registraciju u Telegramu',
        urgentLabel:         '🚨 Hitna porudžbina',
    },
    en: {
        phoneInvalid:        'Please enter a valid Serbian phone number in the format: +381XXXXXXXX (8–10 digits after +381)',
        telegramInvalid:     'Please enter a valid Telegram username (e.g. @username) or phone number',
        contactRequired:     'Please fill in at least one contact field: Telegram or WhatsApp',
        submitError:         'An error occurred while submitting. Please try again.',
        photoLabel:          '📷 Photo of the problem (optional, up to 3)',
        photoAdd:            'Attach photo',
        photoTooMany:        'You can attach up to 3 photos',
        photoBadType:        'Only images can be attached',
        photoTooBig:         'File is too large (up to 10 MB)',
        photoRemove:         'Remove',
        masterFinishTelegram:'✅ Finish registration in Telegram',
        urgentLabel:         '🚨 Urgent order',
    }
};

// Публичный username бота мастеров — для диплинка «завершить регистрацию».
const MASTER_BOT_DEEPLINK = 'https://t.me/mastera_serbia_bot?start=master';

// Глобальная переменная текущего языка
// window.__FORCE_LANG__ устанавливается в языковых подстраницах (/ru/, /sr/, /en/)
let currentLang = window.__FORCE_LANG__ || 'ru';

// Вспомогательная функция — получить перевод
function t(key) {
    return (i18n[currentLang] || i18n.ru)[key] || i18n.ru[key] || key;
}

// ============================================
// ИНИЦИАЛИЗАЦИЯ
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    initStatsAnimation();
    initScrollAnimation();
    initSmoothScroll();
    initButtonHoverEffects();
    initOnlineCounter();
    initLanguageSwitcher();
    initTypingEffect();
    initServiceTypingEffect();
    initModalForms();
    initScrollToTop();
    initClientLeadFormTracking();
    initClientPhotoUpload();
    initClientDistrictOptions();
    initClientUrgentOption();
    initMasterLeadFormTracking();
    initWhatsAppButtonTracking();
    initBannerShift();
    initFAQ();
});

// ============================================
// 1. АНИМАЦИЯ ЦИФР (УНИВЕРСАЛЬНАЯ)
// ============================================

function initStatsAnimation() {
    const stats = document.querySelectorAll('.stat-number');
    if (stats.length === 0) return;

    const observerOptions = {
        threshold: 0.5,
        rootMargin: '0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.target.dataset.animated) {
                const element = entry.target;
                const target = parseInt(element.dataset.target, 10);
                const suffix = element.dataset.suffix || '';
                const startVal = parseInt(element.dataset.start, 10) || 0;
                element.dataset.animated = 'true';
                animateCounter(element, target, 2500, suffix, startVal);
                observer.unobserve(element);
            }
        });
    }, observerOptions);

    stats.forEach(stat => {
        if (!stat.dataset.target) {
            const rawText = stat.textContent.trim();
            const match = rawText.match(/^(\d+)(.*)$/);
            if (match) {
                stat.dataset.target = match[1];
                stat.dataset.suffix = match[2];
            } else {
                return;
            }
        }
        stat.textContent = '0' + (stat.dataset.suffix || '');
        observer.observe(stat);
    });
}

function animateCounter(element, target, duration, suffix, start) {
    start = start || 0;
    const range = target - start;
    const isReverse = start > target;
    const startTime = performance.now();

    function ease(t) {
        return isReverse ? t : (1 - Math.pow(1 - t, 5));
    }

    // Разделитель тысяч (неразрывный пробел) — для крупных сумм вроде «45 000 RSD»
    function fmt(n) {
        return n.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
    }

    function animate(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const easedProgress = ease(progress);
        const current = Math.floor(start + easedProgress * range);
        element.textContent = fmt(current) + suffix;
        if (progress < 1) {
            requestAnimationFrame(animate);
        } else {
            element.textContent = fmt(target) + suffix;
        }
    }

    requestAnimationFrame(animate);
}

// ============================================
// 2. АНИМАЦИЯ ПОЯВЛЕНИЯ ПРИ СКРОЛЛЕ
// ============================================

function initScrollAnimation() {
    const elementsToAnimate = document.querySelectorAll('.section-card');

    if (!window.IntersectionObserver) {
        elementsToAnimate.forEach(el => el.style.opacity = 1);
        return;
    }

    const scrollObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.target.dataset.scrollAnimated) {
                entry.target.dataset.scrollAnimated = 'true';
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });

    elementsToAnimate.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        scrollObserver.observe(card);
    });
}

// ============================================
// 3. ПЛАВНАЯ ПРОКРУТКА
// ============================================

function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href === '#' || href === '#!') return;
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
}

// ============================================
// 4. ЭФФЕКТЫ НАВЕДЕНИЯ НА КНОПКИ
// ============================================

function initButtonHoverEffects() {
    document.querySelectorAll('.cta-button').forEach(button => {
        button.addEventListener('mouseenter', function () {
            this.style.transform = 'scale(1.05)';
        });
        button.addEventListener('mouseleave', function () {
            this.style.transform = 'scale(1)';
        });
    });
}

// ============================================
// 5. СЧЕТЧИК ОНЛАЙН МАСТЕРОВ
// ============================================

function initOnlineCounter() {
    const counterElement = document.querySelector('.online-count');
    if (!counterElement) return;

    const minCount = 3;
    const maxCount = 16;
    const baseVal = parseInt(counterElement.dataset.base, 10);
    const initialCount = !isNaN(baseVal) ? baseVal : Math.floor(Math.random() * 8) + 1;
    counterElement.textContent = initialCount;
    let currentCount = initialCount;

    function updateCounter() {
        const change = Math.floor(Math.random() * 7) - 3; // -3..+3
        let targetCount = Math.max(minCount, Math.min(maxCount, currentCount + change));
        counterElement.classList.add('updating');
        setTimeout(() => {
            counterElement.textContent = targetCount;
            counterElement.classList.remove('updating');
            currentCount = targetCount;
        }, 150);
    }

    function scheduleNextUpdate() {
        const delay = Math.random() * 8000 + 12000;
        setTimeout(() => {
            updateCounter();
            scheduleNextUpdate();
        }, delay);
    }

    setTimeout(scheduleNextUpdate, 5000);
}

// ============================================
// 6. FAQ АККОРДЕОН
// ============================================

function initFAQ() {
    const faqItems = document.querySelectorAll('.faq-item');
    if (faqItems.length === 0) return;

    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        question.addEventListener('click', () => {
            faqItems.forEach(other => {
                if (other !== item) other.classList.remove('active');
            });
            item.classList.toggle('active');
        });
    });
}

// ============================================
// 7. ПЕРЕКЛЮЧЕНИЕ ЯЗЫКОВ
// ============================================

function initLanguageSwitcher() {
    const langButtons = document.querySelectorAll('.lang-btn');

    // На языковых подстраницах (/ru/, /sr/, /en/) язык задан принудительно
    if (window.__FORCE_LANG__) {
        setLanguage(window.__FORCE_LANG__);
        return;
    }

    const browserLang = navigator.language || navigator.userLanguage;

    let defaultLang = 'ru';
    if (browserLang.startsWith('sr')) defaultLang = 'sr';
    else if (browserLang.startsWith('en')) defaultLang = 'en';

    const savedLang = localStorage.getItem('language') || defaultLang;
    setLanguage(savedLang);

    langButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const lang = btn.dataset.lang;
            setLanguage(lang);
            localStorage.setItem('language', lang);
        });
    });
}

function setLanguage(lang) {
    // Обновляем глобальную переменную
    currentLang = lang;

    // Активная кнопка
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.lang === lang);
    });

    // HTML lang атрибут
    document.documentElement.lang = lang;

    // Переводим все элементы с data-атрибутами
    document.querySelectorAll('[data-ru], [data-sr], [data-en]').forEach(element => {
        if (element.classList.contains('hero-title')) {
            const cursor = element.querySelector('.typing-cursor');
            if (cursor) cursor.remove();
            const text = element.dataset[lang];
            if (text) element.textContent = text;
            return;
        }

        const text = element.dataset[lang];
        if (text) {
            if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                element.placeholder = text;
            } else if (element.tagName === 'OPTION') {
                element.textContent = text;
            } else if (element.hasAttribute('content')) {
                element.setAttribute('content', text);
            } else {
                element.textContent = text;
            }
        }
    });

    // Placeholders через отдельные атрибуты
    document.querySelectorAll('[data-ru-placeholder], [data-sr-placeholder], [data-en-placeholder]').forEach(element => {
        const placeholder = element.dataset[lang + 'Placeholder'];
        if (placeholder) element.placeholder = placeholder;
    });

    // Title страницы
    const titleElement = document.querySelector('title');
    if (titleElement && titleElement.dataset[lang]) {
        titleElement.textContent = titleElement.dataset[lang];
    }

    // Суффиксы счётчиков статистики
    document.querySelectorAll('.stat-number[data-suffix-ru], .stat-number[data-suffix-sr], .stat-number[data-suffix-en]').forEach(element => {
        const suffixKey = lang === 'en' ? 'suffixEn' : lang === 'sr' ? 'suffixSr' : 'suffixRu';
        const newSuffix = element.dataset[suffixKey];
        if (newSuffix) {
            element.dataset.suffix = newSuffix;
            if (element.dataset.animated === 'true') {
                const target = parseInt(element.dataset.target, 10);
                element.textContent = target + newSuffix;
            } else {
                element.textContent = '0' + newSuffix;
            }
        }
    });

    // Meta description
    const metaDesc = document.querySelector('meta[name="description"]');
    if (metaDesc && metaDesc.dataset[lang]) {
        metaDesc.setAttribute('content', metaDesc.dataset[lang]);
    }

    // title-атрибуты на полях ввода (браузерные подсказки при нативной валидации)
    document.querySelectorAll('input[type="tel"][pattern]').forEach(el => {
        el.title = t('phoneInvalid');
    });
    document.querySelectorAll('input[name="telegram"][pattern]').forEach(el => {
        el.title = t('telegramInvalid');
    });
}

// ============================================
// 8. МОДАЛЬНЫЕ ОКНА
// ============================================

function initModalForms() {
    // Закрытие по клику вне модального окна
    window.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal')) {
            e.target.style.display = 'none';
            // Окно закрыто в обход _modal — снимаем блокировку прокрутки вручную
            _syncScrollLock();
        }
    });

    // Закрытие по ESC
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeClientLeadForm();
            closeMasterLeadForm();
            closeThankYou();
            closeMasterThankYou();
        }
    });

    initPhoneFormatting();
}

// Форматирование телефонных номеров
function initPhoneFormatting() {
    const phoneInputs = document.querySelectorAll('#leadPhone, #masterLeadPhone');

    phoneInputs.forEach(input => {
        input.addEventListener('input', (e) => {
            let value = e.target.value.replace(/\D/g, '');
            if (!value.startsWith('381') && value.length > 0) {
                value = '381' + value;
            }
            if (value.length > 13) value = value.substring(0, 13);
            e.target.value = value.length > 0 ? '+' + value : '';
        });

        input.addEventListener('focus', (e) => {
            if (e.target.value === '') e.target.value = '+381';
        });

        input.addEventListener('blur', (e) => {
            if (e.target.value === '+381') e.target.value = '';
        });
    });
}

// ============================================
// 9. ВАЛИДАЦИЯ — ОБЩИЕ ФУНКЦИИ
// ============================================

// Сербские номера: +381 и 8–10 цифр (моб. и городские). Без белого списка кодов оператора.
const PHONE_PATTERN    = /^\+381[0-9]{8,10}$/;
const TELEGRAM_PATTERN = /^(@[a-zA-Z0-9_]{5,32}|[0-9]{9,15})$/;

function validatePhone(phoneInput) {
    if (!phoneInput) return true;
    const val = phoneInput.value;

    if (!PHONE_PATTERN.test(val)) {
        alert(t('phoneInvalid'));
        phoneInput.focus();
        return false;
    }

    return true;
}

function validateTelegram(telegramInput) {
    if (!telegramInput) return true;
    const val = telegramInput.value.trim();
    if (!val) return true; // необязательное поле — проверяем только если заполнено

    if (!TELEGRAM_PATTERN.test(val)) {
        alert(t('telegramInvalid'));
        telegramInput.focus();
        return false;
    }
    return true;
}

// Валидация стандартных форм (clientForm / masterForm)
function validateForm(e) {
    const form = e.target;
    const phoneInput    = form.querySelector('input[type="tel"]');
    const telegramInput = form.querySelector('input[name="telegram"]');

    if (!validatePhone(phoneInput)) { e.preventDefault(); return false; }
    if (!validateTelegram(telegramInput)) { e.preventDefault(); return false; }

    return true;
}

// ============================================
// 10. ЛИД-ФОРМА КЛИЕНТА
// ============================================

// Адрес эндпоинта бота для приёма заявок с сайта (напрямую, без секрета).
// Защита от спама на стороне бота: проверка домена-источника + honeypot.
const BOT_REQUEST_URL = 'https://mastera-serbia-bot-mastera-serbii.up.railway.app/site/new-request';
// Эндпоинт бота для анкет мастеров с сайта (уведомление админу-лид).
const BOT_MASTER_URL  = 'https://mastera-serbia-bot-mastera-serbii.up.railway.app/site/new-master';

// Канонический (русский) город по URL страницы — бот хранит города по-русски
// (config.yaml → cities). /novi-sad/ → «Нови-Сад», иначе «Белград» (по умолчанию).
function botCityFromUrl() {
    return window.location.pathname.includes('novi-sad') ? 'Нови-Сад' : 'Белград';
}

// Район на сайте выбирается слугами (Vake, Saburtalo...), а бот ждёт названия по-русски.
const BOT_DISTRICT_MAP = {
    // Белград (совпадают с config.yaml бота → cities['Белград'])
    Vracar: 'Врачар', NoviBeograd: 'Нови-Београд', Zvezdara: 'Звездара', Vozdovac: 'Вождовац',
    Zemun: 'Земун', StariGrad: 'Стари-Град', SavskiVenac: 'Савски-Венац', Palilula: 'Палилула',
    Cukarica: 'Чукарица', Rakovica: 'Раковица',
    // Нови-Сад (совпадают с config.yaml бота → cities['Нови-Сад']).
    // StariGrad общий с Белградом (в обоих городах «Стари-Град» — задан выше).
    // ВНИМАНИЕ: Ново-Насеље — с сербской «њ», точь-в-точь как в config.yaml бота.
    Liman: 'Лиман', Petrovaradin: 'Петроварадин', Detelinara: 'Детелинара',
    NovoNaselje: 'Ново-Насеље', Podbara: 'Подбара', Grbavica: 'Грбавица', Telep: 'Телеп',
    Other: 'Другой'
};

// Категория работ в EN/GE формах выбирается на своём языке, а бот принимает только
// канонические русские названия (specialties в config.yaml). Без этого маппинга
// заявки с английской/грузинской форм бот отбраковывает (на email они всё равно уходят).
// RU-значения уже канонические — проходят через fallback в sendLeadToBot без записи здесь.
const BOT_SERVICE_MAP = {
    // EN
    Plumbing: 'Сантехника', Electrical: 'Электрика', Repair: 'Ремонт',
    Furniture: 'Мебель', Movers: 'Грузчики', Cleaning: 'Клининг', Other: 'Другое',
    // GE
    'სანტექნიკა': 'Сантехника', 'ელექტრიკა': 'Электрика', 'რემონტი': 'Ремонт',
    'ავეჯი': 'Мебель', 'მზიდვები': 'Грузчики', 'დასუფთავება': 'Клининг', 'სხვა': 'Другое'
};

// Отправка клиентской заявки в Telegram-бота через прокси.
// Не блокирует пользователя и не зависит от ответа — заявка в любом случае уйдёт на email.
function sendLeadToBot(formData) {
    try {
        const get = (k) => (formData.get(k) || '').toString().trim();

        const phone    = get('phone');
        const telegram = get('telegram');
        const whatsapp = get('whatsapp');
        const name     = get('name');

        // Контакты — откроются мастеру ТОЛЬКО после взятия заявки и списания.
        const contactParts = [];
        if (phone)    contactParts.push('📱 ' + phone);
        if (telegram) contactParts.push('✈️ Telegram: ' + telegram);
        if (whatsapp) contactParts.push('🟢 WhatsApp: ' + whatsapp);

        // Что видят мастера СРАЗУ (в превью, до взятия): имя + задача, без контактов.
        const descParts = [];
        if (name) descParts.push('Имя: ' + name);
        descParts.push('Задача: ' + (get('message') || '—'));

        const payload = {
            city:        botCityFromUrl(),                  // город (Белград/Нови-Сад) — бот рассылает своему городу
            district:    BOT_DISTRICT_MAP[get('district')] || get('district') || 'Другой',
            subdistrict: 'Не указан',                       // подрайон убрали — адрес точнее
            category:    BOT_SERVICE_MAP[get('service')] || get('service') || 'Другое',
            description: descParts.join('\n'),              // имя + задача → видно в превью
            address:     'Не указан',                       // адрес у клиента не спрашиваем — только район
            contact:     contactParts.join('\n') || 'Нет контакта', // скрыто до оплаты
            honeypot:    get('_gotcha'),                    // антиспам: люди это поле не заполняют
            lang:        ['ru', 'en', 'sr'].includes(currentLang) ? currentLang : 'ru',
            // Срочность: галочка без name (в Formspree не уходит) — читаем состояние из DOM.
            // false по умолчанию; бот помечает «🚨 СРОЧНО» только срочные заявки.
            urgent:      !!(document.getElementById('leadUrgent') && document.getElementById('leadUrgent').checked),
            photos:      leadPhotoDataUrls.slice(0, MAX_LEAD_PHOTOS) // сжатые фото (base64), до 3
        };

        // keepalive имеет лимит тела ~64 КБ — при наличии фото его НЕ используем
        // (заявку всё равно держит открытая модалка благодарности, навигации нет).
        const hasPhotos = payload.photos.length > 0;
        fetch(BOT_REQUEST_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
            keepalive: !hasPhotos
        }).catch(() => {}); // молча игнорируем — на email заявка всё равно уходит
    } catch (e) {
        console.error('sendLeadToBot error:', e);
    }
}

// ============================================
// 10.0 ФОТО ПРОБЛЕМЫ В КЛИЕНТСКОЙ ФОРМЕ (до 3, по желанию)
// ============================================

const MAX_LEAD_PHOTOS = 3;          // максимум фото на заявку
const LEAD_PHOTO_MAX_BYTES = 10 * 1024 * 1024;  // ограничение на исходный файл (10 МБ)
let leadPhotoDataUrls = [];          // сжатые dataURL для отправки в бота

// Сжимает изображение через <canvas> до ~1280px по длинной стороне (JPEG ~0.7).
// Возвращает Promise<dataURL>. На ошибке — отклоняется.
function compressImage(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onerror = () => reject(new Error('read error'));
        reader.onload = () => {
            const img = new Image();
            img.onerror = () => reject(new Error('decode error'));
            img.onload = () => {
                const MAX = 1280;
                let { width, height } = img;
                if (width > MAX || height > MAX) {
                    const k = Math.min(MAX / width, MAX / height);
                    width = Math.round(width * k);
                    height = Math.round(height * k);
                }
                const canvas = document.createElement('canvas');
                canvas.width = width;
                canvas.height = height;
                canvas.getContext('2d').drawImage(img, 0, 0, width, height);
                resolve(canvas.toDataURL('image/jpeg', 0.7));
            };
            img.src = reader.result;
        };
        reader.readAsDataURL(file);
    });
}

// Инжектит блок загрузки фото в clientLeadForm (как initClientDistrictOptions — без правки HTML).
function initClientPhotoUpload() {
    const form = document.getElementById('clientLeadForm');
    if (!form) return;
    if (form.querySelector('.lead-photo-wrap')) return; // уже добавлено

    const wrap = document.createElement('div');
    wrap.className = 'lead-photo-wrap';

    const label = document.createElement('label');
    label.className = 'lead-photo-label';
    label.textContent = t('photoLabel');

    const input = document.createElement('input');
    input.type = 'file';
    input.name = 'photo';            // попадёт в FormData → Formspree приложит оригиналы к email
    input.accept = 'image/*';
    input.multiple = true;
    input.className = 'lead-photo-input';
    // Прячем нативный input: его текст («Выбрать файлы / Файлы не выбраны») задаётся
    // локалью браузера и не переводится. Вместо него — своя кнопка с переводом.

    // Кастомная кнопка вместо нативной «Выбрать файлы»
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'lead-photo-btn';
    btn.textContent = t('photoAdd');
    btn.addEventListener('click', () => input.click());

    const previews = document.createElement('div');
    previews.className = 'lead-photo-previews';

    wrap.appendChild(label);
    wrap.appendChild(input);
    wrap.appendChild(btn);
    wrap.appendChild(previews);

    // Вставляем перед блоком согласия/кнопкой отправки (или в конец формы)
    const consent = form.querySelector('.consent-label') || form.querySelector('button[type="submit"]');
    if (consent) form.insertBefore(wrap, consent);
    else form.appendChild(wrap);

    function renderPreviews() {
        previews.innerHTML = '';
        leadPhotoDataUrls.forEach((url, idx) => {
            const item = document.createElement('div');
            item.className = 'lead-photo-thumb';
            const im = document.createElement('img');
            im.src = url;
            const rm = document.createElement('button');
            rm.type = 'button';
            rm.className = 'lead-photo-remove';
            rm.setAttribute('aria-label', t('photoRemove'));
            rm.textContent = '×';
            rm.addEventListener('click', () => {
                leadPhotoDataUrls.splice(idx, 1);
                renderPreviews();
            });
            item.appendChild(im);
            item.appendChild(rm);
            previews.appendChild(item);
        });
    }

    input.addEventListener('change', async () => {
        const files = Array.from(input.files || []);
        input.value = ''; // позволяем выбрать те же файлы повторно после удаления
        for (const file of files) {
            if (leadPhotoDataUrls.length >= MAX_LEAD_PHOTOS) { alert(t('photoTooMany')); break; }
            if (!file.type.startsWith('image/')) { alert(t('photoBadType')); continue; }
            if (file.size > LEAD_PHOTO_MAX_BYTES) { alert(t('photoTooBig')); continue; }
            try {
                leadPhotoDataUrls.push(await compressImage(file));
            } catch (e) {
                console.error('compressImage error:', e);
            }
        }
        renderPreviews();
    });

    // Доступно снаружи для очистки после успешной отправки
    initClientPhotoUpload._reset = () => { leadPhotoDataUrls = []; renderPreviews(); };
}

// Отправка анкеты мастера в Telegram-бота (лид админу). Fire-and-forget, не влияет на email.
function sendMasterLeadToBot(formData) {
    try {
        const get = (k) => (formData.get(k) || '').toString().trim();
        const specialty = get('specialty');
        const experience = get('experience');
        const payload = {
            name:      get('name'),
            phone:     get('phone'),
            telegram:  get('telegram'),
            whatsapp:  get('whatsapp'),
            specialty: experience ? `${specialty} (опыт: ${experience} лет)` : specialty,
            message:   get('message'),
            honeypot:  get('_gotcha'),
            lang:      ['ru', 'en', 'sr'].includes(currentLang) ? currentLang : 'ru'
        };
        fetch(BOT_MASTER_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
            keepalive: true
        }).catch(() => {});
    } catch (e) {
        console.error('sendMasterLeadToBot error:', e);
    }
}

// Добавляет в модалку благодарности мастеру кнопку «Завершить регистрацию в Telegram» (один раз).
function ensureMasterTelegramButton() {
    const modal = document.getElementById('masterThankYouModal');
    if (!modal) return;
    const content = modal.querySelector('.thank-you-content');
    if (!content || content.querySelector('.master-tg-finish-btn')) return;
    const link = document.createElement('a');
    link.className = 'master-tg-finish-btn';
    link.href = MASTER_BOT_DEEPLINK;
    link.target = '_blank';
    link.rel = 'noopener';
    link.textContent = t('masterFinishTelegram');
    // Вставляем перед кнопкой «Отлично!», если она есть
    const okBtn = content.querySelector('.thank-you-btn');
    if (okBtn) content.insertBefore(link, okBtn);
    else content.appendChild(link);
}

// ============================================
// 10.1 КАСКАД: РАЙОН → ПОДРАЙОН (данные из бота, config.yaml)
// ============================================

// Недостающие на сайте районы бота (slug -> подпись по языкам). Добавляются в <select> скриптом.
const DISTRICT_LABELS = {
    Vracar:      { ru: 'Врачар',       en: 'Vračar',       sr: 'Vračar' },
    NoviBeograd: { ru: 'Нови-Београд', en: 'New Belgrade', sr: 'Novi Beograd' },
    Zvezdara:    { ru: 'Звездара',     en: 'Zvezdara',     sr: 'Zvezdara' },
    Vozdovac:    { ru: 'Вождовац',     en: 'Voždovac',     sr: 'Voždovac' },
    Zemun:       { ru: 'Земун',        en: 'Zemun',        sr: 'Zemun' },
    StariGrad:   { ru: 'Стари-Град',   en: 'Stari Grad',   sr: 'Stari Grad' },
    SavskiVenac: { ru: 'Савски-Венац', en: 'Savski Venac', sr: 'Savski Venac' },
    Palilula:    { ru: 'Палилула',     en: 'Palilula',     sr: 'Palilula' },
    Cukarica:    { ru: 'Чукарица',     en: 'Čukarica',     sr: 'Čukarica' },
    Rakovica:    { ru: 'Раковица',     en: 'Rakovica',     sr: 'Rakovica' }
};

// Дозаполняет недостающие районы бота в клиентской форме на всех страницах —
// через JS, без правки HTML каждой страницы.
function initClientDistrictOptions() {
    const form = document.getElementById('clientLeadForm');
    if (!form) return;
    const districtSel = form.querySelector('select[name="district"]');
    if (!districtSel) return;

    const lang = ['ru', 'en', 'sr'].includes(currentLang) ? currentLang : 'ru';

    // Дозаполняем недостающие районы бота (Мтацминда, Крцаниси) — перед «Other», если он есть
    Object.keys(DISTRICT_LABELS).forEach(function (slug) {
        if (districtSel.querySelector('option[value="' + slug + '"]')) return;
        const opt = document.createElement('option');
        opt.value = slug;
        opt.textContent = DISTRICT_LABELS[slug][lang] || DISTRICT_LABELS[slug].ru;
        const other = districtSel.querySelector('option[value="Other"]');
        if (other) districtSel.insertBefore(opt, other);
        else districtSel.appendChild(opt);
    });
}

// Инжектит галочку «Срочный заказ» в клиентскую форму на всех страницах —
// через JS, без правки HTML каждой страницы (как фото/районы выше).
// Галочка необязательная и по умолчанию снята. У неё НЕТ name — она не уходит
// в Formspree; состояние читается в sendLeadToBot и шлётся боту полем urgent.
function initClientUrgentOption() {
    const form = document.getElementById('clientLeadForm');
    if (!form) return;
    if (form.querySelector('.lead-urgent-label')) return; // уже добавлено

    // Точка вставки ищется ДО создания нашей метки, иначе querySelector('.consent-label')
    // зацепил бы её саму (у неё тот же класс consent-label для одинакового вида).
    const consent = form.querySelector('.consent-label') || form.querySelector('button[type="submit"]');

    const label = document.createElement('label');
    // Тот же класс, что у строки согласия → идентичный стиль (в т.ч. компактный чекбокс,
    // иначе общий стиль формы растягивает input на всю ширину). Своя метка — для guard.
    label.className = 'consent-label lead-urgent-label';

    const input = document.createElement('input');
    input.type = 'checkbox';
    input.id = 'leadUrgent';   // без name — в Formspree не уходит, читаем в sendLeadToBot

    const span = document.createElement('span');
    // data-атрибуты → строка переводится автоматически при смене языка (см. setLanguage)
    span.setAttribute('data-ru', i18n.ru.urgentLabel);
    span.setAttribute('data-sr', i18n.sr.urgentLabel);
    span.setAttribute('data-en', i18n.en.urgentLabel);
    span.textContent = t('urgentLabel');

    label.appendChild(input);
    label.appendChild(span);

    // Вставляем прямо над строкой согласия (или перед кнопкой отправки, если согласия нет)
    if (consent) form.insertBefore(label, consent);
    else form.appendChild(label);
}

function initClientLeadFormTracking() {
    const leadForm = document.getElementById('clientLeadForm');
    if (!leadForm) return;

    let isSubmitting = false;

    leadForm.addEventListener('submit', async function (e) {
        e.preventDefault();
        if (isSubmitting) return;
        if (!validateLeadForm(e)) return;

        isSubmitting = true;

        const formData = new FormData(leadForm);
        const transactionId = 'client_' + Date.now();

        // Дублируем заявку в Telegram-бота (fire-and-forget, не влияет на отправку на email)
        sendLeadToBot(formData);

        try {
            const response = await fetch('https://formspree.io/f/xljrrklq', {
                method: 'POST',
                body: formData,
                headers: { 'Accept': 'application/json' }
            });

            const data = await response.json();
            if (!response.ok) throw new Error(data.error || 'Submit failed');

            if (typeof gtag === 'function') {
                gtag('event', 'generate_lead_client', {
                    form_name: 'client_lead_form',
                    form_location: 'Заявка клиента',
                    user_type: 'client',
                    value: 1,
                    currency: 'USD'
                });
            }

            closeClientLeadForm();
            openThankYou();
            leadForm.reset();
            if (initClientPhotoUpload._reset) initClientPhotoUpload._reset(); // чистим превью фото

        } catch (error) {
            console.error(error);
            alert(t('submitError'));
            isSubmitting = false;
        }
    });

    // Checkbox
    const leadConsent   = document.getElementById('leadConsent');
    const leadSubmitBtn = document.getElementById('leadSubmitBtn');
    if (leadConsent && leadSubmitBtn) {
        leadSubmitBtn.disabled = !leadConsent.checked;
        leadConsent.addEventListener('change', function () {
            leadSubmitBtn.disabled = !this.checked;
        });
    }
}

function validateLeadForm(e) {
    const form          = e.target;
    const phoneInput    = document.getElementById('leadPhone');
    const telegramInput = form.querySelector('input[name="telegram"]');
    const whatsappInput = form.querySelector('input[name="whatsapp"]');

    const telegramValue = telegramInput ? telegramInput.value.trim() : '';
    const whatsappValue = whatsappInput ? whatsappInput.value.trim() : '';

    if (!telegramValue && !whatsappValue) {
        alert(t('contactRequired'));
        if (telegramInput && !telegramValue) telegramInput.focus();
        else if (whatsappInput) whatsappInput.focus();
        return false;
    }

    if (!validatePhone(phoneInput)) return false;
    if (telegramValue && !validateTelegram(telegramInput)) return false;

    return true;
}

// ============================================
// 11. ЛИД-ФОРМА МАСТЕРА
// ============================================

function initMasterLeadFormTracking() {
    const masterLeadForm = document.getElementById('masterLeadForm');
    if (!masterLeadForm) return;

    let isSubmitting = false;

    // Кнопка-диплинк в модалке благодарности готовится заранее (до открытия модалки)
    ensureMasterTelegramButton();

    masterLeadForm.addEventListener('submit', async function (e) {
        e.preventDefault();
        if (isSubmitting) return;
        if (!validateMasterLeadForm(e)) return;

        isSubmitting = true;

        const formData = new FormData(masterLeadForm);

        // Дублируем анкету мастера в Telegram-бота (лид админу), не влияет на email
        sendMasterLeadToBot(formData);

        try {
            const response = await fetch('https://formspree.io/f/xeajjwlo', {
                method: 'POST',
                body: formData,
                headers: { 'Accept': 'application/json' }
            });

            const data = await response.json();
            if (!response.ok) throw new Error(data.error || 'Submit failed');

            if (typeof gtag === 'function') {
                gtag('event', 'generate_lead_master', {
                    form_name: 'master_lead_form',
                    form_location: 'Регистрация мастера',
                    user_type: 'master',
                    value: 0,
                    currency: 'USD'
                });
            }

            closeMasterLeadForm();
            ensureMasterTelegramButton();
            openMasterThankYou();
            masterLeadForm.reset();

        } catch (error) {
            console.error('Master form error:', error);
            alert(t('submitError'));
            isSubmitting = false;
        }
    });

    // Checkbox
    const masterLeadConsent   = document.getElementById('masterLeadConsent');
    const masterLeadSubmitBtn = document.getElementById('masterLeadSubmitBtn');
    if (masterLeadConsent && masterLeadSubmitBtn) {
        masterLeadSubmitBtn.disabled = !masterLeadConsent.checked;
        masterLeadConsent.addEventListener('change', function () {
            masterLeadSubmitBtn.disabled = !this.checked;
        });
    }
}

function validateMasterLeadForm(e) {
    const form          = e.target;
    const phoneInput    = document.getElementById('masterLeadPhone');
    const telegramInput = form.querySelector('input[name="telegram"]');
    const whatsappInput = form.querySelector('input[name="whatsapp"]');

    const telegramValue = telegramInput ? telegramInput.value.trim() : '';
    const whatsappValue = whatsappInput ? whatsappInput.value.trim() : '';

    if (!telegramValue && !whatsappValue) {
        alert(t('contactRequired'));
        if (telegramInput && !telegramValue) telegramInput.focus();
        else if (whatsappInput) whatsappInput.focus();
        return false;
    }

    if (!validatePhone(phoneInput)) return false;
    if (telegramValue && !validateTelegram(telegramInput)) return false;

    return true;
}

// ============================================
// 12. УПРАВЛЕНИЕ МОДАЛЬНЫМИ ОКНАМИ
// ============================================

function openClientLeadForm()  { _modal('clientLeadFormModal',   'flex'); }
function closeClientLeadForm() { _modal('clientLeadFormModal',   'none'); }
function openThankYou()        { _modal('thankYouModal',          'flex'); }
function closeThankYou()       { _modal('thankYouModal',          'none'); }
function openMasterThankYou()  { _modal('masterThankYouModal',   'flex'); }
function closeMasterThankYou() { _modal('masterThankYouModal',   'none'); }
function openMasterLeadForm()  { _modal('masterLeadFormModal',   'flex'); }
function closeMasterLeadForm() { _modal('masterLeadFormModal',   'none'); }

function _modal(id, display) {
    const el = document.getElementById(id);
    if (el) el.style.display = display;
    _syncScrollLock();
}

// Запомненная позиция прокрутки на момент открытия окна.
// null — значит страница сейчас не заблокирована.
let _savedScrollY = null;

/**
 * Блокирует прокрутку страницы, пока открыто хотя бы одно модальное окно.
 *
 * Считаем именно ВСЕ окна, а не текущее: окна могут перекрываться
 * (например, из формы заявки открывается «спасибо»), и закрытие одного
 * не должно разблокировать страницу, пока второе ещё на экране.
 */
function _syncScrollLock() {
    // Открытым считаем окно с любым display, кроме 'none'
    const anyOpen = Array.from(document.querySelectorAll('.modal'))
        .some(m => m.style.display && m.style.display !== 'none');

    if (anyOpen && _savedScrollY === null) {
        // ЗАКРЫВАЕМ прокрутку: запоминаем позицию и фиксируем body.
        _savedScrollY = window.pageYOffset || document.documentElement.scrollTop || 0;

        // Компенсируем исчезающую полосу прокрутки: на десктопе она занимает
        // ~15px, и без отступа контент дёргается вправо в момент открытия.
        // На мобильных и при overlay-скроллбарах ширина равна 0 — отступ не нужен.
        const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth;
        if (scrollbarWidth > 0) {
            document.body.style.paddingRight = `${scrollbarWidth}px`;
        }

        document.body.style.top = `-${_savedScrollY}px`;
        document.body.classList.add('modal-open');
    } else if (!anyOpen && _savedScrollY !== null) {
        // ВОЗВРАЩАЕМ прокрутку: снимаем фиксацию и восстанавливаем позицию
        document.body.classList.remove('modal-open');
        document.body.style.top = '';
        document.body.style.paddingRight = '';
        window.scrollTo(0, _savedScrollY);
        _savedScrollY = null;
    }
}

// ============================================
// 13. КНОПКА «НАВЕРХ» / TELEGRAM FAB
// ============================================

function initScrollToTop() {
    const scrollButton = document.getElementById('scrollToTop');
    if (!scrollButton) return;

    window.addEventListener('scroll', () => {
        scrollButton.classList.toggle('visible', window.pageYOffset > 300);
    });
}

// Баннер #app-banner стоит внизу на всю ширину и налезает на FAB в правом углу.
// Когда баннер виден — приподнимаем FAB и меню над ним (класс .banner-shift).
// Инлайн-скрипт баннера меняет banner.style.display ('block'/'none'); следим за
// этим через MutationObserver — ловит и показ через 1.5с, и закрытие крестиком.
function initBannerShift() {
    const banner = document.getElementById('app-banner');
    const fab = document.getElementById('scrollToTop');
    if (!banner || !fab) return;

    const sync = () => {
        const shown = getComputedStyle(banner).display !== 'none';
        fab.classList.toggle('banner-shift', shown);
        // Меню создаётся initWhatsAppButtonTracking() и живёт у <body>.
        const menu = document.querySelector('.contact-fab-menu');
        if (menu) menu.classList.toggle('banner-shift', shown);
    };

    new MutationObserver(sync).observe(banner, { attributes: true, attributeFilter: ['style'] });
    sync();
}

// ============================================
// 14. ТРЕКИНГ КНОПКИ WHATSAPP
// ============================================

function initWhatsAppButtonTracking() {
    const fab = document.getElementById('scrollToTop');
    if (!fab) return;

    const isMastersPage = window.location.pathname.includes('/masters/');
    const lang = window.__FORCE_LANG__ || 'ru';

    // Предзаполненный текст для WhatsApp по языку страницы.
    const waTexts = {
        ru: encodeURIComponent(isMastersPage
            ? 'Здравствуйте! Хочу стать партнёром сервиса.'
            : 'Здравствуйте! Нужен мастер в Белграде.'),
        sr: encodeURIComponent(isMastersPage
            ? 'Zdravo! Želim da postanem partner servisa.'
            : 'Zdravo! Potreban mi je majstor u Beogradu.'),
        en: encodeURIComponent(isMastersPage
            ? 'Hello! I want to become a partner.'
            : 'Hello! I need a handyman in Belgrade.')
    };
    // TODO(Сербия): заменить номер 995557645196 на сербский +381, когда будет сим-карта.
    const waHref = 'https://wa.me/995557645196?text=' + (waTexts[lang] || waTexts.ru);

    // Telegram-бот: на странице мастеров — бот мастеров, иначе клиентский бот по языку
    // страницы (RU/SR/EN). start=site_<lang> — для атрибуции.
    const tgBots = { ru: 'mastera_rus_bot', en: 'mastera_eng_bot', sr: 'mastera_sr_bot' };
    const tgBot = isMastersPage ? 'mastera_serbia_bot' : (tgBots[lang] || tgBots.ru);
    const tgHref = 'https://t.me/' + tgBot + '?start=site_' + lang;

    // Подписи (доступность/тултипы) по языку.
    const labels = ({
        ru: { open: 'Связаться с нами', wa: 'Написать в WhatsApp', tg: 'Написать в Telegram' },
        en: { open: 'Contact us',       wa: 'Message on WhatsApp', tg: 'Message on Telegram' },
        sr: { open: 'Kontaktirajte nas', wa: 'Pišite na WhatsApp',  tg: 'Pišite na Telegram' }
    })[lang] || { open: 'Связаться с нами', wa: 'WhatsApp', tg: 'Telegram' };

    // FAB больше не прямая ссылка, а переключатель меню с нейтральной «чат»-иконкой.
    fab.removeAttribute('href');
    fab.removeAttribute('target');
    fab.classList.add('contact-fab');
    fab.setAttribute('role', 'button');
    fab.setAttribute('tabindex', '0');
    fab.setAttribute('aria-label', labels.open);
    fab.setAttribute('aria-expanded', 'false');
    // FAB морфит иконку между двумя логотипами (WhatsApp ↔ Telegram). Смена —
    // плавный «wipe»: новый слой прокрашивается по диагонали слева направо вслед
    // за бликом. Стартует с WhatsApp (передний слой — is-front).
    fab.innerHTML =
        '<span class="cf-morph">' +
            '<span class="cf-layer cf-layer--wa is-front" aria-hidden="true"><img src="/image/whatsapp-icon.png" alt=""></span>' +
            '<span class="cf-layer cf-layer--tg" aria-hidden="true"><img src="/image/telegram-icon.png" alt=""></span>' +
            '<span class="cf-shine" aria-hidden="true"></span>' +
        '</span>';

    // Две опции живут отдельным контейнером у <body> — у FAB overflow:hidden, иначе их обрежет.
    const menu = document.createElement('div');
    menu.className = 'contact-fab-menu';
    menu.innerHTML =
        '<a class="contact-opt contact-opt--tg" href="' + tgHref + '" target="_blank" rel="noopener" ' +
        'aria-label="' + labels.tg + '" title="' + labels.tg + '">' +
        '<img src="/image/telegram-icon.png" alt="Telegram" loading="lazy"></a>' +
        '<a class="contact-opt contact-opt--wa" href="' + waHref + '" target="_blank" rel="noopener" ' +
        'aria-label="' + labels.wa + '" title="' + labels.wa + '">' +
        '<img src="/image/whatsapp-icon.png" alt="WhatsApp" loading="lazy"></a>';
    document.body.appendChild(menu);

    // Ротация слоёв FAB: блик и смена иконки играют всегда, независимо от
    // системной настройки prefers-reduced-motion.
    const cfLayers = Array.from(fab.querySelectorAll('.cf-layer'));
    const cfShine = fab.querySelector('.cf-shine');
    let cfIndex = 0;
    let cfTimer = null;
    // Перезапуск CSS-анимации: снять класс, форсировать reflow, навесить снова.
    const cfRestart = (el, cls) => { el.classList.remove(cls); void el.offsetWidth; el.classList.add(cls); };
    const cfMorph = () => {
        const next = (cfIndex + 1) % cfLayers.length;
        cfLayers[cfIndex].classList.remove('is-front');
        cfLayers[next].classList.add('is-front');
        // Блик и прокраска — на одном таймере, поэтому всегда совпадают.
        // Играем всегда, независимо от prefers-reduced-motion.
        cfRestart(cfShine, 'go');
        cfRestart(cfLayers[next], 'cf-wipe');
        cfIndex = next;
    };
    const cfStart = () => { if (!cfTimer && cfLayers.length > 1) cfTimer = setInterval(cfMorph, 3200); };
    const cfStop = () => { if (cfTimer) { clearInterval(cfTimer); cfTimer = null; } };
    cfStart();

    let isOpen = false;
    const setOpen = (v) => {
        isOpen = v;
        fab.classList.toggle('open', v);
        menu.classList.toggle('open', v);
        fab.setAttribute('aria-expanded', String(v));
        // Пока меню открыто — иконка стабильна; закрыли — снова играет.
        if (v) cfStop(); else cfStart();
    };

    // Открытие/закрытие меню по клику на FAB (+ событие аналитики при открытии).
    fab.addEventListener('click', function (e) {
        e.preventDefault();
        setOpen(!isOpen);
        if (isOpen && typeof gtag === 'function') {
            gtag('event', 'contact_open', { event_category: 'engagement', event_label: 'contact_fab' });
        }
    });
    // Клавиатурная доступность: Enter/Space открывает, Esc закрывает.
    fab.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); fab.click(); }
    });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') setOpen(false); });
    // Закрытие по клику вне меню и при прокрутке к верху (FAB скрывается).
    document.addEventListener('click', function (e) {
        if (isOpen && !menu.contains(e.target) && !fab.contains(e.target)) setOpen(false);
    });
    window.addEventListener('scroll', function () { if (window.pageYOffset <= 300) setOpen(false); });

    // Клик по опции: при наличии gtag шлём событие и открываем канал с небольшой задержкой.
    const bindOption = (selector, method, href) => {
        const el = menu.querySelector(selector);
        if (!el) return;
        el.addEventListener('click', function (e) {
            setOpen(false);
            if (typeof gtag !== 'function') return; // нет аналитики — обычный переход по ссылке
            e.preventDefault();
            gtag('event', method + '_click', {
                event_category: 'engagement',
                event_label: method + '_fab',
                method: method
            });
            setTimeout(function () { window.open(href, '_blank', 'noopener'); }, 300);
        });
    };
    bindOption('.contact-opt--wa', 'whatsapp', waHref);
    bindOption('.contact-opt--tg', 'telegram', tgHref);
}

// ============================================
// 15. ЭФФЕКТ ПЕЧАТНОЙ МАШИНКИ ДЛЯ H1
// ============================================

function initTypingEffect() {
    const titleElement = document.querySelector('.hero-title');
    if (!titleElement) return;

    const path = window.location.pathname;
    const isMastersPage = path.includes('/masters/');

    // Город определяем по URL: /novi-sad/ → Нови-Сад, иначе Белград (город по умолчанию).
    // На masters-хабах город не показываем — там общесербский партнёрский текст (Сербия).
    const cityKey = path.includes('novi-sad') ? 'noviSad' : 'beograd';
    // ВНИМАНИЕ: в «Нови‑Сад» дефис — НЕРАЗРЫВНЫЙ (U+2011, а не обычный минус),
    // чтобы заголовок hero-title не разрывался по дефису на новую строку
    // («Нови-» / «Сад»). Касается только визуального заголовка; город для бота
    // берётся отдельно из botCityFromUrl() с обычным дефисом.
    const cityName = {
        ru: { beograd: 'Белград', noviSad: 'Нови‑Сад' },
        en: { beograd: 'Belgrade', noviSad: 'Novi Sad' },
        sr: { beograd: 'Beograd', noviSad: 'Novi Sad' }
    };
    const city = (cityName[currentLang] || cityName.ru)[cityKey];

    const textParts = {
        ru: {
            start:   'Сервис ',
            option1: 'поиска мастеров ' + city,
            option2: 'подбора мастеров ' + city
        },
        en: {
            start:   'Master ',
            option1: 'search service ' + city,
            option2: 'matching service ' + city
        },
        sr: {
            start:   'Servis ',
            option1: 'pretrage majstora ' + city,
            option2: 'izbora majstora ' + city
        },
        ru_masters: {
            start:   'Сервис ',
            option1: 'поиска заказов Сербия',
            option2: 'подбора заказов Сербия'
        },
        en_masters: {
            start:   'Order ',
            option1: 'search service Serbia',
            option2: 'matching service Serbia'
        },
        sr_masters: {
            start:   'Servis ',
            option1: 'pretrage porudžbina Srbija',
            option2: 'izbora porudžbina Srbija'
        }
    };

    const langKey = isMastersPage ? currentLang + '_masters' : currentLang;
    const parts = textParts[langKey] || textParts[currentLang] || textParts.ru;

    const typeSpeed  = 180;
    const deleteSpeed = 50;
    const pauseTime  = 1000;

    const cursor = document.createElement('span');
    cursor.className = 'typing-cursor';
    titleElement.innerHTML = '';
    titleElement.appendChild(cursor);

    const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));

    async function typeText(text) {
        for (let i = 0; i < text.length; i++) {
            // Курсор мог быть удалён (повторный запуск/уход со страницы) — тогда
            // вставка перед ним упала бы с insertBefore-ошибкой. Проверяем родство.
            if (cursor.parentNode !== titleElement) return;
            titleElement.insertBefore(document.createTextNode(text[i]), cursor);
            await wait(typeSpeed);
        }
    }

    async function deleteText(count) {
        for (let i = 0; i < count; i++) {
            if (cursor.parentNode !== titleElement) return;
            if (titleElement.childNodes.length > 1) {
                titleElement.removeChild(titleElement.childNodes[titleElement.childNodes.length - 2]);
            }
            await wait(deleteSpeed);
        }
    }

    async function runAnimation() {
        await typeText(parts.start + parts.option1);
        await wait(pauseTime);
        await deleteText(parts.option1.length);
        await typeText(parts.option2);
        await wait(1000);
        cursor.remove();
    }

    setTimeout(runAnimation, 500);
}

// ============================================
// ЭФФЕКТ ПЕЧАТНОЙ МАШИНКИ ДЛЯ H1 НА СТРАНИЦАХ СЕРВИСА
// ============================================

function initServiceTypingEffect() {
    const titleElement = document.querySelector('.service-title');
    if (!titleElement) return;

    const html = titleElement.innerHTML;
    const parts = html.split(/<br\s*\/?>/i);
    const line1 = parts[0] ? parts[0].trim() : '';
    const line2 = parts[1] ? parts[1].trim() : '';

    const typeSpeed = 180;

    const cursor = document.createElement('span');
    cursor.className = 'typing-cursor';
    titleElement.innerHTML = '';
    titleElement.appendChild(cursor);

    const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));

    async function typeText(text) {
        for (let i = 0; i < text.length; i++) {
            // Курсор мог быть удалён — тогда insertBefore упал бы с ошибкой.
            if (cursor.parentNode !== titleElement) return;
            titleElement.insertBefore(document.createTextNode(text[i]), cursor);
            await wait(typeSpeed);
        }
    }

    async function runAnimation() {
        await typeText(line1);
        if (line2 && cursor.parentNode === titleElement) {
            const br = document.createElement('br');
            titleElement.insertBefore(br, cursor);
            await typeText(line2);
        }
        await wait(400);
        cursor.remove();
    }

    setTimeout(runAnimation, 500);
}