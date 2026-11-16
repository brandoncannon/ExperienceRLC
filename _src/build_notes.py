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
    (Romans 1:16-17) The verse, typed the way you want it shown.
    (Philippians 4:6-7)            (reference only: the NLT text is filled in)
    Principle: The main idea. People can share it or save it as a wallpaper.
    ### A small heading

    # (v6a) The first point, with a [blank] in it.
    Takeaway: A line to stand out, like "The Gospel gives us the ability to..."
    Quote: A line people can share or save as a phone wallpaper.
    - A bullet point

    ## Questions for Reflection
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
        return (
            f'<span class="blank" data-answer="{ans}"><input type="text" class="blank-input" style="--len:{max(len(m.group(1)), 5)}" '
            'aria-label="Fill in the blank" autocomplete="off" autocapitalize="off" spellcheck="false" enterkeyhint="next"></span>'
        )

    out = re.sub(r"\[([^\]]+)\]", blank, out)
    return re.sub(r"\*([^*]+)\*", r"<em>\1</em>", out)


def plain(text):
    return re.sub(r"[\[\]*]", "", text)


# "(Romans 1:16-17) For I am not ashamed..." — a reference in parentheses, then the verse as you want it shown.
SCRIPTURE_LINE = re.compile(r"^\(((?:[1-3] ?)?[A-Z][A-Za-z]+(?: (?:of )?[A-Z][a-z]+)* ?\d+[:\d\w ,\-–]*)\)\s*(.*)$")


def parse(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    meta, i = {}, 0
    while i < len(lines) and lines[i].strip():
        k, _, v = lines[i].partition(":")
        meta[k.strip().lower()] = v.strip()
        i += 1
    msg = {"meta": meta, "intro": [], "points": [], "questions": [], "challenge": [], "talk_title": "Talk It Over"}
    target = msg["intro"]
    section = None
    for line in lines[i:]:
        s = line.strip()
        if not s:
            continue
        low = s.lower()
        ref = SCRIPTURE_LINE.match(s)
        if low.startswith(("big idea:", "principle:")):
            label, _, text = s.partition(":")
            target.append(("bigidea", (label.strip(), text.strip())))
        elif s.startswith("### "):
            target.append(("heading", s[4:].strip()))
        elif s.startswith("## "):
            section = s[3:].strip().lower()
            if "question" in section or "talk" in section:
                msg["talk_title"] = s[3:].strip()
                section = "talk"
                target = msg["questions"]
            else:
                target = msg["challenge"]
        elif s.startswith("# "):
            section = None
            point = {"title": s[2:].strip(), "items": []}
            msg["points"].append(point)
            target = point["items"]
        elif section == "talk":
            target.append(s.lstrip("- ").strip())
        elif low.startswith("scripture:"):
            target.append(("scripture", (s.split(":", 1)[1].strip(), "")))
        elif ref:
            target.append(("scripture", (ref.group(1).strip(), ref.group(2).strip())))
        elif low.startswith("takeaway:"):
            target.append(("takeaway", s.split(":", 1)[1].strip()))
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
    "insta": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="17.3" cy="6.7" r="1.2" fill="currentColor"/></svg>',
    "moon": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg>',
    "text": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M3 19 8 5h2l5 14h-2.2l-1.3-3.8H6.5L5.2 19H3zm4.2-5.8h3.6L9 7.9l-1.8 5.3zM16 19l3-8h1.6l3 8H22l-.7-2h-3l-.7 2H16zm2.1-3.4h2.2l-1.1-3.1-1.1 3.1z"/></svg>',
    "eye": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3" fill="currentColor"/></svg>',
    "play": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M8 5.5v13l11-6.5z"/></svg>',
}


def share_buttons():
    """Share, Instagram and wallpaper buttons for a quotable line."""
    return (
        f'<button type="button" class="n-chip" data-share-quote>{ICON["share"]}Share</button>'
        f'<button type="button" class="n-chip" data-instagram>{ICON["insta"]}Share on Instagram</button>'
        f'<button type="button" class="n-chip" data-wallpaper>{ICON["image"]}Save as wallpaper</button>'
    )


def render_items(items, blanks, cache, point_id):
    out, bullets = [], []

    def flush():
        if bullets:
            out.append("<ul class=\"n-bullets\">" + "".join(f"<li data-keep>{b}</li>" for b in bullets) + "</ul>")
            bullets.clear()

    for kind, text in items:
        if kind != "bullet":
            flush()
        if kind == "p":
            out.append(f"<p data-keep>{inline(text, blanks)}</p>")
        elif kind == "heading":
            out.append(f'<h3 class="n-sub" data-keep>{inline(text, blanks)}</h3>')
        elif kind == "takeaway":
            out.append(
                f'<div class="n-takeaway" data-quote="{html.escape(plain(text))}"><p data-keep>{inline(text, blanks)}</p>'
                f'<p class="n-actions">{share_buttons()}</p></div>'
            )
        elif kind == "bigidea":
            label, idea = text
            out.append(
                f'<section class="n-bigidea" data-quote="{html.escape(plain(idea))}"><p class="n-label">{html.escape(label)}</p>'
                f'<p class="n-big" data-keep>{inline(idea, blanks)}</p><p class="n-actions">{share_buttons()}</p></section>'
            )
        elif kind == "bullet":
            bullets.append(inline(text, blanks))
        elif kind == "quote":
            q = html.escape(text)
            out.append(
                f'<figure class="n-quote" data-quote="{q}"><blockquote>{q}</blockquote>'
                f'<figcaption>{share_buttons()}</figcaption></figure>'
            )
        elif kind == "scripture":
            ref, words = text
            if words:
                has_blank = "[" in words
                body = f'<p{" data-keep" if has_blank else ""}>{inline(words, blanks)}</p>'
            else:
                body = nlt(ref, cache) or '<p class="n-muted">Open it in your Bible app.</p>'
            link = "https://www.biblegateway.com/passage/?" + urllib.parse.urlencode({"search": ref, "version": "NLT"})
            out.append(
                f'<div class="n-scripture"><p class="n-ref" data-keep><a href="{link}" target="_blank" rel="noopener">{html.escape(ref)}</a> <span>NLT</span></p>'
                f'<div class="n-verse">{body}</div></div>'
            )
    flush()
    if point_id:
        out.append(
            f'<div class="n-mynote"><label class="n-note-label" for="note-{point_id}">{ICON["pen"]}My notes</label>'
            f'<textarea id="note-{point_id}" class="n-note-input" data-note="{point_id}" rows="2" placeholder="Write anything that stands out to you…"></textarea></div>'
        )
    return "".join(out)


