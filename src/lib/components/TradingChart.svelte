<script lang="ts">
	import { onMount } from 'svelte';
	import { createChart, type IChartApi, type ISeriesApi, type Time } from 'lightweight-charts';
	import { binanceWS, type Candle } from '../websocket';

	let chartContainer: HTMLDivElement;
	let chart: IChartApi;
	let candleSeries: ISeriesApi<'Candlestick'>;
	let volumeSeries: ISeriesApi<'Histogram'>;
	let resizeObserver: ResizeObserver;

	// EMA overlays (calculated client-side for now)
	let ema20Series: ISeriesApi<'Line'>;
	let ema50Series: ISeriesApi<'Line'>;

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

	onMount(() => {
		chart = createChart(chartContainer, {
			width: chartContainer.clientWidth,
			height: chartContainer.clientHeight,
			layout: {
				background: { color: '#0a0a0a' },
				textColor: '#d1d5db'
			},
			grid: {
				vertLines: { color: '#1f2937' },
				horzLines: { color: '#1f2937' }
			},
			crosshair: {
				mode: 1
			},
			rightPriceScale: {
				borderColor: '#374151'
			},
			timeScale: {
				borderColor: '#374151',
				timeVisible: true
			}
		});

		candleSeries = chart.addCandlestickSeries({
			upColor: '#10b981',
			downColor: '#ef4444',
			borderUpColor: '#10b981',
			borderDownColor: '#ef4444',
			wickUpColor: '#10b981',
			wickDownColor: '#ef4444'
		});

		volumeSeries = chart.addHistogramSeries({
			color: '#3b82f6',
			priceFormat: { type: 'volume' },
			priceScaleId: ''
		});
		volumeSeries.priceScale().applyOptions({
			scaleMargins: {
				top: 0.8,
				bottom: 0
			}
		});

		ema20Series = chart.addLineSeries({
			color: '#f59e0b',
			lineWidth: 2,
			title: 'EMA 20'
		});

		ema50Series = chart.addLineSeries({
			color: '#8b5cf6',
			lineWidth: 2,
			title: 'EMA 50'
		});

		// Subscribe to candle updates
		const unsubscribe = binanceWS.subscribe(state => {
			if (state.candles.length > 0) {
				const chartData = state.candles.map((c: Candle) => ({
					time: c.time,
					open: c.open,
					high: c.high,
					low: c.low,
					close: c.close
				}));

				const volumeData = state.candles.map((c: Candle) => ({
					time: c.time,
					value: c.volume,
					color: c.close >= c.open ? '#10b98180' : '#ef444480'
				}));

				candleSeries.setData(chartData as any);
				volumeSeries.setData(volumeData as any);

				// Calculate and update EMAs
				const closes = state.candles.map(c => ({ time: c.time as any, value: c.close }));
				if (closes.length >= 20) {
					ema20Series.setData(calculateEMA(closes, 20) as any);
				}
				if (closes.length >= 50) {
					ema50Series.setData(calculateEMA(closes, 50) as any);
				}

				chart.timeScale().fitContent();
			}
		});

		// Handle resize
		resizeObserver = new ResizeObserver(entries => {
			for (const entry of entries) {
				chart.applyOptions({
					width: entry.contentRect.width,
					height: entry.contentRect.height
				});
			}
		});
		resizeObserver.observe(chartContainer);

		binanceWS.connect();

		return () => {
			unsubscribe();
			resizeObserver?.disconnect();
			binanceWS.disconnect();
			chart.remove();
		};
	});

</script>

<div bind:this={chartContainer} style="width: 100%; height: 500px;"></div>
