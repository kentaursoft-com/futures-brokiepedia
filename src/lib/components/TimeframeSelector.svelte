<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	
	const dispatch = createEventDispatcher<{change: string}>();
	
	const timeframes = [
		{ label: '1m', value: '1m', ms: 60000 },
		{ label: '5m', value: '5m', ms: 300000 },
		{ label: '15m', value: '15m', ms: 900000 },
		{ label: '1h', value: '1h', ms: 3600000 },
		{ label: '4h', value: '4h', ms: 14400000 },
		{ label: '1d', value: '1d', ms: 86400000 }
	];
	
	let activeTf = '1m';
	
	function selectTf(tf: string) {
		activeTf = tf;
		dispatch('change', tf);
	}
</script>

<div class="flex items-center gap-1 rounded-lg bg-secondary/50 p-1">
	{#each timeframes as tf}
		<button
			class="rounded px-2.5 py-1 text-xs font-medium transition-all {activeTf === tf.value ? 'bg-primary text-primary-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground hover:bg-secondary'}"
			on:click={() => selectTf(tf.value)}
		>
			{tf.label}
		</button>
	{/each}
</div>
