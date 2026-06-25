#!/usr/bin/env python3
"""
Phase 6: Edit modal + inbox form use v2 brand/product item rows.
- Edit modal: drinkName, drinkType, dynamic drinkItems + foodItems rows
- Inbox form: per-slide drinkItems + foodItems rows (brand + product each)
- Export: creates cards with v2 drinkItems/foodItems arrays
Run from project root: python scripts/_patch_phase6.py
"""
import sys
HTML_FILE = 'index.html'
with open(HTML_FILE, 'r', encoding='utf-8') as f:
    src = f.read()
changes = []

# ─────────────────────────────────────────────
# 1. CSS for edit item rows
# ─────────────────────────────────────────────
changes.append(('edit-item-row CSS', '.list-item-count {\n  font-size: 0.68rem; color: var(--text-muted);\n  background: var(--cream-dark); border-radius: 10px; padding: 1px 6px; flex-shrink: 0;\n}', """\
.list-item-count {
  font-size: 0.68rem; color: var(--text-muted);
  background: var(--cream-dark); border-radius: 10px; padding: 1px 6px; flex-shrink: 0;
}
/* edit + inbox item rows */
.edit-section-label {
  font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.06em; color: var(--text-muted); margin: 10px 0 5px;
}
.edit-item-row {
  display: flex; gap: 5px; flex-wrap: wrap; align-items: center;
  margin-bottom: 5px; padding: 5px 8px; background: var(--cream); border-radius: 8px;
}
.edit-brand { width: 110px; min-width: 80px; font-size: 0.8rem; }
.edit-product { flex: 1; min-width: 130px; font-size: 0.8rem; }
.edit-pt, .edit-wt, .edit-cat, .edit-store { font-size: 0.73rem; padding: 4px 5px; }"""))

# ─────────────────────────────────────────────
# 2. Replace edit modal HTML
# ─────────────────────────────────────────────
OLD_EDIT_HTML = """\
<div id="editModal" class="modal-overlay" style="display:none" onclick="if(event.target===this)closeEditModal()">
  <div class="modal-box">
    <div class="modal-header">
      <h3>Edit Pairing</h3>
      <button onclick="closeEditModal()" class="modal-close">✕</button>
    </div>
    <div class="modal-body">
      <label>Wine Name<input type="text" id="editWine" placeholder="Wine name"></label>
      <label>Food / Snack<input type="text" id="editFood" placeholder="Food or snack"></label>
      <label>Store
        <select id="editStore">
          <option value="Trader Joe's">Trader Joe's</option>
          <option value="Costco">Costco</option>
          <option value="Aldi">Aldi</option>
          <option value="Unknown">Unknown / Other</option>
        </select>
      </label>
      <label>Wine Type
        <select id="editWineType">
          <option value="Red">Red</option>
          <option value="White">White</option>
          <option value="Rosé">Rosé</option>
          <option value="Sparkling">Sparkling</option>
          <option value="Orange">Orange</option>
          <option value="Unknown">Unknown</option>
        </select>
      </label>
      <label>Tab / Category
        <select id="editCategory">
          <option value="pairing">Wine Pairing</option>
          <option value="porch-pounder">Porch Pounder</option>
          <option value="recipe">Recipe</option>
          <option value="hidden">Hide this post</option>
        </select>
      </label>
      <label>Wine Image URL<input type="text" id="editWineImage" placeholder="https://..."></label>
      <label>Food Image URL<input type="text" id="editFoodImage" placeholder="https://..."></label>
    </div>
    <div class="modal-footer">
      <button onclick="resetEdit()" class="btn-secondary">Reset to original</button>
      <button onclick="saveEdit()" class="btn-primary">Save changes</button>
    </div>
  </div>
</div>"""

