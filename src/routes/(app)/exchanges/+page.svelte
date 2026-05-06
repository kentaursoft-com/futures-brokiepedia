<script lang="ts">
  import { onMount } from 'svelte';
  import GlassCard from '$lib/components/GlassCard.svelte';
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
    error?: string;
  }
  
  let balances: ExchangeBalance[] = [];
  let totalBalance = 0;
  let totalPnl = 0;
  let loading = true;
  let error: string | null = null;
  
  $: totalDual = formatDual(totalBalance);
  $: pnlDual = formatDual(totalPnl);
  $: todayDual = formatDual(balances.reduce((sum, b) => sum + (b.realized_pnl_today || 0), 0));
  
  // Exchange brand colors and inline SVG logos
  const exchangeMeta: Record<string, { color: string; bgColor: string; logo: string }> = {
    binance: {
      color: '#F0B90B',
      bgColor: 'rgba(240, 185, 11, 0.1)',
      logo: `<svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg"><rect width="32" height="32" rx="8" fill="#F0B90B"/><path d="M16 4l-3 3 3 3 3-3-3-3zM8 12l-3 3 3 3 3-3-3-3zM24 12l-3 3 3 3 3-3-3-3zM16 10l-5 5 5 5 5-5-5-5zM8 20l-3 3 3 3 3-3-3-3zM24 20l-3 3 3 3 3-3-3-3zM16 22l-3 3 3 3 3-3-3-3z" fill="white"/></svg>`
    },
    bybit: {
      color: '#F7A600',
      bgColor: 'rgba(247, 166, 0, 0.1)',
      logo: `<svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg"><rect width="32" height="32" rx="8" fill="#F7A600"/><path d="M8 10h3v12H8V10zm5 0h3l5 7.5V10h3v12h-3l-5-7.5V22h-3V10z" fill="white"/></svg>`
    },
    okx: {
      color: '#000000',
      bgColor: 'rgba(255, 255, 255, 0.1)',
      logo: `<svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg"><rect width="32" height="32" rx="8" fill="white"/><path d="M10 10h4.5v4.5H10V10zm7.5 0H22v4.5h-4.5V10zM10 17.5h4.5V22H10v-4.5zm7.5 0H22V22h-4.5v-4.5zM17.5 13.75h-3v4.5h3v-4.5z" fill="black"/></svg>`
    },
    bitget: {
      color: '#00F0FF',
      bgColor: 'rgba(0, 240, 255, 0.1)',
      logo: `<svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg"><rect width="32" height="32" rx="8" fill="#00F0FF"/><path d="M16 6l10 10-10 10L6 16 16 6z" fill="white"/></svg>`
    },
    mexc: {
      color: '#00D084',
      bgColor: 'rgba(0, 208, 132, 0.1)',
      logo: `<svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg"><rect width="32" height="32" rx="8" fill="#00D084"/><path d="M9 22V10h2.5l4.5 7.5L20.5 10H23v12h-2.5v-7l-3.5 7h-1.5l-3.5-7v7H9z" fill="white"/></svg>`
    }
  };
  
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
    return {
      primary: result.crypto,
      secondary: result.fiat
    };
  }
  
  function pnlColor(value: number) {
    if (value > 0) return 'text-emerald-400';
    if (value < 0) return 'text-rose-400';
    return 'text-white/60';
  }
  
  function pnlSign(value: number) {
    if (value > 0) return '+';
    return '';
  }
</script>

