<script lang="ts">
	import { onMount } from 'svelte';
	import { liveState, startPolling } from '$lib/api';
	import CryptoIcon from '$lib/components/CryptoIcon.svelte';
	
	let stopPolling: (() => void) | null = null;
	
	onMount(() => {
		stopPolling = startPolling(5000);
	});
	
	$: todayPnl = $liveState?.todayPnl ?? 0;
	$: unrealizedPnl = $liveState?.unrealizedPnl ?? 0;
	$: equity = $liveState?.equity ?? 10000;
	$: dailyDrawdown = $liveState?.dailyDrawdown ?? 0;
	$: lastSync = $liveState?.lastSync ? new Date($liveState.lastSync).toISOString() : new Date().toISOString();
	$: daemonConnected = $liveState ? true : false;
	$: systemStatus = $liveState?.systemStatus || 'paper';
	$: departments = $liveState?.departments || [];
	$: positions = $liveState?.positions || [];
	
	const recentActivity = [
		{ time: '14:32:15', action: 'Signal Generated', detail: 'BTC-PERP Long @ $78,450', type: 'signal' },
		{ time: '14:28:00', action: 'Position Opened', detail: 'Long 0.15 BTC @ $78,250', type: 'trade' },
		{ time: '14:15:30', action: 'Alert', detail: 'RSI oversold on 15m', type: 'alert' },
		{ time: '13:45:00', action: 'System', detail: 'Daemon connected', type: 'system' },
	];
</script>

<svelte:head>
	<title>Dashboard | Futures Brokiepedia</title>
</svelte:head>

