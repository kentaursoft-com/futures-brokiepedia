<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { api } from '$lib/api';
	import { toast } from '$lib/toast';
	
	interface PaperTrade {
		id: string;
		symbol: string;
		side: 'long' | 'short';
		size: number;
		entry_price: number;
		mark_price?: number;
		unrealized_pnl?: number;
		unrealized_pct?: number;
		created_at: number;
	}
	
	interface BalanceInfo {
		balance: number;
		initial_balance: number;
		total_pnl: number;
		unrealized_pnl: number;
		open_positions: number;
		total_trades: number;
		winning_trades: number;
		win_rate: number;
	}
	
	let balance: BalanceInfo = {
		balance: 10000,
		initial_balance: 10000,
		total_pnl: 0,
		unrealized_pnl: 0,
		open_positions: 0,
		total_trades: 0,
		winning_trades: 0,
		win_rate: 0
	};
	
	let positions: PaperTrade[] = [];
	let prices: Record<string, { price: number; change24h: number }> = {};
	let loading = false;
	let pollInterval: ReturnType<typeof setInterval>;
	
	// Form state
	let newSymbol = 'BTC-PERP';
	let newSide: 'long' | 'short' = 'long';
	let newSize = 0.1;
	let newLeverage = 1;
	
	async function loadData() {
		try {
			const [balanceData, positionsData, pricesData] = await Promise.all([
				api.getPaperBalance(),
				api.getPaperPositions(),
				api.getPaperTradingPrices()
			]);
			
			balance = balanceData;
			positions = positionsData.positions || [];
			prices = pricesData.prices || {};
		} catch (err) {
			console.error("Paper trading load error:", err);
		}
	}
	
	async function openTrade() {
		loading = true;
		try {
			const result = await api.executePaperTrade(newSymbol, newSide, newSize, newLeverage);
			toast.success(`Opened ${newSide} ${newSize} ${newSymbol} @ $${result.entry_price?.toFixed(2) || 'N/A'}`);
			await loadData();
		} catch (err: any) {
			toast.error(err.message || "Failed to open trade");
		} finally {
			loading = false;
		}
	}
	
	async function closeTrade(tradeId: string) {
		loading = true;
		try {
			// Get current price for the symbol
			const trade = positions.find(p => p.id === tradeId);
			if (!trade) return;
			
			const symbolClean = trade.symbol.replace('-PERP', 'USDT');
			const currentPrice = prices[symbolClean]?.price || trade.entry_price;
			
			const result = await api.closePaperTrade(tradeId, currentPrice);
			const pnlText = result.pnl >= 0 ? `+$${result.pnl.toFixed(2)}` : `-$${Math.abs(result.pnl).toFixed(2)}`;
			toast.success(`Closed ${trade.side} ${trade.symbol} with P&L: ${pnlText}`);
			await loadData();
		} catch (err: any) {
			toast.error(err.message || "Failed to close trade");
		} finally {
			loading = false;
		}
	}
	
	function formatTime(timestamp: number): string {
		return new Date(timestamp).toLocaleTimeString();
	}
	
	function getPrice(symbol: string): number {
		const clean = symbol.replace('-PERP', 'USDT');
		return prices[clean]?.price || 0;
	}
	
	onMount(() => {
		loadData();
		pollInterval = setInterval(loadData, 5000); // Refresh every 5 seconds
	});
	
	onDestroy(() => {
		if (pollInterval) clearInterval(pollInterval);
	});
</script>

