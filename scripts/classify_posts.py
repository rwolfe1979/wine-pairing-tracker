#!/usr/bin/env python3
"""
Classify posts into tabs (pairing / porch-pounder / recipe / hidden)
and split multi-pairing slideshow captions into individual entries.
Run from the project root: python scripts/classify_posts.py
"""

import json
import re
from collections import Counter

DATA_FILE = 'pairings-data.json'

# -------------------------------------------------------------------
# Keywords
# -------------------------------------------------------------------

# Recipe = the DRINK ITSELF is a recipe (slushie, cocktail, spritz with instructions)
# NOT triggered by food that happens to have recipe-like prep instructions
RECIPE_WINE_SIGNALS = [
    'slushie', 'slushies',  # wine slushie posts
]
# Caption-level signals that mean the post IS a how-to-make-this-drink post
RECIPE_POST_SIGNALS = [
    'blend together', 'blend it',
    'handful frozen mango', 'handful frozen peach',
    '⬇️ recipe', '⬇️ wine slushie', '⬇️ sauvy b',
    'spritz recipe',
    'limoncello liqueur',  # the Limoncello Spritz recipe post specifically
    '~ 1', '~ 2',   # ingredient list format used in recipe posts
    '• your choice of sauvignon',  # KJ spritz recipe
]

HIDDEN_SIGNALS = [
    '#onthisday', 'on this day',
    'shareslo', 'paso robles', 'santa barbara', 'pacific northwest',
    'biddle ranch', 'tolosa winery', 'hotel slo',
    'please don\'t break promises', 'show wine', 'sniffs wine',
    'i\'d love for you to try',
]

# Specific posts that are promo-only (wine club ads with no pairing data)
HIDDEN_POST_IDS = {
    '7654400348412562701',  # wine club promo slideshow
    '7652433024302222606',  # #onthisday
    '7649617364220153101',  # #onthisday
    '7643188745759444237',  # #onthisday
    '7647581369270357261',  # #onthisday
    '7629865547362028814',  # "I don't make the rules"
    '7625863680302779662',  # wine club promo
    '7649082138402262286',  # "sorry i've been on a constant tj's..." (no actual pairing)
    '7652068180772310285',  # "sniffs wine - I got nothing"
    '7650329546444639501',  # SLO travel vlog
    '7636849214953213198',  # spritz recipe only, no food
    '7609038223909670158',  # solo date lifestyle vlog (cocktail+tbell extracted incorrectly)
}

WINE_TYPE_HINTS = {
    'red': ['rouge', 'red', 'cabernet', 'merlot', 'pinot noir', 'syrah', 'shiraz',
            'zinfandel', 'malbec', 'chianti', 'amarone', 'primitivo', 'barbera',
            'tempranillo', 'grenache', 'garnacha', 'sangiovese', 'lambrusco',
            'susumaniello', 'côtes du rhône réserve', 'nero d\'avola'],
    'white': ['blanc', 'white', 'chardonnay', 'sauvignon blanc', 'sauvy b', 'pinot grigio',
              'riesling', 'albariño', 'vermentino', 'vinho verde', 'chablis', 'sancerre',
              'gavi', 'soave', 'grüner veltliner', 'gruner veltliner', 'muscadet',
              'viognier', 'torrontés', 'gewürztraminer', 'chenin blanc'],
    'rosé': ['rosé', 'rose', 'rosato', 'rosado', 'blush'],
    'sparkling': ['prosecco', 'champagne', 'cava', 'crémant', 'cremant', 'sekt',
                  'spumante', 'lambrusco', 'pétillant', 'frizzante', 'sparkling',
                  'vinho verde', 'aperol', 'spritz'],
    'orange': ['orange wine', 'amber wine', 'skin contact', 'ramato'],
}


def guess_wine_type(wine_name: str) -> str:
    wl = wine_name.lower()
    for wtype, keywords in WINE_TYPE_HINTS.items():
        if any(k in wl for k in keywords):
            return wtype.capitalize() if wtype != 'rosé' else 'Rosé'
    return 'Unknown'


