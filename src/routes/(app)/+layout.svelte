<script lang="ts">
	import '../../app.css';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { liveState, startPolling } from '$lib/api';
	import { onMount } from 'svelte';

	
	let sidebarOpen = true;
	let mobileMenuOpen = false;
	let userMenuOpen = false;
	let stopPolling: (() => void) | null = null;
	let tickerPrices: Record<string, { price: string; change: number }> = {};
	let tickerInterval: ReturnType<typeof setInterval>;
	
	const tickerSymbols = [
		{ symbol: 'BTCUSDT', label: 'BTC', icon: 'https://assets.coingecko.com/coins/images/1/small/bitcoin.png' },
		{ symbol: 'ETHUSDT', label: 'ETH', icon: 'https://assets.coingecko.com/coins/images/279/small/ethereum.png' },
		{ symbol: 'SOLUSDT', label: 'SOL', icon: 'https://assets.coingecko.com/coins/images/4128/small/solana.png' },
		{ symbol: 'BNBUSDT', label: 'BNB', icon: 'https://assets.coingecko.com/coins/images/825/small/bnb-icon2_2x.png' },
		{ symbol: 'XRPUSDT', label: 'XRP', icon: 'https://assets.coingecko.com/coins/images/44/small/xrp-symbol-white-128.png' },
		{ symbol: 'ADAUSDT', label: 'ADA', icon: 'https://assets.coingecko.com/coins/images/975/small/cardano.png' },
		{ symbol: 'DOGEUSDT', label: 'DOGE', icon: 'https://assets.coingecko.com/coins/images/5/small/dogecoin.png' },
		{ symbol: 'DOTUSDT', label: 'DOT', icon: 'https://assets.coingecko.com/coins/images/12171/small/polkadot.png' },
		{ symbol: 'AVAXUSDT', label: 'AVAX', icon: 'https://assets.coingecko.com/coins/images/12559/small/Avalanche_Circle_RedWhite_Trans.png' },
		{ symbol: 'LINKUSDT', label: 'LINK', icon: 'https://assets.coingecko.com/coins/images/877/small/chainlink-new-logo.png' },
	];
	
	async function fetchTickerPrices() {
		try {
			const symbols = tickerSymbols.map(s => s.symbol);
			const res = await fetch(`https://futures-brokiepedia-api.kentaursoft-com.workers.dev/api/v1/prices?symbols=${encodeURIComponent(JSON.stringify(symbols))}`);
			if (res.ok) {
				const data = await res.json();
				data.forEach((ticker: any) => {
					tickerPrices[ticker.symbol] = {
						price: parseFloat(ticker.lastPrice).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }),
						change: parseFloat(ticker.priceChangePercent)
					};
				});
				tickerPrices = tickerPrices;
			}
		} catch (err) {
			console.error('Ticker fetch error:', err);
		}
	}
	
	onMount(() => {
		stopPolling = startPolling(5000);
		fetchTickerPrices();
		tickerInterval = setInterval(fetchTickerPrices, 5000);
		return () => {
			if (stopPolling) stopPolling();
			clearInterval(tickerInterval);
		};
	});
	
	$: daemonConnected = $liveState ? true : false;
	$: systemStatus = $liveState?.systemStatus || 'paper';
	
	const navItems = [
		{ path: '/', label: 'Dashboard', icon: 'dashboard' },
		{ path: '/trade', label: 'Trade', icon: 'chart' },
		{ path: '/positions', label: 'Positions', icon: 'portfolio' },
		{ path: '/signals', label: 'Signals', icon: 'signal' },
		{ path: '/analytics', label: 'Analytics', icon: 'analytics' },
		{ path: '/settings', label: 'Settings', icon: 'settings' },
	];
	
	function toggleSidebar() {
		sidebarOpen = !sidebarOpen;
	}
	
	function navigateTo(path: string) {
		goto(path);
		mobileMenuOpen = false;
	}
	
	function logout() {
		document.cookie = 'session_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Strict';
		window.location.href = '/auth';
	}
</script>

