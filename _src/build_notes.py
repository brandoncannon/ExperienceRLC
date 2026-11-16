"""Message Notes: turns each Sunday's notes in _src/notes/ into web pages.

Write one plain-text file per Sunday, named by its date (2026-11-15.txt).
It reads the way a printed handout does:

    Series: Thankful Anyway
    Part: 2 of 3
    Title: Thankful in the Middle
    Date: 2026-11-15
    Speaker: Pastor Brandon Cannon
    Video: https://...            (optional; add it once the message is posted)

    Big Idea: Gratitude isn't a feeling I wait for. It's a [choice] I make.

    An opening paragraph. Each line is its own paragraph.
    Scripture: Philippians 4:6-7   (the NLT text is filled in for you)

    # The first point, with a [blank] in it.
    Quote: A line people can share or save as a phone wallpaper.
    - A bullet point

    ## Talk It Over
    - A LifeGroup question

    ## This Week
    The weekly challenge.

[Brackets] make a fill-in-the-blank, *stars* make italics.

The newest file becomes /notes/; every file also gets its own page at
/notes/2026-11-15/. Scripture text comes from Tyndale's NLT API and is
saved in _src/notes/nlt-cache.json, so each passage is fetched only once.
"""
import html
import json
import re
import urllib.parse
import urllib.request
from datetime import date, timedelta
from pathlib import Path

SRC = Path(__file__).resolve().parent
NOTES = SRC / "notes"
CACHE = NOTES / "nlt-cache.json"
NLT_KEY = "362e29ab-dee0-4f7d-81fd-70d730331494"  # same key as assets/js/daily-config.js

NLT_NOTICE = (
    "Scripture quotations are taken from the <i>Holy Bible</i>, New Living Translation, "
    "copyright &copy;1996, 2004, 2015 by Tyndale House Foundation. Used by permission of "
    "Tyndale House Publishers, Carol Stream, Illinois 60188. All rights reserved."
)


# ---------- Scripture ----------

