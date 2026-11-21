---
title: RLC App Setup Guide
tags: [rlc, app, subsplash]
---

# RLC App Setup Guide (Subsplash)

Everything in this folder is ready to upload in the **Subsplash Dashboard** (dashboard.subsplash.com). Menu names in Subsplash change from time to time. If something isn't where this guide says, look for **App Builder**, **Branding** or **Appearance**.

## 1. App icon

- `app-icon-black-on-white-1024.png`: the black RLC logo on white (matches the website).
- `app-icon-white-on-black-1024.png`: reversed, if you prefer a dark icon.

Upload one where Subsplash asks for the **app icon** (1024 × 1024). The icon on phones updates the next time Subsplash publishes the app to the App Store and Google Play. Subsplash support can tell you when that is.

## 2. Brand colors

Enter these where Subsplash asks for app colors:

| Use | Color | Hex |
|---|---|---|
| Main / primary | Navy | `#153C5D` |
| Accent / buttons | Light aqua | `#9ECBD1` |
| Secondary | Steel blue | `#5B8DAE` |
| Muted text | Slate | `#5E7887` |
| Soft background | Cream | `#E8DFCE` |
| Text | Charcoal | `#4D4D4D` |

## 3. Tile graphics

Every topic comes in three shapes. Subsplash asks for different ones in different places (lists, home-screen tiles, headers):

| Folder | Size | Shape |
|---|---|---|
| `square/` | 1400 × 1400 | Square (1:1) |
| `wide/` | 1920 × 1080 | Wide (16:9) |
| `banner/` | 1920 × 692 | Banner |
| `thumbnail/` | 600 × 600 | Square, **no text**: use for small list thumbnails, where the name is already written beside the picture |

If Subsplash shows a different size for a spot, use the closest shape. It will crop to fit.

## 4. What each tile links to

Subsplash can open a web page **inside the app**. Pages on the website look just like the website, and when you update the website, the app is updated too.

| Tile | Link |
|---|---|
| Watch Live | https://www.experiencerlc.com/watch-live/ (or your Subsplash media/livestream) |
| Give | https://tithe.ly/give_new/www/#/tithely/give-one-time/306850 (or Subsplash Giving, if you use it) |
| Events | https://experiencerlc.churchcenter.com/registrations/events |
| Daily Reading | https://www.experiencerlc.com/daily/ |
| Worship Guide | https://www.experiencerlc.com/worship-guide/ |
| Message Notes | https://www.experiencerlc.com/notes/ |
| RLC Connect | https://www.experiencerlc.com/rlcconnect/ |
| Life Groups | https://experiencerlc.churchcenter.com/groups |
| Kids Life | https://www.experiencerlc.com/kidslife/ |
| Prayer | https://www.experiencerlc.com/prayer/ |

## 5. Screen-by-screen plan (your current app)

Your five tabs already match the website, so keep them. Use the **wide** tiles for the big full-width cards, the **banner** tiles across the top of a tab, and the **thumbnail** pictures (no text) for the small list items. The **square** tiles (with text) are for anywhere Subsplash shows a big square on its own.

### Welcome tab (top to bottom)
| Card | Tile | Links to |
|---|---|---|
| Worship Guide (replaces "Weekly Worship Guide") | `worship-guide` | /worship-guide/ |
| Daily Reading (replaces "SOAP Bible Reading Plan") | `daily-reading` | /daily/ |
| Message Notes | `message-notes` | /notes/ |
| Give | `give` | Tithe.ly (or Subsplash Giving) |
| RLC Connect | `rlc-connect` | /rlcconnect/ |
| Life Groups | `life-groups` | Church Center groups |
| Events | `events` | Church Center events |
| Counseling Center | `counseling-center` | /rlcc/ |
| Pray First App | keep your current graphic | (it's Pray First's own branding) |
| Connect Card | `connect-card` | Church Center connect card |

Remove the second "RLC Connect" card and the "Connect" (train) card. They repeat the cards above.

### Messages tab
| Card | Tile | Links to |
|---|---|---|
| Watch Live & Past Messages (replaces the gray YouTube box) | `watch-live` | YouTube channel or /watch-live/ |
| Message Notes (replaces the gray notepad box) | `message-notes` | /notes/ |

### Connect tab
- **Top banner:** `rlc-connect` (banner), replacing the "Welcome Home / RLC Connect 5PM" slides.
- **List thumbnails (`thumbnail/` folder):** Location & Service Times → `location` (/new-here/) · Events → `events` · Life Groups → `life-groups` · RLC Connect → `rlc-connect` · Student Life → `student-life` (/student-life/) · Kids Life → `kids-life` (/kidslife/) · Connect Card → `connect-card`.
- **Rename** "LifeGroups" → **Life Groups** and "KidsLife" → **Kids Life**.
- Facebook, Instagram and Pastor Brandon's Blog can keep their current icons.

### Bible tab
- **Top banner:** `bible-plans` (banner), replacing "Experience the Bible".
- **SOAP Bible Reading Plan:** thumbnail `daily-reading`, linking to /daily/ (today's chapter and SOAP).
- **Every other reading plan** (Making Sense of God, How to Forgive…): thumbnail `bible-plans` (`thumbnail/` folder), replacing the repeated "Bible" picture.

### More tab
- **Top banner:** `welcome-home` (banner), replacing the old green "Real Life Church / Welcome Home" banner.
- **Remove the Twitter button.**
- Keep View Map, Give, Online Connection Card, Facebook and Website.

### App icon
`app-icon-black-on-white-1024.png` (or the white-on-black version).
