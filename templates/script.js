(function() {
  let A = { threads: [] }; // INDEX
  let B = {}; // CACHE
  let C = []; // filteredItems
  let D = 10; // visibleCount
  let E = 10; // pageSize
  
  const F = document.getElementById('threadList');
  const G = document.getElementById('q');
  const H = document.querySelectorAll('.filter-chip[data-model]');
  const I = document.getElementById('topicFilter');
  const J = document.getElementById('sortBy');
  
  const K = document.getElementById('statThreads');
  const L = document.getElementById('statReplies');
  const M = document.getElementById('statUsers');
  const N = document.getElementById('statViews');
  const O = document.getElementById('mainHeading');
  
  const P = document.getElementById('detailModal');
  const Q = document.getElementById('modalScroll');
  const R = document.getElementById('modalTitle');
  const S = document.getElementById('closeModal');
  const T = document.getElementById('themeToggle');
  
  let U = { query: '', model: '', topic: '', sort: 'recent' }; // currentFilters
  let V = new Set(); // expandedThreads

  function track(n, p = {}) { if (typeof gtag === 'function') { gtag('event', n, p); } }

  async function init() {
    it();
    try {
      const r = await fetch('data.json');
      if (!r.ok) throw new Error("Database not found.");
      A = await r.json();
      const u = [...new Set(A.threads.map(t => t.topic_group).filter(Boolean))].sort();
      u.forEach(t => { const o = document.createElement('option'); o.value = t; o.innerText = t; I.appendChild(o); });
      const p = new URLSearchParams(window.location.search);
      U.model = p.get('model') || (!window.location.search ? 'F54' : '');
      U.topic = p.get('topic') || '';
      if (U.topic) I.value = U.topic;
      cu(U.model);
      af();
      rn();
    } catch(e) { console.error(e); F.innerHTML = `<div class="empty-state">Unable to load database.</div>`; }
  }

  function it() { const s = localStorage.getItem('theme'); const d = window.matchMedia('(prefers-color-scheme: dark)').matches; document.body.className = s || (d ? 'theme-dark' : 'theme-light'); ub(); }
  function tt() { const d = document.body.classList.contains('theme-dark'); const n = d ? 'theme-light' : 'theme-dark'; document.body.className = n; localStorage.setItem('theme', n); ub(); }
  function ub() { T.innerText = document.body.classList.contains('theme-dark') ? '☀️' : '🌙'; }
  function cu(m) { H.forEach(c => { if (c.dataset.model === m) c.classList.add('active'); else c.classList.remove('active'); }); }

  function af() {
    let i = (A.threads || []).slice();
    const m = U.model;
    if (m && m !== 'All') {
      i = i.filter(t => t.model === m || (m === 'F54' && t.source_file === 'f54.txt'));
      O.innerText = `Samsung ${m} Complaints Board`;
    } else { O.innerText = "Samsung Dashboard (All Models)"; }
    if (U.topic) i = i.filter(t => t.topic_group === U.topic);
    if (U.query) { const q = U.query.toLowerCase(); i = i.filter(t => [t.title, t.model, t.topic_group, t.author].join(' ').toLowerCase().includes(q)); }
    i.sort((a,b) => new Date(b.published || 0) - new Date(a.published || 0));
    C = i; D = E;
    K.innerText = C.length;
    L.innerText = C.reduce((a, t) => a + (t.reply_count || 0), 0);
    N.innerText = C.reduce((a, t) => a + (t.views || 0), 0);
    M.innerText = new Set(C.map(t => t.author)).size;
  }

  function rn(ap = false) {
    if (C.length === 0) { F.innerHTML = `<div class="empty-state">No matching complaints found.</div>`; return; }
    const k = C.slice(D - E, D);
    const h = k.map(t => {
      const x = V.has(t.thread_id);
      return `
        <div class="thread-card ${x ? 'expanded' : ''}" onclick="window.hcc('${t.thread_id}', event)" id="card-${t.thread_id}">
          <div class="badge-row">
            <span class="badge badge-model">${es(t.model)}</span>
            <span class="badge badge-issue">${es(t.topic_group)}</span>
            <span class="badge badge-meta">📅 ${fd(t.published)}</span>
            <span class="badge badge-meta">💬 ${t.reply_count}</span>
          </div>
          <h2>${es(t.title)}</h2>
          ${!x ? `<div class="preview-text">${es(t.preview)}...</div>` : ''}
          <div style="display:flex; justify-content:space-between; align-items:center;">
             <span class="msg-author">@${es(t.author)}</span>
             <button class="show-replies-btn desktop-only" onclick="event.stopPropagation(); window.hcc('${t.thread_id}', event)">
                ${x ? 'Hide' : 'Replies'}
             </button>
          </div>
          <div id="details-${t.thread_id}" class="inline-replies" style="display:${x ? 'flex' : 'none'}">
             <div class="empty-state">Loading history...</div>
          </div>
        </div>
      `;
    }).join('');
    if (ap) F.insertAdjacentHTML('beforeend', h); else F.innerHTML = h;
  }

  async function fdt(id) {
    if (B[id]) return B[id];
    try {
      const r = await fetch(`api/${id}.json`);
      if (!r.ok) return null;
      B[id] = await r.json();
      return B[id];
    } catch(e) { return null; }
  }

  window.hcc = async function(id, e) {
    if (window.innerWidth > 800) {
        if (V.has(id)) { V.delete(id); document.getElementById(`details-${id}`).style.display = 'none'; } else {
            V.add(id); track('board_interaction', { action: 'thread_expand', thread_id: id });
            const d = document.getElementById(`details-${id}`); d.style.display = 'flex';
            const x = await fdt(id);
            if (x) d.innerHTML = x.messages.map(m => rm(m, x)).join(''); else d.innerHTML = '<div class="empty-state">Request failed.</div>';
        }
    } else { ot(id); }
  };

  async function ot(id) {
    const x = A.threads.find(t => String(t.thread_id) === String(id));
    if (!x) return;
    R.innerHTML = es(x.title); Q.innerHTML = '<div class="empty-state">Connecting...</div>';
    P.classList.add('modal-active'); document.body.classList.add('modal-open-scroll');
    const d = await fdt(id);
    if (d) Q.innerHTML = d.messages.map(m => rm(m, d)).join(''); else Q.innerHTML = '<div class="empty-state">Load failed.</div>';
  }

  function rm(m, t) {
    const i = (m.images || []).length ? `<div class="msg-images">${m.images.map(u => `<img src="${ea(u)}" class="msg-img-thumb" onclick="event.stopPropagation();window.open('${ea(u)}')">`).join('')}</div>` : '';
    return `
      <div class="message ${m.source === 'comment' ? 'is-reply' : ''}">
        <div class="msg-info"><span class="msg-author">@${es(m.author)}</span><span class="msg-date">${fd(m.published)}</span></div>
        <div class="msg-body">${es(m.text)}</div>
        ${i}
      </div>
    `;
  }

  window.onscroll = function() { if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight - 500) { if (D < C.length) { D += E; rn(true); } } };
  S.onclick = function() { P.classList.remove('modal-active'); document.body.classList.remove('modal-open-scroll'); };
  G.oninput = function() { U.query = G.value; track('board_interaction', { action: 'search', term: G.value }); af(); rn(); };
  I.onchange = function() { U.topic = I.value; af(); rn(); };
  J.onchange = function() { U.sort = J.value; af(); rn(); };
  H.forEach(c => { c.onclick = function() { U.model = c.dataset.model || 'All'; cu(U.model); af(); rn(); }; });
  T.onclick = tt;
  function fd(d) { return d ? new Date(d).toLocaleDateString() : ''; }
  function es(v) { return String(v ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }
  function ea(v) { return es(v).replace(/"/g, "&quot;"); }
  init();
})();