def _load_cache():
    try:
        return json.loads(CACHE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def nlt(ref, cache):
    """The passage as simple HTML (<p> with <sup> verse numbers), or "" if unavailable."""
    if ref in cache:
        return cache[ref]
    url = "https://api.nlt.to/api/passages?" + urllib.parse.urlencode({"ref": ref, "version": "NLT", "key": NLT_KEY})
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (site build)"})
        with urllib.request.urlopen(req, timeout=20) as r:
            raw = r.read().decode("utf-8")
    except Exception as e:  # noqa: BLE001 — a missing verse shouldn't stop the build
        print(f"  ! couldn't fetch {ref}: {e}")
        return ""
    m = re.search(r'<div id="bibletext".*?>(.*)</div>', raw, re.S)
    if not m or 'class="vn"' not in m.group(1):
        print(f"  ! no text for {ref}")
        return ""
    t = m.group(1)
    t = re.sub(r"<h[1-6][^>]*>.*?</h[1-6]>", " ", t, flags=re.S)       # headings
    t = re.sub(r'<span class="tn">(?:<span[^>]*>.*?</span>|.)*?</span>', "", t, flags=re.S)  # footnotes
    t = re.sub(r'<a class="a-tn">.*?</a>', "", t, flags=re.S)
    t = re.sub(r'<span class="vn">(\d+)</span>', "\x00\\1\x01", t)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(re.sub(r"\s+", " ", t)).strip()
    t = html.escape(t, quote=False).replace("\x00", "<sup>").replace("\x01", "</sup>")
    cache[ref] = f"<p>{t}</p>"
    return cache[ref]


# ---------- Reading the notes file ----------

def inline(text, blanks):
    """Escape text, then turn [answer] into a blank and *word* into italics."""
    out = html.escape(text, quote=False)

    def blank(m):
        blanks.append(m.group(1))
        ans = html.escape(m.group(1))
        return f'<span class="blank" data-answer="{ans}" style="--len:{max(len(m.group(1)), 4)}"><span class="blank-text">{ans}</span></span>'

    out = re.sub(r"\[([^\]]+)\]", blank, out)
    return re.sub(r"\*([^*]+)\*", r"<em>\1</em>", out)


def plain(text):
    return re.sub(r"[\[\]*]", "", text)


def parse(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    meta, i = {}, 0
    while i < len(lines) and lines[i].strip():
        k, _, v = lines[i].partition(":")
        meta[k.strip().lower()] = v.strip()
        i += 1
    msg = {"meta": meta, "big_idea": "", "intro": [], "points": [], "questions": [], "challenge": []}
    target = msg["intro"]
    section = None
    for line in lines[i:]:
        s = line.strip()
        if not s:
            continue
        low = s.lower()
        if low.startswith("big idea:"):
            msg["big_idea"] = s.split(":", 1)[1].strip()
        elif s.startswith("## "):
            section = s[3:].strip().lower()
            target = msg["questions"] if section.startswith("talk") else msg["challenge"]
        elif s.startswith("# "):
            section = None
            point = {"title": s[2:].strip(), "items": []}
            msg["points"].append(point)
            target = point["items"]
        elif section and section.startswith("talk"):
            target.append(s.lstrip("- ").strip())
        elif low.startswith("scripture:"):
            target.append(("scripture", s.split(":", 1)[1].strip()))
        elif low.startswith("quote:"):
            target.append(("quote", s.split(":", 1)[1].strip()))
        elif s.startswith("- "):
            target.append(("bullet", s[2:].strip()))
        else:
            target.append(("p", s))
    return msg


# ---------- Writing the page ----------

ICON = {
    "share": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M12 3v12M7 8l5-5 5 5M5 13v6a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-6"/></svg>',
    "pen": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M4 20h4L19 9l-4-4L4 16v4zM13.5 6.5l4 4"/></svg>',
    "image": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="2" width="14" height="20" rx="3" fill="none" stroke="currentColor" stroke-width="2"/><path d="M9 18h6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
    "moon": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg>',
    "text": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M3 19 8 5h2l5 14h-2.2l-1.3-3.8H6.5L5.2 19H3zm4.2-5.8h3.6L9 7.9l-1.8 5.3zM16 19l3-8h1.6l3 8H22l-.7-2h-3l-.7 2H16zm2.1-3.4h2.2l-1.1-3.1-1.1 3.1z"/></svg>',
    "eye": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3" fill="currentColor"/></svg>',
    "play": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M8 5.5v13l11-6.5z"/></svg>',
}


def render_items(items, blanks, cache, point_id):
    out, bullets = [], []

    def flush():
        if bullets:
            out.append("<ul class=\"n-bullets\">" + "".join(f"<li>{b}</li>" for b in bullets) + "</ul>")
            bullets.clear()

    for kind, text in items:
        if kind != "bullet":
            flush()
        if kind == "p":
            out.append(f"<p>{inline(text, blanks)}</p>")
        elif kind == "bullet":
            bullets.append(inline(text, blanks))
        elif kind == "quote":
            q = html.escape(text)
            out.append(
                f'<figure class="n-quote" data-quote="{q}"><blockquote>{q}</blockquote>'
                f'<figcaption><button type="button" class="n-chip" data-share-quote>{ICON["share"]}Share</button>'
                f'<button type="button" class="n-chip" data-wallpaper>{ICON["image"]}Save as wallpaper</button></figcaption></figure>'
            )
        elif kind == "scripture":
            body = nlt(text, cache) or '<p class="n-muted">Open it in your Bible app.</p>'
            link = "https://www.biblegateway.com/passage/?" + urllib.parse.urlencode({"search": text, "version": "NLT"})
            out.append(
                f'<div class="n-scripture"><p class="n-ref"><a href="{link}" target="_blank" rel="noopener">{html.escape(text)}</a> <span>NLT</span></p>'
                f'<div class="n-verse">{body}</div></div>'
            )
    flush()
    if point_id:
        out.append(
            f'<div class="n-mynote"><button type="button" class="n-chip n-addnote" aria-expanded="false" aria-controls="note-{point_id}">{ICON["pen"]}Add my own note</button>'
            f'<label class="sr-only" for="note-{point_id}">My note</label>'
            f'<textarea id="note-{point_id}" class="n-note-input" data-note="{point_id}" rows="3" placeholder="What is God saying to you here?" hidden></textarea></div>'
        )
    return "".join(out)


def render(msg, cache, all_msgs):
    m = msg["meta"]
    blanks = []
    when = date.fromisoformat(m["date"])
    pretty = f"{when:%B} {when.day}, {when.year}"
    big = inline(msg["big_idea"], blanks) if msg["big_idea"] else ""

    points = []
    for n, p in enumerate(msg["points"], 1):
        points.append(
            f'<section class="n-point" id="point-{n}" data-point="{n}"><h2><span class="n-num" aria-hidden="true">{n}</span>'
            f'<span class="n-title">{inline(p["title"], blanks)}</span></h2>'
            f'{render_items(p["items"], blanks, cache, str(n))}</section>'
        )

    questions = ""
    if msg["questions"]:
        qs = "".join(f"<li>{inline(q, blanks)}</li>" for q in msg["questions"])
        questions = (
            '<details class="n-panel" id="talk"><summary><span><span class="n-label">For LifeGroups &amp; family</span>Talk It Over</span>'
            f'<span class="n-count">{len(msg["questions"])} questions</span></summary><ol class="n-questions">{qs}</ol></details>'
        )

    challenge = ""
    if msg["challenge"]:
        days = []
        for k in range(1, 8):
            d = when + timedelta(days=k)
            days.append(
                f'<label class="n-day"><input type="checkbox" data-day="{d.isoformat()}"><span><b>{d:%a}</b>{d.day}</span></label>'
            )
        text = "".join(f"<p>{inline(t, blanks)}</p>" for _, t in msg["challenge"])
        challenge = (
            '<section class="n-panel n-challenge" id="this-week"><p class="n-label">This week</p>'
            f'{text}<div class="n-days" role="group" aria-label="Days you did it">{"".join(days)}</div>'
            '<p class="n-muted n-streak" aria-live="polite"></p></section>'
        )

    video = ""
    if m.get("video"):
        video = f'<a class="btn btn-tint btn-sm n-watch" href="{html.escape(m["video"])}" target="_blank" rel="noopener">{ICON["play"]}Watch this message</a>'

    others = [x for x in all_msgs if x["meta"]["date"] != m["date"]]
    past = ""
    if others:
        items = "".join(
            f'<li><a href="/notes/{x["meta"]["date"]}/">{html.escape(plain(x["meta"].get("title", "")))}</a>'
            f'<small>{html.escape(x["meta"].get("series", ""))} · {date.fromisoformat(x["meta"]["date"]):%B %-d, %Y}</small></li>'
            for x in others[:8]
        )
        past = f'<section class="n-past"><h2>Earlier messages</h2><ul class="archive-list">{items}</ul></section>'

    intro = render_items(msg["intro"], blanks, cache, None)
    part = f'<span class="n-part">{html.escape(m["part"])}</span>' if m.get("part") else ""

    body = f"""
<div class="notes" data-date="{m['date']}" data-title="{html.escape(plain(m.get('title', '')))}" data-series="{html.escape(m.get('series', ''))}" data-speaker="{html.escape(m.get('speaker', ''))}">
<section class="n-hero">
  <div class="wrap-narrow">
    <p class="n-series"><span>{html.escape(m.get('series', ''))}</span>{part}</p>
    <h1>{html.escape(plain(m.get('title', '')))}</h1>
    <p class="n-meta">{html.escape(m.get('speaker', ''))} · {pretty}</p>
    {video}
  </div>
</section>

<div class="n-tools" role="toolbar" aria-label="Notes settings">
  <div class="wrap-narrow">
    <span class="n-progress" aria-live="polite"><b data-filled>0</b> of {len(blanks)} blanks</span>
    <span class="n-tool-buttons">
      <button type="button" class="n-tool" data-reveal aria-pressed="false">{ICON['eye']}<span>Fill them in</span></button>
      <button type="button" class="n-tool" data-textsize aria-label="Text size">{ICON['text']}<span>Size</span></button>
      <button type="button" class="n-tool" data-lights aria-pressed="false">{ICON['moon']}<span>Lights down</span></button>
    </span>
  </div>
</div>

<div class="wrap-narrow n-body">
  {f'<section class="n-bigidea" data-quote="{html.escape(plain(msg["big_idea"]))}"><p class="n-label">The Big Idea</p><p class="n-big">{big}</p><p class="n-actions"><button type="button" class="n-chip" data-share-quote>{ICON["share"]}Share</button><button type="button" class="n-chip" data-wallpaper>{ICON["image"]}Save as wallpaper</button></p></section>' if big else ''}
  <div class="n-intro">{intro}</div>
  {''.join(points)}
  {challenge}
  {questions}

  <section class="n-panel n-send" id="send">
    <p class="n-label">Keep your notes</p>
    <p>Your blanks and notes save on this phone automatically. Send yourself a copy to keep.</p>
    <form class="n-send-form" novalidate>
      <label class="sr-only" for="n-email">Your email</label>
      <input id="n-email" type="email" name="email" autocomplete="email" inputmode="email" placeholder="you@example.com">
      <div class="btn-row">
        <button class="btn btn-dark btn-sm" type="submit">Email me my notes</button>
        <button class="btn btn-outline btn-sm" type="button" data-copy-notes>Copy</button>
      </div>
      <p class="n-muted n-status" role="status" aria-live="polite"></p>
    </form>
  </section>

  <section class="n-respond">
    <h2>Take a next step</h2>
    <div class="n-respond-grid">
      <a href="{{{{link:connect_card}}}}" target="_blank" rel="noopener"><b>I said yes to Jesus</b><span>Let us know so we can celebrate and help.</span></a>
      <a href="/water-baptism/"><b>Get baptized</b><span>Sign up for the next baptism Sunday.</span></a>
      <a href="/prayer/"><b>Ask for prayer</b><span>Our prayer team would love to pray with you.</span></a>
      <a href="{{{{link:groups}}}}" target="_blank" rel="noopener"><b>Join a LifeGroup</b><span>Talk this message over with friends.</span></a>
    </div>
  </section>

  <p class="n-muted n-copyright">{NLT_NOTICE}</p>
  {past}
</div>
<dialog class="n-wall" aria-label="Phone wallpaper">
  <p class="n-wall-tip">Press and hold the image to save it, then set it as your lock screen.</p>
  <img alt="">
  <div class="btn-row"><button type="button" class="btn btn-dark btn-sm" data-wall-save>Save image</button><button type="button" class="btn btn-outline btn-sm" data-wall-close>Close</button></div>
</dialog>
</div>
<script src="/assets/js/notes.js"></script>
"""
    title = plain(m.get("title", "Message Notes"))
    desc = f"Notes for “{title}” from {m.get('series', '')} at Real Life Church, {pretty}."
    head = '<link href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">'
    return f"<!-- title: {title} -->\n<!-- description: {desc} -->\n<!-- head: {head} -->\n" + body


def pages():
    """[(slug, page source)] for build.py: /notes/ (newest) and /notes/<date>/ for each."""
    files = sorted(NOTES.glob("[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].txt"), reverse=True)
    if not files:
        return []
    cache = _load_cache()
    msgs = [parse(f) for f in files]
    out = [(f"notes/{x['meta']['date']}", render(x, cache, msgs)) for x in msgs]
    out.insert(0, ("notes", render(msgs[0], cache, msgs)))
    CACHE.write_text(json.dumps(cache, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return out