<div class="rounded-lg border bg-card p-4">
	<div class="flex items-center justify-between mb-4">
		<div>
			<h2 class="text-sm font-semibold">Paper Trading</h2>
			<p class="text-xs text-muted-foreground">Practice without real money</p>
		</div>
		<div class="text-right">
			<p class="text-xs text-muted-foreground">Balance</p>
			<p class="text-xl font-bold">${balance.balance.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</p>
			<p class="text-xs {balance.total_pnl >= 0 ? 'text-emerald-400' : 'text-red-400'}">
				{balance.total_pnl >= 0 ? '+' : ''}${balance.total_pnl.toFixed(2)} total
			</p>
		</div>
	</div>
	
	<!-- Quick Trade Form -->
	<div class="grid grid-cols-5 gap-2 mb-4">
		<select bind:value={newSymbol} class="rounded bg-secondary px-2 py-1 text-xs border-0">
			<option value="BTC-PERP">BTC-PERP</option>
			<option value="ETH-PERP">ETH-PERP</option>
			<option value="SOL-PERP">SOL-PERP</option>
			<option value="BNB-PERP">BNB-PERP</option>
			<option value="XRP-PERP">XRP-PERP</option>
		</select>
		<select bind:value={newSide} class="rounded bg-secondary px-2 py-1 text-xs border-0">
			<option value="long">Long</option>
			<option value="short">Short</option>
		</select>
		<input type="number" bind:value={newSize} step="0.01" min="0.001" placeholder="Size" class="rounded bg-secondary px-2 py-1 text-xs border-0" />
		<input type="number" bind:value={newLeverage} step="1" min="1" max="125" placeholder="Leverage" class="rounded bg-secondary px-2 py-1 text-xs border-0" />
		<button 
			on:click={openTrade}
			disabled={loading}
			class="rounded bg-primary px-3 py-1 text-xs font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
		>
			{loading ? '...' : 'Open Trade'}
		</button>
	</div>
	
	<!-- Open Positions -->
	<div class="mb-4">
		<p class="text-xs font-medium mb-2">Open Positions ({balance.open_positions})</p>
		{#if positions.length === 0}
			<p class="text-xs text-muted-foreground">No open paper positions</p>
		{:else}
			<div class="space-y-1">
				{#each positions as trade}
					<div class="flex items-center justify-between rounded bg-secondary/50 px-3 py-2">
						<div class="flex items-center gap-2">
							<span class="text-xs rounded px-1.5 py-0.5 {trade.side === 'long' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}">
								{trade.side.toUpperCase()}
							</span>
							<span class="text-sm">{trade.symbol}</span>
							<span class="text-xs text-muted-foreground">{trade.size} @ ${trade.entry_price?.toLocaleString(undefined, {maximumFractionDigits: 2})}</span>
							{#if trade.unrealized_pnl !== undefined}
								<span class="text-xs {trade.unrealized_pnl >= 0 ? 'text-emerald-400' : 'text-red-400'}">
									{trade.unrealized_pnl >= 0 ? '+' : ''}${trade.unrealized_pnl.toFixed(2)} ({trade.unrealized_pct}%)
								</span>
							{/if}
						</div>
						<button 
							on:click={() => closeTrade(trade.id)}
							disabled={loading}
							class="rounded bg-destructive/20 px-2 py-0.5 text-xs text-destructive hover:bg-destructive/30 disabled:opacity-50"
						>
							Close
						</button>
					</div>
				{/each}
			</div>
		{/if}
	</div>
	
	<!-- Stats -->
	<div class="grid grid-cols-4 gap-2 text-center">
		<div class="rounded bg-secondary/50 p-2">
			<p class="text-xs text-muted-foreground">Total Trades</p>
			<p class="text-sm font-semibold">{balance.total_trades}</p>
		</div>
		<div class="rounded bg-secondary/50 p-2">
			<p class="text-xs text-muted-foreground">Win Rate</p>
			<p class="text-sm font-semibold">{balance.win_rate.toFixed(1)}%</p>
		</div>
		<div class="rounded bg-secondary/50 p-2">
			<p class="text-xs text-muted-foreground">Open P&L</p>
			<p class="text-sm font-semibold {balance.unrealized_pnl >= 0 ? 'text-emerald-400' : 'text-red-400'}">
				{balance.unrealized_pnl >= 0 ? '+' : ''}${balance.unrealized_pnl.toFixed(2)}
			</p>
		</div>
		<div class="rounded bg-secondary/50 p-2">
			<p class="text-xs text-muted-foreground">Wins/Losses</p>
			<p class="text-sm font-semibold">{balance.winning_trades}/{balance.total_trades - balance.winning_trades}</p>
		</div>
	</div>
</div>