#!/usr/bin/env python3
"""Builds the static site.

Each file in _src/pages/ is a page body. Its first lines are settings:

    <!-- title: Plan Your Visit -->
    <!-- description: One sentence for search engines. -->

The output path comes from the file name: index.html -> /index.html,
new-here.html -> /new-here/index.html (so URLs match the old WordPress site).

Run:  python3 _src/build.py
"""
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "_src"
SITE_NAME = "Real Life Church"
SITE_URL = "https://www.experiencerlc.com"

# Shared links, so a change here updates every page.
LINKS = {
    "give": "https://tithe.ly/give_new/www/#/tithely/give-one-time/306850",
    "app": "https://subsplash.com/reallifechurch/app",
    "events": "https://experiencerlc.churchcenter.com/registrations/events",
    "groups": "https://experiencerlc.churchcenter.com/groups",
    "connect_card": "https://experiencerlc.churchcenter.com/people/forms/443983",
    "facebook": "https://www.facebook.com/reallifechurchbg/",
    "facebook_live": "https://www.facebook.com/experiencerlc",
    "instagram": "https://instagram.com/experience_rlc",
    "youtube": "https://www.youtube.com/myreallifechurch",
    "podcast": "https://itunes.apple.com/us/podcast/real-life-church-real-life/id747574962",
    "bible_podcast": "https://thebiblebreakdown.buzzsprout.com/share",
    "bb_facebook": "https://www.facebook.com/thebiblebreakdown",
    "blog": "https://brandoncannon.com",
    "text_alerts": "sms:94000?&body=reallife",
    "counseling_form": "https://forms.gle/Je6UF3yQepL8sQFy9",
    "maps": "https://maps.google.com/?q=2714+Scottsville+Road+Bowling+Green+KY+42104",
    # TEMPORARY: Message Notes use Subsplash's built-in notes (the same link as
    # "Current Message Notes" on the app's Messages tab). When our own notes at
    # /notes/ are ready, change this one line back to "/notes/" and rebuild.
    "notes": "https://notes.subsplash.com/fill-in/view?app=FD65J8",
}

NAV = [
    ("About", [
        ("New Here?", "/new-here/"),
        ("Who We Are", "/about-us/"),
        ("Our Story", "/our-story/"),
        ("Leadership", "/leadership/"),
        ("Beliefs", "/beliefs/"),
        ("Events", LINKS["events"]),
    ]),
    ("Next Steps", [
        ("Next Steps", "/next-steps/"),
        ("Water Baptism", "/water-baptism/"),
        ("Daily Reading & SOAP", "/daily/"),
        ("The Bible", "/the-bible/"),
        ("Life Groups", "/life-groups/"),
        ("RLC Connect", "/rlcconnect/"),
        ("Serve", "/serve/"),
    ]),
    ("Ministries", [
        ("Kids Life", "/kidslife/"),
        ("Student Life", "/student-life/"),
        ("Prayer", "/prayer/"),
        ("Hope Cafe", "/hope-cafe/"),
        ("Counseling Center", "/rlcc/"),
    ]),
    ("Watch", [
        ("Watch Live", "/watch-live/"),
        ("Sermon Series Archive", LINKS["youtube"]),
        ("RLC Podcast", LINKS["podcast"]),
        ("The Bible Breakdown Podcast", LINKS["bible_podcast"]),
        ("Pastor Brandon's Blog", LINKS["blog"]),
        ("Get the App", "/app/"),
    ]),
    ("Contact", "/contact/"),
]

