// Message Notes: fill-in blanks, personal notes, sharing, wallpapers, the weekly
// challenge and "Lights down". Everything a person types stays on their own device.
(function () {
  const root = document.querySelector(".notes");
  if (!root) return;
  const $ = (sel, el = root) => el.querySelector(sel);
  const $$ = (sel, el = root) => [...el.querySelectorAll(sel)];
  const KEY = `rlc-notes-${root.dataset.date}`;

  // Storage can be unavailable (private browsing); everything still works without it.
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} },
  };
  let saved = {};
  try { saved = JSON.parse(store.get(KEY) || "{}"); } catch (e) {}
  saved.blanks = saved.blanks || {};
  saved.notes = saved.notes || {};
  saved.days = saved.days || {};
  const save = () => store.set(KEY, JSON.stringify(saved));

  // Small message that fades away.
  const toast = document.createElement("div");
  toast.className = "n-toast";
  toast.setAttribute("role", "status");
  document.body.appendChild(toast);
  let toastTimer;
  const say = (msg) => {
    toast.textContent = msg;
    toast.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove("show"), 2200);
  };

  const copy = (text) =>
    (navigator.clipboard ? navigator.clipboard.writeText(text) : Promise.reject()).catch(() => {
      const t = document.createElement("textarea");
      t.value = text; t.setAttribute("readonly", ""); t.style.position = "fixed"; t.style.opacity = "0";
      document.body.appendChild(t); t.select();
      try { document.execCommand("copy"); } finally { t.remove(); }
    });

  // ---- Fill-in blanks ----
  const norm = (s) => s.toLowerCase().replace(/[^a-z0-9]/g, "");
  const blanks = $$(".blank").map((span, i) => {
    const input = $("input", span);
    input.id = `blank-${i}`;
    input.value = saved.blanks[i] || "";
    return { span, input, answer: span.dataset.answer, i };
  });
  const isRight = (b) => norm(b.input.value) === norm(b.answer);
  const filledEl = $("[data-filled]");
  const update = (b, celebrate) => {
    const right = isRight(b);
    const was = b.span.classList.contains("right");
    b.span.classList.toggle("right", right);
    if (right && celebrate && !was) {
      b.span.classList.remove("pop"); void b.span.offsetWidth; b.span.classList.add("pop");
    }
    const n = blanks.filter(isRight).length;
    if (filledEl) filledEl.textContent = n;
    root.classList.toggle("all-filled", blanks.length > 0 && n === blanks.length);
  };
  blanks.forEach((b) => {
    update(b, false);
    b.input.addEventListener("input", () => {
      b.span.classList.remove("revealed");
      saved.blanks[b.i] = b.input.value; save();
      update(b, true);
    });
    // Enter jumps to the next blank, like a form.
    b.input.addEventListener("keydown", (e) => {
      if (e.key !== "Enter") return;
      e.preventDefault();
      const next = blanks[b.i + 1];
      if (next) next.input.focus(); else b.input.blur();
    });
  });

  // "Fill them in" for anyone who fell behind; press again to take back the ones it filled.
  const revealBtn = $("[data-reveal]");
  if (revealBtn) revealBtn.addEventListener("click", () => {
    const on = revealBtn.getAttribute("aria-pressed") !== "true";
    revealBtn.setAttribute("aria-pressed", String(on));
    blanks.forEach((b) => {
      if (on && !isRight(b)) { b.input.value = b.answer; b.span.classList.add("revealed"); }
      else if (!on && b.span.classList.contains("revealed")) { b.input.value = ""; b.span.classList.remove("revealed"); }
      saved.blanks[b.i] = b.input.value;
      update(b, false);
    });
    save();
  });

  // ---- Text size and Lights down (remembered for every message) ----
  const sizes = ["", "n-size-lg", "n-size-xl"];
  let size = Math.max(0, sizes.indexOf(store.get("rlc-notes-size") || ""));
  const applySize = () => { sizes.forEach((c) => c && root.classList.remove(c)); if (sizes[size]) root.classList.add(sizes[size]); };
  applySize();
  const sizeBtn = $("[data-textsize]");
  if (sizeBtn) sizeBtn.addEventListener("click", () => {
    size = (size + 1) % sizes.length; applySize(); store.set("rlc-notes-size", sizes[size]);
    say(["Regular text", "Larger text", "Largest text"][size]);
  });

  const html = document.documentElement;
  const lightsBtn = $("[data-lights]");
  const setLights = (on) => {
    html.classList.toggle("lights-down", on);
    if (lightsBtn) lightsBtn.setAttribute("aria-pressed", String(on));
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.content = on ? "#0b1a28" : "#153c5d";
  };
  setLights(store.get("rlc-notes-lights") === "1");
  if (lightsBtn) lightsBtn.addEventListener("click", () => {
    const on = !html.classList.contains("lights-down");
    setLights(on); store.set("rlc-notes-lights", on ? "1" : "0");
  });

  // ---- My own notes under each point ----
  // The box grows as you write.
  const grow = (ta) => { ta.style.height = "auto"; ta.style.height = ta.scrollHeight + 2 + "px"; };
  $$(".n-note-input").forEach((ta) => {
    const id = ta.dataset.note;
    if (saved.notes[id]) ta.value = saved.notes[id];
    if (ta.value) grow(ta);
    ta.addEventListener("input", () => { saved.notes[id] = ta.value; save(); grow(ta); });
  });

  // ---- Weekly challenge ----
  const days = $$(".n-day input");
  const streak = $(".n-streak");
  const showStreak = () => {
    const n = days.filter((d) => d.checked).length;
    if (!streak) return;
    streak.textContent = n === 0 ? "" : n === 7 ? "All seven days. Well done!" : `${n} of 7 days so far. Keep going!`;
  };
  days.forEach((d) => {
    d.checked = !!saved.days[d.dataset.day];
    d.addEventListener("change", () => { saved.days[d.dataset.day] = d.checked; save(); showStreak(); });
  });
  showStreak();

  // ---- Sharing a quote ----
  const credit = () => `${root.dataset.speaker ? root.dataset.speaker + ", " : ""}Real Life Church`;
  const quoteOf = (btn) => {
    const box = btn.closest("[data-quote]");
    // The Big Idea shares with the reader's blanks filled in as the answers.
    return box ? box.dataset.quote : "";
  };
  $$("[data-share-quote]").forEach((btn) => btn.addEventListener("click", () => {
    const text = `“${quoteOf(btn)}”\n— ${credit()}`;
    const url = location.href.split("#")[0];
    if (navigator.share) {
      navigator.share({ text, url }).catch(() => {});
    } else {
      copy(`${text}\n${url}`).then(() => say("Quote copied. Paste it anywhere."));
    }
  }));

  // ---- Phone wallpaper from a quote ----
  const dialog = $(".n-wall");
  const wallImg = dialog && $("img", dialog);
  const wrap = (ctx, text, max) => {
    const words = text.split(/\s+/); const lines = []; let line = "";
    words.forEach((w) => {
      const t = line ? line + " " + w : w;
      if (ctx.measureText(t).width > max && line) { lines.push(line); line = w; } else line = t;
    });
    if (line) lines.push(line);
    return lines;
  };
  const makeWallpaper = (quote) => {
    const W = 1170, H = 2532, c = document.createElement("canvas");
    c.width = W; c.height = H;
    const ctx = c.getContext("2d");
    const g = ctx.createLinearGradient(0, 0, W * 0.4, H);
    g.addColorStop(0, "#1d4a70"); g.addColorStop(1, "#0b1f31");
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    // Soft aqua glow, like stage light.
    const glow = ctx.createRadialGradient(W * 0.85, H * 0.18, 10, W * 0.85, H * 0.18, W * 0.9);
    glow.addColorStop(0, "rgba(158,203,209,.35)"); glow.addColorStop(1, "rgba(158,203,209,0)");
    ctx.fillStyle = glow; ctx.fillRect(0, 0, W, H);
    const pad = 120;
    let fs = 104;
    ctx.font = `700 ${fs}px Figtree, system-ui, sans-serif`;
    let lines = wrap(ctx, quote, W - pad * 2);
    while (lines.length > 7 && fs > 64) { fs -= 8; ctx.font = `700 ${fs}px Figtree, system-ui, sans-serif`; lines = wrap(ctx, quote, W - pad * 2); }
    const lh = fs * 1.18;
    // Leave the top third clear for the phone's clock.
    let y = H * 0.44;
    ctx.fillStyle = "#9ecbd1"; ctx.fillRect(pad, y - fs - 70, 96, 10);
    ctx.fillStyle = "#ffffff"; ctx.textBaseline = "alphabetic";
    lines.forEach((l) => { ctx.fillText(l, pad, y); y += lh; });
    ctx.font = "600 44px Figtree, system-ui, sans-serif";
    ctx.fillStyle = "#cfe6ea";
    ctx.fillText(`${root.dataset.series} · ${root.dataset.title}`, pad, y + 60);
    ctx.font = "500 40px Figtree, system-ui, sans-serif";
    ctx.fillStyle = "rgba(255,255,255,.6)";
    ctx.fillText("experiencerlc.com", pad, H - 200);
    return c.toDataURL("image/png");
  };
  $$("[data-wallpaper]").forEach((btn) => btn.addEventListener("click", () => {
    if (!dialog) return;
    const q = `“${quoteOf(btn)}”`;
    (document.fonts ? document.fonts.ready : Promise.resolve()).then(() => {
      wallImg.src = makeWallpaper(q);
      wallImg.alt = `Wallpaper: ${q}`;
      if (dialog.showModal) dialog.showModal(); else dialog.setAttribute("open", "");
    });
  }));
  if (dialog) {
    $("[data-wall-close]", dialog).addEventListener("click", () => dialog.close ? dialog.close() : dialog.removeAttribute("open"));
    dialog.addEventListener("click", (e) => { if (e.target === dialog && dialog.close) dialog.close(); });
    $("[data-wall-save]", dialog).addEventListener("click", () => {
      const a = document.createElement("a");
      a.href = wallImg.src; a.download = `rlc-${root.dataset.date}-wallpaper.png`;
      document.body.appendChild(a); a.click(); a.remove();
    });
  }

  // ---- Email or copy my notes ----
  const textOf = (el) => {
    if (!el) return "";
    const c = el.cloneNode(true);
    $$("input.blank-input", c).forEach((inp, k) => {
      const live = $$("input.blank-input", el)[k];
      inp.replaceWith(live && live.value.trim() ? live.value.trim().toUpperCase() : "_____");
    });
    $$("sup", c).forEach((s) => s.replaceWith(""));
    $$(".n-vtag", c).forEach((s) => s.replaceWith(`(${s.textContent}) `));
    return c.textContent.replace(/\s+/g, " ").trim();
  };
  const compose = () => {
    const meta = $(".n-meta");
    const out = [`${root.dataset.title} \u2014 ${root.dataset.series}`, meta ? meta.textContent.trim() : "", ""];
    $$("[data-keep], .n-point h2, .n-note-input").forEach((el) => {
      const point = el.closest(".n-point");
      const indent = point ? "   " : "";
      if (el.matches(".n-note-input")) {
        if (el.value.trim()) out.push(`${indent}MY NOTES: ${el.value.trim()}`);
      } else if (el.matches(".n-point h2")) {
        out.push("", `${point.dataset.point}. ${textOf($(".n-title", el))}`);
      } else if (el.matches(".n-ref")) {
        out.push(`${indent}(${$("a", el).textContent})`);
      } else {
        out.push(`${indent}${textOf(el)}`);
      }
    });
    const qs = $$(".n-questions li");
    if (qs.length) {
      const title = $("#talk summary > span");
      out.push("", (title ? title.lastChild.textContent : "Questions").toUpperCase());
      qs.forEach((q, k) => out.push(`${k + 1}. ${textOf(q)}`));
    }
    out.push("", `Notes online: ${location.href.split("#")[0]}`);
    return out.join("\n");
  };
  const status = $(".n-status");
  const subject = `My notes: ${root.dataset.title}`;
  const sendBtn = $("[data-send-notes]");
  if (sendBtn) sendBtn.addEventListener("click", () => {
    const text = compose();
    // Phones: the share sheet (Mail, Messages, Notes...). Computers: the email app.
    if (navigator.share) {
      navigator.share({ title: subject, text })
        .then(() => { status.textContent = "Sent."; })
        .catch((e) => {
          if (e && e.name === "AbortError") return;
          copy(text).then(() => { status.textContent = "Sharing isn't available here, so your notes were copied. Paste them into an email, a text or Notes."; });
        });
    } else {
      status.textContent = "Opening your email app\u2026 If nothing opens, use Copy.";
      location.href = `mailto:?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(text)}`;
    }
  });
  const copyBtn = $("[data-copy-notes]");
  if (copyBtn) copyBtn.addEventListener("click", () => copy(compose()).then(() => { status.textContent = "Copied. Paste it into an email, a text or your Notes app."; }));
})();
