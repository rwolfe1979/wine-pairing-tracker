#!/usr/bin/env python3
"""
Phase 2 patch: compact card face + click-to-open detail modal.
Run from project root: python scripts/_patch_phase2.py
"""
import sys, re

HTML_FILE = 'index.html'

with open(HTML_FILE, 'r', encoding='utf-8') as f:
    src = f.read()

changes = []  # (description, old, new)

# ─────────────────────────────────────────────
# 1. Card CSS: add cursor + position:relative
# ─────────────────────────────────────────────
changes.append(('card cursor+position', '''\
.card {
  background: var(--card-bg);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: transform 0.2s, box-shadow 0.2s;
}''', '''\
.card {
  background: var(--card-bg);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;
  position: relative;
}'''))

# ─────────────────────────────────────────────
# 2. Add detail modal CSS after .btn-secondary
# ─────────────────────────────────────────────
changes.append(('detail modal CSS', '''\
.btn-secondary {
  background: #f5f0eb; color: #666; border: 1px solid #ddd;
  padding: 10px 20px; border-radius: 8px; cursor: pointer;
}''', '''\
.btn-secondary {
  background: #f5f0eb; color: #666; border: 1px solid #ddd;
  padding: 10px 20px; border-radius: 8px; cursor: pointer;
}

/* DETAIL MODAL */
.detail-modal-box { width: min(680px, 95vw); }
.detail-modal-header {
  padding: 18px 24px 14px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}
.detail-wine-name {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--burgundy);
  margin-bottom: 4px;
  line-height: 1.3;
}
.detail-food-name {
  font-size: 0.88rem;
  color: var(--text-secondary);
  line-height: 1.3;
}
.detail-body {
  padding: 16px 24px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  overflow-y: auto;
  max-height: 60vh;
}
.detail-caption-wrap {
  background: var(--cream);
  border-radius: 8px;
  padding: 12px 14px;
}
.detail-caption-label {
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
  font-weight: 700;
  margin-bottom: 6px;
}
.detail-caption {
  font-size: 0.83rem;
  color: var(--text-secondary);
  line-height: 1.65;
  white-space: pre-wrap;
}
.detail-ratings-wrap {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-top: 2px;
}
.detail-notes-wrap { display: flex; flex-direction: column; gap: 6px; }
.detail-footer {
  display: flex;
  gap: 8px;
  padding: 14px 24px;
  border-top: 1px solid #eee;
  flex-wrap: wrap;
}
.detail-footer > * { flex: 1; min-width: 110px; text-align: center; }
/* Status dot overlaid on card image */
.card-status-dot {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 2.5px solid white;
  box-shadow: 0 1px 4px rgba(0,0,0,0.35);
  z-index: 5;
  pointer-events: none;
}'''))

# ─────────────────────────────────────────────
# 3. Add detail modal HTML before <script>
# ─────────────────────────────────────────────
detail_modal_html = '''
<div id="detailOverlay" class="modal-overlay" style="display:none" onclick="if(event.target===this)closeDetailModal()">
  <div class="modal-box detail-modal-box">
    <div class="detail-modal-header">
      <div>
        <div id="detailWineName" class="detail-wine-name"></div>
        <div id="detailFoodName" class="detail-food-name"></div>
      </div>
      <button class="modal-close" onclick="closeDetailModal()">✕</button>
    </div>
    <div id="detailBody" class="detail-body">
      <div id="detailRatingsWrap" class="detail-ratings-wrap"></div>
      <div id="detailNotesWrap" class="detail-notes-wrap"></div>
      <div id="detailCaptionWrap"></div>
    </div>
    <div class="detail-footer">
      <a id="detailTikTokBtn" class="tiktok-btn" href="#" target="_blank" rel="noopener">🎵 TikTok →</a>
      <button class="btn-secondary" onclick="openEditFromDetail()">✏️ Edit</button>
      <button class="btn-secondary" onclick="closeDetailModal()">Close</button>
    </div>
  </div>
</div>

'''

changes.append(('detail modal HTML', '\n<script>\n', '\n' + detail_modal_html.strip() + '\n\n<script>\n'))

