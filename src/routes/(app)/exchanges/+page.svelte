<script lang="ts">
  import { onMount } from 'svelte';
  import { onDestroy } from 'svelte';
  import GlassCard from '$lib/components/GlassCard.svelte';
  import StatusBadge from '$lib/components/StatusBadge.svelte';
  import { liveState } from '$lib/api';
  import { currency, formatCryptoFiat } from '$lib/stores/currency';

  interface ExchangeBalance {
    exchange: string;
    name: string;
    status: string;
    wallet_balance: number;
    used_margin: number;
    total_balance: number;
    unrealized_pnl: number;
    realized_pnl_today: number;
    currency: string;
    available?: number;
    positions_count?: number;
    error?: string;
  }

  let balances: ExchangeBalance[] = [];
  let totalBalance = 0;
  let totalPnl = 0;
  let loading = true;
  let error: string | null = null;
  let refreshing = '';

  $: state = $liveState;
  $: positions = state?.positions || [];

  $: totalDual = formatDual(totalBalance);
  $: pnlDual = formatDual(totalPnl);
  $: todayDual = formatDual(balances.reduce((sum, b) => sum + (b.realized_pnl_today || 0), 0));

  // All 8 configured exchanges
  const ALL_EXCHANGES: ExchangeBalance[] = [
    { exchange: 'binance', name: 'Binance', status: '', wallet_balance: 0, used_margin: 0, total_balance: 0, unrealized_pnl: 0, realized_pnl_today: 0, currency: 'USDT' },
    { exchange: 'bybit', name: 'Bybit', status: '', wallet_balance: 0, used_margin: 0, total_balance: 0, unrealized_pnl: 0, realized_pnl_today: 0, currency: 'USDT' },
    { exchange: 'okx', name: 'OKX', status: '', wallet_balance: 0, used_margin: 0, total_balance: 0, unrealized_pnl: 0, realized_pnl_today: 0, currency: 'USDT' },
    { exchange: 'bitget', name: 'Bitget', status: '', wallet_balance: 0, used_margin: 0, total_balance: 0, unrealized_pnl: 0, realized_pnl_today: 0, currency: 'USDT' },
    { exchange: 'mexc', name: 'MEXC', status: '', wallet_balance: 0, used_margin: 0, total_balance: 0, unrealized_pnl: 0, realized_pnl_today: 0, currency: 'USDT' },
    { exchange: 'kucoin', name: 'KuCoin', status: '', wallet_balance: 0, used_margin: 0, total_balance: 0, unrealized_pnl: 0, realized_pnl_today: 0, currency: 'USDT' },
    { exchange: 'bingx', name: 'BingX', status: '', wallet_balance: 0, used_margin: 0, total_balance: 0, unrealized_pnl: 0, realized_pnl_today: 0, currency: 'USDT' },
    { exchange: 'gateio', name: 'Gate.io', status: '', wallet_balance: 0, used_margin: 0, total_balance: 0, unrealized_pnl: 0, realized_pnl_today: 0, currency: 'USDT' },
  ];

  const exchangeMeta: Record<string, { color: string; bgColor: string }> = {
    binance:  { color: '#F0B90B', bgColor: 'rgba(240, 185, 11, 0.1)' },
    bybit:    { color: '#F7A600', bgColor: 'rgba(247, 166, 0, 0.1)' },
    okx:      { color: '#000000', bgColor: 'rgba(255, 255, 255, 0.08)' },
    bitget:   { color: '#00F0FF', bgColor: 'rgba(0, 240, 255, 0.1)' },
    mexc:     { color: '#00D084', bgColor: 'rgba(0, 208, 132, 0.1)' },
    kucoin:   { color: '#01C480', bgColor: 'rgba(1, 196, 128, 0.1)' },
    bingx:    { color: '#FFC107', bgColor: 'rgba(255, 193, 7, 0.1)' },
    gateio:   { color: '#1E6FFF', bgColor: 'rgba(30, 111, 255, 0.1)' },
  };

  // Count positions per exchange
  function positionsOnExchange(exchangeName: string): number {
    return positions.filter((p: any) => p.exchange?.toLowerCase() === exchangeName).length;
  }

  async function fetchExchangeBalances() {
    try {
      loading = true;
      error = null;
      const res = await fetch('https://futures-brokiepedia-api.kentaursoft-com.workers.dev/api/v1/exchanges/balances');
      if (!res.ok) throw new Error('Failed to fetch balances');
      const data = await res.json();
      balances = data.balances || [];
      totalBalance = data.total_balance || 0;
      totalPnl = data.total_pnl || 0;
    } catch (err: any) {
      error = err.message || 'Failed to load exchange balances';
      console.error('Exchange balances error:', err);
    } finally {
      loading = false;
    }
  }

  async function refreshExchange(exchangeId: string) {
    refreshing = exchangeId;
    try {
      const res = await fetch(`https://futures-brokiepedia-api.kentaursoft-com.workers.dev/api/v1/exchanges/balances?exchange=${exchangeId}`);
      if (res.ok) {
        const data = await res.json();
        if (data.balances) {
          // Update just this exchange in the list
          const updated = data.balances.find((b: any) => b.exchange === exchangeId);
          if (updated) {
            balances = balances.map(b => b.exchange === exchangeId ? { ...b, ...updated } : b);
            recalcTotals();
          }
        }
      }
    } catch (e) {
      console.error(`Refresh ${exchangeId} failed:`, e);
    } finally {
      refreshing = '';
    }
  }

  function recalcTotals() {
    totalBalance = balances.reduce((s, b) => s + (b.total_balance || 0), 0);
    totalPnl = balances.reduce((s, b) => s + (b.unrealized_pnl || 0), 0);
  }

  onMount(() => {
    fetchExchangeBalances();
    const interval = setInterval(fetchExchangeBalances, 30000);
    return () => clearInterval(interval);
  });

  function formatDual(value: number) {
    const crypto = $currency.cryptoCurrency;
    const fiat = $currency.fiatCurrency;
    const rates = $currency.exchangeRates;
    const result = formatCryptoFiat(value, crypto, fiat, rates);
    return { primary: result.crypto, secondary: result.fiat };
  }

  function pnlColor(value: number) {
    if (value > 0) return 'text-emerald-400';
    if (value < 0) return 'text-rose-400';
    return 'text-white/60';
  }

  function pnlSign(value: number) {
    return value > 0 ? '+' : '';
  }

  // Merge live data into the full exchange list
  $: mergedExchanges = ALL_EXCHANGES.map(ex => {
    const live = balances.find(b => b.exchange === ex.exchange);
    const posCount = positionsOnExchange(ex.exchange);
    return {
      ...ex,
      ...live,
      positions_count: posCount,
      available: live ? (live.wallet_balance || 0) - (live.used_margin || 0) : 0,
      status: live?.status || (live ? 'disconnected' : 'unknown'),
    };
  });
