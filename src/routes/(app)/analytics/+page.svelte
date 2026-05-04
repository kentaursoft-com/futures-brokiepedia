<script lang="ts">
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';
	
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
	});
	
	const performanceStats = {
		totalReturn: 24.5,
		sharpeRatio: 1.85,
		maxDrawdown: -8.2,
		winRate: 68.5,
		profitFactor: 1.72,
		avgTrade: 125.50,
		avgWin: 450.00,
		avgLoss: -180.00,
		bestTrade: 1250.00,
		worstTrade: -520.00,
		totalTrades: 127,
		winningTrades: 87,
		losingTrades: 40,
	};
	
	const monthlyReturns = [
		{ month: 'Jan', return: 5.2 },
		{ month: 'Feb', return: -2.1 },
		{ month: 'Mar', return: 8.5 },
		{ month: 'Apr', return: 3.2 },
		{ month: 'May', return: -1.5 },
		{ month: 'Jun', return: 6.8 },
		{ month: 'Jul', return: 4.2 },
	];
	
	const tradeDistribution = [
		{ range: '0-50', count: 23 },
		{ range: '50-100', count: 31 },
		{ range: '100-200', count: 28 },
		{ range: '200-500', count: 18 },
		{ range: '500+', count: 7 },
	];
	
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
	
	<!-- Key Metrics -->
	<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
		<div class="bg-card border border-border rounded-xl p-5">
			<p class="text-muted-foreground text-sm">Total Return</p>
			<p class="text-2xl font-bold mt-1 text-green-400">+{performanceStats.totalReturn}%</p>
		</div>
		<div class="bg-card border border-border rounded-xl p-5">
			<p class="text-muted-foreground text-sm">Sharpe Ratio</p>
			<p class="text-2xl font-bold mt-1">{performanceStats.sharpeRatio}</p>
		</div>
		<div class="bg-card border border-border rounded-xl p-5">
			<p class="text-muted-foreground text-sm">Max Drawdown</p>
			<p class="text-2xl font-bold mt-1 text-red-400">{performanceStats.maxDrawdown}%</p>
		</div>
		<div class="bg-card border border-border rounded-xl p-5">
			<p class="text-muted-foreground text-sm">Win Rate</p>
			<p class="text-2xl font-bold mt-1">{performanceStats.winRate}%</p>
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
								<svelte:component this={EquityChart} />
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
								<span class="font-medium">{performanceStats.profitFactor}</span>
							</div>
							<div class="flex justify-between py-2 border-b border-border/50">
								<span class="text-muted-foreground">Average Trade</span>
								<span class="font-medium ${performanceStats.avgTrade >= 0 ? 'text-green-400' : 'text-red-400'}">
									{performanceStats.avgTrade >= 0 ? '+' : ''}${performanceStats.avgTrade}
								</span>
							</div>
							<div class="flex justify-between py-2 border-b border-border/50">
								<span class="text-muted-foreground">Average Win</span>
								<span class="font-medium text-green-400">+${performanceStats.avgWin}</span>
							</div>
							<div class="flex justify-between py-2 border-b border-border/50">
								<span class="text-muted-foreground">Average Loss</span>
								<span class="font-medium text-red-400">${performanceStats.avgLoss}</span>
							</div>
							<div class="flex justify-between py-2 border-b border-border/50">
								<span class="text-muted-foreground">Best Trade</span>
								<span class="font-medium text-green-400">+${performanceStats.bestTrade.toLocaleString()}</span>
							</div>
							<div class="flex justify-between py-2">
								<span class="text-muted-foreground">Worst Trade</span>
								<span class="font-medium text-red-400">${performanceStats.worstTrade.toLocaleString()}</span>
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
							{#each tradeDistribution as item}
								<div class="flex items-center gap-3">
									<span class="text-sm w-16">${item.range}</span>
									<div class="flex-1 h-6 bg-background rounded-full overflow-hidden">
										<div class="h-full bg-primary rounded-full flex items-center justify-end px-2" style="width: {(item.count / 31) * 100}%">
											<span class="text-xs">{item.count}</span>
										</div>
									</div>
								</div>
							{/each}
						</div>
					</div>
					
					<!-- Trade Stats -->
					<div class="bg-muted rounded-lg p-5">
						<h3 class="font-semibold mb-4">Trade Statistics</h3>
						<div class="grid grid-cols-2 gap-4">
							<div class="text-center p-4 bg-background rounded-lg">
								<p class="text-3xl font-bold">{performanceStats.totalTrades}</p>
								<p class="text-sm text-muted-foreground mt-1">Total Trades</p>
							</div>
							<div class="text-center p-4 bg-background rounded-lg">
								<p class="text-3xl font-bold text-green-400">{performanceStats.winningTrades}</p>
								<p class="text-sm text-muted-foreground mt-1">Winning</p>
							</div>
							<div class="text-center p-4 bg-background rounded-lg">
								<p class="text-3xl font-bold text-red-400">{performanceStats.losingTrades}</p>
								<p class="text-sm text-muted-foreground mt-1">Losing</p>
							</div>
							<div class="text-center p-4 bg-background rounded-lg">
								<p class="text-3xl font-bold">{performanceStats.winRate}%</p>
								<p class="text-sm text-muted-foreground mt-1">Win Rate</p>
							</div>
						</div>
					</div>
				</div>
				
			{:else if activeTab === 'monthly'}
				<div class="bg-muted rounded-lg p-5">
					<h3 class="font-semibold mb-4">Monthly Returns</h3>
					<div class="grid grid-cols-7 gap-2">
						{#each monthlyReturns as month}
							<div class="text-center">
								<div class="h-32 bg-background rounded-lg relative flex items-end justify-center p-2">
									<div 
										class="w-full rounded {month.return >= 0 ? 'bg-green-500/50' : 'bg-red-500/50'}"
										style="height: {Math.abs(month.return) * 5}%"
									></div>
								</div>
								<p class="text-sm mt-2">{month.month}</p>
								<p class="text-xs {month.return >= 0 ? 'text-green-400' : 'text-red-400'}">
									{month.return >= 0 ? '+' : ''}{month.return}%
								</p>
							</div>
						{/each}
					</div>
				</div>
			{/if}
		</div>
	</div>
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