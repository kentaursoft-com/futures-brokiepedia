<script lang="ts">
	import { onMount } from 'svelte';
	import { toast } from '$lib/toast';
	
	let activeSection = 'api';
	
	const sections = [
		{ id: 'api', label: 'API Keys', icon: 'key' },
		{ id: 'trading', label: 'Trading Preferences', icon: 'settings' },
		{ id: 'notifications', label: 'Notifications', icon: 'bell' },
		{ id: 'security', label: 'Security', icon: 'shield' },
		{ id: 'system', label: 'System', icon: 'server' },
	];
	
	// API Keys (masked)
	let apiKeys = {
		binance: '',
		binanceSecret: '',
		deepseek: '',
		telegram: '',
		turso: '',
	};
	
	// Trading preferences
	let tradingPrefs = {
		defaultLeverage: 10,
		maxPositionSize: 1000,
		riskPerTrade: 2,
		defaultTimeframe: '1h',
		autoTrade: false,
		tpDefault: 2.0,
		slDefault: 1.0,
	};
	
	// Notifications
	let notifications: Record<string, boolean | number> = {
		email: false,
		telegram: true,
		signals: true,
		trades: true,
		alerts: true,
		priceThreshold: 5,
	};
	
	// Security / Passkey
	let hasPasskey = false;
	let isAddingPasskey = false;
	let passkeyError = '';
	let passkeySuccess = '';
	
	// System
	let systemSettings = {
		pollingInterval: 5000,
		logLevel: 'info',
		paperTrading: true,
		darkMode: true,
	};
	
	const timeframes = ['1m', '5m', '15m', '1h', '4h', '1d'];
	const logLevels = ['debug', 'info', 'warn', 'error'];
	
	let isSaving = false;
	let hasUnsavedChanges = false;
	
	function markChanged() {
		hasUnsavedChanges = true;
	}
	
	async function saveSettings() {
		try {
			isSaving = true;
			const token = localStorage.getItem('auth_token');
			const res = await fetch('https://futures-brokiepedia-api.kentaursoft-com.workers.dev/api/v1/settings', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'Authorization': `Bearer ${token}`
				},
				body: JSON.stringify({
					apiKeys: {
						binance: apiKeys.binance ? '***' : '',
						binanceSecret: apiKeys.binanceSecret ? '***' : '',
						deepseek: apiKeys.deepseek ? '***' : '',
						telegram: apiKeys.telegram ? '***' : '',
						turso: apiKeys.turso ? '***' : ''
					},
					trading: tradingPrefs,
					notifications: notifications,
					system: systemSettings
				})
			});
			
			if (res.ok) {
				hasUnsavedChanges = false;
				toast.success('Settings saved successfully!');
			} else {
				const err = await res.json();
				toast.error(err.error || 'Failed to save settings');
			}
		} catch (err) {
			toast.error('Network error. Please try again.');
			console.error('Save settings error:', err);
		} finally {
			isSaving = false;
		}
	}
	
	async function loadSettings() {
		try {
			const token = localStorage.getItem('auth_token');
			const res = await fetch('https://futures-brokiepedia-api.kentaursoft-com.workers.dev/api/v1/settings', {
				headers: { 'Authorization': `Bearer ${token}` }
			});
			if (res.ok) {
				const data = await res.json();
				if (data.trading) tradingPrefs = { ...tradingPrefs, ...data.trading };
				if (data.notifications) notifications = { ...notifications, ...data.notifications };
				if (data.system) systemSettings = { ...systemSettings, ...data.system };
			}
		} catch (err) {
			console.error('Load settings error:', err);
		}
	}
	
	function isPasskeySupported() {
		return typeof window !== 'undefined' && window.PublicKeyCredential !== undefined;
	}
	
	async function addPasskey() {
		try {
			isAddingPasskey = true;
			passkeyError = '';
			passkeySuccess = '';
			
			// Get challenge from server
			const challengeRes = await fetch('https://futures-brokiepedia-api.kentaursoft-com.workers.dev/api/v1/auth/challenge');
			if (!challengeRes.ok) throw new Error('Failed to get challenge');
			
			const { challenge, rp } = await challengeRes.json();
			
			// Create credential
			const credential = await navigator.credentials.create({
				publicKey: {
					challenge: new Uint8Array(challenge),
					rp: { name: rp.name, id: rp.id },
					user: {
						id: new TextEncoder().encode('user-001'),
						name: 'Kentaur',
						displayName: 'Kentaur'
					},
					pubKeyCredParams: [
						{ alg: -7, type: 'public-key' },
						{ alg: -257, type: 'public-key' }
					],
					authenticatorSelection: {
						residentKey: 'required',
						userVerification: 'required'
					},
					attestation: 'none'
				}
			});
			
			if (!credential) {
				throw new Error('Passkey registration cancelled');
			}
			
			// Send to server
			const verifyRes = await fetch('https://futures-brokiepedia-api.kentaursoft-com.workers.dev/api/v1/auth/register', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					id: credential.id,
					rawId: Array.from(new Uint8Array((credential as any).rawId)),
					response: {
						clientDataJSON: Array.from(new Uint8Array((credential as any).response.clientDataJSON)),
						attestationObject: Array.from(new Uint8Array((credential as any).response.attestationObject))
					},
					type: credential.type
				})
			});
			
			if (!verifyRes.ok) {
				const err = await verifyRes.json();
				throw new Error(err.error || 'Registration failed');
			}
			
			hasPasskey = true;
			passkeySuccess = 'Passkey added successfully! You can now sign in with your passkey.';
			
		} catch (err) {
			passkeyError = err instanceof Error ? err.message : 'Failed to add passkey. Please try again.';
			console.error('Passkey error:', err);
		} finally {
			isAddingPasskey = false;
		}
	}
	
	async function removePasskey() {
		// In a real app, this would call the backend to remove the passkey
		hasPasskey = false;
		passkeySuccess = 'Passkey removed.';
	}
	
	onMount(() => {
		loadSettings();
		// Check if passkey is supported and if user already has one registered
		// In a real app, you'd fetch this from the backend
		hasPasskey = false;
	});