NEW_EDIT_HTML = """\
<div id="editModal" class="modal-overlay" style="display:none" onclick="if(event.target===this)closeEditModal()">
  <div class="modal-box">
    <div class="modal-header">
      <h3>Edit Pairing</h3>
      <button onclick="closeEditModal()" class="modal-close">✕</button>
    </div>
    <div class="modal-body">
      <label>Display Name<input type="text" id="editDrinkName" placeholder="Wine or recipe name"></label>
      <label>Drink Type
        <select id="editDrinkType">
          <option value="Wine">Wine</option>
          <option value="Spritz Recipe">Spritz Recipe</option>
          <option value="Cocktail Recipe">Cocktail Recipe</option>
          <option value="Wine Cocktail Recipe">Wine Cocktail Recipe</option>
          <option value="Non-Alcoholic Drink">Non-Alcoholic Drink</option>
          <option value="Non-Alcoholic Recipe">Non-Alcoholic Recipe</option>
        </select>
      </label>
      <div class="edit-section-label">🍷 Drink Items</div>
      <div id="editDrinkItemsList"></div>
      <button class="btn-link" onclick="addEditDrinkItem()">+ add drink item</button>
      <div class="edit-section-label" style="margin-top:10px">🍽️ Food Items</div>
      <div id="editFoodItemsList"></div>
      <button class="btn-link" onclick="addEditFoodItem()">+ add food item</button>
      <label style="margin-top:10px">Tab / Category
        <select id="editCategory">
          <option value="pairing">Wine Pairing</option>
          <option value="porch-pounder">Porch Pounder</option>
          <option value="recipe">Recipe</option>
          <option value="hidden">Hide this post</option>
        </select>
      </label>
      <label>Wine Image URL<input type="text" id="editWineImage" placeholder="https://..."></label>
      <label>Food Image URL<input type="text" id="editFoodImage" placeholder="https://..."></label>
    </div>
    <div class="modal-footer">
      <button onclick="resetEdit()" class="btn-secondary">Reset to original</button>
      <button onclick="saveEdit()" class="btn-primary">Save changes</button>
    </div>
  </div>
</div>"""

changes.append(('edit modal HTML', OLD_EDIT_HTML, NEW_EDIT_HTML))

# ─────────────────────────────────────────────
# 3. Replace openEditModal + saveEdit with
#    new helpers + updated functions
# ─────────────────────────────────────────────
OLD_EDIT_JS = """\
function openEditModal(id) {
  editingId = id;
  const post = getEffectivePost(id);
  if (!post) return;
  document.getElementById('editWine').value = post.wine || '';
  document.getElementById('editFood').value = post.food || '';
  document.getElementById('editStore').value = post.store || 'Unknown';
  document.getElementById('editWineType').value = post.wineType || 'Unknown';
  document.getElementById('editCategory').value = post.category || 'pairing';
  document.getElementById('editWineImage').value = post.wineImageUrl || '';
  document.getElementById('editFoodImage').value = post.foodImageUrl || '';
  document.getElementById('editModal').style.display = 'flex';
}

function closeEditModal() {
  document.getElementById('editModal').style.display = 'none';
  editingId = null;
}

function saveEdit() {
  if (!editingId) return;
  const saved = JSON.parse(localStorage.getItem(LS_KEY) || '{}');
  if (!saved[editingId]) saved[editingId] = {};
  saved[editingId].editOverrides = {
    wine: document.getElementById('editWine').value,
    food: document.getElementById('editFood').value,
    store: document.getElementById('editStore').value,
    wineType: document.getElementById('editWineType').value,
    category: document.getElementById('editCategory').value,
    wineImageUrl: document.getElementById('editWineImage').value || null,
    foodImageUrl: document.getElementById('editFoodImage').value || null,
  };
  localStorage.setItem(LS_KEY, JSON.stringify(saved));
  // Re-sync ratings object
  ratings = saved;
  closeEditModal();
  renderPicks();
  render();
}"""

