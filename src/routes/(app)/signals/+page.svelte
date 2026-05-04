<script lang="ts">
	import { liveState } from '$lib/api';
	import type { AgentVerdict } from '$lib/types';
	import CryptoIcon from '$lib/components/CryptoIcon.svelte';
	
	$: departments = $liveState?.departments || [];
	
	const mockSignals = [
		{ 
			id: '1', 
			symbol: 'BTC-PERP', 
			type: 'long',
			confidence: 0.85,
			entry: 78250,
			tp: 81000,
			sl: 76500,
			risk_reward: 1.6,
			timeframe: '1h',
			strategy: 'EMA Trend',
			time: '14:30:00',
			status: 'active'
		},
		{ 
			id: '2', 
			symbol: 'ETH-PERP', 
			type: 'short',
			confidence: 0.72,
			entry: 4250,
			tp: 4000,
			sl: 4400,
			risk_reward: 1.4,
			timeframe: '4h',
			strategy: 'RSI Reversal',
			time: '13:15:00',
			status: 'pending'
		},
		{ 
			id: '3', 
			symbol: 'SOL-PERP', 
			type: 'long',
			confidence: 0.91,
			entry: 195.50,
			tp: 220.00,
			sl: 185.00,
			risk_reward: 2.4,
			timeframe: '1d',
			strategy: 'Breakout',
			time: '12:00:00',
			status: 'closed',
			result: 'win',
			pnl: 12.50
		},
	];
	
	const mockAlerts = [
		{ symbol: 'BTC-PERP', condition: 'Price > 80,000', triggered: false, created: '2024-01-15 10:00:00' },
		{ symbol: 'ETH-PERP', condition: 'RSI < 30', triggered: true, created: '2024-01-15 09:30:00' },
		{ symbol: 'BTC-PERP', condition: 'Volume spike > 200%', triggered: true, created: '2024-01-15 08:00:00' },
	];
	
	let activeTab = 'signals';
	const tabs = [
		{ id: 'signals', label: 'Trading Signals' },
		{ id: 'alerts', label: 'Price Alerts' },
		{ id: 'departments', label: 'AI Departments' },
	];
</script>

<svelte:head>
	<title>Signals | Futures Brokiepedia</title>
</svelte:head>

