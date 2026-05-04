<script lang="ts">
	export let data: number[] = [];
	export let color: string = '#3b82f6';
	export let height: number = 40;
	export let width: number = 120;
	export let strokeWidth: number = 2;
	
	$: min = Math.min(...data, 0);
	$: max = Math.max(...data, 0);
	$: range = max - min || 1;
	
	$: points = data.map((val, i) => {
		const x = (i / (data.length - 1 || 1)) * width;
		const y = height - ((val - min) / range) * height;
		return `${x},${y}`;
	}).join(' ');
	
	$: areaPoints = `0,${height} ${points} ${width},${height}`;
</script>

<svg {width} {height} class="overflow-visible" viewBox="0 0 {width} {height}">
	{#if data.length > 1}
		<!-- Gradient fill -->
		<defs>
			<linearGradient id="sparkline-grad" x1="0" y1="0" x2="0" y2="1">
				<stop offset="0%" stop-color={color} stop-opacity="0.3"/>
				<stop offset="100%" stop-color={color} stop-opacity="0"/>
			</linearGradient>
		</defs>
		
		<!-- Area fill -->
		<polygon points={areaPoints} fill="url(#sparkline-grad)" />
		
		<!-- Line -->
		<polyline
			points={points}
			fill="none"
			stroke={color}
			stroke-width={strokeWidth}
			stroke-linecap="round"
			stroke-linejoin="round"
		/>
		
		<!-- End dot -->
		{#if data.length > 0}
			{@const lastIdx = data.length - 1}
			{@const lastX = width}
			{@const lastY = height - ((data[lastIdx] - min) / range) * height}
			<circle cx={lastX} cy={lastY} r="3" fill={color} />
		{/if}
	{:else}
		<text x={width/2} y={height/2} text-anchor="middle" class="fill-muted-foreground" style="font-size: 10px;">No data</text>
	{/if}
</svg>