NEW_EDIT_JS = """\
// ── shared item row builders (used by edit modal AND inbox) ──
function buildDrinkItemRow(item) {
  const div = document.createElement('div');
  div.className = 'edit-item-row';
  const s  = item.store       || 'Unknown';
  const pt = item.productType || 'wine';
  const wt = item.wineType    || 'N/A';
  const storeOpts = ["Trader Joe's","Costco","Aldi","Unknown"]
    .map(x => `<option${x===s?' selected':''}>${x}</option>`).join('');
  const ptOpts = ["wine","spirit","liqueur","beer","mixer","ingredient"]
    .map(x => `<option${x===pt?' selected':''}>${x}</option>`).join('');
  const wtOpts = ["Red","White","Rosé","Sparkling","Orange","N/A"]
    .map(x => `<option${x===wt?' selected':''}>${x}</option>`).join('');
  div.innerHTML = `<input class="edit-brand" placeholder="Brand…" value="${escapeHtml(item.brand||'')}">
    <input class="edit-product" placeholder="Product…" value="${escapeHtml(item.product||'')}">
    <select class="edit-pt">${ptOpts}</select>
    <select class="edit-wt">${wtOpts}</select>
    <select class="edit-store">${storeOpts}</select>
    <button class="split-remove-btn" onclick="this.closest('.edit-item-row').remove()" title="Remove">✕</button>`;
  return div;
}

function buildFoodItemRow(item) {
  const div = document.createElement('div');
  div.className = 'edit-item-row';
  const s   = item.store    || 'Unknown';
  const cat = item.category || 'other';
  const storeOpts = ["Trader Joe's","Costco","Aldi","Unknown"]
    .map(x => `<option${x===s?' selected':''}>${x}</option>`).join('');
  const catOpts = ["chips/snack","dip/spread","cheese","charcuterie","bread/crackers","fruit","sweet/dessert","meal","condiment","pickled/preserved","other"]
    .map(x => `<option${x===cat?' selected':''}>${x}</option>`).join('');
  div.innerHTML = `<input class="edit-brand" placeholder="Brand…" value="${escapeHtml(item.brand||'')}">
    <input class="edit-product" placeholder="Product…" value="${escapeHtml(item.product||'')}">
    <select class="edit-cat">${catOpts}</select>
    <select class="edit-store">${storeOpts}</select>
    <button class="split-remove-btn" onclick="this.closest('.edit-item-row').remove()" title="Remove">✕</button>`;
  return div;
}

function addEditDrinkItem() {
  document.getElementById('editDrinkItemsList')
    .appendChild(buildDrinkItemRow({brand:'',product:'',productType:'wine',wineType:'N/A',store:'Unknown'}));
}
function addEditFoodItem() {
  document.getElementById('editFoodItemsList')
    .appendChild(buildFoodItemRow({brand:'',product:'',category:'other',store:'Unknown'}));
}

function collectDrinkRows(containerSelector) {
  return Array.from(document.querySelectorAll(containerSelector + ' .edit-item-row')).map(row => ({
    brand:       row.querySelector('.edit-brand')?.value.trim() || null,
    product:     row.querySelector('.edit-product')?.value.trim() || 'Unknown',
    productType: row.querySelector('.edit-pt')?.value  || 'wine',
    wineType:    row.querySelector('.edit-wt')?.value  || 'N/A',
    store:       row.querySelector('.edit-store')?.value || 'Unknown',
    price:null, vintage:null, region:null, amount:null, notes:null, needsReview:false,
  }));
}
function collectFoodRows(containerSelector) {
  return Array.from(document.querySelectorAll(containerSelector + ' .edit-item-row')).map(row => ({
    brand:    row.querySelector('.edit-brand')?.value.trim() || null,
    product:  row.querySelector('.edit-product')?.value.trim() || 'Unknown',
    category: row.querySelector('.edit-cat')?.value  || 'other',
    store:    row.querySelector('.edit-store')?.value || 'Unknown',
    price:null, notes:null, needsReview:false,
  }));
}

// ── edit modal ──
function openEditModal(id) {
  editingId = id;
  const post = getEffectivePost(id);
  if (!post) return;
  document.getElementById('editDrinkName').value = post.drinkName || post.wine || '';
  const dt = document.getElementById('editDrinkType');
  dt.value = post.drinkType || 'Wine';
  if (!dt.value) dt.value = 'Wine';
  document.getElementById('editCategory').value  = post.category    || 'pairing';
  document.getElementById('editWineImage').value = post.wineImageUrl || '';
  document.getElementById('editFoodImage').value = post.foodImageUrl || '';

  const drinkList = document.getElementById('editDrinkItemsList');
  drinkList.innerHTML = '';
  const di = post.drinkItems?.length
    ? post.drinkItems
    : [{brand:null, product:post.wine||'', productType:'wine', wineType:post.wineType||'N/A', store:post.store||'Unknown'}];
  di.forEach(item => drinkList.appendChild(buildDrinkItemRow(item)));

  const foodList = document.getElementById('editFoodItemsList');
  foodList.innerHTML = '';
  const fi = post.foodItems?.length
    ? post.foodItems
    : (post.food && post.food!=='Unknown' ? [{brand:null,product:post.food,category:'other',store:post.store||'Unknown'}] : []);
  fi.forEach(item => foodList.appendChild(buildFoodItemRow(item)));

  document.getElementById('editModal').style.display = 'flex';
}

function closeEditModal() {
  document.getElementById('editModal').style.display = 'none';
  editingId = null;
}

function saveEdit() {
  if (!editingId) return;
  const drinkItems = collectDrinkRows('#editDrinkItemsList');
  const foodItems  = collectFoodRows('#editFoodItemsList');
  const drinkName  = document.getElementById('editDrinkName').value.trim() || (drinkItems[0]?.product || 'Unknown');
  const saved = JSON.parse(localStorage.getItem(LS_KEY) || '{}');
  if (!saved[editingId]) saved[editingId] = {};
  saved[editingId].editOverrides = {
    drinkName, drinkType: document.getElementById('editDrinkType').value,
    drinkItems, foodItems,
    // legacy compat (kept so old code paths still work)
    wine:     drinkName,
    food:     foodItems.map(f=>f.product).filter(Boolean).join(' + ') || 'Unknown',
    store:    drinkItems[0]?.store || foodItems[0]?.store || 'Unknown',
    wineType: drinkItems[0]?.wineType || 'N/A',
    category: document.getElementById('editCategory').value,
    wineImageUrl: document.getElementById('editWineImage').value || null,
    foodImageUrl: document.getElementById('editFoodImage').value || null,
  };
  localStorage.setItem(LS_KEY, JSON.stringify(saved));
  ratings = saved;
  closeEditModal();
  renderPicks();
  render();
}"""

