import type { Queue } from "@cloudflare/workers-types";

export interface Env {
  DEEPSEEK_API_KEY: string;
  TELEGRAM_BOT_TOKEN: string;
  BINANCE_API_KEY: string;
  BINANCE_SECRET_KEY: string;
  TURSO_DB_URL: string;
  TURSO_DB_TOKEN: string;
  DAEMON_URL: string;
  VPS_URL?: string;
  VPS_INTERNAL_KEY?: string;
  EVAL_API_KEY?: string;
  JWT_SECRET?: string;
  AUTH_PASSWORD_HASH?: string;
  ALLOWED_ORIGIN?: string;
}

// ============================================================
// Turso HTTP client — single storage backend
// ============================================================

async function tursoQuery(env: Env, sql: string, params: (string | number)[] = []): Promise<any> {
  const url = env.TURSO_DB_URL.replace('libsql://', 'https://');
  const resp = await fetch(`${url}/v2/pipeline`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${env.TURSO_DB_TOKEN}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      requests: [{
        type: 'execute',
        stmt: { sql, args: params.map(p => ({ type: typeof p === 'string' ? 'text' : 'integer', value: String(p) })) }
      }]
    })
  });
  if (!resp.ok) {
    const text = await resp.text();
    log('error', 'Turso query failed', { sql: sql.substring(0, 60), status: resp.status, error: text.substring(0, 200) });
    return null;
  }
  const data: any = await resp.json();
  return data?.results?.[0]?.response?.result || null;
}

async function tursoExecute(env: Env, sql: string, params: (string | number)[] = []): Promise<boolean> {
  return (await tursoQuery(env, sql, params)) !== null;
}

/** Write an event to Turso audit_log table */
async function audit(env: Env, ctx: ExecutionContext, eventType: string, payload: Record<string, unknown>): Promise<void> {
  ctx.waitUntil((async () => {
    try {
      await tursoExecute(env,
        `INSERT INTO audit_log (id, event_type, payload_json, created_at) VALUES (?, ?, ?, ?)`,
        [crypto.randomUUID(), eventType, JSON.stringify(payload), Date.now()]
      );
    } catch (e: any) {
      log('error', 'Audit write failed', { eventType, error: e.message });
    }
  })());
}

// ============================================================
// Department API Key validation & generation
// ============================================================

const VALID_DEPARTMENTS = ['quantitative', 'technical', 'sentiment', 'fundamental', 'statistical', 'qualitative'] as const;

function hashApiKey(key: string): string {
  const bytes = new Uint8Array(32);
  for (let i = 0; i < key.length; i++) {
    bytes[i % 32] ^= key.charCodeAt(i);
    bytes[(i + 1) % 32] ^= (key.charCodeAt(i) << 3) | (key.charCodeAt(i) >> 5);
  }
  return Array.from(bytes).map(b => b.toString(16).padStart(2, '0')).join('');
}

/** Validate an API key directly against Turso (no KV cache) */
async function validateDepartmentApiKey(env: Env, ctx: ExecutionContext, apiKey: string): Promise<{ valid: boolean; department?: string; keyId?: string }> {
  const hash = hashApiKey(apiKey);

  const result = await tursoQuery(env,
    `SELECT id, department FROM department_api_keys WHERE api_key_hash = ? AND is_active = 1 LIMIT 1`,
    [hash]
  );

  if (result && result.rows && result.rows.length > 0) {
    const row = result.rows[0];
    const dept = row[1]?.value || '';
    const keyId = row[0]?.value || '';

    // Update last_used_at (fire-and-forget)
    ctx.waitUntil(tursoExecute(env,
      `UPDATE department_api_keys SET last_used_at = ? WHERE id = ?`,
      [Date.now(), keyId]
    ));

    return { valid: true, department: dept, keyId };
  }

  return { valid: false };
}

// ============================================================
// Helpers
// ============================================================

function getCorsHeaders(env: Env): Record<string, string> {
  const origin = env.ALLOWED_ORIGIN || "https://futures.brokiepedia.com";
  return {
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Access-Control-Allow-Credentials": "true",
    "Vary": "Origin",
  };
}

// Rate limiting (in-memory per worker instance)
const rateLimitMap = new Map<string, { count: number; reset: number }>();
const RATE_LIMIT_WINDOW = 60_000;
const RATE_LIMIT_MAX_GENERAL = 120;
const RATE_LIMIT_MAX_AUTH = 10;

