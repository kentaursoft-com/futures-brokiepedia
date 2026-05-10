<script lang="ts">
  import { onMount } from 'svelte';
  import GlassCard from '$lib/components/GlassCard.svelte';
  import StatusBadge from '$lib/components/StatusBadge.svelte';
  import {
    getDepartmentKeys,
    generateDepartmentKey,
    revokeDepartmentKey,
    getPendingSignals,
    DEPARTMENT_LABELS,
    type DepartmentKey,
    type KeyGenerationResult,
  } from '$lib/departments';

  let keys: DepartmentKey[] = [];
  let loading = true;
  let error = '';
  let showGenerateModal = false;
  let generateDepartment = 'quantitative';
  let generateLabel = '';
  let generating = false;
  let generatedKey: KeyGenerationResult | null = null;
  let keyCopied = false;
  let signals: Record<string, any[]> = {};
  let showRevokeConfirm = '';
  let revoking = false;
  let successMsg = '';

  const departments = [
    'quantitative', 'technical', 'sentiment',
    'fundamental', 'statistical', 'qualitative'
  ];

  onMount(async () => {
    await loadKeys();
    await loadSignals();
  });

  async function loadKeys() {
    try {
      loading = true;
      keys = await getDepartmentKeys();
    } catch (e: any) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  async function loadSignals() {
    try {
      signals = await getPendingSignals();
    } catch {}
  }

  function openGenerate() {
    generatedKey = null;
    keyCopied = false;
    showGenerateModal = true;
  }

  async function handleGenerate() {
    try {
      generating = true;
      error = '';
      generatedKey = await generateDepartmentKey(generateDepartment, generateLabel || undefined);
      await loadKeys();
      await loadSignals();
    } catch (e: any) {
      error = e.message;
    } finally {
      generating = false;
    }
  }

  async function copyKey() {
    if (generatedKey?.key) {
      await navigator.clipboard.writeText(generatedKey.key);
      keyCopied = true;
    }
  }

  async function handleRevoke(keyId: string) {
    try {
      revoking = true;
      await revokeDepartmentKey(keyId);
      keys = keys.filter(k => k.id !== keyId);
      showRevokeConfirm = '';
      successMsg = 'API key revoked successfully';
      setTimeout(() => successMsg = '', 3000);
    } catch (e: any) {
      error = e.message;
    } finally {
      revoking = false;
    }
  }

  function getDepartmentColor(dept: string): string {
    const colors: Record<string, string> = {
      quantitative: 'from-blue-500/20 to-blue-600/10',
      technical: 'from-cyan-500/20 to-cyan-600/10',
      sentiment: 'from-pink-500/20 to-pink-600/10',
      fundamental: 'from-purple-500/20 to-purple-600/10',
      statistical: 'from-emerald-500/20 to-emerald-600/10',
      qualitative: 'from-amber-500/20 to-amber-600/10',
    };
    return colors[dept] || 'from-zinc-500/20 to-zinc-600/10';
  }

  function formatDate(ts: number): string {
    return new Date(ts).toLocaleDateString('en-US', {
      month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
    });
  }

  function timeAgo(ts: number | null): string {
    if (!ts) return 'Never used';
    const diff = Date.now() - ts;
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return 'Just now';
    if (mins < 60) return `${mins}m ago`;
    const hours = Math.floor(mins / 60);
    if (hours < 24) return `${hours}h ago`;
    return `${Math.floor(hours / 24)}d ago`;
  }
</script>

<svelte:head>
  <title>Department API Keys — Futures Brokiepedia</title>
</svelte:head>

<div class="p-6 space-y-6">
  <!-- Header -->
  <div class="flex items-center justify-between">
    <div>
      <h1 class="text-2xl font-bold text-white">Department API Keys</h1>
      <p class="text-zinc-400 text-sm mt-1">
        Manage API keys for Discord agents to submit trading signals
      </p>
    </div>
    <button
      class="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-medium transition-colors flex items-center gap-2"
      onclick={openGenerate}
    >
      <span>＋</span>
      Generate New Key
    </button>
  </div>

  <!-- Success/Error messages -->
  {#if successMsg}
    <div class="px-4 py-3 bg-emerald-900/50 border border-emerald-700/50 rounded-lg text-emerald-300 text-sm">
      {successMsg}
    </div>
  {/if}
  {#if error}
    <div class="px-4 py-3 bg-red-900/50 border border-red-700/50 rounded-lg text-red-300 text-sm">
      {error}
    </div>
  {/if}

  <!-- Stats overview -->
  <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
    <GlassCard>
      <div class="text-zinc-400 text-xs font-medium uppercase tracking-wider">Total Keys</div>
      <div class="text-2xl font-bold text-white mt-1">{keys.length}</div>
    </GlassCard>
    <GlassCard>
      <div class="text-zinc-400 text-xs font-medium uppercase tracking-wider">Active</div>
      <div class="text-2xl font-bold text-emerald-400 mt-1">{keys.filter(k => k.is_active).length}</div>
    </GlassCard>
    <GlassCard>
      <div class="text-zinc-400 text-xs font-medium uppercase tracking-wider">Departments</div>
      <div class="text-2xl font-bold text-white mt-1">
        {new Set(keys.filter(k => k.is_active).map(k => k.department)).size}
      </div>
    </GlassCard>
    <GlassCard>
      <div class="text-zinc-400 text-xs font-medium uppercase tracking-wider">Pending Signals</div>
      <div class="text-2xl font-bold text-amber-400 mt-1">
        {Object.values(signals).reduce((a: number, b: any[]) => a + b.length, 0)}
      </div>
    </GlassCard>
  </div>

  <!-- Department Overview -->
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    {#each departments as dept}
      {@const deptKeys = keys.filter(k => k.department === dept)}
      {@const activeKeys = deptKeys.filter(k => k.is_active)}
      {@const deptSignals = signals[dept] || []}
      <GlassCard>
        <div class="flex items-center justify-between mb-3">
          <span class="text-white font-semibold text-sm">{DEPARTMENT_LABELS[dept] || dept}</span>
          <div class="flex gap-2">
            <StatusBadge status={activeKeys.length > 0 ? 'active' : 'inactive'}>
              {activeKeys.length} key{activeKeys.length !== 1 ? 's' : ''}
            </StatusBadge>
            {#if deptSignals.length > 0}
              <span class="bg-amber-500/20 text-amber-400 text-xs px-2 py-0.5 rounded-full">
                {deptSignals.length} pending
              </span>
            {/if}
          </div>
        </div>

        {#if deptSignals.length > 0}
          <div class="space-y-1 mb-3">
            {#each deptSignals.slice(0, 2) as sig}
              <div class="flex items-center gap-2 text-xs">
                <span class="font-mono {sig.direction === 'long' ? 'text-emerald-400' : sig.direction === 'short' ? 'text-red-400' : 'text-zinc-400'}">
                  {sig.direction.toUpperCase()}
                </span>
                <span class="text-zinc-400">{sig.symbol}</span>
                <span class="text-zinc-500">{(sig.confidence * 100).toFixed(0)}%</span>
                <span class="text-zinc-600 ml-auto">{timeAgo(sig.timestamp)}</span>
              </div>
            {/each}
          </div>
        {/if}

        <button
          class="text-xs text-emerald-400 hover:text-emerald-300 transition-colors"
          onclick={() => { generateDepartment = dept; openGenerate(); }}
        >
          ＋ Add key for {dept}
        </button>
      </GlassCard>
    {/each}
  </div>

  <!-- Keys Table -->
  <GlassCard>
    <div class="p-4">
      <h2 class="text-lg font-semibold text-white mb-4">All API Keys</h2>

      {#if loading}
        <div class="text-center py-8 text-zinc-500">Loading keys...</div>
      {:else if keys.length === 0}
        <div class="text-center py-8 text-zinc-500">
          No API keys generated yet. Click "Generate New Key" above to create one.
        </div>
      {:else}
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="text-zinc-400 text-xs uppercase tracking-wider border-b border-zinc-800">
                <th class="text-left py-3 px-2">Department</th>
                <th class="text-left py-3 px-2">Label</th>
                <th class="text-left py-3 px-2">Key Prefix</th>
                <th class="text-left py-3 px-2">Status</th>
                <th class="text-left py-3 px-2">Last Used</th>
                <th class="text-left py-3 px-2">Created</th>
                <th class="text-right py-3 px-2">Actions</th>
              </tr>
            </thead>
            <tbody>
              {#each keys as keyItem}
                <tr class="border-b border-zinc-800/50 hover:bg-zinc-800/30 transition-colors">
                  <td class="py-3 px-2">
                    <span class="text-white font-medium">
                      {DEPARTMENT_LABELS[keyItem.department] || keyItem.department}
                    </span>
                  </td>
                  <td class="py-3 px-2 text-zinc-300">{keyItem.label}</td>
                  <td class="py-3 px-2">
                    <code class="text-amber-300 bg-zinc-800 px-2 py-0.5 rounded text-xs">
                      {keyItem.prefix}
                    </code>
                  </td>
                  <td class="py-3 px-2">
                    {#if keyItem.is_active}
                      <span class="text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full text-xs">Active</span>
                    {:else}
                      <span class="text-red-400 bg-red-500/10 px-2 py-0.5 rounded-full text-xs">Revoked</span>
                    {/if}
                  </td>
                  <td class="py-3 px-2 text-zinc-400 text-xs">{timeAgo(keyItem.last_used_at)}</td>
                  <td class="py-3 px-2 text-zinc-400 text-xs">{formatDate(keyItem.created_at)}</td>
                  <td class="py-3 px-2 text-right">
                    {#if keyItem.is_active}
                      {#if showRevokeConfirm === keyItem.id}
                        <div class="flex items-center justify-end gap-2">
                          <button
                            class="text-xs text-zinc-400 hover:text-white transition-colors"
                            onclick={() => showRevokeConfirm = ''}
                          >
                            Cancel
                          </button>
                          <button
                            class="text-xs text-red-400 hover:text-red-300 bg-red-500/10 px-2 py-1 rounded transition-colors"
                            onclick={() => handleRevoke(keyItem.id)}
                            disabled={revoking}
                          >
                            {revoking ? 'Revoking...' : 'Confirm Revoke'}
                          </button>
                        </div>
                      {:else}
                        <button
                          class="text-xs text-red-400 hover:text-red-300 transition-colors"
                          onclick={() => showRevokeConfirm = keyItem.id}
                        >
                          Revoke
                        </button>
                      {/if}
                    {/if}
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      {/if}
    </div>
  </GlassCard>
</div>

<!-- Generate Key Modal -->
{#if showGenerateModal}
  <div class="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
    <div class="bg-zinc-900 border border-zinc-800 rounded-xl max-w-md w-full p-6 shadow-2xl">
      {#if generatedKey}
        <!-- Key generated - show once -->
        <div class="text-center space-y-4">
          <div class="text-emerald-400 text-4xl">🔑</div>
          <h3 class="text-xl font-bold text-white">API Key Generated</h3>
          <p class="text-zinc-400 text-sm">
            Store this key securely. It <span class="text-red-400">will not be shown again</span>.
          </p>
          <div class="bg-zinc-950 border border-zinc-700 rounded-lg p-3 mt-2">
            <code class="text-emerald-300 text-xs break-all select-all font-mono">
              {generatedKey.key}
            </code>
          </div>
          <div class="flex gap-3 justify-center">
            <button
              class="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-sm font-medium transition-colors"
              onclick={copyKey}
            >
              {keyCopied ? '✓ Copied!' : 'Copy Key'}
            </button>
            <button
              class="px-4 py-2 bg-zinc-700 hover:bg-zinc-600 text-white rounded-lg text-sm transition-colors"
              onclick={() => { showGenerateModal = false; }}
            >
              Done
            </button>
          </div>
          {#if keyCopied}
            <p class="text-emerald-400 text-xs">Key copied to clipboard!</p>
          {/if}
        </div>
      {:else}
        <!-- Generate form -->
        <h3 class="text-lg font-bold text-white mb-4">Generate New API Key</h3>

        <div class="space-y-4">
          <div>
            <label class="text-zinc-400 text-xs font-medium uppercase tracking-wider block mb-1.5">
              Department
            </label>
            <select
              class="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-emerald-500"
              bind:value={generateDepartment}
            >
              {#each departments as dept}
                <option value={dept}>{DEPARTMENT_LABELS[dept] || dept}</option>
              {/each}
            </select>
          </div>
          <div>
            <label class="text-zinc-400 text-xs font-medium uppercase tracking-wider block mb-1.5">
              Label (optional)
            </label>
            <input
              type="text"
              class="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-emerald-500"
              placeholder="e.g. Prometheus Discord Agent"
              bind:value={generateLabel}
            />
          </div>

          {#if error}
            <p class="text-red-400 text-sm">{error}</p>
          {/if}

          <div class="flex gap-3 justify-end pt-2">
            <button
              class="px-4 py-2 bg-zinc-700 hover:bg-zinc-600 text-white rounded-lg text-sm transition-colors"
              onclick={() => showGenerateModal = false}
            >
              Cancel
            </button>
            <button
              class="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
              onclick={handleGenerate}
              disabled={generating}
            >
              {generating ? 'Generating...' : 'Generate Key'}
            </button>
          </div>
        </div>
      {/if}
    </div>
  </div>
{/if}
