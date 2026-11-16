// Lists every past SOAP from the last 12 months, newest first.
(function () {
  const ROOT = ((document.currentScript && document.currentScript.src) || "").replace(/assets\/js\/daily-archive\.js.*$/, "");
  const DATA = ROOT + "daily/data/";
  const pad = (n) => String(n).padStart(2, "0");
  const d = new Date();
  const today = `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const months = [];
  for (let i = 0; i < 12; i++) { const m = new Date(d.getFullYear(), d.getMonth() - i, 1); months.push(`${m.getFullYear()}-${pad(m.getMonth() + 1)}`); }
  const list = document.getElementById("archive-list");
  Promise.all([
    fetch(DATA + "reading-plan.json", { cache: "no-cache" }).then((r) => r.json()),
    ...months.map((m) => fetch(`${DATA}soaps/${m}.json`, { cache: "no-cache" }).then((r) => (r.ok ? r.json() : {})).catch(() => ({}))),
  ])
    .then(([plan, ...ms]) => ms.flatMap((mo) => Object.entries(mo))
      .filter(([date]) => date <= today)
      .sort((a, b) => b[0].localeCompare(a[0]))
      .map(([date, s]) => ({ date, title: s.title || "Daily SOAP", reading: ((plan[date] || {}).passages || []).join(" · ") })))
    .then((items) => {
      list.innerHTML = items.length
        ? items.map((i) => {
            const [y, m, dd] = i.date.split("-").map(Number);
            const when = new Date(y, m - 1, dd).toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric", year: "numeric" });
            return `<li><a href="../index.html?date=${i.date}">${esc(i.title)}</a><small>${when}${i.reading ? " · " + esc(i.reading) : ""}</small></li>`;
          }).join("")
        : "<li>No entries yet.</li>";
    })
    .catch(() => { list.innerHTML = "<li>Archive unavailable.</li>"; });
})();