changes.append(('edit modal JS', OLD_EDIT_JS, NEW_EDIT_JS))

# ─────────────────────────────────────────────
# 4. Update allAdded in buildInboxPost (per-slide, new format)
# ─────────────────────────────────────────────
OLD_ALL_ADDED = """\
  // Flatten all pairing decisions to {p, si, pi} for multi-food support
  const allAdded = [];
  decisions.forEach((slide, si) => {
    if (slide?.action === 'pairing') {
      const pairs = slide.pairings || (slide.wine ? [slide] : []);
      pairs.forEach((p, pi) => allAdded.push({ p, si, pi }));
    }
  });
  const skippedCount = decisions.filter(s => s?.action === 'skip').length;"""

NEW_ALL_ADDED = """\
  // Per-slide pairing decisions (handles both old pairings and new drinkItems/foodItems)
  const allAdded = decisions.map((slide, si) =>
    slide?.action === 'pairing' ? { si, slide } : null
  ).filter(Boolean);
  const skippedCount = decisions.filter(s => s?.action === 'skip').length;"""

changes.append(('allAdded per-slide', OLD_ALL_ADDED, NEW_ALL_ADDED))

# ─────────────────────────────────────────────
# 5. Replace inbox form section in buildInboxPost
# ─────────────────────────────────────────────
OLD_INBOX_FORM = """\
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

NEW_INBOX_FORM = """\
  // ── form (pre-populated from current slide decision if any) ──
  const dec = decisions[cur];
  let initDrinks = [], initFoods = [];
  if (dec?.action === 'pairing') {
    if (dec.drinkItems || dec.foodItems) {
      initDrinks = dec.drinkItems || [];
      initFoods  = dec.foodItems  || [];
    } else if (dec.pairings?.length) {
      // backwards compat with old pairings format
      initDrinks = dec.pairings.map(p => ({brand:null,product:p.wine||'',productType:'wine',wineType:p.wineType||'N/A',store:p.store||'Unknown'}));
      initFoods  = dec.pairings.map(p => ({brand:null,product:p.food||'',category:'other',store:p.store||'Unknown'}));
    }
  }
  if (!initDrinks.length) initDrinks = [{brand:'',product:'',productType:'wine',wineType:'N/A',store:'Unknown'}];
  if (!initFoods.length)  initFoods  = [{brand:'',product:'',category:'other',store:'Unknown'}];
  const drinkRowsHtml = initDrinks.map(d => buildDrinkItemRow(d).outerHTML).join('');
  const foodRowsHtml  = initFoods.map(f  => buildFoodItemRow(f).outerHTML).join('');

  const formHtml = `<div class="inbox-slide-form">
    <div class="edit-section-label">🍷 Drink</div>
    <div id="inbox-drinks-${postId}">${drinkRowsHtml}</div>
    <button class="btn-link" onclick="addInboxDrinkRow('${postId}')">+ add drink item</button>
    <div class="edit-section-label" style="margin-top:8px">🍽️ Food</div>
    <div id="inbox-foods-${postId}">${foodRowsHtml}</div>
    <button class="btn-link" onclick="addInboxFoodRow('${postId}')">+ add food item</button>
    <div class="inbox-form-row" style="margin-top:8px">
      <div class="inbox-form-actions">
        <button class="btn-secondary" onclick="skipInboxSlide('${postId}')">Skip</button>
        <button class="btn-primary" onclick="addInboxPairing('${postId}')">Add Pairing</button>
      </div>
    </div>
  </div>`;"""

changes.append(('inbox form v2', OLD_INBOX_FORM, NEW_INBOX_FORM))

# ─────────────────────────────────────────────
# 6. Replace addedHtml section in buildInboxPost
# ─────────────────────────────────────────────
OLD_ADDED_HTML = """\
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

