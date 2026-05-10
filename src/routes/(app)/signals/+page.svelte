<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import GlassCard from '$lib/components/GlassCard.svelte';
  import { api } from '$lib/api';

  const MARKETS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT'];
  const DEPARTMENTS = ['Quantitative', 'Technical', 'Sentiment', 'Fundamental', 'Statistical', 'Qualitative'];

  let selectedMarket = 'BTCUSDT';
  let departments: any[] = [];
  let lastUpdate: number | null = null;
  let loading = true;
  let pollInterval: ReturnType<typeof setInterval>;

  // Mock signal history for demo (will be replaced by real trade_journal data)
  let signalHistory: { direction: string; timestamp: Date }[] = [];

  onMount(async () => {
    await fetchDepartments();
    pollInterval = setInterval(fetchDepartments, 10000);
  });

  onDestroy(() => {
    if (pollInterval) clearInterval(pollInterval);
  });

  async function fetchDepartments() {
    try {
      const result = await api.getDepartments();
      if (result.departments) {
        departments = result.departments;
      }
      if (result.last_update) {
        lastUpdate = result.last_update;
      }
      loading = false;
    } catch (err) {
      console.error('Failed to fetch departments:', err);
      loading = false;
    }
  }

  function getDepartmentDirection(deptName: string): string {
    const dept = departments.find(
      d => d.name?.toLowerCase() === deptName.toLowerCase()
    );
    return dept?.direction || '—';
  }

  function getDepartmentConfidence(deptName: string): number {
    const dept = departments.find(
      d => d.name?.toLowerCase() === deptName.toLowerCase()
    );
    return dept?.confidence || 0;
  }

  $: overallDirection = (() => {
    const longs = departments.filter(d => d.direction === 'long').length;
    const shorts = departments.filter(d => d.direction === 'short').length;
    if (longs > shorts) return 'Long';
    if (shorts > longs) return 'Short';
    return 'Neutral';
  })();

  $: overallConfidence = (() => {
    const scores = departments.map(d => {
      const weight = d.direction === 'long' ? 1 : d.direction === 'short' ? -1 : 0;
      return weight * (d.confidence || 0);
    });
    if (scores.length === 0) return 0;
    const avg = scores.reduce((a, b) => a + b, 0) / scores.length;
    return Math.abs(avg);
  })();

  $: formattedTime = lastUpdate
    ? new Date(lastUpdate).toLocaleDateString('en-US', {
        month: '2-digit',
        day: '2-digit',
        year: 'numeric',
      }) +
      ' at ' +
      new Date(lastUpdate).toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true,
      })
    : '—';

  function directionColor(dir: string): string {
    if (dir === 'long') return 'text-emerald-400';
    if (dir === 'short') return 'text-rose-400';
    return 'text-zinc-500';
  }

  function directionBg(dir: string): string {
    if (dir === 'long') return 'bg-emerald-500/15';
    if (dir === 'short') return 'bg-rose-500/15';
    return 'bg-zinc-800/50';
  }

  function confidenceBarColor(dir: string): string {
    if (dir === 'long') return 'from-emerald-500 to-emerald-400';
    if (dir === 'short') return 'from-rose-500 to-rose-400';
    return 'from-zinc-500 to-zinc-400';
  }

  $: historyForMarket = signalHistory;
</script>