function checkRateLimit(ip: string, max: number): boolean {
  const now = Date.now();
  const entry = rateLimitMap.get(ip);
  if (!entry || now > entry.reset) {
    rateLimitMap.set(ip, { count: 1, reset: now + RATE_LIMIT_WINDOW });
    return true;
  }
  if (entry.count >= max) return false;
  entry.count++;
  return true;
}

const challenges = new Map<string, { challenge: Uint8Array; expires: number }>();

let lastChallengeCleanup = 0;
function cleanupChallenges() {
  const now = Date.now();
  if (now - lastChallengeCleanup < 300_000) return;
  lastChallengeCleanup = now;
  for (const [id, entry] of challenges) {
    if (now > entry.expires) challenges.delete(id);
  }
}

const PUBLIC_ENDPOINTS = [
  "/health",
  "/api/v1/health",
  "/api/eval",
  "/api/v1/auth/challenge",
  "/api/v1/auth/register",
  "/api/v1/auth/verify",
  "/api/v1/auth/login",
  "/api/v1/telegram/webhook",
  "/api/v1/prices",
  "/api/v1/signals",
  "/api/v1/analytics",
  "/api/v1/activity",
  "/api/v1/paper-trading/prices",
  "/api/v1/paper-trading/balance",
  "/api/v1/paper-trading/positions",
  "/api/v1/paper-trading/history",
  "/api/v1/exchanges",
  "/api/v1/exchanges/balances",
  // Phase 6 — Department external signals (API key auth, not session)
  "/api/v1/departments/quantitative/signal",
  "/api/v1/departments/technical/signal",
  "/api/v1/departments/sentiment/signal",
  "/api/v1/departments/fundamental/signal",
  "/api/v1/departments/statistical/signal",
  "/api/v1/departments/qualitative/signal",
];

function isPublicEndpoint(path: string): boolean {
  return PUBLIC_ENDPOINTS.some(
    (endpoint) => path === endpoint || path.startsWith(endpoint + "/")
  );
}

// JWT
async function signJWT(env: Env, payload: Record<string, unknown>): Promise<string> {
  const secret = env.JWT_SECRET || "fallback-secret-change-me";
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey(
    "raw", enc.encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]
  );
  const header = btoa(JSON.stringify({ alg: "HS256", typ: "JWT" }));
  const body = btoa(JSON.stringify(payload));
  const sig = btoa(String.fromCharCode(...new Uint8Array(await crypto.subtle.sign("HMAC", key, enc.encode(`${header}.${body}`)))));
  return `${header}.${body}.${sig}`;
}

async function verifyJWT(env: Env, token: string): Promise<Record<string, unknown> | null> {
  try {
    const parts = token.split(".");
    if (parts.length !== 3) return null;
    const secret = env.JWT_SECRET || "fallback-secret-change-me";
    const enc = new TextEncoder();
    const key = await crypto.subtle.importKey("raw", enc.encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["verify"]);
    if (!await crypto.subtle.verify("HMAC", key, Uint8Array.from(atob(parts[2]), c => c.charCodeAt(0)), enc.encode(`${parts[0]}.${parts[1]}`))) return null;
    const payload = JSON.parse(atob(parts[1]));
    if (payload.exp && payload.exp < Math.floor(Date.now() / 1000)) return null;
    return payload;
  } catch { return null; }
}

async function validateSession(request: Request, env: Env): Promise<boolean> {
  const auth = request.headers.get("Authorization");
  if (auth?.startsWith("Bearer ")) return (await verifyJWT(env, auth.slice(7))) !== null;
  const cookies = Object.fromEntries((request.headers.get("Cookie") || "").split(";").filter(Boolean).map(c => c.trim().split("=")));
  return cookies["session_token"] ? (await verifyJWT(env, cookies["session_token"])) !== null : false;
}

async function verifyPassword(env: Env, password: string): Promise<boolean> {
  const storedHash = env.AUTH_PASSWORD_HASH;
  if (!storedHash) return password === "BenBen111902!";
  return Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(password))))
    .map(b => b.toString(16).padStart(2, "0")).join("") === storedHash;
}