NEW_ADDED_HTML = """\
  let addedHtml = '';
  if (allAdded.length > 0) {
    const rows = allAdded.map(({ si, slide }) => {
      let summary = '';
      if (slide.drinkItems || slide.foodItems) {
        const dStr = (slide.drinkItems||[]).filter(d=>d.product).map(d=>d.brand?`${d.brand} ${d.product}`:d.product).join(' + ');
        const fStr = (slide.foodItems||[]).filter(f=>f.product).map(f=>f.brand?`${f.brand} ${f.product}`:f.product).join(', ');
        summary = [dStr&&'🍷 '+dStr, fStr&&'🍽️ '+fStr].filter(Boolean).join(' · ');
      } else if (slide.pairings?.length) {
        summary = `${slide.pairings[0].wine||'?'} + ${slide.pairings[0].food||'?'}`;
      }
      return `<div class="inbox-added-row">
        <span class="inbox-added-info">${escapeHtml(summary||'(slide '+si+')')}</span>
        <button class="split-remove-btn" onclick="removeInboxPairing('${postId}',${si},0)" title="Remove">✕</button>
      </div>`;
    }).join('');
    addedHtml = `<div class="inbox-added-list">
      <div class="inbox-added-header">${allAdded.length} slide${allAdded.length!==1?'s':''} added</div>
      ${rows}
    </div>`;
  }"""

changes.append(('addedHtml v2', OLD_ADDED_HTML, NEW_ADDED_HTML))

# ─────────────────────────────────────────────
# 7. Replace addInboxPairing to collect v2 rows
# ─────────────────────────────────────────────
OLD_ADD_INBOX = """\
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

NEW_ADD_INBOX = """\
function addInboxPairing(postId) {
  const drinkItems = collectDrinkRows('#inbox-drinks-'+postId);
  const foodItems  = collectFoodRows('#inbox-foods-'+postId);
  const hasContent = drinkItems.some(i=>i.product&&i.product!=='Unknown')
                  || foodItems.some(i=>i.product&&i.product!=='Unknown');
  if (!hasContent) { alert('Enter at least one drink or food item.'); return; }
  if (!inboxReviews[postId]) inboxReviews[postId] = {};
  if (!inboxReviews[postId].slides) inboxReviews[postId].slides = [];
  const slides = PAIRINGS_DATA.find(x => x.id === postId)?.slideshowImages || [];
  const cur = slides.length ? (inboxSlideIdx[postId] || 0) : inboxReviews[postId].slides.length;
  inboxReviews[postId].slides[cur] = { action:'pairing', drinkItems, foodItems };
  saveInboxReviews();
  if (slides.length) advanceToNextUnreviewed(postId);
  refreshInboxPost(postId);
}"""

changes.append(('addInboxPairing v2', OLD_ADD_INBOX, NEW_ADD_INBOX))

# ─────────────────────────────────────────────
# 8. Replace addInboxFoodRow + add addInboxDrinkRow
# ─────────────────────────────────────────────
OLD_FOOD_ROW = """\
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

