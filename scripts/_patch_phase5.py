#!/usr/bin/env python3
"""
Phase 5: Update display layer to use v2 schema (drinkName, drinkItems[], foodItems[]).
- Card face shows drinkName + each food item on its own line
- Detail modal shows structured drink/food item lists with brand, wineType, store chips
- Shopping list deduplicates by brand+product, groups by store
- Filters + search use new fields
Run from project root: python scripts/_patch_phase5.py
"""
import sys
HTML_FILE = 'index.html'
with open(HTML_FILE, 'r', encoding='utf-8') as f:
    src = f.read()
changes = []

# ─────────────────────────────────────────────
# 1. CSS additions
# ─────────────────────────────────────────────
changes.append(('v2 CSS', '/* REVIEW INBOX */', """\
/* V2 ITEM DISPLAY */
.drink-type-badge {
  display: inline-block; font-size: 0.65rem; font-weight: 600;
  background: var(--cream-dark); color: var(--burgundy);
  border-radius: 10px; padding: 2px 8px; vertical-align: middle; margin-left: 6px;
}
.card-food-items { display: flex; flex-direction: column; gap: 1px; }
.card-food-item { font-size: 0.78rem; color: var(--text-secondary); line-height: 1.35; }
.card-food-more { font-size: 0.68rem; color: var(--text-muted); font-style: italic; }
/* detail item list */
.detail-items-wrap { padding-bottom: 10px; }
.detail-items-section { margin-bottom: 12px; }
.detail-section-label {
  font-size: 0.68rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.07em; color: var(--text-muted); margin-bottom: 5px;
}
.detail-item-row {
  display: flex; align-items: center; flex-wrap: wrap; gap: 4px;
  padding: 4px 0; border-bottom: 1px solid #f5eeea;
}
.detail-item-name { flex: 1; font-size: 0.82rem; color: var(--text-primary); min-width: 0; }
.detail-item-chip {
  font-size: 0.65rem; background: var(--cream-dark); color: var(--text-muted);
  border-radius: 10px; padding: 2px 7px; white-space: nowrap; flex-shrink: 0;
}
.detail-item-chip.needs-review { background: #fff3cd; color: #856404; }
/* shopping list v2 */
.list-item { display: flex; align-items: center; gap: 8px; padding: 5px 0; border-bottom: 1px solid #f5eeea; }
.list-item-icon { flex-shrink: 0; font-size: 0.85rem; }
.list-item-info { flex: 1; font-size: 0.8rem; min-width: 0; }
.list-item-brand { color: var(--text-muted); }
.list-item-product { color: var(--text-primary); font-weight: 500; }
.list-item-count {
  font-size: 0.68rem; color: var(--text-muted);
  background: var(--cream-dark); border-radius: 10px; padding: 1px 6px; flex-shrink: 0;
}

/* REVIEW INBOX */"""))

# ─────────────────────────────────────────────
# 2. Add detailItemsWrap to modal HTML
# ─────────────────────────────────────────────
changes.append(('detailItemsWrap HTML',
  '      <div id="detailRatingsWrap" class="detail-ratings-wrap"></div>',
  '      <div id="detailItemsWrap" class="detail-items-wrap"></div>\n      <div id="detailRatingsWrap" class="detail-ratings-wrap"></div>'))

