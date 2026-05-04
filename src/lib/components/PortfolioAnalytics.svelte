<script lang="ts">
	import { onMount } from 'svelte';
	import { createChart, type IChartApi, type ISeriesApi, type Time } from 'lightweight-charts';
	import Icon from './Icon.svelte';
	
	interface MonthlyPnL {
		month: string;
		pnl: number;
		trades: number;
	}
	
	const monthlyData: MonthlyPnL[] = [
		{ month: 'Jan', pnl: 450, trades: 23 },
		{ month: 'Feb', pnl: -120, trades: 18 },
		{ month: 'Mar', pnl: 680, trades: 31 },
		{ month: 'Apr', pnl: 320, trades: 25 },
		{ month: 'May', pnl: 890, trades: 28 },
		{ month: 'Jun', pnl: -45, trades: 15 }
	];
	
	let container: HTMLDivElement;
	let chart: IChartApi;
	
	$: totalPnL = monthlyData.reduce((sum, m) => sum + m.pnl, 0);
	$: avgMonthly = totalPnL / monthlyData.length;
	$: bestMonth = monthlyData.reduce((max, m) => m.pnl > max.pnl ? m : max, monthlyData[0]);
	$: worstMonth = monthlyData.reduce((min, m) => m.pnl < min.pnl ? m : min, monthlyData[0]);
	$: winMonths = monthlyData.filter(m => m.pnl > 0).length;
	
	// Mock correlation matrix
	const correlations = [
		{ pair: 'BTC-ETH', corr: 0.82 },
		{ pair: 'BTC-SOL', corr: 0.65 },
		{ pair: 'ETH-SOL', corr: 0.71 }
	];
	
	onMount(() => {
		chart = createChart(container, {
			layout: { background: { color: 'transparent' }, textColor: '#9ca3af' },
			grid: { vertLines: { color: 'transparent' }, horzLines: { color: '#1f2937' } },
			rightPriceScale: { borderColor: '#374151' },
			timeScale: { borderColor: '#374151', visible: false },
			crosshair: { mode: 0 },
			width: container.clientWidth,
			height: container.clientHeight
		});
		
		const series = chart.addHistogramSeries({
			color: '#3b82f6'
		});
		
		const data = monthlyData.map((m, i) => ({
			time: i as Time,
			value: m.pnl,
			color: m.pnl >= 0 ? '#10b98180' : '#ef444480'
		}));
		
		series.setData(data);
		
		const resizeObserver = new ResizeObserver(entries => {
			for (const entry of entries) {
				chart.applyOptions({ width: entry.contentRect.width, height: entry.contentRect.height });
			}
		});
		resizeObserver.observe(container);
		
		return () => {
			resizeObserver.disconnect();
			chart.remove();
		};
	});
</script>

<div class="rounded-lg border bg-card p-4">
	<h2 class="text-sm font-semibold mb-4">Portfolio Analytics</h2>
	
	<!-- Stats Grid -->
	<div class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
		<div class="rounded bg-secondary/50 p-3">
			<p class="text-xs text-muted-foreground">Total P&L (6M)</p>
			<p class="text-lg font-bold {totalPnL >= 0 ? 'text-emerald-400' : 'text-red-400'}">
				{totalPnL >= 0 ? '+' : ''}${totalPnL.toLocaleString()}
			</p>
		</div>
		<div class="rounded bg-secondary/50 p-3">
			<p class="text-xs text-muted-foreground">Avg Monthly</p>
			<p class="text-lg font-bold {avgMonthly >= 0 ? 'text-emerald-400' : 'text-red-400'}">
				{avgMonthly >= 0 ? '+' : ''}${avgMonthly.toFixed(0)}
			</p>
		</div>
		<div class="rounded bg-secondary/50 p-3">
			<p class="text-xs text-muted-foreground">Win Months</p>
			<p class="text-lg font-bold">{winMonths}/{monthlyData.length}</p>
			<p class="text-xs text-muted-foreground">{((winMonths/monthlyData.length)*100).toFixed(0)}%</p>
		</div>
		<div class="rounded bg-secondary/50 p-3">
			<p class="text-xs text-muted-foreground">Best/Worst</p>
			<p class="text-sm font-bold text-emerald-400">+${bestMonth.pnl}</p>
			<p class="text-sm font-bold text-red-400">${worstMonth.pnl}</p>
		</div>
	</div>
	
	<!-- Monthly P&L Chart -->
	<div class="mb-4">
		<p class="text-xs text-muted-foreground mb-2">Monthly P&L</p>
		<div bind:this={container} class="w-full h-[150px]"></div>
	</div>
	
	<!-- Correlation Matrix -->
	<div>
		<p class="text-xs text-muted-foreground mb-2">Position Correlations</p>
		<div class="space-y-2">
			{#each correlations as corr}
				<div class="flex items-center justify-between rounded bg-secondary/50 px-3 py-2">
					<span class="text-sm">{corr.pair}</span>
					<div class="flex items-center gap-2">
						<div class="h-2 w-24 rounded-full bg-secondary">
							<div 
								class="h-full rounded-full {corr.corr > 0.7 ? 'bg-red-500' : corr.corr > 0.5 ? 'bg-amber-500' : 'bg-emerald-500'}"
								style="width: {corr.corr * 100}%"
							></div>
						</div>
						<span class="text-xs font-medium {corr.corr > 0.7 ? 'text-red-400' : ''}">{corr.corr.toFixed(2)}</span>
					</div>
				</div>
			{/each}
		</div>
		{#if correlations.some(c => c.corr > 0.7)}
			<p class="mt-2 text-xs text-red-400">
				<Icon name="warning" size="0.875rem" class_name="text-red-400" />
				High correlation detected — risk of concentrated exposure
			</p>
		{/if}
	</div>
</div>
