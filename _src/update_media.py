#!/usr/bin/env python3
"""Links each day of the reading plan to its Bible Breakdown podcast episode,
YouTube video and blog post, and saves them to daily/data/media.json.

Runs every day from GitHub Actions (.github/workflows/update-media.yml), and
can be run by hand:  python3 _src/update_media.py

Matching: an episode, blog post or video belongs to a day when its title starts with that
day's chapter ("Psalm 124: How to Give a Proper Testimony") and it was
published within a few days of that date. YouTube #shorts are skipped.
Links found earlier are kept, so older days stay linked after they drop off
the YouTube feed (which only lists the latest 15 videos).
"""
import html
import json
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "daily" / "data"
PODCAST_FEED = "https://feeds.buzzsprout.com/2164615.rss"
PODCAST_EPISODE = "https://www.buzzsprout.com/2164615/episodes/{id}"
YOUTUBE_FEED = "https://www.youtube.com/feeds/videos.xml?channel_id=UCZSvvJuCTZvoYPzAGowiYjQ"
BLOG_FEED = "https://www.thebiblebreakdown.com/rss/"
BLOG_SITEMAP = "https://www.thebiblebreakdown.com/sitemap-posts.xml"
# How far from the plan date a release can be and still count as that day's.
EARLY, LATE = timedelta(days=2), timedelta(days=7)


def chapter_key(text):
    """'Psalm 124: How to…' / 'Psalms 124' / 'John07 Round Two' -> 'psalm 124'."""
    m = re.match(r"^\s*([1-3]?\s*[A-Za-z][A-Za-z ]*?)\s*0*(\d+)\b", text or "")
    if not m:
        return None
    book = re.sub(r"\s+", "", m.group(1).lower())
    book = {"psalms": "psalm", "songofsongs": "songofsolomon"}.get(book, book)
    return f"{book} {int(m.group(2))}"


def fetch(url, attempts=5):
    """YouTube's feed sometimes answers 404/500 for a moment, so retry."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (RLC website media updater)"})
    for i in range(attempts):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except Exception:
            if i == attempts - 1:
                raise
            time.sleep(5 * (i + 1))


def podcast_items():
    root = ET.fromstring(fetch(PODCAST_FEED))
    for it in root.findall("./channel/item"):
        title = (it.findtext("title") or "").strip()
        guid = it.findtext("guid") or ""
        m = re.search(r"(\d+)$", guid)
        if not m or not it.findtext("pubDate"):
            continue
        day = parsedate_to_datetime(it.findtext("pubDate")).date()
        yield chapter_key(title), day, title, PODCAST_EPISODE.format(id=m.group(1))


def youtube_items():
    ns = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015"}
    root = ET.fromstring(fetch(YOUTUBE_FEED))
    for e in root.findall("a:entry", ns):
        title = (e.findtext("a:title", namespaces=ns) or "").strip()
        vid = e.findtext("yt:videoId", namespaces=ns)
        if not vid or "#shorts" in title.lower():
            continue
        # Feed times are UTC; shift to US Central so evening uploads keep their date.
        published = datetime.fromisoformat(e.findtext("a:published", namespaces=ns).replace("Z", "+00:00"))
        day = (published - timedelta(hours=6)).date()
        yield chapter_key(title), day, title, f"https://www.youtube.com/watch?v={vid}"


def blog_items():
    """Latest 15 Bible Breakdown blog posts (Ghost's feed doesn't go further back)."""
    root = ET.fromstring(fetch(BLOG_FEED))
    for it in root.findall("./channel/item"):
        title, link = (it.findtext("title") or "").strip(), (it.findtext("link") or "").strip()
        if not link or not it.findtext("pubDate"):
            continue
        day = (parsedate_to_datetime(it.findtext("pubDate")) - timedelta(hours=6)).date()
        yield chapter_key(title), day, title, link


def blog_backfill_items(plan, media, since):
    """Older posts: find candidates in the sitemap by the chapter at the start of
    the address (/podcast/psalm-125-...), then read each post's real publish date."""
    wanted = set()
    today = date.today()
    for day_str, entry in plan.items():
        d = date.fromisoformat(day_str)
        passages = entry.get("passages", []) if isinstance(entry, dict) else entry
        if passages and since <= d <= today and "blog" not in media.get(day_str, {}):
            wanted.add(chapter_key(passages[0]))
    if not wanted:
        return
    urls = re.findall(r"<loc>([^<]+/podcast/[^<]+)</loc>", fetch(BLOG_SITEMAP).decode("utf-8", "replace"))
    for url in urls:
        slug = url.rstrip("/").rsplit("/", 1)[-1]
        key = chapter_key(slug.replace("-", " "))
        if key not in wanted:
            continue
        try:
            page = fetch(url, attempts=2).decode("utf-8", "replace")
        except Exception:
            continue
        when = re.search(r'article:published_time" content="([^"]+)"', page)
        # The visible headline; a post's <title> can differ (custom SEO titles).
        title = re.search(r"<h1[^>]*>(.*?)</h1>", page, re.S) or re.search(r"<title>([^<]+)</title>", page)
        if not when:
            continue
        day = (datetime.fromisoformat(when.group(1).replace("Z", "+00:00")) - timedelta(hours=6)).date()
        t = html.unescape(re.sub(r"<[^>]+>", "", title.group(1))).strip() if title else slug
        # A copied post can keep its old address; the headline is what readers see.
        if chapter_key(t):
            key = chapter_key(t)
        yield key, day, t, url


