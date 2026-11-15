# ExperienceRLC
We are a life-giving church located in Bowling Green Ky. Welcome Home.

## Daily Bible Breakdown + SOAP site

The home page (`index.html`) automatically shows **today's** Bible Breakdown reading
(with links to BibleGateway) and **today's SOAP** devotion, based on the visitor's date.
Readers can step back through previous days, and `archive.html` lists past SOAPs.

### Where the content comes from

- `data/reading-plan.json` holds the 2026–2027 SOAP Bible Reading Plan (from the Google Docs),
  one chapter per day with Catch-Up Days on the 15th and 30th.
- `data/soaps/` holds the SOAPs from cannonstudybible.com, one file per month, keyed by date.
  Days whose chapter has no SOAP yet show "coming soon."

### Adding content

1. **Reading plan** — add a line per day to `data/reading-plan.json`:
   ```json
   "2026-11-22": { "passages": ["Psalm 131"] }
   ```
2. **SOAP** — add an entry keyed by date to that month's file, `data/soaps/YYYY-MM.json`:
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
   To start a new paragraph inside a field, type `\n\n` (JSON text has to stay on one line).

Write entries ahead of time — each one appears on its date. Future dates
never show early. A day with no SOAP shows "coming soon."

Settings (author name, Bible version) are in `assets/config.js`.

### Hosting
Turn on GitHub Pages: repo **Settings → Pages → Deploy from branch → `gh-pages` / root**.
