import re, time
src=open('src/app.html').read()
ver=time.strftime('%Y%m%d%H%M')
head='''<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#f2f3ef">
<meta name="description" content="Statistiche, forma fisica e consigli per le tue uscite in bici.">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icon-192.png?v=ldm" type="image/png">
<link rel="apple-touch-icon" href="apple-touch-icon.png?v=ldm">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Pedalate">
<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui,sans-serif}img{max-width:100%}</style>
'''
src=src.replace('<meta name="claude:viewport-fit-sides" content="cover">\n','')
out=head+src.replace('<header class="top">','</head>\n<body>\n<header class="top">',1)
out=out.replace('</script>\n','</script>\n',)
out=out.rstrip()+'''
<script>
window.APP_VERSION='%s';
if('serviceWorker' in navigator && location.protocol==='https:'){
  const had=!!navigator.serviceWorker.controller;
  navigator.serviceWorker.register('sw.js?v='+APP_VERSION).then(reg=>{
    document.addEventListener('visibilitychange',()=>{ if(document.visibilityState==='visible') reg.update().catch(()=>{}); });
  }).catch(()=>{});
  let reloaded=false;
  navigator.serviceWorker.addEventListener('controllerchange',()=>{
    if(!had||reloaded) return; reloaded=true;
    const t=document.createElement('div');
    t.setAttribute('role','status');
    t.style.cssText='position:fixed;left:16px;right:16px;bottom:calc(16px + env(safe-area-inset-bottom,0px));z-index:20;background:var(--accent);color:var(--on-accent);padding:12px 14px;border-radius:10px;font-weight:600;display:flex;gap:12px;align-items:center;justify-content:space-between;box-shadow:0 4px 18px rgba(0,0,0,.3)';
    t.innerHTML='<span>Nuova versione disponibile</span><button style="background:var(--surface);color:var(--fg);border:none">Aggiorna</button>';
    t.querySelector('button').onclick=()=>location.reload();
    document.body.append(t);
  });
}
</script>
</body>
</html>
''' % ver
open('index.html','w').write(out)
open('manifest.webmanifest','w').write('''{
  "name": "Quaderno Pedalate",
  "short_name": "Pedalate",
  "description": "Statistiche, forma fisica e consigli per le tue uscite in bici.",
  "lang": "it",
  "start_url": "./",
  "scope": "./",
  "display": "standalone",
  "orientation": "portrait",
  "background_color": "#f2f3ef",
  "theme_color": "#f2f3ef",
  "icons": [
    {"src": "icon-192.png?v=ldm", "sizes": "192x192", "type": "image/png"},
    {"src": "icon-512.png?v=ldm", "sizes": "512x512", "type": "image/png"},
    {"src": "icon-maskable-512.png?v=ldm", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}
  ]
}
''')
open('sw.js','w').write('''// Quaderno Pedalate: funziona anche offline. Versione %s
const CACHE = 'qp-%s';
const SHELL = ['./', './index.html', './manifest.webmanifest', './icon-192.png', './icon-512.png',
  'https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.js',
  'https://cdn.jsdelivr.net/npm/jszip@3.10.1/dist/jszip.min.js'];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  const req = e.request, url = new URL(req.url);
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
''' % (ver, ver))
