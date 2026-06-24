#!/usr/bin/env python3
"""
Weekly updater for Sam Sommelier Wine Pairing Tracker.
Scrapes new posts from @samanthasommelier via Apify, extracts pairing info
using Claude, and updates pairings-data.json and index.html.

Required env vars: APIFY_TOKEN, ANTHROPIC_API_KEY
"""

import json
import os
import time
import requests
from anthropic import Anthropic

APIFY_ACTOR = 'GdWCkxBtKWOsKjdch'  # clockworks/tiktok-scraper
TIKTOK_USERNAME = 'samanthasommelier'
DATA_FILE = 'pairings-data.json'
HTML_FILE = 'index.html'

PAIRING_KEYWORDS = [
    'wine', 'pairing', 'pairs with', '🍷', '🥂', '🍾',
    'vinho', 'rosé', 'rose', 'blanc', 'rouge', 'pinot', 'chardonnay',
    'prosecco', 'chablis', 'sauvignon', 'zinfandel', 'cabernet', 'merlot',
    'riesling', 'champagne', 'spritz', 'crémant', 'cremant', 'sancerre',
    'trader joe', "trader joe's", 'costco', 'aldi',
    'chips', 'dip', 'snack', 'cheese', 'crackers', 'paired',
]


def run_apify_scraper(token, max_posts=50):
    """Trigger Apify actor and return scraped posts."""
    base = 'https://api.apify.com/v2'
    headers = {'Content-Type': 'application/json'}

    payload = {
        'profiles': [TIKTOK_USERNAME],
        'resultsPerPage': max_posts,
        'profileSorting': 'latest',
        'profileScrapeSections': ['videos'],
        'downloadSubtitlesOptions': 'DOWNLOAD_SUBTITLES',
    }

    resp = requests.post(
        f'{base}/acts/{APIFY_ACTOR}/runs?token={token}',
        json=payload, headers=headers, timeout=30
    )
    resp.raise_for_status()
    run_id = resp.json()['data']['id']
    print(f'  Apify run started: {run_id}')

    for attempt in range(72):  # up to 6 minutes
        time.sleep(5)
        status_resp = requests.get(
            f'{base}/actor-runs/{run_id}?token={token}', timeout=15
        )
        run_data = status_resp.json()['data']
        status = run_data['status']
        if attempt % 6 == 0:
            print(f'  Status: {status} ({attempt * 5}s elapsed)')
        if status in ('SUCCEEDED', 'FAILED', 'ABORTED', 'TIMED-OUT'):
            break

    if status != 'SUCCEEDED':
        raise RuntimeError(f'Apify run ended with status: {status}')

    dataset_id = run_data['defaultDatasetId']
    items_resp = requests.get(
        f'{base}/datasets/{dataset_id}/items?token={token}&limit=200&clean=true',
        timeout=30
    )
    items_resp.raise_for_status()
    return items_resp.json()


def extract_pairing(text, client):
    """Use Claude Haiku to extract wine/food pairing from caption text."""
    text_lower = text.lower()
    if not any(kw in text_lower for kw in PAIRING_KEYWORDS):
        return {'wine': 'Unknown', 'food': 'Unknown', 'store': 'Unknown', 'wineType': 'Unknown'}

    try:
        response = client.messages.create(
            model='claude-haiku-4-5-20251001',
            max_tokens=300,
            messages=[{
                'role': 'user',
                'content': (
                    'Extract wine/food pairing info from this TikTok caption by @samanthasommelier '
                    '(a certified sommelier who posts affordable wine + snack pairings).\n'
                    'Return ONLY valid JSON, no markdown fences:\n'
                    '{\n'
                    '  "wine": "exact wine name or Unknown",\n'
                    '  "food": "exact food/snack name or Unknown",\n'
                    '  "store": "Trader Joe\'s" or "Costco" or "Aldi" or "Unknown",\n'
                    '  "wineType": "Red" or "White" or "Rosé" or "Sparkling" or "Orange" or "Unknown"\n'
                    '}\n\n'
                    f'Caption:\n{text}'
                )
            }]
        )
        raw = response.content[0].text.strip()
        # Strip markdown fences if present
        if raw.startswith('```'):
            raw = raw.split('```')[1]
            if raw.startswith('json'):
                raw = raw[4:]
        return json.loads(raw.strip())
    except Exception as e:
        print(f'    Warning: extraction failed ({e}), defaulting to Unknown')
        return {'wine': 'Unknown', 'food': 'Unknown', 'store': 'Unknown', 'wineType': 'Unknown'}


