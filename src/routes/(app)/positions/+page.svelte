<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import GlassCard from '$lib/components/GlassCard.svelte';
  
  let positions: any[] = [];
  let orders: any[] = [];
  let history: any[] = [];
  let loading = true;
  let error: string | null = null;
  
  let activeTab = 'positions';
  const tabs = [
    { id: 'positions', label: 'Open Positions' },
    { id: 'orders', label: 'Open Orders' },
    { id: 'history', label: 'Trade History' },
  ];
  
  onMount(() => {
    loadData();
  });
  
  async function loadData() {
    try {
      loading = true;
      error = null;
      
      // Load positions and history in parallel
      const [positionsResult, historyResult] = await Promise.all([
        api.getPaperPositions(),
        api.getPaperTradeHistory()
      ]);
      
      positions = positionsResult.positions || [];
      history = historyResult.trades || [];
      orders = []; // No orders API yet
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to load data';
      console.error('Positions load error:', err);
    } finally {
      loading = false;
    }
  }
  
  $: totalMargin = positions.reduce((sum: number, p: any) => sum + (p.margin || 0), 0);
  $: totalPnl = positions.reduce((sum: number, p: any) => sum + (p.unrealized_pnl || p.pnl || 0), 0);
</script>

<svelte:head>
  <title>Positions | Futures Brokiepedia</title>
</svelte:head>

