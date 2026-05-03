import { writable } from 'svelte/store';
import type { DashboardState } from './types';

export const dashboardState = writable<DashboardState>({
	systemStatus: 'paper',
	activeAsset: 'BTC-PERP',
	regime: 'trending_up',
	lastSync: Date.now(),
	todayPnl: 0,
	unrealizedPnl: 0,
	equity: 10000,
	dailyDrawdown: 0,
	executionEnabled: true,
	killSwitchTriggered: false,
	departments: [],
	positions: [],
	activeStrategy: null,
	health: {
		vps: true,
		binance: true,
		deepseek: true,
		turso: true,
		exchanges: 8
	}
});

export const pollInterval = writable<number>(5000);
