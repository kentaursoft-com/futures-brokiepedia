<script lang="ts">
	import { api } from '../api';
	import type { Trade } from '../types';

	let trades: Trade[] = [];
	let loading = true;
	let error: string | null = null;

	let filterSymbol = 'all';
	let filterSide = 'all';
	let filterPaper = 'all';
	let sortBy: 'date' | 'pnl' = 'date';
	let sortDesc = true;

	async function loadTrades() {
		loading = true;
		error = null;
		try {
			const data = await api.getPaperTradeHistory();
			trades = data.trades || [];
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load trades';
			trades = [];
		}
		loading = false;
	}

	$: filteredTrades = trades.filter(t => {
		if (filterSymbol !== 'all' && t.symbol !== filterSymbol) return false;
		if (filterSide !== 'all' && t.side !== filterSide) return false;
		if (filterPaper !== 'all') {
			const isPaper = filterPaper === 'paper';
			if (t.paper !== isPaper) return false;
		}
		return true;
	}).sort((a, b) => {
		if (sortBy === 'date') {
			return sortDesc ? b.created_at - a.created_at : a.created_at - b.created_at;
		}
		return sortDesc ? (b.pnl || 0) - (a.pnl || 0) : (a.pnl || 0) - (b.pnl || 0);
	});

	$: stats = {
		total: filteredTrades.length,
		wins: filteredTrades.filter(t => (t.pnl || 0) > 0).length,
		losses: filteredTrades.filter(t => (t.pnl || 0) < 0).length,
		netPnl: filteredTrades.reduce((sum, t) => sum + (t.pnl || 0), 0),
		avgWin: filteredTrades.filter(t => (t.pnl || 0) > 0).reduce((sum, t) => sum + (t.pnl || 0), 0) / Math.max(filteredTrades.filter(t => (t.pnl || 0) > 0).length, 1),
		avgLoss: filteredTrades.filter(t => (t.pnl || 0) < 0).reduce((sum, t) => sum + (t.pnl || 0), 0) / Math.max(filteredTrades.filter(t => (t.pnl || 0) < 0).length, 1)
	};

	function formatDate(ts: number) {
		return new Date(ts).toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
	}

	$: symbols = ['all', ...new Set(trades.map(t => t.symbol))];

	import { onMount } from 'svelte';
	onMount(loadTrades);
</script>

