#!/usr/bin/env python3
"""
Phase 4c: Multi-food support in inbox — "+ add food" rows, one card per food on export.
Run from project root: python scripts/_patch_phase4c.py
"""
import sys

HTML_FILE = 'index.html'

with open(HTML_FILE, 'r', encoding='utf-8') as f:
    src = f.read()

changes = []

# ─────────────────────────────────────────────
# 1. Add CSS for food rows and btn-link
# ─────────────────────────────────────────────
changes.append(('food row CSS', '/* form */\n.inbox-slide-form {', """\
/* food rows */
.inbox-foods { display: flex; flex-direction: column; gap: 4px; }
.inbox-food-row { display: flex; gap: 6px; align-items: center; }
.inbox-food-row .split-food { flex: 1; }
.btn-link {
  background: none; border: none; color: var(--burgundy);
  font-size: 0.8rem; cursor: pointer; padding: 2px 0;
  text-decoration: underline; text-underline-offset: 2px;
  align-self: flex-start;
}
.btn-link:hover { opacity: 0.7; }
/* form */
.inbox-slide-form {"""))

# ─────────────────────────────────────────────
# 2. Replace addedPairings / skippedCount with
#    flat allAdded list [{p, si, pi}]
# ─────────────────────────────────────────────
changes.append(('addedPairings flatten',
  "  const addedPairings = decisions.filter(s => s?.action === 'pairing');\n  const skippedCount = decisions.filter(s => s?.action === 'skip').length;",
  """\
  // Flatten all pairing decisions to {p, si, pi} for multi-food support
  const allAdded = [];
  decisions.forEach((slide, si) => {
    if (slide?.action === 'pairing') {
      const pairs = slide.pairings || (slide.wine ? [slide] : []);
      pairs.forEach((p, pi) => allAdded.push({ p, si, pi }));
    }
  });
  const skippedCount = decisions.filter(s => s?.action === 'skip').length;"""))

# ─────────────────────────────────────────────
# 3. Update slide counter to use allAdded.length
# ─────────────────────────────────────────────
changes.append(('counter allAdded',
  "${addedPairings.length} added, ${skippedCount} skipped",
  "${allAdded.length} added, ${skippedCount} skipped"))

# ─────────────────────────────────────────────
# 4. Replace form section (single food → multi-food rows)
# ─────────────────────────────────────────────
OLD_FORM = """\
  // ── form (pre-populated from current slide decision if any) ──
  const dec = decisions[cur] || {};
  const fw = escapeHtml(dec.wine || '');
  const ff = escapeHtml(dec.food || '');
  const fs = dec.store || 'Unknown';
  const ft = dec.wineType || 'Unknown';
  const storeOpts = ["Unknown","Trader Joe's","Costco","Aldi"]
    .map(s => `<option${s===fs?' selected':''}>${s}</option>`).join('');
  const typeOpts = ["Unknown","Red","White","Rosé","Sparkling","Orange"]
    .map(t => `<option${t===ft?' selected':''}>${t}</option>`).join('');

  const formHtml = `<div class="inbox-slide-form">
    <div class="inbox-form-row">
      <input class="split-wine" id="inbox-wine-${postId}" list="wineAC" placeholder="Wine name..." value="${fw}">
      <input class="split-food" id="inbox-food-${postId}" list="foodAC" placeholder="Food / snack..." value="${ff}">
    </div>
    <div class="inbox-form-row">
      <select class="split-store" id="inbox-store-${postId}">${storeOpts}</select>
      <select class="split-type" id="inbox-type-${postId}">${typeOpts}</select>
      <div class="inbox-form-actions">
        <button class="btn-secondary" onclick="skipInboxSlide('${postId}')">Skip</button>
        <button class="btn-primary" onclick="addInboxPairing('${postId}')">Add Pairing</button>
      </div>
    </div>
  </div>`;"""

