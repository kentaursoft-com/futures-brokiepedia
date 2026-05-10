<script lang="ts">
  import { onMount } from 'svelte';
  import { liveState, api } from '$lib/api';
  import GlassCard from '$lib/components/GlassCard.svelte';
  import StatusBadge from '$lib/components/StatusBadge.svelte';
  import { tradingMode } from '$lib/stores/tradingMode';
  
  let marketPrices: Record<string, number> = {};
  let recentActivity: any[] = [];
  let priceInterval: ReturnType<typeof setInterval>;
  let activityInterval: ReturnType<typeof setInterval>;
  
  // Mock equity history for sparkline (will be replaced by real data)
  let equityHistory: number[] = [];
  
  async function fetchMarketPrices() {
    try {
      const res = await fetch('https://futures-brokiepedia-api.kentaursoft-com.workers.dev/api/v1/prices?symbols=["BTCUSDT","ETHUSDT","SOLUSDT"]');
      if (res.ok) {
        const data = await res.json();
        data.forEach((t: any) => marketPrices[t.symbol] = parseFloat(t.lastPrice));
        marketPrices = marketPrices;
      }
    } catch (err) {
      console.error('Failed to fetch market prices:', err);
    }
  }
  
  async function fetchActivity() {
    try {
      const data = await api.getActivity();
      recentActivity = data.activity || [];
    } catch (err) {
      console.error('Activity fetch error:', err);
    }
  }
  
  onMount(() => {
    fetchMarketPrices();
    fetchActivity();
    priceInterval = setInterval(fetchMarketPrices, 5000);
    activityInterval = setInterval(fetchActivity, 10000);
    return () => {
      clearInterval(priceInterval);
      clearInterval(activityInterval);
    };
  });
  
  $: state = $liveState;
  $: equity = state?.equity || 10000;
  $: todayPnl = state?.todayPnl || 0;
  $: unrealizedPnl = state?.unrealizedPnl || 0;
  $: positions = state?.positions || [];
  $: departments = state?.departments || [];
  $: dailyDrawdown = state?.dailyDrawdown || 0;
  $: executionEnabled = state?.executionEnabled !== false;
  $: systemStatus = state?.systemStatus || 'paper';
  $: binanceConnected = state?.binance_ws_connected || false;
  
  $: pnlColor = todayPnl >= 0 ? 'text-emerald-400' : 'text-rose-400';
  $: pnlSign = todayPnl >= 0 ? '+' : '';
  $: hasPositions = positions.length > 0;
  
  // Build equity sparkline path
  $: sparklinePoints = (() => {
    const data = equityHistory;
    if (data.length < 2) return '';
    const w = 300, h = 60;
    const min = Math.min(...data);
    const max = Math.max(...data);
    const range = max - min || 1;
    return data.map((v, i) => {
      const x = (i / (data.length - 1)) * w;
      const y = h - ((v - min) / range) * h;
      return `${i === 0 ? 'M' : 'L'}${x.toFixed(1)},${y.toFixed(1)}`;
    }).join(' ');
  })();
  
  // Mini sparkline for equity trend
  $: equityTrend = (() => {
    if (equityHistory.length < 2) return 'neutral';
    const change = equityHistory[equityHistory.length - 1] - equityHistory[0];
    if (change > 0) return 'up';
    if (change < 0) return 'down';
    return 'neutral';
  })();
  
  // Build department badges
  const DEPARTMENTS = ['Quantitative', 'Technical', 'Sentiment', 'Fundamental', 'Statistical', 'Qualitative'];
  
  function deptDirection(name: string): string {
    const d = departments.find((d: any) => d.name?.toLowerCase() === name.toLowerCase());
    return d?.direction || 'flat';
  }
  
  function deptConfidence(name: string): number {
    const d = departments.find((d: any) => d.name?.toLowerCase() === name.toLowerCase());
    return d?.confidence || 0;
  }
  
  // Overall bias from departments
  $: overallBias = (() => {
    const longs = departments.filter((d: any) => d.direction === 'long').length;
    const shorts = departments.filter((d: any) => d.direction === 'short').length;
    if (longs > shorts) return 'LONG';
    if (shorts > longs) return 'SHORT';
    return '—';
  })();
  
  $: overallConfidence = (() => {
    const scores = departments.map((d: any) => {
      const weight = d.direction === 'long' ? 1 : d.direction === 'short' ? -1 : 0;
      return weight * (d.confidence || 0);
    });
    if (scores.length === 0) return 0;
    return Math.abs(scores.reduce((a: number, b: number) => a + b, 0) / scores.length);
  })();
