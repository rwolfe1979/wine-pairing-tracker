import json

DATA_FILE = 'pairings-data.json'
HTML_FILE = 'index.html'

with open(DATA_FILE, 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

with open(HTML_FILE, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_line = f'let PAIRINGS_DATA = []; // loaded by initApp()\n'
for i, line in enumerate(lines):
    if line.strip().startswith('let PAIRINGS_DATA = '):
        lines[i] = new_line
        print(f'Updated PAIRINGS_DATA on line {i + 1}')
        break

with open(HTML_FILE, 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done.')