<div class="space-y-6">
	<!-- Header -->
	<div>
		<h1 class="text-2xl font-bold">Signals & Alerts</h1>
		<p class="text-muted-foreground text-sm mt-1">AI-generated trading signals and price alerts</p>
	</div>
	
	<!-- Stats -->
	<div class="grid grid-cols-1 md:grid-cols-4 gap-4">
		<div class="bg-card border border-border rounded-xl p-5">
			<p class="text-muted-foreground text-sm">Active Signals</p>
			<p class="text-2xl font-bold mt-1">2</p>
		</div>
		<div class="bg-card border border-border rounded-xl p-5">
			<p class="text-muted-foreground text-sm">Win Rate</p>
			<p class="text-2xl font-bold mt-1 text-green-400">68.5%</p>
		</div>
		<div class="bg-card border border-border rounded-xl p-5">
			<p class="text-muted-foreground text-sm">Avg R:R</p>
			<p class="text-2xl font-bold mt-1">1.8</p>
		</div>
		<div class="bg-card border border-border rounded-xl p-5">
			<p class="text-muted-foreground text-sm">Total Signals</p>
			<p class="text-2xl font-bold mt-1">127</p>
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
			{#if activeTab === 'signals'}
				<div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
					{#each mockSignals as signal}
						<div class="bg-muted rounded-lg p-5 border border-border/50">
							<div class="flex items-start justify-between mb-4">
								<div>
									<div class="flex items-center gap-2">
										<CryptoIcon symbol={signal.symbol} size={24} />
										<span class="font-bold text-lg">{signal.symbol}</span>
										<span class="text-xs px-2 py-1 rounded-full {signal.type === 'long' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}">
											{signal.type.toUpperCase()}
										</span>
									</div>
									<span class="text-sm text-muted-foreground">{signal.strategy} • {signal.timeframe}</span>
								</div>
								<div class="text-right">
									<span class="text-xs px-2 py-1 rounded-full {
										signal.status === 'active' ? 'bg-green-500/20 text-green-400' :
										signal.status === 'pending' ? 'bg-yellow-500/20 text-yellow-400' :
										'bg-gray-500/20 text-gray-400'
									}">
										{signal.status.toUpperCase()}
									</span>
								</div>
							</div>
							
							<div class="grid grid-cols-3 gap-4 mb-4">
								<div>
									<p class="text-xs text-muted-foreground">Entry</p>
									<p class="font-mono font-medium">${signal.entry.toLocaleString()}</p>
								</div>
								<div>
									<p class="text-xs text-muted-foreground">TP</p>
									<p class="font-mono font-medium text-green-400">${signal.tp.toLocaleString()}</p>
								</div>
								<div>
									<p class="text-xs text-muted-foreground">SL</p>
									<p class="font-mono font-medium text-red-400">${signal.sl.toLocaleString()}</p>
								</div>
							</div>
							
							<div class="flex items-center justify-between">
								<div class="flex items-center gap-2">
									<span class="text-sm text-muted-foreground">Confidence</span>
									<div class="w-24 h-2 bg-muted rounded-full overflow-hidden">
										<div class="h-full bg-primary rounded-full" style="width: {signal.confidence * 100}%"></div>
									</div>
									<span class="text-sm font-medium">{(signal.confidence * 100).toFixed(0)}%</span>
								</div>
								<div class="text-sm">
									<span class="text-muted-foreground">R:R </span>
									<span class="font-medium">{signal.risk_reward}</span>
								</div>
							</div>
							
							{#if signal.result}
								<div class="mt-3 pt-3 border-t border-border/50">
									<span class="text-sm {signal.result === 'win' ? 'text-green-400' : 'text-red-400'}">
										{signal.result === 'win' ? '✓' : '✗'} P&L: {signal.pnl && signal.pnl >= 0 ? '+' : ''}${signal.pnl || 0}
									</span>
								</div>
							{/if}
						</div>
					{/each}
				</div>
				
			{:else if activeTab === 'alerts'}
				<div class="space-y-3">
					{#each mockAlerts as alert}
						<div class="flex items-center justify-between p-4 bg-muted rounded-lg">
							<div class="flex items-center gap-4">
								<div class="w-2 h-2 rounded-full {alert.triggered ? 'bg-green-500' : 'bg-yellow-500'}"></div>
								<div>
									<p class="font-medium">{alert.symbol}</p>
									<p class="text-sm text-muted-foreground">{alert.condition}</p>
								</div>
							</div>
							<div class="flex items-center gap-4">
								<span class="text-xs px-2 py-1 rounded-full {alert.triggered ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'}">
									{alert.triggered ? 'TRIGGERED' : 'PENDING'}
								</span>
								<span class="text-sm text-muted-foreground">{alert.created}</span>
								<button class="text-sm text-red-400 hover:text-red-300">Delete</button>
							</div>
						</div>
					{/each}
				</div>
				
				<button class="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors">
					+ New Alert
				</button>
				
			{:else if activeTab === 'departments'}
				<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
					{#each departments.length > 0 ? departments : [
						{ department: 'Fundamental', name: 'Fundamental', confidence: 0.72, direction: 'long', lastRun: '14:30:00', timeframe: '1h' },
						{ department: 'Technical', name: 'Technical', confidence: 0.85, direction: 'long', lastRun: '14:30:00', timeframe: '1h' },
						{ department: 'Sentiment', name: 'Sentiment', confidence: 0.61, direction: 'flat', lastRun: '14:30:00', timeframe: '1h' },
						{ department: 'Quantitative', name: 'Quantitative', confidence: 0.78, direction: 'long', lastRun: '14:30:00', timeframe: '1h' },
						{ department: 'Statistical', name: 'Statistical', confidence: 0.55, direction: 'short', lastRun: '14:30:00', timeframe: '1h' },
						{ department: 'Qualitative', name: 'Qualitative', confidence: 0.90, direction: 'long', lastRun: '14:30:00', timeframe: '1h' },
					] as dept}
						<div class="bg-muted rounded-lg p-5 border border-border/50">
							<div class="flex items-center justify-between mb-3">
								<span class="font-semibold">{dept.department}</span>
								<span class="text-xs text-muted-foreground">{dept.lastRun}</span>
							</div>
							<div class="flex items-center gap-2 mb-3">
								<span class="text-xs px-2 py-1 rounded-full {
									dept.direction === 'long' ? 'bg-green-500/20 text-green-400' :
									dept.direction === 'short' ? 'bg-red-500/20 text-red-400' :
									'bg-gray-500/20 text-gray-400'
								}">
									{dept.direction?.toUpperCase() || 'FLAT'}
								</span>
								<span class="text-xs text-muted-foreground">{dept.timeframe}</span>
							</div>
							<div class="flex items-center gap-2">
								<span class="text-sm text-muted-foreground">Confidence</span>
								<div class="flex-1 h-2 bg-background rounded-full overflow-hidden">
									<div class="h-full bg-primary rounded-full" style="width: {(dept.confidence || 0) * 100}%"></div>
								</div>
								<span class="text-sm font-medium">{((dept.confidence || 0) * 100).toFixed(0)}%</span>
							</div>
						</div>
					{/each}
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
	:global(.bg-background) { background-color: hsl(224 71% 4%); }
	:global(.text-primary) { color: hsl(217 91% 60%); }
	:global(.border-primary) { border-color: hsl(217 91% 60%); }
	:global(.bg-primary) { background-color: hsl(217 91% 60%); }
	:global(.text-primary-foreground) { color: hsl(213 31% 91%); }
</style>