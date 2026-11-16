# Real Life Church website

The website for [Real Life Church](https://www.experiencerlc.com) in Bowling Green, KY. It's a plain static site (HTML, CSS and a little JavaScript), so it can be hosted anywhere: GitHub Pages, Netlify, Cloudflare Pages, or any web host.

## Editing pages

Don't edit the generated `*/index.html` files directly. Edit the source and rebuild:

- **Page content** lives in `_src/pages/`, one file per page. `new-here.html` becomes `/new-here/`.
- **Menu, footer, and shared links** (giving, app, social media, Church Center) are at the top of `_src/build.py`.
- **Styles** are in `assets/css/style.css`. Brand colors are the variables at the top.
- **Photos** are in `assets/img/`.

Then rebuild (needs Python 3, nothing to install):

```sh
python3 _src/build.py
```

Preview locally:

```sh
python3 -m http.server 8000
# open http://localhost:8000
```

## URLs

Page addresses match the old WordPress site (`/new-here/`, `/leadership/`, `/kidslife/` and so on) so existing links and search results keep working. `/prayer-2/` now redirects to `/prayer/`.

## Daily Reading & SOAP (`/daily/`)

`/daily/` shows today's Bible Breakdown chapter (in the NLT, from Tyndale's NLT API) and that day's SOAP devotion. Readers can step back through earlier days, and `/daily/archive/` lists past SOAPs. It works from the visitor's own date, so nothing needs updating day to day as long as entries are written ahead.

- **Reading plan:** `daily/data/reading-plan.json`, one entry per date.
- **SOAPs:** `daily/data/soaps/YYYY-MM.json`, one file per month, keyed by date:
  ```json
  "2026-11-22": {
    "title": "Your devotion title",
    "verseRef": "1 Peter 1:3",
    "verse": "The key verse text...",
    "version": "NET",
    "observation": "...",
    "application": "...",
    "prayer": "..."
  }
  ```
  These are filled in automatically from SOAPs published on cannonstudybible.com by `_src/sync_soaps.py` (`.github/workflows/sync-soaps.yml`, every two hours). Use `\n\n` for a new paragraph inside a field. A date without an entry shows "coming soon"; future dates never show early.
- **Backup Bible text:** `daily/data/bible/` (World English Bible, public domain), used only if the NLT can't load.
- **Podcast, YouTube & blog links:** `daily/data/media.json`, filled in automatically three times a day by the GitHub Action in `.github/workflows/update-media.yml` (it runs `_src/update_media.py`). It matches each day's chapter to the episode/video whose title starts with that chapter. To run it right away: GitHub → **Actions** → *Update daily podcast & video links* → **Run workflow**.
- **Settings:** `assets/js/daily-config.js` (author name, NLT API key, translation for the "read in another translation" link).
