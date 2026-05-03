import { dashboardState } from './stores';
import type { DashboardState } from './types';

const API_BASE = 'https://futures-brokiepedia-api.your-subdomain.workers.dev'; // Update after Worker deploy

class ApiClient {
	private token: string | null = null;
	
	constructor() {
		if (typeof window !== 'undefined') {
			this.token = localStorage.getItem('auth_token');
		}
	}
	
	private async fetch(path: string, options?: RequestInit): Promise<unknown> {
		const headers: Record<string, string> = {
			'Content-Type': 'application/json',
		};
		
		if (this.token) {
			headers['Authorization'] = `Bearer ${this.token}`;
		}
		
		const res = await fetch(`${API_BASE}${path}`, {
			...options,
			headers: {
				...headers,
				...options?.headers
			}
		});
		
		if (res.status === 401) {
			// Token expired, redirect to auth
			if (typeof window !== 'undefined') {
				localStorage.removeItem('auth_token');
				window.location.href = '/auth';
			}
		}
		
		if (!res.ok) throw new Error(`API error: ${res.status}`);
		return res.json();
	}
	
	async getState(): Promise<DashboardState> {
		return this.fetch('/api/v1/state') as Promise<DashboardState>;
	}
	
	async triggerKillSwitch(): Promise<{ success: boolean }> {
		// Step 1: Get challenge that requires passkey
		const challengeRes = await this.fetch('/api/v1/killswitch/challenge') as { challenge: number[]; challengeId: string };
		
		// Step 2: Prompt user for passkey authentication
		const assertion = await navigator.credentials.get({
			publicKey: {
				challenge: new Uint8Array(challengeRes.challenge),
				rpId: 'futures.brokiepedia.com',
				userVerification: 'required'
			}
		});
		
		if (!assertion) {
			throw new Error('Kill-switch cancelled');
		}
		
		// Step 3: Send kill-switch request with verification
		return this.fetch('/api/v1/killswitch', {
			method: 'POST',
			body: JSON.stringify({ passkey_verified: true })
		}) as Promise<{ success: boolean }>;
	}
	
	async getAuthChallenge(): Promise<{ challenge: number[]; rp: { name: string; id: string } }> {
		return this.fetch('/api/v1/auth/challenge') as Promise<{ challenge: number[]; rp: { name: string; id: string } }>;
	}
	
	isAuthenticated(): boolean {
		return !!this.token;
	}
	
	logout() {
		this.token = null;
		if (typeof window !== 'undefined') {
			localStorage.removeItem('auth_token');
		}
	}
}

export const api = new ApiClient();

// Poll live state every 5 seconds
export function startPolling(intervalMs = 5000): () => void {
	const interval = setInterval(async () => {
		try {
			const state = await api.getState();
			dashboardState.set(state);
		} catch (err) {
			console.error('Poll error:', err);
		}
	}, intervalMs);

	return () => clearInterval(interval);
}