<div class="space-y-5 max-w-7xl mx-auto pb-20 sm:pb-0">
  <!-- Header -->
  <div>
    <h1 class="text-2xl font-bold text-white/90 font-sans">Positions & Orders</h1>
    <p class="text-white/40 text-sm mt-1">Manage your open positions and orders</p>
  </div>
  
  {#if loading}
    <div class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
    </div>
  {:else if error}
    <GlassCard className="p-6">
      <p class="text-rose-400 font-sans text-center">{error}</p>
      <button class="mt-4 mx-auto block px-4 py-2 bg-white/[0.08] rounded-lg text-sm" on:click={loadData}>Retry</button>
    </GlassCard>
  {:else}
    <!-- Summary Cards -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
      <GlassCard className="p-4 sm:p-5">
        <p class="text-xs sm:text-sm text-white/40 font-sans">Open Positions</p>
        <p class="text-xl sm:text-2xl font-bold font-mono mt-1 text-white/90">{positions.length}</p>
      </GlassCard>
      <GlassCard className="p-4 sm:p-5">
        <p class="text-xs sm:text-sm text-white/40 font-sans">Total Margin</p>
        <p class="text-xl sm:text-2xl font-bold font-mono mt-1 text-white/90">${totalMargin.toFixed(2)}</p>
      </GlassCard>
      <GlassCard className="p-4 sm:p-5">
        <p class="text-xs sm:text-sm text-white/40 font-sans">Unrealized P&L</p>
        <p class="text-xl sm:text-2xl font-bold font-mono mt-1 {totalPnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}">{totalPnl >= 0 ? '+' : ''}${totalPnl.toFixed(2)}</p>
      </GlassCard>
      <GlassCard className="p-4 sm:p-5">
        <p class="text-xs sm:text-sm text-white/40 font-sans">Open Orders</p>
        <p class="text-xl sm:text-2xl font-bold font-mono mt-1 text-white/90">{orders.length}</p>
      </GlassCard>
    </div>
    
    <!-- Tabs -->
    <div class="flex gap-1 p-1 bg-white/[0.03] rounded-xl border border-white/[0.06]">
      {#each tabs as tab}
        <button
          class="flex-1 py-2.5 px-3 rounded-lg text-sm font-medium transition-all duration-200 {activeTab === tab.id ? 'bg-white/[0.08] text-white/90' : 'text-white/40 hover:text-white/70'}"
          on:click={() => activeTab = tab.id}
        >
          <span class="hidden sm:inline">{tab.label}</span>
          <span class="sm:hidden">{tab.id === 'positions' ? 'Positions' : tab.id === 'orders' ? 'Orders' : 'History'}</span>
        </button>
      {/each}
    </div>
    
    <!-- Table Container -->
    <GlassCard className="p-0 overflow-hidden">
      <div class="p-4 sm:p-6 overflow-x-auto scrollbar-hide">
        {#if activeTab === 'positions'}
          <table class="w-full min-w-[700px]">
            <thead>
              <tr class="border-b border-white/[0.06]">
                <th class="text-left py-3 text-xs text-white/40 font-sans uppercase tracking-wider">Symbol</th>
                <th class="text-left py-3 text-xs text-white/40 font-sans uppercase tracking-wider">Side</th>
                <th class="text-right py-3 text-xs text-white/40 font-sans uppercase tracking-wider">Size</th>
                <th class="text-right py-3 text-xs text-white/40 font-sans uppercase tracking-wider">Entry</th>
                <th class="text-right py-3 text-xs text-white/40 font-sans uppercase tracking-wider">Mark</th>
                <th class="text-right py-3 text-xs text-white/40 font-sans uppercase tracking-wider">Lev</th>
                <th class="text-right py-3 text-xs text-white/40 font-sans uppercase tracking-wider">P&L</th>
              </tr>
            </thead>
            <tbody>
              {#each positions as pos}
                <tr class="border-b border-white/[0.04] hover:bg-white/[0.02] transition-colors">
                  <td class="py-3">
                    <span class="text-sm font-medium text-white/90 font-sans">{pos.symbol}</span>
                  </td>
                  <td class="py-3">
                    <span class="inline-flex items-center px-2 py-0.5 rounded-lg text-xs font-mono font-semibold {pos.side === 'long' ? 'bg-emerald-500/15 text-emerald-400' : 'bg-rose-500/15 text-rose-400'}">
                      {pos.side.toUpperCase()}
                    </span>
                  </td>
                  <td class="py-3 text-right text-sm font-mono text-white/80">{pos.size}</td>
                  <td class="py-3 text-right text-sm font-mono text-white/80">${pos.entry_price.toLocaleString()}</td>
                  <td class="py-3 text-right text-sm font-mono text-white/80">${pos.mark_price?.toLocaleString() || '—'}</td>
                  <td class="py-3 text-right text-sm font-mono {pos.leverage > 5 ? 'text-rose-400' : 'text-white/80'}">{pos.leverage}x</td>
                  <td class="py-3 text-right text-sm font-mono {(pos.unrealized_pnl || pos.pnl || 0) >= 0 ? 'text-emerald-400' : 'text-rose-400'}">{(pos.unrealized_pnl || pos.pnl || 0) >= 0 ? '+' : ''}${(pos.unrealized_pnl || pos.pnl || 0).toFixed(2)}</td>
                </tr>
              {:else}
                <tr>
                  <td colspan="7" class="py-8 text-center text-sm text-white/30 font-sans">No open positions</td>
                </tr>
              {/each}
            </tbody>
          </table>
          
          {#if positions.some((p: any) => p.leverage > 5)}
            <div class="mt-4 p-3 bg-amber-500/10 border border-amber-500/20 rounded-xl flex items-start gap-2">
              <svg class="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
              <p class="text-sm text-amber-400 font-sans">Max allowed leverage: 5x per risk parameters</p>
            </div>
          {/if}
        
        {:else if activeTab === 'orders'}
          <table class="w-full min-w-[600px]">
            <thead>
              <tr class="border-b border-white/[0.06]">
                <th class="text-left py-3 text-xs text-white/40 font-sans uppercase tracking-wider">Symbol</th>
                <th class="text-left py-3 text-xs text-white/40 font-sans uppercase tracking-wider">Type</th>
                <th class="text-left py-3 text-xs text-white/40 font-sans uppercase tracking-wider">Side</th>
                <th class="text-right py-3 text-xs text-white/40 font-sans uppercase tracking-wider">Price</th>
                <th class="text-right py-3 text-xs text-white/40 font-sans uppercase tracking-wider">Size</th>
                <th class="text-left py-3 text-xs text-white/40 font-sans uppercase tracking-wider">Status</th>
              </tr>
            </thead>
            <tbody>
              {#each orders as order}
                <tr class="border-b border-white/[0.04] hover:bg-white/[0.02] transition-colors">
                  <td class="py-3 text-sm font-medium text-white/90">{order.symbol}</td>
                  <td class="py-3 text-sm text-white/70 font-mono">{order.type}</td>
                  <td class="py-3">
                    <span class="inline-flex items-center px-2 py-0.5 rounded-lg text-xs font-mono font-semibold {order.side === 'buy' ? 'bg-emerald-500/15 text-emerald-400' : 'bg-rose-500/15 text-rose-400'}">
                      {order.side.toUpperCase()}
                    </span>
                  </td>
                  <td class="py-3 text-right text-sm font-mono text-white/80">${order.price.toLocaleString()}</td>
                  <td class="py-3 text-right text-sm font-mono text-white/80">{order.size}</td>
                  <td class="py-3">
                    <span class="inline-flex items-center px-2 py-0.5 rounded-lg text-xs font-mono font-semibold bg-amber-500/15 text-amber-400">
                      {order.status.toUpperCase()}
                    </span>
                  </td>
                </tr>
              {:else}
                <tr>
                  <td colspan="6" class="py-8 text-center text-sm text-white/30 font-sans">No open orders</td>
                </tr>
              {/each}
            </tbody>
          </table>
        
        {:else}
          <table class="w-full min-w-[600px]">
            <thead>
              <tr class="border-b border-white/[0.06]">
                <th class="text-left py-3 text-xs text-white/40 font-sans uppercase tracking-wider">Symbol</th>
                <th class="text-left py-3 text-xs text-white/40 font-sans uppercase tracking-wider">Side</th>
                <th class="text-right py-3 text-xs text-white/40 font-sans uppercase tracking-wider">Entry</th>
                <th class="text-right py-3 text-xs text-white/40 font-sans uppercase tracking-wider">Exit</th>
                <th class="text-right py-3 text-xs text-white/40 font-sans uppercase tracking-wider">P&L</th>
                <th class="text-right py-3 text-xs text-white/40 font-sans uppercase tracking-wider">Return</th>
              </tr>
            </thead>
            <tbody>
              {#each history as trade}
                <tr class="border-b border-white/[0.04] hover:bg-white/[0.02] transition-colors">
                  <td class="py-3 text-sm font-medium text-white/90">{trade.symbol}</td>
                  <td class="py-3">
                    <span class="inline-flex items-center px-2 py-0.5 rounded-lg text-xs font-mono font-semibold {trade.side === 'long' ? 'bg-emerald-500/15 text-emerald-400' : 'bg-rose-500/15 text-rose-400'}">
                      {trade.side.toUpperCase()}
                    </span>
                  </td>
                  <td class="py-3 text-right text-sm font-mono text-white/80">${trade.entry_price.toLocaleString()}</td>
                  <td class="py-3 text-right text-sm font-mono text-white/80">${trade.exit_price.toLocaleString()}</td>
                  <td class="py-3 text-right text-sm font-mono {(trade.pnl || 0) >= 0 ? 'text-emerald-400' : 'text-rose-400'}">{(trade.pnl || 0) >= 0 ? '+' : ''}${(trade.pnl || 0).toFixed(2)}</td>
                  <td class="py-3 text-right text-sm font-mono {(trade.return_pct || 0) >= 0 ? 'text-emerald-400' : 'text-rose-400'}">{(trade.return_pct || 0) >= 0 ? '+' : ''}{(trade.return_pct || 0).toFixed(2)}%</td>
                </tr>
              {:else}
                <tr>
                  <td colspan="6" class="py-8 text-center text-sm text-white/30 font-sans">No trade history</td>
                </tr>
              {/each}
            </tbody>
          </table>
        {/if}
      </div>
    </GlassCard>
  {/if}
</div>

<style>
  .scrollbar-hide::-webkit-scrollbar {
    display: none;
  }
  .scrollbar-hide {
    -ms-overflow-style: none;
    scrollbar-width: none;
  }
</style>
