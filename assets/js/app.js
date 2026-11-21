// Makes the website work as an installable app ("Add to Home Screen").
(function () {
  var root = document.documentElement;
  var standalone = window.matchMedia("(display-mode: standalone)").matches || window.navigator.standalone === true;
  if (standalone) root.classList.add("standalone");

  // Offline support, only on the real site (not test links).
  if ("serviceWorker" in navigator && /(^|\.)experiencerlc\.com$|^localhost$/.test(location.hostname)) {
    window.addEventListener("load", function () {
      navigator.serviceWorker.register("/sw.js").catch(function () {});
    });
  }

  // "Get the App" page: install button (Android/Chrome) and the right steps per phone.
  var ua = navigator.userAgent;
  var isIOS = /iPhone|iPad|iPod/.test(ua) || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
  document.querySelectorAll("[data-show]").forEach(function (el) {
    var w = el.getAttribute("data-show");
    el.hidden = !((w === "installed" && standalone) || (w === "ios" && isIOS && !standalone) || (w === "android" && !isIOS && !standalone));
  });
  // The button always shows. Where the browser can install directly (Chrome on
  // Android and computers) it opens the install prompt; everywhere else (iPhone,
  // Samsung Internet, in-app browsers) it jumps to the steps for that phone.
  var deferred = null;
  window.addEventListener("beforeinstallprompt", function (e) {
    e.preventDefault();
    deferred = e;
  });
  function showSteps() {
    var card = document.querySelector('[data-show]:not([hidden])');
    if (!card) return;
    card.scrollIntoView({ behavior: "smooth", block: "center" });
    card.classList.remove("flash");
    void card.offsetWidth;
    card.classList.add("flash");
  }
  document.querySelectorAll("[data-install]").forEach(function (b) {
    if (standalone) return;  // already using the app
    b.hidden = false;
    b.addEventListener("click", function () {
      if (!deferred) { showSteps(); return; }
      var d = deferred;
      deferred = null;
      try {
        d.prompt();
        d.userChoice.then(function (c) { if (c && c.outcome !== "accepted") showSteps(); }, showSteps);
      } catch (err) { showSteps(); }
    });
  });
  window.addEventListener("appinstalled", function () {
    document.querySelectorAll("[data-install]").forEach(function (b) { b.hidden = true; });
  });
})();
