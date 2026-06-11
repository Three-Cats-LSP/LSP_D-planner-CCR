// LSP D-Planner — Service Worker
// Cache-first strategy for offline use.
// Bump CACHE_VERSION when deploying a new app version to force cache refresh.

const CACHE_VERSION = 'lsp-dplanner-v2.9.1b';
const ASSETS = [
  '/LSP_D-planner/',
  '/LSP_D-planner/index.html'
];

// Install — pre-cache core assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_VERSION)
      .then(cache => cache.addAll(ASSETS))
      .then(() => self.skipWaiting())
  );
});

// Activate — delete old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys
          .filter(key => key !== CACHE_VERSION)
          .map(key => caches.delete(key))
      ))
      .then(() => self.clients.claim())
  );
});

// Fetch — cache-first, fall back to network, then cached index
self.addEventListener('fetch', event => {
  // Only handle GET requests for our own origin
  if (event.request.method !== 'GET') return;
  const url = new URL(event.request.url);
  if (url.origin !== self.location.origin) return;

  event.respondWith(
    caches.match(event.request)
      .then(cached => {
        if (cached) return cached;
        return fetch(event.request)
          .then(response => {
            // Cache successful responses for our scope
            if (response.ok && url.pathname.startsWith('/LSP_D-planner/')) {
              const clone = response.clone();
              caches.open(CACHE_VERSION).then(cache => cache.put(event.request, clone));
            }
            return response;
          })
          .catch(() => caches.match('/LSP_D-planner/index.html'));
      })
  );
});
