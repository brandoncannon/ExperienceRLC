#!/usr/bin/env python3
"""Pull SOAPs from cannonstudybible.com (Obsidian Publish) into data/soaps/YYYY-MM.json.

For every reading day in data/reading-plan.json, finds the matching
"SOAP/<Book> <NN>- SOAP.md" note, converts it, and writes one JSON file per month.
Prints what changed and which upcoming reading days still have no SOAP.

Usage:  python3 scripts/update_soaps.py [--days-ahead 14]
Only uses the Python standard library.
"""
import argparse
import collections
import concurrent.futures
import datetime
import json
import os
import re
import sys
import urllib.parse
import urllib.request

SITE_UID = "a865df31454911586d9bec7383349455"
HOST = "https://publish-01.obsidian.md"
SITE_URL = "https://cannonstudybible.com/"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAN = os.path.join(ROOT, "data", "reading-plan.json")
SOAPS = os.path.join(ROOT, "data", "soaps")
UA = {"User-Agent": "curl/8.5.0"}


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def note_index():
    """Map (book, chapter) -> note path for every SOAP note on the site."""
    cache = json.loads(get(f"{HOST}/cache/{SITE_UID}"))
    found = {}
    for path in cache:
        m = re.match(r"SOAP/(.+?) (\d+)\s*-\s*SOAP\.md$", path)
        if m:
            book = m.group(1)
            if book == "Psalms":
                book = "Psalm"
            found[(book, int(m.group(2)))] = path
    return found


def clean(text):
    text = re.sub(r"\[\[([^\]|]+\|)?([^\]]+)\]\]", r"\2", text)          # [[wikilinks]]
    text = re.sub(r"(?m)^\s*#\w[\w/-]*(\s+#\w[\w/-]*)*\s*$", "", text)    # tag-only lines
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)                         # **bold**
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def convert(raw, ref):
    """Turn one SOAP note's markdown into the site's JSON shape (or None if empty)."""
    front = {}
    m = re.match(r"---\n(.*?)\n---\n", raw, re.S)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line and not line.startswith(" "):
                k, v = line.split(":", 1)
                front[k.strip()] = v.strip().strip('"')
        raw = raw[m.end():]
    sections, cur = {}, None
    for line in raw.splitlines():
        h = re.match(r"#{1,6}\s*(Title|Scripture|Observation|Application|Prayer)\s*:?\s*(.*)$", line, re.I)
        if h:
            cur = h.group(1).lower()
            sections[cur] = [h.group(2)] if h.group(2) else []
        elif cur:
            sections[cur].append(line)
    sections = {k: clean("\n".join(v)) for k, v in sections.items()}

    out = {
        "title": front.get("title") or sections.get("title") or f"{ref} SOAP",
        "chapter": ref,
        "source": SITE_URL + front["permalink"] if front.get("permalink") else None,
    }
    scripture = sections.get("scripture", "")
    sm = re.match(r"\(([^)]+)\)\s*(.+?)\s*(\((NET|NIV|NLT|ESV|KJV|CSB|NKJV)\))?\s*$", scripture, re.S)
    if sm:
        out["verseRef"] = sm.group(1).strip()
        out["verse"] = sm.group(2).strip().strip("“”\"").strip()
        if sm.group(4):
            out["version"] = sm.group(4)
    elif scripture:
        out["scripture"] = scripture
    for k in ("observation", "application", "prayer"):
        if sections.get(k):
            out[k] = sections[k]
    if not (out.get("observation") or out.get("verse") or out.get("scripture")):
        return None  # empty template or not a SOAP
    return {k: v for k, v in out.items() if v}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days-ahead", type=int, default=14)
    args = ap.parse_args()

    plan = json.load(open(PLAN, encoding="utf-8"))
    notes = note_index()

    wanted = {}  # date -> (ref, note path)
    for date, day in plan.items():
        for ref in day.get("passages", []):
            book, ch = ref.rsplit(" ", 1)
            path = notes.get((book, int(ch)))
            if path:
                wanted[date] = (ref, path)

    paths = sorted({p for _, p in wanted.values()})
    with concurrent.futures.ThreadPoolExecutor(4) as ex:
        bodies = dict(zip(paths, ex.map(lambda p: get(f"{HOST}/access/{SITE_UID}/" + urllib.parse.quote(p)), paths)))

    months = collections.defaultdict(dict)
    for date, (ref, path) in sorted(wanted.items()):
        soap = convert(bodies[path], ref)
        if soap:
            months[date[:7]][date] = soap

    # Write month files and report what changed.
    added, edited = [], []
    os.makedirs(SOAPS, exist_ok=True)
    for month in sorted({d[:7] for d in plan}):
        fn = os.path.join(SOAPS, f"{month}.json")
        old = json.load(open(fn, encoding="utf-8")) if os.path.exists(fn) else {}
        new = months.get(month, {})
        for d in new:
            if d not in old:
                added.append(d)
            elif new[d] != old[d]:
                edited.append(d)
        if new != old:
            with open(fn, "w", encoding="utf-8") as f:
                json.dump(new, f, ensure_ascii=False, indent=1)

    def label(d):
        return f"{d} {plan[d]['passages'][0]}: {months[d[:7]][d]['title']}"

    print(f"New SOAPs: {len(added)}")
    for d in added:
        print("  +", label(d))
    print(f"Edited SOAPs: {len(edited)}")
    for d in edited:
        print("  ~", label(d))

    today = datetime.date.today()
    horizon = today + datetime.timedelta(days=args.days_ahead)
    missing = [
        f"{d} {plan[d]['passages'][0]}"
        for d in sorted(plan)
        if plan[d].get("passages") and today.isoformat() <= d <= horizon.isoformat() and d not in months.get(d[:7], {})
    ]
    print(f"Reading days in the next {args.days_ahead} days with no SOAP yet: {len(missing)}")
    for m in missing:
        print("  -", m)
    return 0


if __name__ == "__main__":
    sys.exit(main())
