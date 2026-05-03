<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	
	let isRegistering = false;
	let error = '';
	let success = '';
	
	async function registerPasskey() {
		try {
			isRegistering = true;
			error = '';
			
			// Get challenge from server
			const challengeRes = await fetch('/api/v1/auth/challenge');
			const { challenge, rp } = await challengeRes.json();
			
			// Create credential
			const credential = await navigator.credentials.create({
				publicKey: {
					challenge: new Uint8Array(challenge),
					rp: { name: rp.name, id: rp.id },
					user: {
						id: new TextEncoder().encode('user-001'),
						name: 'admin@brokiepedia.com',
						displayName: 'Admin'
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
				throw new Error('Passkey creation cancelled');
			}
			
			// Send to server for verification
			const verifyRes = await fetch('/api/v1/auth/register', {
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
			
			if (verifyRes.ok) {
				success = 'Passkey registered successfully!';
				setTimeout(() => goto('/'), 1500);
			} else {
				throw new Error('Server verification failed');
			}
		} catch (err) {
			error = err instanceof Error ? err.message : 'Unknown error';
		} finally {
			isRegistering = false;
		}
	}
	
	async function authenticate() {
		try {
			isRegistering = true;
			error = '';
			
			// Get challenge from server
			const challengeRes = await fetch('/api/v1/auth/challenge');
			const { challenge, rp } = await challengeRes.json();
			
			// Get credential
			const assertion = await navigator.credentials.get({
				publicKey: {
					challenge: new Uint8Array(challenge),
					rpId: rp.id,
					userVerification: 'required'
				}
			});
			
			if (!assertion) {
				throw new Error('Authentication cancelled');
			}
			
			// Verify with server
			const verifyRes = await fetch('/api/v1/auth/verify', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					id: assertion.id,
					rawId: Array.from(new Uint8Array((assertion as any).rawId)),
					response: {
						authenticatorData: Array.from(new Uint8Array((assertion as any).response.authenticatorData)),
						clientDataJSON: Array.from(new Uint8Array((assertion as any).response.clientDataJSON)),
						signature: Array.from(new Uint8Array((assertion as any).response.signature)),
						userHandle: (assertion as any).response.userHandle ? Array.from(new Uint8Array((assertion as any).response.userHandle)) : null
					},
					type: assertion.type
				})
			});
			
			if (verifyRes.ok) {
				const { token } = await verifyRes.json();
				localStorage.setItem('auth_token', token);
				success = 'Authenticated successfully!';
				setTimeout(() => goto('/'), 1000);
			} else {
				throw new Error('Authentication failed');
			}
		} catch (err) {
			error = err instanceof Error ? err.message : 'Unknown error';
		} finally {
			isRegistering = false;
		}
	}
	
	function isPasskeySupported() {
		return window.PublicKeyCredential !== undefined;
	}
</script>

<div class="min-h-screen flex items-center justify-center bg-background">
	<div class="w-full max-w-md space-y-6 p-8 rounded-lg border bg-card">
		<div class="text-center space-y-2">
			<h1 class="text-2xl font-bold">Futures Brokiepedia</h1>
			<p class="text-sm text-muted-foreground">Secure access with passkey authentication</p>
		</div>
		
		{#if !isPasskeySupported()}
			<div class="rounded-lg bg-amber-500/10 border border-amber-500/20 p-4 text-sm text-amber-400">
				⚠️ Your browser doesn't support passkeys. Please use a modern browser like Chrome, Safari, or Edge.
			</div>
		{:else}
			<div class="space-y-4">
				<button
					on:click={authenticate}
					disabled={isRegistering}
					class="w-full rounded-md bg-primary px-4 py-3 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-50"
				>
					{#if isRegistering}
						Authenticating...
					{:else}
						🔐 Sign in with Passkey
					{/if}
				</button>
				
				<div class="relative">
					<div class="absolute inset-0 flex items-center">
						<span class="w-full border-t"></span>
					</div>
					<div class="relative flex justify-center text-xs uppercase">
						<span class="bg-card px-2 text-muted-foreground">or</span>
					</div>
				</div>
				
				<button
					on:click={registerPasskey}
					disabled={isRegistering}
					class="w-full rounded-md bg-secondary px-4 py-3 text-sm font-medium text-secondary-foreground hover:bg-secondary/80 transition-colors disabled:opacity-50"
				>
					{#if isRegistering}
						Registering...
					{:else}
						📝 Register New Passkey
					{/if}
				</button>
			</div>
		{/if}
		
		{#if error}
			<div class="rounded-lg bg-red-500/10 border border-red-500/20 p-4 text-sm text-red-400">
				❌ {error}
			</div>
		{/if}
		
		{#if success}
			<div class="rounded-lg bg-emerald-500/10 border border-emerald-500/20 p-4 text-sm text-emerald-400">
				✅ {success}
			</div>
		{/if}
		
		<p class="text-center text-xs text-muted-foreground">
			Protected by WebAuthn / FIDO2
		</p>
	</div>
</div>
