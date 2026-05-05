import { writable } from "svelte/store";
import type { DashboardState } from "./types";

// Use the Cloudflare Worker as API gateway
const API_BASE = "https://futures-brokiepedia-api.kentaursoft-com.workers.dev";
// VPS backend for direct access (paper trading, analytics, etc.)
const VPS_BASE = "http://178.238.229.116:8000";

class ApiClient {
  private token: string | null = null;

  constructor() {
    if (typeof window !== "undefined") {
      this.token = localStorage.getItem("auth_token");
    }
  }

  async fetch(path: string, options?: RequestInit): Promise<unknown> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };

    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`;
    }

    const res = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: {
        ...headers,
        ...options?.headers,
      },
    });

    if (res.status === 401) {
      if (typeof window !== "undefined") {
        localStorage.removeItem("auth_token");
        window.location.href = "/auth";
      }
    }

    if (!res.ok) throw new Error(`API error: ${res.status}`);
    return res.json();
  }

  async getState(): Promise<DashboardState> {
    return this.fetch("/api/v1/state") as Promise<DashboardState>;
  }

  async getDepartments(): Promise<{ departments: any[]; last_update: number }> {
    return this.fetch("/api/v1/departments") as Promise<{
      departments: any[];
      last_update: number;
    }>;
  }

  async getPositions(): Promise<{ positions: any[]; count: number }> {
    return this.fetch("/api/v1/positions") as Promise<{
      positions: any[];
      count: number;
    }>;
  }

  async triggerKillSwitch(): Promise<{ success: boolean }> {
    const challengeRes = (await this.fetch("/api/v1/killswitch/challenge")) as {
      challenge: number[];
      challengeId: string;
    };

    const assertion = await navigator.credentials.get({
      publicKey: {
        challenge: new Uint8Array(challengeRes.challenge),
        rpId: "futures.brokiepedia.com",
        userVerification: "required",
      },
    });

    if (!assertion) {
      throw new Error("Kill-switch cancelled");
    }

    return this.fetch("/api/v1/killswitch", {
      method: "POST",
      body: JSON.stringify({ passkey_verified: true }),
    }) as Promise<{ success: boolean }>;
  }

  async getAuthChallenge(): Promise<{
    challenge: number[];
    rp: { name: string; id: string };
  }> {
    return this.fetch("/api/v1/auth/challenge") as Promise<{
      challenge: number[];
      rp: { name: string; id: string };
    }>;
  }

  // Direct VPS fetch (for endpoints blocked by worker)
  private async vpsFetch(path: string, options?: RequestInit): Promise<unknown> {
    const res = await fetch(`${VPS_BASE}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    });
    if (!res.ok) throw new Error(`VPS API error: ${res.status}`);
    return res.json();
  }

  // Paper Trading API (direct to VPS)
  async getPaperTradingPrices(): Promise<{ prices: Record<string, { price: number; change24h: number }>; timestamp: number }> {
    return this.vpsFetch("/api/v1/paper-trading/prices") as Promise<any>;
  }

  async getPaperBalance(): Promise<{
    balance: number;
    initial_balance: number;
    total_pnl: number;
    unrealized_pnl: number;
    open_positions: number;
    total_trades: number;
    winning_trades: number;
    win_rate: number;
    timestamp: number;
  }> {
    return this.vpsFetch("/api/v1/paper-trading/balance") as Promise<any>;
  }

  async getPaperPositions(): Promise<{ positions: any[]; count: number }> {
    return this.vpsFetch("/api/v1/paper-trading/positions") as Promise<any>;
  }

  async executePaperTrade(symbol: string, side: string, size: number, leverage?: number): Promise<any> {
    return this.vpsFetch("/api/v1/paper-trading/execute", {
      method: "POST",
      body: JSON.stringify({ symbol, side, size, leverage: leverage || 1.0 }),
    }) as Promise<any>;
  }

  async closePaperTrade(tradeId: string, exitPrice: number): Promise<any> {
    return this.vpsFetch(`/api/v1/paper-trading/close/${tradeId}`, {
      method: "POST",
      body: JSON.stringify({ exit_price: exitPrice }),
    }) as Promise<any>;
  }

  async getPaperTradeHistory(): Promise<{ trades: any[]; count: number }> {
    return this.vpsFetch("/api/v1/paper-trading/history") as Promise<any>;
  }

  // Analytics, Signals, Activity (direct to VPS)
  async getAnalytics(): Promise<any> {
    return this.vpsFetch("/api/v1/analytics") as Promise<any>;
  }

  async getSignals(): Promise<{ signals: any[]; count: number }> {
    return this.vpsFetch("/api/v1/signals") as Promise<any>;
  }

  async getActivity(): Promise<{ activity: any[]; count: number }> {
    return this.vpsFetch("/api/v1/activity") as Promise<any>;
  }

  isAuthenticated(): boolean {
    return !!this.token;
  }

  logout() {
    this.token = null;
    if (typeof window !== "undefined") {
      localStorage.removeItem("auth_token");
    }
  }
}

export const api = new ApiClient();

// Live dashboard state store
export const liveState = writable<DashboardState | null>(null);

// Poll live state every 5 seconds
export function startPolling(intervalMs = 5000): () => void {
  const interval = setInterval(async () => {
    try {
      const state = await api.getState();
      liveState.set(state);
    } catch (err) {
      console.error("Poll error:", err);
    }
  }, intervalMs);

  // Initial fetch
  api
    .getState()
    .then((state) => liveState.set(state))
    .catch((err) => {
      console.error("Initial state fetch failed:", err);
    });

  return () => clearInterval(interval);
}
