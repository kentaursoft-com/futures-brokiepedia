<script lang="ts">
	import { onMount } from 'svelte';
	import { createChart, LineSeries, type IChartApi, type ISeriesApi } from 'lightweight-charts';
	
	interface EquityPoint {
		time: number;
		value: number;
	}
	
	let container: HTMLDivElement;
	let chart: IChartApi;
	let equitySeries: ISeriesApi<'Line'>;
	let drawdownSeries: ISeriesApi<'Line'>;
	
	// Generate mock equity curve data
	function generateEquityData(): { equity: EquityPoint[]; drawdown: EquityPoint[] } {
		const equity: EquityPoint[] = [];
		const drawdown: EquityPoint[] = [];
		let currentEquity = 10000;
		let peak = 10000;
		const now = Math.floor(Date.now() / 1000);
		const days = 30;
		
		for (let i = days; i >= 0; i--) {
			const time = now - (i * 86400);
			const change = (Math.random() - 0.45) * 200; // Slightly positive bias
			currentEquity += change;
			if (currentEquity > peak) peak = currentEquity;
			
			const dd = ((peak - currentEquity) / peak) * 100;
			
			equity.push({ time, value: currentEquity });
			drawdown.push({ time, value: dd });
		}
		
		return { equity, drawdown };
	}
	
	onMount(() => {
		chart = createChart(container, {
			layout: {
				background: { color: 'transparent' },
				textColor: '#9ca3af'
			},
			grid: {
				vertLines: { color: '#1f2937' },
				horzLines: { color: '#1f2937' }
			},
			rightPriceScale: {
				borderColor: '#374151',
				scaleMargins: { top: 0.1, bottom: 0.3 }
			},
			leftPriceScale: {
				visible: true,
				borderColor: '#374151',
				scaleMargins: { top: 0.1, bottom: 0.3 }
			},
			timeScale: {
				borderColor: '#374151',
				timeVisible: false
			},
			crosshair: { mode: 1 },
			width: container.clientWidth,
			height: container.clientHeight
		});
		
		equitySeries = chart.addLineSeries({
			color: '#3b82f6',
			lineWidth: 2,
			priceScaleId: 'right'
		});
		
		drawdownSeries = chart.addLineSeries({
			color: '#ef4444',
			lineWidth: 1,
			lineStyle: 2,
			priceScaleId: 'left'
		});
		
		const data = generateEquityData();
		equitySeries.setData(data.equity);
		drawdownSeries.setData(data.drawdown);
		
		// Add area fill to equity
		equitySeries.applyOptions({
			lastValueVisible: true,
			priceLineVisible: true
		});
		
		const resizeObserver = new ResizeObserver(entries => {
			for (const entry of entries) {
				chart.applyOptions({
					width: entry.contentRect.width,
					height: entry.contentRect.height
				});
			}
		});
		resizeObserver.observe(container);
		
		return () => {
			resizeObserver.disconnect();
			chart.remove();
		};
	});
</script>

<div bind:this={container} class="w-full h-full min-h-[200px]"></div>
