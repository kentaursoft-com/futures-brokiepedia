import type { D1Database, KVNamespace, Queue } from "@cloudflare/workers-types";

export interface Env {
  LIVE_STATE: KVNamespace;
  AUDIT_DB: D1Database;
  AGENT_QUEUE: Queue;
  DEEPSEEK_API_KEY: string;
  TELEGRAM_BOT_TOKEN: string;
  BINANCE_API_KEY: string;
  BINANCE_SECRET_KEY: string;
  TURSO_DB_TOKEN: string;
  DAEMON_URL: string;
  VPS_URL?: string;
  VPS_INTERNAL_KEY?: string;
}

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization",
};

const challenges = new Map<
  string,
  { challenge: Uint8Array; expires: number }
>();

// Public endpoints that don't require authentication
const PUBLIC_ENDPOINTS = [
  "/health",
  "/api/v1/health",
  "/api/v1/auth/challenge",
  "/api/v1/auth/register",
  "/api/v1/auth/verify",
  "/api/v1/auth/login",
];

function isPublicEndpoint(path: string): boolean {
  return PUBLIC_ENDPOINTS.some(
    (endpoint) => path === endpoint || path.startsWith(endpoint + "/")
  );
}

function validateSession(request: Request): boolean {
  const cookieHeader = request.headers.get("Cookie");
  if (!cookieHeader) return false;

  const cookies = cookieHeader.split(";").reduce((acc, cookie) => {
    const [key, value] = cookie.trim().split("=");
    acc[key] = value;
    return acc;
  }, {} as Record<string, string>);

  const sessionToken = cookies["session_token"];
  if (!sessionToken) return false;

  try {
    // Simple JWT validation (base64 payload check)
    const parts = sessionToken.split(".");
    if (parts.length !== 3) return false;

    const payload = JSON.parse(atob(parts[1]));
    // Check expiration
    if (payload.exp && payload.exp < Date.now()) return false;

    return true;
  } catch {
    return false;
  }
}

// Cache daemon state with TTL
let cachedState: any = null;
let stateCacheTime = 0;
const CACHE_TTL_MS = 5000;

async function fetchDaemonState(env: Env): Promise<any> {
  const now = Date.now();
  if (cachedState && now - stateCacheTime < CACHE_TTL_MS) {
    return cachedState;
  }

  try {
    const daemonUrl = env.DAEMON_URL || "http://localhost:8080";
    const res = await fetch(`${daemonUrl}/api/v1/state`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        ...(env.VPS_INTERNAL_KEY
          ? { "X-Internal-Key": env.VPS_INTERNAL_KEY }
          : {}),
      },
    });

    if (res.ok) {
      const state = await res.json();
      cachedState = state;
      stateCacheTime = now;

      await env.LIVE_STATE.put("dashboard_state", JSON.stringify(state), {
        expirationTtl: 60,
      });

      return state;
    }
  } catch (e) {
    console.error("Daemon fetch failed:", e);
  }

  const fallback = await env.LIVE_STATE.get("dashboard_state");
  return fallback ? JSON.parse(fallback) : getDefaultState();
}

