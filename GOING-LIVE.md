# Moving experiencerlc.com from WordPress to this site

Your domain stays at GoDaddy. The website moves to GitHub Pages (free, with free HTTPS). Every change pushed to the `main` branch goes live within a few minutes.

## Before you start

1. **Back up WordPress.** In GoDaddy, open your hosting (cPanel) and use **Backup** or **File Manager** to download the site files and database. Keep this so nothing is lost.
2. **Find out where your email lives.** In GoDaddy, go to **Domains → experiencerlc.com → DNS** and look at the **MX** records:
   - `outlook.com` / `secureserver.net` → Microsoft 365 or GoDaddy email. Not affected by this switch.
   - `google.com` → Google Workspace. Not affected.
   - Anything pointing at your hosting server (cPanel email) → your email depends on the hosting plan. **Don't cancel the hosting plan** until email is moved.

## The switch (about 30 minutes plus waiting)

1. **Merge the site into `main`.** Merge the `claude/experiencerlc-redesign-7be62v` branch, and add a file named `CNAME` containing `www.experiencerlc.com`. (Claude can do this for you.)
2. **Turn on GitHub Pages.** Repository **Settings → Pages** → Source: *Deploy from a branch* → Branch: `main`, folder `/ (root)` → **Save**. Under **Custom domain**, enter `www.experiencerlc.com` and save.
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

1. **Google Search Console** (free): go to search.google.com/search-console, add the **Domain** `experiencerlc.com`, and verify it with the TXT record it gives you (add it in GoDaddy DNS). Then go to **Sitemaps** and submit `sitemap.xml`. Do the same at **Bing Webmaster Tools** (it can import from Google).
2. **Google Business Profile**: claim or update the church's listing at business.google.com. Use exactly the same name, address and phone number as the website: *Real Life Church, 2714 Scottsville Road, Bowling Green, KY 42104, (270) 681-5298*. Add service times, photos and the website link. This is the biggest factor for showing up when people nearby search "church in Bowling Green."
3. **Keep the hosting plan about a month**, then cancel it once email is confirmed safe (see "Before you start"). Keep the **domain** registration; don't cancel that.

## What changes for old links

Page addresses are the same as the WordPress site (`/new-here/`, `/leadership/`, `/kidslife/`, …). `/prayer-2/` forwards to `/prayer/`, `/commonly-asked-questions/` to the LifeGroups page, and `/weekly-guide/` to the RLC app. Old WordPress image links (`/wp-content/...`) and the RSS feed will stop working once the hosting is cancelled.
