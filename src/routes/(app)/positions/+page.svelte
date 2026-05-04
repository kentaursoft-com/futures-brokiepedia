<script lang="ts">
	import { liveState } from '$lib/api';
	import CryptoIcon from '$lib/components/CryptoIcon.svelte';
	
	$: positions = $liveState?.positions || [];
	
	const mockPositions = [
		{ id: '1', symbol: 'BTC-PERP', side: 'long', size: 0.15, entry_price: 78250.00, mark_price: 78623.25, unrealized_pnl: 55.99, leverage: 10, margin: 1173.75, exchange: 'Binance' },
		{ id: '2', symbol: 'ETH-PERP', side: 'short', size: 2.5, entry_price: 4250.00, mark_price: 4215.00, unrealized_pnl: 87.50, leverage: 5, margin: 2125.00, exchange: 'Binance' },
	];
	
	const mockOrders = [
		{ id: '1', symbol: 'BTC-PERP', type: 'limit', side: 'buy', price: 78000.00, size: 0.1, status: 'open', time: '2024-01-15 14:30:00' },
		{ id: '2', symbol: 'ETH-PERP', type: 'stop_market', side: 'sell', price: 4100.00, size: 1.0, status: 'open', time: '2024-01-15 14:25:00' },
	];
	
	const mockHistory = [
		{ id: '1', symbol: 'BTC-PERP', side: 'long', size: 0.1, entry: 77500.00, exit: 78200.00, pnl: 70.00, pnl_pct: 0.9, time: '2024-01-15 12:00:00' },
		{ id: '2', symbol: 'SOL-PERP', side: 'short', size: 50, entry: 200.00, exit: 198.50, pnl: 75.00, pnl_pct: 0.75, time: '2024-01-15 10:30:00' },
	];
	
	let activeTab = 'positions';
	const tabs = [
		{ id: 'positions', label: 'Open Positions' },
		{ id: 'orders', label: 'Open Orders' },
		{ id: 'history', label: 'Trade History' },
	];
</script>

<svelte:head>
	<title>Positions | Futures Brokiepedia</title>
</svelte:head>

