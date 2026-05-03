<script lang="ts">
	import { writable } from 'svelte/store';
	
	interface PaperTrade {
		id: string;
		symbol: string;
		side: 'long' | 'short';
		size: number;
		entryPrice: number;
		exitPrice?: number;
		pnl?: number;
		status: 'open' | 'closed';
		createdAt: number;
	}
	
	const paperBalance = writable(10000);
	const paperTrades = writable<PaperTrade[]>([
		{ id: '1', symbol: 'BTC-PERP', side: 'long', size: 0.1, entryPrice: 43200, status: 'open', createdAt: Date.now() - 3600000 },
		{ id: '2', symbol: 'ETH-PERP', side: 'short', size: 0.5, entryPrice: 2580, exitPrice: 2550, pnl: 15, status: 'closed', createdAt: Date.now() - 7200000 }
	]);
	
	let newSymbol = 'BTC-PERP';
	let newSide: 'long' | 'short' = 'long';
	let newSize = 0.1;
	let newPrice = 43400;
	
	function openPaperTrade() {
		paperTrades.update(trades => [...trades, {
			id: crypto.randomUUID(),
			symbol: newSymbol,
			side: newSide,
			size: newSize,
			entryPrice: newPrice,
			status: 'open',
			createdAt: Date.now()
		}]);
	}
	
	function closePaperTrade(id: string, exitPrice: number) {
		paperTrades.update(trades => trades.map(t => {
			if (t.id === id && t.status === 'open') {
				const pnl = t.side === 'long' 
					? (exitPrice - t.entryPrice) * t.size
					: (t.entryPrice - exitPrice) * t.size;
				paperBalance.update(b => b + pnl);
				return { ...t, exitPrice, pnl, status: 'closed' as const };
			}
			return t;
		}));
	}
	
	$: openPositions = $paperTrades.filter(t => t.status === 'open');
	$: closedTrades = $paperTrades.filter(t => t.status === 'closed');
	$: winRate = closedTrades.length > 0 
		? (closedTrades.filter(t => (t.pnl || 0) > 0).length / closedTrades.length * 100).toFixed(1)
		: '0';
</script>

<div class="rounded-lg border bg-card p-4">
	<div class="flex items-center justify-between mb-4">
		<div>
			<h2 class="text-sm font-semibold">Paper Trading</h2>
			<p class="text-xs text-muted-foreground">Practice without real money</p>
		</div>
		<div class="text-right">
			<p class="text-xs text-muted-foreground">Balance</p>
			<p class="text-xl font-bold ${$paperBalance.toLocaleString()}">${$paperBalance.toLocaleString()}</p>
		</div>
	</div>
	
	<!-- Quick Trade Form -->
	<div class="grid grid-cols-4 gap-2 mb-4">
		<select bind:value={newSymbol} class="rounded bg-secondary px-2 py-1 text-xs border-0">
			<option value="BTC-PERP">BTC-PERP</option>
			<option value="ETH-PERP">ETH-PERP</option>
			<option value="SOL-PERP">SOL-PERP</option>
		</select>
		<select bind:value={newSide} class="rounded bg-secondary px-2 py-1 text-xs border-0">
			<option value="long">Long</option>
			<option value="short">Short</option>
		</select>
		<input type="number" bind:value={newSize} step="0.01" placeholder="Size" class="rounded bg-secondary px-2 py-1 text-xs border-0" />
		<button 
			on:click={openPaperTrade}
			class="rounded bg-primary px-3 py-1 text-xs font-medium text-primary-foreground hover:bg-primary/90"
		>
			Open Trade
		</button>
	</div>
	
	<!-- Open Positions -->
	<div class="mb-4">
		<p class="text-xs font-medium mb-2">Open Positions ({openPositions.length})</p>
		{#if openPositions.length === 0}
			<p class="text-xs text-muted-foreground">No open paper positions</p>
		{:else}
			<div class="space-y-1">
				{#each openPositions as trade}
					<div class="flex items-center justify-between rounded bg-secondary/50 px-3 py-2">
						<div class="flex items-center gap-2">
							<span class="text-xs rounded px-1.5 py-0.5 {trade.side === 'long' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}">
								{trade.side.toUpperCase()}
							</span>
							<span class="text-sm">{trade.symbol}</span>
							<span class="text-xs text-muted-foreground">{trade.size} @ ${trade.entryPrice.toLocaleString()}</span>
						</div>
						<button 
							on:click={() => closePaperTrade(trade.id, newPrice)}
							class="rounded bg-destructive/20 px-2 py-0.5 text-xs text-destructive hover:bg-destructive/30"
						>
							Close
						</button>
					</div>
				{/each}
			</div>
		{/if}
	</div>
	
	<!-- Stats -->
	<div class="grid grid-cols-3 gap-2 text-center">
		<div class="rounded bg-secondary/50 p-2">
			<p class="text-xs text-muted-foreground">Total Trades</p>
			<p class="text-sm font-semibold">{$paperTrades.length}</p>
		</div>
		<div class="rounded bg-secondary/50 p-2">
			<p class="text-xs text-muted-foreground">Win Rate</p>
			<p class="text-sm font-semibold">{winRate}%</p>
		</div>
		<div class="rounded bg-secondary/50 p-2">
			<p class="text-xs text-muted-foreground">Open P&L</p>
			<p class="text-sm font-semibold text-emerald-400">+$0.00</p>
		</div>
	</div>
</div>