NEW_FORM = """\
  // ── form (pre-populated from current slide decision if any) ──
  const dec = decisions[cur];
  const decPairs = dec?.pairings || (dec?.wine ? [dec] : []);
  const fw = escapeHtml(decPairs[0]?.wine || '');
  const initFoods = decPairs.map(p => p.food || '').filter(Boolean);
  if (initFoods.length === 0) initFoods.push('');
  const fs = decPairs[0]?.store || 'Unknown';
  const ft = decPairs[0]?.wineType || 'Unknown';
  const storeOpts = ["Unknown","Trader Joe's","Costco","Aldi"]
    .map(s => `<option${s===fs?' selected':''}>${s}</option>`).join('');
  const typeOpts = ["Unknown","Red","White","Rosé","Sparkling","Orange"]
    .map(t => `<option${t===ft?' selected':''}>${t}</option>`).join('');
  const foodRowsHtml = initFoods.map(f =>
    `<div class="inbox-food-row"><input class="split-food" list="foodAC" placeholder="Food / snack..." value="${escapeHtml(f)}"><button class="split-remove-btn" onclick="removeInboxFoodRow(this)" title="Remove">✕</button></div>`
  ).join('');

  const formHtml = `<div class="inbox-slide-form">
    <div class="inbox-form-row">
      <input class="split-wine" id="inbox-wine-${postId}" list="wineAC" placeholder="Wine name..." value="${fw}">
    </div>
    <div class="inbox-foods" id="inbox-foods-${postId}">${foodRowsHtml}</div>
    <button class="btn-link" onclick="addInboxFoodRow('${postId}')">+ add food</button>
    <div class="inbox-form-row" style="margin-top:6px">
      <select class="split-store" id="inbox-store-${postId}">${storeOpts}</select>
      <select class="split-type" id="inbox-type-${postId}">${typeOpts}</select>
      <div class="inbox-form-actions">
        <button class="btn-secondary" onclick="skipInboxSlide('${postId}')">Skip</button>
        <button class="btn-primary" onclick="addInboxPairing('${postId}')">Add Pairing</button>
      </div>
    </div>
  </div>`;"""

changes.append(('form multi-food', OLD_FORM, NEW_FORM))

# ─────────────────────────────────────────────
# 5. Replace addedHtml section to use allAdded
# ─────────────────────────────────────────────
OLD_ADDED = """\
  let addedHtml = '';
  if (addedPairings.length > 0) {
    const rows = addedPairings.map(s => {
      const si = decisions.indexOf(s);
      return `<div class="inbox-added-row">
        <span class="inbox-added-info">${escapeHtml(s.wine||'?')} + ${escapeHtml(s.food||'?')}${s.store&&s.store!=='Unknown'?' · '+s.store:''}</span>
        <button class="split-remove-btn" onclick="removeInboxPairing('${postId}',${si})" title="Remove">✕</button>
      </div>`;
    }).join('');
    addedHtml = `<div class="inbox-added-list">
      <div class="inbox-added-header">${addedPairings.length} pairing${addedPairings.length!==1?'s':''} added</div>
      ${rows}
    </div>`;
  }"""

NEW_ADDED = """\
  let addedHtml = '';
  if (allAdded.length > 0) {
    const rows = allAdded.map(({ p, si, pi }) =>
      `<div class="inbox-added-row">
        <span class="inbox-added-info">${escapeHtml(p.wine||'?')} + ${escapeHtml(p.food||'?')}${p.store&&p.store!=='Unknown'?' · '+p.store:''}</span>
        <button class="split-remove-btn" onclick="removeInboxPairing('${postId}',${si},${pi})" title="Remove">✕</button>
      </div>`
    ).join('');
    addedHtml = `<div class="inbox-added-list">
      <div class="inbox-added-header">${allAdded.length} pairing${allAdded.length!==1?'s':''} added</div>
      ${rows}
    </div>`;
  }"""

changes.append(('addedHtml allAdded', OLD_ADDED, NEW_ADDED))

# ─────────────────────────────────────────────
# 6. Replace addInboxPairing to read multi-food rows
# ─────────────────────────────────────────────
OLD_ADD_PAIRING = """\
function addInboxPairing(postId) {
  const wine = (document.getElementById('inbox-wine-'+postId)?.value || '').trim();
  const food = (document.getElementById('inbox-food-'+postId)?.value || '').trim();
  const store = document.getElementById('inbox-store-'+postId)?.value || 'Unknown';
  const wineType = document.getElementById('inbox-type-'+postId)?.value || 'Unknown';
  if (!wine && !food) { alert('Enter at least a wine name or food.'); return; }
  if (!inboxReviews[postId]) inboxReviews[postId] = {};
  if (!inboxReviews[postId].slides) inboxReviews[postId].slides = [];
  const slides = PAIRINGS_DATA.find(x => x.id === postId)?.slideshowImages || [];
  const cur = slides.length ? (inboxSlideIdx[postId] || 0) : inboxReviews[postId].slides.length;
  inboxReviews[postId].slides[cur] = { action:'pairing', wine:wine||'Unknown', food:food||'Unknown', store, wineType };
  saveInboxReviews();
  if (slides.length) advanceToNextUnreviewed(postId);
  refreshInboxPost(postId);
}"""

