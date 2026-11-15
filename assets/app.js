(function () {
  const cfg = window.SITE_CONFIG || {};
  const $ = (id) => document.getElementById(id);

  // ---- Date helpers (always the reader's local date) ----
  const pad = (n) => String(n).padStart(2, "0");
  const toKey = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
  const fromKey = (k) => { const [y, m, d] = k.split("-").map(Number); return new Date(y, m - 1, d); };
  const addDays = (k, n) => { const d = fromKey(k); d.setDate(d.getDate() + n); return toKey(d); };
  const pretty = (k) => fromKey(k).toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric", year: "numeric" });

  const todayKey = toKey(new Date());
  const param = new URLSearchParams(location.search).get("date");
  const key = /^\d{4}-\d{2}-\d{2}$/.test(param || "") ? param : todayKey;
  const isFuture = key > todayKey;

  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const paras = (s) => esc(s).split(/\n\s*\n/).map((p) => `<p>${p.replace(/\n/g, "<br>")}</p>`).join("");
  const bibleUrl = (ref) =>
    `https://www.biblegateway.com/passage/?search=${encodeURIComponent(ref)}&version=${encodeURIComponent(cfg.bibleVersion || "NLT")}`;

  // ---- Header / navigation ----
  $("date").textContent = pretty(key);
  document.title = `Bible Breakdown · ${pretty(key)}`;
  $("prev").href = `?date=${addDays(key, -1)}`;
  const nextKey = addDays(key, 1);
  if (nextKey > todayKey) $("next").classList.add("disabled");
  else $("next").href = nextKey === todayKey ? "./" : `?date=${nextKey}`;
  if (key !== todayKey) { $("today-link").hidden = false; $("reading-label").textContent = "Bible Breakdown · Reading"; }

  // ---- Reading plan ----
  fetch("data/reading-plan.json", { cache: "no-cache" })
    .then((r) => r.json())
    .then((plan) => {
      const day = plan[key];
      if (day && day.title === "Catch-Up Day") {
        $("reading-title").textContent = "Catch-Up Day";
        $("reading-links").innerHTML = '<p class="note">No new chapter today. Use today to catch up on any readings you missed.</p>';
        return;
      }
      if (!day) {
        $("reading-title").textContent = "No reading scheduled for this day.";
        return;
      }
      const passages = Array.isArray(day) ? day : day.passages || [];
      $("reading-title").textContent = (day.title) || passages.join(" · ");
      const otherLinks = passages
        .map((p) => `<a href="${bibleUrl(p)}" target="_blank" rel="noopener">${esc(p)} in the ${esc(cfg.bibleVersion || "NET")} &#8599;</a>`)
        .join(" · ");
      $("reading-links").innerHTML = `<p class="note">Read in another translation: ${otherLinks}</p>`;
      // Embedded chapter text (World English Bible, public domain), stored by month.
      fetch(`data/bible/${key.slice(0, 7)}.json`, { cache: "no-cache" })
        .then((r) => (r.ok ? r.json() : {}))
        .then((month) => {
          if (!month[key]) return;
          $("scripture-text").innerHTML = month[key] + '<p class="translation">World English Bible (public domain)</p>';
          $("scripture-text").hidden = false;
        })
        .catch(() => {});
    })
    .catch(() => { $("reading-title").textContent = "Reading plan unavailable."; });

  // ---- Daily SOAP ----
  const showEmpty = (msg) => {
    $("soap-title").textContent = msg;
    $("byline").textContent = "";
    $("soap-body").innerHTML = "";
  };

  if (isFuture) return showEmpty("Check back that morning.");

  fetch(`data/soaps/${key.slice(0, 7)}.json`, { cache: "no-cache" })
    .then((r) => { if (!r.ok) throw new Error("missing"); return r.json(); })
    .then((month) => {
      const s = month[key];
      if (!s) throw new Error("missing");
      $("soap-title").textContent = s.title || "Today's SOAP";
      $("byline").textContent = `by ${s.author || cfg.author || ""}`;
      const sections = [
        ["S", "Scripture", s.scripture],
        ["O", "Observation", s.observation],
        ["A", "Application", s.application],
        ["P", "Prayer", s.prayer],
      ];
      let html = "";
      if (s.verse) {
        html += `<section class="soap-part"><h3><span class="letter">S</span>Scripture</h3><blockquote class="key-verse">${paras(s.verse)}${s.verseRef ? `<cite><a href="${bibleUrl(s.verseRef)}" target="_blank" rel="noopener">${esc(s.verseRef)}${s.version ? " (" + esc(s.version) + ")" : ""}</a></cite>` : ""}</blockquote></section>`;
      }
      html += sections
        .filter(([, , text]) => text)
        .map(([letter, label, text]) => `<section class="soap-part"><h3><span class="letter">${letter}</span>${label}</h3>${paras(text)}</section>`)
        .join("");
      if (s.source) html += `<p class="source"><a href="${esc(s.source)}" target="_blank" rel="noopener">Read more on Cannon Study Bible &rarr;</a></p>`;
      $("soap-body").innerHTML = html;
    })
    .catch(() => {
      const dom = fromKey(key).getDate();
      showEmpty(dom === 15 || dom === 30 ? "Catch-up day — no new SOAP today." : "This day's SOAP is coming soon.");
    });
})();
