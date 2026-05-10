/**
 * Department API Key management client.
 * Used by the frontend to manage department API keys
 * and by the system to submit signals.
 */

const API_BASE = "https://futures-brokiepedia-api.kentaursoft-com.workers.dev";

export interface DepartmentKey {
  id: string;
  department: string;
  label: string;
  prefix: string;
  is_active: boolean;
  created_by: string;
  last_used_at: number | null;
  created_at: number;
}

export interface DepartmentSignal {
  direction: "long" | "short" | "flat";
  confidence: number;
  symbol: string;
  timeframe: string;
  reasoning: string;
}

export interface KeyGenerationResult {
  key: string;
  prefix: string;
  id: string;
  department: string;
  label: string;
  created_at: number;
}

const DEPARTMENT_SLUGS: Record<string, string> = {
  Quantitative: "quantitative",
  Technical: "technical",
  Sentiment: "sentiment",
  Fundamental: "fundamental",
  Statistical: "statistical",
  Qualitative: "qualitative",
};

const DEPARTMENT_LABELS: Record<string, string> = {
  quantitative: "🧮 Quantitative",
  technical: "📈 Technical",
  sentiment: "💬 Sentiment",
  fundamental: "🏛️ Fundamental",
  statistical: "📊 Statistical",
  qualitative: "🎯 Qualitative",
};

function getSessionToken(): string | null {
  if (typeof document === "undefined") return null;
  const match = document.cookie.match(/(?:^|;\s*)session_token=([^;]*)/);
  return match ? match[1] : null;
}

async function fetchApi(path: string, options?: RequestInit): Promise<any> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  const token = getSessionToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { ...headers, ...options?.headers },
    credentials: "include",
  });

  if (res.status === 401 && typeof window !== "undefined") {
    document.cookie = "session_token=; path=/; max-age=0; SameSite=Strict; Secure";
    window.location.href = "/auth";
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(err.error || `API error: ${res.status}`);
  }

  return res.json();
}

export async function getDepartmentKeys(): Promise<DepartmentKey[]> {
  const data = await fetchApi("/api/v1/departments/keys");
  return data.keys || [];
}

export async function generateDepartmentKey(
  department: string,
  label?: string
): Promise<KeyGenerationResult> {
  return fetchApi("/api/v1/departments/keys", {
    method: "POST",
    body: JSON.stringify({ department, label }),
  });
}

export async function revokeDepartmentKey(keyId: string): Promise<void> {
  await fetchApi(`/api/v1/departments/keys/${keyId}`, {
    method: "DELETE",
  });
}

export async function submitDepartmentSignal(
  department: string,
  apiKey: string,
  signal: DepartmentSignal
): Promise<any> {
  const slug = DEPARTMENT_SLUGS[department] || department.toLowerCase();
  const res = await fetch(`${API_BASE}/api/v1/departments/${slug}/signal`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Api-Key": apiKey,
    },
    body: JSON.stringify(signal),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(err.error || `Signal error: ${res.status}`);
  }
  return res.json();
}

export async function getPendingSignals(): Promise<Record<string, any[]>> {
  const data = await fetchApi("/api/v1/departments/signals/pending");
  return data.signals || {};
}

export { DEPARTMENT_SLUGS, DEPARTMENT_LABELS };
