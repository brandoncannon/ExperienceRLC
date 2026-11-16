#!/usr/bin/env python3
"""Pulls Brandon's published SOAPs from cannonstudybible.com (Obsidian Publish)
into daily/data/soaps/YYYY-MM.json, so the Daily Reading page shows them
without anyone pasting them in.

Runs from GitHub Actions (.github/workflows/update-media.yml) and can be run
by hand:  python3 _src/sync_soaps.py

How it works: for every reading-plan day from a week ago to two months ahead,
it looks for a published note in the vault's SOAP folder for that day's
chapter (e.g. "SOAP/Psalm 125- SOAP.md"). Only notes Brandon has published in
Obsidian are visible, so nothing private leaks. Missing days are filled in.
Today and future days are refreshed if the published note changed, so a fix
in Obsidian flows through. Past days are never overwritten.
"""
import json
import re
import sys
import urllib.parse
import urllib.request
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "daily" / "data"
SITE_ID = "a865df31454911586d9bec7383349455"
PUBLISH = f"https://publish-01.obsidian.md"
SITE_URL = "https://cannonstudybible.com"
BACK, AHEAD = timedelta(days=7), timedelta(days=62)
DIRECTION_MARKS = re.compile("[‎‏‪-‮⁦-⁩]")


def chapter_key(text):
    """'Psalm 125- SOAP.md' / 'Psalms 125' / 'Jeremiah 07 - SOAP' -> 'psalm 125'."""
    m = re.match(r"^\s*([1-3]?\s*[A-Za-z][A-Za-z ]*?)\s*0*(\d+)\b", text or "")
    if not m:
        return None
    book = re.sub(r"\s+", " ", m.group(1)).strip().lower()
    book = {"psalms": "psalm", "song of solomon": "song of songs"}.get(book, book)
    return f"{book} {int(m.group(2))}"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "experiencerlc-daily-sync"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def published_soaps():
    """chapter key -> vault path, for every published note in the SOAP folder."""
    files = json.loads(get(f"{PUBLISH}/cache/{SITE_ID}"))
    out = {}
    for path in files:
        if path.startswith("SOAP/") and path.endswith(".md") and "SOAP" in path[5:]:
            key = chapter_key(path[5:])
            if key:
                out.setdefault(key, path)
    return out


def section(body, name):
    m = re.search(rf"^##\s*{name}:?\s*\n(.*?)(?=^##\s|\Z)", body, re.S | re.M)
    if not m:
        return ""
    text = m.group(1).strip()
    # Paragraphs: keep blank-line breaks, join wrapped lines.
    paras = [re.sub(r"\s*\n\s*", " ", p).strip() for p in re.split(r"\n\s*\n", text)]
    return "\n\n".join(p for p in paras if p)


def parse(md, chapter):
    md = DIRECTION_MARKS.sub("", md)
    fm, body = {}, md
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", md, re.S)
    if m:
        body = m.group(2)
        for line in m.group(1).splitlines():
            kv = re.match(r"^(\w+):\s*(.*)$", line)
            if kv:
                fm[kv.group(1).lower()] = kv.group(2).strip().strip('"')
    title = fm.get("title") or ""
    if not title:
        t = re.search(r"^##\s*Title:\s*(.+)$", body, re.M)
        title = t.group(1).strip() if t else ""
    scripture = section(body, "Scripture")
    ref, verse = "", scripture
    # (Psalm 123:1) “Text.” (NET)
    m = re.match(r"^\((.+?)\)\s*(.*?)\s*(?:\((?:NET)\))?$", scripture, re.S)
    if m:
        ref, verse = m.group(1).strip(), m.group(2).strip()
    else:
        # “Text.” Psalms 126:5-6 (NET)
        m = re.match(r"^(.*?)[\s]*((?:[1-3]\s*)?[A-Za-z][A-Za-z ]+\s+\d+:[\d\-–,: ]+)\s*(?:\(NET\))?$", scripture, re.S)
        if m:
            verse, ref = m.group(1).strip(), re.sub(r"\s+", " ", m.group(2)).strip()
    ref = re.sub(r"^Psalms (\d+:)", r"Psalm \1", ref)
    ref = re.sub(r":0+(\d)", r":\1", ref)
    verse = verse.strip()
    if len(verse) >= 2 and verse[0] in "“\"" and verse[-1] in "”\"":
        verse = verse[1:-1].strip()
    entry = {
        "title": title,
        "chapter": chapter,
        "source": f"{SITE_URL}/{fm['permalink'].strip('/')}" if fm.get("permalink") else "",
        "verseRef": ref,
        "verse": verse,
        "version": "NET",
        "observation": section(body, "Observation"),
        "application": section(body, "Application"),
        "prayer": section(body, "Prayer"),
    }
    if not entry["source"]:
        del entry["source"]
    # Only a finished SOAP goes on the church site.
    if not (entry["title"] and entry["observation"] and entry["application"] and entry["prayer"]):
        return None
    if entry["prayer"].rstrip(" .") in ("Thank You, Jesus, for", "Thank You, Jesus"):
        return None
    return entry


def main():
    plan = json.loads((DATA / "reading-plan.json").read_text())
    today = date.today()
    lo, hi = (today - BACK).isoformat(), (today + AHEAD).isoformat()
    try:
        soaps = published_soaps()
    except Exception as e:  # The site being down should never break the page.
        print(f"Could not reach the published site: {e}")
        return 0
    months, changed = {}, set()
    for day in sorted(plan):
        if not (lo <= day <= hi):
            continue
        passages = plan[day].get("passages") or []
        if not passages:
            continue
        chapter = passages[0]
        path = soaps.get(chapter_key(chapter))
        if not path:
            continue
        month = day[:7]
        if month not in months:
            f = DATA / "soaps" / f"{month}.json"
            months[month] = json.loads(f.read_text()) if f.exists() else {}
        existing = months[month].get(day)
        if existing and day < today.isoformat():
            continue
        try:
            entry = parse(get(f"{PUBLISH}/access/{SITE_ID}/{urllib.parse.quote(path)}"), chapter)
        except Exception as e:
            print(f"{day} {chapter}: could not read {path}: {e}")
            continue
        if not entry or entry == existing:
            continue
        months[month][day] = entry
        changed.add(month)
        print(f"{'Updated' if existing else 'Added'} {day}: {chapter} – {entry['title']}")
    for month in sorted(changed):
        data = dict(sorted(months[month].items()))
        (DATA / "soaps" / f"{month}.json").write_text(json.dumps(data, ensure_ascii=False, indent=1))
    if not changed:
        print("No new SOAPs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