def render(msg, cache, all_msgs):
    m = msg["meta"]
    blanks = []
    when = date.fromisoformat(m["date"])
    pretty = f"{when:%B} {when.day}, {when.year}"

    points = []
    intro = render_items(msg["intro"], blanks, cache, "intro")
    for n, p in enumerate(msg["points"], 1):
        t = p["title"]
        tag = re.match(r"\((v[\w-]+)\)\s*", t)
        chip = f'<span class="n-vtag">{html.escape(tag.group(1))}</span>' if tag else ""
        if tag:
            t = t[tag.end():]
        points.append(
            f'<section class="n-point" id="point-{n}" data-point="{n}"><h2><span class="n-num" aria-hidden="true">{n}</span>'
            f'<span class="n-title">{chip}{inline(t, blanks)}</span></h2>'
            f'{render_items(p["items"], blanks, cache, str(n))}</section>'
        )

    questions = ""
    if msg["questions"]:
        qs = "".join(f"<li>{inline(q, blanks)}</li>" for q in msg["questions"])
        questions = (
            f'<details class="n-panel" id="talk"><summary><span><span class="n-label">For LifeGroups &amp; family</span>{html.escape(msg["talk_title"])}</span>'
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

    part = f'<span class="n-part">{html.escape(m["part"])}</span>' if m.get("part") else ""

    # Series graphic (assets/img/series/) and its two colors: "Colors: background, text".
    art, theme, hero_cls = "", "", "n-hero"
    if m.get("art"):
        art = f'<img class="n-art" src="/assets/img/series/{html.escape(m["art"])}" alt="{html.escape(m.get("series", ""))} series graphic">'
        hero_cls += " has-art"
    colors = [c.strip() for c in m.get("colors", "").split(",") if re.fullmatch(r"#[0-9a-fA-F]{6}", c.strip())]
    if len(colors) == 2:
        theme = f' style="--s-bg:{colors[0]};--s-fg:{colors[1]}"'

    body = f"""
<div class="notes{' has-theme' if theme else ''}"{theme} data-date="{m['date']}" data-title="{html.escape(plain(m.get('title', '')))}" data-series="{html.escape(m.get('series', ''))}" data-speaker="{html.escape(m.get('speaker', ''))}">
<section class="{hero_cls}">
  <div class="wrap-narrow">
    {art}
    <p class="n-series"><span>{html.escape(m.get('series', ''))}</span>{part}</p>
    <h1>{html.escape(plain(m.get('title', '')))}</h1>
    <p class="n-meta">{html.escape(m.get('speaker', ''))} · {pretty}</p>
    {video}
  </div>
</section>

<div class="n-tools" role="toolbar" aria-label="Notes settings">
  <div class="wrap-narrow">
    <span class="n-progress" aria-live="polite"><b data-filled>0</b> of {len(blanks)} blanks filled</span>
    <span class="n-tool-buttons">
      <button type="button" class="n-tool" data-reveal aria-pressed="false">{ICON['eye']}<span>Fill them in</span></button>
      <button type="button" class="n-tool" data-textsize aria-label="Text size">{ICON['text']}<span>Size</span></button>
      <button type="button" class="n-tool" data-lights aria-pressed="false">{ICON['moon']}<span>Lights down</span></button>
    </span>
  </div>
</div>

<div class="wrap-narrow n-body">
  <p class="n-hint">Tap a blank to fill it in. It turns green when it matches. Everything you type saves on this phone.</p>
  <div class="n-intro">{intro}</div>
  {''.join(points)}
  {challenge}
  {questions}

  <section class="n-panel n-send" id="send">
    <p class="n-label">Keep your notes</p>
    <p>Send your filled-in notes to yourself by email or text, or save them in your Notes app.</p>
    <div class="btn-row">
      <button class="btn btn-dark btn-sm" type="button" data-send-notes>Send my notes</button>
      <button class="btn btn-outline btn-sm" type="button" data-copy-notes>Copy</button>
    </div>
    <p class="n-muted n-status" role="status" aria-live="polite"></p>
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
  <div class="btn-row"><button type="button" class="btn btn-dark btn-sm" data-wall-save>Save image</button><a class="btn btn-outline btn-sm" data-wall-insta href="https://www.instagram.com/" target="_blank" rel="noopener" hidden>Open Instagram</a><button type="button" class="btn btn-outline btn-sm" data-wall-close>Close</button></div>
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