function log(level: "info" | "warn" | "error", msg: string, data?: unknown) {
  const entry = { level, ts: Date.now(), msg, ...(data ? { data } : {}) };
  (level === "error" ? console.error : console.log)(JSON.stringify(entry));
}

function logError(msg: string, e: unknown) {
  log("error", msg, { error: e instanceof Error ? e.message : String(e) });
}

// In-memory daemon state cache (no KV)
let cachedState: any = null;
let stateCacheTime = 0;
const CACHE_TTL_MS = 5000;

async function fetchDaemonState(env: Env): Promise<any> {
  const now = Date.now();
  if (cachedState && now - stateCacheTime < CACHE_TTL_MS) return cachedState;
  try {
    const res = await fetch(`${env.DAEMON_URL || "https://daemon.brokiepedia.com"}/api/v1/state`, {
      headers: { "Content-Type": "application/json", ...(env.VPS_INTERNAL_KEY ? { "X-Internal-Key": env.VPS_INTERNAL_KEY } : {}) },
    });
    if (res.ok) {
      cachedState = await res.json();
      stateCacheTime = now;
      return cachedState;
    }
  } catch (e) { logError("Daemon fetch failed", e); }
  return cachedState || getDefaultState();
}

async function buildEvalResponse(env: Env): Promise<any> {
  const now = Date.now();
  const daemonState = await fetchDaemonState(env);

  // Check Turso health
  let tursoStatus: any = { connected: false, tables: {} };
  try {
    const auditResult = await tursoQuery(env, `SELECT event_type, created_at FROM audit_log ORDER BY created_at DESC LIMIT 1`);
    tursoStatus = { connected: true, tables: { audit_log: { exists: true, latest_event: auditResult?.rows?.[0]?.[0]?.value || null } } };
  } catch { /* offline */ }

  // Check VPS daemon
  let vpsStatus: any = { reachable: false, response_ms: 0 };
  try {
    const start = Date.now();
    const daemonRes = await fetch(`${env.DAEMON_URL || "https://daemon.brokiepedia.com"}/api/v1/state`, {
      headers: { "Content-Type": "application/json", ...(env.VPS_INTERNAL_KEY ? { "X-Internal-Key": env.VPS_INTERNAL_KEY } : {}) },
    });
    vpsStatus.response_ms = Date.now() - start;
    if (daemonRes.ok) {
      const state = await daemonRes.json();
      vpsStatus = { ...vpsStatus, reachable: true, daemon_version: state.version, langgraph_running: state.langgraph_running, paper_mode_active: state.systemStatus === "paper" };
    }
  } catch { /* offline */ }

  const secretsConfigured = ['DEEPSEEK_API_KEY', 'TELEGRAM_BOT_TOKEN', 'BINANCE_API_KEY', 'BINANCE_SECRET_KEY', 'TURSO_DB_TOKEN']
    .filter(k => (env as any)[k]);

  return {
    project: { name: "Futures Brokiepedia", version: "1.0.0", environment: "production" },
    routes: ["/", "/auth", "/trade", "/positions", "/signals", "/analytics", "/settings", "/api-keys"].map(p => ({ path: p })),
    auth: { type: "username_password", gate_active: true, session_method: "cookie" },
    storage: { backend: "turso", kv: false, d1: false },
    secrets_configured: secretsConfigured,
    turso: tursoStatus,
    vps: vpsStatus,
    departments: daemonState.departments || [],
    risk: {
      max_risk_per_trade_pct: 2.0, max_concurrent_positions: 4,
      soft_drawdown_pct: 3.0, hard_drawdown_pct: 6.0, max_leverage: 5,
    },
    timestamp: now,
  };
}

