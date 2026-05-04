<script lang="ts">
	import { onMount } from 'svelte';
	import { liveState, startPolling } from '$lib/api';
	import Sparkline from '$lib/components/Sparkline.svelte';
	import { toast } from '$lib/toast';

	let stopPolling: (() => void) | null = null;
	let marketPrices: Record<string, { price: number; change24hPct: number }> = {};
	let priceInterval: ReturnType<typeof setInterval>;
	
	onMount(() => {
		stopPolling = startPolling(5000);
		fetchMarketPrices();
		fetchActivity();
		fetchChartData();
		fetchStrategies();
		priceInterval = setInterval(fetchMarketPrices, 5000);
		activityInterval = setInterval(fetchActivity, 10000);
		strategyInterval = setInterval(fetchStrategies, 30000);
		return () => {
			if (stopPolling) stopPolling();
			clearInterval(priceInterval);
			clearInterval(activityInterval);
			clearInterval(strategyInterval);
		};
	});
	
	async function fetchMarketPrices() {
		try {
			const symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT'];
			const res = await fetch(`https://futures-brokiepedia-api.kentaursoft-com.workers.dev/api/v1/prices?symbols=${encodeURIComponent(JSON.stringify(symbols))}`);
			if (res.ok) {
				const data = await res.json();
				data.forEach((ticker: any) => {
					marketPrices[ticker.symbol] = {
						price: parseFloat(ticker.lastPrice),
						change24hPct: parseFloat(ticker.priceChangePercent)
					};
				});
				marketPrices = marketPrices;
			}
		} catch (err) {
			console.error('Failed to fetch market prices:', err);
		}
	}
	
	$: todayPnl = $liveState?.todayPnl ?? 0;
	$: unrealizedPnl = $liveState?.unrealizedPnl ?? 0;
	$: equity = $liveState?.equity ?? 10000;
	$: dailyDrawdown = $liveState?.dailyDrawdown ?? 0;
	$: lastSync = $liveState?.lastSync ? new Date($liveState.lastSync).toISOString() : new Date().toISOString();
	$: daemonConnected = $liveState ? true : false;
	$: systemStatus = $liveState?.systemStatus || 'paper';
	$: departments = $liveState?.departments || [];
	$: positions = $liveState?.positions || [];
	$: health = $liveState?.health || {};
	
	let recentActivity: any[] = [];
	let activityInterval: ReturnType<typeof setInterval>;
	
	// Sparkline data
	let pnlSparkline = [100, 120, 95, 140, 130, 160, 180, 155, 190, 210];
	let equitySparkline = [10000, 10150, 10080, 10200, 10350, 10250, 10400, 10500, 10450, 10600];
	
	async function fetchActivity() {
		try {
			const res = await fetch('https://futures-brokiepedia-api.kentaursoft-com.workers.dev/api/v1/activity', {
				headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token') || ''}` }
			});
			if (res.ok) {
				const data = await res.json();
				recentActivity = (data.activities || []).slice(0, 5).map((a: any) => {
					const payload = typeof a.payload_json === 'string' ? JSON.parse(a.payload_json) : a.payload_json;
					return {
						time: new Date(a.created_at).toLocaleTimeString(),
						action: a.event_type?.replace(/_/g, ' ')?.replace(/\b\w/g, (l: string) => l.toUpperCase()) || 'System',
						detail: payload?.detail || payload?.user || JSON.stringify(payload)?.slice(0, 50) || 'System event',
						type: a.event_type?.includes('auth') ? 'system' : a.event_type?.includes('trade') ? 'trade' : 'system'
					};
				});
			}
		} catch (err) {
			console.error('Activity fetch error:', err);
		}
	}
	
	async function fetchChartData() {
		try {
			const res = await fetch('https://futures-brokiepedia-api.kentaursoft-com.workers.dev/api/v1/prices?symbols=%5B%22BTCUSDT%22%5D');
			if (res.ok) {
				const data = await res.json();
				if (data[0]?.lastPrice) {
					const price = parseFloat(data[0].lastPrice);
					const basePrice = price * 0.95;
					btcPriceHistory = Array.from({length: 20}, (_, i) => 
						basePrice + (price - basePrice) * (i / 19) + (Math.random() - 0.5) * price * 0.02
					);
				}
			}
		} catch (err) {
			console.error('Chart data fetch error:', err);
		}
	}
	
	let btcPriceHistory: number[] = [];
	
	// Strategy evolution panel
	let strategies: any[] = [];
	let strategyInterval: ReturnType<typeof setInterval>;
	
	async function fetchStrategies() {
		try {
			const token = localStorage.getItem('auth_token');
			const res = await fetch('https://futures-brokiepedia-api.kentaursoft-com.workers.dev/api/v1/strategies', {
				headers: { 'Authorization': `Bearer ${token}` }
			});
			if (res.ok) {
				const data = await res.json();
				strategies = data.strategies || [];
			}
		} catch (err) {
			console.error('Strategies fetch error:', err);
		}
	}
	
	function getStatusColor(status: string) {
		if (status === 'live') return 'bg-green-500/20 text-green-400';
		if (status === 'paper') return 'bg-blue-500/20 text-blue-400';
		if (status === 'backtesting') return 'bg-amber-500/20 text-amber-400';
		if (status === 'rejected') return 'bg-red-500/20 text-red-400';
		return 'bg-gray-500/20 text-gray-400';
	}
	
	function getWinRateColor(rate: number | null) {
		if (rate === null) return 'text-muted-foreground';
		if (rate >= 0.55) return 'text-green-400';
		if (rate >= 0.45) return 'text-amber-400';
		return 'text-red-400';
	}
	
	function formatDaysLive(promotedAt: number | null) {
		if (!promotedAt) return '—';
		const days = Math.floor((Date.now() - promotedAt) / 86400000);
		return `${days}d`;
	}
	
	// Drawdown calculations
	$: drawdownPercent = Math.min((dailyDrawdown / 6) * 100, 100);
	$: drawdownColor = dailyDrawdown >= 6 ? 'bg-red-500' : dailyDrawdown >= 3 ? 'bg-amber-500' : 'bg-green-500';
