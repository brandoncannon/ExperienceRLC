// Visitor counts with GoatCounter (no cookies). Only counts on the real
// site, so test links and local previews don't inflate the numbers.
// Dashboard: https://experiencerlc.goatcounter.com
(function () {
  if (!/(^|\.)experiencerlc\.com$/.test(location.hostname)) return;
  var s = document.createElement("script");
  s.async = true;
  s.src = "https://gc.zgo.at/count.js";
  s.setAttribute("data-goatcounter", "https://experiencerlc.goatcounter.com/count");
  document.head.appendChild(s);
})();
