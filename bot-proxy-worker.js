// ============================================================================
// Cloudflare Worker — прокси заявок с сайта в Telegram-бота «Мастера Сербии».
//
// Зачем: сайт статический (GitHub Pages), и если слать заявку прямо из браузера,
// то WEBHOOK_SECRET был бы виден всем. Этот воркер хранит секрет у себя и
// добавляет его к запросу на стороне сервера. Заодно решает CORS.
//
// Секрет НЕ пишется в код: он берётся из переменной окружения воркера
// (Cloudflare → Worker → Settings → Variables and Secrets → WEBHOOK_SECRET).
// Значение должно совпадать с WEBHOOK_SECRET в .env бота.
// ============================================================================

// TODO: заменить на реальные адреса сербского бота и домена сайта.
const BOT_WEBHOOK_URL = 'https://TODO-mastera-serbia.up.railway.app/webhook/new-request'; // адрес бота
const ALLOWED_ORIGIN  = 'https://TODO-mastera-serbia.example';        // домен сайта

export default {
  async fetch(request, env) {
    const cors = {
      'Access-Control-Allow-Origin': ALLOWED_ORIGIN,
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    };

    // Префлайт-запрос браузера
    if (request.method === 'OPTIONS') return new Response(null, { headers: cors });
    if (request.method !== 'POST')    return new Response('Method Not Allowed', { status: 405, headers: cors });

    const body = await request.text();

    let resp;
    try {
      resp = await fetch(BOT_WEBHOOK_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Webhook-Token': env.WEBHOOK_SECRET // секрет из окружения воркера
        },
        body
      });
    } catch (e) {
      return new Response(JSON.stringify({ ok: false, error: 'bot unreachable' }),
        { status: 502, headers: { ...cors, 'Content-Type': 'application/json' } });
    }

    const text = await resp.text();
    return new Response(text, {
      status: resp.status,
      headers: { ...cors, 'Content-Type': 'application/json' }
    });
  }
};