<div class="space-y-5 max-w-7xl mx-auto pb-20 sm:pb-0">
  <!-- Header with Market Selector -->
  <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
    <div class="flex items-center gap-3">
      <h1 class="text-2xl font-bold text-white/90 font-sans">Signals</h1>
      <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-emerald-500/15 text-emerald-400">LIVE</span>
    </div>
    <div class="flex items-center gap-2">
      <label for="market-select" class="text-sm text-zinc-400 font-sans">Market:</label>
      <select id="market-select"
        class="bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-1.5 text-white text-sm font-mono focus:outline-none focus:border-emerald-500 transition-colors"
        bind:value={selectedMarket}
      >
        {#each MARKETS as market}
          <option value={market}>{market}</option>
        {/each}
      </select>
    </div>
  </div>

  {#if loading}
    <div class="flex items-center justify-center py-16">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-500"></div>
    </div>
  {:else}
    <!-- Department Signal Grid -->
    <GlassCard>
      <div class="p-4 sm:p-6">
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 sm:gap-4">
          {#each DEPARTMENTS as dept}
            {@const direction = getDepartmentDirection(dept)}
            {@const confidence = getDepartmentConfidence(dept)}
            <div class="bg-zinc-800/30 rounded-xl p-3 sm:p-4 border border-zinc-700/30 hover:border-zinc-600/50 transition-colors">
              <div class="text-xs text-zinc-400 font-sans font-medium mb-2 truncate">{dept}</div>
              <div class="text-lg sm:text-xl font-bold font-mono {directionColor(direction)} mb-2">
                {direction === 'long' ? 'LONG' : direction === 'short' ? 'SHORT' : '—'}
              </div>
              <div class="h-1.5 bg-zinc-700/50 rounded-full overflow-hidden">
                <div
                  class="h-full rounded-full bg-gradient-to-r {confidenceBarColor(direction)} transition-all duration-500"
                  style="width: {confidence * 100}%"
                ></div>
              </div>
              <div class="text-xs text-zinc-500 font-mono mt-1">
                {(confidence * 100).toFixed(0)}%
              </div>
            </div>
          {/each}
        </div>
      </div>
    </GlassCard>

    <!-- Overall Bias -->
    <GlassCard>
      <div class="p-4 sm:p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div class="flex items-center gap-3">
          <span class="text-sm text-zinc-400 font-sans">Overall Bias:</span>
          <span class="text-lg sm:text-xl font-bold font-mono {directionColor(overallDirection.toLowerCase())}">
            {overallDirection.toUpperCase()}
          </span>
          <div class="h-6 w-px bg-zinc-700 hidden sm:block"></div>
          <span class="text-sm text-zinc-500 font-sans">{formattedTime}</span>
        </div>
        <div class="flex items-center gap-3">
          <span class="text-xs text-zinc-500 font-sans">Signal Strength</span>
          <div class="w-24 sm:w-32 h-2 bg-zinc-700/50 rounded-full overflow-hidden">
            <div
              class="h-full rounded-full bg-gradient-to-r {overallConfidence > 0.5 ? (overallDirection.toLowerCase() === 'long' ? 'from-emerald-500 to-emerald-400' : 'from-rose-500 to-rose-400') : 'from-zinc-500 to-zinc-400'} transition-all duration-500"
              style="width: {overallConfidence * 100}%"
            ></div>
          </div>
          <span class="text-xs text-zinc-500 font-mono">{(overallConfidence * 100).toFixed(0)}%</span>
        </div>
      </div>
    </GlassCard>

    <!-- Signal History -->
    <GlassCard>
      <div class="p-4 sm:p-6">
        <h2 class="text-sm font-semibold text-zinc-300 font-sans mb-4">Signal History — {selectedMarket}</h2>

        {#if historyForMarket.length > 0}
          <div class="space-y-2">
            {#each historyForMarket as signal}
              <div class="flex items-center gap-3 py-2.5 px-3 rounded-lg bg-zinc-800/20 border border-zinc-800/30">
                <div class="w-2 h-2 rounded-full {signal.direction === 'long' ? 'bg-emerald-400' : 'bg-rose-400'}"></div>
                <span class="text-sm font-mono font-semibold {signal.direction === 'long' ? 'text-emerald-400' : 'text-rose-400'}">
                  {signal.direction === 'long' ? 'LONG' : 'SHORT'}
                </span>
                <span class="text-xs text-zinc-500 font-sans ml-auto">
                  {signal.timestamp.toLocaleDateString('en-US', { month: '2-digit', day: '2-digit', year: 'numeric' })}
                  at {signal.timestamp.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true })}
                </span>
              </div>
            {/each}
          </div>
        {:else}
          <div class="py-6 text-center">
            <p class="text-zinc-500 text-sm font-sans">No signal history yet for this market.</p>
            <p class="text-zinc-600 text-xs font-sans mt-1">Signals will appear here once the department agents start producing verdicts.</p>
          </div>
        {/if}
      </div>
    </GlassCard>

    <!-- Department Details Table -->
    <GlassCard>
      <div class="p-4 sm:p-6">
        <h2 class="text-sm font-semibold text-zinc-300 font-sans mb-4">Department Breakdown</h2>
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="text-xs text-zinc-500 uppercase tracking-wider border-b border-zinc-800">
                <th class="text-left py-2.5 pr-4 font-sans">Department</th>
                <th class="text-left py-2.5 px-4 font-sans">Direction</th>
                <th class="text-left py-2.5 px-4 font-sans">Confidence</th>
                <th class="text-left py-2.5 px-4 font-sans">Timeframe</th>
                <th class="text-left py-2.5 pl-4 font-sans">Last Run</th>
              </tr>
            </thead>
            <tbody>
              {#each DEPARTMENTS as dept}
                {@const deptData = departments.find(d => d.name?.toLowerCase() === dept.toLowerCase())}
                <tr class="border-b border-zinc-800/30 hover:bg-zinc-800/10 transition-colors">
                  <td class="py-3 pr-4 font-sans text-zinc-300">{dept}</td>
                  <td class="py-3 px-4">
                    <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-mono font-semibold {directionBg(deptData?.direction || '')} {directionColor(deptData?.direction || '')}">
                      {(deptData?.direction || '—').toUpperCase()}
                    </span>
                  </td>
                  <td class="py-3 px-4">
                    <div class="flex items-center gap-2">
                      <div class="w-16 h-1.5 bg-zinc-700/50 rounded-full overflow-hidden">
                        <div
                          class="h-full rounded-full bg-gradient-to-r {confidenceBarColor(deptData?.direction || '')} transition-all"
                          style="width: {(deptData?.confidence || 0) * 100}%"
                        ></div>
                      </div>
                      <span class="text-xs font-mono text-zinc-400">{((deptData?.confidence || 0) * 100).toFixed(0)}%</span>
                    </div>
                  </td>
                  <td class="py-3 px-4 font-mono text-xs text-zinc-400">{deptData?.timeframe || '—'}</td>
                  <td class="py-3 pl-4 font-mono text-xs text-zinc-500">{deptData?.lastRun || '—'}</td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      </div>
    </GlassCard>
  {/if}
</div>
