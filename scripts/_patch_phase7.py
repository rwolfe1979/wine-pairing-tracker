#!/usr/bin/env python3
"""
Phase 7: One-click "Publish to App" button.
- Switches PAIRINGS_DATA from embedded const to fetch() call
- Adds GitHub token setup modal
- Adds publishToRepo() that pushes pairings-data.json via GitHub API
- Updates exportInboxJSON() to share buildExportData() with publish
Run from project root: python scripts/_patch_phase7.py
"""
import re, sys
HTML_FILE = 'index.html'
with open(HTML_FILE, 'r', encoding='utf-8') as f:
    src = f.read()
changes = []

# ─────────────────────────────────────────────
# 1. Replace embedded PAIRINGS_DATA line with empty let
#    (single line: "const PAIRINGS_DATA = [huge json];")
# ─────────────────────────────────────────────
before = src
src = re.sub(
    r'^const PAIRINGS_DATA = .+;$',
    'let PAIRINGS_DATA = []; // loaded by initApp()',
    src,
    flags=re.MULTILINE
)
if src == before:
    print('ERROR: PAIRINGS_DATA line not found — aborting')
    sys.exit(1)
print('  OK  [PAIRINGS_DATA => let + fetch]')

# ─────────────────────────────────────────────
# 2. Add GitHub token modal HTML (before closing </body>)
# ─────────────────────────────────────────────
TOKEN_MODAL = """\
<div id="tokenModal" class="modal-overlay" style="display:none" onclick="if(event.target===this)closeTokenModal()">
  <div class="modal-box" style="max-width:420px">
    <div class="modal-header">
      <h3>GitHub Token Setup</h3>
      <button onclick="closeTokenModal()" class="modal-close">✕</button>
    </div>
    <div class="modal-body" style="gap:10px">
      <p style="font-size:0.82rem;color:var(--text-secondary);margin:0">
        Create a <strong>Fine-grained Personal Access Token</strong> at
        <strong>github.com → Settings → Developer settings → Personal access tokens → Fine-grained tokens</strong>.<br><br>
        Set <em>Repository access</em> to <strong>wine-pairing-tracker only</strong>,
        and grant <strong>Contents: Read and write</strong> permission.
      </p>
      <label style="margin-top:6px">GitHub Token
        <input type="password" id="tokenInput" placeholder="github_pat_..." autocomplete="off"
          style="font-family:monospace;font-size:0.78rem">
      </label>
    </div>
    <div class="modal-footer">
      <button onclick="clearGitHubToken()" class="btn-secondary">Clear saved token</button>
      <button onclick="saveGitHubToken()" class="btn-primary">Save token</button>
    </div>
  </div>
</div>

</body>"""

changes.append(('token modal HTML', '</body>', TOKEN_MODAL))

# ─────────────────────────────────────────────
# 3. Update export bar to add Publish + ⚙ buttons
# ─────────────────────────────────────────────
OLD_EXPORT_BAR = """\
const exportBar = `<div class="inbox-export-bar">
    <button class="btn-primary" onclick="exportInboxJSON()">📥 Export Updated JSON</button>
    <span class="inbox-export-hint">Download, then send me the file to make splits permanent in the repo.</span>
  </div>`;"""

NEW_EXPORT_BAR = """\
const exportBar = `<div class="inbox-export-bar">
    <button class="btn-secondary" onclick="exportInboxJSON()">⬇ Export JSON</button>
    <button class="btn-primary" id="publishBtn" onclick="publishToRepo()">🚀 Publish to App</button>
    <button class="btn-link" onclick="openTokenSetup()" title="GitHub token" style="font-size:1rem;padding:4px 8px;margin-left:2px">⚙</button>
  </div>`;"""

changes.append(('export bar v2', OLD_EXPORT_BAR, NEW_EXPORT_BAR))

# ─────────────────────────────────────────────
# 4. Replace exportInboxJSON with buildExportData + exportInboxJSON + publishToRepo
# ─────────────────────────────────────────────
OLD_EXPORT_FN = """\
function exportInboxJSON() {
  let exportData = PAIRINGS_DATA.map(p => Object.assign({}, p));

  for (const [postId, review] of Object.entries(inboxReviews)) {
    if (!review.done) continue;
    const origIdx = exportData.findIndex(p => p.id === postId);
    if (origIdx === -1) continue;
    const origPost = exportData[origIdx];
    // support both old .splits and new .slides model
    const splits = review.slides
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
}"""

