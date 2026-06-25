import json, sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import defaultdict

with open('pairings-data.json', 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

def norm(s):
    return s.lower().strip() if s else ''

for cat in ['pairing', 'porch-pounder', 'recipe']:
    items = [p for p in data if p.get('category') == cat]
    groups = defaultdict(list)
    for p in items:
        key = norm(p.get('wine', 'Unknown'))
        groups[key].append(p)
    dupes = {k: v for k, v in groups.items()
             if len(v) > 1 and k not in ('unknown', 'various wines', 'various snacks')}
    if dupes:
        print(f'\n=== {cat.upper()} duplicates ===')
        for wine_key, posts in sorted(dupes.items()):
            w_display = posts[0].get('wine', '?')
            print(f'  Wine: {repr(w_display)}')
            for p in posts:
                food = p.get('food', '?')
                pid = p['id']
                print(f'    food: {repr(food)}  id={pid}')