# ─────────────────────────────────────────────
# 4. Replace buildCard() — compact card only
# ─────────────────────────────────────────────
OLD_BUILD_CARD = '''\
function buildCard(p) {
  const r = getRating(p.id);
  // cards in tabs are never muted - hidden posts are filtered out upstream
  const notesVisible = r.notes ? 'block' : 'none';

  return `<div class="card" id="card-${p.id}">
    ${buildImageSection(p)}
    <div class="card-body">
      <div class="card-wine">${p.wine !== 'Unknown' ? p.wine : '<em style="color:#999;font-weight:400">Wine not specified</em>'}</div>
      <div class="card-food">${p.food !== 'Unknown' ? p.food : '<em style="color:#999">Food not specified</em>'}</div>
      <div class="card-meta">
        <span>${fmtDate(p.date)}</span>
        <span class="card-engagement"><span>👁️ ${fmtNum(p.views)}</span><span>❤️ ${fmtNum(p.likes)}</span></span>
      </div>
    </div>
    <div class="ratings-section">
      ${p.category === 'pairing'
        ? buildRatingRow(p.id,'wineRating','🍷 Wine',r.wineRating)
          + buildRatingRow(p.id,'foodRating','🍽️ Food',r.foodRating)
          + buildRatingRow(p.id,'pairingRating','🤝 Pairing',r.pairingRating)
        : p.category === 'porch-pounder'
        ? buildRatingRow(p.id,'wineRating','🍷 Wine',r.wineRating)
        : buildRatingRow(p.id,'wineRating','⭐ Overall',r.wineRating)
      }
    </div>
    <div class="notes-section">
      <button class="notes-toggle" onclick="toggleNotes('${p.id}',this)">
        ${r.notes ? '📝 Edit notes' : '+ Add notes…'}
      </button>
      <textarea class="notes-area" id="notes-${p.id}" placeholder="Your tasting notes…" style="display:${notesVisible}" onblur="saveNote('${p.id}',this)">${r.notes||''}</textarea>
    </div>
    <div class="card-footer">
      <a class="tiktok-btn" href="${p.url}" target="_blank" rel="noopener">🎵 View on TikTok →</a>
      <button class="edit-btn" onclick="openEditModal('${p.id}')">✏️ Edit</button>
    </div>
  </div>`;
}'''

NEW_BUILD_CARD = '''\
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
}'''

changes.append(('buildCard compact', OLD_BUILD_CARD, NEW_BUILD_CARD))

# ─────────────────────────────────────────────
# 5. Replace setRating() to update detail modal
# ─────────────────────────────────────────────
OLD_SET_RATING = '''\
function setRating(postId, field, value, btn) {
  if (!ratings[postId]) ratings[postId] = {wineRating:'not-tried',foodRating:'not-tried',pairingRating:'not-tried',notes:''};
  // Toggle off if already selected
  if (ratings[postId][field] === value) {
    ratings[postId][field] = 'not-tried';
  } else {
    ratings[postId][field] = value;
  }
  saveRatings();
  // Re-render just this card's rating row
  const card = document.getElementById('card-'+postId);
  if (!card) return;
  const ratingsSec = card.querySelector('.ratings-section');
  if (!ratingsSec) return;
  const r = getRating(postId);
  ratingsSec.innerHTML =
    buildRatingRow(postId,'wineRating','🍷 Wine',r.wineRating) +
    buildRatingRow(postId,'foodRating','🍽️ Food',r.foodRating) +
    buildRatingRow(postId,'pairingRating','🤝 Pairing',r.pairingRating);
  updateStats();
  updateShoppingList();
}'''

NEW_SET_RATING = '''\
function setRating(postId, field, value, btn) {
  if (!ratings[postId]) ratings[postId] = {wineRating:'not-tried',foodRating:'not-tried',pairingRating:'not-tried',notes:''};
  if (ratings[postId][field] === value) {
    ratings[postId][field] = 'not-tried';
  } else {
    ratings[postId][field] = value;
  }
  saveRatings();
  // Refresh detail modal ratings if it's open for this post
  if (currentDetailId === postId) refreshDetailRatings(postId);
  // Update the status dot on the card
  updateCardStatusDot(postId);
  updateStats();
  updateShoppingList();
}'''

