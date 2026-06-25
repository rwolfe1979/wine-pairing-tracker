#!/usr/bin/env python3
"""
Phase 4 patch: Review Inbox tab.
Run from project root: python scripts/_patch_phase4.py
"""
import sys

HTML_FILE = 'index.html'

with open(HTML_FILE, 'r', encoding='utf-8') as f:
    src = f.read()

changes = []

# ─────────────────────────────────────────────
# 1. Inbox CSS (before shopping list section)
# ─────────────────────────────────────────────
changes.append(('inbox CSS', '/* SHOPPING LIST SIDEBAR */', """\
/* REVIEW INBOX */
.inbox-export-bar {
  display: flex; align-items: center; gap: 12px;
  background: #fff8f0; border: 1.5px solid #e8d8c8;
  border-radius: 10px; padding: 12px 16px; margin-bottom: 16px;
}
.inbox-export-hint { font-size: 0.78rem; color: var(--text-muted); }
.inbox-posts { display: flex; flex-direction: column; gap: 20px; }
.inbox-post {
  background: white; border-radius: var(--radius);
  box-shadow: var(--shadow); overflow: hidden;
}
.inbox-post-header {
  display: flex; justify-content: space-between; align-items: flex-start;
  padding: 12px 14px 6px; gap: 10px;
}
.inbox-post-title { font-size: 0.9rem; font-weight: 600; color: var(--text-primary); flex: 1; }
.inbox-tiktok-link {
  font-size: 0.78rem; color: white; background: #010101;
  padding: 4px 10px; border-radius: 6px; text-decoration: none; white-space: nowrap;
}
.inbox-tiktok-link:hover { opacity: 0.8; }
.inbox-post-meta { padding: 0 14px 8px; font-size: 0.72rem; color: var(--text-muted); }
.inbox-no-slides {
  margin: 0 14px 10px;
  padding: 10px 12px;
  background: var(--cream);
  border-radius: 8px;
  font-size: 0.82rem;
  color: var(--text-secondary);
}
.inbox-no-slides a { color: var(--burgundy); }
.inbox-slides-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 6px; padding: 0 14px 10px;
}
.inbox-slide-img {
  width: 100%; aspect-ratio: 9/16;
  object-fit: cover; border-radius: 6px;
  border: 1px solid #eee; background: var(--cream);
}
.inbox-splits {
  border-top: 1px solid #f0e8de;
  padding: 8px 14px;
  display: flex; flex-direction: column; gap: 8px;
}
.split-row {
  display: flex; gap: 6px; flex-wrap: wrap; align-items: center;
}
.split-wine, .split-food {
  flex: 1; min-width: 120px;
  padding: 6px 9px; border: 1.5px solid #ddd; border-radius: 7px;
  font-size: 0.82rem; color: var(--text-primary);
  outline: none;
}
.split-wine:focus, .split-food:focus { border-color: var(--burgundy); }
.split-store, .split-type {
  padding: 6px 8px; border: 1.5px solid #ddd; border-radius: 7px;
  font-size: 0.78rem; background: white; color: var(--text-secondary);
  outline: none; cursor: pointer;
}
.split-remove-btn {
  background: none; border: 1.5px solid #ddd; border-radius: 50%;
  width: 24px; height: 24px; cursor: pointer; color: #aaa;
  font-size: 12px; display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; transition: all 0.15s;
}
.split-remove-btn:hover { border-color: var(--disliked); color: var(--disliked); }
.inbox-actions {
  padding: 10px 14px 14px; display: flex; gap: 8px; flex-wrap: wrap;
  border-top: 1px solid #f0e8de;
}
.inbox-add-btn { font-size: 0.82rem; }
.inbox-all-done {
  text-align: center; padding: 40px 20px;
  color: var(--text-secondary); font-size: 1rem;
  background: white; border-radius: var(--radius); box-shadow: var(--shadow);
}

/* SHOPPING LIST SIDEBAR */"""))

# ─────────────────────────────────────────────
# 2. Add inbox tab button to tab bar
# ─────────────────────────────────────────────
changes.append(('inbox tab button', """\
    <button class="tab-btn" data-tab="recipe">
      🍹 Recipes <span class="tab-count" id="countRecipe">0</span>
    </button>
  </div>""", """\
    <button class="tab-btn" data-tab="recipe">
      🍹 Recipes <span class="tab-count" id="countRecipe">0</span>
    </button>
    <button class="tab-btn" data-tab="inbox">
      🔍 Review <span class="tab-count" id="countInbox">0</span>
    </button>
  </div>"""))

# ─────────────────────────────────────────────
# 3. Update updateTabCounts to include inbox count
# ─────────────────────────────────────────────
changes.append(('updateTabCounts inbox', """\
function updateTabCounts(baseData) {
  // baseData = posts after search/store/type filters but before status + tab filter
  const countTab = cat => baseData.filter(p => p.category === cat).length;
  document.getElementById('countPairing').textContent = countTab('pairing');
  document.getElementById('countPorchPounder').textContent = countTab('porch-pounder');
  document.getElementById('countRecipe').textContent = countTab('recipe');
}""", """\
function updateTabCounts(baseData) {
  // baseData = posts after search/store/type filters but before status + tab filter
  const countTab = cat => baseData.filter(p => p.category === cat).length;
  document.getElementById('countPairing').textContent = countTab('pairing');
  document.getElementById('countPorchPounder').textContent = countTab('porch-pounder');
  document.getElementById('countRecipe').textContent = countTab('recipe');
  document.getElementById('countInbox').textContent = getInboxCount();
}"""))