NEW_ADD_PAIRING = """\
function addInboxPairing(postId) {
  const wine = (document.getElementById('inbox-wine-'+postId)?.value || '').trim();
  const store = document.getElementById('inbox-store-'+postId)?.value || 'Unknown';
  const wineType = document.getElementById('inbox-type-'+postId)?.value || 'Unknown';
  const foods = Array.from(document.querySelectorAll('#inbox-foods-'+postId+' .split-food'))
    .map(el => el.value.trim()).filter(Boolean);
  if (!wine && foods.length === 0) { alert('Enter at least a wine name or food.'); return; }
  if (!inboxReviews[postId]) inboxReviews[postId] = {};
  if (!inboxReviews[postId].slides) inboxReviews[postId].slides = [];
  const slides = PAIRINGS_DATA.find(x => x.id === postId)?.slideshowImages || [];
  const cur = slides.length ? (inboxSlideIdx[postId] || 0) : inboxReviews[postId].slides.length;
  const pairings = foods.length > 0
    ? foods.map(food => ({ wine: wine || 'Unknown', food, store, wineType }))
    : [{ wine: wine || 'Unknown', food: 'Unknown', store, wineType }];
  inboxReviews[postId].slides[cur] = { action: 'pairing', pairings };
  saveInboxReviews();
  if (slides.length) advanceToNextUnreviewed(postId);
  refreshInboxPost(postId);
}"""

changes.append(('addInboxPairing multi-food', OLD_ADD_PAIRING, NEW_ADD_PAIRING))

# ─────────────────────────────────────────────
# 7. Replace removeInboxPairing + add food row helpers
# ─────────────────────────────────────────────
OLD_REMOVE = """\
function removeInboxPairing(postId, slideIdx) {
  if (!inboxReviews[postId]?.slides) return;
  inboxReviews[postId].slides[slideIdx] = null;
  saveInboxReviews();
  refreshInboxPost(postId);
}"""

NEW_REMOVE = """\
function removeInboxPairing(postId, slideIdx, pairingIdx) {
  const slide = inboxReviews[postId]?.slides?.[slideIdx];
  if (!slide) return;
  if (slide.pairings) {
    slide.pairings.splice(pairingIdx, 1);
    if (slide.pairings.length === 0) inboxReviews[postId].slides[slideIdx] = null;
  } else {
    inboxReviews[postId].slides[slideIdx] = null;
  }
  saveInboxReviews();
  refreshInboxPost(postId);
}

function addInboxFoodRow(postId) {
  const container = document.getElementById('inbox-foods-' + postId);
  if (!container) return;
  const div = document.createElement('div');
  div.className = 'inbox-food-row';
  div.innerHTML = '<input class="split-food" list="foodAC" placeholder="Food / snack..."><button class="split-remove-btn" onclick="removeInboxFoodRow(this)" title="Remove">✕</button>';
  container.appendChild(div);
  div.querySelector('input').focus();
}

function removeInboxFoodRow(btn) {
  const container = btn.closest('.inbox-foods');
  if (!container) return;
  const rows = container.querySelectorAll('.inbox-food-row');
  if (rows.length <= 1) { btn.previousElementSibling.value = ''; return; }
  btn.closest('.inbox-food-row').remove();
}"""

changes.append(('removeInboxPairing + food helpers', OLD_REMOVE, NEW_REMOVE))

# ─────────────────────────────────────────────
# 8. Update exportInboxJSON to flatMap pairings
# ─────────────────────────────────────────────
changes.append(('export flatMap pairings',
  "      ? (review.slides || []).filter(s => s?.action === 'pairing')\n      : (review.splits || []);",
  "      ? (review.slides || []).filter(s => s?.action === 'pairing').flatMap(s => s.pairings || (s.wine ? [{ wine: s.wine, food: s.food, store: s.store, wineType: s.wineType }] : []))\n      : (review.splits || []);"))

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