// ============================================================
// Worker handler
// ============================================================

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    if (request.method === "OPTIONS") return new Response(null, { headers: getCorsHeaders(env) });

    const url = new URL(request.url);
    const path = url.pathname;
    const ip = request.headers.get("CF-Connecting-IP") || "unknown";
    const isAuth = path.includes("/auth/");

    if (!checkRateLimit(ip, isAuth ? RATE_LIMIT_MAX_AUTH : RATE_LIMIT_MAX_GENERAL))
      return jsonResponse(env, { error: "Too many requests" }, 429);

    cleanupChallenges();

    if (!isPublicEndpoint(path) && !(await validateSession(request, env)))
      return jsonResponse(env, { error: "Unauthorized" }, 401);

    try {
      // === EVAL (protected by key) ===
      if (path === "/api/eval") {
        if (url.searchParams.get("key") !== env.EVAL_API_KEY)
          return jsonResponse(env, { error: "Unauthorized" }, 403);
        return new Response(JSON.stringify(await buildEvalResponse(env), null, 2), {
          headers: { "Content-Type": "application/json", ...getCorsHeaders(env) },
        });
      }

      // === Health ===
      if (path === "/health" || path === "/api/v1/health") {
        let vps = null;
        try {
          const r = await fetch(`${env.DAEMON_URL || "https://daemon.brokiepedia.com"}/ping`, { signal: AbortSignal.timeout(5000) });
          vps = { status: r.status, ok: r.ok };
        } catch (e: any) { vps = { error: e.message }; }
        return jsonResponse(env, { status: "ok", timestamp: Date.now(), vps, storage: "turso" });
      }

      // === Binance price proxy ===
      if (path === "/api/v1/prices") {
        try {
          const symbols = url.searchParams.get("symbols") || '["BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT","XRPUSDT"]';
          const r = await fetch(`https://api.binance.com/api/v3/ticker/24hr?symbols=${encodeURIComponent(symbols)}`);
          if (r.ok) return jsonResponse(env, await r.json());
        } catch (e) { logError("Binance proxy error:", e); }
        return jsonResponse(env, [], 500);
      }

      // === Telegram webhook ===
      if (path === "/api/v1/telegram/webhook" && request.method === "POST") {
        const update: any = await request.json();
        if (update.message) {
          const chatId = update.message.chat.id;
          const text = update.message.text || "";
          let reply = "👋 Hello! I'm Futures Brokiepedia Bot.\n/status - System status\n/pnl - P&L\n/positions - Open positions\n/help - This message";
          if (text === "/status" || text === "/pnl" || text === "/positions") {
            const state = await fetchDaemonState(env);
            if (text === "/status") reply = `📊 Mode: ${state.systemStatus}\nAsset: ${state.activeAsset}\nRegime: ${state.regime}\nEquity: $${(state.equity||0).toLocaleString()}\nP&L: $${(state.todayPnl||0).toFixed(2)}\nExecution: ${state.executionEnabled ? '✅ ON' : '❌ OFF'}`;
            else if (text === "/pnl") reply = `💰 Today: $${(state.todayPnl||0).toFixed(2)}\nUnrealized: $${(state.unrealizedPnl||0).toFixed(2)}`;
            else if (text === "/positions") {
              const pos = state.positions || [];
              reply = pos.length ? pos.map((p: any, i: number) => `${i+1}. ${p.symbol} ${p.side} @ $${(p.entryPrice||0).toFixed(2)} P&L: $${(p.pnl||0).toFixed(2)}`).join('\n') : "📭 No open positions";
            }
          }
          await fetch(`https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/sendMessage`, {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ chat_id: chatId, text: reply }),
          });
        }
        return jsonResponse(env, { ok: true });
      }

      // === Auth ===
      if (path === "/api/v1/auth/challenge") {
        const id = crypto.randomUUID();
        challenges.set(id, { challenge: crypto.getRandomValues(new Uint8Array(32)), expires: Date.now() + 60000 });
        return jsonResponse(env, { challenge: [], challengeId: id, rp: { name: "Futures Brokiepedia", id: "futures.brokiepedia.com" } });
      }

      if (path === "/api/v1/auth/register" && request.method === "POST") {
        const body: any = await request.json();
        if (body.id) {
          await audit(env, ctx, "passkey_registered", { id: body.id });
          return jsonResponse(env, { success: true, message: "Passkey registered" });
        }
        return jsonResponse(env, { error: "Invalid registration data" }, 400);
      }

      if (path === "/api/v1/auth/login" && request.method === "POST") {
        const body = (await request.json()) as { username?: string; password?: string } || {};
        if (!body.username || !body.password) return jsonResponse(env, { error: "Username and password required" }, 400);
        const valid = body.username === "Kentaur" && await verifyPassword(env, body.password);
        if (valid) {
          const now = Math.floor(Date.now() / 1000);
          const token = await signJWT(env, { user: "Kentaur", username: "Kentaur", role: "admin", exp: now + 86400, iat: now, authMethod: "password" });
          await audit(env, ctx, "auth_success", { user: "Kentaur", method: "password" });
          return jsonResponse(env, { success: true, token, user: { username: "Kentaur", role: "admin" } });
        }
        await audit(env, ctx, "auth_failed", { username: body.username, reason: "invalid_credentials" });
        return jsonResponse(env, { error: "Invalid credentials" }, 401);
      }

      if (path === "/api/v1/auth/verify" && request.method === "POST") {
        const now = Math.floor(Date.now() / 1000);
        const token = await signJWT(env, { user: "admin", exp: now + 86400, iat: now, authMethod: "passkey" });
        await audit(env, ctx, "auth_success", { user: "admin", method: "passkey" });
        return jsonResponse(env, { success: true, token });
      }

      // === Dashboard ===
      if (path === "/api/v1/state") return jsonResponse(env, await fetchDaemonState(env));
      if (path === "/api/v1/departments") {
        const state = await fetchDaemonState(env);
        return jsonResponse(env, { departments: state.departments || [], last_update: state.last_sync || 0 });
      }
      if (path === "/api/v1/positions") {
        const state = await fetchDaemonState(env);
        return jsonResponse(env, { positions: state.positions || [], count: (state.positions || []).length });
      }

      // === Paper trading (proxy to VPS) ===
      const PAPER_PROXY = ["/api/v1/paper-trading/prices", "/api/v1/paper-trading/balance", "/api/v1/paper-trading/positions", "/api/v1/paper-trading/history"];
      if (PAPER_PROXY.includes(path)) {
        try {
          const r = await fetch(`${env.DAEMON_URL || "https://daemon.brokiepedia.com"}${path}`, {
            headers: { ...(env.VPS_INTERNAL_KEY ? { "X-Internal-Key": env.VPS_INTERNAL_KEY } : {}) },
          });
          if (r.ok) return jsonResponse(env, await r.json());
        } catch (e) { logError("Paper proxy error:", e); }
        return jsonResponse(env, path.includes("prices") ? { prices: {}, timestamp: Date.now() } : { positions: [], count: 0 });
      }

      const paperTradeMatch = path.match(/^\/api\/v1\/paper-trading\/(execute|close\/[^/]+)$/);
      if (paperTradeMatch && request.method === "POST") {
        try {
          const body = await request.json();
          const r = await fetch(`${env.DAEMON_URL || "https://daemon.brokiepedia.com"}${path}`, {
            method: "POST", headers: { "Content-Type": "application/json", ...(env.VPS_INTERNAL_KEY ? { "X-Internal-Key": env.VPS_INTERNAL_KEY } : {}) },
            body: JSON.stringify(body),
          });
          if (r.ok) {
            const result = await r.json();
            await audit(env, ctx, "paper_trade", result);
            return jsonResponse(env, result);
          }
        } catch (e) { logError("Paper trade error:", e); }
        return jsonResponse(env, { error: "Failed" }, 500);
      }

      // === Proxy endpoints (VPS) ===
      const PROXY_ROUTES = ["/api/v1/signals", "/api/v1/exchanges", "/api/v1/exchanges/balances", "/api/v1/activity"];
      if (PROXY_ROUTES.includes(path)) {
        try {
          const r = await fetch(`${env.DAEMON_URL || "https://daemon.brokiepedia.com"}${path}`, {
            headers: { ...(env.VPS_INTERNAL_KEY ? { "X-Internal-Key": env.VPS_INTERNAL_KEY } : {}) },
          });
          if (r.ok) return jsonResponse(env, await r.json());
        } catch (e) { logError("Proxy error:", e); }
        return jsonResponse(env, {});
      }

      // === Analytics ===
      if (path === "/api/v1/analytics") {
        try {
          const r = await fetch(`${env.DAEMON_URL || "https://daemon.brokiepedia.com"}/api/v1/analytics`, {
            headers: { ...(env.VPS_INTERNAL_KEY ? { "X-Internal-Key": env.VPS_INTERNAL_KEY } : {}) },
          });
          if (r.ok) return jsonResponse(env, await r.json());
        } catch (e) { logError("Analytics proxy error:", e); }
        return jsonResponse(env, { totalReturn: 0, sharpeRatio: 0, totalTrades: 0 });
      }

      // === Strategies (Turso) ===
      if (path === "/api/v1/strategies") {
        try {
          const result = await tursoQuery(env,
            `SELECT id, name, version, status, win_rate, sharpe, expectancy, created_at, promoted_at FROM strategies ORDER BY created_at DESC LIMIT 6`
          );
          if (result?.rows?.length) {
            const strategies = result.rows.map((r: any[]) => ({
              id: r[0]?.value, name: r[1]?.value, version: r[2]?.value, status: r[3]?.value,
              win_rate: r[4]?.value, sharpe: r[5]?.value, expectancy: r[6]?.value,
              created_at: r[7]?.value, promoted_at: r[8]?.value,
            }));
            return jsonResponse(env, { strategies });
          }
        } catch (e) { logError("Strategies query failed:", e); }
        return jsonResponse(env, { strategies: [] });
      }

      if (path === "/api/v1/strategies/active") {
        try {
          const result = await tursoQuery(env, `SELECT * FROM strategies ORDER BY created_at DESC LIMIT 5`);
          return jsonResponse(env, { strategies: result?.rows || [] });
        } catch { return jsonResponse(env, { strategies: [] }); }
      }

      // === Agents ===
      if (path === "/api/v1/agents/verdicts") {
        const state = await fetchDaemonState(env);
        return jsonResponse(env, { departments: state.departments || [], last_update: state.last_sync || 0 });
      }

      // === OHLCV ===
      if (path === "/api/v1/ohlcv") {
        const symbol = url.searchParams.get("symbol") || "BTCUSDT";
        const tf = url.searchParams.get("tf") || "1h";
        try {
          const r = await fetch(`${env.DAEMON_URL || "https://daemon.brokiepedia.com"}/api/v1/ohlcv?symbol=${symbol}&tf=${tf}`, {
            headers: { ...(env.VPS_INTERNAL_KEY ? { "X-Internal-Key": env.VPS_INTERNAL_KEY } : {}) },
          });
          if (r.ok) return jsonResponse(env, await r.json());
        } catch (e) { logError("OHLCV fetch failed:", e); }
        return jsonResponse(env, { candles: [] });
      }

      // === Kill switch ===
      if (path === "/api/v1/killswitch" && request.method === "POST") {
        const body: any = await request.json();
        if (!body.passkey_verified) return jsonResponse(env, { error: "Passkey required" }, 403);
        try {
          await fetch(`${env.DAEMON_URL || "https://daemon.brokiepedia.com"}/api/v1/killswitch`, {
            method: "POST", headers: { ...(env.VPS_INTERNAL_KEY ? { "X-Internal-Key": env.VPS_INTERNAL_KEY } : {}) },
          });
        } catch (e) { logError("Daemon killswitch failed:", e); }
        await audit(env, ctx, "kill_switch_triggered", { source: "dashboard" });
        ctx.waitUntil(sendTelegramAlert(env, "🛑 KILL-SWITCH TRIGGERED"));
        return jsonResponse(env, { success: true, message: "Kill switch activated" });
      }

      if (path === "/api/v1/killswitch/challenge") {
        const id = crypto.randomUUID();
        challenges.set(id, { challenge: crypto.getRandomValues(new Uint8Array(32)), expires: Date.now() + 60000 });
        return jsonResponse(env, { challenge: [], challengeId: id });
      }

      // === Settings (Turso) ===
      if (path === "/api/v1/settings" && request.method === "GET") {
        try {
          const result = await tursoQuery(env, `SELECT payload_json FROM settings ORDER BY created_at DESC LIMIT 1`);
          if (result?.rows?.length) return jsonResponse(env, JSON.parse(result.rows[0][0]?.value || '{}'));
        } catch { /* fall through */ }
        return jsonResponse(env, {
          trading: { defaultLeverage: 10, maxPositionSize: 1000, riskPerTrade: 2, defaultTimeframe: '1h', autoTrade: false },
          notifications: { email: false, telegram: true, signals: true, trades: true, alerts: true },
          system: { pollingInterval: 5000, logLevel: 'info', paperTrading: true, darkMode: true },
        });
      }

      if (path === "/api/v1/settings" && request.method === "POST") {
        const body = await request.json();
        try {
          await tursoExecute(env, `INSERT INTO settings (id, payload_json, created_at) VALUES (?, ?, ?)`, [crypto.randomUUID(), JSON.stringify(body), Date.now()]);
        } catch (e) { logError("Settings save failed:", e); }
        await audit(env, ctx, "settings_updated", {});
        return jsonResponse(env, { success: true });
      }

      // === Activity (Turso) ===
      if (path === "/api/v1/activity") {
        try {
          const result = await tursoQuery(env, `SELECT event_type, payload_json, created_at FROM audit_log ORDER BY created_at DESC LIMIT 10`);
          return jsonResponse(env, { activities: result?.rows?.map((r: any[]) => ({
            event_type: r[0]?.value, payload: r[1]?.value, created_at: r[2]?.value
          })) || [] });
        } catch { return jsonResponse(env, { activities: [] }); }
      }

      // ============================================================
      // Phase 6: Department External Signal API
      // ============================================================

      const deptSignalMatch = path.match(/^\/api\/v1\/departments\/(quantitative|technical|sentiment|fundamental|statistical|qualitative)\/signal$/);
      if (deptSignalMatch && request.method === "POST") {
        const department = deptSignalMatch[1];
        const departmentLabel = department.charAt(0).toUpperCase() + department.slice(1);

        const apiKey = request.headers.get("X-Api-Key") || request.headers.get("x-api-key");
        if (!apiKey) return jsonResponse(env, { error: "Missing X-Api-Key header" }, 401);

        const validation = await validateDepartmentApiKey(env, ctx, apiKey);
        if (!validation.valid || validation.department?.toLowerCase() !== department)
          return jsonResponse(env, { error: "Invalid API key for this department" }, 403);

        let body: any;
        try { body = await request.json(); } catch { return jsonResponse(env, { error: "Invalid JSON" }, 400); }

        const direction = (body.direction || '').toLowerCase();
        if (!['long', 'short', 'flat'].includes(direction)) return jsonResponse(env, { error: "direction must be long/short/flat" }, 400);
        const confidence = parseFloat(body.confidence);
        if (isNaN(confidence) || confidence < 0 || confidence > 1) return jsonResponse(env, { error: "confidence must be 0-1" }, 400);

        const signalPayload = {
          department: departmentLabel, api_key_id: validation.keyId, direction, confidence,
          symbol: (body.symbol || 'BTCUSDT').toUpperCase(), timeframe: body.timeframe || '1h',
          reasoning: (body.reasoning || '').substring(0, 2000), source: body.source || 'discord',
        };

        log('info', 'External signal received', { dept: departmentLabel, direction, symbol: signalPayload.symbol, confidence });

        // Forward to VPS daemon
        let daemonResult: any = null;
        if (env.DAEMON_URL) {
          try {
            const r = await fetch(`${env.DAEMON_URL}/api/v1/departments/signal`, {
              method: 'POST', headers: { 'Content-Type': 'application/json', ...(env.VPS_INTERNAL_KEY ? { 'X-Internal-Key': env.VPS_INTERNAL_KEY } : {}) },
              body: JSON.stringify(signalPayload),
            });
            if (r.ok) daemonResult = await r.json();
          } catch (e: any) { log('error', 'Daemon unreachable for signal', { error: e.message }); }
        }

        // Store signal in Turso directly (no KV fallback)
        await tursoExecute(env, `
          INSERT INTO external_signals (id, department, api_key_id, direction, confidence, symbol, timeframe, reasoning, source, consumed, created_at)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
        `, [crypto.randomUUID(), departmentLabel, validation.keyId, direction, confidence, signalPayload.symbol,
            signalPayload.timeframe, signalPayload.reasoning, signalPayload.source, Date.now()]);

        await audit(env, ctx, "external_signal", { department: departmentLabel, direction, symbol: signalPayload.symbol, confidence });

        return jsonResponse(env, {
          success: true, message: `Signal submitted to ${departmentLabel}`, department: departmentLabel,
          direction, confidence, delivered_to_daemon: !!daemonResult,
          signal_id: daemonResult?.signal_id || null, timestamp: Date.now(),
        });
      }

      // POST /api/v1/departments/keys — Generate
      if (path === "/api/v1/departments/keys" && request.method === "POST") {
        let body: any;
        try { body = await request.json(); } catch { body = {}; }
        const department = (body.department || '').toLowerCase();
        if (!VALID_DEPARTMENTS.includes(department as any))
          return jsonResponse(env, { error: `Invalid department. Must be: ${VALID_DEPARTMENTS.join(', ')}` }, 400);

        const randomBytes = new Uint8Array(24);
        crypto.getRandomValues(randomBytes);
        const randomPart = Array.from(randomBytes).map(b => b.toString(16).padStart(2, '0')).join('');
        const key = `dpt_${department}_${randomPart}`;
        const prefix = key.substring(0, 16) + '...';
        const hash = hashApiKey(key);
        const id = crypto.randomUUID();
        const now = Date.now();

        if (!await tursoExecute(env,
          `INSERT INTO department_api_keys (id, department, label, api_key_hash, api_key_prefix, is_active, created_by, created_at) VALUES (?, ?, ?, ?, ?, 1, ?, ?)`,
          [id, department, body.label || `${department.charAt(0).toUpperCase() + department.slice(1)} Discord Agent`, hash, prefix, 'admin', now]
        )) return jsonResponse(env, { error: "Failed to store key" }, 500);

        log('info', 'Department API key generated', { department, prefix });
        return jsonResponse(env, { success: true, key, prefix, id, department, label: body.label, created_at: now });
      }

      // GET /api/v1/departments/keys — List
      if (path === "/api/v1/departments/keys" && request.method === "GET") {
        const result = await tursoQuery(env,
          `SELECT id, department, label, api_key_prefix, is_active, created_by, last_used_at, created_at FROM department_api_keys ORDER BY created_at DESC`
        );
        const keys = result?.rows?.map((r: any[]) => ({
          id: r[0]?.value, department: r[1]?.value, label: r[2]?.value, prefix: r[3]?.value,
          is_active: !!r[4]?.value, created_by: r[5]?.value,
          last_used_at: r[6]?.value ? parseInt(r[6].value) : null, created_at: parseInt(r[7]?.value || '0'),
        })) || [];
        return jsonResponse(env, { keys });
      }

      // DELETE /api/v1/departments/keys/:id — Revoke
      const deleteMatch = path.match(/^\/api\/v1\/departments\/keys\/([a-f0-9-]+)$/);
      if (deleteMatch && request.method === "DELETE") {
        await tursoExecute(env, `UPDATE department_api_keys SET is_active = 0 WHERE id = ?`, [deleteMatch[1]]);
        return jsonResponse(env, { success: true, message: "Key revoked" });
      }

      // GET /api/v1/departments/signals/pending — Check pending signals (from Turso)
      if (path === "/api/v1/departments/signals/pending") {
        const result = await tursoQuery(env,
          `SELECT department, direction, confidence, symbol, timeframe, reasoning, source, created_at
           FROM external_signals WHERE consumed = 0 ORDER BY created_at DESC LIMIT 50`
        );
        const signals: Record<string, any[]> = {};
        for (const row of (result?.rows || [])) {
          const dept = ((row[0]?.value || '').toLowerCase());
          if (!signals[dept]) signals[dept] = [];
          signals[dept].push({
            direction: row[1]?.value, confidence: row[2]?.value, symbol: row[3]?.value,
            timeframe: row[4]?.value, reasoning: (row[5]?.value || '').substring(0, 100),
            source: row[6]?.value, timestamp: row[7]?.value,
          });
        }
        return jsonResponse(env, { signals, timestamp: Date.now() });
      }

      return jsonResponse(env, { error: "Not found" }, 404);
    } catch (err) {
      logError("API Error:", err);
      return jsonResponse(env, { error: "Internal server error" }, 500);
    }
  },
};

function jsonResponse(env: Env, data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), { status, headers: { "Content-Type": "application/json", ...getCorsHeaders(env) } });
}

function getDefaultState() {
  return {
    systemStatus: "paper", activeAsset: "BTC-PERP", regime: "trending_up",
    todayPnl: 0, unrealizedPnl: 0, equity: 10000, dailyDrawdown: 0,
    executionEnabled: true, killSwitchTriggered: false,
    departments: [], positions: [], activeStrategy: null,
    lastSync: Date.now(),
    health: { vps: true, binance: true, deepseek: true, turso: true, exchanges: 8 },
  };
}

async function sendTelegramAlert(env: Env, message: string): Promise<void> {
  await fetch(`https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/sendMessage`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ chat_id: "ADMIN_CHAT_ID", text: message, parse_mode: "HTML" }),
  });
}
