(() => {
  'use strict';

  const STORAGE_KEY = 'pl-prompts-v1';
  const THEME_KEY = 'pl-theme';

  const state = {
    data: null,
    activeSubcategory: 'all',
    searchQuery: '',
    activePromptId: null,
    editingId: null,
  };

  const els = {
    grid: document.getElementById('grid'),
    filters: document.getElementById('filters'),
    search: document.getElementById('search'),
    searchClear: document.getElementById('search-clear'),
    resultsMeta: document.getElementById('results-meta'),
    emptyState: document.getElementById('empty-state'),
    themeToggle: document.getElementById('theme-toggle'),
    addBtn: document.getElementById('add-prompt'),
    exportBtn: document.getElementById('export-json'),

    modal: document.getElementById('modal'),
    modalTitle: document.getElementById('modal-title'),
    modalDesc: document.getElementById('modal-desc'),
    modalTag: document.getElementById('modal-tag'),
    modalContent: document.getElementById('modal-content'),
    modalCopy: document.getElementById('modal-copy'),
    modalShare: document.getElementById('modal-share'),

    formModal: document.getElementById('form-modal'),
    formTitle: document.getElementById('form-title'),
    formSubtitle: document.getElementById('form-subtitle'),
    form: document.getElementById('prompt-form'),
    fTitle: document.getElementById('f-title'),
    fSub: document.getElementById('f-subcategory'),
    fDesc: document.getElementById('f-description'),
    fTags: document.getElementById('f-tags'),
    fContent: document.getElementById('f-content'),
    formDelete: document.getElementById('form-delete'),

    toast: document.getElementById('toast'),
  };

  init();

  async function init() {
    initTheme();
    bindGlobalEvents();
    await loadData();
    renderFilters();
    populateSubcategorySelect();
    syncFromHash();
    render();
  }

  // ===== Data loading & persistence =====
  async function loadData() {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        state.data = JSON.parse(stored);
        return;
      } catch (e) {
        console.warn('Failed to parse stored data, falling back to JSON', e);
      }
    }

    try {
      const res = await fetch('prompts.json');
      if (!res.ok) throw new Error('Failed to load prompts.json');
      state.data = await res.json();
      saveData();
    } catch (err) {
      console.error(err);
      els.grid.innerHTML = `<div class="empty-state" style="grid-column:1/-1"><div class="empty-icon">⚠️</div><h2>שגיאה בטעינת הפרומפטים</h2><p>ודא ש-prompts.json נמצא לצד index.html ושאתה מגיש דרך שרת מקומי.</p></div>`;
    }
  }

  function saveData() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state.data));
    } catch (e) {
      console.error('Failed to save', e);
      showToast('⚠️ שמירה נכשלה');
    }
  }

  // ===== Theme =====
  function initTheme() {
    const theme = localStorage.getItem(THEME_KEY) || 'dark';
    document.documentElement.setAttribute('data-theme', theme);
  }

  function toggleTheme() {
    const cur = document.documentElement.getAttribute('data-theme');
    const next = cur === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem(THEME_KEY, next);
  }

  // ===== Events =====
  function bindGlobalEvents() {
    els.themeToggle.addEventListener('click', toggleTheme);
    els.addBtn.addEventListener('click', () => openForm(null));
    els.exportBtn.addEventListener('click', exportJson);

    els.search.addEventListener('input', (e) => {
      state.searchQuery = e.target.value.trim();
      els.searchClear.hidden = !state.searchQuery;
      render();
    });

    els.searchClear.addEventListener('click', () => {
      els.search.value = '';
      state.searchQuery = '';
      els.searchClear.hidden = true;
      els.search.focus();
      render();
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        if (!els.formModal.hidden) closeForm();
        else if (!els.modal.hidden) closeModal();
      }
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        els.search.focus();
        els.search.select();
      }
    });

    els.modal.addEventListener('click', (e) => {
      if (e.target.dataset.close !== undefined || e.target.closest('[data-close]')) closeModal();
    });

    els.formModal.addEventListener('click', (e) => {
      if (e.target.dataset.closeForm !== undefined || e.target.closest('[data-close-form]')) closeForm();
    });

    els.form.addEventListener('submit', (e) => {
      e.preventDefault();
      submitForm();
    });

    els.formDelete.addEventListener('click', () => {
      if (!state.editingId) return;
      if (confirm('למחוק את הפרומפט הזה? לא ניתן לשחזר.')) {
        deletePrompt(state.editingId);
        closeForm();
      }
    });

    els.modalCopy.addEventListener('click', () => {
      const p = getPrompt(state.activePromptId);
      if (!p) return;
      copyText(p.content).then(() => {
        markCopied(els.modalCopy);
        showToast('הפרומפט הועתק ללוח 📋');
      });
    });

    els.modalShare.addEventListener('click', () => {
      const p = getPrompt(state.activePromptId);
      if (p) sharePrompt(p);
    });

    window.addEventListener('hashchange', syncFromHash);
  }

  function syncFromHash() {
    const hash = window.location.hash.replace(/^#/, '');
    if (hash.startsWith('p/')) {
      const id = decodeURIComponent(hash.slice(2));
      const p = getPrompt(id);
      if (p) openModal(p);
    }
  }

  // ===== Render =====
  function renderFilters() {
    const subs = state.data.subcategories;
    const counts = countBySubcategory();
    const total = state.data.prompts.length;

    const items = [
      { id: 'all', name: 'הכול', icon: '✨', count: total },
      ...subs.map((s) => ({ ...s, count: counts[s.id] || 0 })),
    ];

    els.filters.innerHTML = items
      .map((it) => `
        <button class="chip ${state.activeSubcategory === it.id ? 'active' : ''}" data-id="${it.id}">
          <span>${it.icon || ''}</span>
          <span>${escapeHtml(it.name)}</span>
          <span class="count">${it.count}</span>
        </button>
      `)
      .join('');

    els.filters.querySelectorAll('.chip').forEach((btn) => {
      btn.addEventListener('click', () => {
        state.activeSubcategory = btn.dataset.id;
        renderFilters();
        render();
      });
    });
  }

  function populateSubcategorySelect() {
    els.fSub.innerHTML = state.data.subcategories
      .map((s) => `<option value="${s.id}">${s.icon || ''} ${escapeHtml(s.name)}</option>`)
      .join('');
  }

  function countBySubcategory() {
    const counts = {};
    for (const p of state.data.prompts) counts[p.subcategory] = (counts[p.subcategory] || 0) + 1;
    return counts;
  }

  function render() {
    const filtered = filterPrompts();
    els.resultsMeta.textContent = filtered.length ? `מציג ${filtered.length} פרומפטים` : '';

    if (filtered.length === 0) {
      els.grid.innerHTML = '';
      els.emptyState.hidden = false;
      return;
    }

    els.emptyState.hidden = true;
    els.grid.innerHTML = filtered.map(cardHtml).join('');

    els.grid.querySelectorAll('.card').forEach((card) => {
      const id = card.dataset.id;
      card.addEventListener('click', (e) => {
        if (e.target.closest('.card-btn') || e.target.closest('.card-icon-btn')) return;
        const p = getPrompt(id);
        if (p) openModal(p);
      });
    });

    els.grid.querySelectorAll('[data-action="copy"]').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const p = getPrompt(btn.dataset.id);
        if (!p) return;
        copyText(p.content).then(() => {
          markCopied(btn);
          showToast('הפרומפט הועתק ללוח 📋');
        });
      });
    });

    els.grid.querySelectorAll('[data-action="share"]').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const p = getPrompt(btn.dataset.id);
        if (p) sharePrompt(p);
      });
    });

    els.grid.querySelectorAll('[data-action="edit"]').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        openForm(btn.dataset.id);
      });
    });
  }

  function cardHtml(p) {
    const sub = state.data.subcategories.find((s) => s.id === p.subcategory);
    const tagText = sub ? `${sub.icon || ''} ${sub.name}` : '';
    const tags = (p.tags || []).slice(0, 4).map((t) => `<span class="t">#${escapeHtml(t)}</span>`).join('');
    const userBadge = p.userCreated ? `<span class="user-badge">שלי</span>` : '';

    return `
      <article class="card" data-id="${p.id}" tabindex="0" role="button" aria-label="${escapeHtml(p.title)}">
        <div class="card-head">
          <span class="card-tag">${escapeHtml(tagText)}${userBadge}</span>
          <button class="card-icon-btn" data-action="edit" data-id="${p.id}" title="ערוך" aria-label="ערוך פרומפט">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
          </button>
        </div>
        <h3>${escapeHtml(p.title)}</h3>
        <p class="card-desc">${escapeHtml(p.description || '')}</p>
        ${tags ? `<div class="card-tags">${tags}</div>` : ''}
        <div class="card-actions">
          <button class="card-btn primary" data-action="copy" data-id="${p.id}">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
            <span>העתק</span>
          </button>
          <button class="card-btn" data-action="share" data-id="${p.id}">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"></circle><circle cx="6" cy="12" r="3"></circle><circle cx="18" cy="19" r="3"></circle><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line></svg>
            <span>שתף</span>
          </button>
        </div>
      </article>
    `;
  }

  function filterPrompts() {
    let list = state.data.prompts;
    if (state.activeSubcategory !== 'all') {
      list = list.filter((p) => p.subcategory === state.activeSubcategory);
    }
    const q = state.searchQuery.toLowerCase();
    if (q) {
      list = list.filter((p) => {
        const haystack = [p.title, p.description, p.content, ...(p.tags || [])].join(' ').toLowerCase();
        return haystack.includes(q);
      });
    }
    return list;
  }

  // ===== View modal =====
  function openModal(p) {
    state.activePromptId = p.id;
    const sub = state.data.subcategories.find((s) => s.id === p.subcategory);
    els.modalTag.textContent = sub ? `${sub.icon || ''} ${sub.name}` : '';
    els.modalTitle.textContent = p.title;
    els.modalDesc.textContent = p.description || '';
    els.modalContent.textContent = p.content || '';
    resetCopiedState(els.modalCopy);
    els.modal.hidden = false;
    document.body.style.overflow = 'hidden';

    if (window.location.hash !== `#p/${p.id}`) {
      history.replaceState(null, '', `#p/${encodeURIComponent(p.id)}`);
    }
  }

  function closeModal() {
    els.modal.hidden = true;
    state.activePromptId = null;
    document.body.style.overflow = '';
    if (window.location.hash) history.replaceState(null, '', window.location.pathname + window.location.search);
  }

  // ===== Form (create / edit) =====
  function openForm(id) {
    state.editingId = id;
    const editing = id ? getPrompt(id) : null;

    if (editing) {
      els.formTitle.textContent = 'עריכת פרומפט';
      els.formSubtitle.textContent = 'ערוך את פרטי הפרומפט ולחץ "שמור"';
      els.fTitle.value = editing.title || '';
      els.fSub.value = editing.subcategory || state.data.subcategories[0]?.id;
      els.fDesc.value = editing.description || '';
      els.fTags.value = (editing.tags || []).join(', ');
      els.fContent.value = editing.content || '';
      els.formDelete.hidden = false;
    } else {
      els.formTitle.textContent = 'פרומפט חדש';
      els.formSubtitle.textContent = 'מלא את השדות כדי לשמור פרומפט חדש בספרייה';
      els.form.reset();
      els.fSub.value = state.data.subcategories[0]?.id || '';
      els.formDelete.hidden = true;
    }

    els.formModal.hidden = false;
    document.body.style.overflow = 'hidden';
    setTimeout(() => els.fTitle.focus(), 50);
  }

  function closeForm() {
    els.formModal.hidden = true;
    state.editingId = null;
    document.body.style.overflow = els.modal.hidden ? '' : 'hidden';
  }

  function submitForm() {
    const title = els.fTitle.value.trim();
    const content = els.fContent.value.trim();
    if (!title || !content) return;

    const data = {
      title,
      subcategory: els.fSub.value,
      description: els.fDesc.value.trim(),
      content,
      tags: els.fTags.value.split(',').map((t) => t.trim()).filter(Boolean),
    };

    if (state.editingId) {
      const idx = state.data.prompts.findIndex((p) => p.id === state.editingId);
      if (idx !== -1) {
        state.data.prompts[idx] = { ...state.data.prompts[idx], ...data };
      }
      showToast('הפרומפט עודכן ✓');
    } else {
      const newPrompt = {
        id: `u_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
        userCreated: true,
        createdAt: new Date().toISOString(),
        ...data,
      };
      state.data.prompts.unshift(newPrompt);
      showToast('הפרומפט נוסף ✓');
    }

    saveData();
    renderFilters();
    render();
    closeForm();
  }

  function deletePrompt(id) {
    state.data.prompts = state.data.prompts.filter((p) => p.id !== id);
    saveData();
    renderFilters();
    render();
    showToast('הפרומפט נמחק');
  }

  // ===== Export =====
  function exportJson() {
    const blob = new Blob([JSON.stringify(state.data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    const date = new Date().toISOString().slice(0, 10);
    a.download = `prompts-${date}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast('הקובץ הורד 💾 — אפשר להחליף איתו את prompts.json');
  }

  // ===== Share =====
  async function sharePrompt(p) {
    const url = `${location.origin}${location.pathname}#p/${encodeURIComponent(p.id)}`;
    const shareData = { title: p.title, text: p.description || p.title, url };

    if (navigator.share) {
      try { await navigator.share(shareData); return; }
      catch (err) { if (err.name === 'AbortError') return; }
    }
    await copyText(url);
    showToast('הקישור הועתק ללוח 🔗');
  }

  // ===== Helpers =====
  function getPrompt(id) {
    return state.data?.prompts.find((p) => p.id === id);
  }

  async function copyText(text) {
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      const ta = document.createElement('textarea');
      ta.value = text;
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
    }
  }

  function markCopied(btn) {
    const label = btn.querySelector('span');
    const original = label?.textContent;
    btn.classList.add('copied');
    if (label) label.textContent = 'הועתק ✓';
    setTimeout(() => {
      btn.classList.remove('copied');
      if (label && original) label.textContent = original;
    }, 1500);
  }

  function resetCopiedState(btn) {
    const label = btn.querySelector('span');
    btn.classList.remove('copied');
    if (label) label.textContent = 'העתק פרומפט';
  }

  let toastTimer;
  function showToast(msg) {
    els.toast.textContent = msg;
    els.toast.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => { els.toast.hidden = true; }, 2400);
  }

  function escapeHtml(s) {
    return String(s ?? '').replace(/[&<>"']/g, (c) => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
    }[c]));
  }
})();