def classify(post: dict) -> str:
    text = post.get('text', '')
    tl = text.lower()
    wine = post.get('wine', 'Unknown')
    food = post.get('food', 'Unknown')
    pid = str(post.get('id', ''))

    # Explicit hidden list
    base_id = pid.split('_')[0]
    if base_id in HIDDEN_POST_IDS:
        return 'hidden'

    # Hidden signals in text
    if any(s in tl for s in HIDDEN_SIGNALS) and wine == 'Unknown' and food == 'Unknown':
        return 'hidden'

    # Recipe: the drink ITSELF is a recipe (slushie, cocktail how-to)
    # Don't trigger on food that happens to have prep instructions
    if wine != 'Unknown':
        wine_lower = wine.lower()
        if (any(s in wine_lower for s in RECIPE_WINE_SIGNALS) or
                any(s in tl for s in RECIPE_POST_SIGNALS)):
            return 'recipe'

    # Pairing: both wine and food are known
    if wine != 'Unknown' and food != 'Unknown':
        return 'pairing'

    # Porch pounder: wine known, food not
    if wine != 'Unknown':
        return 'porch-pounder'

    # Nothing useful
    return 'hidden'


# -------------------------------------------------------------------
# Multi-pairing extraction from caption text
# -------------------------------------------------------------------

PAIRING_LINE_RE = re.compile(
    r'[🍷🥂🍾🌹]\s*(.+?)(?=\n[🍷🥂🍾🌹]|\Z)',
    re.DOTALL
)

PRICE_RE = re.compile(r'\$[\d.]+')


def extract_multi_pairings(text: str):
    """
    If a caption lists multiple wine+food pairings (each line starting with
    a wine emoji), return them as a list of {'wine':..., 'food':...} dicts.
    Returns [] if only one (or zero) pairings found.
    """
    matches = PAIRING_LINE_RE.findall(text)
    if len(matches) < 2:
        return []

    pairings = []
    for m in matches:
        m = m.strip()
        if not m:
            continue

        # Split on + to separate wine from food
        parts = [p.strip() for p in m.split('+')]
        if not parts:
            continue

        wine_raw = PRICE_RE.sub('', parts[0]).strip(' ,-–')
        wine_raw = re.sub(r'\s+', ' ', wine_raw)

        food_raw = ' + '.join(parts[1:]).strip() if len(parts) > 1 else 'Unknown'
        food_raw = food_raw.strip(' ,-–')

        # Skip if wine name is too short / looks like an emoji fragment
        if len(wine_raw) < 4:
            continue

        pairings.append({'wine': wine_raw, 'food': food_raw})

    return pairings if len(pairings) >= 2 else []


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------

def main():
    with open(DATA_FILE, 'r', encoding='utf-8-sig') as f:
        raw_data = json.load(f)

    print(f'Loaded {len(raw_data)} posts\n')

    processed = []
    split_count = 0

    for post in raw_data:
        text = post.get('text', '')
        is_slideshow = post.get('isSlideshow', False)
        post_id = str(post.get('id', ''))

        # Only try multi-pairing extraction on slideshow posts where
        # wine/food look generic (meaning we might have only grabbed one)
        should_try_split = (
            is_slideshow
            and post.get('wine', 'Unknown') in ('Unknown', 'Various Rosés',
                'Various Snacks', 'Various Sparkling Wines', 'Various Spritzes',
                'Various Wines', 'Various Snacks')
        )

        if should_try_split:
            multi = extract_multi_pairings(text)
            if multi:
                images = post.get('slideshowImages', [])
                for i, pair in enumerate(multi):
                    child = dict(post)
                    child['id'] = f'{post_id}_{i}'
                    child['originalPostId'] = post_id
                    child['wine'] = pair['wine']
                    child['food'] = pair['food']
                    child['wineType'] = guess_wine_type(pair['wine'])
                    child['wineImageUrl'] = None
                    child['foodImageUrl'] = None
                    # Give each split card the corresponding slide image
                    if images and i < len(images):
                        child['thumbnailUrl'] = images[i]
                        child['slideshowImages'] = []
                        child['isSlideshow'] = False
                    child['category'] = 'pairing'
                    child['isMultiPairingSplit'] = True
                    processed.append(child)
                split_count += len(multi)
                print(f'  Split {post_id} -> {len(multi)} pairings')
                continue

        # Single classification
        post['category'] = classify(post)
        # Fix up wineType if it's still Unknown but we can guess
        if post.get('wineType', 'Unknown') == 'Unknown' and post.get('wine', 'Unknown') != 'Unknown':
            post['wineType'] = guess_wine_type(post['wine'])
        processed.append(post)

    # Stats
    cats = Counter(p['category'] for p in processed)
    print('\nResults:')
    for cat, n in cats.most_common():
        print(f'  {cat:20s} {n}')
    print(f'  {"(split pairings)":20s} {split_count}')
    print(f'  {"TOTAL":20s} {len(processed)}')

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(processed, f, ensure_ascii=False, indent=2)
    print(f'\nSaved -> {DATA_FILE}')


if __name__ == '__main__':
    main()
