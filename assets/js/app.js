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

  // App tab bar: highlight the current tab; "More" opens the menu.
  var bar = document.querySelector(".app-tabbar");
  if (bar) {
    var norm = function (p) { return p.replace(/index\.html$/, ""); };
    var here = norm(location.pathname);
    bar.querySelectorAll("a[data-tab]").forEach(function (a) {
      var target = norm(a.pathname);
      var match = a.getAttribute("data-tab") === "home" ? here === target : here.indexOf(target) === 0;
      if (a.host === location.host && match) a.setAttribute("aria-current", "page");
    });
    var more = bar.querySelector(".app-more");
    if (more) more.addEventListener("click", function () {
      var t = document.querySelector(".menu-toggle");
      if (t) { t.click(); window.scrollTo(0, 0); }
    });
  }

  // "Get the App" page: install button (Android/Chrome) and the right steps per phone.
  var ua = navigator.userAgent;
  var isIOS = /iPhone|iPad|iPod/.test(ua) || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
  document.querySelectorAll("[data-show]").forEach(function (el) {
    var w = el.getAttribute("data-show");
    el.hidden = !((w === "installed" && standalone) || (w === "ios" && isIOS && !standalone) || (w === "android" && !isIOS && !standalone));
  });
  var deferred = null;
  window.addEventListener("beforeinstallprompt", function (e) {
    e.preventDefault();
    deferred = e;
    document.querySelectorAll("[data-install]").forEach(function (b) { b.hidden = false; });
  });
  document.querySelectorAll("[data-install]").forEach(function (b) {
    b.addEventListener("click", function () {
      if (!deferred) return;
      deferred.prompt();
      deferred.userChoice.finally(function () { deferred = null; b.hidden = true; });
    });
  });
  window.addEventListener("appinstalled", function () {
    document.querySelectorAll("[data-install]").forEach(function (b) { b.hidden = true; });
  });
})();
