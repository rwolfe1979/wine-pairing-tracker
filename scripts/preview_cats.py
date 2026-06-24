import json
from collections import defaultdict

with open('pairings-data.json', 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

by_cat = defaultdict(list)
for p in data:
    by_cat[p.get('category', '?')].append(p)

for cat in ['pairing', 'porch-pounder', 'recipe', 'hidden']:
    items = by_cat[cat]
    print('\n=== %s (%d) ===' % (cat.upper(), len(items)))
    for p in items[:8]:
        w = p['wine'][:38]
        fo = p['food'][:38]
        print('  wine=%-40s food=%s' % (repr(w), repr(fo)))
