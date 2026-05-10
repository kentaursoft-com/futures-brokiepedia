<script lang="ts">
  import { onMount } from 'svelte';
  import GlassCard from '$lib/components/GlassCard.svelte';
  import StatusBadge from '$lib/components/StatusBadge.svelte';
  import { api } from '$lib/api';

  // ===== State =====
  const MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December'];
  const DAYS = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
  const SYMBOLS = ['','BTCUSDT','ETHUSDT','SOLUSDT','BNBUSDT'];

  let view: 'calendar' | 'trades' | 'notes' = 'calendar';
  let trades: any[] = [];
  let stats: any = {};
  let calendarDays: Record<number, { day: number; pnl: number; trades: number }> = {};
  let calendarSummary: any = {};
  let notes: any[] = [];
  let loading = true;
  let error = '';
function setView(v: string) {
  if (v === 'calendar' || v === 'trades' || v === 'notes') (view as any) = v;
}

  let curMonth = new Date().getMonth() + 1;
  let curYear = new Date().getFullYear();
  let filterSymbol = '';
  let filterDays = 90;
  let tradePage = 1;
  let totalTrades = 0;

  // ===== Load =====
  onMount(async () => {
    await Promise.all([loadCalendar(), loadStats(), loadTrades(), loadNotes()]);
  });

  async function loadCalendar() {
    try {
      const data = await api.getJournalCalendar(curMonth, curYear);
      calendarDays = data.days || {};
      calendarSummary = data.summary || {};
    } catch (e: any) { console.error('Calendar load error:', e); }
  }

  async function loadStats() {
    try {
      stats = await api.getJournalStats();
    } catch (e: any) { console.error('Stats load error:', e); }
  }

  async function loadTrades() {
    try {
      loading = true;
      const data = await api.getJournalTrades({ page: tradePage, limit: 50, symbol: filterSymbol, days: filterDays });
      trades = data.trades || [];
      totalTrades = data.total || 0;
    } catch (e: any) { error = e.message; }
    finally { loading = false; }
  }

  async function loadNotes() {
    try {
      const data = await api.getJournalNotes();
      notes = data.notes || [];
    } catch (e: any) { console.error('Notes load error:', e); }
  }

  async function prevMonth() { curMonth--; if (curMonth < 1) { curMonth = 12; curYear--; } calendarDays = {}; await loadCalendar(); }
  async function nextMonth() { curMonth++; if (curMonth > 12) { curMonth = 1; curYear++; } calendarDays = {}; await loadCalendar(); }

  // ===== Calendar helpers =====
  $: firstDay = new Date(curYear, curMonth - 1, 1).getDay();
  $: daysInMonth = new Date(curYear, curMonth, 0).getDate();
  $: calendarCells = (() => {
    const cells: { day: number; pnl: number; trades: number; isPadding: boolean }[] = [];
    for (let i = 0; i < firstDay; i++) cells.push({ day: 0, pnl: 0, trades: 0, isPadding: true });
    for (let d = 1; d <= daysInMonth; d++) {
      const dayData = calendarDays[d];
      cells.push({
        day: d,
        pnl: dayData?.pnl || 0,
        trades: dayData?.trades || 0,
        isPadding: false,
      });
    }
    return cells;
  })();

  function pnlShort(v: number): string {
    if (v === 0) return '';
    return (v >= 0 ? '+' : '') + v.toFixed(0);
  }

  function pnlColor(v: number): string {
    if (v > 0) return 'text-emerald-400';
    if (v < 0) return 'text-rose-400';
    return 'text-zinc-500';
  }

  function pnlBg(v: number): string {
    if (v > 5) return 'bg-emerald-500/15 border-emerald-500/25';
    if (v > 0) return 'bg-emerald-500/8 border-emerald-500/15';
    if (v < -5) return 'bg-rose-500/15 border-rose-500/25';
    if (v < 0) return 'bg-rose-500/8 border-rose-500/15';
    return 'bg-zinc-800/30 border-zinc-700/20';
  }

  function fmtDate(ts: number): string {
    return new Date(ts).toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
  }
