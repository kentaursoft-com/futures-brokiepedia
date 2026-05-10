<script lang="ts">
	import { onMount } from 'svelte';
	import { createChart, type IChartApi, type ISeriesApi, type Time } from 'lightweight-charts';
	import { binanceWS, type Candle } from '../websocket';
	
	export let height = 120;
	
	let rsiContainer: HTMLDivElement;
	let macdContainer: HTMLDivElement;
	let atrContainer: HTMLDivElement;
	
	let rsiChart: IChartApi;
	let macdChart: IChartApi;
	let atrChart: IChartApi;
	
	let rsiSeries: ISeriesApi<'Line'>;
	let macdLineSeries: ISeriesApi<'Line'>;
	let macdSignalSeries: ISeriesApi<'Line'>;
	let macdHistSeries: ISeriesApi<'Histogram'>;
	let atrSeries: ISeriesApi<'Line'>;
	
	function calculateRSI(data: { time: Time; value: number }[], period = 14) {
		if (data.length < period + 1) return [];
		const rsi: { time: Time; value: number }[] = [];
		let gains = 0, losses = 0;
		
		// Initial average
		for (let i = 1; i <= period; i++) {
			const change = data[i].value - data[i - 1].value;
			if (change > 0) gains += change;
			else losses -= change;
		}
		
		let avgGain = gains / period;
		let avgLoss = losses / period;
		
		for (let i = period; i < data.length; i++) {
			const change = data[i].value - data[i - 1].value;
			const gain = change > 0 ? change : 0;
			const loss = change < 0 ? -change : 0;
			
			avgGain = (avgGain * (period - 1) + gain) / period;
			avgLoss = (avgLoss * (period - 1) + loss) / period;
			
			const rs = avgLoss === 0 ? 100 : avgGain / avgLoss;
			const rsiValue = avgLoss === 0 ? 100 : 100 - (100 / (1 + rs));
			
			rsi.push({ time: data[i].time, value: rsiValue });
		}
		
		return rsi;
	}
	
	function calculateMACD(data: { time: Time; value: number }[], fast = 12, slow = 26, signal = 9) {
		if (data.length < slow) return { macd: [], signal: [], histogram: [] };
		
		const ema = (values: number[], period: number) => {
			const k = 2 / (period + 1);
			const result: number[] = [values[0]];
			for (let i = 1; i < values.length; i++) {
				result.push(values[i] * k + result[i - 1] * (1 - k));
			}
			return result;
		};
		
		const closes = data.map(d => d.value);
		const emaFast = ema(closes, fast);
		const emaSlow = ema(closes, slow);
		
		const macdLine = emaFast.map((v, i) => v - emaSlow[i]);
		const signalLine = ema(macdLine.slice(slow - fast), signal);
		
		const macd: { time: Time; value: number }[] = [];
		const sig: { time: Time; value: number }[] = [];
		const hist: { time: Time; value: number; color?: string }[] = [];
		
		for (let i = 0; i < signalLine.length; i++) {
			const idx = i + slow - fast + signal - 1;
			if (idx < data.length) {
				const m = macdLine[idx];
				const s = signalLine[i];
				macd.push({ time: data[idx].time, value: m });
				sig.push({ time: data[idx].time, value: s });
				hist.push({
					time: data[idx].time,
					value: m - s,
					color: m - s >= 0 ? '#10b98180' : '#ef444480'
				});
			}
		}
		
		return { macd, signal: sig, histogram: hist };
	}
	
	function calculateATR(data: Candle[], period = 14) {
		if (data.length < period + 1) return [];
		const atr: { time: Time; value: number }[] = [];
		let trSum = 0;
		
		for (let i = 1; i <= period; i++) {
			const tr = Math.max(
				data[i].high - data[i].low,
				Math.abs(data[i].high - data[i - 1].close),
				Math.abs(data[i].low - data[i - 1].close)
			);
			trSum += tr;
		}
		
		let atrValue = trSum / period;
		atr.push({ time: data[period].time as any, value: atrValue });
		
		for (let i = period + 1; i < data.length; i++) {
			const tr = Math.max(
				data[i].high - data[i].low,
				Math.abs(data[i].high - data[i - 1].close),
				Math.abs(data[i].low - data[i - 1].close)
			);
			atrValue = (atrValue * (period - 1) + tr) / period;
			atr.push({ time: data[i].time as any, value: atrValue });
		}
		
		return atr;
	}
	
	function createMiniChart(container: HTMLDivElement) {
		const chart = createChart(container, {
			layout: {
				background: { color: 'transparent' },
				textColor: '#9ca3af'
			},
			grid: {
				vertLines: { color: 'transparent' },
				horzLines: { color: '#1f2937' }
			},
			rightPriceScale: {
				borderColor: '#374151',
				scaleMargins: { top: 0.1, bottom: 0.1 }
			},
			timeScale: {
				borderColor: '#374151',
				visible: false
			},
			crosshair: { mode: 0 },
			width: container.clientWidth,
			height: container.clientHeight
		});
		return chart;
	}
	
	onMount(() => {
		// Connect to Binance WebSocket
		binanceWS.connect();
		
		// RSI Chart
		rsiChart = createMiniChart(rsiContainer);
		rsiSeries = rsiChart.addLineSeries({
			color: '#3b82f6',
			lineWidth: 2
		});
		rsiSeries.createPriceLine({
			price: 70,
			color: '#ef4444',
			lineWidth: 1,
			lineStyle: 2
		});
		rsiSeries.createPriceLine({
			price: 30,
			color: '#10b981',
			lineWidth: 1,
			lineStyle: 2
		});
		
		// MACD Chart
		macdChart = createMiniChart(macdContainer);
		macdHistSeries = macdChart.addHistogramSeries({
			color: '#3b82f6'
		});
		macdLineSeries = macdChart.addLineSeries({
			color: '#f59e0b',
			lineWidth: 2
		});
		macdSignalSeries = macdChart.addLineSeries({
			color: '#8b5cf6',
			lineWidth: 2
		});
		
		// ATR Chart
		atrChart = createMiniChart(atrContainer);
		atrSeries = atrChart.addLineSeries({
			color: '#ec4899',
			lineWidth: 2
		});
		
		// Subscribe to data
		const unsubscribe = binanceWS.subscribe(state => {
			if (state.candles.length < 50) return;
			
			const closes = state.candles.map(c => ({ time: c.time as any, value: c.close }));
			
			// Update RSI
			const rsi = calculateRSI(closes);
			if (rsi.length > 0) rsiSeries.setData(rsi as any);
			
			// Update MACD
			const macd = calculateMACD(closes);
			if (macd.macd.length > 0) {
				macdLineSeries.setData(macd.macd);
				macdSignalSeries.setData(macd.signal);
				macdHistSeries.setData(macd.histogram as any);
			}
			
			// Update ATR
			const atr = calculateATR(state.candles);
			if (atr.length > 0) atrSeries.setData(atr);
		});
		
		return () => {
			unsubscribe();
			rsiChart.remove();
			macdChart.remove();
			atrChart.remove();
		};
	});
</script>

<div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
	<!-- RSI -->
	<div class="rounded-lg border bg-card p-3">
		<div class="flex items-center justify-between mb-2">
			<span class="text-xs font-semibold text-muted-foreground">RSI (14)</span>
			<span class="text-xs text-blue-400">14-period</span>
		</div>
		<div bind:this={rsiContainer} style="height: {height}px;"></div>
	</div>
	
	<!-- MACD -->
	<div class="rounded-lg border bg-card p-3">
		<div class="flex items-center justify-between mb-2">
			<span class="text-xs font-semibold text-muted-foreground">MACD</span>
			<div class="flex gap-2 text-xs">
				<span class="text-amber-400">Line</span>
				<span class="text-purple-400">Signal</span>
			</div>
		</div>
		<div bind:this={macdContainer} style="height: {height}px;"></div>
	</div>
	
	<!-- ATR -->
	<div class="rounded-lg border bg-card p-3">
		<div class="flex items-center justify-between mb-2">
			<span class="text-xs font-semibold text-muted-foreground">ATR (14)</span>
			<span class="text-xs text-pink-400">Volatility</span>
		</div>
		<div bind:this={atrContainer} style="height: {height}px;"></div>
	</div>
</div>
