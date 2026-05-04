<script lang="ts">
	let username = '';
	let password = '';
	let isLoading = false;
	let error = '';
	let success = '';
	
	async function login() {
		try {
			isLoading = true;
			error = '';
			
			if (!username.trim() || !password.trim()) {
				error = 'Please enter both username and password';
				return;
			}
			
			const res = await fetch('/api/v1/auth/login', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ username: username.trim(), password })
			});
			
			const data = await res.json();
			
			if (!res.ok) {
				throw new Error(data.error || 'Login failed');
			}
			
			// Set session cookie
			document.cookie = `session_token=${data.token}; path=/; max-age=86400; SameSite=Strict`;
			
			success = 'Welcome back! Redirecting...';
			setTimeout(() => {
				window.location.href = '/';
			}, 800);
			
		} catch (err) {
			error = err instanceof Error ? err.message : 'Login failed. Please try again.';
			console.error('Login error:', err);
		} finally {
			isLoading = false;
		}
	}
	
	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter') {
			login();
		}
	}
</script>

<svelte:head>
	<title>Sign In | Futures Brokiepedia</title>
</svelte:head>

<div class="min-h-screen flex items-center justify-center bg-background">
	<div class="w-full max-w-md space-y-6 p-8 rounded-xl border border-border bg-card">
		<div class="text-center space-y-2">
			<div class="w-12 h-12 rounded-xl bg-primary flex items-center justify-center mx-auto mb-4">
				<span class="text-primary-foreground font-bold text-xl">FB</span>
			</div>
			<h1 class="text-2xl font-bold">Futures Brokiepedia</h1>
			<p class="text-sm text-muted-foreground">Sign in to access your dashboard</p>
		</div>
		
		<div class="space-y-4">
			<div>
				<label class="block text-sm font-medium mb-2" for="username">Username</label>
				<input
					id="username"
					type="text"
					bind:value={username}
					on:keydown={handleKeydown}
					placeholder="Enter your username"
					class="w-full px-4 py-3 bg-muted border border-border rounded-lg focus:outline-none focus:border-primary text-foreground placeholder:text-muted-foreground"
				/>
			</div>
			
			<div>
				<label class="block text-sm font-medium mb-2" for="password">Password</label>
				<input
					id="password"
					type="password"
					bind:value={password}
					on:keydown={handleKeydown}
					placeholder="Enter your password"
					class="w-full px-4 py-3 bg-muted border border-border rounded-lg focus:outline-none focus:border-primary text-foreground placeholder:text-muted-foreground"
				/>
			</div>
			
			<button
				on:click={login}
				disabled={isLoading}
				class="w-full rounded-lg bg-primary px-4 py-3 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
			>
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"></path>
				</svg>
				{#if isLoading}
					Signing in...
				{:else}
					Sign In
				{/if}
			</button>
		</div>
		
		{#if error}
			<div class="rounded-lg bg-red-500/10 border border-red-500/20 p-4">
				<p class="text-sm text-red-400 font-medium">Authentication Error</p>
				<p class="text-sm text-red-400/80 mt-1">{error}</p>
			</div>
		{/if}
		
		{#if success}
			<div class="rounded-lg bg-emerald-500/10 border border-emerald-500/20 p-4">
				<p class="text-sm text-emerald-400 font-medium">Success</p>
				<p class="text-sm text-emerald-400/80 mt-1">{success}</p>
			</div>
		{/if}
		
		<p class="text-center text-xs text-muted-foreground">
			Protected by secure authentication
		</p>
	</div>
</div>

<style>
	:global(.bg-background) { background-color: hsl(224 71% 4%); }
	:global(.bg-card) { background-color: hsl(224 71% 6%); }
	:global(.border-border) { border-color: hsl(215 20% 18%); }
	:global(.text-muted-foreground) { color: hsl(215 20% 55%); }
	:global(.bg-primary) { background-color: hsl(217 91% 60%); }
	:global(.text-primary-foreground) { color: hsl(213 31% 91%); }
	:global(.bg-muted) { background-color: hsl(215 20% 12%); }
	:global(.text-foreground) { color: hsl(213 31% 91%); }
</style>
