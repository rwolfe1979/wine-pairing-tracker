#!/usr/bin/env python3
"""
Phase 4b: Rebuild inbox as slide-by-slide wizard.
One image at a time — Add Pairing / Skip advances to next slide.
Run from project root: python scripts/_patch_phase4b.py
"""
import sys

HTML_FILE = 'index.html'

with open(HTML_FILE, 'r', encoding='utf-8') as f:
    src = f.read()

changes = []

# ─────────────────────────────────────────────
# 1. Replace old inbox-specific CSS blocks
# ─────────────────────────────────────────────
OLD_INBOX_CSS = """\
.inbox-slides-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 6px; padding: 0 14px 10px;
}
.inbox-slide-img {
  width: 100%; aspect-ratio: 9/16;
  object-fit: cover; border-radius: 6px;
  border: 1px solid #eee; background: var(--cream);
}"""

NEW_INBOX_CSS = """\
/* slide viewer */
.inbox-slide-viewer { padding: 0 14px 10px; }
.inbox-slide-nav-row {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 8px;
}
.inbox-slide-counter { font-size: 0.78rem; color: var(--text-muted); text-align: center; flex: 1; }
.inbox-nav-btn { width: 34px; height: 34px; font-size: 18px; }
.inbox-slide-img-wrap { position: relative; width: 100%; text-align: center; }
.inbox-slide-current {
  max-width: 100%; max-height: 420px; object-fit: contain;
  border-radius: 8px; border: 1px solid #eee; background: var(--cream-dark);
}
.inbox-slide-badge {
  position: absolute; top: 8px; right: 8px;
  padding: 4px 10px; border-radius: 12px; font-size: 0.72rem; font-weight: 700;
}
.badge-added { background: #27AE60; color: white; }
.badge-skipped { background: #999; color: white; }
.inbox-dots-row {
  display: flex; gap: 5px; flex-wrap: wrap; margin-top: 8px; justify-content: center;
}
.inbox-dot {
  width: 9px; height: 9px; border-radius: 50%; cursor: pointer; transition: all 0.15s;
}
.inbox-dot-empty { background: #ddd; border: 1.5px solid #ccc; }
.inbox-dot-green { background: #27AE60; }
.inbox-dot-gray { background: #bbb; }
.inbox-dot-current { outline: 2px solid var(--burgundy); outline-offset: 2px; }
/* form */
.inbox-slide-form {
  padding: 10px 14px 0; display: flex; flex-direction: column; gap: 8px;
  border-top: 1px solid #f0e8de; margin-top: 4px;
}
.inbox-form-row { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
.inbox-form-actions { display: flex; gap: 6px; }
/* added list */
.inbox-added-list { padding: 8px 14px; border-top: 1px solid #f0e8de; }
.inbox-added-header {
  font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.07em;
  color: var(--text-muted); font-weight: 700; margin-bottom: 5px;
}
.inbox-added-row {
  display: flex; align-items: center; gap: 8px;
  padding: 4px 0; border-bottom: 1px solid #f5eeea;
}
.inbox-added-info { flex: 1; font-size: 0.8rem; color: var(--text-secondary); }
.inbox-added-edit { font-size: 0.72rem; color: var(--burgundy); cursor: pointer; background: none; border: none; text-decoration: underline; }"""

changes.append(('inbox CSS slides', OLD_INBOX_CSS, NEW_INBOX_CSS))

# ─────────────────────────────────────────────
# 2. Replace buildInboxPost + old split helpers
#    with new slide-wizard functions
# ─────────────────────────────────────────────
OLD_INBOX_FUNCTIONS = """\
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
}"""

