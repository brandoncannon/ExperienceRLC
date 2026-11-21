// App home: fills in today's chapter and SOAP title from the Daily Reading data.
(function () {
  var ROOT = ((document.currentScript && document.currentScript.src) || "").replace(/assets\/js\/app-home\.js.*$/, "");
  var DATA = ROOT + "daily/data/";
  var pad = function (n) { return String(n).padStart(2, "0"); };
  var d = new Date();
  var key = d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate());
  var ch = document.getElementById("ah-chapter"), soap = document.getElementById("ah-soap");
  if (!ch) return;
  fetch(DATA + "reading-plan.json", { cache: "no-cache" }).then(function (r) { return r.json(); }).then(function (plan) {
    var day = plan[key];
    if (!day) return;
    if (day.title === "Catch-Up Day") { ch.textContent = "Catch-Up Day"; soap.textContent = "No new chapter today. Catch up on any readings you missed."; return; }
    var passages = Array.isArray(day) ? day : day.passages || [];
    if (passages.length) ch.textContent = passages.join(" · ");
    return fetch(DATA + "soaps/" + key.slice(0, 7) + ".json", { cache: "no-cache" })
      .then(function (r) { return r.ok ? r.json() : {}; })
      .then(function (m) { if (m[key] && m[key].title) soap.textContent = "Today's SOAP: " + m[key].title; });
  }).catch(function () {});
})();
