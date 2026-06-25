import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('pairings-data.json', 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

# Posts that belong in the inbox:
# 1. "Various X" generic wine or food in pairing/porch-pounder tabs
# 2. Multi-wine string in pairing tab
# 3. Ambiguous extractions

VARIOUS_PREFIXES = ('various', 'cocktail')

inbox = []
for p in data:
    cat = p.get('category', 'hidden')
    if cat == 'hidden':
        continue
    wine = p.get('wine', 'Unknown')
    food = p.get('food', 'Unknown')
    wine_l = wine.lower()
    if any(wine_l.startswith(v) for v in VARIOUS_PREFIXES):
        inbox.append(p)
        continue
    # Multi-wine: wine field contains ' / ' with multiple wines
    if ' / ' in wine and len(wine.split(' / ')) >= 3:
        inbox.append(p)

print(f'=== INBOX CANDIDATES ({len(inbox)}) ===')
for p in inbox:
    pid = p['id']
    cat = p.get('category','?')
    wine = p.get('wine','?')
    food = p.get('food','?')
    slides = p.get('slideshowImages', [])
    print(f'\n  [{cat}] id={pid}')
    print(f'   wine: {wine!r}')
    print(f'   food: {food!r}')
    print(f'   slides: {len(slides)} images')
    print(f'   url:  {p.get("url","")}')
    for i, img in enumerate(slides[:3]):
        print(f'     img[{i}]: {img[:80]}')
    if len(slides) > 3:
        print(f'     ... +{len(slides)-3} more')
