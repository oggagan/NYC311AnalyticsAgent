const API_BASE = "/api";

export async function checkHealth(): Promise<{
  status: string;
  db_connected: boolean;
  rows_loaded: number;
}> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error("Backend unavailable");
  return res.json();
}
