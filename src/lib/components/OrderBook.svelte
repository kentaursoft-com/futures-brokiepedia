<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { binanceWS } from '../websocket';
	
	interface OrderLevel {
		price: number;
		size: number;
		total: number;
	}
	
	let bids: OrderLevel[] = [];
	let asks: OrderLevel[] = [];
	let spread = 0;
	let lastPrice = 0;
	let ws: WebSocket | null = null;
	let currentBasePrice = 0;
	
	// Subscribe to price updates from main WebSocket
	const unsubscribe = binanceWS.subscribe(state => {
		if (state.lastPrice > 0) {
			currentBasePrice = state.lastPrice;
			lastPrice = state.lastPrice;
			generateOrderBookData(currentBasePrice);
		}
	});
	
	function generateOrderBookData(basePrice: number) {
		if (basePrice <= 0) return;
		
		const newBids: OrderLevel[] = [];
		const newAsks: OrderLevel[] = [];
		let bidTotal = 0;
		let askTotal = 0;
		
		for (let i = 0; i < 10; i++) {
			const bidPrice = basePrice - (i * 5) - Math.random() * 3;
			const bidSize = 0.5 + Math.random() * 2;
			bidTotal += bidSize;
			newBids.push({ price: bidPrice, size: bidSize, total: bidTotal });
			
			const askPrice = basePrice + (i * 5) + Math.random() * 3;
			const askSize = 0.5 + Math.random() * 2;
			askTotal += askSize;
			newAsks.push({ price: askPrice, size: askSize, total: askTotal });
		}
		
		bids = newBids;
		asks = newAsks;
		spread = asks[0].price - bids[0].price;
	}
	
	function connectRealOrderBook() {
		// Connect to Binance depth stream
		ws = new WebSocket('wss://fstream.binance.com/ws/btcusdt@depth20@100ms');
		
		ws.onopen = () => {
			console.log('[OrderBook WS] Connected');
		};
		
		ws.onmessage = (event) => {
			const data = JSON.parse(event.data);
			
			if (data.b && data.a) {
				// Process bids
				const newBids: OrderLevel[] = [];
				let bidTotal = 0;
				data.b.slice(0, 10).forEach(([price, size]: [string, string]) => {
					const p = parseFloat(price);
					const s = parseFloat(size);
					if (s > 0) {
						bidTotal += s;
						newBids.push({ price: p, size: s, total: bidTotal });
					}
				});
				
				// Process asks
				const newAsks: OrderLevel[] = [];
				let askTotal = 0;
				data.a.slice(0, 10).forEach(([price, size]: [string, string]) => {
					const p = parseFloat(price);
					const s = parseFloat(size);
					if (s > 0) {
						askTotal += s;
						newAsks.push({ price: p, size: s, total: askTotal });
					}
				});
				
				if (newBids.length > 0 && newAsks.length > 0) {
					bids = newBids;
					asks = newAsks;
					spread = newAsks[0].price - newBids[0].price;
					lastPrice = (newAsks[0].price + newBids[0].price) / 2;
				}
			}
		};
		
		ws.onclose = () => {
			console.log('[OrderBook WS] Disconnected, reconnecting...');
			setTimeout(connectRealOrderBook, 3000);
		};
		
		ws.onerror = (err) => {
			console.error('[OrderBook WS] Error:', err);
			ws?.close();
		};
	}
	
	let cleanup: () => void;
	
	onMount(() => {
		// Try real WebSocket first, fallback to generated data
		connectRealOrderBook();
		
		// Fallback: update generated data every 2 seconds if real WS fails
		const interval = setInterval(() => {
			if (bids.length === 0 && currentBasePrice > 0) {
				generateOrderBookData(currentBasePrice);
			}
		}, 2000);
		
		cleanup = () => {
			clearInterval(interval);
			ws?.close();
		};
	});
	
	onDestroy(() => {
		cleanup?.();
		unsubscribe();
	});
	
	function getMaxTotal(levels: OrderLevel[]) {
		return Math.max(...levels.map(l => l.total));
	}
	
	$: maxBidTotal = getMaxTotal(bids);
	$: maxAskTotal = getMaxTotal(asks);
</script>

<div class="rounded-lg border bg-card p-4">
	<div class="flex items-center justify-between mb-4">
		<h2 class="text-sm font-semibold">Order Book</h2>
		<div class="text-xs text-muted-foreground">
			Spread: <span class="text-amber-400">${spread.toFixed(2)}</span>
		</div>
	</div>
	
	<!-- Asks (sell orders) -->
	<div class="space-y-0.5 mb-2">
		<div class="grid grid-cols-3 text-xs text-muted-foreground mb-1">
			<span class="text-right">Price</span>
			<span class="text-right">Size</span>
			<span class="text-right">Total</span>
		</div>
		{#each asks.slice().reverse() as ask}
			<div class="grid grid-cols-3 text-xs relative">
				<div 
					class="absolute right-0 top-0 h-full bg-red-500/10 transition-all"
					style="width: {(ask.total / maxAskTotal) * 100}%"
				></div>
				<span class="text-right text-red-400 relative z-10">{ask.price.toFixed(2)}</span>
				<span class="text-right relative z-10">{ask.size.toFixed(4)}</span>
				<span class="text-right relative z-10 text-muted-foreground">{ask.total.toFixed(4)}</span>
			</div>
		{/each}
	</div>
	
	<!-- Current Price -->
	<div class="py-2 text-center border-y border-border">
		<span class="text-lg font-bold {lastPrice > 0 ? 'text-emerald-400' : 'text-red-400'}">
			${lastPrice.toLocaleString('en-US', { minimumFractionDigits: 2 })}
		</span>
	</div>
	
	<!-- Bids (buy orders) -->
	<div class="space-y-0.5 mt-2">
		{#each bids as bid}
			<div class="grid grid-cols-3 text-xs relative">
				<div 
					class="absolute right-0 top-0 h-full bg-emerald-500/10 transition-all"
					style="width: {(bid.total / maxBidTotal) * 100}%"
				></div>
				<span class="text-right text-emerald-400 relative z-10">{bid.price.toFixed(2)}</span>
				<span class="text-right relative z-10">{bid.size.toFixed(4)}</span>
				<span class="text-right relative z-10 text-muted-foreground">{bid.total.toFixed(4)}</span>
			</div>
		{/each}
	</div>
</div>
