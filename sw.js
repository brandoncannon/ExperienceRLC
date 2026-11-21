// Real Life Church app: keeps recently viewed pages available offline.
// Always tries the network first, so people see the newest content;
// falls back to the saved copy only when there's no connection.
const CACHE = "rlc-v2";
const OFFLINE = "/offline/";
const PRECACHE = [OFFLINE, "/", "/daily/", "/worship-guide/", "/assets/css/style.css", "/assets/js/main.js", "/assets/img/logo.png"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(PRECACHE)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET" || new URL(req.url).origin !== self.location.origin) return;
  // Pages always come fresh from the server (no short-term browser cache), so new
  // message notes and edits show up right away in the app and on phones.
  const live = req.mode === "navigate" ? fetch(req.url, { cache: "no-cache", credentials: "same-origin" }) : fetch(req);
  e.respondWith(
    live
      .then((res) => {
        if (res.ok && res.type === "basic") {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(req, copy));
        }
        return res;
      })
      .catch(() =>
        caches.match(req, { ignoreSearch: req.mode === "navigate" }).then(
          (hit) => hit || (req.mode === "navigate" ? caches.match(OFFLINE) : Response.error())
        )
      )
  );
});
