#!/usr/bin/env python3
"""Links each day of the reading plan to its Bible Breakdown podcast episode
and YouTube video, and saves them to daily/data/media.json.

Runs every day from GitHub Actions (.github/workflows/update-media.yml), and
can be run by hand:  python3 _src/update_media.py

Matching: an episode or video belongs to a day when its title starts with that
day's chapter ("Psalm 124: How to Give a Proper Testimony") and it was
published within a few days of that date. YouTube #shorts are skipped.
Links found earlier are kept, so older days stay linked after they drop off
the YouTube feed (which only lists the latest 15 videos).
"""
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
    ok = True
    for kind, source in (("podcast", podcast_items), ("youtube", youtube_items)):
        try:
            n = match(plan, list(source()), kind, media)
            print(f"{kind}: {n} days linked")
        except Exception as err:  # keep going; one source failing shouldn't wipe the other
            print(f"{kind}: could not update ({err})", file=sys.stderr)
            ok = False
    after = json.dumps(media, sort_keys=True)
    if after != before:
        out.write_text(json.dumps(dict(sorted(media.items())), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print("media.json updated")
    else:
        print("no changes")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
