# Wine & Snack Pairing Tracker

An interactive tracker for wine and snack pairings from [@samanthasommelier](https://www.tiktok.com/@samanthasommelier) on TikTok.

**[Open the Tracker →](https://rwolfe1979.github.io/wine-pairing-tracker/)**

## What it is

Sam the Sommelier posts affordable, no-snob wine and food pairings — mostly from Trader Joe's, Costco, and Aldi. This app pulls her posts, extracts the pairings, and gives you a place to track what you've tried, what you liked, and build a shopping list.

## Features

- Browse all of Sam's wine + food pairings with thumbnails from her posts
- Filter by store (Trader Joe's / Costco / Aldi), wine type, or your rating status
- Rate each pairing: Wine / Food / Pairing — separately
- Add your own notes to any card
- Shopping List sidebar — see everything you've loved or liked, grouped by store
- All ratings saved to your browser's local storage

## Auto-updates

A GitHub Actions workflow runs every Monday and:
1. Scrapes the latest posts from @samanthasommelier via Apify
2. Extracts new wine/food pairings using Claude AI
3. Commits updated data and pushes — the site updates automatically

## Setup (for the auto-updater)

Add these two secrets under **Settings → Secrets and variables → Actions**:

| Secret | Where to get it |
|--------|----------------|
| `APIFY_TOKEN` | [apify.com/account/integrations](https://console.apify.com/account/integrations) |
| `ANTHROPIC_API_KEY` | [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys) |

To run an update manually: **Actions → Update Wine Pairings → Run workflow**
