import type { HealthResponse } from "../types/health";

const apiUrl = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export async function getHealth(signal?: AbortSignal): Promise<HealthResponse> {
  const response = await fetch(`${apiUrl}/health`, { signal });
  if (!response.ok) {
    throw new Error(`Health check failed with status ${response.status}`);
  }
  return response.json() as Promise<HealthResponse>;
}