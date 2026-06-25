#!/usr/bin/env python3
"""
Phase 3 patch: group cards by wine name with variant arrow navigation.
Run from project root: python scripts/_patch_phase3.py
"""
import sys

HTML_FILE = 'index.html'

with open(HTML_FILE, 'r', encoding='utf-8') as f:
    src = f.read()

changes = []

# ─────────────────────────────────────────────
# 1. Add variant-nav CSS (after .variant-dot.active ... tab-bar section)
# ─────────────────────────────────────────────
changes.append(('variant nav CSS', '''\
/* TAB BAR */''', '''\
/* VARIANT NAVIGATION (grouped cards) */
.variant-food-row {
  display: flex;
  align-items: flex-start;
  gap: 5px;
}
.variant-food {
  flex: 1;
  min-width: 0;
}
.variant-btn {
  flex-shrink: 0;
  background: none;
  border: 1.5px solid #ddd;
  border-radius: 50%;
  width: 22px;
  height: 22px;
  font-size: 13px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--burgundy);
  transition: all 0.15s;
  padding: 0;
  line-height: 1;
  margin-top: 1px;
}
.variant-btn:hover { background: var(--burgundy); color: white; border-color: var(--burgundy); }
.variant-dots-row {
  display: flex;
  gap: 5px;
  margin-top: 3px;
}
.variant-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #ddd;
  cursor: pointer;
  transition: background 0.15s;
}
.variant-dot.active { background: var(--burgundy); }
.variant-count-label {
  font-size: 0.68rem;
  color: var(--text-muted);
  font-style: italic;
  margin-left: 2px;
  white-space: nowrap;
}

/* TAB BAR */'''))

# ─────────────────────────────────────────────
# 2. Add groupByWine + buildGroupedCard + cycleVariantTo after scrollToCard
# ─────────────────────────────────────────────
OLD_SCROLL_AND_FILTER = '''\
// ─── FILTER / SORT ───'''

NEW_SCROLL_AND_FILTER = '''\
// ─── WINE GROUPING ───
const groupVariantState = {};

function encodeGroupKey(wine) {
  return (wine || '').toLowerCase().trim().replace(/[^a-z0-9]/g, '_').substring(0, 40);
}

function groupByWine(posts) {
  const groups = new Map();
  for (const p of posts) {
    const key = encodeGroupKey(p.wine);
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(p);
  }
  return Array.from(groups.values());
}

function getBestStatus(posts) {
  const order = ['loved','liked','meh','disliked','not-tried'];
  let best = 'not-tried';
  for (const p of posts) {
    const r = getRating(p.id);
    const val = p.category === 'pairing' ? r.pairingRating : r.wineRating;
    if (order.indexOf(val) < order.indexOf(best)) best = val;
  }
  return best;
}

function buildGroupedCard(posts) {
  const wine = posts[0].wine;
  const gkey = encodeGroupKey(wine);
  const rawIdx = groupVariantState[gkey] || 0;
  const idx = Math.min(rawIdx, posts.length - 1);
  const p = posts[idx];

  const statusColors = {loved:'#27AE60',liked:'#2980B9',meh:'#F39C12',disliked:'#E74C3C'};
  const bestStatus = getBestStatus(posts);
  const statusDot = bestStatus !== 'not-tried'
    ? `<div class="card-status-dot" id="gdot-${gkey}" style="background:${statusColors[bestStatus]}"></div>`
    : `<div class="card-status-dot" id="gdot-${gkey}" style="display:none"></div>`;

  const prevIdx = (idx - 1 + posts.length) % posts.length;
  const nextIdx = (idx + 1) % posts.length;
  const food = p.food !== 'Unknown' ? p.food : '<em style="color:#999">Food not specified</em>';
  const dots = posts.map((_, i) =>
    `<span class="variant-dot${i===idx?' active':''}" onclick="cycleVariantTo('${gkey}',${i},event)"></span>`
  ).join('');

  return `<div class="card" id="gcard-${gkey}" onclick="openDetailModal('${p.id}')">
    ${buildImageSection(p)}
    ${statusDot}
    <div class="card-body">
      <div class="card-wine">${wine !== 'Unknown' ? wine : '<em style="color:#999;font-weight:400">Wine not specified</em>'}</div>
      <div class="variant-food-row">
        <button class="variant-btn" onclick="cycleVariantTo('${gkey}',${prevIdx},event)" title="Previous pairing">&#8249;</button>
        <div class="card-food variant-food">${food}</div>
        <button class="variant-btn" onclick="cycleVariantTo('${gkey}',${nextIdx},event)" title="Next pairing">&#8250;</button>
      </div>
      <div class="variant-dots-row">${dots}
        <span class="variant-count-label">${idx+1}/${posts.length} pairings</span>
      </div>
      <div class="card-meta">
        <span>${fmtDate(p.date)}</span>
        <span class="card-engagement"><span>👁️ ${fmtNum(p.views)}</span><span>❤️ ${fmtNum(p.likes)}</span></span>
      </div>
    </div>
  </div>`;
}

function cycleVariantTo(gkey, idx, evt) {
  if (evt) evt.stopPropagation();
  groupVariantState[gkey] = idx;
  const posts = (window._currentGroups || {})[gkey];
  if (!posts) return;
  const cardEl = document.getElementById('gcard-' + gkey);
  if (!cardEl) return;
  const temp = document.createElement('div');
  temp.innerHTML = buildGroupedCard(posts);
  cardEl.replaceWith(temp.firstElementChild);
}

// ─── FILTER / SORT ───'''