ICONS = {
    "chev": '<svg class="chev" viewBox="0 0 12 12" aria-hidden="true"><path d="M2 4l4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "arrow": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "arrow_circle": '<svg class="arrow" viewBox="0 0 28 28" aria-hidden="true"><circle cx="14" cy="14" r="12.5" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M9 14h10M15 10l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "calendar": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="16" rx="2" fill="none" stroke="currentColor" stroke-width="2"/><path d="M3 10h18M8 3v4M16 3v4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
    "facebook": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M24 12.07C24 5.41 18.63 0 12 0S0 5.4 0 12.07C0 18.1 4.39 23.1 10.13 24v-8.44H7.08v-3.49h3.04V9.41c0-3.02 1.8-4.7 4.54-4.7 1.31 0 2.68.24 2.68.24v2.97h-1.5c-1.5 0-1.96.93-1.96 1.89v2.26h3.32l-.53 3.5h-2.8V24C19.62 23.1 24 18.1 24 12.07"/></svg>',
    "instagram": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2.16c3.2 0 3.58.01 4.85.07 1.17.05 1.8.25 2.23.41.56.22.96.48 1.38.9.42.42.68.82.9 1.38.16.42.36 1.06.41 2.23.06 1.27.07 1.65.07 4.85s-.01 3.58-.07 4.85c-.05 1.17-.25 1.8-.41 2.23-.22.56-.48.96-.9 1.38-.42.42-.82.68-1.38.9-.42.16-1.06.36-2.23.41-1.27.06-1.65.07-4.85.07s-3.58-.01-4.85-.07c-1.17-.05-1.8-.25-2.23-.41a3.7 3.7 0 0 1-1.38-.9 3.7 3.7 0 0 1-.9-1.38c-.16-.42-.36-1.06-.41-2.23C2.17 15.58 2.16 15.2 2.16 12s.01-3.58.07-4.85c.05-1.17.25-1.8.41-2.23.22-.56.48-.96.9-1.38.42-.42.82-.68 1.38-.9.42-.16 1.06-.36 2.23-.41C8.42 2.17 8.8 2.16 12 2.16M12 0C8.74 0 8.33.01 7.05.07 5.78.13 4.9.33 4.14.63c-.79.3-1.46.72-2.12 1.38A5.86 5.86 0 0 0 .63 4.14C.33 4.9.13 5.78.07 7.05.01 8.33 0 8.74 0 12s.01 3.67.07 4.95c.06 1.27.26 2.15.56 2.91.3.79.72 1.46 1.38 2.12a5.86 5.86 0 0 0 2.13 1.38c.76.3 1.64.5 2.91.56C8.33 23.99 8.74 24 12 24s3.67-.01 4.95-.07c1.27-.06 2.15-.26 2.91-.56a5.86 5.86 0 0 0 2.12-1.38 5.86 5.86 0 0 0 1.38-2.12c.3-.76.5-1.64.56-2.91.06-1.28.07-1.69.07-4.95s-.01-3.67-.07-4.95c-.06-1.27-.26-2.15-.56-2.91a5.86 5.86 0 0 0-1.38-2.13A5.86 5.86 0 0 0 19.86.63C19.1.33 18.22.13 16.95.07 15.67.01 15.26 0 12 0zm0 5.84a6.16 6.16 0 1 0 0 12.32 6.16 6.16 0 0 0 0-12.32zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.4-11.85a1.44 1.44 0 1 0 0 2.88 1.44 1.44 0 0 0 0-2.88z"/></svg>',
    "youtube": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M23.5 6.19a3.02 3.02 0 0 0-2.12-2.14C19.5 3.55 12 3.55 12 3.55s-7.5 0-9.38.5A3.02 3.02 0 0 0 .5 6.19C0 8.07 0 12 0 12s0 3.93.5 5.81a3.02 3.02 0 0 0 2.12 2.14c1.88.5 9.38.5 9.38.5s7.5 0 9.38-.5a3.02 3.02 0 0 0 2.12-2.14C24 15.93 24 12 24 12s0-3.93-.5-5.81zM9.55 15.57V8.43L15.82 12l-6.27 3.57z"/></svg>',
    "apple": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M16.37 12.6c-.02-2.4 1.96-3.56 2.05-3.62a4.42 4.42 0 0 0-3.47-1.88c-1.47-.15-2.88.87-3.63.87-.76 0-1.9-.85-3.13-.83a4.63 4.63 0 0 0-3.92 2.38c-1.68 2.9-.43 7.2 1.2 9.56.8 1.15 1.75 2.44 2.99 2.4 1.2-.05 1.66-.78 3.1-.78 1.46 0 1.86.78 3.13.75 1.3-.02 2.12-1.17 2.9-2.33a10.3 10.3 0 0 0 1.32-2.7 4.2 4.2 0 0 1-2.54-3.82zM14 5.56A4.28 4.28 0 0 0 14.98 2.5a4.36 4.36 0 0 0-2.82 1.46 4.08 4.08 0 0 0-1.01 2.96A3.6 3.6 0 0 0 14 5.56z"/></svg>',
    "play": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M3.6 1.8 13.8 12 3.6 22.2a1.6 1.6 0 0 1-.6-1.25V3.05c0-.5.22-.95.6-1.25zm11.4 11.4 2.6 2.6-11 6.3 8.4-8.9zm0-2.4L6.6 1.9l11 6.3-2.6 2.6zm3.95-1.9 3.1 1.78c.9.52.9 1.82 0 2.34l-3.1 1.78L16.2 12l2.75-2.7z"/></svg>',
    "menu": '<svg class="icon-open" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg><svg class="icon-close" style="display:none" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>',
    "kids": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="7" r="3.2" fill="none" stroke="currentColor" stroke-width="2"/><path d="M5.5 20c.6-4 3.2-6.2 6.5-6.2s5.9 2.2 6.5 6.2" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
    "group": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="8" cy="8" r="3" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="17" cy="9" r="2.4" fill="none" stroke="currentColor" stroke-width="2"/><path d="M2.5 19.5c.5-3.4 2.7-5.3 5.5-5.3s5 1.9 5.5 5.3M14.5 14.6c.8-.4 1.6-.6 2.5-.6 2.3 0 4 1.5 4.5 4.3" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
    "heart": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 20s-7.5-4.6-7.5-10.2A4.3 4.3 0 0 1 12 7.3a4.3 4.3 0 0 1 7.5 2.5C19.5 15.4 12 20 12 20z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>',
}


