<script lang="ts">
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';
	import { api } from '$lib/api';
	import GlassCard from '$lib/components/GlassCard.svelte';

	let EquityChart: any;

	onMount(async () => {
		if (browser) {
			const equityModule = await import('$lib/components/EquityChart.svelte');
			EquityChart = equityModule.default;
		}
		loadAnalytics();
	});

	let analytics: any = null;
	let loading = true;
	let error: string | null = null;
	let maxTradeCount = 1;
	function barColor(range: string): string {
		return range.startsWith('+') ? 'bg-emerald-500/50' : 'bg-rose-500/50';
	}

	async function loadAnalytics() {
		try {
			loading = true;
			analytics = await api.getAnalytics();
			maxTradeCount = analytics?.tradeDistribution?.length
				? Math.max(...analytics.tradeDistribution.map((d: any) => d.count), 1)
				: 1;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load analytics';
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

<div class="space-y-5 max-w-7xl mx-auto pb-20 sm:pb-0">
	<!-- Header -->
	<div>
		<h1 class="text-2xl font-bold text-white/90 font-sans">Analytics</h1>
		<p class="text-zinc-400 text-sm mt-1 font-sans">Trading performance and statistics</p>
	</div>

	{#if loading}
		<div class="flex items-center justify-center py-20">
			<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-500"></div>
		</div>
	{:else if error}
		<GlassCard>
			<div class="p-6 text-center">
				<p class="text-rose-400 text-sm font-sans">{error}</p>
				<button
					class="mt-4 px-4 py-2 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-sm transition-colors"
					on:click={loadAnalytics}
				>Retry</button>
			</div>
		</GlassCard>
	{:else if analytics}
		<!-- Key Metrics -->
		<div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
			<GlassCard className="p-4 sm:p-5">
				<div class="text-xs text-zinc-500 font-sans uppercase tracking-wider">Total Return</div>
				<div class="text-2xl font-bold font-mono mt-1 {analytics.totalReturn >= 0 ? 'text-emerald-400' : 'text-rose-400'}">
					{analytics.totalReturn >= 0 ? '+' : ''}{analytics.totalReturn}%
				</div>
			</GlassCard>
			<GlassCard className="p-4 sm:p-5">
				<div class="text-xs text-zinc-500 font-sans uppercase tracking-wider">Sharpe Ratio</div>
				<div class="text-2xl font-bold font-mono mt-1 text-white/90">{analytics.sharpeRatio ?? '—'}</div>
			</GlassCard>
			<GlassCard className="p-4 sm:p-5">
				<div class="text-xs text-zinc-500 font-sans uppercase tracking-wider">Max Drawdown</div>
				<div class="text-2xl font-bold font-mono mt-1 text-rose-400">{analytics.maxDrawdown ?? '—'}%</div>
			</GlassCard>
			<GlassCard className="p-4 sm:p-5">
				<div class="text-xs text-zinc-500 font-sans uppercase tracking-wider">Win Rate</div>
				<div class="text-2xl font-bold font-mono mt-1 text-white/90">{analytics.winRate ?? '—'}%</div>
			</GlassCard>
		</div>

		<!-- Tabs Card -->
		<GlassCard>
			<!-- Tab Header -->
			<div class="flex gap-1 p-1 bg-zinc-800/40 rounded-xl border border-zinc-700/20 mx-4 sm:mx-6 mt-4 sm:mt-6">
				{#each tabs as tab}
					<button
						class="flex-1 py-2.5 px-3 rounded-lg text-sm font-medium transition-all duration-200 {activeTab === tab.id ? 'bg-zinc-700/80 text-white/90' : 'text-zinc-500 hover:text-zinc-300'}"
						on:click={() => activeTab = tab.id}
					>{tab.label}</button>
				{/each}
			</div>

			<!-- Tab Content -->
			<div class="p-4 sm:p-6">
				{#if activeTab === 'overview'}
					<div class="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
						<!-- Equity Curve -->
						<div class="bg-zinc-800/30 rounded-xl p-5 border border-zinc-700/20">
							<h3 class="text-sm font-semibold text-zinc-200 font-sans mb-4">Equity Curve</h3>
							<div class="h-64">
								{#if EquityChart}
									<svelte:component this={EquityChart} data={analytics.equityHistory} />
								{:else}
									<div class="h-full flex items-center justify-center text-sm text-zinc-500 font-sans">
										Loading chart...
									</div>
								{/if}
							</div>
						</div>

						<!-- Detailed Stats -->
						<div class="bg-zinc-800/30 rounded-xl p-5 border border-zinc-700/20">
							<h3 class="text-sm font-semibold text-zinc-200 font-sans mb-4">Detailed Statistics</h3>
							<div class="space-y-3">
								{#each [
									{ label: 'Profit Factor', value: analytics.profitFactor, color: '' },
									{ label: 'Average Trade', value: `$${analytics.avgTrade}`, color: analytics.avgTrade >= 0 ? 'text-emerald-400' : 'text-rose-400' },
									{ label: 'Average Win', value: `+$${analytics.avgWin}`, color: 'text-emerald-400' },
									{ label: 'Average Loss', value: `-$${Math.abs(analytics.avgLoss)}`, color: 'text-rose-400' },
									{ label: 'Best Trade', value: `+${analytics.bestTrade?.toLocaleString() || '$0'}`, color: 'text-emerald-400' },
									{ label: 'Worst Trade', value: `-${Math.abs(analytics.worstTrade)?.toLocaleString() || '$0'}`, color: 'text-rose-400' },
								] as item}
									<div class="flex justify-between py-2 border-b border-zinc-800/50 last:border-0">
										<span class="text-sm text-zinc-500 font-sans">{item.label}</span>
										<span class="text-sm font-mono font-semibold {item.color || 'text-zinc-200'}">{item.value}</span>
									</div>
								{/each}
							</div>
						</div>
					</div>

				{:else if activeTab === 'trades'}
					<div class="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
						<!-- Trade Distribution -->
						<div class="bg-zinc-800/30 rounded-xl p-5 border border-zinc-700/20">
							<h3 class="text-sm font-semibold text-zinc-200 font-sans mb-4">Trade Distribution</h3>
							<div class="space-y-3">
								{#if analytics.tradeDistribution && analytics.tradeDistribution.length > 0}
									{#each analytics.tradeDistribution as item}
										<div class="flex items-center gap-3">
											<span class="text-xs text-zinc-400 font-mono w-16 flex-shrink-0">{item.range}</span>
											<div class="flex-1 h-6 bg-zinc-800 rounded-full overflow-hidden">
												<div
													class="h-full rounded-full flex items-center justify-end px-2 text-xs font-mono transition-all {barColor(item.range)}"
													style="width: {(item.count / maxTradeCount) * 100}%"
												>
													<span class="text-white/80">{item.count}</span>
												</div>
											</div>
										</div>
									{/each}
								{:else}
									<p class="text-zinc-500 text-sm text-center py-8 font-sans">No trade data yet</p>
								{/if}
							</div>
						</div>

						<!-- Trade Stats -->
						<div class="bg-zinc-800/30 rounded-xl p-5 border border-zinc-700/20">
							<h3 class="text-sm font-semibold text-zinc-200 font-sans mb-4">Trade Statistics</h3>
							<div class="grid grid-cols-2 gap-3">
								{#each [
									{ label: 'Total Trades', value: analytics.totalTrades, color: 'text-white/90' },
									{ label: 'Winning', value: analytics.winningTrades, color: 'text-emerald-400' },
									{ label: 'Losing', value: analytics.losingTrades, color: 'text-rose-400' },
									{ label: 'Win Rate', value: `${analytics.winRate}%`, color: 'text-white/90' },
								] as stat}
									<div class="text-center p-4 bg-zinc-800/50 rounded-lg border border-zinc-700/20">
										<p class="text-2xl font-bold font-mono {stat.color}">{stat.value ?? '—'}</p>
										<p class="text-xs text-zinc-500 font-sans mt-1">{stat.label}</p>
									</div>
								{/each}
							</div>
						</div>
					</div>

				{:else if activeTab === 'monthly'}
					<div class="bg-zinc-800/30 rounded-xl p-5 border border-zinc-700/20">
						<h3 class="text-sm font-semibold text-zinc-200 font-sans mb-4">Monthly Returns</h3>
						{#if analytics.monthlyReturns && analytics.monthlyReturns.length > 0}
							<div class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-7 gap-3">
								{#each analytics.monthlyReturns as month}
									<div class="text-center">
										<div class="h-28 bg-zinc-800/60 rounded-lg relative flex items-end justify-center p-1.5 border border-zinc-700/20">
											<div
												class="w-full rounded transition-all {month.return >= 0 ? 'bg-emerald-500/60 border border-emerald-500/30' : 'bg-rose-500/60 border border-rose-500/30'}"
												style="height: {Math.max(Math.min(Math.abs(month.return) * 8, 100), 4)}%"
											></div>
										</div>
										<p class="text-xs text-zinc-400 font-sans mt-2">{month.month}</p>
										<p class="text-xs font-mono font-semibold {month.return >= 0 ? 'text-emerald-400' : 'text-rose-400'}">
											{month.return >= 0 ? '+' : ''}{month.return}%
										</p>
									</div>
								{/each}
							</div>
						{:else}
							<p class="text-zinc-500 text-sm text-center py-8 font-sans">No monthly data yet</p>
						{/if}
					</div>
				{/if}
			</div>
		</GlassCard>
	{/if}
</div>
