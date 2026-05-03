<script lang="ts">
	import { onDestroy, onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import TradingChart from '$lib/components/TradingChart.svelte';
	import IndicatorsPanel from '$lib/components/IndicatorsPanel.svelte';
	import OrderBook from '$lib/components/OrderBook.svelte';
	import EquityChart from '$lib/components/EquityChart.svelte';
	import TradeHistory from '$lib/components/TradeHistory.svelte';
	import TimeframeSelector from '$lib/components/TimeframeSelector.svelte';
	import AlertPanel from '$lib/components/AlertPanel.svelte';
	import PortfolioAnalytics from '$lib/components/PortfolioAnalytics.svelte';
	import PaperTradingPanel from '$lib/components/PaperTradingPanel.svelte';
	import OrderForm from '$lib/components/OrderForm.svelte';
	import SocialFeed from '$lib/components/SocialFeed.svelte';
	import { binanceWS } from '$lib/websocket';
	import { api, liveState, startPolling } from '$lib/api';
	
	let wsConnected = false;
	let lastPrice = 0;
	let priceChange = 0;
	let mobileMenuOpen = false;
	let activeTab = 'chart';
	
	const unsubscribe = binanceWS.subscribe(state => {
		wsConnected = state.connected;
		if (state.lastPrice !== lastPrice) {
			priceChange = state.lastPrice - lastPrice;
			lastPrice = state.lastPrice;
		}
	});
	
	// Live state from daemon (via Worker)
	let daemonConnected = false;
	let stopPolling: (() => void) | null = null;
	
	// Subscribe to live state
	liveState.subscribe(state => {
		if (state) {
			daemonConnected = true;
		}
	});
	
	// Default values (used when daemon is offline)
	let defaultStatus = 'paper';
	let defaultAsset = 'BTC-PERP';
	let defaultRegime = 'trending_up';
	let defaultPnl = 124.50;
	let defaultUnrealized = -45.20;
	let defaultEquity = 10500.00;
	let defaultDrawdown = 1.2;
	
	// Computed values - use live data if available
	$: systemStatus = $liveState?.systemStatus || defaultStatus;
	$: activeAsset = $liveState?.activeAsset || defaultAsset;
	$: regime = $liveState?.regime || defaultRegime;
	$: todayPnl = $liveState?.todayPnl ?? defaultPnl;
	$: unrealizedPnl = $liveState?.unrealizedPnl ?? defaultUnrealized;
	$: equity = $liveState?.equity ?? defaultEquity;
	$: dailyDrawdown = $liveState?.dailyDrawdown ?? defaultDrawdown;
	$: lastSync = $liveState?.lastSync ? new Date($liveState.lastSync).toISOString() : new Date().toISOString();
	
	// Departments from daemon or fallback
	const defaultDepartments = [
		{ name: 'Fundamental', confidence: 0.72, direction: 'long', lastRun: '14:30:00' },
		{ name: 'Technical', confidence: 0.85, direction: 'long', lastRun: '14:30:00' },
		{ name: 'Sentiment', confidence: 0.61, direction: 'flat', lastRun: '14:30:00' },
		{ name: 'Quantitative', confidence: 0.78, direction: 'long', lastRun: '14:30:00' },
		{ name: 'Statistical', confidence: 0.55, direction: 'short', lastRun: '14:30:00' },
		{ name: 'Qualitative', confidence: 0.90, direction: 'long', lastRun: '14:30:00' }
	];
	$: departments = ($liveState?.departments?.length > 0) ? $liveState.departments : defaultDepartments;
	
	// Positions from daemon or fallback
	const defaultPositions = [
		{ symbol: 'BTC-PERP', side: 'long', size: 0.15, entry: 43250.00, mark: 43400.00, pnl: 22.50, exchange: 'Binance', strategy: 'EMA-Trend-v1' }
	];
	$: positions = ($liveState?.positions?.length > 0) ? $liveState.positions : defaultPositions;
	
	// Health from daemon
	$: health = {
		vps: $liveState?.health?.vps ?? true,
		binance: wsConnected,
		deepseek: $liveState?.health?.deepseek ?? false,
		turso: $liveState?.health?.turso ?? false,
		exchanges: $liveState?.health?.exchanges ?? 0
	};
	
	onMount(() => {
		stopPolling = startPolling(5000);
	});
	
	let killSwitchLoading = false;
	
	async function triggerKillSwitch() {
		if (!confirm('⚠️ STEP 1/2: You are about to trigger the KILL-SWITCH.\n\nThis will:\n• Cancel all open orders\n• Close all positions at market\n• HALT all trading permanently\n\nContinue?')) {
			return;
		}
		
		try {
			killSwitchLoading = true;
			await api.triggerKillSwitch();
			alert('✅ Kill-switch activated successfully. All trading halted.');
		} catch (err) {
			alert('❌ Kill-switch failed: ' + (err instanceof Error ? err.message : 'Unknown error'));
		} finally {
			killSwitchLoading = false;
		}
	}
	
	function logout() {
		api.logout();
		goto('/auth');
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
	}
	
	const mobileTabs = [
		{ id: 'chart', label: '📊 Chart' },
		{ id: 'orders', label: '📋 Orders' },
		{ id: 'alerts', label: '🔔 Alerts' },
		{ id: 'social', label: '💬 Social' },
		{ id: 'paper', label: '🎮 Paper' }
	];
	
	onDestroy(() => {
		unsubscribe();
		binanceWS.disconnect();
		if (stopPolling) stopPolling();
	});
</script>

<!-- Top Bar -->
<header class="border-b border-border bg-card px-4 lg:px-6 py-3">
	<div class="flex items-center justify-between">
		<div class="flex items-center gap-2 lg:gap-4">
			<!-- Mobile menu button -->
			<button 
				on:click={() => mobileMenuOpen = !mobileMenuOpen}
				class="lg:hidden p-2 text-muted-foreground hover:text-foreground"
			>
				☰
			</button>
			
			<h1 class="text-lg lg:text-xl font-bold tracking-tight">Futures Brokiepedia</h1>
			<span class="hidden sm:inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium {getStatusColor(systemStatus)} text-white">
				<span class="h-1.5 w-1.5 rounded-full bg-white"></span>
				{getStatusText(systemStatus)}
			</span>
			<div class="hidden md:flex items-center gap-2">
				<span class="text-sm font-medium">{activeAsset}</span>
				{#if lastPrice > 0}
					<span class="text-sm {priceChange >= 0 ? 'text-emerald-400' : 'text-red-400'}">
						${lastPrice.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
					</span>
				{/if}
			</div>
			<span class="hidden lg:block rounded-md bg-secondary px-2 py-0.5 text-xs text-secondary-foreground">{regime}</span>
		</div>
		
		<div class="flex items-center gap-2 lg:gap-4">
			<div class="hidden sm:flex items-center gap-2">
				<span class="h-2 w-2 rounded-full {daemonConnected ? 'bg-emerald-500' : 'bg-amber-500'}"></span>
				<span class="text-xs text-muted-foreground hidden lg:inline">{daemonConnected ? 'Daemon Online' : 'Daemon Offline'}</span>
			</div>
			<div class="hidden sm:flex items-center gap-2">
				<span class="h-2 w-2 rounded-full {wsConnected ? 'bg-emerald-500' : 'bg-red-500'}"></span>
				<span class="text-xs text-muted-foreground hidden lg:inline">{wsConnected ? 'Live Feed' : 'Reconnecting...'}</span>
			</div>
			<span class="hidden lg:block text-xs text-muted-foreground">Last sync: {lastSync}</span>
			<button 
				on:click={logout}
				class="hidden sm:block rounded-md bg-secondary px-3 py-1.5 text-xs font-medium text-secondary-foreground hover:bg-secondary/80 transition-colors"
			>
				Logout
			</button>
			<button 
				on:click={triggerKillSwitch}
				disabled={killSwitchLoading}
				class="rounded-md bg-destructive px-3 lg:px-4 py-1.5 text-xs lg:text-sm font-medium text-destructive-foreground hover:bg-destructive/90 transition-colors disabled:opacity-50"
			>
				{killSwitchLoading ? '...' : '🛑 Kill'}
			</button>
		</div>
	</div>
	
	<!-- Mobile tabs -->
	<div class="lg:hidden mt-3 flex gap-1 overflow-x-auto pb-1">
		{#each mobileTabs as tab}
			<button 
				on:click={() => activeTab = tab.id}
				class="whitespace-nowrap rounded px-3 py-1 text-xs font-medium transition-colors {activeTab === tab.id ? 'bg-primary text-primary-foreground' : 'bg-secondary text-secondary-foreground'}"
			>
				{tab.label}
			</button>
		{/each}
	</div>
</header>

<!-- Main Dashboard -->
<main class="container mx-auto p-4 lg:p-6 space-y-4 lg:space-y-6">
	<!-- Metric Cards -->
	<div class="grid grid-cols-2 lg:grid-cols-4 gap-3 lg:gap-4">
		<div class="rounded-lg border bg-card p-3 lg:p-4">
			<p class="text-xs text-muted-foreground uppercase tracking-wider">Today P&L</p>
			<p class="text-lg lg:text-2xl font-bold {todayPnl >= 0 ? 'text-emerald-400' : 'text-red-400'}">
				{todayPnl >= 0 ? '+' : ''}${todayPnl.toFixed(2)}
			</p>
		</div>
		
		<div class="rounded-lg border bg-card p-3 lg:p-4">
			<p class="text-xs text-muted-foreground uppercase tracking-wider">Unrealized P&L</p>
			<p class="text-lg lg:text-2xl font-bold {unrealizedPnl >= 0 ? 'text-emerald-400' : 'text-red-400'}">
				{unrealizedPnl >= 0 ? '+' : ''}${unrealizedPnl.toFixed(2)}
			</p>
		</div>
		
		<div class="rounded-lg border bg-card p-3 lg:p-4">
			<p class="text-xs text-muted-foreground uppercase tracking-wider">Account Equity</p>
			<p class="text-lg lg:text-2xl font-bold">${equity.toLocaleString('en-US', { minimumFractionDigits: 2 })}</p>
		</div>
		
		<div class="rounded-lg border bg-card p-3 lg:p-4">
			<p class="text-xs text-muted-foreground uppercase tracking-wider">Daily Drawdown</p>
			<div class="flex items-center gap-2">
				<p class="text-lg lg:text-2xl font-bold {dailyDrawdown >= 6 ? 'text-red-500' : dailyDrawdown >= 3 ? 'text-amber-500' : 'text-emerald-400'}">
					{dailyDrawdown.toFixed(2)}%
				</p>
			</div>
			<div class="mt-2 h-1.5 w-full rounded-full bg-secondary">
				<div 
					class="h-full rounded-full transition-all {dailyDrawdown >= 6 ? 'bg-red-500' : dailyDrawdown >= 3 ? 'bg-amber-500' : 'bg-emerald-400'}"
					style="width: {Math.min((dailyDrawdown / 6) * 100, 100)}%"
				></div>
			</div>
		</div>
	</div>
	
	<!-- Desktop Layout -->
	<div class="hidden lg:grid grid-cols-3 gap-6">
		<!-- Main Chart Area -->
		<div class="col-span-2 space-y-6">
			<!-- Chart -->
			<div class="rounded-lg border bg-card p-4">
				<div class="flex items-center justify-between mb-4">
					<h2 class="text-sm font-semibold">Chart — {activeAsset}</h2>
					<TimeframeSelector on:change={(e) => onTimeframeChange(e.detail)} />
				</div>
				<div class="h-[400px]">
					<TradingChart />
				</div>
				<IndicatorsPanel height={100} />
			</div>
			
			<!-- Equity & Analytics Row -->
			<div class="grid grid-cols-2 gap-6">
				<div class="rounded-lg border bg-card p-4">
					<h2 class="text-sm font-semibold mb-2">Equity Curve</h2>
					<div class="h-[200px]">
						<EquityChart />
					</div>
				</div>
				<PortfolioAnalytics />
			</div>
			
			<!-- Trade History -->
			<TradeHistory />
			
			<!-- Social Feed -->
			<SocialFeed />
		</div>
		
		<!-- Sidebar -->
		<div class="space-y-6">
			<OrderBook />
			<OrderForm />
			<PaperTradingPanel />
			<AlertPanel />
			
			<!-- Agent Departments -->
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
									<div class="h-full rounded-full bg-primary" style="width: {dept.confidence * 100}%"></div>
								</div>
							</div>
						</div>
					{/each}
				</div>
			</div>
			
			<!-- Open Positions -->
			<div class="rounded-lg border bg-card p-4">
				<h2 class="text-sm font-semibold mb-4">Open Positions ({positions.length})</h2>
				{#if positions.length === 0}
					<p class="text-sm text-muted-foreground">No open positions</p>
				{:else}
					<div class="space-y-2">
						{#each positions as pos}
							<div class="rounded bg-secondary/50 px-3 py-2 text-sm">
								<div class="flex justify-between">
									<span class="font-medium">{pos.symbol}</span>
									<span class="rounded px-1.5 py-0.5 text-xs {pos.side === 'long' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}">
										{pos.side.toUpperCase()}
									</span>
								</div>
								<div class="flex justify-between text-xs text-muted-foreground mt-1">
									<span>{pos.size} @ ${pos.entry.toLocaleString()}</span>
									<span class="{pos.pnl >= 0 ? 'text-emerald-400' : 'text-red-400'}">{pos.pnl >= 0 ? '+' : ''}${pos.pnl.toFixed(2)}</span>
								</div>
							</div>
						{/each}
					</div>
				{/if}
			</div>
			
			<!-- Strategy Evolution -->
			<div class="rounded-lg border bg-card p-4">
				<h2 class="text-sm font-semibold mb-4">Strategy Evolution</h2>
				<div class="space-y-3">
					<div>
						<p class="text-xs text-muted-foreground">Active Strategy</p>
						<p class="text-lg font-bold">EMA-Trend-v1</p>
						<div class="grid grid-cols-3 gap-2 text-xs mt-2">
							<div class="rounded bg-secondary/50 p-2 text-center">
								<p class="text-muted-foreground">Win Rate</p>
								<p class="font-semibold">62.5%</p>
							</div>
							<div class="rounded bg-secondary/50 p-2 text-center">
								<p class="text-muted-foreground">Sharpe</p>
								<p class="font-semibold">1.45</p>
							</div>
							<div class="rounded bg-secondary/50 p-2 text-center">
								<p class="text-muted-foreground">Regime</p>
								<p class="font-semibold">trending</p>
							</div>
						</div>
					</div>
					<div class="border-t border-border pt-2">
						<p class="text-xs text-muted-foreground mb-1">Queue</p>
						<div class="space-y-1">
							<div class="flex justify-between text-xs rounded bg-secondary/50 px-2 py-1">
								<span>RSI-Divergence-v2</span>
								<span class="text-amber-400">Paper</span>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
	
	<!-- Mobile Layout -->
	<div class="lg:hidden space-y-4">
		{#if activeTab === 'chart'}
			<div class="rounded-lg border bg-card p-4">
				<div class="h-[300px]">
					<TradingChart />
				</div>
			</div>
			<IndicatorsPanel height={80} />
			<OrderBook />
		{:else if activeTab === 'orders'}
			<OrderForm />
			<div class="rounded-lg border bg-card p-4">
				<h2 class="text-sm font-semibold mb-4">Open Positions</h2>
				{#each positions as pos}
					<div class="rounded bg-secondary/50 px-3 py-2 mb-2">
						<div class="flex justify-between">
							<span class="font-medium">{pos.symbol}</span>
							<span class="text-xs rounded px-1.5 py-0.5 {pos.side === 'long' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}">
								{pos.side.toUpperCase()}
							</span>
						</div>
						<div class="flex justify-between text-xs text-muted-foreground">
							<span>{pos.size} @ ${pos.entry.toLocaleString()}</span>
							<span class="{pos.pnl >= 0 ? 'text-emerald-400' : 'text-red-400'}">{pos.pnl >= 0 ? '+' : ''}${pos.pnl.toFixed(2)}</span>
						</div>
					</div>
				{/each}
			</div>
		{:else if activeTab === 'alerts'}
			<AlertPanel />
			<PortfolioAnalytics />
		{:else if activeTab === 'social'}
			<SocialFeed />
			<TradeHistory />
		{:else if activeTab === 'paper'}
			<PaperTradingPanel />
			<div class="rounded-lg border bg-card p-4">
				<h2 class="text-sm font-semibold mb-2">Equity Curve</h2>
				<div class="h-[200px]">
					<EquityChart />
				</div>
			</div>
		{/if}
	</div>
</main>

<!-- System Health Bar -->
<footer class="border-t border-border bg-card px-4 lg:px-6 py-2">
	<div class="flex flex-wrap items-center justify-between text-xs gap-2">
		<div class="flex flex-wrap items-center gap-3 lg:gap-4">
			<div class="flex items-center gap-1.5">
				<span class="h-2 w-2 rounded-full {health.vps ? 'bg-emerald-500' : 'bg-red-500'}"></span>
				<span class="text-muted-foreground hidden sm:inline">VPS</span>
			</div>
			<div class="flex items-center gap-1.5">
				<span class="h-2 w-2 rounded-full {health.binance ? 'bg-emerald-500' : 'bg-red-500'}"></span>
				<span class="text-muted-foreground hidden sm:inline">Binance</span>
			</div>
			<div class="flex items-center gap-1.5">
				<span class="h-2 w-2 rounded-full {health.deepseek ? 'bg-emerald-500' : 'bg-red-500'}"></span>
				<span class="text-muted-foreground hidden sm:inline">DeepSeek</span>
			</div>
			<div class="flex items-center gap-1.5">
				<span class="h-2 w-2 rounded-full {health.turso ? 'bg-emerald-500' : 'bg-red-500'}"></span>
				<span class="text-muted-foreground hidden sm:inline">Turso</span>
			</div>
			<div class="flex items-center gap-1.5">
				<span class="h-2 w-2 rounded-full bg-emerald-500"></span>
				<span class="text-muted-foreground">{health.exchanges}/8</span>
			</div>
		</div>
		<span class="text-muted-foreground">Futures Brokiepedia v0.2.0</span>
	</div>
</footer>