<div class="space-y-6">
	<!-- Header -->
	<div>
		<h1 class="text-2xl font-bold">Positions & Orders</h1>
		<p class="text-muted-foreground text-sm mt-1">Manage your open positions and orders</p>
	</div>
	
	<!-- Summary Cards -->
	<div class="grid grid-cols-1 md:grid-cols-4 gap-4">
		<div class="bg-card border border-border rounded-xl p-5">
			<p class="text-muted-foreground text-sm">Open Positions</p>
			<p class="text-2xl font-bold mt-1">{mockPositions.length}</p>
		</div>
		<div class="bg-card border border-border rounded-xl p-5">
			<p class="text-muted-foreground text-sm">Total Margin Used</p>
			<p class="text-2xl font-bold mt-1">$3,298.75</p>
		</div>
		<div class="bg-card border border-border rounded-xl p-5">
			<p class="text-muted-foreground text-sm">Unrealized P&L</p>
			<p class="text-2xl font-bold mt-1 text-green-400">+$143.49</p>
		</div>
		<div class="bg-card border border-border rounded-xl p-5">
			<p class="text-muted-foreground text-sm">Open Orders</p>
			<p class="text-2xl font-bold mt-1">{mockOrders.length}</p>
		</div>
	</div>
	
	<!-- Tabs -->
	<div class="bg-card border border-border rounded-xl">
		<div class="flex border-b border-border">
			{#each tabs as tab}
				<button
					class="px-6 py-4 text-sm font-medium transition-colors border-b-2 {activeTab === tab.id ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground'}"
					on:click={() => activeTab = tab.id}
				>
					{tab.label}
				</button>
			{/each}
		</div>
		
		<div class="p-6">
			{#if activeTab === 'positions'}
				<div class="overflow-x-auto">
					<table class="w-full">
						<thead>
							<tr class="border-b border-border">
								<th class="text-left py-3 text-sm text-muted-foreground font-medium">Symbol</th>
								<th class="text-left py-3 text-sm text-muted-foreground font-medium">Side</th>
								<th class="text-left py-3 text-sm text-muted-foreground font-medium">Size</th>
								<th class="text-left py-3 text-sm text-muted-foreground font-medium">Entry Price</th>
								<th class="text-left py-3 text-sm text-muted-foreground font-medium">Mark Price</th>
								<th class="text-left py-3 text-sm text-muted-foreground font-medium">Leverage</th>
								<th class="text-left py-3 text-sm text-muted-foreground font-medium">Margin</th>
								<th class="text-left py-3 text-sm text-muted-foreground font-medium">P&L</th>
								<th class="text-left py-3 text-sm text-muted-foreground font-medium">Actions</th>
							</tr>
						</thead>
						<tbody>
							{#each mockPositions as pos}
								<tr class="border-b border-border/50 hover:bg-muted/50">
									<td class="py-3 font-medium">
										<div class="flex items-center gap-2">
											<CryptoIcon symbol={pos.symbol} size={20} />
											{pos.symbol}
										</div>
									</td>
									<td class="py-3">
										<span class="text-xs px-2 py-1 rounded-full {pos.side === 'long' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}">
											{pos.side.toUpperCase()}
										</span>
									</td>
									<td class="py-3">{pos.size}</td>
									<td class="py-3 font-mono">${pos.entry_price.toLocaleString()}</td>
									<td class="py-3 font-mono">${pos.mark_price.toLocaleString()}</td>
									<td class="py-3">{pos.leverage}x</td>
									<td class="py-3">${pos.margin.toLocaleString()}</td>
									<td class="py-3 {pos.unrealized_pnl >= 0 ? 'text-green-400' : 'text-red-400'}">
										{pos.unrealized_pnl >= 0 ? '+' : ''}${pos.unrealized_pnl.toFixed(2)}
									</td>
									<td class="py-3">
										<button class="text-xs px-3 py-1.5 bg-red-500/20 text-red-400 rounded hover:bg-red-500/30 transition-colors">
											Close
										</button>
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
				
			{:else if activeTab === 'orders'}
				<div class="overflow-x-auto">
					<table class="w-full">
						<thead>
							<tr class="border-b border-border">
								<th class="text-left py-3 text-sm text-muted-foreground font-medium">Symbol</th>
								<th class="text-left py-3 text-sm text-muted-foreground font-medium">Type</th>
								<th class="text-left py-3 text-sm text-muted-foreground font-medium">Side</th>
								<th class="text-left py-3 text-sm text-muted-foreground font-medium">Price</th>
								<th class="text-left py-3 text-sm text-muted-foreground font-medium">Size</th>
								<th class="text-left py-3 text-sm text-muted-foreground font-medium">Status</th>
								<th class="text-left py-3 text-sm text-muted-foreground font-medium">Time</th>
								<th class="text-left py-3 text-sm text-muted-foreground font-medium">Actions</th>
							</tr>
						</thead>
						<tbody>
							{#each mockOrders as order}
								<tr class="border-b border-border/50 hover:bg-muted/50">
									<td class="py-3 font-medium">
										<div class="flex items-center gap-2">
											<CryptoIcon symbol={order.symbol} size={20} />
											{order.symbol}
										</div>
									</td>
									<td class="py-3 capitalize">{order.type.replace('_', ' ')}</td>
									<td class="py-3">
										<span class="text-xs px-2 py-1 rounded-full {order.side === 'buy' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}">
											{order.side.toUpperCase()}
										</span>
									</td>
									<td class="py-3 font-mono">${order.price.toLocaleString()}</td>
									<td class="py-3">{order.size}</td>
									<td class="py-3">
										<span class="text-xs px-2 py-1 rounded-full bg-yellow-500/20 text-yellow-400">
											{order.status.toUpperCase()}
										</span>
									</td>
									<td class="py-3 text-sm">{order.time}</td>
									<td class="py-3">
										<button class="text-xs px-3 py-1.5 bg-red-500/20 text-red-400 rounded hover:bg-red-500/30 transition-colors">
											Cancel
										</button>
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
				
			{:else if activeTab === 'history'}
				<div class="overflow-x-auto">
					<table class="w-full">
						<thead>
							<tr class="border-b border-border">
								<th class="text-left py-3 text-sm text-muted-foreground font-medium">Symbol</th>
								<th class="text-left py-3 text-sm text-muted-foreground font-medium">Side</th>
								<th class="text-left py-3 text-sm text-muted-foreground font-medium">Size</th>
								<th class="text-left py-3 text-sm text-muted-foreground font-medium">Entry</th>
								<th class="text-left py-3 text-sm text-muted-foreground font-medium">Exit</th>
								<th class="text-left py-3 text-sm text-muted-foreground font-medium">P&L</th>
								<th class="text-left py-3 text-sm text-muted-foreground font-medium">P&L %</th>
								<th class="text-left py-3 text-sm text-muted-foreground font-medium">Time</th>
							</tr>
						</thead>
						<tbody>
							{#each mockHistory as trade}
								<tr class="border-b border-border/50 hover:bg-muted/50">
									<td class="py-3 font-medium">
										<div class="flex items-center gap-2">
											<CryptoIcon symbol={trade.symbol} size={20} />
											{trade.symbol}
										</div>
									</td>
									<td class="py-3">
										<span class="text-xs px-2 py-1 rounded-full {trade.side === 'long' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}">
											{trade.side.toUpperCase()}
										</span>
									</td>
									<td class="py-3">{trade.size}</td>
									<td class="py-3 font-mono">${trade.entry.toLocaleString()}</td>
									<td class="py-3 font-mono">${trade.exit.toLocaleString()}</td>
									<td class="py-3 {trade.pnl >= 0 ? 'text-green-400' : 'text-red-400'}">
										{trade.pnl >= 0 ? '+' : ''}${trade.pnl.toFixed(2)}
									</td>
									<td class="py-3 {trade.pnl_pct >= 0 ? 'text-green-400' : 'text-red-400'}">
										{trade.pnl_pct >= 0 ? '+' : ''}{trade.pnl_pct.toFixed(2)}%
									</td>
									<td class="py-3 text-sm">{trade.time}</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			{/if}
		</div>
	</div>
</div>

<style>
	:global(.bg-card) { background-color: hsl(224 71% 6%); }
	:global(.border-border) { border-color: hsl(215 20% 18%); }
	:global(.text-muted-foreground) { color: hsl(215 20% 55%); }
	:global(.bg-muted) { background-color: hsl(215 20% 12%); }
	:global(.text-primary) { color: hsl(217 91% 60%); }
	:global(.border-primary) { border-color: hsl(217 91% 60%); }
</style>