def link_attrs(href):
    """External links open in a new tab."""
    if href.startswith("http"):
        return f'href="{href}" target="_blank" rel="noopener"'
    return f'href="{href}"'


def render_nav(current):
    out = ['<ul class="nav-list">']
    for i, (label, target) in enumerate(NAV):
        if isinstance(target, str):
            cur = ' aria-current="page"' if target == current else ""
            out.append(f'<li class="nav-item"><a class="nav-link" href="{target}"{cur}>{label}</a></li>')
            continue
        did = f"dd-{i}"
        out.append(
            f'<li class="nav-item has-dropdown"><button class="nav-link" type="button" '
            f'aria-expanded="false" aria-controls="{did}">{label}{ICONS["chev"]}</button>'
            f'<ul class="dropdown" id="{did}">'
        )
        for sub, href in target:
            cur = ' aria-current="page"' if href == current else ""
            out.append(f"<li><a {link_attrs(href)}{cur}>{sub}</a></li>")
        out.append("</ul></li>")
    out.append("</ul>")
    return "\n".join(out)


def render_footer_cols():
    cols = []
    for label, target in NAV:
        if isinstance(target, str):
            continue
        items = "".join(f"<li><a {link_attrs(h)}>{s}</a></li>" for s, h in target)
        cols.append(f'<div class="footer-col"><h2>{label}</h2><ul>{items}</ul></div>')
    return "\n".join(cols)


def socials(cls=""):
    items = [("Facebook", "facebook"), ("Instagram", "instagram"), ("YouTube", "youtube")]
    lis = "".join(
        f'<li><a href="{LINKS[k]}" target="_blank" rel="noopener" aria-label="{n}">{ICONS[k]}</a></li>'
        for n, k in items
    )
    return f'<ul class="socials {cls}">{lis}</ul>'


CHURCH_LD = {
    "@type": "Church",
    "@id": SITE_URL + "/#church",
    "name": SITE_NAME,
    "alternateName": "RLC",
    "url": SITE_URL + "/",
    "logo": SITE_URL + "/assets/img/logo.png",
    "image": SITE_URL + "/assets/img/baptism.jpg",
    "description": "A life-giving church in Bowling Green, Kentucky that exists to make disciples by knowing God, growing in freedom, and sharing Christ in everyday life.",
    "telephone": "+1-270-681-5298",
    "email": "info@experiencerlc.com",
    "foundingDate": "2012-02-05",
    "address": {
        "@type": "PostalAddress",
        "streetAddress": "2714 Scottsville Road",
        "addressLocality": "Bowling Green",
        "addressRegion": "KY",
        "postalCode": "42104",
        "addressCountry": "US",
    },
    "openingHoursSpecification": [
        {"@type": "OpeningHoursSpecification", "dayOfWeek": "Sunday", "opens": "09:15", "closes": "12:30"},
    ],
    "sameAs": [LINKS["facebook"], LINKS["instagram"], LINKS["youtube"]],
}


def page_section(path):
    """The menu section a page sits under, e.g. ("About", "/about-us/")."""
    for label, target in NAV:
        if isinstance(target, list) and any(h == path for _, h in target):
            first_local = next((h for _, h in target if h.startswith("/")), None)
            return label, first_local
    return None


def structured_data(path, title):
    graph = [CHURCH_LD]
    if path == "/":
        graph.append({
            "@type": "WebSite",
            "@id": SITE_URL + "/#website",
            "name": SITE_NAME,
            "alternateName": ["RLC", "Experience RLC"],
            "url": SITE_URL + "/",
            "publisher": {"@id": SITE_URL + "/#church"},
        })
    else:
        crumbs = [("Home", "/")]
        sec = page_section(path)
        if sec and sec[1] and sec[1] != path:
            crumbs.append(sec)
        crumbs.append((title, path))
        graph.append({
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE_URL + u}
                for i, (n, u) in enumerate(crumbs)
            ],
        })
    data = {"@context": "https://schema.org", "@graph": graph}
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + "</script>"


