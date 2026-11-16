(function () {
  const cfg = window.SITE_CONFIG || {};
  // Data lives in /daily/data/; find it relative to this script so it works at any address.
  const ROOT = ((document.currentScript && document.currentScript.src) || "").replace(/assets\/js\/daily\.js.*$/, "");
  const DATA = ROOT + "daily/data/";
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
  else $("next").href = nextKey === todayKey ? location.pathname : `?date=${nextKey}`;
  if (key !== todayKey) { $("today-link").hidden = false; $("reading-label").textContent = "Bible Breakdown · Reading"; }

  // ---- NLT text (Tyndale's NLT API: https://api.nlt.to) ----
  const NLT_NOTICE =
    "Scripture quotations are taken from the <i>Holy Bible</i>, New Living Translation, copyright &copy;1996, 2004, 2015 by Tyndale House Foundation. " +
    "Used by permission of Tyndale House Publishers, Carol Stream, Illinois 60188. All rights reserved.";
  const ALLOWED = new Set(["P", "SPAN", "EM", "I", "B", "STRONG", "H3", "H4", "BR", "SUP", "A", "SECTION", "VERSE_EXPORT"]);
  const clean = (node) => {
    [...node.children].forEach((el) => {
      clean(el);
      if (!ALLOWED.has(el.tagName)) { el.replaceWith(...el.childNodes); return; }
      [...el.attributes].forEach((a) => { if (a.name !== "class") el.removeAttribute(a.name); });
    });
    return node;
  };
  const fetchNlt = (ref) =>
    fetch(`https://api.nlt.to/api/passages?ref=${encodeURIComponent(ref)}&version=NLT&key=${encodeURIComponent(cfg.nltApiKey || "TEST")}`)
      .then((r) => { if (!r.ok) throw new Error("nlt"); return r.text(); })
      .then((t) => {
        const doc = new DOMParser().parseFromString(t, "text/html");
        const box = doc.querySelector("#bibletext");
        if (!box || !box.querySelector(".vn")) throw new Error("nlt");
        box.querySelectorAll("h2, script, style, link").forEach((el) => el.remove());
        return clean(box).innerHTML;
      });

  // Tap a footnote marker (*) to show or hide the note.
  document.addEventListener("click", (e) => {
    const a = e.target.closest(".a-tn");
    if (a && a.nextElementSibling) a.nextElementSibling.classList.toggle("open");
  });

  // ---- Reading plan ----
  fetch(DATA + "reading-plan.json", { cache: "no-cache" })
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
      // Chapter text on the page: NLT from Tyndale's API, falling back to the stored WEB text.
      const showText = (htmlText, credit, cls) => {
        $("scripture-text").innerHTML = htmlText + `<p class="translation">${credit}</p>`;
        $("scripture-text").className = "scripture-text " + cls;
        $("scripture-text").hidden = false;
      };
      const showWeb = () =>
        fetch(`${DATA}bible/${key.slice(0, 7)}.json`, { cache: "no-cache" })
          .then((r) => (r.ok ? r.json() : {}))
          .then((month) => { if (month[key]) showText(month[key], "World English Bible (public domain)", "web"); })
          .catch(() => {});
      if (!passages.length) return;
      Promise.all(passages.map(fetchNlt))
        .then((parts) => showText(parts.join(""), NLT_NOTICE, "nlt"))
        .catch(showWeb);
    })
    .catch(() => { $("reading-title").textContent = "Reading plan unavailable."; });

  // ---- Daily SOAP ----
  const showEmpty = (msg) => {
    $("soap-title").textContent = msg;
    $("byline").textContent = "";
    $("soap-body").innerHTML = "";
  };

  if (isFuture) return showEmpty("Check back that morning.");

  fetch(`${DATA}soaps/${key.slice(0, 7)}.json`, { cache: "no-cache" })
    .then((r) => { if (!r.ok) throw new Error("missing"); return r.json(); })
    .then((month) => {
      const s = month[key];
      if (!s) throw new Error("missing");
      if (s.verseRef) s.verseRef = s.verseRef.replace(/(\s|:)0+(\d)/g, "$1$2"); // "Psalm 122:01" -> "Psalm 122:1"
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

      // Show the SOAP's key verse in the NLT (keeps the original quote if the NLT can't load).
      const quote = $("soap-body").querySelector(".key-verse");
      if (quote && s.verseRef) {
        fetchNlt(s.verseRef)
          .then((h) => {
            const box = document.createElement("div");
            box.innerHTML = h;
            box.querySelectorAll("h3, h4, .subhead, .psa-title, .sos-speaker, .tn, .a-tn").forEach((el) => el.remove());
            const verses = box.querySelectorAll(".vn");
            if (verses.length === 1) verses[0].remove();
            const text = box.textContent.replace(/\s+/g, " ").trim();
            if (!text) return;
            quote.innerHTML = `<p>${esc(text)}</p><cite><a href="https://www.biblegateway.com/passage/?search=${encodeURIComponent(s.verseRef)}&version=NLT" target="_blank" rel="noopener">${esc(s.verseRef)} (NLT)</a></cite>`;
          })
          .catch(() => {});
      }
    })
    .catch(() => {
      const dom = fromKey(key).getDate();
      showEmpty(dom === 15 || dom === 30 ? "Catch-up day — no new SOAP today." : "This day's SOAP is coming soon.");
    });
})();
