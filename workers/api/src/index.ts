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
}

// CORS headers for frontend
const corsHeaders = {
	'Access-Control-Allow-Origin': '*',
	'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
	'Access-Control-Allow-Headers': 'Content-Type, Authorization',
};

// In-memory store for challenges (use KV in production)
const challenges = new Map<string, { challenge: Uint8Array; expires: number }>();

export default {
	async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
		if (request.method === 'OPTIONS') {
			return new Response(null, { headers: corsHeaders });
		}

		const url = new URL(request.url);
		const path = url.pathname;

		try {
			// Health check
			if (path === '/health') {
				return jsonResponse({ status: 'ok', timestamp: Date.now() });
			}

			// Live state — dashboard polls this every 5s
			if (path === '/api/v1/state') {
				const state = await env.LIVE_STATE.get('dashboard_state');
				return jsonResponse(state ? JSON.parse(state) : getDefaultState());
			}

			// Kill switch endpoint (requires passkey re-auth)
			if (path === '/api/v1/killswitch' && request.method === 'POST') {
				const body = await request.json() as { passkey_verified?: boolean };
				
				if (!body.passkey_verified) {
					return jsonResponse({ error: 'Passkey verification required for kill-switch' }, 403);
				}
				
				await env.LIVE_STATE.put('execution_enabled', 'false');
				await env.LIVE_STATE.put('dashboard_state', JSON.stringify({
					...getDefaultState(),
					systemStatus: 'halted',
					killSwitchTriggered: true,
					killSwitchTime: Date.now()
				}));
				
				// Log to D1
				await env.AUDIT_DB.prepare(
					`INSERT INTO audit_log (id, event_type, payload_json, created_at) 
					 VALUES (?, ?, ?, ?)`
				).bind(
					crypto.randomUUID(),
					'kill_switch_triggered',
					JSON.stringify({ source: 'dashboard', passkey_verified: true, timestamp: Date.now() }),
					Date.now()
				).run();

				// Send Telegram alert
				ctx.waitUntil(sendTelegramAlert(env, '🛑 KILL-SWITCH TRIGGERED — All trading halted'));

				return jsonResponse({ success: true, message: 'Kill switch activated' });
			}

			// WebAuthn Challenge
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

			// WebAuthn Register
			if (path === '/api/v1/auth/register' && request.method === 'POST') {
				const body = await request.json() as any;
				
				// In production: verify attestation, store credential in D1
				// For now: accept any valid-looking request
				if (body.id && body.rawId) {
					return jsonResponse({ success: true, message: 'Passkey registered' });
				}
				return jsonResponse({ error: 'Invalid registration data' }, 400);
			}

			// WebAuthn Verify (login)
			if (path === '/api/v1/auth/verify' && request.method === 'POST') {
				const body = await request.json() as any;
				
				// In production: verify signature against stored credential
				// For now: accept any valid-looking request and issue JWT
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

			// Kill-switch challenge (requires fresh passkey auth)
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

			// Agent task enqueue
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
			// Agent task processing will be implemented in Phase 3
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
			chat_id: 'ADMIN_CHAT_ID', // Set during setup
			text: message,
			parse_mode: 'HTML'
		})
	});
}