export default {
  async fetch(
    request: Request,
    env: Env,
    ctx: ExecutionContext,
  ): Promise<Response> {
    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders });
    }

    const url = new URL(request.url);
    const path = url.pathname;

    // Check authentication for non-public endpoints
    if (!isPublicEndpoint(path)) {
      if (!validateSession(request)) {
        return jsonResponse(
          {
            error: "Unauthorized",
            message: "Valid session required. Please authenticate.",
          },
          401,
        );
      }
    }

    try {
      // Health check - PUBLIC
      if (path === "/health" || path === "/api/v1/health") {
        return jsonResponse({
          status: "ok",
          timestamp: Date.now(),
          daemon_connected: !!env.DAEMON_URL,
        });
      }

      // Auth challenge - PUBLIC
      if (path === "/api/v1/auth/challenge") {
        const challenge = crypto.getRandomValues(new Uint8Array(32));
        const challengeId = crypto.randomUUID();
        challenges.set(challengeId, {
          challenge,
          expires: Date.now() + 60000,
        });

        return jsonResponse({
          challenge: Array.from(challenge),
          challengeId,
          rp: { name: "Futures Brokiepedia", id: "futures.brokiepedia.com" },
        });
      }

      // Auth register - PUBLIC
      if (path === "/api/v1/auth/register" && request.method === "POST") {
        const body = (await request.json()) as any;
        if (body.id && body.rawId) {
          // Store credential in D1
          try {
            await env.AUDIT_DB.prepare(
              `INSERT OR REPLACE INTO passkey_credentials (id, raw_id, user_id, created_at) VALUES (?, ?, ?, ?)`,
            )
              .bind(
                body.id,
                JSON.stringify(body.rawId),
                "user-001",
                Date.now(),
              )
              .run();
          } catch (e) {
            console.error("Failed to store credential:", e);
          }

          return jsonResponse({
            success: true,
            message: "Passkey registered",
          });
        }
        return jsonResponse({ error: "Invalid registration data" }, 400);
      }

      // Auth login - PUBLIC (username/password)
      if (path === "/api/v1/auth/login" && request.method === "POST") {
        const body = (await request.json()) as { username?: string; password?: string };
        
        if (!body.username || !body.password) {
          return jsonResponse({ error: "Username and password are required" }, 400);
        }
        
        // Validate credentials
        if (body.username === "Kentaur" && body.password === "BenBen111902!") {
          // Create JWT-like token
          const header = btoa(JSON.stringify({ alg: "none", typ: "JWT" }));
          const payload = btoa(
            JSON.stringify({
              user: "Kentaur",
              username: "Kentaur",
              role: "admin",
              exp: Date.now() + 86400000, // 24 hours
              iat: Date.now(),
              authMethod: "password",
            }),
          );
          const token = `${header}.${payload}.signature`;

          // Log successful auth
          ctx.waitUntil(
            env.AUDIT_DB.prepare(
              `INSERT INTO audit_log (id, event_type, payload_json, created_at) VALUES (?, ?, ?, ?)`,
            )
              .bind(
                crypto.randomUUID(),
                "auth_success",
                JSON.stringify({ user: "Kentaur", method: "password" }),
                Date.now(),
              )
              .run(),
          );

          return jsonResponse({ success: true, token, user: { username: "Kentaur", role: "admin" } });
        }
        
        // Log failed auth attempt
        ctx.waitUntil(
          env.AUDIT_DB.prepare(
            `INSERT INTO audit_log (id, event_type, payload_json, created_at) VALUES (?, ?, ?, ?)`,
          )
            .bind(
              crypto.randomUUID(),
              "auth_failed",
              JSON.stringify({ username: body.username, reason: "invalid_credentials" }),
              Date.now(),
            )
            .run()
            .catch(() => {}),
        );
        
        return jsonResponse({ error: "Invalid username or password" }, 401);
      }

      // Auth verify - PUBLIC
      if (path === "/api/v1/auth/verify" && request.method === "POST") {
        const body = (await request.json()) as any;
        if (body.id && body.rawId && body.response?.signature) {
          // Create JWT-like token
          const header = btoa(JSON.stringify({ alg: "none", typ: "JWT" }));
          const payload = btoa(
            JSON.stringify({
              user: "admin",
              exp: Date.now() + 86400000, // 24 hours
              iat: Date.now(),
            }),
          );
          const token = `${header}.${payload}.signature`;

          // Log successful auth
          ctx.waitUntil(
            env.AUDIT_DB.prepare(
              `INSERT INTO audit_log (id, event_type, payload_json, created_at) VALUES (?, ?, ?, ?)`,
            )
              .bind(
                crypto.randomUUID(),
                "auth_success",
                JSON.stringify({ user: "admin", method: "passkey" }),
                Date.now(),
              )
              .run(),
          );

          return jsonResponse({ success: true, token });
        }
        return jsonResponse({ error: "Invalid authentication data" }, 400);
      }

      // Protected endpoints below

      if (path === "/api/v1/state") {
        const state = await fetchDaemonState(env);
        return jsonResponse(state);
      }

      if (path === "/api/v1/departments") {
        const state = await fetchDaemonState(env);
        return jsonResponse({
          departments: state.departments || [],
          last_update: state.last_sync || 0,
        });
      }

      if (path === "/api/v1/positions") {
        const state = await fetchDaemonState(env);
        return jsonResponse({
          positions: state.positions || [],
          count: (state.positions || []).length,
        });
      }

      if (path === "/api/v1/activity") {
        try {
          const result = await env.AUDIT_DB.prepare(
            `SELECT * FROM audit_log ORDER BY created_at DESC LIMIT 10`,
          ).all();
          return jsonResponse({ activities: result.results || [] });
        } catch (e) {
          return jsonResponse({ activities: [] });
        }
      }

      if (path === "/api/v1/killswitch" && request.method === "POST") {
        const body = (await request.json()) as {
          passkey_verified?: boolean;
        };

        if (!body.passkey_verified) {
          return jsonResponse(
            { error: "Passkey verification required" },
            403,
          );
        }

        try {
          const daemonUrl = env.DAEMON_URL || "http://localhost:8080";
          await fetch(`${daemonUrl}/api/v1/killswitch`, {
            method: "POST",
            headers: {
              ...(env.VPS_INTERNAL_KEY
                ? { "X-Internal-Key": env.VPS_INTERNAL_KEY }
                : {}),
            },
          });
        } catch (e) {
          console.error("Daemon kill-switch failed:", e);
        }

        await env.LIVE_STATE.put("execution_enabled", "false");

        await env.AUDIT_DB.prepare(
          `INSERT INTO audit_log (id, event_type, payload_json, created_at) VALUES (?, ?, ?, ?)`,
        )
          .bind(
            crypto.randomUUID(),
            "kill_switch_triggered",
            JSON.stringify({
              source: "dashboard",
              passkey_verified: true,
              timestamp: Date.now(),
            }),
            Date.now(),
          )
          .run();

        ctx.waitUntil(sendTelegramAlert(env, "🛑 KILL-SWITCH TRIGGERED"));
        return jsonResponse({
          success: true,
          message: "Kill switch activated",
        });
      }

      if (path === "/api/v1/killswitch/challenge") {
        const challenge = crypto.getRandomValues(new Uint8Array(32));
        const challengeId = crypto.randomUUID();
        challenges.set(challengeId, {
          challenge,
          expires: Date.now() + 60000,
        });

        return jsonResponse({
          challenge: Array.from(challenge),
          challengeId,
          message: "Confirm kill-switch with passkey",
        });
      }

      if (path === "/api/v1/agent/task" && request.method === "POST") {
        const body = await request.json();
        await env.AGENT_QUEUE.send(body);
        return jsonResponse({ success: true, message: "Task queued" });
      }

      if (path === "/api/v1/strategies/active") {
        try {
          const result = await env.AUDIT_DB.prepare(
            `SELECT * FROM strategies ORDER BY created_at DESC LIMIT 5`,
          ).all();
          return jsonResponse({ strategies: result.results || [] });
        } catch (e) {
          return jsonResponse({ strategies: [] });
        }
      }

      if (path === "/api/v1/agents/verdicts") {
        const state = await fetchDaemonState(env);
        return jsonResponse({
          departments: state.departments || [],
          last_update: state.last_sync || 0,
        });
      }

      if (path === "/api/v1/ohlcv") {
        const symbol = url.searchParams.get("symbol") || "BTCUSDT";
        const tf = url.searchParams.get("tf") || "1h";

        try {
          const daemonUrl = env.DAEMON_URL || "http://localhost:8080";
          const res = await fetch(
            `${daemonUrl}/api/v1/ohlcv?symbol=${symbol}&tf=${tf}`,
            {
              headers: {
                ...(env.VPS_INTERNAL_KEY
                  ? { "X-Internal-Key": env.VPS_INTERNAL_KEY }
                  : {}),
              },
            },
          );
          if (res.ok) {
            const data = await res.json();
            return jsonResponse(data);
          }
        } catch (e) {
          console.error("OHLCV fetch failed:", e);
        }

        return jsonResponse({ candles: [] });
      }

      return jsonResponse({ error: "Not found" }, 404);
    } catch (err) {
      console.error("API Error:", err);
      return jsonResponse({ error: "Internal server error" }, 500);
    }
  },

  async queue(
    batch: MessageBatch,
    env: Env,
    ctx: ExecutionContext,
  ): Promise<void> {
    for (const message of batch.messages) {
      console.log("Processing agent task:", message.body);
    }
  },
};

function jsonResponse(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json",
      ...corsHeaders,
    },
  });
}

function getDefaultState() {
  return {
    systemStatus: "paper",
    activeAsset: "BTC-PERP",
    regime: "trending_up",
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
      exchanges: 8,
    },
  };
}

async function sendTelegramAlert(env: Env, message: string): Promise<void> {
  const url = `https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/sendMessage`;
  await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      chat_id: "ADMIN_CHAT_ID",
      text: message,
      parse_mode: "HTML",
    }),
  });
}
