<script lang="ts">
	import { onDestroy } from 'svelte';
	import TradingChart from '$lib/components/TradingChart.svelte';
	import IndicatorsPanel from '$lib/components/IndicatorsPanel.svelte';
	import OrderBook from '$lib/components/OrderBook.svelte';
	import EquityChart from '$lib/components/EquityChart.svelte';
	import TradeHistory from '$lib/components/TradeHistory.svelte';
	import TimeframeSelector from '$lib/components/TimeframeSelector.svelte';
	import { binanceWS } from '$lib/websocket';
	
	let wsConnected = false;
	let lastPrice = 0;
	let priceChange = 0;
	
	const unsubscribe = binanceWS.subscribe(state => {
		wsConnected = state.connected;
		if (state.lastPrice !== lastPrice) {
			priceChange = state.lastPrice - lastPrice;
			lastPrice = state.lastPrice;
		}
	});
	
	let systemStatus = 'paper';
	let activeAsset = 'BTC-PERP';
	let regime = 'trending_up';
	let lastSync = new Date().toISOString();
	
	let todayPnl = 124.50;
	let unrealizedPnl = -45.20;
	let equity = 10500.00;
	let dailyDrawdown = 1.2;
	
	const departments = [
		{ name: 'Fundamental', confidence: 0.72, direction: 'long', lastRun: '14:30:00' },
		{ name: 'Technical', confidence: 0.85, direction: 'long', lastRun: '14:30:00' },
		{ name: 'Sentiment', confidence: 0.61, direction: 'flat', lastRun: '14:30:00' },
		{ name: 'Quantitative', confidence: 0.78, direction: 'long', lastRun: '14:30:00' },
		{ name: 'Statistical', confidence: 0.55, direction: 'short', lastRun: '14:30:00' },
		{ name: 'Qualitative', confidence: 0.90, direction: 'long', lastRun: '14:30:00' }
	];
	
	const positions = [
		{ symbol: 'BTC-PERP', side: 'long', size: 0.15, entry: 43250.00, mark: 43400.00, pnl: 22.50, exchange: 'Binance', strategy: 'EMA-Trend-v1' }
	];
	
	$: health = {
		vps: true,
		binance: wsConnected,
		deepseek: true,
		turso: true,
		exchanges: 8
	};
	
	function triggerKillSwitch() {
		if (confirm('⚠️ CONFIRM KILL-SWITCH: This will close ALL positions and halt trading. Continue?')) {
			alert('Kill-switch triggered (demo)');
		}
	}
	
	function getStatusColor(status: string) {
		return status === 'live' ? 'bg-emerald-500' : status === 'paper' ? 'bg-amber-500' : 'bg-red-500';
	}
	
	function getStatusText(status: string) {
		return status === 'live' ? 'LIVE' : status === 'paper' ? 'PAPER' : 'HALTED';
	}
	
	function getDirectionColor(dir: string) {
		return dir === 'long' ? 'text-emerald-400' : dir === 'short' ? 'text-red-400' : 'text-slate-400';
	}
	
	function onTimeframeChange(tf: string) {
		console.log('Timeframe changed to:', tf);
		// Will be implemented with multi-timeframe support
	}
	
	onDestroy(() => {
		unsubscribe();
		binanceWS.disconnect();
	});
</script>