NEW_INBOX_FUNCTIONS = """\
// per-post slide cursor (not persisted)
const inboxSlideIdx = {};

function buildInboxPost(p) {
  const slides = p.slideshowImages || [];
  const postId = p.id;
  const cur = Math.min(inboxSlideIdx[postId] || 0, Math.max(0, slides.length - 1));
  const review = inboxReviews[postId] || {};
  const decisions = review.slides || [];
  const addedPairings = decisions.filter(s => s?.action === 'pairing');
  const skippedCount = decisions.filter(s => s?.action === 'skip').length;

  // ── slide viewer ──
  let slideHtml;
  if (slides.length > 0) {
    const curImg = slides[cur];
    const dec = decisions[cur];
    const badge = dec?.action === 'pairing'
      ? '<span class="inbox-slide-badge badge-added">✓ Added</span>'
      : dec?.action === 'skip'
      ? '<span class="inbox-slide-badge badge-skipped">Skip</span>'
      : '';
    const dots = slides.map((_, i) => {
      const d = decisions[i];
      const cls = d?.action === 'pairing' ? 'green' : d?.action === 'skip' ? 'gray' : 'empty';
      const current = i === cur ? ' inbox-dot-current' : '';
      return `<span class="inbox-dot inbox-dot-${cls}${current}" onclick="jumpInboxSlide('${postId}',${i})" title="Slide ${i+1}"></span>`;
    }).join('');
    slideHtml = `<div class="inbox-slide-viewer">
      <div class="inbox-slide-nav-row">
        <button class="variant-btn inbox-nav-btn" onclick="navInboxSlide('${postId}',-1)">&#8249;</button>
        <span class="inbox-slide-counter">Slide ${cur+1} of ${slides.length} &nbsp;·&nbsp; ${addedPairings.length} added, ${skippedCount} skipped</span>
        <button class="variant-btn inbox-nav-btn" onclick="navInboxSlide('${postId}',1)">&#8250;</button>
      </div>
      <div class="inbox-slide-img-wrap">
        <img class="inbox-slide-current" src="${curImg}" loading="lazy" onerror="this.style.opacity='0.25'">
        ${badge}
      </div>
      <div class="inbox-dots-row">${dots}</div>
    </div>`;
  } else {
    slideHtml = `<div class="inbox-no-slides">Video post — <a href="${escapeHtml(p.url)}" target="_blank" rel="noopener">watch on TikTok</a> then add pairings below.</div>`;
  }

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
  </div>`;

  // ── added pairings list ──
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
  }

  return `<div class="inbox-post" id="inbox-${postId}">
    <div class="inbox-post-header">
      <div class="inbox-post-title"><strong>${escapeHtml(p.wine)}</strong></div>
      <a href="${escapeHtml(p.url)}" target="_blank" rel="noopener" class="inbox-tiktok-link">🎵 TikTok</a>
    </div>
    <div class="inbox-post-meta">${p.date ? fmtDate(p.date) : ''}${slides.length?' &nbsp;·&nbsp; '+slides.length+' slides':' &nbsp;·&nbsp; video'}</div>
    ${slideHtml}
    ${formHtml}
    ${addedHtml}
    <div class="inbox-actions">
      <button class="btn-secondary" onclick="hideInboxPost('${postId}')">Hide post</button>
      <button class="btn-primary" onclick="markPostDone('${postId}')">Done ✓</button>
    </div>
  </div>`;
}

function navInboxSlide(postId, dir) {
  const p = PAIRINGS_DATA.find(x => x.id === postId);
  const slides = p?.slideshowImages || [];
  if (!slides.length) return;
  const cur = inboxSlideIdx[postId] || 0;
  inboxSlideIdx[postId] = (cur + dir + slides.length) % slides.length;
  refreshInboxPost(postId);
}

function jumpInboxSlide(postId, idx) {
  inboxSlideIdx[postId] = idx;
  refreshInboxPost(postId);
}

function refreshInboxPost(postId) {
  const el = document.getElementById('inbox-' + postId);
  if (!el) return;
  const p = getEffectivePost(postId);
  const tmp = document.createElement('div');
  tmp.innerHTML = buildInboxPost(p);
  el.replaceWith(tmp.firstElementChild);
}

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
}

function skipInboxSlide(postId) {
  if (!inboxReviews[postId]) inboxReviews[postId] = {};
  if (!inboxReviews[postId].slides) inboxReviews[postId].slides = [];
  const cur = inboxSlideIdx[postId] || 0;
  inboxReviews[postId].slides[cur] = { action:'skip' };
  saveInboxReviews();
  advanceToNextUnreviewed(postId);
  refreshInboxPost(postId);
}

function removeInboxPairing(postId, slideIdx) {
  if (!inboxReviews[postId]?.slides) return;
  inboxReviews[postId].slides[slideIdx] = null;
  saveInboxReviews();
  refreshInboxPost(postId);
}

function advanceToNextUnreviewed(postId) {
  const slides = PAIRINGS_DATA.find(x => x.id === postId)?.slideshowImages || [];
  if (!slides.length) return;
  const decisions = inboxReviews[postId]?.slides || [];
  const cur = inboxSlideIdx[postId] || 0;
  for (let i = 1; i <= slides.length; i++) {
    const next = (cur + i) % slides.length;
    if (!decisions[next]) { inboxSlideIdx[postId] = next; return; }
  }
  // all reviewed — stay put
}"""

changes.append(('buildInboxPost wizard', OLD_INBOX_FUNCTIONS, NEW_INBOX_FUNCTIONS))

# ─────────────────────────────────────────────
# 3. Update exportInboxJSON to read .slides
# ─────────────────────────────────────────────
OLD_EXPORT = """\
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
  }"""

NEW_EXPORT = """\
  for (const [postId, review] of Object.entries(inboxReviews)) {
    if (!review.done) continue;
    const origIdx = exportData.findIndex(p => p.id === postId);
    if (origIdx === -1) continue;
    const origPost = exportData[origIdx];
    // support both old .splits and new .slides model
    const splits = review.slides
      ? (review.slides || []).filter(s => s?.action === 'pairing')
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
    }
  }"""

changes.append(('exportInboxJSON slides model', OLD_EXPORT, NEW_EXPORT))

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
