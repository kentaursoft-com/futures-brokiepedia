<script lang="ts">
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';
	import { api } from '$lib/api';
	
	// Dynamic imports for browser-only components
	let EquityChart: any;
	let PortfolioAnalytics: any;
	
	onMount(async () => {
		if (browser) {
			const equityModule = await import('$lib/components/EquityChart.svelte');
			EquityChart = equityModule.default;
			const portfolioModule = await import('$lib/components/PortfolioAnalytics.svelte');
			PortfolioAnalytics = portfolioModule.default;
		}
		loadAnalytics();
	});
	
	let analytics: any = null;
	let loading = true;
	let error: string | null = null;
	
	async function loadAnalytics() {
		try {
			loading = true;
			analytics = await api.getAnalytics();
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load analytics';
			console.error('Analytics load error:', err);
		} finally {
			loading = false;
		}
	}
	
	let activeTab = 'overview';
	const tabs = [
		{ id: 'overview', label: 'Overview' },
		{ id: 'trades', label: 'Trade Analysis' },
		{ id: 'monthly', label: 'Monthly Returns' },
	];
</script>

<svelte:head>
	<title>Analytics | Futures Brokiepedia</title>
</svelte:head>

<div class="space-y-6">
	<!-- Header -->
	<div>
		<h1 class="text-2xl font-bold">Performance Analytics</h1>
		<p class="text-muted-foreground text-sm mt-1">Track your trading performance and statistics</p>
	</div>
	
	{#if loading}
		<div class="flex items-center justify-center h-64">
			<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
		</div>
	{:else if error}
		<div class="bg-red-500/10 border border-red-500/20 rounded-xl p-6 text-center">
			<p class="text-red-400">{error}</p>
			<button class="mt-4 px-4 py-2 bg-primary rounded-lg text-sm" on:click={loadAnalytics}>Retry</button>
		</div>
	{:else if analytics}
		<!-- Key Metrics -->
		<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
			<div class="bg-card border border-border rounded-xl p-5">
				<p class="text-muted-foreground text-sm">Total Return</p>
				<p class="text-2xl font-bold mt-1 {analytics.totalReturn >= 0 ? 'text-green-400' : 'text-red-400'}">
					{analytics.totalReturn >= 0 ? '+' : ''}{analytics.totalReturn}%
				</p>
			</div>
			<div class="bg-card border border-border rounded-xl p-5">
				<p class="text-muted-foreground text-sm">Sharpe Ratio</p>
				<p class="text-2xl font-bold mt-1">{analytics.sharpeRatio}</p>
			</div>
			<div class="bg-card border border-border rounded-xl p-5">
				<p class="text-muted-foreground text-sm">Max Drawdown</p>
				<p class="text-2xl font-bold mt-1 text-red-400">{analytics.maxDrawdown}%</p>
			</div>
			<div class="bg-card border border-border rounded-xl p-5">
				<p class="text-muted-foreground text-sm">Win Rate</p>
				<p class="text-2xl font-bold mt-1">{analytics.winRate}%</p>
			</div>
		</div>
		
		<!-- Tabs -->
		<div class="bg-card border border-border rounded-xl">
			<div class="flex border-b border-border">
				{#each tabs as tab}
					<button
						class="px-6 py-4 text-sm font-medium transition-colors border-b-2 {activeTab === tab.id ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'}"
						on:click={() => activeTab = tab.id}
					>
						{tab.label}
					</button>
				{/each}
			</div>
			
			<div class="p-6">
				{#if activeTab === 'overview'}
					<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
						<!-- Equity Curve -->
						<div class="bg-muted rounded-lg p-5">
							<h3 class="font-semibold mb-4">Equity Curve</h3>
							<div class="h-64">
								{#if EquityChart}
									<svelte:component this={EquityChart} data={analytics.equityHistory} />
								{:else}
									<div class="h-full flex items-center justify-center text-muted-foreground">
										Loading chart...
									</div>
								{/if}
							</div>
						</div>
						
						<!-- Detailed Stats -->
						<div class="bg-muted rounded-lg p-5">
							<h3 class="font-semibold mb-4">Detailed Statistics</h3>
							<div class="space-y-3">
								<div class="flex justify-between py-2 border-b border-border/50">
									<span class="text-muted-foreground">Profit Factor</span>
									<span class="font-medium">{analytics.profitFactor}</span>
								</div>
								<div class="flex justify-between py-2 border-b border-border/50">
									<span class="text-muted-foreground">Average Trade</span>
									<span class="font-medium {analytics.avgTrade >= 0 ? 'text-green-400' : 'text-red-400'}">
										{analytics.avgTrade >= 0 ? '+' : ''}${analytics.avgTrade}
									</span>
								</div>
								<div class="flex justify-between py-2 border-b border-border/50">
									<span class="text-muted-foreground">Average Win</span>
									<span class="font-medium text-green-400">+${analytics.avgWin}</span>
								</div>
								<div class="flex justify-between py-2 border-b border-border/50">
									<span class="text-muted-foreground">Average Loss</span>
									<span class="font-medium text-red-400">${analytics.avgLoss}</span>
								</div>
								<div class="flex justify-between py-2 border-b border-border/50">
									<span class="text-muted-foreground">Best Trade</span>
									<span class="font-medium text-green-400">+${analytics.bestTrade.toLocaleString()}</span>
								</div>
								<div class="flex justify-between py-2">
									<span class="text-muted-foreground">Worst Trade</span>
									<span class="font-medium text-red-400">${analytics.worstTrade.toLocaleString()}</span>
								</div>
							</div>
						</div>
					</div>
					
				{:else if activeTab === 'trades'}
					<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
						<!-- Win/Loss Distribution -->
						<div class="bg-muted rounded-lg p-5">
							<h3 class="font-semibold mb-4">Trade Distribution</h3>
							<div class="space-y-3">
								{#if analytics.tradeDistribution && analytics.tradeDistribution.length > 0}
									{#each analytics.tradeDistribution as item}
										<div class="flex items-center gap-3">
											<span class="text-sm w-16">${item.range}</span>
											<div class="flex-1 h-6 bg-background rounded-full overflow-hidden">
												<div class="h-full bg-primary rounded-full flex items-center justify-end px-2" style="width: {(item.count / Math.max(...analytics.tradeDistribution.map((d: any) => d.count))) * 100}%">
													<span class="text-xs">{item.count}</span>
												</div>
											</div>
										</div>
									{/each}
								{:else}
									<p class="text-muted-foreground text-center py-8">No trade data yet</p>
								{/if}
							</div>
						</div>
						
						<!-- Trade Stats -->
						<div class="bg-muted rounded-lg p-5">
							<h3 class="font-semibold mb-4">Trade Statistics</h3>
							<div class="grid grid-cols-2 gap-4">
								<div class="text-center p-4 bg-background rounded-lg">
									<p class="text-3xl font-bold">{analytics.totalTrades}</p>
									<p class="text-sm text-muted-foreground mt-1">Total Trades</p>
								</div>
								<div class="text-center p-4 bg-background rounded-lg">
									<p class="text-3xl font-bold text-green-400">{analytics.winningTrades}</p>
									<p class="text-sm text-muted-foreground mt-1">Winning</p>
								</div>
								<div class="text-center p-4 bg-background rounded-lg">
									<p class="text-3xl font-bold text-red-400">{analytics.losingTrades}</p>
									<p class="text-sm text-muted-foreground mt-1">Losing</p>
								</div>
								<div class="text-center p-4 bg-background rounded-lg">
									<p class="text-3xl font-bold">{analytics.winRate}%</p>
									<p class="text-sm text-muted-foreground mt-1">Win Rate</p>
								</div>
							</div>
						</div>
					</div>
					
				{:else if activeTab === 'monthly'}
					<div class="bg-muted rounded-lg p-5">
						<h3 class="font-semibold mb-4">Monthly Returns</h3>
						{#if analytics.monthlyReturns && analytics.monthlyReturns.length > 0}
							<div class="grid grid-cols-7 gap-2">
								{#each analytics.monthlyReturns as month}
									<div class="text-center">
										<div class="h-32 bg-background rounded-lg relative flex items-end justify-center p-2">
											<div 
												class="w-full rounded {month.return >= 0 ? 'bg-green-500/50' : 'bg-red-500/50'}"
												style="height: {Math.min(Math.abs(month.return) * 10, 100)}%"
											></div>
										</div>
										<p class="text-sm mt-2">{month.month}</p>
										<p class="text-xs {month.return >= 0 ? 'text-green-400' : 'text-red-400'}">
											{month.return >= 0 ? '+' : ''}{month.return}%
										</p>
									</div>
								{/each}
							</div>
						{:else}
							<p class="text-muted-foreground text-center py-8">No monthly data yet</p>
						{/if}
					</div>
				{/if}
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
	:global(.border-primary) { border-color: hsl(217 91% 60%); }
</style>
