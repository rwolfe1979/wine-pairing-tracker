import json, sys
sys.stdout.reconfigure(encoding='utf-8')
with open('pairings-data.json', 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

SEPS = [' + ', ' & ', ' and ', ' / ']
multi = [p for p in data if p.get('category') != 'hidden'
         and any(sep in (p.get('food') or '') for sep in SEPS)]

print(f'Found {len(multi)} cards with multi-food separators:\n')
for p in multi:
    cat = p.get('category','?')
    wine = p.get('wine','?')
    food = p.get('food','?')
    print(f'[{cat}] {wine}')
    print(f'  food: {food!r}')
    print()
