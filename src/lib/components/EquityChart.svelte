<script lang="ts">
	import { onMount } from 'svelte';
	import { createChart, type IChartApi, type ISeriesApi, type Time } from 'lightweight-charts';
	
	interface EquityPoint {
		time: number;
		value: number;
	}
	
	export let data: EquityPoint[] = [];
	
	let container: HTMLDivElement;
	let chart: IChartApi;
	let equitySeries: ISeriesApi<'Line'>;
	let drawdownSeries: ISeriesApi<'Line'>;
	
	function processData(points: EquityPoint[]): { equity: any[]; drawdown: any[] } {
		if (!points || points.length === 0) {
			return { equity: [], drawdown: [] };
		}
		
		const equity: any[] = [];
		const drawdown: any[] = [];
		let peak = 0;
		
		for (const point of points) {
			// Convert ms timestamp to seconds for lightweight-charts
			const time = Math.floor(point.time / 1000) as Time;
			const value = point.value;
			
			if (value > peak) peak = value;
			const dd = peak > 0 ? ((peak - value) / peak) * 100 : 0;
			
			equity.push({ time, value });
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
		
		const processed = processData(data);
		if (processed.equity.length > 0) {
			equitySeries.setData(processed.equity);
			drawdownSeries.setData(processed.drawdown);
		}
		
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
