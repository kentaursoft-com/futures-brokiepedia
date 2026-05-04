<script lang="ts">
	import { browser } from '$app/environment';
	export let fallback: string = 'Loading...';
</script>

{#if browser}
	<slot />
{:else}
	<div class="h-full flex items-center justify-center text-muted-foreground">
		{fallback}
	</div>
{/if}
