// Service Worker для лендинга Мастера в Белграде
// Базовое кэширование: оболочка страниц, манифест, стили, шрифты

const CACHE_NAME = 'mastera-landing-v12';

const PRECACHE_URLS = [
  '/',
  '/ru/',
  '/sr/',
  '/en/',
  '/site.webmanifest',
  '/style.css',
  '/service.css',
  '/script.js',
  '/image/favicon.svg',
  '/image/favicon.ico',
  '/image/web-app-manifest-192x192.png',
  '/image/web-app-manifest-512x512.png',
];

// ── Установка: прекэш ключевых ресурсов ──────────────────────────────────────
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(PRECACHE_URLS))
  );
  self.skipWaiting();
});

// ── Активация: удаляем старые кэши ───────────────────────────────────────────
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((k) => k !== CACHE_NAME)
          .map((k) => caches.delete(k))
      )
    )
  );
  self.clients.claim();
});

// ── Fetch: стратегия Network First для HTML, Cache First для статики ─────────
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Только собственные запросы
  if (url.origin !== self.location.origin) return;

  // HTML-страницы, script.js и CSS — Network First (свежая логика/контент важнее).
  // Иначе Cache First «замораживает» старый script.js (с прежними текстами typing-эффекта)
  // до следующей смены CACHE_NAME — именно это показывало на h1 старый язык/город.
  const isHtml = request.headers.get('accept') && request.headers.get('accept').includes('text/html');
  const isCriticalAsset = /\.(?:js|css)(?:\?.*)?$/.test(url.pathname);
  if (isHtml || isCriticalAsset) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
          return response;
        })
        .catch(() => caches.match(request).then((r) => r || (isHtml ? caches.match('/') : undefined)))
    );
    return;
  }

  // Остальная статика (изображения, шрифты, манифест) — Cache First
  event.respondWith(
    caches.match(request).then((cached) => {
      if (cached) return cached;
      return fetch(request).then((response) => {
        if (response.ok) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
        }
        return response;
      });
    })
  );
});
