<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { liveState } from '$lib/api';
  import OrderBook from '$lib/components/OrderBook.svelte';
  import OrderForm from '$lib/components/OrderForm.svelte';
  import GlassCard from '$lib/components/GlassCard.svelte';
  import { binanceWS } from '$lib/websocket';

  const MARKETS = [
    { symbol: 'BTCUSDT', label: 'BTC', icon: 'https://assets.coingecko.com/coins/images/1/small/bitcoin.png' },
    { symbol: 'ETHUSDT', label: 'ETH', icon: 'https://assets.coingecko.com/coins/images/279/small/ethereum.png' },
    { symbol: 'SOLUSDT', label: 'SOL', icon: 'https://assets.coingecko.com/coins/images/4128/small/solana.png' },
    { symbol: 'BNBUSDT', label: 'BNB', icon: 'https://assets.coingecko.com/coins/images/825/small/bnb-icon2_2x.png' },
    { symbol: 'XRPUSDT', label: 'XRP', icon: 'https://assets.coingecko.com/coins/images/44/small/xrp-symbol-white-128.png' },
  ];

  let wsConnected = false;
  let activeTimeframe = '1h';
  let selectedSymbol = 'BTCUSDT';
  let orderSide: 'long' | 'short' = 'long';

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

  $: state = $liveState;
  $: positions = state?.positions || [];

  $: selectedMarket = MARKETS.find(m => m.symbol === selectedSymbol) || MARKETS[0];
  $: tvInterval = activeTimeframe === '1m' ? '1' : activeTimeframe === '5m' ? '5' : activeTimeframe === '15m' ? '15' : activeTimeframe === '1h' ? '60' : activeTimeframe === '4h' ? '240' : 'D';
  $: tvSymbol = `BINANCE:${selectedSymbol}`;
  $: livePrice = $binanceWS.lastPrice;
  $: change24h = ($binanceWS.ticker?.change24hPct ?? 0);
  $: pnlColor = change24h >= 0 ? 'text-emerald-400' : 'text-rose-400';
  $: pnlSign = change24h >= 0 ? '+' : '';

  function posColor(dir: string) {
    return dir === 'long' ? 'text-emerald-400' : 'text-rose-400';
  }
  function posBg(dir: string) {
    return dir === 'long' ? 'bg-emerald-500/10 border-emerald-500/20' : 'bg-rose-500/10 border-rose-500/20';
  }
</script>

<svelte:head>
  <title>Trade {selectedSymbol} | Futures Brokiepedia</title>
</svelte:head>

