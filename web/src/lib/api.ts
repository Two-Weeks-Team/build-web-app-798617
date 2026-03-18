export type PlanRequest = { query: string; preferences: string };
export type PlanResponse = { summary: string; items: Record<string, string>; score: { value: number; rationale: string } };
export type InsightsRequest = { selection: string; context: string };
export type InsightsResponse = { insights: string[]; next_actions: string[]; highlights: string[] };

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const msg = await res.text();
    throw new Error(msg || "Request failed");
  }
  return res.json() as Promise<T>;
}

export async function generatePlan(payload: PlanRequest): Promise<PlanResponse> {
  const res = await fetch("/api/plan", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  return handle<PlanResponse>(res);
}

export async function getInsights(payload: InsightsRequest): Promise<InsightsResponse> {
  const res = await fetch("/api/insights", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  return handle<InsightsResponse>(res);
}

export async function saveDossier(payload: { title: string; summary: string; score: { value: number; rationale: string } }) {
  const res = await fetch("/api/dossiers", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  return handle<{ ok: boolean }>(res);
}

export async function fetchDossiers() {
  const res = await fetch("/api/dossiers", { method: "GET" });
  return handle<Array<{ id: number; title: string; summary: string; score: number }>>(res);
}
