<script lang="ts">
	export let symbol: string;
	export let size: number = 24;
	
	// CoinGecko coin IDs mapping
	const coinGeckoIds: Record<string, string> = {
		'BTC': 'bitcoin',
		'BTC-PERP': 'bitcoin',
		'ETH': 'ethereum',
		'ETH-PERP': 'ethereum',
		'SOL': 'solana',
		'SOL-PERP': 'solana',
		'BNB': 'binancecoin',
		'BNB-PERP': 'binancecoin',
		'XRP': 'ripple',
		'XRP-PERP': 'ripple',
		'ADA': 'cardano',
		'ADA-PERP': 'cardano',
		'DOGE': 'dogecoin',
		'DOGE-PERP': 'dogecoin',
		'DOT': 'polkadot',
		'DOT-PERP': 'polkadot',
		'MATIC': 'matic-network',
		'MATIC-PERP': 'matic-network',
		'AVAX': 'avalanche-2',
		'AVAX-PERP': 'avalanche-2',
		'LINK': 'chainlink',
		'LINK-PERP': 'chainlink',
		'LTC': 'litecoin',
		'LTC-PERP': 'litecoin',
		'UNI': 'uniswap',
		'UNI-PERP': 'uniswap',
		'ATOM': 'cosmos',
		'ATOM-PERP': 'cosmos',
		'ETC': 'ethereum-classic',
		'ETC-PERP': 'ethereum-classic',
		'NEAR': 'near',
		'NEAR-PERP': 'near',
		'FIL': 'filecoin',
		'FIL-PERP': 'filecoin',
		'TRX': 'tron',
		'TRX-PERP': 'tron',
		'USDT': 'tether',
		'USDC': 'usd-coin',
		'BUSD': 'binance-usd',
	};
	
	// CoinGecko image CDN - most reliable
	$: coinId = coinGeckoIds[symbol.toUpperCase()] || symbol.toLowerCase().replace('-perp', '');
	$: iconUrl = `https://assets.coingecko.com/coins/images/1/small/${coinId}.png`;
	
	// Alternative: use CoinGecko's actual image IDs
	const coinGeckoImageIds: Record<string, number> = {
		'bitcoin': 1,
		'ethereum': 279,
		'solana': 4128,
		'binancecoin': 825,
		'ripple': 44,
		'cardano': 975,
		'dogecoin': 5,
		'polkadot': 12171,
		'matic-network': 4713,
		'avalanche-2': 12559,
		'chainlink': 877,
		'litecoin': 2,
		'uniswap': 12504,
		'cosmos': 1481,
		'ethereum-classic': 453,
		'near': 10365,
		'filecoin': 12817,
		'tron': 1094,
		'tether': 325,
		'usd-coin': 6319,
		'binance-usd': 9576,
	};
	
	$: imageId = coinGeckoImageIds[coinId] || 1;
	$: finalUrl = `https://assets.coingecko.com/coins/images/${imageId}/small/${coinId}.png`;
	
	let error = false;
	
	function handleError() {
		error = true;
	}
</script>

{#if !error}
	<img 
		src={finalUrl} 
		alt={symbol}
		width={size}
		height={size}
		class="inline-block {$$props.class || ''}"
		style="border-radius: 50%;"
		on:error={handleError}
		loading="lazy"
	/>
{:else}
	<!-- Fallback: colored circle with symbol -->
	<div 
		class="inline-flex items-center justify-center rounded-full font-bold text-xs {$$props.class || ''}"
		style="width: {size}px; height: {size}px; background: linear-gradient(135deg, hsl({symbol.length * 30}, 70%, 50%), hsl({symbol.length * 30 + 40}, 70%, 40%)); color: white;"
	>
		{symbol.slice(0, 2)}
	</div>
{/if}
