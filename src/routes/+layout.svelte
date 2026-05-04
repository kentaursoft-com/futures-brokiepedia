<script lang="ts">
	import '../app.css';
	import Toast from '$lib/components/Toast.svelte';
</script>

<div class="min-h-screen bg-background text-foreground">
	<slot />
	<Toast />
</div>

<style>
	:global(.bg-background) {
		background-color: hsl(224 71% 4%);
	}
	:global(.text-foreground) {
		color: hsl(213 31% 91%);
	}
</style>
