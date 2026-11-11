// Quaderno Pedalate: funziona anche offline. Versione 202611112201
const CACHE = 'qp-202611112201';
const SHELL = ['./', './index.html', './manifest.webmanifest', './icon-192.png', './icon-512.png',
  'https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.js',
  'https://cdn.jsdelivr.net/npm/jszip@3.10.1/dist/jszip.min.js'];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  const req = e.request, url = new URL(req.url);
  // file condivisi da un'altra app (BiNavi, Garmin, Wahoo...): li parcheggio e apro la pagina Importa
  if (req.method === 'POST' && url.origin === location.origin && url.searchParams.has('share')) {
    e.respondWith((async () => {
      try {
        const fd = await req.formData(), c = await caches.open('qp-share'); let i = 0;
        for (const f of fd.getAll('files')) { if (f && f.size) await c.put('./__share/' + Date.now() + '-' + (i++) + '?name=' + encodeURIComponent(f.name || 'attivita'), new Response(f)); }
      } catch (err) {}
      return Response.redirect('./#importa-condivisi', 303);
    })());
    return;
  }
  if (req.method !== 'GET' || url.hostname.endsWith('strava.com')) return;
  if (req.mode === 'navigate') {
    // Pagina: prima la rete (aggiornamenti), se offline la copia salvata
    e.respondWith(fetch(req).then(r => { const c = r.clone(); caches.open(CACHE).then(x => x.put('./index.html', c)); return r; })
      .catch(() => caches.match('./index.html')));
    return;
  }
  e.respondWith(caches.match(req).then(hit => hit || fetch(req).then(r => {
    if (r.ok && (url.origin === location.origin || /jsdelivr|gstatic|googleapis/.test(url.hostname))) { const c = r.clone(); caches.open(CACHE).then(x => x.put(req, c)); }
    return r;
  })));
});