NEW_EXPORT_FN = """\
function buildExportData() {
  let exportData = PAIRINGS_DATA.map(p => Object.assign({}, p));
  for (const [postId, review] of Object.entries(inboxReviews)) {
    if (!review.done) continue;
    const origIdx = exportData.findIndex(p => p.id === postId);
    if (origIdx === -1) continue;
    const origPost = exportData[origIdx];
    const splits = review.slides
      ? (review.slides || []).filter(s => s?.action === 'pairing')
      : (review.splits || []).map(s => ({ drinkItems:[{brand:null,product:s.wine||'Unknown',productType:'wine',wineType:s.wineType||'N/A',store:s.store||'Unknown',price:null,vintage:null,region:null,amount:null,notes:null,needsReview:false}], foodItems:[{brand:null,product:s.food||'Unknown',category:'other',store:s.store||'Unknown',price:null,notes:null,needsReview:false}] }));
    if (splits.length > 0) {
      exportData[origIdx] = Object.assign({}, origPost, { category: 'hidden' });
      const children = splits.map((s, i) => {
        const di = s.drinkItems || [];
        const fi = s.foodItems  || [];
        const name = di[0]?.product || 'Unknown';
        return Object.assign({}, origPost, {
          id: postId + '_r' + i, originalPostId: postId,
          drinkName: name, drinkType: 'Wine', drinkItems: di, foodItems: fi,
          wine: name, food: fi.map(f=>f.product).filter(Boolean).join(' + ') || 'Unknown',
          store: di[0]?.store || fi[0]?.store || 'Unknown',
          wineType: di[0]?.wineType || 'N/A',
          category: 'pairing', wineImageUrl: null, foodImageUrl: null,
          isMultiPairingSplit: true,
        });
      });
      exportData.splice(origIdx, 0, ...children);
    } else {
      exportData[origIdx] = Object.assign({}, origPost, { category: 'hidden' });
    }
  }
  return exportData;
}

function exportInboxJSON() {
  const json = JSON.stringify(buildExportData(), null, 2);
  const blob = new Blob([json], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = 'pairings-data-export.json';
  document.body.appendChild(a); a.click();
  document.body.removeChild(a); URL.revokeObjectURL(url);
}

// ── GitHub token + publish ──
const GITHUB_TOKEN_KEY = 'githubToken';
const REPO_OWNER = 'rwolfe1979';
const REPO_NAME  = 'wine-pairing-tracker';
const DATA_PATH  = 'pairings-data.json';

function openTokenSetup() {
  const saved = localStorage.getItem(GITHUB_TOKEN_KEY) || '';
  document.getElementById('tokenInput').value = saved ? '(token saved)' : '';
  document.getElementById('tokenModal').style.display = 'flex';
}
function closeTokenModal() { document.getElementById('tokenModal').style.display = 'none'; }
function saveGitHubToken() {
  const val = document.getElementById('tokenInput').value.trim();
  if (val && val !== '(token saved)') {
    localStorage.setItem(GITHUB_TOKEN_KEY, val);
    alert('Token saved.');
  }
  closeTokenModal();
}
function clearGitHubToken() {
  localStorage.removeItem(GITHUB_TOKEN_KEY);
  document.getElementById('tokenInput').value = '';
  alert('Token cleared.');
}

async function publishToRepo() {
  const token = localStorage.getItem(GITHUB_TOKEN_KEY);
  if (!token) { openTokenSetup(); return; }

  const btn = document.getElementById('publishBtn');
  const origLabel = btn.textContent;
  btn.textContent = '⏳ Publishing…'; btn.disabled = true;

  try {
    const apiBase = `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/contents/${DATA_PATH}`;
    const headers = { 'Authorization': `token ${token}`, 'Accept': 'application/vnd.github.v3+json' };

    // 1. Get current file SHA
    const infoResp = await fetch(apiBase, { headers });
    if (!infoResp.ok) throw new Error(`GitHub API error ${infoResp.status} — check your token.`);
    const info = await infoResp.json();

    // 2. Encode content (handles unicode: emoji, accents, etc.)
    const jsonStr = JSON.stringify(buildExportData(), null, 2);
    const bytes = new TextEncoder().encode(jsonStr);
    let binary = '';
    bytes.forEach(b => binary += String.fromCharCode(b));
    const content = btoa(binary);

    // 3. PUT updated file
    const putResp = await fetch(apiBase, {
      method: 'PUT',
      headers: { ...headers, 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: 'Import inbox review via app', content, sha: info.sha }),
    });
    if (!putResp.ok) {
      const err = await putResp.json();
      throw new Error(err.message || `PUT failed ${putResp.status}`);
    }

    // 4. Reload local data + clear reviewed items
    PAIRINGS_DATA = buildExportData();
    Object.keys(inboxReviews).forEach(id => {
      if (inboxReviews[id]?.done) delete inboxReviews[id];
    });
    saveInboxReviews();
    render(); renderPicks();
    btn.textContent = '✅ Published!';
    setTimeout(() => { btn.textContent = origLabel; btn.disabled = false; }, 3000);
  } catch (err) {
    alert('Publish failed: ' + err.message);
    btn.textContent = origLabel; btn.disabled = false;
  }
}"""

changes.append(('exportInboxJSON + publishToRepo', OLD_EXPORT_FN, NEW_EXPORT_FN))

# ─────────────────────────────────────────────
# 5. Replace init block with initApp() fetch
# ─────────────────────────────────────────────
OLD_INIT = """\
// ─── INIT ───
loadRatings();
renderPicks();
render();"""

NEW_INIT = """\
// ─── INIT ───
function initApp() {
  fetch('./pairings-data.json?v=' + Date.now())
    .then(r => { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(data => { PAIRINGS_DATA = data; loadRatings(); renderPicks(); render(); })
    .catch(() => { loadRatings(); renderPicks(); render(); }); // fallback to embedded []
}
initApp();"""

changes.append(('initApp fetch', OLD_INIT, NEW_INIT))

# ─────────────────────────────────────────────
# Apply all str.replace changes
# ─────────────────────────────────────────────
for desc, old, new in changes:
    count = src.count(old)
    if count == 0:
        print(f'ERROR: [{desc}] NOT FOUND — aborting')
        sys.exit(1)
    if count > 1:
        print(f'WARNING: [{desc}] matched {count} times')
    src = src.replace(old, new)
    print(f'  OK  [{desc}] ({count} replacement(s))')

with open(HTML_FILE, 'w', encoding='utf-8') as f:
    f.write(src)
print(f'\nDone. Wrote {HTML_FILE}')
