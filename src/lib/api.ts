import { writable } from "svelte/store";
import type { DashboardState } from "./types";

// Use the Cloudflare Worker as API gateway
const API_BASE = "https://futures-brokiepedia-api.kentaursoft-com.workers.dev";

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
