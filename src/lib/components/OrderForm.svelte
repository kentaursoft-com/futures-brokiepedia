<script lang="ts">
	interface OrderParams {
		symbol: string;
		side: 'long' | 'short';
		type: 'market' | 'limit' | 'stop' | 'stop_limit' | 'trailing_stop';
		size: number;
		price?: number;
		stopPrice?: number;
		trailingPercent?: number;
		takeProfit?: number;
		stopLoss?: number;
	}
	
	let order: OrderParams = {
		symbol: 'BTC-PERP',
		side: 'long',
		type: 'market',
		size: 0.1,
		price: 43400,
		stopPrice: 43000,
		trailingPercent: 2,
		takeProfit: 45000,
		stopLoss: 42000
	};
	
	let showPreview = false;
	
	$: estimatedPnl = order.takeProfit && order.stopLoss 
		? {
				profit: order.side === 'long' 
					? (order.takeProfit - (order.price || 43400)) * order.size
					: ((order.price || 43400) - order.takeProfit) * order.size,
				loss: order.side === 'long'
					? (order.stopLoss - (order.price || 43400)) * order.size
					: ((order.price || 43400) - order.stopLoss) * order.size
			}
		: null;
	
	function submitOrder() {
		alert(`Order submitted:\n${order.side.toUpperCase()} ${order.size} ${order.symbol}\nType: ${order.type}`);
	}
</script>

<div class="rounded-lg border bg-card p-4">
	<h2 class="text-sm font-semibold mb-4">New Order</h2>
	
	<div class="space-y-3">
		<!-- Symbol & Side -->
		<div class="grid grid-cols-2 gap-2">
			<select bind:value={order.symbol} class="rounded bg-secondary px-3 py-2 text-sm border-0">
				<option value="BTC-PERP">BTC-PERP</option>
				<option value="ETH-PERP">ETH-PERP</option>
				<option value="SOL-PERP">SOL-PERP</option>
			</select>
			<div class="flex rounded overflow-hidden">
				<button 
					on:click={() => order.side = 'long'}
					class="flex-1 py-2 text-sm font-medium transition-colors {order.side === 'long' ? 'bg-emerald-500 text-white' : 'bg-secondary text-secondary-foreground'}"
				>
					Long
				</button>
				<button 
					on:click={() => order.side = 'short'}
					class="flex-1 py-2 text-sm font-medium transition-colors {order.side === 'short' ? 'bg-red-500 text-white' : 'bg-secondary text-secondary-foreground'}"
				>
					Short
				</button>
			</div>
		</div>
		
		<!-- Order Type -->
		<select bind:value={order.type} class="w-full rounded bg-secondary px-3 py-2 text-sm border-0">
			<option value="market">Market</option>
			<option value="limit">Limit</option>
			<option value="stop">Stop Market</option>
			<option value="stop_limit">Stop Limit</option>
			<option value="trailing_stop">Trailing Stop</option>
		</select>
		
		<!-- Size -->
		<div class="flex gap-2">
			<input 
				type="number" 
				bind:value={order.size} 
				step="0.01" 
				placeholder="Size"
				class="flex-1 rounded bg-secondary px-3 py-2 text-sm border-0"
			/>
			<button class="rounded bg-secondary px-3 py-2 text-xs text-muted-foreground hover:bg-secondary/80">25%</button>
			<button class="rounded bg-secondary px-3 py-2 text-xs text-muted-foreground hover:bg-secondary/80">50%</button>
			<button class="rounded bg-secondary px-3 py-2 text-xs text-muted-foreground hover:bg-secondary/80">100%</button>
		</div>
		
		<!-- Price inputs based on order type -->
		{#if order.type === 'limit' || order.type === 'stop_limit'}
			<input 
				type="number" 
				bind:value={order.price} 
				placeholder="Limit Price"
				class="w-full rounded bg-secondary px-3 py-2 text-sm border-0"
			/>
		{/if}
		
		{#if order.type === 'stop' || order.type === 'stop_limit'}
			<input 
				type="number" 
				bind:value={order.stopPrice} 
				placeholder="Stop Price"
				class="w-full rounded bg-secondary px-3 py-2 text-sm border-0"
			/>
		{/if}
		
		{#if order.type === 'trailing_stop'}
			<div class="flex items-center gap-2">
				<input 
					type="number" 
					bind:value={order.trailingPercent} 
					placeholder="Trailing %"
					class="flex-1 rounded bg-secondary px-3 py-2 text-sm border-0"
				/>
				<span class="text-sm text-muted-foreground">%</span>
			</div>
		{/if}
		
		<!-- Bracket Order -->
		<div class="border-t border-border pt-3">
			<p class="text-xs text-muted-foreground mb-2">Bracket Order (optional)</p>
			<div class="grid grid-cols-2 gap-2">
				<input 
					type="number" 
					bind:value={order.takeProfit} 
					placeholder="Take Profit"
					class="rounded bg-secondary px-3 py-2 text-sm border-0"
				/>
				<input 
					type="number" 
					bind:value={order.stopLoss} 
					placeholder="Stop Loss"
					class="rounded bg-secondary px-3 py-2 text-sm border-0"
				/>
			</div>
		</div>
		
		<!-- P&L Preview -->
		{#if estimatedPnl}
			<div class="rounded bg-secondary/50 p-3 text-xs space-y-1">
				<div class="flex justify-between">
					<span class="text-muted-foreground">Est. Profit (TP):</span>
					<span class="text-emerald-400">+${estimatedPnl.profit.toFixed(2)}</span>
				</div>
				<div class="flex justify-between">
					<span class="text-muted-foreground">Est. Loss (SL):</span>
					<span class="text-red-400">${estimatedPnl.loss.toFixed(2)}</span>
				</div>
				<div class="flex justify-between">
					<span class="text-muted-foreground">Risk/Reward:</span>
					<span class="font-medium">{Math.abs(estimatedPnl.profit / estimatedPnl.loss).toFixed(2)}:1</span>
				</div>
			</div>
		{/if}
		
		<!-- Submit -->
		<button 
			on:click={submitOrder}
			class="w-full rounded-md {order.side === 'long' ? 'bg-emerald-500 hover:bg-emerald-600' : 'bg-red-500 hover:bg-red-600'} px-4 py-3 text-sm font-medium text-white transition-colors"
		>
			{order.side === 'long' ? '🟢 Buy' : '🔴 Sell'} {order.symbol}
		</button>
	</div>
</div>
