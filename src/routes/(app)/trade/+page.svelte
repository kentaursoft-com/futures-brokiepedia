<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import OrderBook from '$lib/components/OrderBook.svelte';
  import OrderForm from '$lib/components/OrderForm.svelte';
  import GlassCard from '$lib/components/GlassCard.svelte';
  import { binanceWS } from '$lib/websocket';
  
  let wsConnected = false;
  let activeTimeframe = '1m';
  
  const unsubscribe = binanceWS.subscribe(state => {
    wsConnected = state.connected;
  });
  
  const timeframes = ['1m', '5m', '15m', '1h', '4h', '1d'];
  
  onMount(() => {
    binanceWS.connect();
  });
  
  onDestroy(() => {
    unsubscribe();
    binanceWS.disconnect();
  });
  
  $: tvInterval = activeTimeframe === '1m' ? '1' : activeTimeframe === '5m' ? '5' : activeTimeframe === '15m' ? '15' : activeTimeframe === '1h' ? '60' : activeTimeframe === '4h' ? '240' : 'D';
</script>

<svelte:head>
  <title>Trade | Futures Brokiepedia</title>
</svelte:head>

<div class="space-y-4 max-w-7xl mx-auto pb-20 sm:pb-0">
  <!-- Top Bar -->
  <GlassCard className="p-4 sm:p-5">
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
      <div class="flex items-center gap-4">
        <img src="https://assets.coingecko.com/coins/images/1/small/bitcoin.png" alt="BTC" class="w-8 h-8 rounded-full" />
        <div>
          <p class="text-sm text-white/40 font-sans">BTC-PERP</p>
          <div class="flex items-center gap-2">
            <span class="text-xl sm:text-2xl font-bold font-mono text-white/90">${$binanceWS.lastPrice?.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) || '—'}</span>
            <span class="text-sm font-mono {($binanceWS.ticker?.change24hPct ?? -1) >= 0 ? 'text-emerald-400' : 'text-rose-400'}">
              {($binanceWS.ticker?.change24hPct ?? -1) >= 0 ? '+' : ''}{$binanceWS.ticker?.change24hPct?.toFixed(2) || '—'}%
            </span>
          </div>
        </div>
      </div>
      
      <div class="flex items-center gap-3 w-full sm:w-auto">
        <!-- Timeframe buttons - scrollable on mobile -->
        <div class="flex gap-1 overflow-x-auto scrollbar-hide flex-1 sm:flex-none">
          {#each timeframes as tf}
            <button 
              class="px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium transition-all whitespace-nowrap {activeTimeframe === tf ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30' : 'text-white/40 hover:text-white/70 hover:bg-white/[0.04]'}"
              on:click={() => activeTimeframe = tf}
            >
              {tf}
            </button>
          {/each}
        </div>
        
        <div class="flex items-center gap-2 flex-shrink-0">
          <div class="w-2 h-2 rounded-full {wsConnected ? 'bg-emerald-400 shadow-[0_0_8px_rgba(16,185,129,0.6)]' : 'bg-rose-400 shadow-[0_0_8px_rgba(244,63,94,0.6)]'}"></div>
          <span class="text-xs text-white/40 font-mono">{wsConnected ? 'Live' : 'Off'}</span>
        </div>
      </div>
    </div>
  </GlassCard>
  
  <!-- Main Trading Area -->
  <div class="grid grid-cols-1 lg:grid-cols-4 gap-4">
    <!-- Chart Area -->
    <div class="lg:col-span-3">
      <GlassCard className="p-0 overflow-hidden" title="Chart">
        <div class="w-full" style="height: 400px; min-height: 350px;">
          <iframe 
            src="https://www.tradingview.com/widgetembed/?frameElementId=tradingview_chart&symbol=BINANCE:BTCUSDT&interval={tvInterval}&hidesidetoolbar=1&symboledit=0&saveimage=0&toolbarbg=0F172A&studies=%5B%5D&theme=dark&style=1&timezone=Etc%2FUTC&locale=en"
            class="w-full h-full border-0"
            title="TradingView Chart"
            loading="lazy"
          ></iframe>
        </div>
      </GlassCard>
    </div>
    
    <!-- Right Panel -->
    <div class="space-y-4">
      <!-- Order Form -->
      <GlassCard title="Place Order" className="p-4 sm:p-5">
        <OrderForm />
      </GlassCard>
      
      <!-- Order Book -->
      <GlassCard title="Order Book" className="p-0 overflow-hidden">
        <div class="p-4 max-h-80 overflow-y-auto scrollbar-hide">
          <OrderBook />
        </div>
      </GlassCard>
    </div>
  </div>
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