<div class="space-y-6">
	<!-- Header -->
	<div class="flex items-center justify-between">
		<div>
			<h1 class="text-2xl font-bold">Dashboard</h1>
			<p class="text-muted-foreground text-sm mt-1">Overview of your trading activity</p>
		</div>
		<div class="flex items-center gap-2">
			<div class="w-2 h-2 rounded-full {daemonConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}"></div>
			<span class="text-sm text-muted-foreground">{daemonConnected ? 'Live' : 'Disconnected'}</span>
			<span class="ml-2 text-xs px-2 py-0.5 rounded-full {systemStatus === 'live' ? 'bg-red-500/20 text-red-400' : 'bg-yellow-500/20 text-yellow-400'}">
				{systemStatus.toUpperCase()}
			</span>
		</div>
	</div>
	
	<!-- Quick Stats Grid -->
	<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
		<div class="bg-card border border-border rounded-xl p-5">
			<p class="text-muted-foreground text-sm">Today P&L</p>
			<p class="text-2xl font-bold mt-1 {todayPnl >= 0 ? 'text-green-400' : 'text-red-400'}">${todayPnl.toFixed(2)}</p>
		</div>
		<div class="bg-card border border-border rounded-xl p-5">
			<p class="text-muted-foreground text-sm">Unrealized P&L</p>
			<p class="text-2xl font-bold mt-1 {unrealizedPnl >= 0 ? 'text-green-400' : 'text-red-400'}">${unrealizedPnl.toFixed(2)}</p>
		</div>
		<div class="bg-card border border-border rounded-xl p-5">
			<p class="text-muted-foreground text-sm">Account Equity</p>
			<p class="text-2xl font-bold mt-1">${equity.toLocaleString()}</p>
		</div>
		<div class="bg-card border border-border rounded-xl p-5">
			<p class="text-muted-foreground text-sm">Daily Drawdown</p>
			<p class="text-2xl font-bold mt-1 {dailyDrawdown > 2 ? 'text-red-400' : 'text-yellow-400'}">{dailyDrawdown.toFixed(2)}%</p>
		</div>
	</div>
	
	<!-- Main Content Grid -->
	<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
		<!-- Market Overview -->
		<div class="lg:col-span-2 bg-card border border-border rounded-xl p-6">
			<h2 class="text-lg font-semibold mb-4">Market Overview</h2>
			<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
				<div class="text-center p-4 bg-muted rounded-lg">
					<div class="flex items-center justify-center gap-2 mb-1">
						<CryptoIcon symbol="BTC" size={20} />
						<p class="text-muted-foreground text-xs">BTC/USDT</p>
					</div>
					<p class="text-lg font-bold mt-1">$78,623</p>
					<p class="text-xs text-green-400">+1.24%</p>
				</div>
				<div class="text-center p-4 bg-muted rounded-lg">
					<div class="flex items-center justify-center gap-2 mb-1">
						<CryptoIcon symbol="ETH" size={20} />
						<p class="text-muted-foreground text-xs">ETH/USDT</p>
					</div>
					<p class="text-lg font-bold mt-1">$4,215</p>
					<p class="text-xs text-green-400">+0.89%</p>
				</div>
				<div class="text-center p-4 bg-muted rounded-lg">
					<div class="flex items-center justify-center gap-2 mb-1">
						<CryptoIcon symbol="SOL" size={20} />
						<p class="text-muted-foreground text-xs">SOL/USDT</p>
					</div>
					<p class="text-lg font-bold mt-1">$198.50</p>
					<p class="text-xs text-red-400">-0.34%</p>
				</div>
				<div class="text-center p-4 bg-muted rounded-lg">
					<div class="flex items-center justify-center gap-2 mb-1">
						<CryptoIcon symbol="BNB" size={20} />
						<p class="text-muted-foreground text-xs">BNB/USDT</p>
					</div>
					<p class="text-lg font-bold mt-1">$712.30</p>
					<p class="text-xs text-green-400">+0.56%</p>
				</div>
			</div>
			
			<!-- Chart Placeholder -->
			<div class="mt-6 h-48 bg-muted rounded-lg flex items-center justify-center">
				<p class="text-muted-foreground flex items-center gap-2">
					<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"></path>
					</svg>
					Live chart available on Trade page
				</p>
			</div>
		</div>
		
		<!-- Side Panel -->
		<div class="space-y-6">
			<!-- Recent Activity -->
			<div class="bg-card border border-border rounded-xl p-6">
				<h2 class="text-lg font-semibold mb-4">Recent Activity</h2>
				<div class="space-y-3">
					{#each recentActivity as activity}
						<div class="flex items-start gap-3 p-3 bg-muted rounded-lg">
							<div class="w-2 h-2 rounded-full mt-2 {activity.type === 'signal' ? 'bg-blue-400' : activity.type === 'trade' ? 'bg-green-400' : activity.type === 'alert' ? 'bg-yellow-400' : 'bg-gray-400'}"></div>
							<div class="flex-1">
								<p class="text-sm font-medium">{activity.action}</p>
								<p class="text-xs text-muted-foreground">{activity.detail}</p>
							</div>
							<span class="text-xs text-muted-foreground">{activity.time}</span>
						</div>
					{/each}
				</div>
			</div>
			
			<!-- System Health -->
			<div class="bg-card border border-border rounded-xl p-6">
				<h2 class="text-lg font-semibold mb-4">System Health</h2>
				<div class="space-y-3">
					<div class="flex items-center justify-between">
						<span class="text-sm">VPS Daemon</span>
						<span class="text-xs px-2 py-1 rounded-full bg-green-500/20 text-green-400">Online</span>
					</div>
					<div class="flex items-center justify-between">
						<span class="text-sm">Binance WS</span>
						<span class="text-xs px-2 py-1 rounded-full bg-green-500/20 text-green-400">Connected</span>
					</div>
					<div class="flex items-center justify-between">
						<span class="text-sm">QuestDB</span>
						<span class="text-xs px-2 py-1 rounded-full bg-green-500/20 text-green-400">Running</span>
					</div>
					<div class="flex items-center justify-between">
						<span class="text-sm">ChromaDB</span>
						<span class="text-xs px-2 py-1 rounded-full bg-green-500/20 text-green-400">Running</span>
					</div>
					<div class="flex items-center justify-between">
						<span class="text-sm">Last Sync</span>
						<span class="text-xs text-muted-foreground">{new Date(lastSync).toLocaleTimeString()}</span>
					</div>
				</div>
			</div>
		</div>
	</div>
	
	<!-- Open Positions Preview -->
	<div class="bg-card border border-border rounded-xl p-6">
		<div class="flex items-center justify-between mb-4">
			<h2 class="text-lg font-semibold">Open Positions</h2>
			<a href="/positions" class="text-sm text-primary hover:underline">View All</a>
		</div>
		<div class="overflow-x-auto">
			<table class="w-full">
				<thead>
					<tr class="border-b border-border">
						<th class="text-left py-3 text-sm text-muted-foreground font-medium">Symbol</th>
						<th class="text-left py-3 text-sm text-muted-foreground font-medium">Side</th>
						<th class="text-left py-3 text-sm text-muted-foreground font-medium">Size</th>
						<th class="text-left py-3 text-sm text-muted-foreground font-medium">Entry Price</th>
						<th class="text-left py-3 text-sm text-muted-foreground font-medium">Mark Price</th>
						<th class="text-left py-3 text-sm text-muted-foreground font-medium">P&L</th>
					</tr>
				</thead>
				<tbody>
					{#if positions.length > 0}
						{#each positions as pos}
							<tr class="border-b border-border/50">
								<td class="py-3 font-medium">{pos.symbol}</td>
								<td class="py-3"><span class="text-xs px-2 py-1 rounded-full {pos.side === 'long' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}">{pos.side?.toUpperCase()}</span></td>
								<td class="py-3">{pos.size}</td>
								<td class="py-3 font-mono">${pos.entry_price?.toLocaleString() || '-'}</td>
								<td class="py-3 font-mono">${pos.mark_price?.toLocaleString() || '-'}</td>
								<td class="py-3 {pos.unrealized_pnl >= 0 ? 'text-green-400' : 'text-red-400'}">{pos.unrealized_pnl >= 0 ? '+' : ''}${pos.unrealized_pnl?.toFixed(2) || '0.00'}</td>
							</tr>
						{/each}
					{:else}
						<tr>
							<td colspan="6" class="py-8 text-center text-muted-foreground">No open positions</td>
						</tr>
					{/if}
				</tbody>
			</table>
		</div>
	</div>
	
	<!-- AI Departments -->
	{#if departments.length > 0}
		<div class="bg-card border border-border rounded-xl p-6">
			<h2 class="text-lg font-semibold mb-4">AI Departments</h2>
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
				{#each departments as dept}
					<div class="bg-muted rounded-lg p-4">
						<div class="flex items-center justify-between mb-2">
							<span class="font-medium">{dept.department}</span>
							<span class="text-xs px-2 py-1 rounded-full {dept.direction === 'long' ? 'bg-green-500/20 text-green-400' : dept.direction === 'short' ? 'bg-red-500/20 text-red-400' : 'bg-gray-500/20 text-gray-400'}">{dept.direction?.toUpperCase() || 'FLAT'}</span>
						</div>
						<div class="flex items-center gap-2">
							<div class="flex-1 h-2 bg-background rounded-full overflow-hidden">
								<div class="h-full bg-primary rounded-full" style="width: {(dept.confidence || 0) * 100}%"></div>
							</div>
							<span class="text-xs">{((dept.confidence || 0) * 100).toFixed(0)}%</span>
						</div>
					</div>
				{/each}
			</div>
		</div>
	{/if}
</div>

<style>
	:global(.bg-card) { background-color: hsl(224 71% 6%); }
	:global(.border-border) { border-color: hsl(215 20% 18%); }
	:global(.text-muted-foreground) { color: hsl(215 20% 55%); }
	:global(.bg-muted) { background-color: hsl(215 20% 12%); }
	:global(.bg-background) { background-color: hsl(224 71% 4%); }
	:global(.text-primary) { color: hsl(217 91% 60%); }
	:global(.bg-primary) { background-color: hsl(217 91% 60%); }
</style>
