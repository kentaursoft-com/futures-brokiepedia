<script lang="ts">
	import { onMount } from 'svelte';
	import OrderBook from '$lib/components/OrderBook.svelte';
	import OrderForm from '$lib/components/OrderForm.svelte';
	import CryptoIcon from '$lib/components/CryptoIcon.svelte';
	import { binanceWS } from '$lib/websocket';
	
	let wsConnected = false;
	let activeTimeframe = '1m';
	
	const unsubscribe = binanceWS.subscribe(state => {
		wsConnected = state.connected;
	});
	
	const timeframes = ['1m', '5m', '15m', '1h', '4h', '1d'];
	
	onMount(() => {
		binanceWS.connect();
	});
</script>

<svelte:head>
	<title>Trade | Futures Brokiepedia</title>
</svelte:head>

<div class="h-full flex flex-col gap-4">
	<!-- Top Bar -->
	<div class="flex items-center justify-between bg-card border border-border rounded-lg p-4">
		<div class="flex items-center gap-6">
			<div>
				<div class="flex items-center gap-2">
					<CryptoIcon symbol="BTC" size={20} />
					<span class="text-muted-foreground text-sm">BTC-PERP</span>
				</div>
				<div class="flex items-center gap-2">
					<span class="text-2xl font-bold font-mono">$78,623.25</span>
					<span class="text-sm text-green-400">+1.24%</span>
				</div>
			</div>
			<div class="h-8 w-px bg-border"></div>
			<div class="flex gap-1">
				{#each timeframes as tf}
					<button 
						class="px-3 py-1 rounded text-sm transition-colors {activeTimeframe === tf ? 'bg-primary text-primary-foreground' : 'hover:bg-muted'}"
						on:click={() => activeTimeframe = tf}
					>
						{tf}
					</button>
				{/each}
			</div>
		</div>
		<div class="flex items-center gap-2">
			<div class="w-2 h-2 rounded-full {wsConnected ? 'bg-green-500' : 'bg-red-500'}"></div>
			<span class="text-sm text-muted-foreground">{wsConnected ? 'Live' : 'Disconnected'}</span>
		</div>
	</div>
	
	<!-- Main Trading Area -->
	<div class="flex-1 grid grid-cols-1 lg:grid-cols-4 gap-4 min-h-0">
		<!-- Chart Area -->
		<div class="lg:col-span-3 bg-card border border-border rounded-lg flex flex-col" style="min-height: 500px;">
			<div class="p-4 border-b border-border">
				<h2 class="font-semibold">Chart</h2>
			</div>
			<div class="flex-1 p-0" style="height: 500px;">
				<iframe 
					src="https://www.tradingview.com/widgetembed/?frameElementId=tradingview_chart&symbol=BINANCE:BTCUSDT&interval={activeTimeframe === '1m' ? '1' : activeTimeframe === '5m' ? '5' : activeTimeframe === '15m' ? '15' : activeTimeframe === '1h' ? '60' : activeTimeframe === '4h' ? '240' : 'D'}&hidesidetoolbar=1&symboledit=0&saveimage=0&toolbarbg=0a0a0a&studies=%5B%5D&theme=dark&style=1&timezone=Etc%2FUTC&locale=en"
					style="width: 100%; height: 100%; border: none; border-radius: 0 0 8px 8px;"
					title="TradingView Chart"
					loading="lazy"
				></iframe>
			</div>
		</div>
		
		<!-- Right Panel -->
		<div class="space-y-4 flex flex-col">
			<!-- Order Form -->
			<div class="bg-card border border-border rounded-lg p-4">
				<h3 class="font-semibold mb-3">Place Order</h3>
				<OrderForm />
			</div>
			
			<!-- Order Book -->
			<div class="bg-card border border-border rounded-lg flex-1 flex flex-col min-h-0">
				<div class="p-4 border-b border-border">
					<h3 class="font-semibold">Order Book</h3>
				</div>
				<div class="flex-1 p-4 overflow-auto">
					<OrderBook />
				</div>
			</div>
		</div>
	</div>
	
	<!-- Bottom Panel - Indicators -->
	<div class="bg-card border border-border rounded-lg p-4">
		<h3 class="font-semibold mb-3">Technical Indicators</h3>
		<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
			<div class="bg-muted rounded-lg p-3">
				<p class="text-xs text-muted-foreground mb-1">RSI (14)</p>
				<p class="text-xl font-bold text-blue-400">58.32</p>
				<p class="text-xs text-muted-foreground">Neutral</p>
			</div>
			<div class="bg-muted rounded-lg p-3">
				<p class="text-xs text-muted-foreground mb-1">MACD</p>
				<p class="text-xl font-bold text-yellow-400">+125.50</p>
				<p class="text-xs text-green-400">Bullish</p>
			</div>
			<div class="bg-muted rounded-lg p-3">
				<p class="text-xs text-muted-foreground mb-1">ATR (14)</p>
				<p class="text-xl font-bold text-pink-400">$342.15</p>
				<p class="text-xs text-muted-foreground">Normal volatility</p>
			</div>
		</div>
	</div>
</div>

<style>
	:global(.bg-card) { background-color: hsl(224 71% 6%); }
	:global(.border-border) { border-color: hsl(215 20% 18%); }
	:global(.text-muted-foreground) { color: hsl(215 20% 55%); }
	:global(.bg-muted) { background-color: hsl(215 20% 12%); }
	:global(.bg-primary) { background-color: hsl(217 91% 60%); }
	:global(.text-primary-foreground) { color: hsl(213 31% 91%); }
</style>
