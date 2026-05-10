<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import { binanceWS } from '$lib/websocket';
	
	export let symbol: string = 'BTCUSDT';
	
	export let side: 'long' | 'short' = 'long';
	
	interface OrderParams {
		type: 'market' | 'limit' | 'stop' | 'stop_limit' | 'trailing_stop';
		size: number;
		price?: number;
		stopPrice?: number;
		trailingPercent: number;
		takeProfit?: number;
		stopLoss?: number;
	}
	
	let order: OrderParams = {
		type: 'market',
		size: 0.1,
		price: undefined,
		stopPrice: undefined,
		trailingPercent: 2,
		takeProfit: undefined,
		stopLoss: undefined,
	};
	
	let submitting = false;
	let result: { success?: boolean; message?: string; trade?: any } | null = null;
	let error: string | null = null;
	
	$: currentPrice = $binanceWS.lastPrice;
	
	$: {
		if ($binanceWS.prices[symbol]) {
			order.price = $binanceWS.prices[symbol];
		}
	}
	
	$: estimatedPnl = order.takeProfit && order.stopLoss && order.price
		? {
				profit: side === 'long' 
					? (order.takeProfit - order.price) * order.size
					: (order.price - order.takeProfit) * order.size,
				loss: side === 'long'
					? (order.stopLoss - order.price) * order.size
					: (order.price - order.stopLoss) * order.size
			}
		: null;
	
	async function submitOrder() {
		if (!order.price) {
			error = 'Price not available. Please wait for market data.';
			return;
		}
		try {
			submitting = true;
			error = null;
			result = null;
			const response = await api.executePaperTrade(symbol, side, order.size, 1.0);
			result = response;
			if (response.success) order.size = 0.1;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to submit order';
		} finally {
			submitting = false;
		}
	}
	
	function setSize(pct: number) {
		order.size = parseFloat((currentPrice ? (10000 * pct) / currentPrice : 0.1).toFixed(4)) || 0.1;
	}
	
	function setOrderType(type: string) {
		order.type = type as any;
	}
</script>