</script>

<svelte:head>
	<title>Settings | Futures Brokiepedia</title>
</svelte:head>

<div class="space-y-6">
	<!-- Header -->
	<div>
		<h1 class="text-2xl font-bold">Settings</h1>
		<p class="text-muted-foreground text-sm mt-1">Configure your trading bot and preferences</p>
	</div>
	
	<div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
		<!-- Sidebar -->
		<div class="lg:col-span-1">
			<div class="bg-card border border-border rounded-xl p-2 space-y-1">
				{#each sections as section}
					<button
						class="w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors {activeSection === section.id ? 'bg-primary text-primary-foreground' : 'hover:bg-muted'}"
						on:click={() => activeSection = section.id}
					>
						<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							{#if section.icon === 'key'}
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"></path>
							{:else if section.icon === 'settings'}
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"></path>
							{:else if section.icon === 'bell'}
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path>
							{:else if section.icon === 'shield'}
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path>
							{:else if section.icon === 'server'}
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01"></path>
							{/if}
						</svg>
						<span class="font-medium">{section.label}</span>
					</button>
				{/each}
			</div>
		</div>
		
		<!-- Content -->
		<div class="lg:col-span-3">
			{#if activeSection === 'api'}
				<div class="bg-card border border-border rounded-xl p-6">
					<h2 class="text-lg font-semibold mb-4">API Keys</h2>
					<p class="text-sm text-muted-foreground mb-6">Configure your exchange and service API keys</p>
					
					<div class="space-y-4">
						<div>
							<label class="block text-sm font-medium mb-2">Binance API Key</label>
							<input 
								type="password" 
								bind:value={apiKeys.binance}
								placeholder="Enter Binance API Key"
								class="w-full px-4 py-2 bg-muted border border-border rounded-lg focus:outline-none focus:border-primary"
							/>
						</div>
						
						<div>
							<label class="block text-sm font-medium mb-2">Binance Secret Key</label>
							<input 
								type="password" 
								bind:value={apiKeys.binanceSecret}
								placeholder="Enter Binance Secret Key"
								class="w-full px-4 py-2 bg-muted border border-border rounded-lg focus:outline-none focus:border-primary"
							/>
						</div>
						
						<div class="pt-4 border-t border-border">
							<label class="block text-sm font-medium mb-2">DeepSeek API Key</label>
							<input 
								type="password" 
								bind:value={apiKeys.deepseek}
								placeholder="Enter DeepSeek API Key"
								class="w-full px-4 py-2 bg-muted border border-border rounded-lg focus:outline-none focus:border-primary"
							/>
						</div>
						
						<div>
							<label class="block text-sm font-medium mb-2">Telegram Bot Token</label>
							<input 
								type="password" 
								bind:value={apiKeys.telegram}
								placeholder="Enter Telegram Bot Token"
								class="w-full px-4 py-2 bg-muted border border-border rounded-lg focus:outline-none focus:border-primary"
							/>
						</div>
						
						<div>
							<label class="block text-sm font-medium mb-2">Turso Database Token</label>
							<input 
								type="password" 
								bind:value={apiKeys.turso}
								placeholder="Enter Turso Token"
								class="w-full px-4 py-2 bg-muted border border-border rounded-lg focus:outline-none focus:border-primary"
							/>
						</div>
					</div>
				</div>
				
			{:else if activeSection === 'trading'}
				<div class="bg-card border border-border rounded-xl p-6">
					<h2 class="text-lg font-semibold mb-4">Trading Preferences</h2>
					<p class="text-sm text-muted-foreground mb-6">Configure your default trading parameters</p>
					
					<div class="space-y-4">
						<div class="grid grid-cols-2 gap-4">
							<div>
								<label class="block text-sm font-medium mb-2">Default Leverage</label>
								<select bind:value={tradingPrefs.defaultLeverage} class="w-full px-4 py-2 bg-muted border border-border rounded-lg focus:outline-none focus:border-primary">
									{#each [1, 2, 3, 5, 10, 20, 50, 100] as lev}
										<option value={lev}>{lev}x</option>
									{/each}
								</select>
							</div>
							<div>
								<label class="block text-sm font-medium mb-2">Max Position Size ($)</label>
								<input 
									type="number" 
									bind:value={tradingPrefs.maxPositionSize}
									class="w-full px-4 py-2 bg-muted border border-border rounded-lg focus:outline-none focus:border-primary"
								/>
							</div>
						</div>
						
						<div>
							<label class="block text-sm font-medium mb-2">Risk Per Trade (%)</label>
							<input 
								type="range" 
								bind:value={tradingPrefs.riskPerTrade}
								min="0.5" 
								max="10" 
								step="0.5"
								class="w-full"
							/>
							<span class="text-sm text-muted-foreground">{tradingPrefs.riskPerTrade}%</span>
						</div>
						
						<div>
							<label class="block text-sm font-medium mb-2">Default Timeframe</label>
							<select bind:value={tradingPrefs.defaultTimeframe} class="w-full px-4 py-2 bg-muted border border-border rounded-lg focus:outline-none focus:border-primary">
								{#each timeframes as tf}
									<option value={tf}>{tf}</option>
								{/each}
							</select>
						</div>
						
						<div class="grid grid-cols-2 gap-4">
							<div>
								<label class="block text-sm font-medium mb-2">Default TP (R)</label>
								<input 
									type="number" 
									bind:value={tradingPrefs.tpDefault}
									step="0.1"
									class="w-full px-4 py-2 bg-muted border border-border rounded-lg focus:outline-none focus:border-primary"
								/>
							</div>
							<div>
								<label class="block text-sm font-medium mb-2">Default SL (R)</label>
								<input 
									type="number" 
									bind:value={tradingPrefs.slDefault}
									step="0.1"
									class="w-full px-4 py-2 bg-muted border border-border rounded-lg focus:outline-none focus:border-primary"
								/>
							</div>
						</div>
						
						<div class="flex items-center gap-3 pt-4 border-t border-border">
							<input 
								type="checkbox" 
								bind:checked={tradingPrefs.autoTrade}
								class="w-4 h-4 rounded border-border"
							/>
							<div>
								<label class="text-sm font-medium">Auto Trading</label>
								<p class="text-xs text-muted-foreground">Allow AI to execute trades automatically</p>
							</div>
						</div>
					</div>
				</div>
				
			{:else if activeSection === 'notifications'}
				<div class="bg-card border border-border rounded-xl p-6">
					<h2 class="text-lg font-semibold mb-4">Notifications</h2>
					<p class="text-sm text-muted-foreground mb-6">Configure your alert preferences</p>
					
					<div class="space-y-4">
						{#each [
							{ key: 'telegram', label: 'Telegram Alerts', desc: 'Receive alerts via Telegram bot' },
							{ key: 'email', label: 'Email Notifications', desc: 'Receive email summaries' },
							{ key: 'signals', label: 'Trading Signals', desc: 'Notify when new signals are generated' },
							{ key: 'trades', label: 'Trade Executions', desc: 'Notify on trade open/close' },
							{ key: 'alerts', label: 'Price Alerts', desc: 'Notify when price alerts trigger' },
						] as item}
							<div class="flex items-center justify-between p-4 bg-muted rounded-lg">
								<div>
									<p class="font-medium">{item.label}</p>
									<p class="text-sm text-muted-foreground">{item.desc}</p>
								</div>
								<label class="relative inline-flex items-center cursor-pointer">
									<input 
										type="checkbox" 
										checked={!!notifications[item.key]}
										on:change={(e) => notifications[item.key] = e.currentTarget.checked}
										class="sr-only peer"
									/>
									<div class="w-11 h-6 bg-muted peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-primary rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
								</label>
							</div>
						{/each}
						
						<div class="pt-4">
							<label class="block text-sm font-medium mb-2">Price Alert Threshold (%)</label>
							<input 
								type="range" 
								bind:value={notifications.priceThreshold}
								min="1" 
								max="20" 
								step="1"
								class="w-full"
							/>
							<span class="text-sm text-muted-foreground">{notifications.priceThreshold}%</span>
						</div>
					</div>
				</div>
				
			{:else if activeSection === 'security'}
				<div class="bg-card border border-border rounded-xl p-6">
					<h2 class="text-lg font-semibold mb-4">Security</h2>
					<p class="text-sm text-muted-foreground mb-6">Manage your authentication methods</p>
					
					<div class="space-y-6">
						<!-- Current Auth Method -->
						<div class="p-4 bg-muted rounded-lg">
							<div class="flex items-center justify-between">
								<div class="flex items-center gap-3">
									<svg class="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
									</svg>
									<div>
										<p class="font-medium">Password Sign-In</p>
										<p class="text-sm text-muted-foreground">Currently active</p>
									</div>
								</div>
								<span class="px-2 py-1 text-xs font-medium bg-emerald-500/20 text-emerald-400 rounded-full">Active</span>
							</div>
						</div>
						
						<!-- Passkey Section -->
						<div class="pt-4 border-t border-border">
							<h3 class="font-medium mb-2">Passkey Authentication</h3>
							<p class="text-sm text-muted-foreground mb-4">
								Passkeys provide a more secure, passwordless sign-in experience using biometric authentication or device PIN.
							</p>
							
							{#if !isPasskeySupported()}
								<div class="rounded-lg bg-amber-500/10 border border-amber-500/20 p-4 text-sm text-amber-400">
									<p class="font-medium">Browser not supported</p>
									<p class="mt-1">Your browser doesn't support passkeys. Please use Chrome, Safari, or Edge.</p>
								</div>
							{:else if hasPasskey}
								<div class="flex items-center justify-between p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-lg">
									<div class="flex items-center gap-3">
										<svg class="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
										</svg>
										<div>
											<p class="font-medium text-emerald-400">Passkey Registered</p>
											<p class="text-sm text-emerald-400/70">You can sign in with your passkey</p>
										</div>
									</div>
									<button
										on:click={removePasskey}
										class="px-3 py-1.5 text-sm font-medium text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
									>
										Remove
									</button>
								</div>
							{:else}
								<div class="p-4 bg-muted rounded-lg">
									<div class="flex items-center gap-3 mb-4">
										<svg class="w-5 h-5 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path>
										</svg>
										<div>
											<p class="font-medium">No Passkey Registered</p>
											<p class="text-sm text-muted-foreground">Add a passkey for faster, more secure sign-in</p>
										</div>
									</div>
									<button
										on:click={addPasskey}
										disabled={isAddingPasskey}
										class="w-full rounded-lg border border-border bg-card px-4 py-3 text-sm font-medium text-foreground hover:bg-muted transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
									>
										<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
										</svg>
										{#if isAddingPasskey}
											Registering...
										{:else}
											Add Passkey
										{/if}
									</button>
								</div>
							{/if}
							
							{#if passkeyError}
								<div class="mt-4 rounded-lg bg-red-500/10 border border-red-500/20 p-4">
									<p class="text-sm text-red-400 font-medium">Error</p>
									<p class="text-sm text-red-400/80 mt-1">{passkeyError}</p>
								</div>
							{/if}
							
							{#if passkeySuccess}
								<div class="mt-4 rounded-lg bg-emerald-500/10 border border-emerald-500/20 p-4">
									<p class="text-sm text-emerald-400 font-medium">Success</p>
									<p class="text-sm text-emerald-400/80 mt-1">{passkeySuccess}</p>
								</div>
							{/if}
						</div>
						
						<!-- Session Info -->
						<div class="pt-4 border-t border-border">
							<h3 class="font-medium mb-3">Session Information</h3>
							<div class="space-y-2 text-sm">
								<div class="flex justify-between">
									<span class="text-muted-foreground">Signed in as</span>
									<span>Kentaur</span>
								</div>
								<div class="flex justify-between">
									<span class="text-muted-foreground">Authentication</span>
									<span>Password</span>
								</div>
								<div class="flex justify-between">
									<span class="text-muted-foreground">Session expires</span>
									<span>24 hours</span>
								</div>
							</div>
						</div>
					</div>
				</div>
				
			{:else if activeSection === 'system'}
				<div class="bg-card border border-border rounded-xl p-6">
					<h2 class="text-lg font-semibold mb-4">System Settings</h2>
					<p class="text-sm text-muted-foreground mb-6">Configure system behavior</p>
					
					<div class="space-y-4">
						<div>
							<label class="block text-sm font-medium mb-2">Polling Interval (ms)</label>
							<select bind:value={systemSettings.pollingInterval} class="w-full px-4 py-2 bg-muted border border-border rounded-lg focus:outline-none focus:border-primary">
								<option value={1000}>1 second</option>
								<option value={5000}>5 seconds</option>
								<option value={10000}>10 seconds</option>
								<option value={30000}>30 seconds</option>
								<option value={60000}>1 minute</option>
							</select>
						</div>
						
						<div>
							<label class="block text-sm font-medium mb-2">Log Level</label>
							<select bind:value={systemSettings.logLevel} class="w-full px-4 py-2 bg-muted border border-border rounded-lg focus:outline-none focus:border-primary">
								{#each logLevels as level}
									<option value={level}>{level.toUpperCase()}</option>
								{/each}
							</select>
						</div>
						
						<div class="flex items-center gap-3 p-4 bg-muted rounded-lg">
							<input 
								type="checkbox" 
								bind:checked={systemSettings.paperTrading}
								class="w-4 h-4 rounded border-border"
							/>
							<div>
								<label class="text-sm font-medium">Paper Trading Mode</label>
								<p class="text-xs text-muted-foreground">Trade with virtual money for testing</p>
							</div>
						</div>
						
						<div class="flex items-center gap-3 p-4 bg-muted rounded-lg">
							<input 
								type="checkbox" 
								bind:checked={systemSettings.darkMode}
								class="w-4 h-4 rounded border-border"
							/>
							<div>
								<label class="text-sm font-medium">Dark Mode</label>
								<p class="text-xs text-muted-foreground">Use dark theme for the interface</p>
							</div>
						</div>
						
						<div class="pt-4 border-t border-border">
							<h3 class="font-medium mb-3">System Information</h3>
							<div class="space-y-2 text-sm">
								<div class="flex justify-between">
									<span class="text-muted-foreground">Version</span>
									<span>v1.0.0</span>
								</div>
								<div class="flex justify-between">
									<span class="text-muted-foreground">Daemon Status</span>
									<span class="text-green-400">Online</span>
								</div>
								<div class="flex justify-between">
									<span class="text-muted-foreground">Last Sync</span>
									<span>{new Date().toLocaleTimeString()}</span>
								</div>
							</div>
						</div>
					</div>
				</div>
			{/if}
			
			<!-- Save Button -->
			<div class="mt-6 flex items-center justify-end gap-3">
				{#if hasUnsavedChanges}
					<span class="text-sm text-amber-400 flex items-center gap-1">
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
						</svg>
						Unsaved changes
					</span>
				{/if}
				<button 
					on:click={saveSettings}
					disabled={isSaving}
					class="px-6 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
				>
					{#if isSaving}
						<svg class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
							<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
							<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
						</svg>
						Saving...
					{:else}
						Save Settings
					{/if}
				</button>
			</div>
		</div>
	</div>
</div>

<style>
	:global(.bg-card) { background-color: hsl(224 71% 6%); }
	:global(.border-border) { border-color: hsl(215 20% 18%); }
	:global(.text-muted-foreground) { color: hsl(215 20% 55%); }
	:global(.bg-muted) { background-color: hsl(215 20% 12%); }
	:global(.bg-primary) { background-color: hsl(217 91% 60%); }
	:global(.text-primary-foreground) { color: hsl(213 31% 91%); }
	:global(.text-primary) { color: hsl(217 91% 60%); }
	:global(.border-primary) { border-color: hsl(217 91% 60%); }
	:global(.focus\:border-primary:focus) { border-color: hsl(217 91% 60%); }
	:global(.peer-checked\:bg-primary) { background-color: hsl(217 91% 60%); }
	:global(.peer-focus\:ring-primary) { --tw-ring-color: hsl(217 91% 60%); }
	:global(.text-green-400) { color: hsl(142 76% 56%); }
	:global(.text-emerald-400) { color: hsl(160 84% 39%); }
</style>