LAYOUT = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{site}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_image}">
<meta name="twitter:card" content="summary_large_image">
{robots}{ld}
<meta name="theme-color" content="#153c5d">
<link rel="icon" href="/assets/img/favicon.png" sizes="32x32">
<link rel="icon" href="/assets/img/app-icon-192.png" sizes="192x192">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<link rel="manifest" href="/manifest.webmanifest">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="RLC">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/style.css">
<script>document.documentElement.classList.add('js')</script>
{head_extra}
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
  <div class="header-inner">
    <a class="brand" href="/" aria-label="Real Life Church home"><img src="/assets/img/logo.png" alt="Real Life Church" width="600" height="220"></a>
    <nav class="primary-nav" aria-label="Main">
{nav}
    </nav>
    <div class="header-actions">
      <a class="btn btn-tint btn-watch" href="/watch-live/">Watch Live</a>
      <a class="btn btn-dark" {give}>Give</a>
      <button class="menu-toggle" type="button" aria-expanded="false" aria-label="Open menu">{menu_icon}</button>
    </div>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="footer-top">
{footer_cols}
      <div class="footer-brand">
        <img src="/assets/img/logo.png" alt="Real Life Church" width="600" height="220" loading="lazy">
        <p class="tag">Making disciples by knowing God, growing in freedom, and sharing Christ in everyday life.</p>
        {socials}
      </div>
    </div>
    <div class="footer-bottom">
      <a class="btn btn-tint btn-sm" href="/contact/">Contact Us</a>
      <a href="tel:+12706815298">(270) 681-5298</a>
      <a {maps}>2714 Scottsville Road, Bowling Green, KY 42104</a>
      <span>Mail: P.O. Box 50597, Bowling Green, KY 42104</span>
      <span class="copy">&copy; <span data-year>2026</span> Real Life Church</span>
    </div>
  </div>