<div class="space-y-4 max-w-7xl mx-auto pb-20 sm:pb-0">
  <!-- Top Bar -->
  <GlassCard className="p-4 sm:p-5">
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
      <!-- Left: Market selector + price -->
      <div class="flex items-center gap-4 w-full sm:w-auto">
        <img src={selectedMarket.icon} alt={selectedMarket.label} class="w-8 h-8 rounded-full flex-shrink-0" />
        <div class="flex-1 sm:flex-none">
          <!-- Market selector dropdown -->
          <div class="flex items-center gap-2 mb-0.5">
            <select
              class="bg-zinc-800 border border-zinc-700 rounded-lg px-2 py-1 text-white text-sm font-mono focus:outline-none focus:border-emerald-500"
              bind:value={selectedSymbol}
            >
              {#each MARKETS as m}
                <option value={m.symbol}>{m.label}-PERP</option>
              {/each}
            </select>
            <!-- Long/Short toggle -->
            <div class="flex rounded-lg overflow-hidden border border-zinc-700">
              <button
                class="px-3 py-1 text-xs font-semibold font-mono transition-colors {orderSide === 'long' ? 'bg-emerald-600 text-white' : 'bg-zinc-800 text-zinc-500 hover:text-zinc-300'}"
                on:click={() => orderSide = 'long'}
              >LONG</button>
              <button
                class="px-3 py-1 text-xs font-semibold font-mono transition-colors {orderSide === 'short' ? 'bg-rose-600 text-white' : 'bg-zinc-800 text-zinc-500 hover:text-zinc-300'}"
                on:click={() => orderSide = 'short'}
              >SHORT</button>
            </div>
          </div>
          <div class="flex items-center gap-3">
            <span class="text-xl sm:text-2xl font-bold font-mono text-white/90">
              ${livePrice?.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) || '—'}
            </span>
            <span class="text-sm font-mono {pnlColor}">
              {pnlSign}{change24h.toFixed(2)}%
            </span>
          </div>
        </div>
      </div>

      <!-- Right: Timeframes + WS status -->
      <div class="flex items-center gap-3 w-full sm:w-auto">
        <div class="flex gap-1 overflow-x-auto flex-1 sm:flex-none">
          {#each timeframes as tf}
            <button
              class="px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium transition-all whitespace-nowrap {activeTimeframe === tf ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'text-zinc-500 hover:text-zinc-300 hover:bg-zinc-800/50'}"
              on:click={() => activeTimeframe = tf}
            >{tf}</button>
          {/each}
        </div>
        <div class="flex items-center gap-2 flex-shrink-0">
          <div class="w-2 h-2 rounded-full {wsConnected ? 'bg-emerald-400' : 'bg-rose-400'}"></div>
          <span class="text-xs text-zinc-500 font-mono">{wsConnected ? 'Live' : 'Off'}</span>
        </div>
      </div>
    </div>
  </GlassCard>

  <!-- Main Grid -->
  <div class="grid grid-cols-1 lg:grid-cols-4 gap-4">
    <!-- Chart + Positions -->
    <div class="lg:col-span-3 space-y-4">
      <!-- Chart -->
      <GlassCard className="p-0 overflow-hidden">
        <div class="w-full" style="height: 400px; min-height: 350px;">
          <iframe
            src="https://www.tradingview.com/widgetembed/?frameElementId=tradingview_chart&symbol={tvSymbol}&interval={tvInterval}&hidesidetoolbar=1&symboledit=0&saveimage=0&toolbarbg=0F172A&studies=%5B%5D&theme=dark&style=1&timezone=Etc%2FUTC&locale=en"
            class="w-full h-full border-0"
            title="TradingView Chart"
            loading="lazy"
          ></iframe>
        </div>
      </GlassCard>

      <!-- Open Positions Panel -->
      <GlassCard title="Open Positions" subtitle="{positions.length} position{positions.length !== 1 ? 's' : ''} across all exchanges">
        {#if positions.length > 0}
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead>
                <tr class="text-xs text-zinc-500 uppercase tracking-wider border-b border-zinc-800">
                  <th class="text-left py-2 pr-3 font-sans">Symbol</th>
                  <th class="text-left py-2 px-3 font-sans">Side</th>
                  <th class="text-right py-2 px-3 font-sans">Size</th>
                  <th class="text-right py-2 px-3 font-sans">Entry</th>
                  <th class="text-right py-2 px-3 font-sans">Mark</th>
                  <th class="text-right py-2 px-3 font-sans">P&L</th>
                  <th class="text-left py-2 pl-3 font-sans">Exchange</th>
                </tr>
              </thead>
              <tbody>
                {#each positions as pos}
                  <tr class="border-b border-zinc-800/30 hover:bg-zinc-800/10 transition-colors">
                    <td class="py-2.5 pr-3 font-mono text-zinc-200">{pos.symbol}</td>
                    <td class="py-2.5 px-3">
                      <span class="text-xs font-mono font-semibold {posColor(pos.side)}">{pos.side?.toUpperCase()}</span>
                    </td>
                    <td class="py-2.5 px-3 text-right font-mono text-zinc-300">{pos.size}</td>
                    <td class="py-2.5 px-3 text-right font-mono text-zinc-400">${pos.entry_price?.toFixed(2) || '—'}</td>
                    <td class="py-2.5 px-3 text-right font-mono text-zinc-400">${pos.mark_price?.toFixed(2) || '—'}</td>
                    <td class="py-2.5 px-3 text-right font-mono font-semibold {pos.unrealized_pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}">
                      {pos.unrealized_pnl >= 0 ? '+' : ''}{pos.unrealized_pnl?.toFixed(2) || '0.00'}
                    </td>
                    <td class="py-2.5 pl-3 text-xs text-zinc-500 font-sans">{pos.exchange || 'Binance'}</td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        {:else}
          <div class="py-8 text-center">
            <p class="text-zinc-500 text-sm font-sans">No open positions</p>
            <p class="text-zinc-600 text-xs font-sans mt-1">Place a trade above to see it here</p>
          </div>
        {/if}
      </GlassCard>
    </div>

    <!-- Right Panel -->
    <div class="space-y-4">
      <!-- Order Form -->
      <GlassCard title="Place Order" subtitle={selectedSymbol}>
        <OrderForm symbol={selectedSymbol} side={orderSide} />
      </GlassCard>

      <!-- Order Book -->
      <GlassCard title="Order Book" className="p-0 overflow-hidden">
        <div class="p-4 max-h-80 overflow-y-auto">
          <OrderBook />
        </div>
      </GlassCard>
    </div>
  </div>
</div>

<style>
</style>