changes.append(('setRating modal-aware', OLD_SET_RATING, NEW_SET_RATING))

# ─────────────────────────────────────────────
# 6. Add new JS functions after scrollToCard
# ─────────────────────────────────────────────
OLD_SCROLL = '''\
function scrollToCard(id) {
  const el = document.getElementById('card-'+id);
  if (el) el.scrollIntoView({behavior:'smooth', block:'center'});
}'''

NEW_SCROLL = '''\
function scrollToCard(id) {
  const el = document.getElementById('card-'+id);
  if (el) el.scrollIntoView({behavior:'smooth', block:'center'});
}

// ─── DETAIL MODAL ───
let currentDetailId = null;

function escapeHtml(s) {
  return (s || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function refreshDetailRatings(postId) {
  const p = getEffectivePost(postId);
  const r = getRating(postId);
  const wrap = document.getElementById('detailRatingsWrap');
  if (!wrap) return;
  wrap.innerHTML = p.category === 'pairing'
    ? buildRatingRow(postId,'wineRating','🍷 Wine',r.wineRating)
      + buildRatingRow(postId,'foodRating','🍽️ Food',r.foodRating)
      + buildRatingRow(postId,'pairingRating','🤝 Pairing',r.pairingRating)
    : p.category === 'porch-pounder'
    ? buildRatingRow(postId,'wineRating','🍷 Wine',r.wineRating)
    : buildRatingRow(postId,'wineRating','⭐ Overall',r.wineRating);
}

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
}

function openDetailModal(postId) {
  const p = getEffectivePost(postId);
  currentDetailId = postId;
  document.getElementById('detailWineName').textContent =
    p.wine !== 'Unknown' ? p.wine : 'Wine not specified';
  document.getElementById('detailFoodName').textContent =
    p.food !== 'Unknown' ? p.food : '';

  // Ratings
  refreshDetailRatings(postId);

  // Notes
  const r = getRating(postId);
  const notesVisible = r.notes ? 'block' : 'none';
  document.getElementById('detailNotesWrap').innerHTML = `
    <button class="notes-toggle" onclick="toggleNotes('${postId}',this)">
      ${r.notes ? '📝 Edit notes' : '+ Add notes…'}
    </button>
    <textarea class="notes-area" id="notes-${postId}" placeholder="Your tasting notes…"
      style="display:${notesVisible}" onblur="saveNote('${postId}',this)">${escapeHtml(r.notes)}</textarea>`;

  // Caption
  const captionEl = document.getElementById('detailCaptionWrap');
  if (p.text && p.text.trim()) {
    captionEl.innerHTML = `<div class="detail-caption-wrap">
      <div class="detail-caption-label">Sam’s caption</div>
      <div class="detail-caption">${escapeHtml(p.text.trim())}</div>
    </div>`;
  } else {
    captionEl.innerHTML = '';
  }

  // TikTok link
  const tikBtn = document.getElementById('detailTikTokBtn');
  tikBtn.href = p.url || '#';
  tikBtn.style.display = p.url ? '' : 'none';

  document.getElementById('detailOverlay').style.display = 'flex';
  document.getElementById('detailBody').scrollTop = 0;
}

function closeDetailModal() {
  document.getElementById('detailOverlay').style.display = 'none';
  currentDetailId = null;
}

function openEditFromDetail() {
  const id = currentDetailId;
  closeDetailModal();
  openEditModal(id);
}'''

changes.append(('scrollToCard + detail modal JS', OLD_SCROLL, NEW_SCROLL))

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
        print(f'WARNING: [{desc}] matched {count} times — replacing all')
    result = result.replace(old, new)
    print(f'  OK  [{desc}] ({count} replacement(s))')

with open(HTML_FILE, 'w', encoding='utf-8') as f:
    f.write(result)

print(f'\nDone. Wrote {HTML_FILE}')