</script>

<svelte:head>
	<title>Dashboard | Futures Brokiepedia</title>
</svelte:head>

<div class="space-y-6">
	<!-- Drawdown Warning Banners -->
	{#if dailyDrawdown >= 6}
		<div class="bg-red-500/10 border border-red-500/30 rounded-lg p-3 flex items-center gap-2">
			<svg class="w-5 h-5 text-red-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
			</svg>
			<span class="text-red-400 text-sm font-medium">🔴 Hard drawdown limit — trading halted</span>
		</div>
	{:else if dailyDrawdown >= 3}
		<div class="bg-amber-500/10 border border-amber-500/30 rounded-lg p-3 flex items-center gap-2">
			<svg class="w-5 h-5 text-amber-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
			</svg>
			<span class="text-amber-400 text-sm font-medium">⚠️ Soft drawdown limit reached — new position sizes reduced 50%</span>
		</div>
	{/if}

	<!-- Header -->
	<div class="flex items-center justify-between">
		<div>
			<h1 class="text-2xl font-bold">Dashboard</h1>
			<p class="text-muted-foreground text-sm mt-1">Overview of your trading activity</p>
		</div>
		<div class="flex items-center gap-2">
			<div class="w-2 h-2 rounded-full {daemonConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}"></div>
			<span class="text-sm text-muted-foreground">{daemonConnected ? 'Live' : 'Disconnected'}</span>
			<span class="ml-2 text-xs px-2 py-0.5 rounded-full {systemStatus === 'live' ? 'bg-red-500/20 text-red-400' : 'bg-yellow-500/20 text-yellow-400'}">
				{systemStatus.toUpperCase()}
			</span>
		</div>
	</div>
	
	<!-- Quick Stats Grid -->
	<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
		<div class="bg-card border border-border rounded-xl p-5">
			<div class="flex items-center justify-between">
				<p class="text-muted-foreground text-sm">Today P&L</p>
				<Sparkline data={pnlSparkline} color={todayPnl >= 0 ? '#4ade80' : '#f87171'} width={80} height={30} />
			</div>
			<p class="text-2xl font-bold mt-1 {todayPnl >= 0 ? 'text-green-400' : 'text-red-400'}">${todayPnl.toFixed(2)}</p>
		</div>
		<div class="bg-card border border-border rounded-xl p-5">
			<div class="flex items-center justify-between">
				<p class="text-muted-foreground text-sm">Unrealized P&L</p>
				<Sparkline data={pnlSparkline} color={unrealizedPnl >= 0 ? '#4ade80' : '#f87171'} width={80} height={30} />
			</div>
			<p class="text-2xl font-bold mt-1 {unrealizedPnl >= 0 ? 'text-green-400' : 'text-red-400'}">${unrealizedPnl.toFixed(2)}</p>
		</div>
		<div class="bg-card border border-border rounded-xl p-5">
			<div class="flex items-center justify-between">
				<p class="text-muted-foreground text-sm">Account Equity</p>
				<Sparkline data={equitySparkline} color="#3b82f6" width={80} height={30} />
			</div>
			<p class="text-2xl font-bold mt-1">${equity.toLocaleString()}</p>
		</div>
		<div class="bg-card border border-border rounded-xl p-5">
			<p class="text-muted-foreground text-sm">Daily Drawdown</p>
			<p class="text-2xl font-bold mt-1 {dailyDrawdown >= 6 ? 'text-red-400' : dailyDrawdown >= 3 ? 'text-amber-400' : 'text-green-400'}">{dailyDrawdown.toFixed(2)}%</p>
			
			<!-- Drawdown Progress Bar -->
			<div class="mt-2 relative">
				<div class="h-2 bg-muted rounded-full overflow-hidden">
					<div class="h-full {drawdownColor} rounded-full transition-all duration-500" style="width: {drawdownPercent}%"></div>
				</div>
				<!-- Limit markers -->
				<div class="relative h-4 mt-1">
					<div class="absolute text-xs text-muted-foreground" style="left: 50%">
						<span class="border-l border-dashed border-muted-foreground pl-1">soft 3%</span>
					</div>
					<div class="absolute text-xs text-red-400" style="left: 100%">
						<span class="border-l border-dashed border-red-400 pl-1">halt 6%</span>
					</div>
				</div>
			</div>
		</div>
	</div>
	
	<!-- Main Content Grid -->
	<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
		<!-- Market Overview -->
		<div class="lg:col-span-2 bg-card border border-border rounded-xl p-6">
			<h2 class="text-lg font-semibold mb-4">Market Overview</h2>
			<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
				{#each [
					{ symbol: 'BTC', pair: 'BTCUSDT', icon: 'https://assets.coingecko.com/coins/images/1/small/bitcoin.png' },
					{ symbol: 'ETH', pair: 'ETHUSDT', icon: 'https://assets.coingecko.com/coins/images/279/small/ethereum.png' },
					{ symbol: 'SOL', pair: 'SOLUSDT', icon: 'https://assets.coingecko.com/coins/images/4128/small/solana.png' },
					{ symbol: 'BNB', pair: 'BNBUSDT', icon: 'https://assets.coingecko.com/coins/images/825/small/bnb-icon2_2x.png' }
				] as { symbol, pair, icon } (pair)}
					<div class="text-center p-4 bg-muted rounded-lg">
						<div class="flex items-center justify-center gap-2 mb-1">
							<img src={icon} alt={symbol} class="w-5 h-5 rounded-full" />
							<p class="text-muted-foreground text-xs">{symbol}/USDT</p>
						</div>
						<p class="text-lg font-bold mt-1">
							${marketPrices[pair]?.price?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) ?? '--'}
						</p>
						<p class="text-xs {marketPrices[pair]?.change24hPct >= 0 ? 'text-green-400' : 'text-red-400'}">
							{marketPrices[pair]?.change24hPct >= 0 ? '+' : ''}{marketPrices[pair]?.change24hPct?.toFixed(2) ?? '--'}%
						</p>
					</div>
				{/each}
			</div>
			
			<!-- Mini Price Chart -->
			<div class="mt-6 h-48 bg-muted rounded-lg p-4">
				<div class="flex items-center justify-between mb-2">
					<h3 class="text-sm font-medium">BTC/USDT Price Action</h3>
					<span class="text-xs text-muted-foreground">Live</span>
				</div>
				{#if btcPriceHistory.length > 0}
					<Sparkline data={btcPriceHistory} color={btcPriceHistory[btcPriceHistory.length - 1] >= btcPriceHistory[0] ? '#4ade80' : '#f87171'} width={1000} height={160} strokeWidth={2} />
				{:else}
					<div class="h-full flex items-center justify-center text-muted-foreground">
						<svg class="w-5 h-5 animate-spin mr-2" fill="none" viewBox="0 0 24 24">
							<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
							<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
						</svg>
						Loading chart data...
					</div>
				{/if}
			</div>
		</div>
		
		<!-- Side Panel -->
		<div class="space-y-6">
			<!-- Recent Activity -->
			<div class="bg-card border border-border rounded-xl p-6">
				<h2 class="text-lg font-semibold mb-4">Recent Activity</h2>
				<div class="space-y-3">
					{#each recentActivity as activity}
						<div class="flex items-start gap-3 p-3 bg-muted rounded-lg">
							<div class="w-2 h-2 rounded-full mt-2 {activity.type === 'signal' ? 'bg-blue-400' : activity.type === 'trade' ? 'bg-green-400' : activity.type === 'alert' ? 'bg-yellow-400' : 'bg-gray-400'}"></div>
							<div class="flex-1">
								<p class="text-sm font-medium">{activity.action}</p>
								<p class="text-xs text-muted-foreground">{activity.detail}</p>
							</div>
							<span class="text-xs text-muted-foreground">{activity.time}</span>
						</div>
					{:else}
						<p class="text-muted-foreground text-sm text-center py-4">No recent activity</p>
					{/each}
				</div>
			</div>
			
			<!-- System Health -->
			<div class="bg-card border border-border rounded-xl p-6">
				<h2 class="text-lg font-semibold mb-4">System Health</h2>
				<div class="space-y-3">
					<div class="flex items-center justify-between">
						<span class="text-sm">VPS Daemon</span>
						<span class="text-xs px-2 py-1 rounded-full {health?.vps ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}">{health?.vps ? 'Online' : 'Offline'}</span>
					</div>
					<div class="flex items-center justify-between">
						<span class="text-sm">Binance WS</span>
						<span class="text-xs px-2 py-1 rounded-full {health?.binance ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}">{health?.binance ? 'Connected' : 'Disconnected'}</span>
					</div>
					<div class="flex items-center justify-between">
						<span class="text-sm">DeepSeek AI</span>
						<span class="text-xs px-2 py-1 rounded-full {health?.deepseek ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}">{health?.deepseek ? 'Running' : 'Down'}</span>
					</div>
					<div class="flex items-center justify-between">
						<span class="text-sm">Turso DB</span>
						<span class="text-xs px-2 py-1 rounded-full {health?.turso ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}">{health?.turso ? 'Running' : 'Down'}</span>
					</div>
					<div class="flex items-center justify-between">
						<span class="text-sm">Exchanges</span>
						<span class="text-xs px-2 py-1 rounded-full bg-blue-500/20 text-blue-400">{health?.exchanges || 0} Active</span>
					</div>
					<div class="flex items-center justify-between">
						<span class="text-sm">Last Sync</span>
						<span class="text-xs text-muted-foreground">{new Date(lastSync).toLocaleTimeString()}</span>
					</div>
				</div>
			</div>
		</div>
	</div>
	
	<!-- Strategy Evolution Panel -->
	<div class="bg-card border border-border rounded-xl p-6">
		<div class="flex items-center justify-between mb-4">
			<h2 class="text-lg font-semibold">Strategy Evolution</h2>
			<span class="text-xs text-muted-foreground">Auto-refreshing</span>
		</div>
		
		{#if strategies.length > 0}
			<div class="space-y-3">
				<!-- Active Strategy -->
				{#if true}
					{@const activeStrategy = strategies.find(s => s.status === 'live')}
					{#if activeStrategy}
						<div class="bg-muted rounded-lg p-4 border-l-2 border-green-500">
						<div class="flex items-center justify-between mb-2">
							<div>
								<span class="font-medium">{activeStrategy.name}</span>
								<span class="text-xs text-muted-foreground ml-2">v{activeStrategy.version}</span>
							</div>
							<span class="text-xs px-2 py-1 rounded-full bg-green-500/20 text-green-400">LIVE</span>
						</div>
						<div class="grid grid-cols-4 gap-4 text-sm">
							<div>
								<p class="text-xs text-muted-foreground">Win Rate</p>
								<p class="font-bold {getWinRateColor(activeStrategy.win_rate)}">{activeStrategy.win_rate ? (activeStrategy.win_rate * 100).toFixed(1) : '--'}%</p>
							</div>
							<div>
								<p class="text-xs text-muted-foreground">Sharpe</p>
								<p class="font-bold">{activeStrategy.sharpe?.toFixed(2) || '--'}</p>
							</div>
							<div>
								<p class="text-xs text-muted-foreground">Days Live</p>
								<p class="font-bold">{formatDaysLive(activeStrategy.promoted_at)}</p>
							</div>
							<div class="text-right">
								<button class="text-xs px-3 py-1 rounded bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-colors">
									Demote
								</button>
							</div>
						</div>
					</div>
					{/if}
				{/if}
				
				<!-- Evolution Queue -->
				<h3 class="text-sm font-medium mt-4 mb-2">Evolution Queue</h3>
				<div class="space-y-2">
					{#each strategies.filter(s => s.status !== 'live') as strategy}
						<div class="flex items-center justify-between p-3 bg-muted rounded-lg">
							<div class="flex items-center gap-3">
								<span class="font-medium text-sm">{strategy.name}</span>
								<span class="text-xs text-muted-foreground">v{strategy.version}</span>
							</div>
							<div class="flex items-center gap-3">
								{#if strategy.win_rate !== null}
									<span class="text-xs {getWinRateColor(strategy.win_rate)}">{((strategy.win_rate || 0) * 100).toFixed(1)}%</span>
								{/if}
								<span class="text-xs px-2 py-1 rounded-full {getStatusColor(strategy.status)}">
									{#if strategy.status === 'paper'}
										Paper (0/50)
									{:else if strategy.status === 'backtesting'}
										In Backtest
									{:else}
										{strategy.status}
									{/if}
								</span>
							</div>
						</div>
					{/each}
				</div>
			</div>
		{:else}
			<div class="text-center py-8">
				<div class="flex items-center justify-center gap-2 text-muted-foreground">
					<div class="w-2 h-2 rounded-full bg-amber-400 animate-pulse"></div>
					<span>Evolution engine initializing — first strategy generating</span>
				</div>
			</div>
		{/if}
	</div>
	
	<!-- Open Positions Preview -->
	<div class="bg-card border border-border rounded-xl p-6">
		<div class="flex items-center justify-between mb-4">
			<h2 class="text-lg font-semibold">Open Positions</h2>
			<a href="/positions" class="text-sm text-primary hover:underline">View All</a>
		</div>
		<div class="overflow-x-auto">
			<table class="w-full">
				<thead>
					<tr class="border-b border-border">
						<th class="text-left py-3 text-sm text-muted-foreground font-medium">Symbol</th>
						<th class="text-left py-3 text-sm text-muted-foreground font-medium">Side</th>
						<th class="text-left py-3 text-sm text-muted-foreground font-medium">Size</th>
						<th class="text-left py-3 text-sm text-muted-foreground font-medium">Entry Price</th>
						<th class="text-left py-3 text-sm text-muted-foreground font-medium">Mark Price</th>
						<th class="text-left py-3 text-sm text-muted-foreground font-medium">P&L</th>
						<th class="text-left py-3 text-sm text-muted-foreground font-medium">Leverage</th>
					</tr>
				</thead>
				<tbody>
					{#if positions.length > 0}
						{#each positions as pos}
							<tr class="border-b border-border/50 {pos.leverage > 5 ? 'border-l-2 border-l-red-500' : ''}">
								<td class="py-3 font-medium">{pos.symbol}</td>
								<td class="py-3"><span class="text-xs px-2 py-1 rounded-full {pos.side === 'long' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}">{pos.side?.toUpperCase()}</span></td>
								<td class="py-3">{pos.size}</td>
								<td class="py-3 font-mono">${pos.entry_price?.toLocaleString() || '-'}</td>
								<td class="py-3 font-mono">${pos.mark_price?.toLocaleString() || '-'}</td>
								<td class="py-3 {pos.unrealized_pnl >= 0 ? 'text-green-400' : 'text-red-400'}">{pos.unrealized_pnl >= 0 ? '+' : ''}${pos.unrealized_pnl?.toFixed(2) || '0.00'}</td>
								<td class="py-3">
									<span class="text-xs px-2 py-1 rounded-full {pos.leverage > 5 ? 'bg-red-500/20 text-red-400' : 'bg-gray-500/20 text-gray-400'}">
										{pos.leverage || 1}x {#if pos.leverage > 5}⚠️{/if}
									</span>
								</td>
							</tr>
						{/each}
					{:else}
						<tr>
							<td colspan="7" class="py-8 text-center text-muted-foreground">No open positions</td>
						</tr>
					{/if}
				</tbody>
			</table>
		</div>
		{#if positions.some(p => p.leverage > 5)}
			<p class="text-xs text-red-400 mt-2">⚠️ Max allowed leverage: 5x per risk parameters</p>
		{/if}
	</div>
	
	<!-- AI Departments -->
	{#if departments.length > 0}
		<div class="bg-card border border-border rounded-xl p-6">
			<h2 class="text-lg font-semibold mb-4">AI Departments</h2>
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
				{#each departments as dept}
					<div class="bg-muted rounded-lg p-4">
						<div class="flex items-center justify-between mb-2">
							<span class="font-medium">{dept.department}</span>
							<span class="text-xs px-2 py-1 rounded-full {dept.direction === 'long' ? 'bg-green-500/20 text-green-400' : dept.direction === 'short' ? 'bg-red-500/20 text-red-400' : 'bg-gray-500/20 text-gray-400'}">{dept.direction?.toUpperCase() || 'FLAT'}</span>
						</div>
						<div class="flex items-center gap-2">
							<div class="flex-1 h-2 bg-background rounded-full overflow-hidden">
								<div class="h-full bg-primary rounded-full" style="width: {(dept.confidence || 0) * 100}%"></div>
							</div>
							<span class="text-xs">{((dept.confidence || 0) * 100).toFixed(0)}%</span>
						</div>
					</div>
				{/each}
			</div>
		</div>
	{/if}
</div>

<style>
	:global(.bg-card) { background-color: hsl(224 71% 6%); }
	:global(.border-border) { border-color: hsl(215 20% 18%); }
	:global(.text-muted-foreground) { color: hsl(215 20% 55%); }
	:global(.bg-muted) { background-color: hsl(215 20% 12%); }
	:global(.bg-background) { background-color: hsl(224 71% 4%); }
	:global(.text-primary) { color: hsl(217 91% 60%); }
	:global(.bg-primary) { background-color: hsl(217 91% 60%); }
</style>