<div class="rounded-lg border bg-card p-4">
	<div class="flex items-center justify-between mb-4">
		<h2 class="text-sm font-semibold">Trade History</h2>
		<div class="flex items-center gap-4">
			{#if loading}
				<span class="text-xs text-muted-foreground">Loading...</span>
			{:else if error}
				<div class="flex items-center gap-2">
					<span class="text-xs text-red-400">{error}</span>
					<button on:click={loadTrades} class="text-xs text-primary hover:underline">Retry</button>
				</div>
			{:else}
				<div class="flex items-center gap-4 text-xs">
					<div class="flex items-center gap-1">
						<span class="text-muted-foreground">Win Rate:</span>
						<span class="font-semibold {stats.wins / Math.max(stats.total, 1) >= 0.55 ? 'text-emerald-400' : 'text-amber-400'}">
							{stats.total > 0 ? ((stats.wins / stats.total) * 100).toFixed(1) : 0}%
						</span>
					</div>
					<div class="flex items-center gap-1">
						<span class="text-muted-foreground">Net P&L:</span>
						<span class="font-semibold {stats.netPnl >= 0 ? 'text-emerald-400' : 'text-red-400'}">
							{stats.netPnl >= 0 ? '+' : ''}${stats.netPnl.toFixed(2)}
						</span>
					</div>
				</div>
			{/if}
		</div>
	</div>
	
	{#if !loading && !error}
		<div class="flex flex-wrap gap-2 mb-4">
			<select bind:value={filterSymbol} class="rounded-md bg-secondary px-2 py-1 text-xs text-secondary-foreground border-0">
				<option value="all">All Symbols</option>
				{#each symbols.slice(1) as sym}
					<option value={sym}>{sym}</option>
				{/each}
			</select>
			
			<select bind:value={filterSide} class="rounded-md bg-secondary px-2 py-1 text-xs text-secondary-foreground border-0">
				<option value="all">All Sides</option>
				<option value="long">Long</option>
				<option value="short">Short</option>
			</select>
			
			<select bind:value={filterPaper} class="rounded-md bg-secondary px-2 py-1 text-xs text-secondary-foreground border-0">
				<option value="all">All Trades</option>
				<option value="live">Live Only</option>
				<option value="paper">Paper Only</option>
			</select>
			
			<button 
				class="rounded-md bg-secondary px-2 py-1 text-xs text-secondary-foreground hover:bg-secondary/80 transition-colors"
				on:click={() => { sortBy = sortBy === 'date' ? 'pnl' : 'date'; sortDesc = true; }}
			>
				Sort: {sortBy === 'date' ? 'Date' : 'P&L'} {sortDesc ? '↓' : '↑'}
			</button>
		</div>
		
		<div class="grid grid-cols-5 gap-2 mb-4 text-center">
			<div class="rounded bg-secondary/50 p-2">
				<p class="text-xs text-muted-foreground">Total</p>
				<p class="text-sm font-semibold">{stats.total}</p>
			</div>
			<div class="rounded bg-secondary/50 p-2">
				<p class="text-xs text-muted-foreground">Wins</p>
				<p class="text-sm font-semibold text-emerald-400">{stats.wins}</p>
			</div>
			<div class="rounded bg-secondary/50 p-2">
				<p class="text-xs text-muted-foreground">Losses</p>
				<p class="text-sm font-semibold text-red-400">{stats.losses}</p>
			</div>
			<div class="rounded bg-secondary/50 p-2">
				<p class="text-xs text-muted-foreground">Avg Win</p>
				<p class="text-sm font-semibold text-emerald-400">+${stats.avgWin.toFixed(2)}</p>
			</div>
			<div class="rounded bg-secondary/50 p-2">
				<p class="text-xs text-muted-foreground">Avg Loss</p>
				<p class="text-sm font-semibold text-red-400">${stats.avgLoss.toFixed(2)}</p>
			</div>
		</div>
	{/if}

	{#if loading}
		<div class="text-center py-8">
			<div class="inline-block w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
			<p class="text-xs text-muted-foreground mt-2">Loading trades...</p>
		</div>
	{:else if error}
		<div class="text-center py-8">
			<p class="text-sm text-red-400">{error}</p>
			<button on:click={loadTrades} class="mt-2 text-xs text-primary hover:underline">Retry</button>
		</div>
	{:else if filteredTrades.length === 0}
		<div class="text-center py-8">
			<p class="text-sm text-muted-foreground">No trades found</p>
			<p class="text-xs text-muted-foreground mt-1">Execute a paper trade to see history here</p>
		</div>
	{:else}
		<div class="overflow-x-auto">
			<table class="w-full text-sm">
				<thead>
					<tr class="border-b text-muted-foreground text-xs">
						<th class="pb-2 text-left font-medium">Date</th>
						<th class="pb-2 text-left font-medium">Symbol</th>
						<th class="pb-2 text-left font-medium">Side</th>
						<th class="pb-2 text-right font-medium">Entry</th>
						<th class="pb-2 text-right font-medium">Exit</th>
						<th class="pb-2 text-right font-medium">Size</th>
						<th class="pb-2 text-right font-medium">P&L</th>
						<th class="pb-2 text-center font-medium">Type</th>
					</tr>
				</thead>
				<tbody>
					{#each filteredTrades as trade}
						<tr class="border-b border-border/50 hover:bg-secondary/30 transition-colors">
							<td class="py-2 text-xs text-muted-foreground">{formatDate(trade.created_at)}</td>
							<td class="py-2 font-medium">{trade.symbol}</td>
							<td class="py-2">
								<span class="rounded px-1.5 py-0.5 text-xs {trade.side === 'long' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}">
									{trade.side.toUpperCase()}
								</span>
							</td>
							<td class="py-2 text-right">${trade.entry_price.toLocaleString()}</td>
							<td class="py-2 text-right">${trade.exit_price?.toLocaleString() || '-'}</td>
							<td class="py-2 text-right">{trade.size}</td>
							<td class="py-2 text-right font-medium {(trade.pnl || 0) >= 0 ? 'text-emerald-400' : 'text-red-400'}">
								{(trade.pnl || 0) >= 0 ? '+' : ''}${trade.pnl?.toFixed(2)}
							</td>
							<td class="py-2 text-center">
								<span class="rounded px-1.5 py-0.5 text-xs {trade.paper ? 'bg-amber-500/20 text-amber-400' : 'bg-blue-500/20 text-blue-400'}">
									{trade.paper ? 'Paper' : 'Live'}
								</span>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</div>
