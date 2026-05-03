import type { D1Database, KVNamespace, Queue } from '@cloudflare/workers-types';

export interface Env {
	LIVE_STATE: KVNamespace;
	AUDIT_DB: D1Database;
	AGENT_QUEUE: Queue;
	DEEPSEEK_API_KEY: string;
	TELEGRAM_BOT_TOKEN: string;
	BINANCE_API_KEY: string;
	BINANCE_SECRET_KEY: string;
	TURSO_DB_TOKEN: string;
	DAEMON_URL: string;  // VPS daemon API endpoint
}

const corsHeaders = {
	'Access-Control-Allow-Origin': '*',
	'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
	'Access-Control-Allow-Headers': 'Content-Type, Authorization',
};

const challenges = new Map<string, { challenge: Uint8Array; expires: number }>();

// Cache daemon state with TTL
let cachedState: any = null;
let stateCacheTime = 0;
const CACHE_TTL_MS = 5000; // 5 seconds

async function fetchDaemonState(env: Env): Promise<any> {
	const now = Date.now();
	if (cachedState && (now - stateCacheTime) < CACHE_TTL_MS) {
		return cachedState;
	}
	
	try {
		const daemonUrl = env.DAEMON_URL || 'http://localhost:8080';
		const res = await fetch(`${daemonUrl}/api/v1/state`, {
			method: 'GET',
			headers: { 'Content-Type': 'application/json' }
		});
		
		if (res.ok) {
			const state = await res.json();
			cachedState = state;
			stateCacheTime = now;
			
			// Also cache in KV for edge reads
			await env.LIVE_STATE.put('dashboard_state', JSON.stringify(state), {
				expirationTtl: 60
			});
			
			return state;
		}
	} catch (e) {
		console.error('Daemon fetch failed:', e);
	}
	
	// Fallback to KV cache
	const fallback = await env.LIVE_STATE.get('dashboard_state');
	return fallback ? JSON.parse(fallback) : getDefaultState();
}

export default {
	async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
		if (request.method === 'OPTIONS') {
			return new Response(null, { headers: corsHeaders });
		}

		const url = new URL(request.url);
		const path = url.pathname;

		try {
			if (path === '/health') {
				return jsonResponse({ 
					status: 'ok', 
					timestamp: Date.now(),
					daemon_connected: !!env.DAEMON_URL 
				});
			}

			if (path === '/api/v1/state') {
				const state = await fetchDaemonState(env);
				return jsonResponse(state);
			}

			if (path === '/api/v1/departments') {
				const state = await fetchDaemonState(env);
				return jsonResponse({
					departments: state.departments || [],
					last_update: state.last_sync || 0
				});
			}

			if (path === '/api/v1/positions') {
				const state = await fetchDaemonState(env);
				return jsonResponse({
					positions: state.positions || [],
					count: (state.positions || []).length
				});
			}

			if (path === '/api/v1/killswitch' && request.method === 'POST') {
				const body = await request.json() as { passkey_verified?: boolean };
				
				if (!body.passkey_verified) {
					return jsonResponse({ error: 'Passkey verification required' }, 403);
				}
				
				// Forward to daemon
				try {
					const daemonUrl = env.DAEMON_URL || 'http://localhost:8080';
					await fetch(`${daemonUrl}/api/v1/killswitch`, { method: 'POST' });
				} catch (e) {
					console.error('Daemon kill-switch failed:', e);
				}
				
				await env.LIVE_STATE.put('execution_enabled', 'false');
				
				await env.AUDIT_DB.prepare(
					`INSERT INTO audit_log (id, event_type, payload_json, created_at) 
					 VALUES (?, ?, ?, ?)`
				).bind(
					crypto.randomUUID(),
					'kill_switch_triggered',
					JSON.stringify({ source: 'dashboard', passkey_verified: true, timestamp: Date.now() }),
					Date.now()
				).run();

				ctx.waitUntil(sendTelegramAlert(env, '🛑 KILL-SWITCH TRIGGERED'));
				return jsonResponse({ success: true, message: 'Kill switch activated' });
			}

			if (path === '/api/v1/auth/challenge') {
				const challenge = crypto.getRandomValues(new Uint8Array(32));
				const challengeId = crypto.randomUUID();
				challenges.set(challengeId, { challenge, expires: Date.now() + 60000 });
				
				return jsonResponse({ 
					challenge: Array.from(challenge),
					challengeId,
					rp: { name: 'Futures Brokiepedia', id: 'futures.brokiepedia.com' }
				});
			}

			if (path === '/api/v1/auth/register' && request.method === 'POST') {
				const body = await request.json() as any;
				if (body.id && body.rawId) {
					return jsonResponse({ success: true, message: 'Passkey registered' });
				}
				return jsonResponse({ error: 'Invalid registration data' }, 400);
			}

			if (path === '/api/v1/auth/verify' && request.method === 'POST') {
				const body = await request.json() as any;
				if (body.id && body.rawId && body.response?.signature) {
					const token = btoa(JSON.stringify({
						user: 'admin',
						exp: Date.now() + 86400000,
						iat: Date.now()
					}));
					return jsonResponse({ success: true, token });
				}
				return jsonResponse({ error: 'Invalid authentication data' }, 400);
			}

			if (path === '/api/v1/killswitch/challenge') {
				const challenge = crypto.getRandomValues(new Uint8Array(32));
				const challengeId = crypto.randomUUID();
				challenges.set(challengeId, { challenge, expires: Date.now() + 60000 });
				
				return jsonResponse({
					challenge: Array.from(challenge),
					challengeId,
					message: 'Confirm kill-switch with passkey'
				});
			}

			if (path === '/api/v1/agent/task' && request.method === 'POST') {
				const body = await request.json();
				await env.AGENT_QUEUE.send(body);
				return jsonResponse({ success: true, message: 'Task queued' });
			}

			return jsonResponse({ error: 'Not found' }, 404);
		} catch (err) {
			console.error('API Error:', err);
			return jsonResponse({ error: 'Internal server error' }, 500);
		}
	},

	async queue(batch: MessageBatch, env: Env, ctx: ExecutionContext): Promise<void> {
		for (const message of batch.messages) {
			console.log('Processing agent task:', message.body);
		}
	}
};

function jsonResponse(data: unknown, status = 200): Response {
	return new Response(JSON.stringify(data), {
		status,
		headers: {
			'Content-Type': 'application/json',
			...corsHeaders
		}
	});
}

function getDefaultState() {
	return {
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
	};
}

async function sendTelegramAlert(env: Env, message: string): Promise<void> {
	const url = `https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/sendMessage`;
	await fetch(url, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({
			chat_id: 'ADMIN_CHAT_ID',
			text: message,
			parse_mode: 'HTML'
		})
	});
}
