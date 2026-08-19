export interface DashboardContext {
  providers: Record<string, any[]>;
  sync_metadata: {
    total_keys: number;
    providers_active: string[];
    sources_synced: Array<{ file: string; fmt: string; exists: boolean; last_ok: string | null }>;
  };
  last_sync: string;
  last_sync_duration_ms: number;
  last_sync_result: string;
  cron: {
    enabled: boolean;
    schedule: string;
    last_run: string | null;
    next_run: string | null;
  };
  history: Array<{
    timestamp: string;
    duration_ms: number;
    providers: number;
    keys: number;
    result: string;
    sources_ok: number;
    sources_total: number;
  }>;
  version: string;
}

function fmtTime(iso: string | null | undefined): string {
  if (!iso) return '—';
  const d = new Date(iso);
  const ago = Math.floor((Date.now() - d.getTime()) / 1000);
  if (ago < 60) return `${ago}s ago`;
  if (ago < 3600) return `${Math.floor(ago / 60)}m ago`;
  if (ago < 86400) return `${Math.floor(ago / 3600)}h ago`;
  return d.toLocaleDateString();
}

function fmtDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(2)}s`;
}

function escapeHtml(s: string): string {
  return s.replace(/&/g, '&').replace(/</g, '<').replace(/>/g, '>').replace(/"/g, '"');
}

export function renderDashboard(ctx: DashboardContext): string {
  const provRows = Object.entries(ctx.providers)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([name, keys]) => {
      const active = keys.length > 0;
      const dot = active ? '🟢' : '⚪';
      const sources = [...new Set(keys.map((k: any) => k.source || '?'))];
      return `<tr class="hover:bg-gray-700/50">
        <td class="px-4 py-3 font-medium text-left whitespace-nowrap">${dot} ${escapeHtml(name)}</td>
        <td class="px-4 py-3 text-center">${keys.length}</td>
        <td class="px-4 py-3 text-sm">${sources.map(s => escapeHtml(s)).join(', ')}</td>
        <td class="px-4 py-3 text-right space-x-2">
          <button class="btn-key-add bg-green-600 hover:bg-green-700 text-white font-medium px-3 py-1 rounded text-sm" data-prov="${escapeHtml(name)}">+</button>
          <button class="btn-key-rm bg-red-600 hover:bg-red-700 text-white font-medium px-3 py-1 rounded text-sm" data-prov="${escapeHtml(name)}">−</button>
        </td>
      </tr>`;
    }).join('\n');

  const srcRows = (ctx.sync_metadata.sources_synced || []).map((s) => {
    const dot = s.exists ? '✅' : '❌';
    const file = s.file.replace(process.env.HOME || '', '~');
    return `<tr class="border-t">
      <td class="px-4 py-3">${dot} ${escapeHtml(file)}</td>
      <td class="px-4 py-3 text-center">${s.fmt}</td>
      <td class="px-4 py-3 text-center">${s.exists ? 'present' : 'missing'}</td>
      <td class="px-4 py-3 text-right">${fmtTime(s.last_ok)}</td>
    </tr>`;
  }).join('\n');

  const histRows = ctx.history.slice(0, 15).map((h) => {
    const icon = h.result === 'ok' ? '✅' : '❌';
    return `<tr class="border-t">
      <td class="px-4 py-3">${fmtTime(h.timestamp)}</td>
      <td class="px-4 py-3 text-center">${icon}</td>
      <td class="px-4 py-3 text-center">${h.providers}</td>
      <td class="px-4 py-3 text-center">${h.keys}</td>
      <td class="px-4 py-3 text-right">${fmtDuration(h.duration_ms)}</td>
    </tr>`;
  }).join('\n');

  const totalSources = ctx.sync_metadata.sources_synced.length;
  const healthySources = ctx.sync_metadata.sources_synced.filter((s) => s.exists).length;
  const syncIcon = ctx.last_sync_result === 'ok' ? '✅' : '❌';
  const cronChecked = ctx.cron?.enabled ? 'checked' : '';
  const lastCron = ctx.cron?.last_run ? fmtTime(ctx.cron.last_run) : '—';
  const nextCron = ctx.cron?.enabled && ctx.cron?.next_run ? fmtTime(ctx.cron.next_run) : '—';
  const totalKeys = ctx.providers ? Object.values(ctx.providers).flat().length : 0;
  const totalProvs = Object.keys(ctx.providers || {}).length;
  const activeProvs = Object.values(ctx.providers || {}).filter((k: any[]) => k.length > 0).length;

  return `<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>LLM Infra Sync Dashboard</title>
  <link rel="stylesheet" href="/static/output.css" />
