<script lang="ts">
	import Icon from './Icon.svelte';
	
	interface Alert {
		id: string;
		type: 'price' | 'rsi' | 'drawdown' | 'custom';
		symbol: string;
		condition: 'above' | 'below' | 'crosses';
		value: number;
		message: string;
		triggered: boolean;
		createdAt: number;
	}
	
	let alerts: Alert[] = [
		{ id: '1', type: 'price', symbol: 'BTC-PERP', condition: 'above', value: 45000, message: 'BTC above $45,000', triggered: false, createdAt: Date.now() - 3600000 },
		{ id: '2', type: 'rsi', symbol: 'BTC-PERP', condition: 'above', value: 70, message: 'RSI overbought (>70)', triggered: false, createdAt: Date.now() - 7200000 },
		{ id: '3', type: 'drawdown', symbol: 'PORTFOLIO', condition: 'above', value: 3, message: 'Daily drawdown > 3%', triggered: true, createdAt: Date.now() - 1800000 }
	];
	
	let newAlertType: Alert['type'] = 'price';
	let newAlertSymbol = 'BTC-PERP';
	let newAlertCondition: Alert['condition'] = 'above';
	let newAlertValue = 0;
	let newAlertMessage = '';
	let showForm = false;
	
	function addAlert() {
		const alert: Alert = {
			id: crypto.randomUUID(),
			type: newAlertType,
			symbol: newAlertSymbol,
			condition: newAlertCondition,
			value: newAlertValue,
			message: newAlertMessage || `${newAlertSymbol} ${newAlertCondition} ${newAlertValue}`,
			triggered: false,
			createdAt: Date.now()
		};
		alerts = [...alerts, alert];
		showForm = false;
		resetForm();
	}
	
	function removeAlert(id: string) {
		alerts = alerts.filter(a => a.id !== id);
	}
	
	function resetForm() {
		newAlertType = 'price';
		newAlertSymbol = 'BTC-PERP';
		newAlertCondition = 'above';
		newAlertValue = 0;
		newAlertMessage = '';
	}
	
	function getAlertIcon(type: string) {
		return type === 'price' ? 'dollar' : type === 'rsi' ? 'bar-chart' : type === 'drawdown' ? 'warning' : 'alarm';
	}
	
	function formatTime(ts: number) {
		return new Date(ts).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
	}
</script>

<div class="rounded-lg border bg-card p-4">
	<div class="flex items-center justify-between mb-4">
		<h2 class="text-sm font-semibold">Alerts ({alerts.length})</h2>
		<button 
			on:click={() => showForm = !showForm}
			class="rounded-md bg-primary px-3 py-1 text-xs font-medium text-primary-foreground hover:bg-primary/90"
		>
			{showForm ? 'Cancel' : '+ New Alert'}
		</button>
	</div>
	
	{#if showForm}
		<div class="mb-4 space-y-2 rounded-lg bg-secondary/50 p-3">
			<div class="grid grid-cols-2 gap-2">
				<select bind:value={newAlertType} class="rounded bg-background px-2 py-1 text-xs border">
					<option value="price">Price</option>
					<option value="rsi">RSI</option>
					<option value="drawdown">Drawdown %</option>
					<option value="custom">Custom</option>
				</select>
				<input 
					type="text" 
					bind:value={newAlertSymbol} 
					placeholder="Symbol" 
					class="rounded bg-background px-2 py-1 text-xs border"
				/>
			</div>
			<div class="grid grid-cols-2 gap-2">
				<select bind:value={newAlertCondition} class="rounded bg-background px-2 py-1 text-xs border">
					<option value="above">Above</option>
					<option value="below">Below</option>
					<option value="crosses">Crosses</option>
				</select>
				<input 
					type="number" 
					bind:value={newAlertValue} 
					placeholder="Value" 
					class="rounded bg-background px-2 py-1 text-xs border"
				/>
			</div>
			<input 
				type="text" 
				bind:value={newAlertMessage} 
				placeholder="Message (optional)" 
				class="w-full rounded bg-background px-2 py-1 text-xs border"
			/>
			<button 
				on:click={addAlert}
				class="w-full rounded-md bg-primary py-1 text-xs font-medium text-primary-foreground hover:bg-primary/90"
			>
				Create Alert
			</button>
		</div>
	{/if}
	
	<div class="space-y-2 max-h-[300px] overflow-y-auto">
		{#each alerts as alert}
			<div class="flex items-center justify-between rounded-md bg-secondary/50 px-3 py-2 {alert.triggered ? 'border border-amber-500/30' : ''}">
				<div class="flex items-center gap-2">
					<Icon name={getAlertIcon(alert.type)} size="1.5rem" class_name="text-muted-foreground" />
					<div>
						<p class="text-sm font-medium {alert.triggered ? 'text-amber-400' : ''}">{alert.message}</p>
						<p class="text-xs text-muted-foreground">{alert.symbol} • {formatTime(alert.createdAt)}</p>
					</div>
				</div>
				<div class="flex items-center gap-2">
					{#if alert.triggered}
						<span class="rounded bg-amber-500/20 px-1.5 py-0.5 text-xs text-amber-400">TRIGGERED</span>
					{/if}
					<button 
						on:click={() => removeAlert(alert.id)}
						class="text-muted-foreground hover:text-red-400 transition-colors"
					>
						✕
					</button>
				</div>
			</div>
		{/each}
	</div>
</div>
