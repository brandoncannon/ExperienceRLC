// "Your Turn": readers write their own SOAP, saved on their device,
// then email it to themselves through their own email app (mailto:).
(function () {
  const form = document.getElementById("my-soap-form");
  if (!form) return;
  const $ = (id) => document.getElementById(id);
  const pad = (n) => String(n).padStart(2, "0");
  const toKey = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
  const todayKey = toKey(new Date());
  const param = new URLSearchParams(location.search).get("date");
  const key = /^\d{4}-\d{2}-\d{2}$/.test(param || "") ? param : todayKey;
  const [y, m, d] = key.split("-").map(Number);
  const pretty = new Date(y, m - 1, d).toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric", year: "numeric" });

  if (key > todayKey) { $("my-soap").hidden = true; return; }

  // Storage can be unavailable (private browsing); everything still works without it.
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} },
    del(k) { try { localStorage.removeItem(k); } catch (e) {} },
  };
  const DRAFT = `rlc-soap-${key}`;
  const fields = ["s", "o", "a", "p"];
  const status = (msg) => { $("my-soap-status").textContent = msg; };

  // Restore this day's draft and the saved email address.
  try {
    const saved = JSON.parse(store.get(DRAFT) || "{}");
    fields.forEach((f) => { if (saved[f]) form.elements[f].value = saved[f]; });
  } catch (e) {}
  form.elements.email.value = store.get("rlc-soap-email") || "";

  let timer;
  form.addEventListener("input", (e) => {
    if (e.target.name === "email") { store.set("rlc-soap-email", e.target.value.trim()); return; }
    clearTimeout(timer);
    timer = setTimeout(() => {
      const data = {};
      fields.forEach((f) => { data[f] = form.elements[f].value; });
      store.set(DRAFT, JSON.stringify(data));
      status("Saved on this device.");
    }, 400);
  });

  const reading = () => {
    const t = ($("reading-title") && $("reading-title").textContent.trim()) || "";
    return /loading|no reading|unavailable/i.test(t) ? "" : t;
  };
  const compose = () => {
    const v = (f) => form.elements[f].value.trim() || "—";
    return [
      `My SOAP · ${pretty}`,
      reading() ? `Reading: ${reading()}` : "",
      "",
      "S · SCRIPTURE", v("s"), "",
      "O · OBSERVATION", v("o"), "",
      "A · APPLICATION", v("a"), "",
      "P · PRAYER", v("p"), "",
      `Today's reading: ${location.origin}${location.pathname}?date=${key}`,
    ].filter((line, i) => !(i === 1 && !line)).join("\n");
  };
  const isEmpty = () => fields.every((f) => !form.elements[f].value.trim());

  const copy = (text) =>
    (navigator.clipboard ? navigator.clipboard.writeText(text) : Promise.reject())
      .catch(() => {
        const t = document.createElement("textarea");
        t.value = text; document.body.appendChild(t); t.select();
        try { document.execCommand("copy"); } finally { t.remove(); }
      });

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    if (isEmpty()) { status("Write at least one part of your SOAP first."); form.elements.s.focus(); return; }
    const email = form.elements.email.value.trim();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { status("Enter your email address so it knows where to send it."); form.elements.email.focus(); return; }
    store.set("rlc-soap-email", email);
    const subject = `My SOAP${reading() ? " – " + reading() : ""}, ${pretty.replace(/, \d{4}$/, "")}`;
    const body = compose();
    // Very long messages can be cut off by some email apps, so also copy it.
    if (body.length > 1800) copy(body);
    const url = `mailto:${encodeURIComponent(email)}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    form.dataset.mailto = url; // handy for checking what was sent
    window.location.href = url;
    status(body.length > 1800
      ? "Your email app should open with your SOAP. It's long, so it's also copied: if anything is cut off, paste it in."
      : "Your email app should open with your SOAP ready. Just tap Send.");
  });

  $("my-soap-copy").addEventListener("click", () => {
    if (isEmpty()) { status("Nothing to copy yet."); return; }
    copy(compose()).then(() => status("Copied. Paste it anywhere: notes, a journal app, a text."));
  });

  $("my-soap-clear").addEventListener("click", () => {
    if (!isEmpty() && !confirm("Clear your SOAP for this day?")) return;
    fields.forEach((f) => { form.elements[f].value = ""; });
    store.del(DRAFT);
    status("Cleared.");
  });
})();
