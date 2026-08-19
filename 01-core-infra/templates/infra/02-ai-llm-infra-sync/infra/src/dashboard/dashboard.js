// Client-side dashboard interactivity
// Auto-refresh, toast notifications, modals, cron toggle, sync trigger

(function () {
  'use strict';

  const API_BASE = '';
  let refreshTimer = null;
  let refreshInterval = 10000; // 10 seconds
  let syncInProgress = false;

  // --- Toast ---
  function showToast(message, isError = false) {
    const toast = document.getElementById('toast');
    if (!toast) return;
    toast.textContent = message;
    toast.className = `fixed bottom-4 right-4 px-4 py-2 rounded-md text-sm font-medium ${isError ? 'bg-red-600' : 'bg-green-600'} text-white`;
    toast.classList.remove('hidden');
    clearTimeout(toast._hide);
    toast._hide = setTimeout(() => { toast.classList.add('hidden'); }, 3000);
  }

  // --- Modal ---
  const modalOverlay = document.getElementById('modal-overlay');
  const modalForm = document.getElementById('modal-form');
  const modalTitle = document.getElementById('modal-title');
  const modalProvider = document.getElementById('modal-provider');
  const modalLabel = document.getElementById('modal-label');
  const modalKey = document.getElementById('modal-key');

  function openModal(providerHint = '') {
    if (modalProvider) modalProvider.value = providerHint;
    if (modalLabel) modalLabel.value = '';
    if (modalKey) modalKey.value = '';
    if (modalTitle) modalTitle.textContent = providerHint ? 'Add Key to ' + providerHint : 'Add API Key';
    if (modalOverlay) modalOverlay.classList.remove('hidden');
  }

  function closeModal() {
    if (modalOverlay) modalOverlay.classList.add('hidden');
  }

  document.getElementById('modal-cancel')?.addEventListener('click', closeModal);
  document.getElementById('btn-add-key-global')?.addEventListener('click', () => openModal());

  // Provider row + / − buttons (delegated)
  document.addEventListener('click', (e) => {
    if (e.target instanceof HTMLButtonElement && e.target.classList.contains('btn-key-add')) {
      openModal(e.target.dataset.prov || '');
    }
    if (e.target instanceof HTMLButtonElement && e.target.classList.contains('btn-key-rm')) {
      const prov = e.target.dataset.prov;
      if (prov && confirm(`Remove all keys for "${prov}"?`)) {
        deleteProviderKeys(prov);
      }
    }
  });

  async function deleteProviderKeys(provider) {
    try {
      const res = await fetch(`${API_BASE}/api/key/${encodeURIComponent(provider)}`, { method: 'DELETE' });
      const data = await res.json();
      if (data.ok) {
        showToast(`Keys removed for ${provider}`);
        refreshDashboard();
      } else {
        showToast('Failed: ' + (data.error || 'unknown'), true);
      }
    } catch (err) {
      showToast('Network error: ' + err.message, true);
    }
  }

  // Modal submit (add key)
  modalForm?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const provider = modalProvider?.value.trim();
    const label = modalLabel?.value.trim();
    const key = modalKey?.value.trim();
    if (!provider || !label || !key) {
      showToast('All fields required', true);
      return;
    }
    try {
      const res = await fetch(`${API_BASE}/api/key`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider, label, key }),
      });
      const data = await res.json();
      if (data.ok) {
        showToast(`Key added to ${provider}`);
        closeModal();
        refreshDashboard();
      } else {
        showToast('Failed: ' + (data.error || 'unknown'), true);
      }
    } catch (err) {
      showToast('Network error: ' + err.message, true);
    }
  });

  // --- Sync Now ---
  document.getElementById('btn-sync-now')?.addEventListener('click', async () => {
    if (syncInProgress) return;
    syncInProgress = true;
    const btn = document.getElementById('btn-sync-now');
    if (btn) { btn.disabled = true; btn.textContent = '⟳ Syncing...'; }
    try {
      const res = await fetch(`${API_BASE}/sync`, { method: 'POST' });
      const data = await res.json();
      showToast(data.started ? 'Sync started' : 'Failed to start sync', !data.started);
      setTimeout(refreshDashboard, 1500);
    } catch (err) {
      showToast('Network error: ' + err.message, true);
    } finally {
      syncInProgress = false;
      if (btn) { btn.disabled = false; btn.textContent = '⟳ Sync Now'; }
    }
  });

  // --- Cron Toggle ---
  const cronToggle = document.getElementById('cron-toggle');
  if (cronToggle) {
    cronToggle.addEventListener('change', async (e) => {
      const target = e.target;
      const enabled = (target && target instanceof HTMLInputElement) ? target.checked : false;
      try {
        const res = await fetch(`${API_BASE}/api/cron`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ enabled }),
        });
        const data = await res.json();
        if (data.ok) {
          showToast(enabled ? 'Cron sync enabled' : 'Cron sync disabled');
          refreshDashboard();
        } else {
          showToast('Failed: ' + (data.error || 'unknown'), true);
        }
      } catch (err) {
        showToast('Network error: ' + err.message, true);
      }
    });
  }

  // Save cron schedule
  document.getElementById('btn-save-cron')?.addEventListener('click', async () => {
    const scheduleSelect = document.getElementById('cron-schedule');
    const schedule = (scheduleSelect && scheduleSelect instanceof HTMLSelectElement) ? scheduleSelect.value : undefined;
    if (!schedule) return;
    try {
      const res = await fetch(`${API_BASE}/api/cron`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ schedule }),
      });
      const data = await res.json();
      if (data.ok) {
        showToast('Schedule updated');
        refreshDashboard();
      } else {
        showToast('Failed: ' + (data.error || 'unknown'), true);
      }
    } catch (err) {
      showToast('Network error: ' + err.message, true);
    }
  });

  // --- Dashboard Refresh ---
  async function refreshDashboard() {
    if (syncInProgress) return;
    try {
      const res = await fetch(`${API_BASE}/dashboard?partial=1`);
      if (!res.ok) {
        console.error('Failed to fetch partial dashboard');
        return;
      }
      const html = await res.text();
      // Simple partial refresh: replace main content area
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, 'text/html');
      const newContent = doc.querySelector('#dashboard-content');
      const currentContent = document.getElementById('dashboard-content');
      if (newContent && currentContent) {
        currentContent.innerHTML = newContent.innerHTML;
        // Re-attach event listeners to new elements if needed, or rely on delegation
      }
    } catch (err) {
      console.error('Dashboard refresh error:', err);
      showToast('Dashboard refresh failed: ' + err.message, true);
    }
  }

  // --- Auto-refresh ---
  function startAutoRefresh() {
    if (refreshTimer) clearInterval(refreshTimer);
    refreshTimer = setInterval(() => {
      refreshDashboard();
    }, refreshInterval);
  }

  startAutoRefresh();

  // Keyboard shortcuts
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeModal();
    if (e.key === 's' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      document.getElementById('btn-sync-now')?.click();
    }
  });

  console.log('Dashboard ready. Auto-refresh every ' + (refreshInterval / 1000) + 's.');
})();
