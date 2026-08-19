// Service Worker kept only to remove caches created by older PWA versions.
// Do not preserve named caches here: an old cached index can keep the entire
// application pinned to an obsolete JavaScript bundle after a deploy.

// Install event
self.addEventListener("install", (event) => {
  event.waitUntil(caches.keys().then((names) => Promise.all(names.map((name) => caches.delete(name)))));
  self.skipWaiting();
});

// Activate event
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((names) => Promise.all(names.map((name) => caches.delete(name)))),
  );
  self.clients.claim();
});

// Fetch event
self.addEventListener("fetch", (event) => {
  event.respondWith(fetch(event.request));
});
