<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '../api';

	let signals: any[] = [];
	let loading = true;
	let error: string | null = null;

	async function loadSignals() {
		loading = true;
		error = null;
		try {
			const data = await api.getSignals();
			signals = data.signals || [];
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load signals';
			signals = [];
		}
		loading = false;
	}

	function formatTime(ts: number) {
		const mins = Math.floor((Date.now() - ts) / 60000);
		if (mins < 60) return `${mins}m ago`;
		const hours = Math.floor(mins / 60);
		if (hours < 24) return `${hours}h ago`;
		return `${Math.floor(hours / 24)}d ago`;
	}

	onMount(loadSignals);
</script>

<div class="rounded-lg border bg-card p-4">
	<div class="flex items-center justify-between mb-4">
		<h2 class="text-sm font-semibold">Agent Signals Feed</h2>
		<button on:click={loadSignals} class="text-xs text-primary hover:underline">Refresh</button>
	</div>
	
	{#if loading}
		<div class="text-center py-8">
			<div class="inline-block w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
			<p class="text-xs text-muted-foreground mt-2">Loading agent signals...</p>
		</div>
	{:else if error}
		<div class="text-center py-8">
			<p class="text-sm text-red-400">{error}</p>
			<button on:click={loadSignals} class="mt-2 text-xs text-primary hover:underline">Retry</button>
		</div>
	{:else if signals.length === 0}
		<div class="text-center py-8">
			<p class="text-sm text-muted-foreground">No agent signals yet</p>
			<p class="text-xs text-muted-foreground mt-1">Signals will appear when the AI agents generate trade ideas</p>
		</div>
	{:else}
		<div class="space-y-3 max-h-[500px] overflow-y-auto">
			{#each signals as signal}
				<div class="rounded-lg bg-secondary/50 p-4 space-y-2">
					<div class="flex items-center justify-between">
						<div>
							<p class="text-sm font-medium">{signal.department || signal.department_name || 'Agent Signal'}</p>
							<p class="text-xs text-muted-foreground">{signal.timestamp ? formatTime(signal.timestamp) : 'Just now'}</p>
						</div>
						<span class="rounded px-2 py-0.5 text-xs font-medium {signal.direction === 'long' ? 'bg-emerald-500/20 text-emerald-400' : signal.direction === 'short' ? 'bg-red-500/20 text-red-400' : 'bg-amber-500/20 text-amber-400'}">
							{(signal.direction || signal.side || 'NEUTRAL').toUpperCase()}
						</span>
					</div>
					
					{#if signal.symbol}
						<div class="flex items-center gap-4 text-sm">
							<div>
								<span class="text-xs text-muted-foreground">Symbol</span>
								<p class="font-medium">{signal.symbol}</p>
							</div>
							{#if signal.confidence != null}
								<div>
									<span class="text-xs text-muted-foreground">Confidence</span>
									<p class="font-medium">{(signal.confidence * 100).toFixed(0)}%</p>
								</div>
							{/if}
							{#if signal.regime_tag}
								<div>
									<span class="text-xs text-muted-foreground">Regime</span>
									<p class="font-medium">{signal.regime_tag}</p>
								</div>
							{/if}
						</div>
					{/if}
					
					{#if signal.reasoning}
						<p class="text-sm text-muted-foreground">{signal.reasoning}</p>
					{/if}
				</div>
			{/each}
		</div>
	{/if}
	
	<p class="mt-4 text-xs text-muted-foreground text-center">
		AI-generated signals for analysis. Always verify before trading.
	</p>
</div>
