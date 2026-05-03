<script lang="ts">
	interface TradeIdea {
		id: string;
		author: string;
		avatar: string;
		symbol: string;
		side: 'long' | 'short';
		entry: number;
		target: number;
		stop: number;
		reasoning: string;
		likes: number;
		liked: boolean;
		timestamp: number;
	}
	
	let ideas: TradeIdea[] = [
		{
			id: '1',
			author: 'QuantBot_Alpha',
			avatar: '🤖',
			symbol: 'BTC-PERP',
			side: 'long',
			entry: 43200,
			target: 45000,
			stop: 42500,
			reasoning: 'EMA20 crossing above EMA50 on 4h timeframe. Volume confirms breakout. Funding rate negative = bullish contrarian signal.',
			likes: 42,
			liked: false,
			timestamp: Date.now() - 1800000
		},
		{
			id: '2',
			author: 'TrendHunter',
			avatar: '📈',
			symbol: 'ETH-PERP',
			side: 'short',
			entry: 2580,
			target: 2400,
			stop: 2650,
			reasoning: 'RSI divergence on daily. Double top formation. High funding rate suggests overcrowded longs.',
			likes: 28,
			liked: true,
			timestamp: Date.now() - 3600000
		},
		{
			id: '3',
			author: 'FundingArb_Pro',
			avatar: '⚡',
			symbol: 'SOL-PERP',
			side: 'long',
			entry: 98.5,
			target: 110,
			stop: 95,
			reasoning: 'Funding rate >0.08% per 8h on 3 exchanges. Pure arbitrage play — market neutral with positive carry.',
			likes: 67,
			liked: false,
			timestamp: Date.now() - 7200000
		}
	];
	
	function toggleLike(id: string) {
		ideas = ideas.map(idea => {
			if (idea.id === id) {
				return { ...idea, liked: !idea.liked, likes: idea.liked ? idea.likes - 1 : idea.likes + 1 };
			}
			return idea;
		});
	}
	
	function formatTime(ts: number) {
		const mins = Math.floor((Date.now() - ts) / 60000);
		if (mins < 60) return `${mins}m ago`;
		const hours = Math.floor(mins / 60);
		if (hours < 24) return `${hours}h ago`;
		return `${Math.floor(hours / 24)}d ago`;
	}
	
	function getRiskReward(idea: TradeIdea) {
		const risk = Math.abs(idea.entry - idea.stop);
		const reward = Math.abs(idea.target - idea.entry);
		return (reward / risk).toFixed(2);
	}
</script>

<div class="rounded-lg border bg-card p-4">
	<div class="flex items-center justify-between mb-4">
		<h2 class="text-sm font-semibold">Trade Ideas Feed</h2>
		<span class="text-xs text-muted-foreground">Anonymized setups from agents</span>
	</div>
	
	<div class="space-y-4 max-h-[500px] overflow-y-auto">
		{#each ideas as idea}
			<div class="rounded-lg bg-secondary/50 p-4 space-y-3">
				<div class="flex items-center justify-between">
					<div class="flex items-center gap-2">
						<span class="text-xl">{idea.avatar}</span>
						<div>
							<p class="text-sm font-medium">{idea.author}</p>
							<p class="text-xs text-muted-foreground">{formatTime(idea.timestamp)}</p>
						</div>
					</div>
					<span class="rounded px-2 py-0.5 text-xs font-medium {idea.side === 'long' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}">
						{idea.side.toUpperCase()}
					</span>
				</div>
				
				<div class="flex items-center gap-4 text-sm">
					<div>
						<span class="text-xs text-muted-foreground">Symbol</span>
						<p class="font-medium">{idea.symbol}</p>
					</div>
					<div>
						<span class="text-xs text-muted-foreground">Entry</span>
						<p class="font-medium">${idea.entry.toLocaleString()}</p>
					</div>
					<div>
						<span class="text-xs text-muted-foreground">Target</span>
						<p class="font-medium text-emerald-400">${idea.target.toLocaleString()}</p>
					</div>
					<div>
						<span class="text-xs text-muted-foreground">Stop</span>
						<p class="font-medium text-red-400">${idea.stop.toLocaleString()}</p>
					</div>
					<div>
						<span class="text-xs text-muted-foreground">R:R</span>
						<p class="font-medium">{getRiskReward(idea)}:1</p>
					</div>
				</div>
				
				<p class="text-sm text-muted-foreground">{idea.reasoning}</p>
				
				<div class="flex items-center gap-4 pt-2 border-t border-border">
					<button 
						on:click={() => toggleLike(idea.id)}
						class="flex items-center gap-1 text-sm {idea.liked ? 'text-pink-400' : 'text-muted-foreground hover:text-pink-400'} transition-colors"
					>
						{idea.liked ? '❤️' : '🤍'} {idea.likes}
					</button>
					<button class="text-sm text-muted-foreground hover:text-foreground transition-colors">
						💾 Save
					</button>
					<button class="text-sm text-muted-foreground hover:text-foreground transition-colors">
						📋 Copy Setup
					</button>
				</div>
			</div>
		{/each}
	</div>
	
	<p class="mt-4 text-xs text-muted-foreground text-center">
		⚠️ These are agent-generated ideas. Always verify with your own analysis.
	</p>
</div>
