<script lang="ts">
	import { onMount } from 'svelte';
	import { createChart, type IChartApi, type ISeriesApi, type Time } from 'lightweight-charts';
	import Icon from './Icon.svelte';
	
	interface MonthlyReturn {
		month: string;
		return: number;
		trades: number;
	}
	
	export let monthlyReturns: MonthlyReturn[] = [];
	
	let container: HTMLDivElement;
	let chart: IChartApi;
	
	$: data = monthlyReturns || [];
	$: totalPnL = data.length > 0 ? data.reduce((sum, m) => sum + (m.return || 0), 0) : 0;
	$: avgMonthly = data.length > 0 ? totalPnL / data.length : 0;
	$: bestMonth = data.length > 0 ? data.reduce((max, m) => (m.return || 0) > (max.return || 0) ? m : max, data[0]) : { month: '-', return: 0 };
	$: worstMonth = data.length > 0 ? data.reduce((min, m) => (m.return || 0) < (min.return || 0) ? m : min, data[0]) : { month: '-', return: 0 };
	$: winMonths = data.filter(m => (m.return || 0) > 0).length;
	
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
		
		const chartData = data.map((m, i) => ({
			time: i as Time,
			value: m.return || 0,
			color: (m.return || 0) >= 0 ? '#10b98180' : '#ef444480'
		}));
		
		if (chartData.length > 0) {
			series.setData(chartData);
		}
		
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
			<p class="text-xs text-muted-foreground">Total Return</p>
			<p class="text-lg font-bold {totalPnL >= 0 ? 'text-emerald-400' : 'text-red-400'}">
				{totalPnL >= 0 ? '+' : ''}{totalPnL.toFixed(1)}%
			</p>
		</div>
		<div class="rounded bg-secondary/50 p-3">
			<p class="text-xs text-muted-foreground">Avg Monthly</p>
			<p class="text-lg font-bold {avgMonthly >= 0 ? 'text-emerald-400' : 'text-red-400'}">
				{avgMonthly >= 0 ? '+' : ''}{avgMonthly.toFixed(1)}%
			</p>
		</div>
		<div class="rounded bg-secondary/50 p-3">
			<p class="text-xs text-muted-foreground">Win Months</p>
			<p class="text-lg font-bold">{winMonths}/{data.length}</p>
			{#if data.length > 0}
				<p class="text-xs text-muted-foreground">{((winMonths/data.length)*100).toFixed(0)}%</p>
			{/if}
		</div>
		<div class="rounded bg-secondary/50 p-3">
			<p class="text-xs text-muted-foreground">Best/Worst</p>
			<p class="text-sm font-bold text-emerald-400">+{(bestMonth.return || 0).toFixed(1)}%</p>
			<p class="text-sm font-bold text-red-400">{(worstMonth.return || 0).toFixed(1)}%</p>
		</div>
	</div>
	
	<!-- Monthly P&L Chart -->
	<div class="mb-4">
		<p class="text-xs text-muted-foreground mb-2">Monthly Returns</p>
		{#if data.length > 0}
			<div bind:this={container} class="w-full h-[150px]"></div>
		{:else}
			<div class="w-full h-[150px] flex items-center justify-center text-muted-foreground text-sm">
				No data yet
			</div>
		{/if}
	</div>
</div>
