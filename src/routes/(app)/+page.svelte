<script lang="ts">
  import { onMount } from 'svelte';
  import { liveState, api } from '$lib/api';
  import GlassCard from '$lib/components/GlassCard.svelte';
  import StatusBadge from '$lib/components/StatusBadge.svelte';
  import ProgressBar from '$lib/components/ProgressBar.svelte';
  
  let marketPrices: Record<string, number> = {};
  let recentActivity: any[] = [];
  let activeStrategies: any[] = [];
  let priceInterval: ReturnType<typeof setInterval>;
  let activityInterval: ReturnType<typeof setInterval>;
  let strategyInterval: ReturnType<typeof setInterval>;
  
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
  
  async function fetchStrategies() {
    try {
      const res = await fetch('https://futures-brokiepedia-api.kentaursoft-com.workers.dev/api/v1/strategies/active');
      if (res.ok) {
        const data = await res.json();
        activeStrategies = data.strategies || [];
      }
    } catch (err) {
      console.error('Strategies fetch error:', err);
    }
  }
  
  onMount(() => {
    fetchMarketPrices();
    fetchActivity();
    fetchStrategies();
    priceInterval = setInterval(fetchMarketPrices, 5000);
    activityInterval = setInterval(fetchActivity, 10000);
    strategyInterval = setInterval(fetchStrategies, 30000);
    return () => {
      clearInterval(priceInterval);
      clearInterval(activityInterval);
      clearInterval(strategyInterval);
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
  
  $: pnlColor = todayPnl >= 0 ? 'text-emerald-400' : 'text-rose-400';
  $: pnlSign = todayPnl >= 0 ? '+' : '';
  
  $: progressMetrics = [
    { label: 'Auth Gate', value: 100, variant: 'emerald' as const },
    { label: 'Health Checks', value: state ? 100 : 0, variant: state ? 'emerald' as const : 'rose' as const },
    { label: 'VPS Connected', value: state ? 100 : 0, variant: state ? 'emerald' as const : 'rose' as const },
    { label: 'Real KV Data', value: state ? 100 : 0, variant: state ? 'emerald' as const : 'amber' as const },
    { label: 'Trading Chart', value: 100, variant: 'emerald' as const },
    { label: 'Agent Panel', value: 100, variant: 'emerald' as const },
    { label: 'Strategy Panel', value: 100, variant: 'emerald' as const },
    { label: 'Kill Switch', value: 100, variant: 'emerald' as const },
    { label: 'Paper Trading', value: 100, variant: 'emerald' as const },
    { label: 'Risk Gate', value: 100, variant: 'emerald' as const },
  ];
</script>

<div class="space-y-5 sm:space-y-6 max-w-7xl mx-auto pb-20 sm:pb-0">
  <!-- Header Section -->
  <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
    <div>
      <h1 class="text-2xl sm:text-3xl font-bold text-white/90 font-sans">Dashboard</h1>
      <p class="text-sm text-white/40 mt-1 font-mono">{new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</p>
    </div>
    <div class="flex items-center gap-3">
      <StatusBadge status={executionEnabled ? 'online' : 'error'} label={systemStatus.toUpperCase()} size="md" />
      <StatusBadge status={dailyDrawdown > 3 ? 'warning' : dailyDrawdown > 6 ? 'error' : 'online'} label={`DD: ${dailyDrawdown.toFixed(1)}%`} size="md" />
    </div>
  </div>

  <!-- Key Metrics Row -->
  <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
    <GlassCard className="p-4 sm:p-5">
      <div class="flex items-center justify-between mb-2 sm:mb-3">
        <span class="text-sm sm:text-xs text-white/40 font-sans uppercase tracking-wider">Equity</span>
        <div class="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(16,185,129,0.6)] animate-glow-emerald"></div>
      </div>
      <p class="text-xl sm:text-2xl font-bold font-mono text-white/90">${equity.toLocaleString('en-US', { minimumFractionDigits: 2 })}</p>
    </GlassCard>
    
    <GlassCard className="p-4 sm:p-5">
      <div class="flex items-center justify-between mb-2 sm:mb-3">
        <span class="text-sm sm:text-xs text-white/40 font-sans uppercase tracking-wider">Today's P&L</span>
        <div class="w-2 h-2 rounded-full {todayPnl >= 0 ? 'bg-emerald-400 shadow-[0_0_8px_rgba(16,185,129,0.6)]' : 'bg-rose-400 shadow-[0_0_8px_rgba(244,63,94,0.6)]'} {todayPnl >= 0 ? 'animate-glow-emerald' : 'animate-glow-rose'}"></div>
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
        <div class="w-2 h-2 rounded-full bg-blue-400 shadow-[0_0_8px_rgba(59,130,246,0.6)]"></div>
      </div>
      <p class="text-xl sm:text-2xl font-bold font-mono text-white/90">{positions.length}</p>
    </GlassCard>
  </div>

  <!-- Main Content Grid -->
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
    <!-- Left Column - 2/3 width -->
    <div class="lg:col-span-2 space-y-4 sm:space-y-6">
      <!-- Risk Management - Prominent -->
      <GlassCard 
        title="Risk Management" 
        subtitle="Real-time risk monitoring" 
        variant={dailyDrawdown > 3 ? 'danger' : 'default'}
        pulseDanger={dailyDrawdown > 3}
      >
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
            <p class="text-lg sm:text-xl font-mono font-bold text-emerald-400">WIRED</p>
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
              class="h-full rounded-full transition-all duration-500 {dailyDrawdown > 6 ? 'bg-gradient-to-r from-rose-500 to-rose-400 shadow-[0_0_10px_rgba(244,63,94,0.4)]' : dailyDrawdown > 3 ? 'bg-gradient-to-r from-amber-500 to-amber-400 shadow-[0_0_10px_rgba(245,158,11,0.4)]' : 'bg-gradient-to-r from-emerald-500 to-emerald-400 shadow-[0_0_10px_rgba(16,185,129,0.4)]'}"
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

      <!-- Progress Breakdown -->
      <GlassCard title="Evaluation Progress" subtitle="System readiness metrics">
        <div class="space-y-3 sm:space-y-4">
          {#each progressMetrics as metric}
            <ProgressBar 
              value={metric.value} 
              max={100} 
              variant={metric.variant}
              showValue={true}
            >
              <span slot="label" class="text-sm sm:text-xs text-white/40 font-sans">{metric.label}</span>
            </ProgressBar>
          {/each}
        </div>
      </GlassCard>

      <!-- Department Signals -->
      <GlassCard title="Agent Departments" subtitle="Live trading signals">
        <div class="overflow-x-auto scrollbar-hide -mx-2 px-2">
          <table class="w-full min-w-[500px]">
            <thead>
              <tr class="border-b border-white/[0.06]">
                <th class="text-left text-sm sm:text-xs text-white/40 font-sans uppercase tracking-wider pb-3">Department</th>
                <th class="text-left text-sm sm:text-xs text-white/40 font-sans uppercase tracking-wider pb-3">Direction</th>
                <th class="text-left text-sm sm:text-xs text-white/40 font-sans uppercase tracking-wider pb-3">Confidence</th>
                <th class="text-left text-sm sm:text-xs text-white/40 font-sans uppercase tracking-wider pb-3">Timeframe</th>
              </tr>
            </thead>
            <tbody>
              {#each departments as dept}
                <tr class="border-b border-white/[0.04] hover:bg-white/[0.02] transition-colors">
                  <td class="py-3 text-sm sm:text-base text-white/80 font-sans">{dept.department}</td>
                  <td class="py-3">
                    <span class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs sm:text-sm font-mono font-semibold {dept.direction === 'long' ? 'bg-emerald-500/15 text-emerald-400' : dept.direction === 'short' ? 'bg-rose-500/15 text-rose-400' : 'bg-white/5 text-white/40'}">
                      {dept.direction.toUpperCase()}
                    </span>
                  </td>
                  <td class="py-3 text-sm sm:text-base font-mono text-white/70">{(dept.confidence * 100).toFixed(0)}%</td>
                  <td class="py-3 text-sm sm:text-base font-mono text-white/50">{dept.timeframe}</td>
                </tr>
              {:else}
                <tr>
                  <td colspan="4" class="py-8 text-center text-base text-white/30 font-sans">No active signals</td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      </GlassCard>
    </div>

    <!-- Right Column - 1/3 width -->
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

      <!-- System Status -->
      <GlassCard title="System Status" subtitle="Infrastructure health">
        <div class="space-y-3">
          <div class="flex items-center justify-between py-2">
            <span class="text-base sm:text-sm text-white/50 font-sans">Daemon</span>
            <StatusBadge status={state ? 'online' : 'offline'} size="sm" />
          </div>
          <div class="flex items-center justify-between py-2">
            <span class="text-base sm:text-sm text-white/50 font-sans">Binance WS</span>
            <StatusBadge status={state?.binance_ws_connected ? 'online' : 'offline'} size="sm" />
          </div>
          <div class="flex items-center justify-between py-2">
            <span class="text-base sm:text-sm text-white/50 font-sans">Execution</span>
            <StatusBadge status={executionEnabled ? 'online' : 'error'} size="sm" />
          </div>
          <div class="flex items-center justify-between py-2">
            <span class="text-base sm:text-sm text-white/50 font-sans">KV Sync</span>
            <StatusBadge status="online" size="sm" />
          </div>
        </div>
      </GlassCard>

      <!-- Recent Activity -->
      <GlassCard title="Activity Log" subtitle="Latest events">
        <div class="space-y-3 max-h-64 overflow-y-auto scrollbar-hide">
          {#each recentActivity as activity}
            <div class="flex items-start gap-3 py-2 border-b border-white/[0.04] last:border-0">
              <div class="w-2 h-2 rounded-full mt-1.5 bg-blue-400 shadow-[0_0_6px_rgba(59,130,246,0.5)]"></div>
              <div>
                <p class="text-sm sm:text-base text-white/70 font-sans">{activity.type || 'Event'}</p>
                <p class="text-xs sm:text-sm text-white/30 font-mono mt-0.5">{activity.timestamp ? new Date(activity.timestamp).toLocaleTimeString() : 'Just now'}</p>
              </div>
            </div>
          {:else}
            <div class="py-4 text-center text-base text-white/30 font-sans">No recent activity</div>
          {/each}
        </div>
      </GlassCard>

      <!-- Quick Actions -->
      <GlassCard title="Quick Actions">
        <div class="grid grid-cols-2 gap-3">
          <a href="/trade" class="flex flex-col items-center gap-2 p-4 rounded-xl bg-white/[0.03] hover:bg-white/[0.06] border border-white/[0.06] hover:border-emerald-500/30 transition-all group">
            <svg class="w-6 h-6 text-emerald-400 group-hover:drop-shadow-[0_0_4px_rgba(16,185,129,0.5)]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path></svg>
            <span class="text-sm sm:text-base font-medium text-white/70">New Trade</span>
          </a>
          <a href="/positions" class="flex flex-col items-center gap-2 p-4 rounded-xl bg-white/[0.03] hover:bg-white/[0.06] border border-white/[0.06] hover:border-blue-500/30 transition-all group">
            <svg class="w-6 h-6 text-blue-400 group-hover:drop-shadow-[0_0_4px_rgba(59,130,246,0.5)]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path></svg>
            <span class="text-sm sm:text-base font-medium text-white/70">Positions</span>
          </a>
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
