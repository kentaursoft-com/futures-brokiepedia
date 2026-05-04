<script lang="ts">
	import { toast } from '$lib/toast';
	import { fly, fade } from 'svelte/transition';
</script>

{#if $toast.length > 0}
	<div class="fixed bottom-4 right-4 z-[9999] flex flex-col gap-2 pointer-events-none">
		{#each $toast as t (t.id)}
			<div
				transition:fly={{ x: 100, duration: 300 }}
				class="pointer-events-auto flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg border min-w-[300px] max-w-[400px] {t.type === 'success' ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' : t.type === 'error' ? 'bg-red-500/10 border-red-500/30 text-red-400' : t.type === 'warning' ? 'bg-amber-500/10 border-amber-500/30 text-amber-400' : 'bg-blue-500/10 border-blue-500/30 text-blue-400'}"
			>
				{#if t.type === 'success'}
					<svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
					</svg>
				{:else if t.type === 'error'}
					<svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
					</svg>
				{:else if t.type === 'warning'}
					<svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
					</svg>
				{:else}
					<svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
					</svg>
				{/if}
				<p class="text-sm flex-1">{t.message}</p>
				<button
					on:click={() => toast.remove(t.id)}
					class="text-muted-foreground hover:text-foreground transition-colors"
				>
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
					</svg>
				</button>
			</div>
		{/each}
	</div>
{/if}
