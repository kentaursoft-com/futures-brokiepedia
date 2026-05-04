<script lang="ts">
	export let name: string;
	export let size: string = '1.2em';
	export let color: string = '';
	export let class_name: string = '';
</script>

<i 
	class="lni lni-{name} {class_name}" 
	style="font-size: {size}; {color ? `color: ${color};` : ''}"
></i>