<div class="space-y-5 max-w-7xl mx-auto pb-20 sm:pb-0">
  <!-- Header -->
  <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
    <div>
      <h1 class="text-2xl font-bold text-white/90 font-sans">Crypto Broker Exchange</h1>
      <p class="text-white/40 text-sm mt-1">Manage your exchange accounts and balances</p>
    </div>
    <button 
      class="px-4 py-2 rounded-xl text-sm font-medium transition-all hover:opacity-90"
      style="background: linear-gradient(135deg, var(--accent-primary), var(--accent-primary)dd);"
      on:click={fetchExchangeBalances}
    >
      Refresh Balances
    </button>
  </div>

  <!-- Summary Cards -->
  <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
    <GlassCard className="p-4 sm:p-5">
      <div class="flex items-center justify-between mb-2">
        <span class="text-xs text-white/40 uppercase tracking-wider">Total Balance</span>
        <div class="w-2 h-2 rounded-full bg-blue-400 shadow-[0_0_8px_rgba(59,130,246,0.6)]"></div>
      </div>
      <p class="text-lg font-mono font-bold text-white/90">{totalDual.primary}</p>
      <p class="text-xs text-white/40">{totalDual.secondary}</p>
    </GlassCard>
    
    <GlassCard className="p-4 sm:p-5">
      <div class="flex items-center justify-between mb-2">
        <span class="text-xs text-white/40 uppercase tracking-wider">Unrealized P&L</span>
        <div class="w-2 h-2 rounded-full {totalPnl >= 0 ? 'bg-emerald-400' : 'bg-rose-400'}"></div>
      </div>
      <p class="text-lg font-mono font-bold {pnlColor(totalPnl)}">{pnlSign(totalPnl)}{pnlDual.primary}</p>
      <p class="text-xs {totalPnl >= 0 ? 'text-emerald-400/60' : 'text-rose-400/60'}">{pnlSign(totalPnl)}{pnlDual.secondary}</p>
    </GlassCard>
    
    <GlassCard className="p-4 sm:p-5">
      <div class="flex items-center justify-between mb-2">
        <span class="text-xs text-white/40 uppercase tracking-wider">Connected</span>
        <div class="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(16,185,129,0.6)]"></div>
      </div>
      <p class="text-lg font-mono font-bold text-white/90">{balances.filter(b => b.status === 'connected').length}/{balances.length}</p>
      <p class="text-xs text-white/40">Exchanges</p>
    </GlassCard>
    
    <GlassCard className="p-4 sm:p-5">
      <div class="flex items-center justify-between mb-2">
        <span class="text-xs text-white/40 uppercase tracking-wider">Today's P&L</span>
        <div class="w-2 h-2 rounded-full bg-amber-400"></div>
      </div>
      <p class="text-lg font-mono font-bold text-white/90">{todayDual.primary}</p>
      <p class="text-xs text-white/40">{todayDual.secondary}</p>
    </GlassCard>
  </div>

  <!-- Exchange Cards -->
  {#if loading}
    <div class="flex items-center justify-center py-12">
      <div class="animate-spin w-8 h-8 border-2 border-white/20 border-t-white/80 rounded-full"></div>
      <span class="ml-3 text-white/40 text-sm">Loading exchange balances...</span>
    </div>
  {:else if error}
    <div class="glass-card p-6 rounded-xl text-center">
      <p class="text-rose-400 text-sm">{error}</p>
      <button 
        class="mt-3 px-4 py-2 rounded-lg bg-white/[0.08] text-white/60 text-sm hover:bg-white/[0.12] transition-colors"
        on:click={fetchExchangeBalances}
      >
        Try Again
      </button>
    </div>
  {:else}
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      {#each balances as exchange}
        {@const meta = exchangeMeta[exchange.exchange] || { color: '#888', bgColor: 'rgba(136,136,136,0.1)', logo: '' }}
        {@const wallet = formatDual(exchange.wallet_balance)}
        {@const margin = formatDual(exchange.used_margin)}
        {@const total = formatDual(exchange.total_balance)}
        {@const unPnl = formatDual(exchange.unrealized_pnl)}
        <div class="glass-card rounded-xl p-5 transition-all hover:border-white/20">
          <!-- Exchange Header -->
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-3">
              <div class="w-12 h-12 rounded-xl flex items-center justify-center overflow-hidden" style="background: {meta.bgColor}">
                {@html meta.logo}
              </div>
              <div>
                <h3 class="font-semibold text-white/90 text-lg">{exchange.name}</h3>
                <div class="flex items-center gap-1.5 mt-0.5">
                  <span class="w-2 h-2 rounded-full {exchange.status === 'connected' ? 'bg-emerald-400' : exchange.status === 'error' ? 'bg-rose-400' : 'bg-amber-400'}"></span>
                  <span class="text-xs text-white/40 capitalize">{exchange.status}</span>
                </div>
              </div>
            </div>
            {#if exchange.status === 'disconnected'}
              <span class="text-xs px-2 py-1 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20">API Key Required</span>
            {/if}
          </div>
          
          <!-- Balance Grid -->
          <div class="grid grid-cols-2 gap-3">
            <!-- Wallet Balance -->
            <div class="p-3 rounded-lg bg-white/[0.03]">
              <span class="text-[10px] text-white/30 uppercase tracking-wider block mb-1">Wallet Balance</span>
              <span class="text-sm font-mono font-semibold text-white/80">{wallet.primary}</span>
              <span class="text-[10px] text-white/30 block">{wallet.secondary}</span>
            </div>
            
            <!-- Used Margin -->
            <div class="p-3 rounded-lg bg-white/[0.03]">
              <span class="text-[10px] text-white/30 uppercase tracking-wider block mb-1">Used Margin</span>
              <span class="text-sm font-mono font-semibold text-white/80">{margin.primary}</span>
              <span class="text-[10px] text-white/30 block">{margin.secondary}</span>
            </div>
            
            <!-- Total Balance -->
            <div class="p-3 rounded-lg bg-white/[0.03]">
              <span class="text-[10px] text-white/30 uppercase tracking-wider block mb-1">Total Balance</span>
              <span class="text-sm font-mono font-semibold text-white/80">{total.primary}</span>
              <span class="text-[10px] text-white/30 block">{total.secondary}</span>
            </div>
            
            <!-- Unrealized P&L -->
            <div class="p-3 rounded-lg bg-white/[0.03]">
              <span class="text-[10px] text-white/30 uppercase tracking-wider block mb-1">Unrealized P&L</span>
              <span class="text-sm font-mono font-semibold {pnlColor(exchange.unrealized_pnl)}">{pnlSign(exchange.unrealized_pnl)}{unPnl.primary}</span>
              <span class="text-[10px] {exchange.unrealized_pnl >= 0 ? 'text-emerald-400/60' : 'text-rose-400/60'} block">{pnlSign(exchange.unrealized_pnl)}{unPnl.secondary}</span>
            </div>
          </div>
          
          {#if exchange.error}
            <div class="mt-3 p-2 rounded-lg bg-rose-500/10 border border-rose-500/20">
              <p class="text-xs text-rose-400">{exchange.error}</p>
            </div>
          {/if}
        </div>
      {/each}
    </div>
  {/if}
</div>
