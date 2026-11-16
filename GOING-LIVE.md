# Moving experiencerlc.com from WordPress to this site

Your domain stays at GoDaddy. The website moves to GitHub Pages (free, with free HTTPS). Every change pushed to the `gh-pages` branch goes live within a few minutes.

## Before you start

1. **Back up WordPress.** In GoDaddy, open your hosting (cPanel) and use **Backup** or **File Manager** to download the site files and database. Keep this so nothing is lost.
2. **Find out where your email lives.** In GoDaddy, go to **Domains → experiencerlc.com → DNS** and look at the **MX** records (the "Value" or "Points to" column):
   - `...mail.protection.outlook.com` → Microsoft 365 (often sold by GoDaddy as "Professional Email" or "Microsoft 365 from GoDaddy"). **Safe**, not affected.
   - `...secureserver.net` → GoDaddy Workspace Email. **Safe**, not affected.
   - `...google.com` or `...googlemail.com` → Google Workspace. **Safe**, not affected.
   - `mail.experiencerlc.com`, `experiencerlc.com`, or `@` → email runs on your **hosting server** (cPanel email). **Not safe yet.** Email depends on the hosting plan, and one DNS record needs extra care. Stop here and ask for help before step 3 below.

   You can also check **My Products** in GoDaddy: a separate "Email" or "Microsoft 365" product means email is its own service.

## What your DNS looks like now (checked November 16, 2026)

| Type  | Name         | Value                                         | During the switch |
|-------|--------------|-----------------------------------------------|-------------------|
| A     | @            | 107.180.28.113 (GoDaddy WordPress hosting)    | **Replace** with the four GitHub addresses below |
| CNAME | www          | experiencerlc.com (`@`)                       | **Change** to `brandoncannon.github.io` |
| MX    | @            | experiencerlc-com.mail.protection.outlook.com | Leave alone (Microsoft 365 email) |
| TXT   | @            | `v=spf1 include:spf.protection.outlook.com -all`, `NETORGFT6462049.onmicrosoft.com`, two `google-site-verification=…` | Leave alone |
| CNAME | autodiscover | autodiscover.outlook.com                      | Leave alone (lets Outlook set itself up) |
| A     | mail         | 107.180.28.113                                | Leave alone for now |

Email (pastor@, info@ and every other @experiencerlc.com address) runs on **Microsoft 365 bought through GoDaddy**, a separate service from the WordPress hosting. Changing the website doesn't affect it. Keep paying for the Microsoft 365 email; only the hosting plan goes away later.

## The switch (about 30 minutes plus waiting)

1. **Merge the site into `gh-pages`.** Merge the `claude/experiencerlc-redesign-7be62v` branch into `gh-pages` (it already includes the `CNAME` file that tells GitHub the site's address).
2. **Turn on GitHub Pages.** Repository **Settings → Pages** → Source: *Deploy from a branch* → Branch: `gh-pages`, folder `/ (root)` → **Save**. Under **Custom domain**, enter `www.experiencerlc.com` and save.
3. **Point the domain at GitHub.** In GoDaddy **DNS**, change only these records:

   | Type  | Name  | Value                     |
   |-------|-------|---------------------------|
   | A     | @     | 185.199.108.153           |
   | A     | @     | 185.199.109.153           |
   | A     | @     | 185.199.110.153           |
   | A     | @     | 185.199.111.153           |
   | CNAME | www   | brandoncannon.github.io   |

   Delete any other **A** record for `@`, and any existing `www` record (GoDaddy usually has one pointing at your hosting). **Do not touch MX or TXT records.** Those are your email.
4. **Wait** 15 minutes to a few hours for the change to spread. Then, back in **Settings → Pages**, tick **Enforce HTTPS**.
5. **Check** that `experiencerlc.com` and `www.experiencerlc.com` both show the new site, and send yourself a test email.
6. **Remove the test copy.** Once the real site is live, the `preview/` folder can be deleted (it's already hidden from Google).

## After it's live: get found on Google

1. **Google Search Console** (free). Do this 1–2 days after the new site is showing at experiencerlc.com.
   1. On a computer, go to **search.google.com/search-console** and sign in with the Google account used before (the domain already has Google verification records, so the property probably exists).
   2. Click the property picker at the top left. Pick **experiencerlc.com** (or **https://www.experiencerlc.com/** if that's what's listed).
      - If nothing is listed, someone else owns it. Click **Add property**, choose **Domain**, type `experiencerlc.com`, and Google shows a TXT record. Add it in GoDaddy DNS as a new **TXT** record with name **@** (don't delete the existing ones), wait a few minutes, then click **Verify**.
   3. In the left menu, click **Sitemaps**.
   4. Under **Add a new sitemap**, type `sitemap.xml` and click **Submit**.
   5. It should say **Success** (it can take a day). If an old WordPress sitemap is listed (e.g. `wp-sitemap.xml`), click it, then the **⋮** menu → **Remove sitemap**.
   6. Optional: in **URL inspection** at the top, paste `https://www.experiencerlc.com/` and click **Request indexing** to nudge Google sooner.
   - **Bing Webmaster Tools** (bing.com/webmasters): sign in and choose **Import from Google Search Console**. It copies everything over.
2. **Google Business Profile**: claim or update the church's listing at business.google.com. Use exactly the same name, address and phone number as the website: *Real Life Church, 2714 Scottsville Road, Bowling Green, KY 42104, (270) 681-5298*. Add service times, photos and the website link. This is the biggest factor for showing up when people nearby search "church in Bowling Green."
3. **Keep the hosting plan about a month**, then cancel it once email is confirmed safe (see "Before you start"). Keep the **domain** registration; don't cancel that.

## What changes for old links

Page addresses are the same as the WordPress site (`/new-here/`, `/leadership/`, `/kidslife/`, …). `/prayer-2/` forwards to `/prayer/`, `/commonly-asked-questions/` to the LifeGroups page, and `/weekly-guide/` to the RLC app. Old WordPress image links (`/wp-content/...`) and the RSS feed will stop working once the hosting is cancelled.