# ─────────────────────────────────────────────
# 4. Update render() to route inbox tab
# ─────────────────────────────────────────────
changes.append(('render inbox routing', """\
function render() {
  const data = getFilteredData();
  const grid = document.getElementById('cardsGrid');
  const empty = document.getElementById('emptyState');
  const info = document.getElementById('resultsInfo');""", """\
function render() {
  if (activeTab === 'inbox') { renderInbox(); return; }
  const data = getFilteredData();
  const grid = document.getElementById('cardsGrid');
  const empty = document.getElementById('emptyState');
  const info = document.getElementById('resultsInfo');"""))

# ─────────────────────────────────────────────
# 5. Add inbox JS functions before TAB HANDLER
# ─────────────────────────────────────────────
changes.append(('inbox JS functions', '// ─── TAB HANDLER ───', """\
// ─── REVIEW INBOX ───
const INBOX_LS_KEY = 'wineInboxReviews';
let inboxReviews = JSON.parse(localStorage.getItem(INBOX_LS_KEY) || '{}');

function saveInboxReviews() {
  localStorage.setItem(INBOX_LS_KEY, JSON.stringify(inboxReviews));
}

function isInboxCandidate(p) {
  if (p.category === 'hidden') return false;
  const wine = (p.wine || '').toLowerCase();
  return wine.startsWith('various') ||
         wine === 'cocktail' ||
         (p.wine || '').split(' / ').length >= 3;
}

function getInboxPosts() {
  return PAIRINGS_DATA
    .map(p => getEffectivePost(p.id))
    .filter(p => isInboxCandidate(p) && !inboxReviews[p.id]?.done);
}

function getInboxCount() {
  return PAIRINGS_DATA
    .map(p => getEffectivePost(p.id))
    .filter(p => isInboxCandidate(p) && !inboxReviews[p.id]?.done).length;
}

function renderInbox() {
  const grid = document.getElementById('cardsGrid');
  const empty = document.getElementById('emptyState');
  const info = document.getElementById('resultsInfo');
  empty.style.display = 'none';

  const posts = getInboxPosts();

  if (posts.length === 0) {
    info.textContent = '';
    grid.innerHTML = '<div class="inbox-all-done">All posts reviewed! Use Export to download updated data.</div>';
    return;
  }

  info.textContent = `${posts.length} post${posts.length !== 1 ? 's' : ''} need review`;

  const allWines = [...new Set(
    PAIRINGS_DATA.map(p => p.wine)
      .filter(w => w && w !== 'Unknown' && !w.toLowerCase().startsWith('various') && !(w.includes(' / ')))
  )].sort();
  const allFoods = [...new Set(
    PAIRINGS_DATA.map(p => p.food)
      .filter(f => f && f !== 'Unknown' && !f.toLowerCase().startsWith('various'))
  )].sort();

  const exportBar = `<div class="inbox-export-bar">
    <button class="btn-primary" onclick="exportInboxJSON()">📥 Export Updated JSON</button>
    <span class="inbox-export-hint">Download, then send me the file to make splits permanent in the repo.</span>
  </div>`;

  const datalists = `<datalist id="wineAC">${allWines.map(w => `<option value="${escapeHtml(w)}">`).join('')}</datalist>
    <datalist id="foodAC">${allFoods.map(f => `<option value="${escapeHtml(f)}">`).join('')}</datalist>`;

  grid.innerHTML = datalists + exportBar +
    '<div class="inbox-posts">' + posts.map(p => buildInboxPost(p)).join('') + '</div>';
}

function buildInboxPost(p) {
  const slides = p.slideshowImages || [];
  const review = inboxReviews[p.id] || { splits: [] };
  const slidesHtml = slides.length > 0
    ? `<div class="inbox-slides-grid">${slides.map(url =>
        `<img class="inbox-slide-img" src="${url}" loading="lazy" onerror="this.style.display='none'">`
      ).join('')}</div>`
    : `<div class="inbox-no-slides">Video — no slides. <a href="${escapeHtml(p.url)}" target="_blank" rel="noopener">Watch on TikTok</a> then add pairings below.</div>`;

  const existingSplits = (review.splits || []).map((s, i) => buildSplitRow(p.id, i, s)).join('');

  return `<div class="inbox-post" id="inbox-${p.id}">
    <div class="inbox-post-header">
      <div class="inbox-post-title"><strong>${escapeHtml(p.wine)}</strong>${p.food && p.food !== 'Unknown' ? ' — ' + escapeHtml(p.food) : ''}</div>
      <a href="${escapeHtml(p.url)}" target="_blank" rel="noopener" class="inbox-tiktok-link">🎵 TikTok</a>
    </div>
    <div class="inbox-post-meta">${p.date ? fmtDate(p.date) : ''} &nbsp; ${slides.length > 0 ? slides.length + ' slides' : 'video'}</div>
    ${slidesHtml}
    <div class="inbox-splits" id="splits-${p.id}">${existingSplits}</div>
    <div class="inbox-actions">
      <button class="btn-secondary inbox-add-btn" onclick="addSplitRow('${p.id}')">+ Add pairing</button>
      <button class="btn-secondary" onclick="hideInboxPost('${p.id}')">Hide post</button>
      <button class="btn-primary" onclick="markPostDone('${p.id}')">Done ✓</button>
    </div>
  </div>`;
}

function buildSplitRow(postId, idx, data) {
  const wine = escapeHtml(data?.wine || '');
  const food = escapeHtml(data?.food || '');
  const store = data?.store || 'Unknown';
  const wineType = data?.wineType || 'Unknown';
  const storeOpts = ["Unknown","Trader Joe's","Costco","Aldi"]
    .map(s => `<option${s === store ? ' selected' : ''}>${s}</option>`).join('');
  const typeOpts = ["Unknown","Red","White","Rosé","Sparkling","Orange"]
    .map(t => `<option${t === wineType ? ' selected' : ''}>${t}</option>`).join('');

  return `<div class="split-row" id="split-${postId}-${idx}">
    <input class="split-wine" list="wineAC" placeholder="Wine name..." value="${wine}"
      onchange="saveSplitField('${postId}',${idx},'wine',this.value)">
    <input class="split-food" list="foodAC" placeholder="Food / snack..." value="${food}"
      onchange="saveSplitField('${postId}',${idx},'food',this.value)">
    <select class="split-store" onchange="saveSplitField('${postId}',${idx},'store',this.value)">${storeOpts}</select>
    <select class="split-type" onchange="saveSplitField('${postId}',${idx},'wineType',this.value)">${typeOpts}</select>
    <button class="split-remove-btn" onclick="removeSplitRow('${postId}',${idx})" title="Remove">✕</button>
  </div>`;
}

function addSplitRow(postId) {
  if (!inboxReviews[postId]) inboxReviews[postId] = { splits: [] };
  if (!inboxReviews[postId].splits) inboxReviews[postId].splits = [];
  const idx = inboxReviews[postId].splits.length;
  inboxReviews[postId].splits.push({ wine: '', food: '', store: 'Unknown', wineType: 'Unknown' });
  saveInboxReviews();
  const container = document.getElementById('splits-' + postId);
  if (container) {
    const div = document.createElement('div');
    div.innerHTML = buildSplitRow(postId, idx, {});
    container.appendChild(div.firstElementChild);
  }
}

function removeSplitRow(postId, idx) {
  if (!inboxReviews[postId]?.splits) return;
  inboxReviews[postId].splits.splice(idx, 1);
  saveInboxReviews();
  const container = document.getElementById('splits-' + postId);
  if (container) {
    container.innerHTML = (inboxReviews[postId].splits || []).map((s, i) => buildSplitRow(postId, i, s)).join('');
  }
}

function saveSplitField(postId, idx, field, value) {
  if (!inboxReviews[postId]?.splits) return;
  if (!inboxReviews[postId].splits[idx]) return;
  inboxReviews[postId].splits[idx][field] = value;
  saveInboxReviews();
}

function hideInboxPost(postId) {
  if (!confirm('Hide this post? It will be removed from the inbox.')) return;
  if (!inboxReviews[postId]) inboxReviews[postId] = {};
  inboxReviews[postId].done = true;
  inboxReviews[postId].action = 'hide';
  saveInboxReviews();
  const el = document.getElementById('inbox-' + postId);
  if (el) el.remove();
  document.getElementById('countInbox').textContent = getInboxCount();
}

function markPostDone(postId) {
  const splits = inboxReviews[postId]?.splits || [];
  if (splits.length === 0) {
    if (!confirm('No pairings added. Hide this post from the inbox?')) return;
  }
  if (!inboxReviews[postId]) inboxReviews[postId] = {};
  inboxReviews[postId].done = true;
  inboxReviews[postId].action = splits.length > 0 ? 'split' : 'hide';
  saveInboxReviews();
  const el = document.getElementById('inbox-' + postId);
  if (el) el.remove();
  document.getElementById('countInbox').textContent = getInboxCount();
}

function exportInboxJSON() {
  let exportData = PAIRINGS_DATA.map(p => Object.assign({}, p));

  for (const [postId, review] of Object.entries(inboxReviews)) {
    if (!review.done) continue;
    const origIdx = exportData.findIndex(p => p.id === postId);
    if (origIdx === -1) continue;
    const origPost = exportData[origIdx];

    if (review.action === 'split' && (review.splits || []).length > 0) {
      exportData[origIdx] = Object.assign({}, origPost, { category: 'hidden' });
      const children = review.splits
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
    }
  }

  const json = JSON.stringify(exportData, null, 2);
  const blob = new Blob([json], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'pairings-data-export.json';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// ─── TAB HANDLER ───"""))

# ─────────────────────────────────────────────
# Apply all changes
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