# ─────────────────────────────────────────────
# 3. Update openDetailModal to use new fields
# ─────────────────────────────────────────────
changes.append(('openDetailModal v2',
"""\
  document.getElementById('detailWineName').textContent =
    p.wine !== 'Unknown' ? p.wine : 'Wine not specified';
  document.getElementById('detailFoodName').textContent =
    p.food !== 'Unknown' ? p.food : '';

  // Ratings""",
"""\
  // Drink name + type badge
  const drinkName = p.drinkName || p.wine || 'Wine not specified';
  const drinkType = p.drinkType || 'Wine';
  const typeBadge = drinkType !== 'Wine' ? ` <span class="drink-type-badge">${drinkType}</span>` : '';
  document.getElementById('detailWineName').innerHTML = escapeHtml(drinkName) + typeBadge;
  document.getElementById('detailFoodName').innerHTML = '';

  // Structured drink + food items
  const drinkItems = p.drinkItems || [];
  const foodItems  = p.foodItems  || [];
  let itemsHtml = '';
  if (drinkItems.length) {
    itemsHtml += `<div class="detail-items-section">
      <div class="detail-section-label">🍷 Drink</div>
      ${drinkItems.map(i => `<div class="detail-item-row">
        <span class="detail-item-name">${i.brand ? `<strong>${escapeHtml(i.brand)}</strong> — ` : ''}${escapeHtml(i.product||'')}</span>
        ${i.wineType && i.wineType !== 'N/A' ? `<span class="detail-item-chip">${escapeHtml(i.wineType)}</span>` : ''}
        ${i.store ? `<span class="detail-item-chip">${escapeHtml(i.store)}</span>` : ''}
        ${i.vintage ? `<span class="detail-item-chip">${escapeHtml(i.vintage)}</span>` : ''}
        ${i.needsReview ? '<span class="detail-item-chip needs-review">needs review</span>' : ''}
      </div>`).join('')}
    </div>`;
  }
  if (foodItems.length) {
    itemsHtml += `<div class="detail-items-section">
      <div class="detail-section-label">🍽️ Food</div>
      ${foodItems.map(i => `<div class="detail-item-row">
        <span class="detail-item-name">${i.brand ? `<strong>${escapeHtml(i.brand)}</strong> — ` : ''}${escapeHtml(i.product||'')}</span>
        ${i.store ? `<span class="detail-item-chip">${escapeHtml(i.store)}</span>` : ''}
        ${i.needsReview ? '<span class="detail-item-chip needs-review">needs review</span>' : ''}
      </div>`).join('')}
    </div>`;
  }
  if (!drinkItems.length && !foodItems.length && p.food && p.food !== 'Unknown') {
    itemsHtml = `<div class="detail-item-row"><span class="detail-item-name">${escapeHtml(p.food)}</span></div>`;
  }
  document.getElementById('detailItemsWrap').innerHTML = itemsHtml;

  // Ratings"""))

# ─────────────────────────────────────────────
# 4. groupByWine — use drinkName
# ─────────────────────────────────────────────
changes.append(('groupByWine drinkName',
  '    const key = encodeGroupKey(p.wine);',
  '    const key = encodeGroupKey(p.drinkName || p.wine);'))

# ─────────────────────────────────────────────
# 5. render() — use drinkName for group key map
# ─────────────────────────────────────────────
changes.append(('render drinkName groupKey',
  "    groups.forEach(g => { window._currentGroups[encodeGroupKey(g[0].wine)] = g; });",
  "    groups.forEach(g => { window._currentGroups[encodeGroupKey(g[0].drinkName || g[0].wine)] = g; });"))

# ─────────────────────────────────────────────
# 6. Add buildFoodItemsHtml helper + update buildCard
# ─────────────────────────────────────────────
OLD_BUILD_CARD = """\
function buildCard(p) {
  const r = getRating(p.id);
  const primaryField = p.category === 'pairing' ? 'pairingRating' : 'wineRating';
  const primaryVal = r[primaryField];
  const statusColors = {loved:'#27AE60',liked:'#2980B9',meh:'#F39C12',disliked:'#E74C3C'};
  const statusDot = primaryVal !== 'not-tried'
    ? `<div class="card-status-dot" id="dot-${p.id}" style="background:${statusColors[primaryVal]}"></div>`
    : `<div class="card-status-dot" id="dot-${p.id}" style="display:none"></div>`;

  return `<div class="card" id="card-${p.id}" onclick="openDetailModal('${p.id}')">
    ${buildImageSection(p)}
    ${statusDot}
    <div class="card-body">
      <div class="card-wine">${p.wine !== 'Unknown' ? p.wine : '<em style="color:#999;font-weight:400">Wine not specified</em>'}</div>
      <div class="card-food">${p.food !== 'Unknown' ? p.food : '<em style="color:#999">Food not specified</em>'}</div>
      <div class="card-meta">
        <span>${fmtDate(p.date)}</span>
        <span class="card-engagement"><span>👁️ ${fmtNum(p.views)}</span><span>❤️ ${fmtNum(p.likes)}</span></span>
      </div>
    </div>
  </div>`;
}"""

