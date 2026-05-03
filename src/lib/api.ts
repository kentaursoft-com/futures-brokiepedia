import { dashboardState } from './stores';
import type { DashboardState } from './types';

const API_BASE = 'https://futures-brokiepedia-api.your-subdomain.workers.dev'; // Update after Worker deploy

class ApiClient {
	private async fetch(path: string, options?: RequestInit): Promise<unknown> {
		const res = await fetch(`${API_BASE}${path}`, {
			...options,
			headers: {
				'Content-Type': 'application/json',
				...options?.headers
			}
		});
		if (!res.ok) throw new Error(`API error: ${res.status}`);
		return res.json();
	}

	async getState(): Promise<DashboardState> {
		return this.fetch('/api/v1/state') as Promise<DashboardState>;
	}

	async triggerKillSwitch(): Promise<{ success: boolean }> {
		return this.fetch('/api/v1/killswitch', { method: 'POST' }) as Promise<{ success: boolean }>;
	}

	async getAuthChallenge(): Promise<{ challenge: number[]; rp: { name: string; id: string } }> {
		return this.fetch('/api/v1/auth/challenge') as Promise<{ challenge: number[]; rp: { name: string; id: string } }>;
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