<div class="space-y-3">
	<!-- Order Type -->
	<div class="grid grid-cols-5 gap-1 p-1 bg-zinc-800/50 rounded-lg">
		{#each [{ id: 'market', label: 'Market' }, { id: 'limit', label: 'Limit' }, { id: 'stop', label: 'Stop' }, { id: 'stop_limit', label: 'S/L' }, { id: 'trailing_stop', label: 'T/S' }] as t}
			<button
				class="py-1.5 rounded-md text-xs font-medium transition-all {order.type === t.id ? 'bg-zinc-700/80 text-white/90' : 'text-zinc-500 hover:text-zinc-300'}"
				on:click={() => setOrderType(t.id)}
			>{t.label}</button>
		{/each}
	</div>

	<!-- Current Price Display -->
	<div class="flex items-center justify-between py-2 px-3 rounded-lg bg-zinc-800/30 border border-zinc-700/30">
		<span class="text-xs text-zinc-500 font-sans">Mark Price</span>
		<span class="text-sm font-mono font-semibold text-zinc-100">${order.price?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '—'}</span>
	</div>
	
	<!-- Size + Quick % buttons -->
	<div>
		<span class="text-xs text-zinc-500 font-sans block mb-1.5">Size ({symbol.replace('USDT', '')})
		<div class="flex gap-2">
			<input
				type="number"
				bind:value={order.size}
				step="0.001"
				min="0"
				class="flex-1 bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-white text-sm font-mono focus:outline-none focus:border-emerald-500"
			/>
			<button class="px-2.5 py-2 rounded-lg bg-zinc-800 border border-zinc-700 text-xs text-zinc-400 hover:text-zinc-200 hover:border-zinc-500 transition-colors font-mono" on:click={() => setSize(0.25)}>25%</button>
			<button class="px-2.5 py-2 rounded-lg bg-zinc-800 border border-zinc-700 text-xs text-zinc-400 hover:text-zinc-200 hover:border-zinc-500 transition-colors font-mono" on:click={() => setSize(0.50)}>50%</button>
			<button class="px-2.5 py-2 rounded-lg bg-zinc-800 border border-zinc-700 text-xs text-zinc-400 hover:text-zinc-200 hover:border-zinc-500 transition-colors font-mono" on:click={() => setSize(1.00)}>100%</button>
		</div>
	</div>
	
	<!-- Price inputs based on order type -->
	{#if order.type === 'limit' || order.type === 'stop_limit'}
		<div>
			<span class="text-xs text-zinc-500 font-sans block mb-1.5">Limit Price (USDT)
			<input type="number" bind:value={order.price} step="0.01"
				class="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-white text-sm font-mono focus:outline-none focus:border-emerald-500"
			/>
		</div>
	{/if}
	
	{#if order.type === 'stop' || order.type === 'stop_limit'}
		<div>
			<span class="text-xs text-zinc-500 font-sans block mb-1.5">Stop Price (USDT)
			<input type="number" bind:value={order.stopPrice} step="0.01"
				class="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-white text-sm font-mono focus:outline-none focus:border-red-500"
			/>
		</div>
	{/if}
	
	{#if order.type === 'trailing_stop'}
		<div>
			<span class="text-xs text-zinc-500 font-sans block mb-1.5">Trailing Percent
			<div class="flex items-center gap-2">
				<input type="number" bind:value={order.trailingPercent} step="0.1" min="0.1"
					class="flex-1 bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-white text-sm font-mono focus:outline-none focus:border-emerald-500"
				/>
				<span class="text-sm text-zinc-500 font-mono">%</span>
			</div>
		</div>
	{/if}
	
	<!-- Bracket Order (TP/SL) -->
	<div class="pt-3 border-t border-zinc-800/50">
		<p class="text-xs text-zinc-500 font-sans mb-2">TP / SL (optional)</p>
		<div class="grid grid-cols-2 gap-2">
			<div>
				<span class="text-[10px] text-emerald-500 font-mono block mb-1">Take Profit
				<input type="number" bind:value={order.takeProfit} step="0.01" placeholder="—"
					class="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-2.5 py-1.5 text-white text-sm font-mono focus:outline-none focus:border-emerald-500"
				/>
			</div>
			<div>
				<span class="text-[10px] text-rose-500 font-mono block mb-1">Stop Loss
				<input type="number" bind:value={order.stopLoss} step="0.01" placeholder="—"
					class="w-full bg-zinc-800 border border-zinc-700 rounded-lg px-2.5 py-1.5 text-white text-sm font-mono focus:outline-none focus:border-rose-500"
				/>
			</div>
		</div>
	</div>
	
	<!-- P&L Preview -->
	{#if estimatedPnl}
		<div class="rounded-lg bg-zinc-800/30 border border-zinc-700/30 p-3 text-xs space-y-1.5">
			<div class="flex justify-between">
				<span class="text-zinc-500 font-sans">Est. Profit (TP):</span>
				<span class="text-emerald-400 font-mono font-semibold">+${estimatedPnl.profit.toFixed(2)}</span>
			</div>
			<div class="flex justify-between">
				<span class="text-zinc-500 font-sans">Est. Loss (SL):</span>
				<span class="text-rose-400 font-mono font-semibold">{estimatedPnl.loss.toFixed(2)}</span>
			</div>
			<div class="flex justify-between pt-1 border-t border-zinc-700/30">
				<span class="text-zinc-500 font-sans">Risk/Reward:</span>
				<span class="text-zinc-200 font-mono font-semibold">{Math.abs(estimatedPnl.profit / estimatedPnl.loss).toFixed(2)}:1</span>
			</div>
		</div>
	{/if}
	
	<!-- Result / Error -->
	{#if result}
		<div class="rounded-lg bg-emerald-500/10 border border-emerald-500/20 p-3">
			<p class="text-sm text-emerald-400 font-sans">{result.message || 'Order submitted'}</p>
			{#if result.trade}
				<p class="text-xs text-zinc-500 font-mono mt-1">ID: {result.trade.id}</p>
			{/if}
		</div>
	{/if}
	{#if error}
		<div class="rounded-lg bg-rose-500/10 border border-rose-500/20 p-3">
			<p class="text-sm text-rose-400 font-sans">{error}</p>
		</div>
	{/if}
	
	<!-- Submit Button -->
	<button
		on:click={submitOrder}
		disabled={submitting}
		class="w-full py-3 rounded-xl text-sm font-semibold text-white transition-all active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed {side === 'long' ? 'bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 shadow-lg shadow-emerald-900/30' : 'bg-gradient-to-r from-rose-600 to-rose-500 hover:from-rose-500 hover:to-rose-400 shadow-lg shadow-rose-900/30'}"
	>
		{#if submitting}
			<span class="inline-block mr-2">⏳</span> Submitting...
		{:else}
			{side === 'long' ? '📈' : '📉'} {side === 'long' ? 'Buy / Long' : 'Sell / Short'} {symbol.replace('USDT', '')}
		{/if}
	</button>
</div>