def normalize_post(raw, pairing):
    """Convert raw Apify post into our standard data shape."""
    vm = raw.get('videoMeta') or {}
    thumbnail = vm.get('coverUrl') or vm.get('originalCoverUrl')

    slideshow_images = []
    if raw.get('isSlideshow') and raw.get('slideshowImageLinks'):
        for img in raw['slideshowImageLinks']:
            if isinstance(img, dict):
                link = img.get('tiktokLink') or img.get('downloadLink')
                if link:
                    slideshow_images.append(link)
            elif isinstance(img, str):
                slideshow_images.append(img)

    hashtags = []
    for h in (raw.get('hashtags') or []):
        if isinstance(h, dict) and h.get('name'):
            hashtags.append(h['name'])
        elif isinstance(h, str):
            hashtags.append(h)

    return {
        'id': str(raw.get('id', '')),
        'text': raw.get('text', ''),
        'date': raw.get('createTimeISO', ''),
        'url': raw.get('webVideoUrl', ''),
        'thumbnailUrl': thumbnail,
        'isSlideshow': bool(raw.get('isSlideshow', False)),
        'slideshowImages': slideshow_images,
        'likes': int(raw.get('diggCount', 0)),
        'views': int(raw.get('playCount', 0)),
        'hashtags': hashtags,
        'wine': pairing.get('wine', 'Unknown'),
        'food': pairing.get('food', 'Unknown'),
        'store': pairing.get('store', 'Unknown'),
        'wineType': pairing.get('wineType', 'Unknown'),
    }


def update_html_data(all_data):
    """Replace the embedded PAIRINGS_DATA constant in index.html."""
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_line = f'const PAIRINGS_DATA = {json.dumps(all_data, ensure_ascii=False)};\n'
    for i, line in enumerate(lines):
        if line.strip().startswith('const PAIRINGS_DATA = '):
            lines[i] = new_line
            print(f'  Updated PAIRINGS_DATA on line {i + 1} of {HTML_FILE}')
            break

    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.writelines(lines)


def main():
    apify_token = os.environ.get('APIFY_TOKEN')
    anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
    if not apify_token or not anthropic_key:
        raise SystemExit('ERROR: APIFY_TOKEN and ANTHROPIC_API_KEY must be set.')

    # Load existing data
    existing_data = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    existing_ids = {p['id'] for p in existing_data}
    print(f'Existing posts in database: {len(existing_data)}')

    # Scrape latest posts
    print('Running Apify scraper...')
    raw_posts = run_apify_scraper(apify_token, max_posts=50)
    print(f'Scraped {len(raw_posts)} posts from TikTok')

    # Identify new posts
    new_raw = [p for p in raw_posts if str(p.get('id', '')) not in existing_ids]
    print(f'New posts to process: {len(new_raw)}')

    if not new_raw:
        print('No new posts found. Nothing to update.')
        return

    # Extract pairings for new posts
    client = Anthropic(api_key=anthropic_key)
    new_posts = []
    for i, raw in enumerate(new_raw):
        post_id = raw.get('id', '?')
        caption_preview = (raw.get('text', '') or '')[:60].replace('\n', ' ')
        print(f'  [{i + 1}/{len(new_raw)}] {post_id}: {caption_preview}...')
        pairing = extract_pairing(raw.get('text', ''), client)
        print(f'    → wine={pairing["wine"]!r}, food={pairing["food"]!r}, store={pairing["store"]!r}')
        new_posts.append(normalize_post(raw, pairing))
        time.sleep(0.3)  # gentle rate limiting

    # Merge: new posts at the front (chronologically newest)
    all_data = new_posts + existing_data

    # Save canonical JSON
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f'Saved {len(all_data)} total posts to {DATA_FILE}')

    # Update embedded data in HTML
    update_html_data(all_data)

    print(f'\nDone! Added {len(new_posts)} new posts (total: {len(all_data)}).')


if __name__ == '__main__':
    main()