</script>

<div class="space-y-5 sm:space-y-6 max-w-7xl mx-auto pb-20 sm:pb-0">
  <!-- Header Section -->
  <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
    <div class="flex items-center gap-3">
      <h1 class="text-2xl sm:text-3xl font-bold text-white/90 font-sans">Dashboard</h1>
      <StatusBadge status={executionEnabled ? 'online' : 'error'} label={$tradingMode === 'live' ? 'LIVE' : 'PAPER'} size="sm" />
    </div>
    <div class="flex items-center gap-3">
      <!-- Connection Health Dots -->
      <div class="flex items-center gap-2.5 bg-zinc-800/50 rounded-lg px-3 py-1.5 border border-zinc-700/30">
        <div class="flex items-center gap-1.5" title="Daemon">
          <div class="w-1.5 h-1.5 rounded-full {state ? 'bg-emerald-400' : 'bg-rose-400'}"></div>
          <span class="text-xs text-zinc-400 font-mono">Daemon</span>
        </div>
        <div class="flex items-center gap-1.5" title="Binance WebSocket">
          <div class="w-1.5 h-1.5 rounded-full {binanceConnected ? 'bg-emerald-400' : 'bg-rose-400'}"></div>
          <span class="text-xs text-zinc-400 font-mono">WS</span>
        </div>
        <div class="flex items-center gap-1.5" title="DeepSeek AI">
          <div class="w-1.5 h-1.5 rounded-full bg-emerald-400"></div>
          <span class="text-xs text-zinc-400 font-mono">AI</span>
        </div>
        <div class="flex items-center gap-1.5" title="Turso Database">
          <div class="w-1.5 h-1.5 rounded-full bg-emerald-400"></div>
          <span class="text-xs text-zinc-400 font-mono">DB</span>
        </div>
        <div class="flex items-center gap-1.5" title="Execution">
          <div class="w-1.5 h-1.5 rounded-full {executionEnabled ? 'bg-emerald-400' : 'bg-rose-400'}"></div>
          <span class="text-xs text-zinc-400 font-mono">Exec</span>
        </div>
      </div>
      <StatusBadge status={dailyDrawdown > 3 ? 'warning' : dailyDrawdown > 6 ? 'error' : 'online'} label={`DD: ${dailyDrawdown.toFixed(1)}%`} size="sm" />
    </div>
  </div>

  <!-- Key Metrics Row -->
  <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
    <GlassCard className="p-4 sm:p-5">
      <div class="flex items-center justify-between mb-2 sm:mb-3">
        <span class="text-sm sm:text-xs text-white/40 font-sans uppercase tracking-wider">Equity</span>
        <div class="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(16,185,129,0.6)]"></div>
      </div>
      <p class="text-xl sm:text-2xl font-bold font-mono text-white/90">${equity.toLocaleString('en-US', { minimumFractionDigits: 2 })}</p>
    </GlassCard>
    
    <GlassCard className="p-4 sm:p-5">
      <div class="flex items-center justify-between mb-2 sm:mb-3">
        <span class="text-sm sm:text-xs text-white/40 font-sans uppercase tracking-wider">Today's P&L</span>
        <div class="w-2 h-2 rounded-full {todayPnl >= 0 ? 'bg-emerald-400' : 'bg-rose-400'}"></div>
      </div>
      <p class="text-xl sm:text-2xl font-bold font-mono {pnlColor}">{pnlSign}{todayPnl.toFixed(2)}</p>
    </GlassCard>
    
    <GlassCard className="p-4 sm:p-5">
      <div class="flex items-center justify-between mb-2 sm:mb-3">
        <span class="text-sm sm:text-xs text-white/40 font-sans uppercase tracking-wider">Unrealized</span>
        <div class="w-2 h-2 rounded-full {unrealizedPnl >= 0 ? 'bg-emerald-400' : 'bg-rose-400'}"></div>
      </div>
      <p class="text-xl sm:text-2xl font-bold font-mono {unrealizedPnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}">{unrealizedPnl >= 0 ? '+' : ''}{unrealizedPnl.toFixed(2)}</p>
    </GlassCard>
    
    <GlassCard className="p-4 sm:p-5">
      <div class="flex items-center justify-between mb-2 sm:mb-3">
        <span class="text-sm sm:text-xs text-white/40 font-sans uppercase tracking-wider">Positions</span>
        <div class="w-2 h-2 rounded-full bg-blue-400"></div>
      </div>
      <p class="text-xl sm:text-2xl font-bold font-mono text-white/90">{positions.length}</p>
    </GlassCard>
  </div>

  <!-- Main Content Grid -->
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
    <!-- Left Column -->
    <div class="lg:col-span-2 space-y-4 sm:space-y-6">
      <!-- Risk Management -->
      <GlassCard title="Risk Management" subtitle="Real-time risk monitoring">
        <div class="grid grid-cols-2 sm:grid-cols-3 gap-3 sm:gap-4">
          <div class="bg-white/[0.03] rounded-xl p-3 sm:p-4 border border-white/[0.06]">
            <p class="text-sm sm:text-xs text-white/40 mb-1 font-sans">Max Risk/Trade</p>
            <p class="text-lg sm:text-xl font-mono font-bold text-white/90">2.0%</p>
          </div>
          <div class="bg-white/[0.03] rounded-xl p-3 sm:p-4 border border-white/[0.06]">
            <p class="text-sm sm:text-xs text-white/40 mb-1 font-sans">Max Positions</p>
            <p class="text-lg sm:text-xl font-mono font-bold text-white/90">4</p>
          </div>
          <div class="bg-white/[0.03] rounded-xl p-3 sm:p-4 border border-white/[0.06]">
            <p class="text-sm sm:text-xs text-white/40 mb-1 font-sans">Soft Drawdown</p>
            <p class="text-lg sm:text-xl font-mono font-bold text-amber-400">3.0%</p>
          </div>
          <div class="bg-white/[0.03] rounded-xl p-3 sm:p-4 border border-white/[0.06]">
            <p class="text-sm sm:text-xs text-white/40 mb-1 font-sans">Hard Drawdown</p>
            <p class="text-lg sm:text-xl font-mono font-bold text-rose-400">6.0%</p>
          </div>
          <div class="bg-white/[0.03] rounded-xl p-3 sm:p-4 border border-white/[0.06]">
            <p class="text-sm sm:text-xs text-white/40 mb-1 font-sans">Max Leverage</p>
            <p class="text-lg sm:text-xl font-mono font-bold text-white/90">5x</p>
          </div>
          <div class="bg-white/[0.03] rounded-xl p-3 sm:p-4 border border-white/[0.06]">
            <p class="text-sm sm:text-xs text-white/40 mb-1 font-sans">Kill Switch</p>
            <p class="text-lg sm:text-xl font-mono font-bold {executionEnabled ? 'text-emerald-400' : 'text-rose-400'}">{executionEnabled ? 'ARMED' : 'TRIPPED'}</p>
          </div>
        </div>
        
        <!-- Drawdown Bar -->
        <div class="mt-4 sm:mt-5">
          <div class="flex items-center justify-between mb-2">
            <span class="text-sm sm:text-xs text-white/40 font-sans">Current Drawdown</span>
            <span class="text-sm sm:text-xs font-mono {dailyDrawdown > 3 ? 'text-rose-400' : 'text-emerald-400'}">{dailyDrawdown.toFixed(2)}%</span>
          </div>
          <div class="h-2.5 sm:h-2 bg-white/[0.06] rounded-full overflow-hidden">
            <div 
              class="h-full rounded-full transition-all duration-500 {dailyDrawdown > 6 ? 'bg-gradient-to-r from-rose-500 to-rose-400' : dailyDrawdown > 3 ? 'bg-gradient-to-r from-amber-500 to-amber-400' : 'bg-gradient-to-r from-emerald-500 to-emerald-400'}"
              style="width: {Math.min(100, (dailyDrawdown / 6) * 100)}%"
            ></div>
          </div>
          <div class="flex justify-between mt-1">
            <span class="text-xs text-white/30 font-mono">0%</span>
            <span class="text-xs text-amber-400/60 font-mono">3%</span>
            <span class="text-xs text-rose-400/60 font-mono">6%</span>
          </div>
        </div>
      </GlassCard>

      <!-- Equity Curve Sparkline -->
      <GlassCard title="Equity Trend" subtitle="Portfolio value over time">
        {#if equityHistory.length >= 2}
          <svg viewBox="0 0 300 60" class="w-full h-16" preserveAspectRatio="none">
            <defs>
              <linearGradient id="sparkline-fill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="rgb(52, 211, 153)" stop-opacity="0.3" />
                <stop offset="100%" stop-color="rgb(52, 211, 153)" stop-opacity="0" />
              </linearGradient>
            </defs>
            <path d="{sparklinePoints} L300,60 L0,60 Z" fill="url(#sparkline-fill)" />
            <path d={sparklinePoints} fill="none" stroke="rgb(52, 211, 153)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
          <div class="flex justify-between text-xs text-zinc-500 font-mono mt-1">
            <span>${Math.min(...equityHistory).toFixed(0)}</span>
            <span class="{equityTrend === 'up' ? 'text-emerald-400' : equityTrend === 'down' ? 'text-rose-400' : 'text-zinc-400'}">
              {equityTrend === 'up' ? '📈 Trending Up' : equityTrend === 'down' ? '📉 Trending Down' : '➡️ Stable'}
            </span>
            <span>${Math.max(...equityHistory).toFixed(0)}</span>
          </div>
        {:else}
          <div class="h-16 flex items-center justify-center">
            <p class="text-sm text-zinc-500 font-sans">Collecting equity data...</p>
          </div>
          <div class="flex justify-center mt-2 gap-1">
            {#each Array(30) as _, i}
              <div 
                class="w-2 bg-emerald-500/30 rounded-t" 
                style="height: {10 + Math.random() * 30}px"
              ></div>
            {/each}
          </div>
          <div class="flex justify-between text-xs text-zinc-500 font-mono mt-1">
            <span>$9,800</span>
            <span class="text-zinc-500">📊 Simulated</span>
            <span>$10,500</span>
          </div>
        {/if}
      </GlassCard>

      <!-- Agent Verdicts Compact -->
      <GlassCard title="Agent Verdicts" subtitle="6 department signals">
        <div class="flex flex-wrap gap-2 sm:gap-3">
          {#each DEPARTMENTS as dept}
            {@const dir = deptDirection(dept)}
            {@const conf = deptConfidence(dept)}
            <div class="flex-1 min-w-[80px] sm:min-w-[100px] bg-zinc-800/40 rounded-xl p-3 border {dir === 'long' ? 'border-emerald-500/20' : dir === 'short' ? 'border-rose-500/20' : 'border-zinc-700/20'}">
              <div class="text-[10px] sm:text-xs text-zinc-400 font-sans truncate">{dept.substring(0, 5)}</div>
              <div class="text-sm sm:text-base font-bold font-mono mt-1 {dir === 'long' ? 'text-emerald-400' : dir === 'short' ? 'text-rose-400' : 'text-zinc-500'}">
                {dir === 'long' ? 'LONG' : dir === 'short' ? 'SHORT' : '—'}
              </div>
              <div class="h-1 bg-zinc-700/50 rounded-full overflow-hidden mt-1.5">
                <div 
                  class="h-full rounded-full transition-all {dir === 'long' ? 'bg-emerald-400' : dir === 'short' ? 'bg-rose-400' : 'bg-zinc-600'}"
                  style="width: {conf * 100}%"
                ></div>
              </div>
            </div>
          {/each}
        </div>
        <!-- Overall bias mini row -->
        <div class="flex items-center justify-center gap-3 mt-3 pt-3 border-t border-zinc-800/50">
          <span class="text-xs text-zinc-500 font-sans">Overall:</span>
          <span class="text-sm font-bold font-mono {overallBias === 'LONG' ? 'text-emerald-400' : overallBias === 'SHORT' ? 'text-rose-400' : 'text-zinc-500'}">
            {overallBias}
          </span>
          <div class="w-20 h-1.5 bg-zinc-700/50 rounded-full overflow-hidden">
            <div 
              class="h-full rounded-full transition-all {overallBias === 'LONG' ? 'bg-emerald-400' : overallBias === 'SHORT' ? 'bg-rose-400' : 'bg-zinc-600'}"
              style="width: {overallConfidence * 100}%"
            ></div>
          </div>
          <span class="text-xs text-zinc-500 font-mono">{(overallConfidence * 100).toFixed(0)}%</span>
        </div>
      </GlassCard>
    </div>

    <!-- Right Column -->
    <div class="space-y-4 sm:space-y-6">
      <!-- Market Prices -->
      <GlassCard title="Market Prices" subtitle="Live Binance futures">
        <div class="space-y-3">
          {#each Object.entries(marketPrices) as [symbol, price]}
            <div class="flex items-center justify-between py-2 border-b border-white/[0.04] last:border-0">
              <span class="text-base sm:text-sm font-sans text-white/70">{symbol.replace('USDT', '')}</span>
              <span class="text-base sm:text-sm font-mono font-semibold text-white/90">${price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
            </div>
          {:else}
            <div class="py-4 text-center text-base text-white/30 font-sans">Loading prices...</div>
          {/each}
        </div>
      </GlassCard>

      <!-- Quick Actions -->
      <GlassCard title="Quick Actions">
        <div class="grid grid-cols-2 gap-3">
          <a href="/trade" class="flex flex-col items-center gap-2 p-4 rounded-xl bg-white/[0.03] hover:bg-white/[0.06] border border-white/[0.06] hover:border-emerald-500/30 transition-all group">
            <svg class="w-6 h-6 text-white/40 group-hover:text-emerald-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
            <span class="text-sm font-sans text-white/50 group-hover:text-white/90 transition-colors">New Trade</span>
          </a>
          <a href="/positions" class="flex flex-col items-center gap-2 p-4 rounded-xl bg-white/[0.03] hover:bg-white/[0.06] border border-white/[0.06] hover:border-blue-500/30 transition-all group">
            <svg class="w-6 h-6 text-white/40 group-hover:text-blue-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <span class="text-sm font-sans text-white/50 group-hover:text-white/90 transition-colors">Positions</span>
          </a>
          <a href="/signals" class="flex flex-col items-center gap-2 p-4 rounded-xl bg-white/[0.03] hover:bg-white/[0.06] border border-white/[0.06] hover:border-purple-500/30 transition-all group">
            <svg class="w-6 h-6 text-white/40 group-hover:text-purple-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            <span class="text-sm font-sans text-white/50 group-hover:text-white/90 transition-colors">Signals</span>
          </a>
          <a href="/settings" class="flex flex-col items-center gap-2 p-4 rounded-xl bg-white/[0.03] hover:bg-white/[0.06] border border-white/[0.06] hover:border-amber-500/30 transition-all group">
            <svg class="w-6 h-6 text-white/40 group-hover:text-amber-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            </svg>
            <span class="text-sm font-sans text-white/50 group-hover:text-white/90 transition-colors">Settings</span>
          </a>
        </div>
      </GlassCard>
    </div>
  </div>
</div>