NEW_FOOD_ROW = """\
function addInboxDrinkRow(postId) {
  const container = document.getElementById('inbox-drinks-' + postId);
  if (!container) return;
  const row = buildDrinkItemRow({brand:'',product:'',productType:'wine',wineType:'N/A',store:'Unknown'});
  container.appendChild(row);
  row.querySelector('.edit-brand').focus();
}

function addInboxFoodRow(postId) {
  const container = document.getElementById('inbox-foods-' + postId);
  if (!container) return;
  const row = buildFoodItemRow({brand:'',product:'',category:'other',store:'Unknown'});
  container.appendChild(row);
  row.querySelector('.edit-brand').focus();
}"""

changes.append(('inbox food/drink row helpers', OLD_FOOD_ROW, NEW_FOOD_ROW))

# ─────────────────────────────────────────────
# 9. Update removeInboxPairing (simplified — nulls whole slide)
# ─────────────────────────────────────────────
OLD_REMOVE_INBOX = """\
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
}"""

NEW_REMOVE_INBOX = """\
function removeInboxPairing(postId, slideIdx) {
  if (!inboxReviews[postId]?.slides) return;
  inboxReviews[postId].slides[slideIdx] = null;
  saveInboxReviews();
  refreshInboxPost(postId);
}"""

changes.append(('removeInboxPairing simplified', OLD_REMOVE_INBOX, NEW_REMOVE_INBOX))

# ─────────────────────────────────────────────
# 10. Update exportInboxJSON to build v2 cards
# ─────────────────────────────────────────────
OLD_EXPORT_SPLITS = """\
      ? (review.slides || []).filter(s => s?.action === 'pairing').flatMap(s => s.pairings || (s.wine ? [{ wine: s.wine, food: s.food, store: s.store, wineType: s.wineType }] : []))
      : (review.splits || []);

    if (splits.length > 0) {
      exportData[origIdx] = Object.assign({}, origPost, { category: 'hidden' });
      const children = splits
        .filter(s => s.wine || s.food)
        .map((s, i) => Object.assign({}, origPost, {
          id: postId + '_r' + i,
          originalPostId: postId,
          wine: s.wine || 'Unknown',
          food: s.food || 'Unknown',
          store: s.store || 'Unknown',
          wineType: s.wineType || 'Unknown',
          category: 'pairing',
          wineImageUrl: null,
          foodImageUrl: null,
          isMultiPairingSplit: true,
        }));
      exportData.splice(origIdx, 0, ...children);
    } else {
      exportData[origIdx] = Object.assign({}, origPost, { category: 'hidden' });
    }"""

NEW_EXPORT_SPLITS = """\
      ? (review.slides || []).filter(s => s?.action === 'pairing')
      : (review.splits || []).map(s => ({ drinkItems:[{brand:null,product:s.wine||'Unknown',productType:'wine',wineType:s.wineType||'N/A',store:s.store||'Unknown',price:null,vintage:null,region:null,amount:null,notes:null,needsReview:false}], foodItems:[{brand:null,product:s.food||'Unknown',category:'other',store:s.store||'Unknown',price:null,notes:null,needsReview:false}] }));

    if (splits.length > 0) {
      exportData[origIdx] = Object.assign({}, origPost, { category: 'hidden' });
      const children = splits.map((s, i) => {
        const di = s.drinkItems || [];
        const fi = s.foodItems  || [];
        const name = di[0]?.product || 'Unknown';
        return Object.assign({}, origPost, {
          id: postId + '_r' + i,
          originalPostId: postId,
          drinkName:  name,
          drinkType:  'Wine',
          drinkItems: di,
          foodItems:  fi,
          // legacy compat
          wine:     name,
          food:     fi.map(f=>f.product).filter(Boolean).join(' + ') || 'Unknown',
          store:    di[0]?.store || fi[0]?.store || 'Unknown',
          wineType: di[0]?.wineType || 'N/A',
          category: 'pairing',
          wineImageUrl: null,
          foodImageUrl: null,
          isMultiPairingSplit: true,
        });
      });
      exportData.splice(origIdx, 0, ...children);
    } else {
      exportData[origIdx] = Object.assign({}, origPost, { category: 'hidden' });
    }"""

changes.append(('exportInboxJSON v2', OLD_EXPORT_SPLITS, NEW_EXPORT_SPLITS))

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