</head>
<body class="bg-gray-900 text-gray-100 min-h-screen">
  <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-6">
    <header class="mb-8">
      <h1 class="text-2xl font-bold text-gray-100">
        🔐 LLM‑Infra‑Sync Dashboard <span class="text-gray-400 text-sm">v${escapeHtml(ctx.version)}</span>
      </h1>
    </header>

    <!-- Stats Cards -->
    <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-8">
      <div class="bg-gray-800 rounded-lg p-4">
        <h3 class="text-xs font-medium text-gray-400 mb-2">Total Keys</h3>
        <p class="text-2xl font-bold">${totalKeys}</p>
      </div>
      <div class="bg-gray-800 rounded-lg p-4">
        <h3 class="text-xs font-medium text-gray-400 mb-2">Active Providers</h3>
        <p class="text-2xl font-bold">${activeProvs}<span class="text-xs text-gray-400 ml-1">/${totalProvs}</span></p>
      </div>
      <div class="bg-gray-800 rounded-lg p-4">
        <h3 class="text-xs font-medium text-gray-400 mb-2">Sources</h3>
        <p class="text-2xl font-bold">${healthySources}<span class="text-xs text-gray-400 ml-1">/${totalSources}</span></p>
        <p class="text-xs text-gray-400 mt-1">healthy</p>
      </div>
      <div class="bg-gray-800 rounded-lg p-4">
        <h3 class="text-xs font-medium text-gray-400 mb-2">Last Sync</h3>
        <p class="text-2xl font-bold flex items-center gap-2">
          ${syncIcon} ${fmtTime(ctx.last_sync)}
        </p>
        <p class="text-xs text-gray-400 mt-1">${fmtDuration(ctx.last_sync_duration_ms)}</p>
      </div>
    </div>

    <!-- Main Content -->
    <div class="grid gap-6">
      <!-- Left Column -->
      <div class="lg:w-1/2">
        <!-- Source Health -->
        <section class="mb-6">
          <h2 class="text-lg font-semibold mb-4">📡 Source Health</h2>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-700">
              <thead>
                <tr class="bg-gray-800">
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Source</th>
                  <th class="px-4 py-3 text-center text-xs font-medium text-gray-400 uppercase tracking-wider">Format</th>
                  <th class="px-4 py-3 text-center text-xs font-medium text-gray-400 uppercase tracking-wider">Status</th>
                  <th class="px-4 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">Last OK</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-700">
                ${srcRows || '<tr><td colspan="4" class="px-4 py-3 text-center text-gray-500">No sources configured</td></tr>'}
              </tbody>
            </table>
          </div>
        </section>

        <!-- Sync Controls -->
        <section class="mb-6">
          <h2 class="text-lg font-semibold mb-4">⚙️ Sync Controls</h2>
          <div class="space-y-4">
            <button id="btn-sync-now" class="w-full bg-green-600 hover:bg-green-700 text-white font-medium py-3 px-4 rounded-lg transition-colors duration-200">
              ⟳ Sync Now
            </button>
            <div id="sync-status" class="text-center text-sm text-gray-400 min-h-4"></div>

            <div class="flex items-center space-x-4">
              <label class="flex items-center text-sm font-medium text-gray-300">
                <input type="checkbox" id="cron-toggle" class="h-4 w-4 text-green-600 bg-gray-700 border-gray-600 rounded focus:ring-primary-500" ${cronChecked}>
                <span class="ml-2">Cron Sync</span>
              </label>
              <div class="ml-auto flex items-center space-x-2">
                <label class="text-sm font-medium text-gray-300">Schedule:</label>
                <select id="cron-schedule" class="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-gray-100 focus:ring-2 focus:ring-green-500">
                  <option value="*/15 * * * *" ${ctx.cron?.schedule === '*/15 * * * *' ? 'selected' : ''}>Every 15 min</option>
                  <option value="*/30 * * * *" ${ctx.cron?.schedule === '*/30 * * * *' ? 'selected' : ''}>Every 30 min</option>
                  <option value="0 * * * *" ${ctx.cron?.schedule === '0 * * * *' ? 'selected' : ''}>Every hour</option>
                  <option value="0 */6 * * *" ${ctx.cron?.schedule === '0 */6 * * *' ? 'selected' : ''}>Every 6 hours</option>
                  <option value="0 0 * * *" ${ctx.cron?.schedule === '0 0 * * *' ? 'selected' : ''}>Daily</option>
                </select>
                <button id="btn-save-cron" class="bg-gray-700 hover:bg-gray-600 text-white font-medium px-3 py-2 rounded text-sm">Save</button>
              </div>
            </div>
            <div class="text-xs text-gray-500 mt-2 flex justify-between">
              <span>Last cron: <span id="cron-last" class="font-medium">${lastCron}</span></span>
              <span>Next: <span id="cron-next" class="font-medium">${nextCron}</span></span>
            </div>
          </div>
        </section>
      </div>

      <!-- Right Column -->
      <div class="lg:w-1/2">
        <!-- Providers Table -->
        <section class="mb-6">
          <div class="flex justify-between items-start mb-4">
            <h2 class="text-lg font-semibold">📋 Providers</h2>
            <button id="btn-add-key-global" class="bg-blue-600 hover:bg-blue-700 text-white font-medium px-4 py-2 rounded">+ Add Key</button>
          </div>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-700">
              <thead>
                <tr class="bg-gray-800">
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Provider</th>
                  <th class="px-4 py-3 text-center text-xs font-medium text-gray-400 uppercase tracking-wider">Keys</th>
                  <th class="px-4 py-3 text-center text-xs font-medium text-gray-400 uppercase tracking-wider">Sources</th>
                  <th class="px-4 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-700">
                ${provRows || '<tr><td colspan="4" class="px-4 py-3 text-center text-gray-500">No providers yet</td></tr>'}
              </tbody>
            </table>
          </div>
        </section>

        <!-- Sync History -->
        <section>
          <h2 class="text-lg font-semibold mb-4">📜 Sync History</h2>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-700">
              <thead>
                <tr class="bg-gray-800">
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Time</th>
                  <th class="px-4 py-3 text-center text-xs font-medium text-gray-400 uppercase tracking-wider">Result</th>
                  <th class="px-4 py-3 text-center text-xs font-medium text-gray-400 uppercase tracking-wider">Providers</th>
                  <th class="px-4 py-3 text-center text-xs font-medium text-gray-400 uppercase tracking-wider">Keys</th>
                  <th class="px-4 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">Duration</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-700">
                ${histRows || '<tr><td colspan="5" class="px-4 py-3 text-center text-gray-500">No history yet</td></tr>'}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </div>

    <!-- Toast Notification -->
    <div id="toast" class="fixed bottom-4 right-4 hidden px-4 py-2 rounded-md text-sm font-medium transition-opacity duration-300"></div>

    <!-- Add Key Modal -->
    <div id="modal-overlay" class="fixed inset-0 bg-black/50 hidden flex items-center justify-center z-50">
      <div class="bg-gray-800 rounded-lg p-6 w-96">
        <h3 id="modal-title" class="text-lg font-semibold mb-4">Add API Key</h3>
        <form id="modal-form" class="space-y-4">
          <div>
            <label for="modal-provider" class="block text-sm font-medium text-gray-300 mb-1">Provider</label>
            <input list="providers-list" id="modal-provider" class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:outline-none focus:ring-2 focus:ring-green-500" placeholder="e.g. openrouter" required />
            <datalist id="providers-list">
              ${Object.keys(ctx.providers || {}).map(p => `<option value="${escapeHtml(p)}">`).join('')}
              <option value="openrouter"><option value="gemini"><option value="xai"><option value="anthropic">
            </datalist>
          </div>
          <div>
            <label for="modal-label" class="block text-sm font-medium text-gray-300 mb-1">Label</label>
            <input id="modal-label" class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:outline-none focus:ring-2 focus:ring-green-500" placeholder="e.g. my-work-key" required />
          </div>
          <div>
            <label for="modal-key" class="block text-sm font-medium text-gray-300 mb-1">API Key</label>
            <textarea id="modal-key" rows="3" class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white font-mono focus:outline-none focus:ring-2 focus:ring-green-500" placeholder="sk-..." required></textarea>
          </div>
          <div class="flex justify-end space-x-3">
            <button type="button" id="modal-cancel" class="bg-gray-700 hover:bg-gray-600 text-white font-medium px-4 py-2 rounded">Cancel</button>
            <button type="submit" id="modal-confirm" class="bg-green-600 hover:bg-green-700 text-white font-medium px-4 py-2 rounded">Add Key</button>
          </div>
        </form>
      </div>
    </div>

    <script src="/static/dashboard.js"></script>
  </body>
</html>`;
}