NEW_BUILD_CARD = """\
function buildFoodItemsHtml(p) {
  const items = (p.foodItems && p.foodItems.length)
    ? p.foodItems
    : (p.food && p.food !== 'Unknown' ? [{product: p.food}] : []);
  if (!items.length) return '<div class="card-food"><em style="color:#999">Food not specified</em></div>';
  const MAX = 3;
  const shown = items.slice(0, MAX);
  const extra = items.length - MAX;
  return `<div class="card-food-items">${
    shown.map(f => `<div class="card-food-item">${escapeHtml(f.product||'')}</div>`).join('')
  }${extra > 0 ? `<div class="card-food-more">+${extra} more</div>` : ''}</div>`;
}

function buildCard(p) {
  const r = getRating(p.id);
  const primaryField = p.category === 'pairing' ? 'pairingRating' : 'wineRating';
  const primaryVal = r[primaryField];
  const statusColors = {loved:'#27AE60',liked:'#2980B9',meh:'#F39C12',disliked:'#E74C3C'};
  const statusDot = primaryVal !== 'not-tried'
    ? `<div class="card-status-dot" id="dot-${p.id}" style="background:${statusColors[primaryVal]}"></div>`
    : `<div class="card-status-dot" id="dot-${p.id}" style="display:none"></div>`;
  const drinkName = p.drinkName || p.wine || 'Wine not specified';

  return `<div class="card" id="card-${p.id}" onclick="openDetailModal('${p.id}')">
    ${buildImageSection(p)}
    ${statusDot}
    <div class="card-body">
      <div class="card-wine">${drinkName !== 'Unknown' ? escapeHtml(drinkName) : '<em style="color:#999;font-weight:400">Wine not specified</em>'}</div>
      ${buildFoodItemsHtml(p)}
      <div class="card-meta">
        <span>${fmtDate(p.date)}</span>
        <span class="card-engagement"><span>👁️ ${fmtNum(p.views)}</span><span>❤️ ${fmtNum(p.likes)}</span></span>
      </div>
    </div>
  </div>`;
}"""

changes.append(('buildCard + buildFoodItemsHtml', OLD_BUILD_CARD, NEW_BUILD_CARD))

# ─────────────────────────────────────────────
# 7. buildGroupedCard — use drinkName + foodItemsHtml
# ─────────────────────────────────────────────
OLD_GROUPED = """\
  const wine = posts[0].wine;"""
NEW_GROUPED = """\
  const wine = posts[0].drinkName || posts[0].wine;"""
changes.append(('buildGroupedCard drinkName', OLD_GROUPED, NEW_GROUPED))

OLD_GROUPED_FOOD = """\
  const food = p.food !== 'Unknown' ? p.food : '<em style="color:#999">Food not specified</em>';"""
NEW_GROUPED_FOOD = """\
  const foodHtml = buildFoodItemsHtml(p);"""
changes.append(('buildGroupedCard foodHtml', OLD_GROUPED_FOOD, NEW_GROUPED_FOOD))

OLD_GROUPED_FOOD_ROW = """\
        <div class="card-food variant-food">${food}</div>"""
NEW_GROUPED_FOOD_ROW = """\
        <div class="variant-food">${foodHtml}</div>"""
changes.append(('buildGroupedCard food row', OLD_GROUPED_FOOD_ROW, NEW_GROUPED_FOOD_ROW))

# ─────────────────────────────────────────────
# 8. getFilteredData — update type filter + search
# ─────────────────────────────────────────────
changes.append(('typeFilter v2',
  "  if (typeFilter !== 'all') data = data.filter(p => p.wineType === typeFilter);",
  "  if (typeFilter !== 'all') data = data.filter(p => (p.drinkItems?.[0]?.wineType || p.wineType) === typeFilter);"))

OLD_SEARCH = """\
  if (searchQuery) {
    const q = searchQuery.toLowerCase();
    data = data.filter(p =>
      (p.wine || '').toLowerCase().includes(q) ||
      (p.food || '').toLowerCase().includes(q) ||
      (p.text || '').toLowerCase().includes(q)
    );
  }"""
NEW_SEARCH = """\
  if (searchQuery) {
    const q = searchQuery.toLowerCase();
    data = data.filter(p =>
      (p.drinkName || p.wine || '').toLowerCase().includes(q) ||
      (p.drinkItems || []).some(i => ((i.brand||'')+' '+(i.product||'')).toLowerCase().includes(q)) ||
      (p.foodItems  || []).some(i => ((i.brand||'')+' '+(i.product||'')).toLowerCase().includes(q)) ||
      (p.food || '').toLowerCase().includes(q) ||
      (p.text || '').toLowerCase().includes(q)
    );
  }"""
changes.append(('search v2', OLD_SEARCH, NEW_SEARCH))

# ─────────────────────────────────────────────
# 9. updateShoppingList — item-level dedup by brand+product
# ─────────────────────────────────────────────
OLD_SHOPPING = """\
function updateShoppingList() {
  const liked = PAIRINGS_DATA.filter(p => {
    const r = getRating(p.id);
    return [r.wineRating,r.foodRating,r.pairingRating].some(x => x === 'loved' || x === 'liked');
  });
  document.getElementById('fabBadge').textContent = liked.length;

  const body = document.getElementById('sidebarBody');
  if (liked.length === 0) {
    body.innerHTML = '<div class="sidebar-empty">Mark pairings as "Loved it" or "Liked it" to build your list!</div>';
    return;
  }

  const byStore = {};
  liked.forEach(p => {
    const key = p.store === 'Unknown' ? 'Other / Unknown Store' : p.store;
    if (!byStore[key]) byStore[key] = [];
    byStore[key].push(p);
  });

  body.innerHTML = Object.entries(byStore).map(([store, posts]) => `
    <div class="store-group">
      <div class="store-group-title">${store}</div>
      ${posts.map(p => {
        const r = getRating(p.id);
        const topRating = [r.wineRating,r.foodRating,r.pairingRating].find(x => x==='loved'||x==='liked') || '';
        return `<div class="list-item">
          <div class="list-wine">${p.wine !== 'Unknown' ? p.wine : '—'}</div>
          <div class="list-food">${p.food !== 'Unknown' ? p.food : '—'}</div>
          <div class="list-rating">${topRating === 'loved' ? '💚 Loved it' : topRating === 'liked' ? '💙 Liked it' : ''}</div>
        </div>`;
      }).join('')}
    </div>
  `).join('');
}"""