</script>

<div class="space-y-5 max-w-7xl mx-auto pb-20 sm:pb-0">
  <!-- Header -->
  <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
    <div>
      <h1 class="text-2xl font-bold text-white/90 font-sans">Exchanges</h1>
      <p class="text-white/40 text-sm mt-1">8 futures exchanges connected</p>
    </div>
    <button 
      class="px-4 py-2 rounded-xl text-sm font-medium transition-all hover:opacity-90 flex items-center gap-2"
      style="background: linear-gradient(135deg, var(--accent-primary), var(--accent-primary)dd);"
      on:click={fetchExchangeBalances}
    >
      <svg class="w-4 h-4 {loading ? 'animate-spin' : ''}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
      </svg>
      Refresh All
    </button>
  </div>

  <!-- Summary Cards -->
  <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
    <GlassCard className="p-4 sm:p-5">
      <div class="flex items-center justify-between mb-2">
        <span class="text-xs text-white/40 uppercase tracking-wider">Total Balance</span>
        <svg class="w-4 h-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <p class="text-lg font-mono font-bold text-white/90">{totalDual.primary || '$0.00'}</p>
      <p class="text-xs text-white/40">{totalDual.secondary || '≈ $0.00'}</p>
    </GlassCard>
    
    <GlassCard className="p-4 sm:p-5">
      <div class="flex items-center justify-between mb-2">
        <span class="text-xs text-white/40 uppercase tracking-wider">Unrealized P&L</span>
        <div class="w-2 h-2 rounded-full {totalPnl >= 0 ? 'bg-emerald-400' : 'bg-rose-400'}"></div>
      </div>
      <p class="text-lg font-mono font-bold {pnlColor(totalPnl)}">{pnlSign(totalPnl)}{pnlDual.primary || '$0.00'}</p>
      <p class="text-xs {totalPnl >= 0 ? 'text-emerald-400/60' : 'text-rose-400/60'}">{pnlSign(totalPnl)}{pnlDual.secondary || '≈ $0.00'}</p>
    </GlassCard>
    
    <GlassCard className="p-4 sm:p-5">
      <div class="flex items-center justify-between mb-2">
        <span class="text-xs text-white/40 uppercase tracking-wider">Connected</span>
        <svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      </div>
      <p class="text-lg font-mono font-bold text-white/90">{balances.filter(b => b.status === 'connected').length}/{ALL_EXCHANGES.length}</p>
      <p class="text-xs text-white/40">Exchanges online</p>
    </GlassCard>
    
    <GlassCard className="p-4 sm:p-5">
      <div class="flex items-center justify-between mb-2">
        <span class="text-xs text-white/40 uppercase tracking-wider">Open Positions</span>
        <svg class="w-4 h-4 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      </div>
      <p class="text-lg font-mono font-bold text-white/90">{positions.length}</p>
      <p class="text-xs text-white/40">Across all exchanges</p>
    </GlassCard>
  </div>

  <!-- Exchange Cards -->
  {#if loading && balances.length === 0}
    <div class="flex items-center justify-center py-12">
      <div class="animate-spin w-8 h-8 border-2 border-white/20 border-t-white/80 rounded-full"></div>
      <span class="ml-3 text-white/40 text-sm">Loading exchange balances...</span>
    </div>
  {:else}
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      {#each mergedExchanges as exchange}
        {@const meta = exchangeMeta[exchange.exchange] || { color: '#888', bgColor: 'rgba(136,136,136,0.1)' }}
        {@const isConnected = exchange.status === 'connected'}
        {@const isUnknown = exchange.status === 'unknown' || (!loading && exchange.status === '')}
        {@const av = formatDual(exchange.available)}
        {@const wallet = formatDual(exchange.wallet_balance)}
        {@const total = formatDual(exchange.total_balance)}

        <div class="rounded-xl p-5 transition-all border {isConnected ? 'glass-card border-white/[0.08]' : isUnknown ? 'glass-card border-white/[0.04] opacity-60' : 'glass-card border-rose-500/20'}">
          <!-- Exchange Header -->
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-3">
              <div class="w-12 h-12 rounded-xl flex items-center justify-center overflow-hidden font-bold text-lg" style="background: {meta.bgColor}; color: {meta.color}">
                {exchange.name.charAt(0)}
              </div>
              <div>
                <h3 class="font-semibold text-white/90 text-lg">{exchange.name}</h3>
                <div class="flex items-center gap-2 mt-0.5">
                  {#if isConnected}
                    <StatusBadge status="online" size="sm" />
                    {#if exchange.positions_count > 0}
                      <span class="text-xs px-1.5 py-0.5 rounded bg-amber-500/15 text-amber-400 font-mono">{exchange.positions_count} pos</span>
                    {/if}
                  {:else if isUnknown}
                    <span class="text-xs text-zinc-500 font-sans">Not configured</span>
                  {:else}
                    <span class="text-xs text-rose-400 font-sans">{exchange.status}</span>
                  {/if}
                </div>
              </div>
            </div>

            <div class="flex items-center gap-2">
              {#if isConnected}
                <button
                  class="p-1.5 rounded-lg hover:bg-white/[0.08] transition-colors"
                  on:click={() => refreshExchange(exchange.exchange)}
                  title="Refresh"
                >
                  <svg class="w-4 h-4 text-white/40 {refreshing === exchange.exchange ? 'animate-spin' : ''}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                </button>
              {/if}
              <span class="text-xs px-2 py-1 rounded-lg {isConnected ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : isUnknown ? 'bg-zinc-700/30 text-zinc-500 border border-zinc-700/30' : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'}">
                {isConnected ? 'Live' : isUnknown ? 'Pending' : 'Error'}
              </span>
            </div>
          </div>

          {#if isConnected}
            <!-- Balance Grid (connected exchanges) -->
            <div class="grid grid-cols-2 gap-3">
              <div class="p-3 rounded-lg bg-white/[0.03]">
                <span class="text-[10px] text-white/30 uppercase tracking-wider block mb-1">Available</span>
                <span class="text-sm font-mono font-semibold text-white/80">{av.primary}</span>
                <span class="text-[10px] text-white/30 block">{av.secondary}</span>
              </div>
              <div class="p-3 rounded-lg bg-white/[0.03]">
                <span class="text-[10px] text-white/30 uppercase tracking-wider block mb-1">Used Margin</span>
                <span class="text-sm font-mono font-semibold text-white/80">{(exchange.used_margin || 0).toFixed(2)} USDT</span>
              </div>
              <div class="p-3 rounded-lg bg-white/[0.03]">
                <span class="text-[10px] text-white/30 uppercase tracking-wider block mb-1">Wallet Balance</span>
                <span class="text-sm font-mono font-semibold text-white/80">{wallet.primary}</span>
                <span class="text-[10px] text-white/30 block">{wallet.secondary}</span>
              </div>
              <div class="p-3 rounded-lg bg-white/[0.03]">
                <span class="text-[10px] text-white/30 uppercase tracking-wider block mb-1">Unrealized P&L</span>
                <span class="text-sm font-mono font-semibold {pnlColor(exchange.unrealized_pnl)}">{pnlSign(exchange.unrealized_pnl)}{(exchange.unrealized_pnl || 0).toFixed(2)}</span>
              </div>
            </div>
          {:else if isUnknown}
            <!-- Placeholder for unconfigured exchanges -->
            <div class="py-4 text-center">
              <p class="text-sm text-zinc-500 font-sans">API keys not configured yet</p>
              <a href="/settings" class="text-xs text-emerald-500 hover:text-emerald-400 transition-colors mt-1 inline-block">Configure in Settings →</a>
            </div>
          {:else}
            <!-- Error state -->
            <div class="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20">
              <p class="text-xs text-rose-400">{exchange.error || 'Connection failed'}</p>
            </div>
          {/if}

          {#if exchange.error && isConnected}
            <div class="mt-3 p-2 rounded-lg bg-rose-500/10 border border-rose-500/20">
              <p class="text-xs text-rose-400">{exchange.error}</p>
            </div>
          {/if}
        </div>
      {/each}
    </div>
  {/if}
</div>
