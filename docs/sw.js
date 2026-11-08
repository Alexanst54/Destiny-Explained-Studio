const CACHE='destiny-studio-a1f0a7cb3a616d1a';
const FILES=['./','./index.html','./assets/editor.js','./assets/editor.css','./engine-contract.json','./GUIDE.html'];
self.addEventListener('install',event=>event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(FILES)).then(()=>self.skipWaiting())));
self.addEventListener('activate',event=>event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith('destiny-studio-')&&k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',event=>{
 if(event.request.method!=='GET'||new URL(event.request.url).origin!==self.location.origin)return;
 event.respondWith(caches.match(event.request).then(cached=>cached||fetch(event.request)));
});
