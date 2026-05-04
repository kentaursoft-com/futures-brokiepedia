<script lang="ts">
  import { liveState } from '$lib/api';
  import GlassCard from '$lib/components/GlassCard.svelte';
  
  $: positions = $liveState?.positions || [];
  
  const mockPositions = [
    { id: '1', symbol: 'BTC-PERP', side: 'long', size: 0.15, entry_price: 78250.00, mark_price: 78623.25, unrealized_pnl: 55.99, leverage: 10, margin: 1173.75, exchange: 'Binance' },
    { id: '2', symbol: 'ETH-PERP', side: 'short', size: 2.5, entry_price: 4250.00, mark_price: 4215.00, unrealized_pnl: 87.50, leverage: 5, margin: 2125.00, exchange: 'Binance' },
  ];
  
  const mockOrders = [
    { id: '1', symbol: 'BTC-PERP', type: 'limit', side: 'buy', price: 78000.00, size: 0.1, status: 'open', time: '2024-01-15 14:30:00' },
    { id: '2', symbol: 'ETH-PERP', type: 'stop_market', side: 'sell', price: 4100.00, size: 1.0, status: 'open', time: '2024-01-15 14:25:00' },
  ];
  
  const mockHistory = [
    { id: '1', symbol: 'BTC-PERP', side: 'long', size: 0.1, entry: 77500.00, exit: 78200.00, pnl: 70.00, pnl_pct: 0.9, time: '2024-01-15 12:00:00' },
    { id: '2', symbol: 'SOL-PERP', side: 'short', size: 50, entry: 200.00, exit: 198.50, pnl: 75.00, pnl_pct: 0.75, time: '2024-01-15 10:30:00' },
  ];
  
  let activeTab = 'positions';
  const tabs = [
    { id: 'positions', label: 'Open Positions' },
    { id: 'orders', label: 'Open Orders' },
    { id: 'history', label: 'Trade History' },
  ];
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
  
  <!-- Summary Cards -->
  <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
    <GlassCard className="p-4 sm:p-5">
      <p class="text-xs sm:text-sm text-white/40 font-sans">Open Positions</p>
      <p class="text-xl sm:text-2xl font-bold font-mono mt-1 text-white/90">{mockPositions.length}</p>
    </GlassCard>
    <GlassCard className="p-4 sm:p-5">
      <p class="text-xs sm:text-sm text-white/40 font-sans">Total Margin</p>
      <p class="text-xl sm:text-2xl font-bold font-mono mt-1 text-white/90">$3,298.75</p>
    </GlassCard>
    <GlassCard className="p-4 sm:p-5">
      <p class="text-xs sm:text-sm text-white/40 font-sans">Unrealized P&L</p>
      <p class="text-xl sm:text-2xl font-bold font-mono mt-1 text-emerald-400">+$143.49</p>
    </GlassCard>
    <GlassCard className="p-4 sm:p-5">
      <p class="text-xs sm:text-sm text-white/40 font-sans">Open Orders</p>
      <p class="text-xl sm:text-2xl font-bold font-mono mt-1 text-white/90">{mockOrders.length}</p>
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
            {#each mockPositions as pos}
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
                <td class="py-3 text-right text-sm font-mono text-white/80">${pos.mark_price.toLocaleString()}</td>
                <td class="py-3 text-right text-sm font-mono {pos.leverage > 5 ? 'text-rose-400' : 'text-white/80'}">{pos.leverage}x</td>
                <td class="py-3 text-right text-sm font-mono {pos.unrealized_pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}">{pos.unrealized_pnl >= 0 ? '+' : ''}${pos.unrealized_pnl.toFixed(2)}</td>
              </tr>
            {:else}
              <tr>
                <td colspan="7" class="py-8 text-center text-sm text-white/30 font-sans">No open positions</td>
              </tr>
            {/each}
          </tbody>
        </table>
        
        {#if mockPositions.some(p => p.leverage > 5)}
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
            {#each mockOrders as order}
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
              <th class="text-left py-3 text-xs text-white/40 font-sans uppercase tracking-wider">Time</th>
            </tr>
          </thead>
          <tbody>
            {#each mockHistory as trade}
              <tr class="border-b border-white/[0.04] hover:bg-white/[0.02] transition-colors">
                <td class="py-3 text-sm font-medium text-white/90">{trade.symbol}</td>
                <td class="py-3">
                  <span class="inline-flex items-center px-2 py-0.5 rounded-lg text-xs font-mono font-semibold {trade.side === 'long' ? 'bg-emerald-500/15 text-emerald-400' : 'bg-rose-500/15 text-rose-400'}">
                    {trade.side.toUpperCase()}
                  </span>
                </td>
                <td class="py-3 text-right text-sm font-mono text-white/80">${trade.entry.toLocaleString()}</td>
                <td class="py-3 text-right text-sm font-mono text-white/80">${trade.exit.toLocaleString()}</td>
                <td class="py-3 text-right text-sm font-mono {trade.pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}">{trade.pnl >= 0 ? '+' : ''}${trade.pnl.toFixed(2)}</td>
                <td class="py-3 text-sm font-mono text-white/50">{trade.time}</td>
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
