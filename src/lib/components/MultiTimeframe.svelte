<script lang="ts">
	import { onMount } from 'svelte';
	import { createChart, type IChartApi, type ISeriesApi, type Time } from 'lightweight-charts';
	import { binanceWS } from '../websocket';
	
	export let activeTimeframe = '1m';
	
	let container: HTMLDivElement;
	let chart: IChartApi;
	let candleSeries: ISeriesApi<'Candlestick'>;
	let ema20Series: ISeriesApi<'Line'>;
	let ema50Series: ISeriesApi<'Line'>;
	
	const timeframes = [
		{ label: '1m', value: '1m', interval: '1m' },
		{ label: '5m', value: '5m', interval: '5m' },
		{ label: '15m', value: '15m', interval: '15m' },
		{ label: '1h', value: '1h', interval: '1h' },
		{ label: '4h', value: '4h', interval: '4h' },
		{ label: '1d', value: '1d', interval: '1d' }
	];
	
	// Store candle data per timeframe
	const timeframeData = new Map<string, any[]>();
	
	function initChart() {
		chart = createChart(container, {
			layout: {
				background: { color: '#0a0a0a' },
				textColor: '#d1d5db'
			},
			grid: {
				vertLines: { color: '#1f2937' },
				horzLines: { color: '#1f2937' }
			},
			crosshair: { mode: 1 },
			rightPriceScale: { borderColor: '#374151' },
			timeScale: { borderColor: '#374151', timeVisible: true },
			width: container.clientWidth,
			height: container.clientHeight
		});
		
		candleSeries = chart.addCandlestickSeries({
			upColor: '#10b981',
			downColor: '#ef4444',
			borderUpColor: '#10b981',
			borderDownColor: '#ef4444',
			wickUpColor: '#10b981',
			wickDownColor: '#ef4444'
		});
		
		ema20Series = chart.addLineSeries({ color: '#f59e0b', lineWidth: 2 });
		ema50Series = chart.addLineSeries({ color: '#8b5cf6', lineWidth: 2 });
		
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
	}
	
	async function fetchHistoricalData(timeframe: string) {
		// Fetch from Binance REST API
		const symbol = 'BTCUSDT';
		const limit = 500;
		const url = `https://fapi.binance.com/fapi/v1/klines?symbol=${symbol}&interval=${timeframe}&limit=${limit}`;
		
		try {
			const res = await fetch(url);
			const data = await res.json();
			
			const candles = data.map((d: any[]) => ({
				time: Math.floor(d[0] / 1000) as Time,
				open: parseFloat(d[1]),
				high: parseFloat(d[2]),
				low: parseFloat(d[3]),
				close: parseFloat(d[4]),
				volume: parseFloat(d[5])
			}));
			
			timeframeData.set(timeframe, candles);
			return candles;
		} catch (err) {
			console.error('Failed to fetch historical data:', err);
			return [];
		}
	}
	
	function calculateEMA(data: { time: Time; value: number }[], period: number) {
		const k = 2 / (period + 1);
		const ema: { time: Time; value: number }[] = [];
		let prevEma = data[0]?.value || 0;
		
		for (let i = 0; i < data.length; i++) {
			if (i === 0) {
				ema.push({ time: data[i].time, value: data[i].value });
			} else {
				const currentEma = data[i].value * k + prevEma * (1 - k);
				ema.push({ time: data[i].time, value: currentEma });
				prevEma = currentEma;
			}
		}
		return ema;
	}
	
	async function switchTimeframe(tf: string) {
		activeTimeframe = tf;
		
		let candles = timeframeData.get(tf);
		if (!candles) {
			candles = await fetchHistoricalData(tf);
		}
		
		if (candles && candles.length > 0) {
			candleSeries.setData(candles);
			
			const closes = candles.map((c: any) => ({ time: c.time, value: c.close }));
			if (closes.length >= 20) {
				ema20Series.setData(calculateEMA(closes, 20));
			}
			if (closes.length >= 50) {
				ema50Series.setData(calculateEMA(closes, 50));
			}
			
			chart.timeScale().fitContent();
		}
	}
	
	onMount(() => {
		const cleanup = initChart();
		switchTimeframe(activeTimeframe);
		
		// Subscribe to WS for 1m updates
		const unsubscribe = binanceWS.subscribe(state => {
			if (activeTimeframe === '1m' && state.candles.length > 0) {
				const latest = state.candles[state.candles.length - 1];
				candleSeries.update(latest);
			}
		});
		
		return () => {
			unsubscribe();
			cleanup();
		};
	});
</script>

<div class="w-full h-full flex flex-col">
	<div class="flex items-center justify-between mb-2">
		<span class="text-sm font-semibold">Multi-Timeframe</span>
		<div class="flex gap-1">
			{#each timeframes as tf}
				<button
					class="rounded px-2 py-0.5 text-xs font-medium transition-all {activeTimeframe === tf.value ? 'bg-primary text-primary-foreground' : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'}"
					on:click={() => switchTimeframe(tf.value)}
				>
					{tf.label}
				</button>
			{/each}
		</div>
	</div>
	<div bind:this={container} class="flex-1 min-h-[300px]"></div>
</div>
