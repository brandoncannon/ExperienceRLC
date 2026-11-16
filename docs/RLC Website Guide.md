---
title: RLC Website Guide
tags: [rlc, website, how-to]
updated: 2026-11-16
---

# RLC Website Guide

> [!summary] The short version
> The website lives on **GitHub** (free hosting). The domain and email stay at **GoDaddy**. To change the website, start a **Claude Code** session with the `brandoncannon/ExperienceRLC` repository and say what you want changed. Merge the pull request it opens, and the change is live in a few minutes.

---

## Where everything is

| What | Where |
|---|---|
| Live website | https://www.experiencerlc.com |
| Daily Reading & SOAP | https://www.experiencerlc.com/daily/ |
| Past SOAPs | https://www.experiencerlc.com/daily/archive/ |
| Website code (GitHub repo) | https://github.com/brandoncannon/ExperienceRLC |
| Branch that is the live site | `gh-pages` |
| GitHub Pages settings | https://github.com/brandoncannon/ExperienceRLC/settings/pages |
| Pull requests (changes waiting to go live) | https://github.com/brandoncannon/ExperienceRLC/pulls |
| Domain & DNS (GoDaddy) | https://dcc.godaddy.com/control/portfolio → experiencerlc.com → DNS |
| Email (pastor@, info@) | Microsoft 365, bought through GoDaddy. Separate from the website. |
| Google Search Console | https://search.google.com/search-console |
| Google Business Profile | https://business.google.com |
| Make changes with Claude | https://claude.ai/code |

### Things the website links to (update these in their own apps)
These change often, so they live in other tools, and the website just links to them. Updating them there updates the site automatically.

- **Events & RLC Connect sign-ups:** Church Center → https://experiencerlc.churchcenter.com/registrations/events
- **LifeGroups:** Church Center → https://experiencerlc.churchcenter.com/groups
- **Connect card / prayer requests:** Church Center form
- **Giving:** Tithe.ly
- **Sermons:** YouTube (youtube.com/myreallifechurch) and the RLC Podcast
- **Weekly worship guide, notes:** RLC app (Subsplash)
- **Counseling intake:** Google Form

---

## How to make a change

### The easy way: ask Claude
1. Go to **https://claude.ai/code** and start a new session.
2. Pick the repository **brandoncannon/ExperienceRLC**.
3. Say what you want in plain English. Examples:
   - "Change Sunday service times to 9:00 and 10:45 everywhere on the site."
   - "Add Jane Smith as Youth Pastor on the Leadership page. Here's her photo." *(attach the photo)*
   - "Put a Christmas Eve service banner at the top of the homepage."
   - "Replace the top photo on the Prayer page with this one."
   - "Add SOAPs for these dates to the daily reading." *(paste them in)*
4. Claude makes the change, checks it, and gives you a **test link** to look at.
5. When you're happy, say **"open the pull request."**
6. Open the link, click **Merge pull request** → **Confirm merge**.
7. The live site updates within about **2–5 minutes**.

> [!tip]
> Nothing goes live until you click **Merge**. Test links are safe to share for feedback first.

### Doing it yourself (only for someone comfortable with code)
- Page text lives in `_src/pages/` (one file per page; `leadership.html` → `/leadership/`).
- The menu, footer and shared links (giving, app, social) are at the top of `_src/build.py`.
- Colors are at the top of `assets/css/style.css`. Photos are in `assets/img/`.
- After editing, run `python3 _src/build.py` to rebuild the pages, then commit.
- Editing the finished `index.html` files directly on GitHub works for a quick typo fix, but the next rebuild overwrites it. Fix the `_src/` file too.

---

## Daily Reading & SOAP

- Shows the day's Bible Breakdown chapter (NLT) and that day's SOAP, based on the visitor's date.
- **Reading plan:** `daily/data/reading-plan.json`
- **SOAPs:** `daily/data/soaps/YYYY-MM.json` (one file per month, one entry per date)
- A date with no SOAP shows "coming soon." Future SOAPs never show early, so you can load them ahead.
- **Your Turn:** under each SOAP, readers can write their own SOAP. It autosaves on their device (never sent to the church), and **Email it to me** opens their own email app with the entry ready to send; **Copy** pastes it anywhere.
- **Go deeper:** a link to that day's post on thebiblebreakdown.com, found the same way (posts whose title starts with the chapter). Re-run chapters with no new post link to that chapter's most recent post.
- **Listen / Watch buttons:** each day links to that day's Bible Breakdown podcast episode and YouTube video. A GitHub job finds new episodes automatically (about 5 AM, noon and 6 PM Central). Nothing to do; if an episode is posted with a title that doesn't start with the chapter (e.g. "Psalm 125: …"), it won't be matched, and the button falls back to the podcast page / a YouTube search. To check right away: GitHub → **Actions** → *Update daily podcast & video links* → **Run workflow**.
- **NLT API key:** `assets/js/daily-config.js` (from api.nlt.to). It's meant to be public.
- Easiest: paste new SOAPs into a Claude session and ask it to add them.