</footer>
<script src="/assets/js/main.js" defer></script>
<script src="/assets/js/count.js" defer></script>
<script src="/assets/js/app.js" defer></script>
</body>
</html>
"""


def relativize(html, depth):
    """Turn root-relative links ("/about-us/") into relative ones ("../about-us/")
    so the site works at any address, e.g. a GitHub Pages test URL."""
    prefix = "../" * depth

    def fix(m):
        attr, path = m.group(1), m.group(2)
        new = prefix + path if (prefix + path) else "./"
        return f'{attr}="{new}'

    return re.sub(r'\b(href|src|content)="/(?!/)([^"]*)', lambda m: fix(m) if m.group(1) != "content" or m.group(2).startswith(("assets", "prayer", "life-groups")) else m.group(0), html)


def worship_guide_parts():
    """{{announcements}} ("Get Connected" cards) for the Worship Guide page."""
    out = {"announcements": ""}
    src = SRC / "worship-guide" / "announcements.txt"
    items, cur = [], None
    for line in (src.read_text(encoding="utf-8").splitlines() if src.exists() else []):
        t = line.strip()
        if t.startswith("## "):
            cur = {"title": t[3:].strip(), "text": [], "link": None, "image": None}
            items.append(cur)
        elif not t or t.startswith("#") or cur is None:
            continue
        elif t.lower().startswith("link:"):
            label, _, url = t[5:].partition("|")
            cur["link"] = (label.strip(), url.strip())
        elif t.lower().startswith("image:"):
            cur["image"] = t[6:].strip()
        else:
            cur["text"].append(t)
    cards = []
    for it in items:
        img = f'<img src="/assets/img/{html_escape(it["image"])}" alt="" loading="lazy">' if it["image"] else ""
        btn = ""
        if it["link"]:
            label, url = it["link"]
            btn = f'<a class="btn btn-outline btn-sm" {link_attrs(url)}>{html_escape(label)}</a>'
        text = "".join(f"<p>{html_escape(t)}</p>" for t in it["text"])
        cards.append(f'      <article class="guide-card">{img}<div><h3>{html_escape(it["title"])}</h3>{text}{btn}</div></article>')
    out["announcements"] = '    <div class="guide-cards">\n' + "\n".join(cards) + "\n    </div>\n"
    return out


def html_escape(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;"))


def build():
    import build_notes  # Message Notes pages, written from _src/notes/*.txt
    entries = [
        (pg.relative_to(SRC / "pages").with_suffix("").as_posix(), pg.read_text(encoding="utf-8"))
        for pg in sorted((SRC / "pages").rglob("*.html"))
    ] + build_notes.pages()
    for slug, raw in entries:
        meta = dict(re.findall(r"<!--\s*(\w+):\s*(.*?)\s*-->", raw[:600]))
        body = re.sub(r"\A(\s*<!--.*?-->\s*)+", "", raw, flags=re.S)
        # {{link:key}} and {{icon:key}} shortcuts
        body = re.sub(r"\{\{link:(\w+)\}\}", lambda m: LINKS[m.group(1)], body)
        body = re.sub(r"\{\{icon:(\w+)\}\}", lambda m: ICONS[m.group(1)], body)
        body = body.replace("{{socials}}", socials())
        body = body.replace("{{share_icon}}", '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3v12M8 7l4-4 4 4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M6 11H5a1 1 0 0 0-1 1v8a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-8a1 1 0 0 0-1-1h-1" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>')
        if "{{announcements}}" in body:
            for k, v in worship_guide_parts().items():
                body = body.replace("{{" + k + "}}", v)
        path = "/" if slug == "index" else f"/{slug}/"
        title = meta.get("title", SITE_NAME)
        full_title = SITE_NAME + " | Bowling Green, KY" if slug == "index" else f"{title} | {SITE_NAME}"
        hero = re.search(r'class="hero-media"><img src="/(assets/img/[^"]+)"', body)
        og_image = f"{SITE_URL}/{hero.group(1) if hero else 'assets/img/baptism.jpg'}"
        html = LAYOUT.format(
            title=full_title,
            description=meta.get("description", ""),
            canonical=SITE_URL + path,
            site=SITE_NAME,
            site_url=SITE_URL,
            head_extra=meta.get("head", ""),
            og_image=og_image,
            # Message Notes stay unlisted (link only) while they're being tried out.
            robots='<meta name="robots" content="noindex">\n' if slug in ("404", "offline", "app-home") or slug.startswith(("notes", "worship-guide")) else "",
            ld="" if slug == "404" else structured_data(path, title),
            nav=render_nav(path),
            give=link_attrs(LINKS["give"]),
            menu_icon=ICONS["menu"],
            body=body.strip(),
            footer_cols=render_footer_cols(),
            socials=socials("plain"),
            maps=link_attrs(LINKS["maps"]),
        )
        if slug in ("index", "404"):
            out = ROOT / f"{slug}.html"
        else:
            out = ROOT / slug / "index.html"
        # The 404 page is shown at any address, so it keeps site-root links.
        # "<!-- layout: bare -->": no site header/footer (pages shown inside the RLC app,
        # which has its own top bar and tabs).
        if meta.get("layout") == "bare":
            html = re.sub(r'<a class="skip-link".*?</a>\n', "", html)
            html = re.sub(r'<header class="site-header">.*?</header>\n', "", html, flags=re.S)
            html = re.sub(r'<footer class="site-footer">.*?</footer>\n', "", html, flags=re.S)
            html = html.replace("<body>", '<body class="bare">', 1)
        if slug != "404":
            html = relativize(html, len(out.relative_to(ROOT).parts) - 1)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8")
        print("built", out.relative_to(ROOT))

    # Sitemap for search engines.
    slugs = [sl for sl, _ in entries if sl not in ("offline", "app-home") and not sl.startswith(("notes", "worship-guide"))]
    urls = ["/" if sl == "index" else f"/{sl}/" for sl in slugs if sl != "404"]
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{SITE_URL}{u}</loc><lastmod>{date.today().isoformat()}</lastmod></url>\n" for u in urls)
        + "</urlset>\n",
        encoding="utf-8",
    )
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /preview/\nDisallow: /_src/\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")

    # Old WordPress URLs that moved.
    redirects = {
        "prayer-2": "/prayer/",
        "weekly-guide": "/worship-guide/",
        "commonly-asked-questions": "/life-groups/#questions",
    }
    for old, new in redirects.items():
        out = ROOT / old / "index.html"
        canonical = SITE_URL + new if new.startswith("/") else new
        if new.startswith("/"):
            new = "../" + new.lstrip("/")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            f'<!doctype html><meta charset="utf-8"><title>Redirecting…</title><meta name="robots" content="noindex">'
            f'<meta http-equiv="refresh" content="0; url={new}"><link rel="canonical" href="{canonical}">'
            f'<a href="{new}">Continue</a>\n',
            encoding="utf-8",
        )
        print("redirect", old, "->", new)


if __name__ == "__main__":
    build()
    # Keep the preview/ copy (for raw.githack.com test links) in sync.
    import make_preview  # noqa: E402,F401  (runs on import)
