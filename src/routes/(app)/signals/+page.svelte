<script lang="ts">
  import { onMount } from 'svelte';
  import GlassCard from '$lib/components/GlassCard.svelte';
  import StatusBadge from '$lib/components/StatusBadge.svelte';
  import { api } from '$lib/api';
  
  let signals: any[] = [];
  let loading = true;
  let error: string | null = null;
  let activeTab: 'signals' | 'alerts' | 'departments' = 'signals';
  
  onMount(() => {
    loadSignals();
  });
  
  async function loadSignals() {
    try {
      loading = true;
      error = null;
      const result = await api.getSignals();
      signals = result.signals || [];
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to load signals';
      console.error('Signals load error:', err);
    } finally {
      loading = false;
    }
  }
  
  const tabs = [
    { id: 'signals' as const, label: 'Trading Signals' },
    { id: 'alerts' as const, label: 'Price Alerts' },
    { id: 'departments' as const, label: 'AI Departments' }
  ];
</script>

<div class="space-y-5 max-w-7xl mx-auto pb-20 sm:pb-0">
  <!-- Header -->
  <div class="flex items-center justify-between">
    <h1 class="text-2xl font-bold text-white/90 font-sans">Signals</h1>
    <StatusBadge status="online" label="LIVE" size="sm" />
  </div>

  <!-- Tabs -->
  <div class="flex gap-1 p-1 bg-white/[0.03] rounded-xl border border-white/[0.06]">
    {#each tabs as tab}
      <button
        class="flex-1 py-2.5 px-3 rounded-lg text-sm font-medium transition-all duration-200 {activeTab === tab.id ? 'bg-white/[0.08] text-white/90' : 'text-white/40 hover:text-white/70'}"
        on:click={() => activeTab = tab.id}
      >
        <span class="hidden sm:inline">{tab.label}</span>
        <span class="sm:hidden">{tab.id === 'signals' ? 'Signals' : tab.id === 'alerts' ? 'Alerts' : 'AI'}</span>
      </button>
    {/each}
  </div>

  {#if activeTab === 'signals'}
    {#if loading}
      <div class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    {:else if error}
      <GlassCard className="p-6">
        <p class="text-rose-400 font-sans text-center">{error}</p>
        <button class="mt-4 mx-auto block px-4 py-2 bg-white/[0.08] rounded-lg text-sm" on:click={loadSignals}>Retry</button>
      </GlassCard>
    {:else}
      <!-- Signal Cards -->
      <div class="space-y-4">
        {#each signals as signal}
          <GlassCard className="p-4 sm:p-5">
            <!-- Card Header -->
            <div class="flex items-start justify-between mb-4">
              <div class="flex items-center gap-3">
                <img src={signal.icon} alt={signal.symbol} class="w-10 h-10 rounded-full" />
                <div>
                  <h3 class="text-lg font-bold text-white/90 font-sans">{signal.symbol}</h3>
                  <p class="text-sm text-white/40 font-sans">{signal.strategy} · {signal.timeframe}</p>
                </div>
              </div>
              <div class="flex gap-2">
                <span class="inline-flex items-center px-3 py-1 rounded-lg text-xs font-mono font-semibold {signal.direction === 'long' ? 'bg-emerald-500/15 text-emerald-400' : signal.direction === 'short' ? 'bg-rose-500/15 text-rose-400' : 'bg-white/5 text-white/40'}">
                  {signal.direction.toUpperCase()}
                </span>
                <span class="inline-flex items-center px-3 py-1 rounded-lg text-xs font-mono font-semibold {signal.status === 'active' ? 'bg-emerald-500/15 text-emerald-400' : signal.status === 'pending' ? 'bg-amber-500/15 text-amber-400' : 'bg-white/5 text-white/40'}">
                  {signal.status.toUpperCase()}
                </span>
              </div>
            </div>

            <!-- Price Grid -->
            <div class="grid grid-cols-3 gap-4 mb-4">
              <div>
                <p class="text-xs text-white/40 mb-1 font-sans">Entry</p>
                <p class="text-lg font-mono font-bold text-white/90">${signal.entry.toLocaleString('en-US', { minimumFractionDigits: signal.entry < 1000 ? 2 : 0, maximumFractionDigits: signal.entry < 1000 ? 2 : 0 })}</p>
              </div>
              <div>
                <p class="text-xs text-white/40 mb-1 font-sans">TP</p>
                <p class="text-lg font-mono font-bold text-emerald-400">${signal.tp.toLocaleString()}</p>
              </div>
              <div>
                <p class="text-xs text-white/40 mb-1 font-sans">SL</p>
                <p class="text-lg font-mono font-bold text-rose-400">${signal.sl.toLocaleString()}</p>
              </div>
            </div>

            <!-- Confidence & R:R Row -->
            <div class="flex items-center gap-4">
              <div class="flex-1">
                <div class="flex items-center justify-between mb-1.5">
                  <span class="text-xs text-white/40 font-sans">Confidence</span>
                  <span class="text-sm font-mono font-semibold text-white/80">{signal.confidence}%</span>
                </div>
                <div class="h-2 bg-white/[0.06] rounded-full overflow-hidden">
                  <div 
                    class="h-full rounded-full bg-gradient-to-r from-blue-500 to-cyan-400 transition-all duration-500"
                    style="width: {signal.confidence}%"
                  ></div>
                </div>
              </div>
              <div class="text-right flex-shrink-0">
                <p class="text-xs text-white/40 font-sans">R:R</p>
                <p class="text-lg font-mono font-bold text-white/90">{signal.rr}</p>
              </div>
            </div>
          </GlassCard>
        {:else}
          <GlassCard className="p-6">
            <p class="text-white/30 font-sans text-center py-8">No active signals. Check back when market conditions trigger new opportunities.</p>
          </GlassCard>
        {/each}
      </div>
    {/if}
  {:else if activeTab === 'alerts'}
    <GlassCard className="p-6">
      <p class="text-white/40 font-sans text-center py-8">Price alerts coming soon</p>
    </GlassCard>
  {:else}
    <GlassCard className="p-6">
      <p class="text-white/40 font-sans text-center py-8">AI departments view coming soon</p>
    </GlassCard>
  {/if}
</div>

<style>
</style>