</script>

<div class="space-y-5 max-w-7xl mx-auto pb-20 sm:pb-0">
  <!-- Header -->
  <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
    <div>
      <h1 class="text-2xl font-bold text-white/90 font-sans">Journal</h1>
      <p class="text-zinc-400 text-sm mt-1 font-sans">Trade history, daily P&L, and journal notes</p>
    </div>
    <div class="flex gap-1 p-1 bg-zinc-800/40 rounded-xl border border-zinc-700/20">
      {#each [
        { id: 'calendar', label: 'Calendar' },
        { id: 'trades', label: 'Trades' },
        { id: 'notes', label: 'Notes' },
      ] as tab}
        <button
          class="px-3 py-1.5 rounded-lg text-xs font-medium transition-all {view === tab.id ? 'bg-zinc-700/80 text-white/90' : 'text-zinc-500 hover:text-zinc-300'}"
          on:click={() => setView(tab.id)}
        >{tab.label}</button>
      {/each}
    </div>
  </div>

  <!-- ======================================================================== -->
  <!-- CALENDAR VIEW -->
  <!-- ======================================================================== -->
  {#if view === 'calendar'}
    <!-- Summary mini-cards -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
      <GlassCard className="p-3 sm:p-4">
        <div class="text-xs text-zinc-500 font-sans">Total P&L</div>
        <div class="text-lg font-bold font-mono mt-0.5 {pnlColor(calendarSummary.total_pnl)}">
          {calendarSummary.total_pnl >= 0 ? '+' : ''}{calendarSummary.total_pnl?.toFixed(2) || '0.00'}
        </div>
      </GlassCard>
      <GlassCard className="p-3 sm:p-4">
        <div class="text-xs text-zinc-500 font-sans">Trades</div>
        <div class="text-lg font-bold font-mono mt-0.5 text-white/90">{calendarSummary.total_trades || 0}</div>
      </GlassCard>
      <GlassCard className="p-3 sm:p-4">
        <div class="text-xs text-zinc-500 font-sans">Best Day</div>
        <div class="text-lg font-bold font-mono mt-0.5 text-emerald-400">+${Math.abs(calendarSummary.best_day || 0).toFixed(0)}</div>
      </GlassCard>
      <GlassCard className="p-3 sm:p-4">
        <div class="text-xs text-zinc-500 font-sans">Worst Day</div>
        <div class="text-lg font-bold font-mono mt-0.5 text-rose-400">-${Math.abs(calendarSummary.worst_day || 0).toFixed(0)}</div>
      </GlassCard>
    </div>

    <!-- Calendar -->
    <GlassCard>
      <!-- Month navigation -->
      <div class="flex items-center justify-between mb-4 px-1">
        <button class="p-2 rounded-lg hover:bg-zinc-800 transition-colors text-zinc-400" on:click={prevMonth}>
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
        </button>
        <span class="text-base font-semibold text-white/90 font-sans">{MONTHS[curMonth - 1]} {curYear}</span>
        <button class="p-2 rounded-lg hover:bg-zinc-800 transition-colors text-zinc-400" on:click={nextMonth}>
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
        </button>
      </div>

      <!-- Day headers -->
      <div class="grid grid-cols-7 gap-1 mb-1">
        {#each DAYS as d}
          <div class="text-center text-xs text-zinc-500 font-sans py-1">{d}</div>
        {/each}
      </div>

      <!-- Calendar grid -->
      <div class="grid grid-cols-7 gap-1">
        {#each calendarCells as cell}
          {#if cell.isPadding}
            <div class="aspect-square rounded-lg bg-transparent"></div>
          {:else}
            <div class="aspect-square rounded-lg border p-1 flex flex-col {pnlBg(cell.pnl)} transition-colors hover:border-zinc-500/30 cursor-pointer"
              title="{MONTHS[curMonth - 1]} {cell.day}: {pnlShort(cell.pnl)} ({cell.trades} trades)"
            >
              <span class="text-xs font-mono text-zinc-400">{cell.day}</span>
              {#if cell.pnl !== 0}
                <span class="text-[10px] font-mono font-semibold leading-tight {pnlColor(cell.pnl)} mt-auto">{pnlShort(cell.pnl)}</span>
              {/if}
              {#if cell.trades > 0}
                <span class="text-[8px] text-zinc-600">{cell.trades}t</span>
              {/if}
            </div>
          {/if}
        {/each}
      </div>
    </GlassCard>

    <!-- All-time stats -->
    <GlassCard title="Lifetime Summary" subtitle="Across all time">
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {#each [
          { label: 'Total Trades', value: stats.total_trades, color: 'text-white/90' },
          { label: 'Total P&L', value: `$${stats.total_pnl?.toFixed(2)}`, color: (stats.total_pnl || 0) >= 0 ? 'text-emerald-400' : 'text-rose-400' },
          { label: 'Winning', value: stats.winning_trades, color: 'text-emerald-400' },
          { label: 'Losing', value: stats.losing_trades, color: 'text-rose-400' },
          { label: 'Avg P&L', value: `$${stats.avg_pnl?.toFixed(2)}`, color: (stats.avg_pnl || 0) >= 0 ? 'text-emerald-400' : 'text-rose-400' },
          { label: 'Best Trade', value: `+$${stats.best_trade?.toFixed(2)}`, color: 'text-emerald-400' },
          { label: 'Worst Trade', value: `-$${Math.abs(stats.worst_trade || 0).toFixed(2)}`, color: 'text-rose-400' },
          { label: 'Trading Days', value: stats.trading_days, color: 'text-white/90' },
        ] as stat}
          <div class="bg-zinc-800/30 rounded-xl p-3 border border-zinc-700/20">
            <div class="text-xs text-zinc-500 font-sans">{stat.label}</div>
            <div class="text-sm font-bold font-mono mt-0.5 {stat.color}">{stat.value ?? '—'}</div>
          </div>
        {/each}
      </div>
    </GlassCard>

  <!-- ======================================================================== -->
  <!-- TRADES VIEW -->
  <!-- ======================================================================== -->
  {:else if view === 'trades'}
    <GlassCard title="Trade History" subtitle="{totalTrades} trades recorded">
      <!-- Filters -->
      <div class="flex flex-wrap gap-3 mb-4">
        <select class="bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-1.5 text-white text-xs font-mono focus:outline-none focus:border-emerald-500" bind:value={filterSymbol} on:change={() => { tradePage = 1; loadTrades(); }}>
          <option value="">All Markets</option>
          {#each SYMBOLS.slice(1) as sym}
            <option value={sym}>{sym}</option>
          {/each}
        </select>
        <select class="bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-1.5 text-white text-xs font-mono focus:outline-none focus:border-emerald-500" bind:value={filterDays} on:change={() => { tradePage = 1; loadTrades(); }}>
          <option value={7}>7 days</option>
          <option value={30}>30 days</option>
          <option value={90}>90 days</option>
          <option value={365}>1 year</option>
          <option value={9999}>All time</option>
        </select>
        <button class="px-3 py-1.5 rounded-lg text-xs bg-zinc-800 border border-zinc-700 text-zinc-400 hover:text-zinc-200 transition-colors" on:click={() => { tradePage = 1; loadTrades(); }}>
          Refresh
        </button>
      </div>

      <!-- Table -->
      {#if loading}
        <div class="flex justify-center py-8"><div class="animate-spin w-6 h-6 border-2 border-zinc-500/30 border-t-emerald-400 rounded-full"></div></div>
      {:else if trades.length === 0}
        <div class="py-8 text-center text-zinc-500 text-sm font-sans">No trades in this period</div>
      {:else}
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="text-xs text-zinc-500 uppercase tracking-wider border-b border-zinc-800">
                <th class="text-left py-2 pr-2 font-sans">Date</th>
                <th class="text-left py-2 px-2 font-sans">Symbol</th>
                <th class="text-left py-2 px-2 font-sans">Side</th>
                <th class="text-right py-2 px-2 font-sans">Entry</th>
                <th class="text-right py-2 px-2 font-sans">Exit</th>
                <th class="text-right py-2 px-2 font-sans">Size</th>
                <th class="text-right py-2 px-2 font-sans">P&L</th>
                <th class="text-left py-2 pl-2 font-sans">Exchange</th>
              </tr>
            </thead>
            <tbody>
              {#each trades as t}
                <tr class="border-b border-zinc-800/20 hover:bg-zinc-800/10 transition-colors">
                  <td class="py-2 pr-2 font-mono text-xs text-zinc-500 whitespace-nowrap">{fmtDate(t.created_at)}</td>
                  <td class="py-2 px-2 font-mono text-zinc-200">{t.symbol}</td>
                  <td class="py-2 px-2">
                    <span class="text-xs font-mono font-semibold {t.side === 'long' ? 'text-emerald-400' : 'text-rose-400'}">{t.side?.toUpperCase()}</span>
                  </td>
                  <td class="py-2 px-2 text-right font-mono text-zinc-400">{t.entry_price?.toFixed(2) || '—'}</td>
                  <td class="py-2 px-2 text-right font-mono text-zinc-400">{t.exit_price?.toFixed(2) || '—'}</td>
                  <td class="py-2 px-2 text-right font-mono text-zinc-400">{t.size}</td>
                  <td class="py-2 px-2 text-right font-mono font-semibold {t.pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}">
                    {t.pnl != null ? (t.pnl >= 0 ? '+' : '') + t.pnl.toFixed(2) : '—'}
                  </td>
                  <td class="py-2 pl-2 text-xs text-zinc-500 font-sans">{t.exchange}</td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      {/if}
    </GlassCard>

  <!-- ======================================================================== -->
  <!-- NOTES VIEW -->
  <!-- ======================================================================== -->
  {:else if view === 'notes'}
    <GlassCard title="Journal Notes" subtitle="Agent-authored trade reflections">
      {#if notes.length === 0}
        <div class="py-8 text-center text-zinc-500 text-sm font-sans">No journal notes yet. Your Journaling agent will write here.</div>
      {:else}
        <div class="space-y-3">
          {#each notes as note}
            <div class="bg-zinc-800/30 rounded-xl p-4 border border-zinc-700/20">
              <div class="flex items-start justify-between gap-3">
                <div class="flex-1">
                  <p class="text-sm text-zinc-200 font-sans whitespace-pre-wrap">{note.content}</p>
                  {#if note.trade}
                    <div class="flex items-center gap-2 mt-2 text-xs">
                      <span class="text-zinc-500 font-mono">{note.trade.symbol}</span>
                      <span class="font-mono {note.trade.side === 'long' ? 'text-emerald-400' : 'text-rose-400'}">{note.trade.side?.toUpperCase()}</span>
                      <span class="font-mono {note.trade.pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}">{note.trade.pnl >= 0 ? '+' : ''}{note.trade.pnl?.toFixed(2)}</span>
                    </div>
                  {/if}
                </div>
                <div class="text-xs text-zinc-600 font-mono whitespace-nowrap">{fmtDate(note.created_at)}</div>
              </div>
              {#if note.tags?.length}
                <div class="flex gap-1.5 mt-2">
                  {#each note.tags as tag}
                    <span class="text-[10px] px-1.5 py-0.5 rounded bg-zinc-700/40 text-zinc-400">{tag}</span>
                  {/each}
                </div>
              {/if}
            </div>
          {/each}
        </div>
      {/if}
    </GlassCard>
  {/if}
</div>