NEW_SHOPPING = """\
function updateShoppingList() {
  const liked = PAIRINGS_DATA.filter(p => {
    const r = getRating(p.id);
    return [r.wineRating,r.foodRating,r.pairingRating].some(x => x === 'loved' || x === 'liked');
  });
  document.getElementById('fabBadge').textContent = liked.length;

  const body = document.getElementById('sidebarBody');
  if (liked.length === 0) {
    body.innerHTML = '<div class="sidebar-empty">Mark pairings as "Loved it" or "Liked it" to build your list!</div>';
    return;
  }

  // Deduplicate items by brand|product, grouped by store
  const storeMap = {};
  const addItem = (item, icon, fallbackStore) => {
    const storeKey = (item.store && item.store !== 'Unknown') ? item.store
      : (fallbackStore && fallbackStore !== 'Unknown') ? fallbackStore
      : 'Other / Unknown Store';
    const key = (item.brand||'')+'\x00'+(item.product||'');
    if (!storeMap[storeKey]) storeMap[storeKey] = new Map();
    if (storeMap[storeKey].has(key)) { storeMap[storeKey].get(key).count++; }
    else { storeMap[storeKey].set(key, {brand:item.brand, product:item.product, icon, count:1}); }
  };

  liked.forEach(p => {
    const fallback = p.store;
    const drinks = p.drinkItems?.length ? p.drinkItems : [{brand:null, product:p.wine||null, store:fallback}];
    const foods  = p.foodItems?.length  ? p.foodItems  : (p.food && p.food!=='Unknown' ? [{brand:null,product:p.food,store:fallback}] : []);
    drinks.forEach(i => addItem(i, '🍷', fallback));
    foods.forEach(i  => addItem(i, '🍽️', fallback));
  });

  body.innerHTML = Object.entries(storeMap).map(([store, items]) => `
    <div class="store-group">
      <div class="store-group-title">${store}</div>
      ${Array.from(items.values()).map(item => `
        <div class="list-item">
          <span class="list-item-icon">${item.icon}</span>
          <div class="list-item-info">
            ${item.brand ? `<span class="list-item-brand">${escapeHtml(item.brand)} — </span>` : ''}
            <span class="list-item-product">${escapeHtml(item.product||'—')}</span>
          </div>
          ${item.count > 1 ? `<span class="list-item-count">${item.count}×</span>` : ''}
        </div>`).join('')}
    </div>`).join('');
}"""

changes.append(('updateShoppingList v2', OLD_SHOPPING, NEW_SHOPPING))

# ─────────────────────────────────────────────
# 10. isInboxCandidate — use drinkName
# ─────────────────────────────────────────────
OLD_INBOX_CANDIDATE = """\
  const wine = (p.wine || '').toLowerCase();
  return wine.startsWith('various') ||
         wine === 'cocktail' ||
         (p.wine || '').split(' / ').length >= 3;"""
NEW_INBOX_CANDIDATE = """\
  const name = (p.drinkName || p.wine || '').toLowerCase();
  return name.startsWith('various') ||
         name === 'cocktail' ||
         (p.drinkName || p.wine || '').split(' / ').length >= 3;"""
changes.append(('isInboxCandidate drinkName', OLD_INBOX_CANDIDATE, NEW_INBOX_CANDIDATE))

# ─────────────────────────────────────────────
# Apply
# ─────────────────────────────────────────────
result = src
for desc, old, new in changes:
    count = result.count(old)
    if count == 0:
        print(f'ERROR: [{desc}] NOT FOUND — aborting')
        sys.exit(1)
    if count > 1:
        print(f'WARNING: [{desc}] matched {count} times')
    result = result.replace(old, new)
    print(f'  OK  [{desc}] ({count} replacement(s))')

with open(HTML_FILE, 'w', encoding='utf-8') as f:
    f.write(result)
print(f'\nDone. Wrote {HTML_FILE}')
