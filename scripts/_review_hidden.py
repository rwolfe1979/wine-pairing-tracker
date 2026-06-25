import json, sys
sys.stdout.reconfigure(encoding='utf-8')
with open('pairings-data.json', 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

hidden = [p for p in data if p.get('category') == 'hidden']
print(f'=== HIDDEN ({len(hidden)}) ===')
for p in hidden:
    pid = p['id']
    w = p.get('wine','?')[:35]
    fo = p.get('food','?')[:35]
    snippet = p.get('text','')[:90].replace('\n',' ')
    print(f'  {pid}  wine={repr(w)}  food={repr(fo)}')
    print(f'    {repr(snippet)}')