def match(plan, items, kind, media):
    by_chapter = {}
    for key, day, title, url in items:
        if key:
            by_chapter.setdefault(key, []).append((day, title, url))
    found = 0
    for day_str, entry in plan.items():
        passages = entry.get("passages", []) if isinstance(entry, dict) else entry
        if not passages:
            continue
        key = chapter_key(passages[0])
        plan_day = date.fromisoformat(day_str)
        candidates = [
            (abs((d - plan_day).days), title, url)
            for d, title, url in by_chapter.get(key, [])
            if plan_day - EARLY <= d <= plan_day + LATE
        ]
        if candidates:
            _, title, url = min(candidates)
            media.setdefault(day_str, {})[kind] = {"title": title, "url": url}
            found += 1
    return found


def main():
    plan = json.loads((DATA / "reading-plan.json").read_text(encoding="utf-8"))
    out = DATA / "media.json"
    media = json.loads(out.read_text(encoding="utf-8")) if out.exists() else {}
    before = json.dumps(media, sort_keys=True)
    failed, worked = [], 0
    # Normally only recent days are rechecked against the blog's post pages;
    # "--backfill" looks back over the whole year.
    since = date(date.today().year, 1, 1) if "--backfill" in sys.argv else date.today() - timedelta(days=10)
    sources = (
        ("podcast", podcast_items),
        ("youtube", youtube_items),
        ("blog", blog_items),
    )
    backfill = []
    for kind, source in sources:
        try:
            n = match(plan, list(source()), kind, media)
            print(f"{kind}: {n} days linked")
            worked += 1
        except Exception as err:  # keep going; one source failing shouldn't wipe the other
            print(f"{kind}: could not update ({err})", file=sys.stderr)
            failed.append(kind)
    # Blog posts for older days, read from each post's page.
    try:
        backfill = list(blog_backfill_items(plan, media, since))
        n = match(plan, backfill, "blog", media)
        # Re-run chapters ("Round Two" episodes) may have no new blog post that year;
        # link that chapter's most recent post instead. A dated post replaces it later.
        latest = {}
        for key, d, title, url in backfill:
            if key and (key not in latest or d > latest[key][0]):
                latest[key] = (d, title, url)
        older = 0
        for day_str, entry in plan.items():
            passages = entry.get("passages", []) if isinstance(entry, dict) else entry
            d = date.fromisoformat(day_str)
            if passages and since <= d < date.today() and "blog" not in media.get(day_str, {}):
                hit = latest.get(chapter_key(passages[0]))
                if hit and hit[0] < d:
                    media.setdefault(day_str, {})["blog"] = {"title": hit[1], "url": hit[2]}
                    older += 1
        print(f"blog (post pages): {n} days linked, {older} linked to an earlier post")
    except Exception as err:
        print(f"blog backfill: could not update ({err})", file=sys.stderr)
        failed.append("blog backfill")

    after = json.dumps(media, sort_keys=True)
    if after != before:
        out.write_text(json.dumps(dict(sorted(media.items())), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print("media.json updated")
    else:
        print("no changes")
    # A short outage at one site (YouTube answering 503, say) is only a warning:
    # the other links are still saved, and the next run (a few hours later)
    # picks up what was missed. Fail only when nothing could be reached.
    if failed:
        print(f"::warning::Could not reach {', '.join(failed)} this run; the next run will try again.")
    return 0 if worked else 1


if __name__ == "__main__":
    sys.exit(main())