<!-- Top Bar -->
<header class="border-b border-border bg-card px-6 py-3">
	<div class="flex items-center justify-between">
		<div class="flex items-center gap-4">
			<h1 class="text-xl font-bold tracking-tight">Futures Brokiepedia</h1>
			<span class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium {getStatusColor(systemStatus)} text-white">
				<span class="h-1.5 w-1.5 rounded-full bg-white"></span>
				{getStatusText(systemStatus)}
			</span>
			<div class="flex items-center gap-2">
				<span class="text-sm font-medium">{activeAsset}</span>
				{#if lastPrice > 0}
					<span class="text-sm {priceChange >= 0 ? 'text-emerald-400' : 'text-red-400'}">
						${lastPrice.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
						{#if priceChange !== 0}
							<span class="text-xs">({priceChange >= 0 ? '+' : ''}{priceChange.toFixed(2)})</span>
						{/if}
					</span>
				{/if}
			</div>
			<span class="rounded-md bg-secondary px-2 py-0.5 text-xs text-secondary-foreground">{regime}</span>
		</div>
		
		<div class="flex items-center gap-4">
			<div class="flex items-center gap-2">
				<span class="h-2 w-2 rounded-full {wsConnected ? 'bg-emerald-500' : 'bg-red-500'}"></span>
				<span class="text-xs text-muted-foreground">{wsConnected ? 'Live Feed' : 'Reconnecting...'}</span>
			</div>
			<span class="text-xs text-muted-foreground">Last sync: {lastSync}</span>
			<button 
				on:click={triggerKillSwitch}
				class="rounded-md bg-destructive px-4 py-1.5 text-sm font-medium text-destructive-foreground hover:bg-destructive/90 transition-colors"
			>
				🛑 Kill Switch
			</button>
		</div>
	</div>
</header>

<!-- Main Dashboard -->
<main class="container mx-auto p-6 space-y-6">
	<!-- Metric Cards -->
	<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
		<div class="rounded-lg border bg-card p-4">
			<p class="text-xs text-muted-foreground uppercase tracking-wider">Today P&L</p>
			<p class="text-2xl font-bold {todayPnl >= 0 ? 'text-emerald-400' : 'text-red-400'}">
				{todayPnl >= 0 ? '+' : ''}${todayPnl.toFixed(2)}
			</p>
		</div>
		
		<div class="rounded-lg border bg-card p-4">
			<p class="text-xs text-muted-foreground uppercase tracking-wider">Unrealized P&L</p>
			<p class="text-2xl font-bold {unrealizedPnl >= 0 ? 'text-emerald-400' : 'text-red-400'}">
				{unrealizedPnl >= 0 ? '+' : ''}${unrealizedPnl.toFixed(2)}
			</p>
		</div>
		
		<div class="rounded-lg border bg-card p-4">
			<p class="text-xs text-muted-foreground uppercase tracking-wider">Account Equity</p>
			<p class="text-2xl font-bold">${equity.toLocaleString('en-US', { minimumFractionDigits: 2 })}</p>
		</div>
		
		<div class="rounded-lg border bg-card p-4">
			<p class="text-xs text-muted-foreground uppercase tracking-wider">Daily Drawdown</p>
			<div class="flex items-center gap-2">
				<p class="text-2xl font-bold {dailyDrawdown >= 6 ? 'text-red-500' : dailyDrawdown >= 3 ? 'text-amber-500' : 'text-emerald-400'}">
					{dailyDrawdown.toFixed(2)}%
				</p>
				<span class="text-xs text-muted-foreground">
					({dailyDrawdown >= 3 ? '⚠️ Soft' : 'Safe'} / Hard: 6%)
				</span>
			</div>
			<div class="mt-2 h-1.5 w-full rounded-full bg-secondary">
				<div 
					class="h-full rounded-full transition-all {dailyDrawdown >= 6 ? 'bg-red-500' : dailyDrawdown >= 3 ? 'bg-amber-500' : 'bg-emerald-400'}"
					style="width: {Math.min((dailyDrawdown / 6) * 100, 100)}%"
				></div>
			</div>
		</div>
	</div>
	
	<!-- Chart + Order Book Row -->
	<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
		<!-- Chart Panel -->
		<div class="lg:col-span-2 rounded-lg border bg-card p-4">
			<div class="flex items-center justify-between mb-4">
				<h2 class="text-sm font-semibold">Chart — {activeAsset}</h2>
				<TimeframeSelector on:change={(e) => onTimeframeChange(e.detail)} />
			</div>
			<div class="h-[400px] rounded-md">
				<TradingChart />
			</div>
			<!-- Technical Indicators -->
			<div class="mt-4">
				<IndicatorsPanel height={100} />
			</div>
		</div>
		
		<!-- Side Panel: Order Book + Agent Departments -->
		<div class="space-y-6">
			<OrderBook />
			
			<div class="rounded-lg border bg-card p-4">
				<h2 class="text-sm font-semibold mb-4">Agent Departments</h2>
				<div class="space-y-3">
					{#each departments as dept}
						<div class="flex items-center justify-between rounded-md bg-secondary/50 px-3 py-2">
							<div>
								<p class="text-sm font-medium">{dept.name}</p>
								<p class="text-xs text-muted-foreground">{dept.lastRun}</p>
							</div>
							<div class="text-right">
								<p class="text-sm font-bold {getDirectionColor(dept.direction)}">{dept.direction.toUpperCase()}</p>
								<div class="mt-1 h-1 w-16 rounded-full bg-secondary">
									<div 
										class="h-full rounded-full bg-primary transition-all"
										style="width: {dept.confidence * 100}%"
									></div>
								</div>
							</div>
						</div>
					{/each}
				</div>
			</div>
		</div>
	</div>
	
	<!-- Equity Curve -->
	<div class="rounded-lg border bg-card p-4">
		<div class="flex items-center justify-between mb-4">
			<h2 class="text-sm font-semibold">Equity Curve & Drawdown</h2>
			<div class="flex items-center gap-4 text-xs">
				<div class="flex items-center gap-1">
					<span class="h-2 w-2 rounded-full bg-blue-500"></span>
					<span class="text-muted-foreground">Equity</span>
				</div>
				<div class="flex items-center gap-1">
					<span class="h-2 w-2 rounded-full bg-red-500"></span>
					<span class="text-muted-foreground">Drawdown %</span>
				</div>
			</div>
		</div>
		<div class="h-[200px]">
			<EquityChart />
		</div>
	</div>
	
	<!-- Positions & Strategy Row -->
	<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
		<!-- Open Positions -->
		<div class="rounded-lg border bg-card p-4">
			<h2 class="text-sm font-semibold mb-4">Open Positions ({positions.length})</h2>
			{#if positions.length === 0}
				<p class="text-sm text-muted-foreground">No open positions</p>
			{:else}
				<div class="overflow-x-auto">
					<table class="w-full text-sm">
						<thead>
							<tr class="border-b text-muted-foreground">
								<th class="pb-2 text-left font-medium">Symbol</th>
								<th class="pb-2 text-left font-medium">Side</th>
								<th class="pb-2 text-left font-medium">Size</th>
								<th class="pb-2 text-left font-medium">Entry</th>
								<th class="pb-2 text-left font-medium">Mark</th>
								<th class="pb-2 text-left font-medium">P&L</th>
								<th class="pb-2 text-left font-medium">Exchange</th>
								<th class="pb-2 text-left font-medium">Strategy</th>
							</tr>
						</thead>
						<tbody>
							{#each positions as pos}
								<tr class="border-b border-border/50">
									<td class="py-2 font-medium">{pos.symbol}</td>
									<td class="py-2">
										<span class="rounded px-1.5 py-0.5 text-xs {pos.side === 'long' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}">
											{pos.side.toUpperCase()}
										</span>
									</td>
									<td class="py-2">{pos.size}</td>
									<td class="py-2">${pos.entry.toLocaleString()}</td>
									<td class="py-2">${pos.mark.toLocaleString()}</td>
									<td class="py-2 {pos.pnl >= 0 ? 'text-emerald-400' : 'text-red-400'}">
										{pos.pnl >= 0 ? '+' : ''}${pos.pnl.toFixed(2)}
									</td>
									<td class="py-2 text-muted-foreground">{pos.exchange}</td>
									<td class="py-2 text-muted-foreground">{pos.strategy}</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			{/if}
		</div>
		
		<!-- Strategy Evolution -->
		<div class="rounded-lg border bg-card p-4">
			<h2 class="text-sm font-semibold mb-4">Strategy Evolution</h2>
			<div class="space-y-4">
				<div>
					<p class="text-xs text-muted-foreground uppercase tracking-wider">Active Strategy</p>
					<p class="text-lg font-bold">EMA-Trend-v1</p>
					<div class="mt-2 grid grid-cols-3 gap-2 text-xs">
						<div class="rounded bg-secondary/50 p-2">
							<p class="text-muted-foreground">Win Rate</p>
							<p class="font-semibold">62.5%</p>
						</div>
						<div class="rounded bg-secondary/50 p-2">
							<p class="text-muted-foreground">Sharpe</p>
							<p class="font-semibold">1.45</p>
						</div>
						<div class="rounded bg-secondary/50 p-2">
							<p class="text-muted-foreground">Regime</p>
							<p class="font-semibold">trending</p>
						</div>
					</div>
					<p class="mt-2 text-xs text-muted-foreground">Days live: 12 | Last promoted: 2024-01-03</p>
				</div>
				
				<div class="border-t border-border pt-3">
					<p class="text-xs text-muted-foreground uppercase tracking-wider mb-2">Evolution Queue</p>
					<div class="space-y-2">
						<div class="flex items-center justify-between rounded bg-secondary/50 px-3 py-2 text-xs">
							<span>RSI-Divergence-v2</span>
							<span class="rounded bg-amber-500/20 px-1.5 py-0.5 text-amber-400">Paper</span>
						</div>
						<div class="flex items-center justify-between rounded bg-secondary/50 px-3 py-2 text-xs">
							<span>Funding-Arb-v1</span>
							<span class="rounded bg-blue-500/20 px-1.5 py-0.5 text-blue-400">Backtest</span>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
	
	<!-- Trade History -->
	<TradeHistory />
</main>

<!-- System Health Bar -->
<footer class="border-t border-border bg-card px-6 py-2">
	<div class="flex items-center justify-between text-xs">
		<div class="flex items-center gap-4">
			<div class="flex items-center gap-1.5">
				<span class="h-2 w-2 rounded-full {health.vps ? 'bg-emerald-500' : 'bg-red-500'}"></span>
				<span class="text-muted-foreground">VPS Daemon</span>
			</div>
			<div class="flex items-center gap-1.5">
				<span class="h-2 w-2 rounded-full {health.binance ? 'bg-emerald-500' : 'bg-red-500'}"></span>
				<span class="text-muted-foreground">Binance Feed</span>
			</div>
			<div class="flex items-center gap-1.5">
				<span class="h-2 w-2 rounded-full {health.deepseek ? 'bg-emerald-500' : 'bg-red-500'}"></span>
				<span class="text-muted-foreground">DeepSeek API</span>
			</div>
			<div class="flex items-center gap-1.5">
				<span class="h-2 w-2 rounded-full {health.turso ? 'bg-emerald-500' : 'bg-red-500'}"></span>
				<span class="text-muted-foreground">Turso Sync</span>
			</div>
			<div class="flex items-center gap-1.5">
				<span class="h-2 w-2 rounded-full bg-emerald-500"></span>
				<span class="text-muted-foreground">Exchanges: {health.exchanges}/8</span>
			</div>
		</div>
		<span class="text-muted-foreground">Futures Brokiepedia v0.1.0</span>
	</div>
</footer>