changes.append(('grouping JS', OLD_SCROLL_AND_FILTER, NEW_SCROLL_AND_FILTER))

# ─────────────────────────────────────────────
# 3. Update render() to use groups
# ─────────────────────────────────────────────
OLD_RENDER = '''\
  } else {
    empty.style.display = 'none';
    const tabTotal = PAIRINGS_DATA.map(p => getEffectivePost(p.id)).filter(p => p.category === activeTab).length;
    info.textContent = `Showing ${data.length} of ${tabTotal} posts`;
    grid.innerHTML = data.map(p => buildCard(getEffectivePost(p.id))).join('');
  }'''

NEW_RENDER = '''\
  } else {
    empty.style.display = 'none';
    const tabTotal = PAIRINGS_DATA.map(p => getEffectivePost(p.id)).filter(p => p.category === activeTab).length;
    const groups = groupByWine(data);
    window._currentGroups = {};
    groups.forEach(g => { window._currentGroups[encodeGroupKey(g[0].wine)] = g; });
    info.textContent = `Showing ${groups.length} wines (${data.length} pairings) of ${tabTotal} total`;
    grid.innerHTML = groups.map(g => g.length === 1 ? buildCard(g[0]) : buildGroupedCard(g)).join('');
  }'''

changes.append(('render grouping', OLD_RENDER, NEW_RENDER))

# ─────────────────────────────────────────────
# 4. Update updateCardStatusDot to handle grouped cards
# ─────────────────────────────────────────────
OLD_STATUS_DOT = '''\
function updateCardStatusDot(postId) {
  const dot = document.getElementById('dot-'+postId);
  if (!dot) return;
  const p = getEffectivePost(postId);
  const r = getRating(postId);
  const primaryField = p.category === 'pairing' ? 'pairingRating' : 'wineRating';
  const val = r[primaryField];
  const statusColors = {loved:'#27AE60',liked:'#2980B9',meh:'#F39C12',disliked:'#E74C3C'};
  if (val !== 'not-tried') {
    dot.style.background = statusColors[val];
    dot.style.display = '';
  } else {
    dot.style.display = 'none';
  }
}'''

NEW_STATUS_DOT = '''\
function updateCardStatusDot(postId) {
  const p = getEffectivePost(postId);
  const gkey = encodeGroupKey(p.wine);
  const groups = window._currentGroups || {};
  const statusColors = {loved:'#27AE60',liked:'#2980B9',meh:'#F39C12',disliked:'#E74C3C'};

  if (groups[gkey] && groups[gkey].length > 1) {
    const dot = document.getElementById('gdot-'+gkey);
    if (!dot) return;
    const best = getBestStatus(groups[gkey]);
    if (best !== 'not-tried') {
      dot.style.background = statusColors[best];
      dot.style.display = '';
    } else {
      dot.style.display = 'none';
    }
  } else {
    const dot = document.getElementById('dot-'+postId);
    if (!dot) return;
    const r = getRating(postId);
    const val = p.category === 'pairing' ? r.pairingRating : r.wineRating;
    if (val !== 'not-tried') {
      dot.style.background = statusColors[val];
      dot.style.display = '';
    } else {
      dot.style.display = 'none';
    }
  }
}'''

changes.append(('updateCardStatusDot grouped', OLD_STATUS_DOT, NEW_STATUS_DOT))

# ─────────────────────────────────────────────
# 5. Update scrollToCard to find grouped cards
# ─────────────────────────────────────────────
OLD_SCROLL = '''\
function scrollToCard(id) {
  const el = document.getElementById('card-'+id);
  if (el) el.scrollIntoView({behavior:'smooth', block:'center'});
}'''

NEW_SCROLL = '''\
function scrollToCard(id) {
  let el = document.getElementById('card-'+id);
  if (!el) {
    const p = getEffectivePost(id);
    if (p && p.wine) {
      const gkey = encodeGroupKey(p.wine);
      const group = (window._currentGroups || {})[gkey];
      if (group && group.length > 1) {
        const vIdx = group.findIndex(post => post.id === id);
        if (vIdx !== -1) cycleVariantTo(gkey, vIdx, null);
        el = document.getElementById('gcard-'+gkey);
      }
    }
  }
  if (el) el.scrollIntoView({behavior:'smooth', block:'center'});
}'''

changes.append(('scrollToCard grouped', OLD_SCROLL, NEW_SCROLL))

# ─────────────────────────────────────────────
# Apply
# ─────────────────────────────────────────────
result = src
for desc, old, new in changes:
    count = result.count(old)
    if count == 0:
        print(f'ERROR: [{desc}] old string NOT FOUND — aborting')
        sys.exit(1)
    if count > 1:
        print(f'WARNING: [{desc}] matched {count} times')
    result = result.replace(old, new)
    print(f'  OK  [{desc}] ({count} replacement(s))')

with open(HTML_FILE, 'w', encoding='utf-8') as f:
    f.write(result)

print(f'\nDone. Wrote {HTML_FILE}')