---

## Domain & email settings (GoDaddy DNS)

> [!warning] Never change or delete the **MX** or **TXT** records. They run the email.

| Type | Name | Value | Purpose |
|---|---|---|---|
| A | @ | 185.199.108.153 | GitHub (website) |
| A | @ | 185.199.109.153 | GitHub (website) |
| A | @ | 185.199.110.153 | GitHub (website) |
| A | @ | 185.199.111.153 | GitHub (website) |
| CNAME | www | brandoncannon.github.io | Sends www to GitHub |
| MX | @ | experiencerlc-com.mail.protection.outlook.com | **Email** (Microsoft 365) |
| TXT | @ | `v=spf1 include:spf.protection.outlook.com -all` and others | **Email security** + Google verification |
| CNAME | autodiscover | autodiscover.outlook.com | Outlook setup |
| A | mail | 107.180.28.113 | Old, unused; harmless |

---

## Launch checklist

- [x] New site merged into `gh-pages` (Nov 15, 2026)
- [x] GitHub Pages set to `gh-pages` / root, custom domain `www.experiencerlc.com`
- [x] GoDaddy A records switched to GitHub (Nov 15, 2026)
- [x] Security certificate (padlock) issued by GitHub (Nov 16, 2026)
- [ ] GitHub Pages: tick **Enforce HTTPS** (Settings → Pages)
- [ ] Send a test email to pastor@experiencerlc.com and info@experiencerlc.com
- [x] Google Search Console → **Sitemaps** → submitted `https://www.experiencerlc.com/sitemap.xml` (Nov 16, 2026)
- [ ] Google Business Profile: check name, address, phone, service times and website link
- [ ] Around **Dec 15, 2026**: cancel the GoDaddy **hosting** plan (WordPress). **Keep** the domain and Microsoft 365 email.
- [ ] Optional cleanup (ask Claude): delete the `preview/` test folder and the old `claude/daily-bible-devotion-site-6146k3` branch

### Submitting the sitemap to Google
1. On a computer, open https://search.google.com/search-console and sign in.
2. Top left: pick **experiencerlc.com** (if missing, add it as a **Domain** property and verify with the TXT record Google gives you).
3. Left menu → **Sitemaps**.
4. Type the full address `https://www.experiencerlc.com/sitemap.xml` → **Submit**. (Typing only `sitemap.xml` gives "Invalid sitemap address".) It should say **Success** (can take a day).
5. Optional: paste `https://www.experiencerlc.com/` in the top search bar → **Request indexing**.

---

## If something goes wrong

- **Site shows the old WordPress site:** DNS hasn't caught up yet. Wait an hour. Check the A records above.
- **"Your connection is not private":** GitHub's security certificate isn't ready yet (can take up to a day after DNS changes). Then tick **Enforce HTTPS** in Pages settings.
- **A change didn't show up:** Did the pull request get **merged**? Then wait 5 minutes and refresh (or open in a private window).
- **Email stopped:** Check that the **MX** record still points to `...mail.protection.outlook.com`.
- **Anything else:** Start a Claude Code session with the repo and describe what you see.

---

## Site facts

- **Pages:** Home, New Here, Who We Are, Our Story, Leadership, Beliefs, Next Steps, Water Baptism, Daily Reading & SOAP, The Bible, LifeGroups, RLC Connect, Serve, KidsLife, Student Life, Prayer, Hope Cafe, Counseling Center, Watch Live, Give, Contact
- **Colors:** navy #153C5D · steel blue #5B8DAE · slate #5E7887 · aqua #9ECBD1 · cream #E8DFCE · charcoal #4D4D4D · white
- **Font:** Figtree (Lora for Scripture on the daily page)
- **Old WordPress addresses** like `/new-here/` and `/leadership/` still work. `/prayer-2/` forwards to `/prayer/`.