<div class="min-h-screen bg-background text-foreground flex">
	<!-- Mobile Overlay -->
	{#if mobileMenuOpen}
		<div class="fixed inset-0 bg-black/50 z-40 lg:hidden" on:click={() => mobileMenuOpen = false}></div>
	{/if}
	
	<!-- Sidebar -->
	<aside class="{sidebarOpen ? 'w-64' : 'w-16'} {mobileMenuOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0 transition-all duration-300 bg-card border-r border-border fixed lg:relative h-screen z-50 flex flex-col">
		<!-- Logo -->
		<div class="h-16 flex items-center px-4 border-b border-border">
			<div class="w-8 h-8 rounded-lg bg-primary flex items-center justify-center mr-3">
				<span class="text-primary-foreground font-bold text-sm">FB</span>
			</div>
			{#if sidebarOpen}
				<span class="font-bold text-lg">Futures Brokiepedia</span>
			{/if}
			<button class="ml-auto lg:block hidden p-1 hover:bg-muted rounded" on:click={toggleSidebar}>
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={sidebarOpen ? "M11 19l-7-7 7-7m8 14l-7-7 7-7" : "M4 6h16M4 12h16M4 18h16"}></path>
				</svg>
			</button>
		</div>
		
		<!-- Navigation -->
		<nav class="flex-1 py-4 px-2 space-y-1">
			{#each navItems as item}
				<button
					class="w-full flex items-center px-3 py-2.5 rounded-lg transition-colors {$page.url.pathname === item.path ? 'bg-primary text-primary-foreground' : 'hover:bg-muted'}"
					on:click={() => navigateTo(item.path)}
				>
					<svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						{#if item.icon === 'dashboard'}
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"></path>
						{:else if item.icon === 'chart'}
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"></path>
						{:else if item.icon === 'portfolio'}
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path>
						{:else if item.icon === 'signal'}
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
						{:else if item.icon === 'analytics'}
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
						{:else if item.icon === 'settings'}
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
						{/if}
					</svg>
					{#if sidebarOpen}
						<span class="ml-3">{item.label}</span>
					{/if}
				</button>
			{/each}
		</nav>
		
		<!-- Status Footer -->
		<div class="p-4 border-t border-border">
			<div class="flex items-center gap-2">
				<div class="w-2 h-2 rounded-full {daemonConnected ? 'bg-green-500' : 'bg-red-500'}"></div>
				{#if sidebarOpen}
					<span class="text-sm">{daemonConnected ? 'Daemon Online' : 'Offline'}</span>
					<span class="ml-auto text-xs px-2 py-0.5 rounded-full {systemStatus === 'live' ? 'bg-red-500/20 text-red-400' : 'bg-yellow-500/20 text-yellow-400'}">
						{systemStatus.toUpperCase()}
					</span>
				{/if}
			</div>
		</div>
	</aside>
	
	<!-- Main Content -->
	<div class="flex-1 flex flex-col min-h-screen">
		<!-- Top Header -->
		<header class="h-16 bg-card border-b border-border flex items-center px-6">
			<button class="lg:hidden mr-4 p-2 hover:bg-muted rounded" on:click={() => mobileMenuOpen = true}>
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
				</svg>
			</button>
			
			<!-- Live Crypto Ticker -->
			<div class="flex-1 overflow-hidden flex items-center">
				<div class="flex items-center gap-6 px-4 overflow-x-auto whitespace-nowrap">
					{#each tickerSymbols as { symbol, label, icon } (symbol)}
						<div class="flex items-center gap-2 flex-shrink-0">
							<img 
								src={icon}
								alt={label}
								class="w-4 h-4 rounded-full"
								on:error={(e) => { e.target.style.display = 'none'; }}
							/>
							<span class="text-sm font-medium">{label}</span>
							<span class="text-sm">${tickerPrices[symbol]?.price ?? '--'}</span>
							<span class="text-xs {tickerPrices[symbol]?.change >= 0 ? 'text-green-400' : 'text-red-400'}">
								{tickerPrices[symbol]?.change >= 0 ? '+' : ''}{tickerPrices[symbol]?.change?.toFixed(2) ?? '--'}%
							</span>
						</div>
					{/each}
				</div>
			</div>
			
			<div class="ml-auto flex items-center gap-4">
				<button class="p-2 hover:bg-muted rounded relative">
					<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path>
					</svg>
					<span class="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
				</button>
				<div class="relative">
					<button 
						class="w-8 h-8 rounded-full bg-primary flex items-center justify-center hover:bg-primary/80 transition-colors"
						on:click={() => userMenuOpen = !userMenuOpen}
					>
						<span class="text-primary-foreground text-sm font-bold">K</span>
					</button>
					{#if userMenuOpen}
						<div class="absolute right-0 mt-2 w-48 bg-card border border-border rounded-xl shadow-lg z-50 py-1">
							<div class="px-4 py-2 border-b border-border">
								<p class="text-sm font-medium">Kentaur</p>
								<p class="text-xs text-muted-foreground">Admin</p>
							</div>
							<button 
								class="w-full text-left px-4 py-2 text-sm hover:bg-muted transition-colors flex items-center gap-2"
								on:click={() => { userMenuOpen = false; goto('/settings'); }}
							>
								<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
								</svg>
								Settings
							</button>
							<button 
								class="w-full text-left px-4 py-2 text-sm hover:bg-muted transition-colors text-red-400 flex items-center gap-2"
								on:click={() => { userMenuOpen = false; logout(); }}
							>
								<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
								</svg>
								Sign Out
							</button>
						</div>
					{/if}
				</div>
			</div>
		</header>
		
		<!-- Page Content -->
		<main class="flex-1 p-6 overflow-auto">
			<slot />
		</main>
	</div>
</div>

<style>
	:global(.bg-background) {
		background-color: hsl(224 71% 4%);
	}
	:global(.bg-card) {
		background-color: hsl(224 71% 6%);
	}
	:global(.border-border) {
		border-color: hsl(215 20% 18%);
	}
	:global(.text-foreground) {
		color: hsl(213 31% 91%);
	}
	:global(.text-muted-foreground) {
		color: hsl(215 20% 55%);
	}
	:global(.bg-primary) {
		background-color: hsl(217 91% 60%);
	}
	:global(.text-primary-foreground) {
		color: hsl(213 31% 91%);
	}
	:global(.bg-muted) {
		background-color: hsl(215 20% 15%);
	}
	:global(.hover\\:bg-muted:hover) {
		background-color: hsl(215 20% 15%);
	}
</style>