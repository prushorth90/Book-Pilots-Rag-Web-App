import type { HealthResponse } from "../types/health";
import { apiClient } from "./client";

export async function getHealth(signal?: AbortSignal): Promise<HealthResponse> {
  return apiClient.get<HealthResponse>("/health", signal);
}